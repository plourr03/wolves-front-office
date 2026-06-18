#!/usr/bin/env python3
"""
backtest_harness.py  -- Acceptance calibration backtest, the state-reconstruction harness.

For a trade that really happened on date D, rebuild each side's roster as of D and feed it to
partner_acceptance.decide, so we can check whether the model would have said yes. This file is the
reconstruction core (rosters and salaries as-of-D); the label set, fleeces, and tuning sit on top.

Reconstruction (per the spec):
  - Rosters as of D: start from the nba_team_rosters snapshot just BEFORE D, then replay
    nba_transactions between the snapshot and D (apply Signing/Trade as adds, Waive as removes), so
    the roster reflects the state the front offices actually faced. For 2025-offseason trades, which
    predate the first 2025-26 snapshot (Oct 2025), start from the 2024-25 end-of-season rosters
    (nba_player_stats) instead. Reconstruction confidence is tagged per trade.
  - Salaries: the verified contracts (verified_contracts.load_verified), with dead-money handling.
  - Metrics (consensus_net, surplus, need, posture): full-season 2025-26 values as the approximation,
    with posture and the need vector recomputed from the as-of-D roster (not the current one).

    python backtest_harness.py            # self-validate roster reconstruction on a deadline trade
"""

import os
import sys
import csv
import argparse
import collections
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POST, ".env"))
    load_dotenv(os.path.abspath(os.path.join(HERE, "..", "..", ".env")))
except Exception:
    pass
from lib import db                       # noqa: E402

FIRST_SNAPSHOT = date(2025, 10, 22)      # nba_team_rosters 2025-26 coverage starts here
ADD_TYPES = ("Signing", "Trade", "ContractConverted", "AwardOnWaivers")


# --------------------------------- team id <-> tricode ---------------------------------------- #
def team_tricode_map():
    """nba_team_id -> tricode, from the contracts table (authoritative + clean)."""
    d = db.query("SELECT DISTINCT nba_team_id, nba_team_tricode FROM nba_player_contracts")
    return {int(r.nba_team_id): r.nba_team_tricode for _, r in d.iterrows() if r.nba_team_id is not None}


# --------------------------------- roster snapshots ------------------------------------------- #
def snapshot_before(D):
    """The latest roster snapshot date strictly before D (None if none exists yet)."""
    d = db.query("SELECT MAX(roster_date) m FROM nba_team_rosters WHERE roster_date < %s", (D,))
    m = d.iloc[0].m
    return m if m is not None else None


def rosters_at_snapshot(snap_date):
    """{tricode: set(player_id)} from the snapshot on snap_date."""
    d = db.query("""SELECT team_abbreviation t, player_id FROM nba_team_rosters
                    WHERE roster_date = %s AND player_id IS NOT NULL""", (snap_date,))
    out = collections.defaultdict(set)
    for _, r in d.iterrows():
        out[r.t].add(int(r.player_id))
    return out


def rosters_2024_25_end():
    """{tricode: set(player_id)} from the player's final 2024-25 team (most minutes), as the start
    state for replaying 2025-offseason trades that predate the first 2025-26 snapshot."""
    d = db.query("""SELECT player_id, team_abbreviation t, SUM(minutes_played) m
                    FROM nba_player_stats WHERE season_year='2024-25'
                    GROUP BY player_id, team_abbreviation""")
    best = {}
    for _, r in d.iterrows():
        pid = int(r.player_id)
        if pid not in best or (r.m or 0) > best[pid][1]:
            best[pid] = (r.t, r.m or 0)
    out = collections.defaultdict(set)
    for pid, (t, _m) in best.items():
        out[t].add(pid)
    return out


def replay(rosters, start_date, end_date, tri_of):
    """Apply transactions in (start_date, end_date) to the roster dict in place: an acquisition moves
    the player onto the acquiring team (removing him elsewhere); a Waive removes him."""
    d = db.query("""SELECT transaction_date, transaction_type, team_id, player_id, additional_sort
                    FROM nba_transactions
                    WHERE transaction_date > %s AND transaction_date <= %s AND player_id IS NOT NULL
                    ORDER BY transaction_date, additional_sort""", (start_date, end_date))
    for _, r in d.iterrows():
        pid = int(r.player_id)
        tri = tri_of.get(int(r.team_id)) if r.team_id is not None else None
        if r.transaction_type in ADD_TYPES and tri:
            for s in rosters.values():
                s.discard(pid)
            rosters[tri].add(pid)
        elif r.transaction_type == "Waive":
            if tri and pid in rosters.get(tri, set()):
                rosters[tri].discard(pid)
    return rosters


def rosters_as_of(D, tri_of):
    """{tricode: set(player_id)} as of date D, plus a reconstruction-confidence tag."""
    snap = snapshot_before(D)
    if snap is not None and snap >= FIRST_SNAPSHOT:
        rosters = rosters_at_snapshot(snap)
        replay(rosters, snap, D - timedelta(days=1), tri_of)   # close the gap snapshot -> day before D
        conf = "high (snapshot %s + replay)" % snap
    else:
        rosters = rosters_2024_25_end()
        replay(rosters, date(2025, 7, 1) - timedelta(days=1), D - timedelta(days=1), tri_of)
        conf = "low (2024-25 end + offseason replay)"
    return rosters, conf


# --------------------------------- trade label assembly --------------------------------------- #
def two_team_trades(since="2025-07-01"):
    """Genuine two-team trades only (v1). A trade is one group_sort (the full-deal id); we count teams
    over ALL rows including draft-pick rows (player_id NULL = 'received draft consideration'), so a
    three-team deal is excluded rather than mis-split into bilateral legs. Returns per team the players
    it RECEIVED and the number of pick considerations it received."""
    d = db.query("""SELECT transaction_date, group_sort, team_id, player_id, transaction_description
                    FROM nba_transactions
                    WHERE transaction_type='Trade' AND transaction_date >= %s
                    ORDER BY transaction_date, group_sort""", (since,))
    import pandas as pd
    groups = collections.defaultdict(lambda: {"players": collections.defaultdict(list),
                                              "picks": collections.defaultdict(int), "teams": set()})
    gdate = {}
    for _, r in d.iterrows():
        if pd.isna(r.team_id):
            continue
        key = (r.transaction_date, r.group_sort)
        g = groups[key]
        gdate[key] = r.transaction_date
        g["teams"].add(int(r.team_id))
        if pd.notna(r.player_id):
            g["players"][int(r.team_id)].append(int(r.player_id))
        else:                                   # a 'draft consideration' row (vague, no pick id)
            g["picks"][int(r.team_id)] += 1
    out = []
    for key, g in groups.items():
        if len(g["teams"]) == 2:
            out.append({"date": gdate[key], "group": key[1], "teams": sorted(g["teams"]),
                        "players": dict(g["players"]), "picks": dict(g["picks"])})
    return out


DEADLINE_CUTOFF = date(2026, 1, 1)       # trades on/after this fit; before this are held-out offseason
# All trade picks in the feed are vague 'draft consideration' (no year/round/protection), so they
# cannot be matched to nba_draft_picks_future. Each takes one flat generic value on the model's
# asset-point scale (the same scale partner_acceptance prices its own sweetener picks on); a roughly
# right value is enough to flip an asset-hungry seller to yes, which is what the backtest tests.
FLAT_PICK_POINTS = 1.5


# --------------------------------- 2025-26 salary basis --------------------------------------- #
def salaries_2025_26():
    """(nba_player_id, team_tricode) -> 2025-26 salary, resolved through the encoding-robust name
    resolver. Keyed by team because a waive-and-stretch player has a row on two teams."""
    import verified_contracts as VC
    byname, pid_team, _pos = VC.name_authority()
    d = db.query("""SELECT player_name, nba_team_tricode tri, team_abbr, salary
                    FROM nba_player_contracts WHERE season='2025-26'""")
    out = {}
    for _, r in d.iterrows():
        pid, _how = VC.resolve(byname, pid_team, r.player_name, r.team_abbr)
        if pid is not None:
            out[(pid, r.tri)] = int(r.salary or 0)
    return out


def player_salary(pid, team, sal_map):
    """The player's 2025-26 salary on the team he was on pre-trade; falls back to his max row."""
    if (pid, team) in sal_map:
        return sal_map[(pid, team)]
    cand = [v for (p, _t), v in sal_map.items() if p == pid]
    return max(cand) if cand else 0


# --------------------------------- trade -> bilateral packages --------------------------------- #
def build_packages(trades, tri_of, sal_map):
    """For each two-team trade, a record the decide() wiring consumes: each side's RECEIVES and SENDS
    as [{pid, salary, label}], plus pick_pts (the flat-valued draft considerations that side received).
    fit_set marks deadline trades; offseason trades are held out. lower_conf_picks flags trades whose
    return includes vague picks."""
    out = []
    for t in trades:
        a_id, b_id = t["teams"]
        a, b = tri_of.get(a_id), tri_of.get(b_id)
        if not a or not b:
            continue
        gotA, gotB = t["players"].get(a_id, []), t["players"].get(b_id, [])
        pickA, pickB = t["picks"].get(a_id, 0), t["picks"].get(b_id, 0)

        def items(pids, from_team):
            return [{"pid": p, "salary": player_salary(p, from_team, sal_map), "label": str(p)} for p in pids]

        out.append({
            "date": t["date"].isoformat(), "group": t["group"],
            "fit_set": t["date"] >= DEADLINE_CUTOFF, "lower_conf_picks": (pickA + pickB) > 0,
            "A": a, "B": b,
            # raw pick COUNTS (the points-per-pick conversion is a tunable knob in backtest_tune)
            "A_receives": items(gotA, b), "A_sends": items(gotB, a), "A_pick_count": pickA,
            "B_receives": items(gotB, a), "B_sends": items(gotA, b), "B_pick_count": pickB,
        })
    return out


# --------------------------------- synthetic fleeces ------------------------------------------- #
def _load_csv(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def generate_fleeces():
    """Per-team synthetic negatives the acceptance gate must REJECT, of two kinds:
      (a) quality-for-scraps: the team sends its highest-net player for a minimum-salary throw-in,
      (b) redundant-archetype: the team acquires a player who duplicates its strongest dimension and
          fills no measured need, sending a useful rotation piece for him.
    Generated from current rosters/values; a fleece is a fleece regardless of as-of-date."""
    surplus = {r["player_id"]: r for r in _load_csv("player_surplus.csv")}
    dims = {r["player_id"]: r for r in _load_csv("player_dimensions.csv")}
    needs = collections.defaultdict(dict)
    for r in _load_csv("team_needs.csv"):
        needs[r["team_abbr"]][r["dimension"]] = float(r["need"])
    by_team = collections.defaultdict(list)
    for pid, r in surplus.items():
        if r["consensus_net"] != "" and float(r["salary_2026_27"] or 0) > 4_000_000:
            by_team[r["team_abbr"]].append((pid, float(r["consensus_net"]), float(r["salary_2026_27"] or 0)))
    DIMS = ["hc_creation", "secondary_playmaking", "off_ball_shooting",
            "def_versatility_poa", "rim_protect_reb", "transition"]
    fleeces = []
    for team, plist in by_team.items():
        plist.sort(key=lambda x: -x[1])
        if len(plist) < 3:
            continue
        star = plist[0]                                    # highest-net player
        # (a) quality-for-scraps: star out, a minimum filler in
        fleeces.append({"type": "quality_for_scraps", "team": team,
                        "sends": [{"pid": star[0], "salary": star[2], "label": "star"}],
                        "receives": [{"pid": None, "salary": 2_300_000, "label": "min filler"}]})
        # (b) redundant-archetype: send a useful mid piece, get a player strong in a NON-need dim
        team_need = needs.get(team, {})
        surplus_dim = min(DIMS, key=lambda d: team_need.get(d, 0.0))      # the team's least-needed axis
        cand = [(pid, float(dims[pid].get(surplus_dim, 0.5))) for pid, _n, _s in plist
                if pid in dims]
        cand.sort(key=lambda x: -x[1])
        if cand and len(plist) >= 2:
            redundant = cand[0][0]
            outpiece = plist[1]                            # a useful rotation player
            fleeces.append({"type": "redundant_archetype", "team": team, "redundant_dim": surplus_dim,
                            "sends": [{"pid": outpiece[0], "salary": outpiece[2], "label": "useful piece"}],
                            "receives": [{"pid": redundant, "salary": 12_000_000, "label": "redundant"}]})
    return fleeces


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true", help="validate reconstruction on a deadline trade")
    ap.add_argument("--packages", action="store_true", help="assemble trade packages + fleeces (mechanical)")
    args = ap.parse_args()

    if args.packages:
        tri_of = team_tricode_map()
        trades = two_team_trades()
        sal_map = salaries_2025_26()
        pkgs = build_packages(trades, tri_of, sal_map)
        fit = [p for p in pkgs if p["fit_set"]]
        held = [p for p in pkgs if not p["fit_set"]]
        print(f"=== trade packages: {len(pkgs)} two-team trades ({len(fit)} FIT deadline, {len(held)} HELD-OUT offseason) ===")
        for p in sorted(pkgs, key=lambda x: x["date"])[:4]:
            tag = "FIT" if p["fit_set"] else "HELD-OUT"
            arec = ", ".join(f"{i['label']}(${i['salary']/1e6:.0f}M)" for i in p["A_receives"])
            brec = ", ".join(f"{i['label']}(${i['salary']/1e6:.0f}M)" for i in p["B_receives"])
            print(f"  [{tag}] {p['date']} {p['A']}<->{p['B']}: {p['A']} gets [{arec}] | {p['B']} gets [{brec}]")
        fleeces = generate_fleeces()
        qfs = [f for f in fleeces if f["type"] == "quality_for_scraps"]
        red = [f for f in fleeces if f["type"] == "redundant_archetype"]
        print(f"\n=== synthetic fleeces: {len(fleeces)} ({len(qfs)} quality-for-scraps, {len(red)} redundant-archetype) ===")
        for f in fleeces[:4]:
            print(f"  {f['team']} {f['type']}: sends {f['sends'][0]['label']} for {f['receives'][0]['label']}"
                  + (f" (dim {f.get('redundant_dim')})" if f.get("redundant_dim") else ""))
        print("\n  (decide() wiring + tuning deferred until after the team_state apron rebuild)")
        return

    tri_of = team_tricode_map()
    trades = two_team_trades()
    print(f"=== {len(trades)} genuine two-team trades in window (2025-07-01 .. now) ===")
    deadline = [t for t in trades if t["date"] >= date(2026, 1, 1)]
    offseas = [t for t in trades if t["date"] < date(2026, 1, 1)]
    print(f"   deadline/in-season (clean snapshot reconstruction): {len(deadline)}")
    print(f"   2025 offseason (2024-25-end + replay, lower conf):  {len(offseas)}")

    # validate: reconstruct rosters as of a Feb 2026 deadline trade and confirm the received players
    # were on the OTHER team's roster the day before (the receiving team did not already have them).
    for t in sorted(deadline, key=lambda x: x["date"])[:3]:
        rosters, conf = rosters_as_of(t["date"], tri_of)
        a, b = tri_of.get(t["teams"][0]), tri_of.get(t["teams"][1])
        print(f"\n  trade {t['group']} on {t['date']}  [{a} <-> {b}]  reconstruction: {conf}")
        for team_id, got in t["players"].items():
            recv = tri_of.get(team_id)
            other = b if recv == a else a
            pre_other = rosters.get(other, set())
            on_other = sum(1 for p in got if p in pre_other)
            print(f"    {recv} received {len(got)} -> {on_other}/{len(got)} were on {other}'s pre-trade roster")


if __name__ == "__main__":
    main()
