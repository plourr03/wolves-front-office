#!/usr/bin/env python3
"""
verified_contracts.py  -- Phase 2-D follow-up: the verified salary source.

Reads nba.nba_player_contracts (Basketball-Reference, per-season salary + option_type) from the
warehouse and exposes it to the trade model with three pieces of plumbing the raw table needs:

  1. ENCODING-ROBUST nba_player_id resolution. The table has no nba_player_id and its player_name
     column is double-encoded (Joki -> mojibake), so a naive name join silently drops accented stars
     (Jokic, Doncic, Sengun, ...). We repair the double-encoding (latin-1 -> utf-8), normalize like
     the trade_search resolver (accent/punct/suffix folding), and resolve against nba_player_bio (the
     clean league-wide id authority), disambiguating name collisions by the contract row's team.

  2. WAIVE-AND-STRETCH DEAD MONEY. A waived-then-resigned player has two rows (e.g. Beal on PHO dead
     money + LAC active; Lillard on MIL + POR). The ACTIVE team is the one that most recently acquired
     him (latest Signing/Trade in nba_transactions); the other rows are a cap charge only, never a
     tradable asset. (Zubac is NOT this case: he was really traded to IND, so the old scrape had the
     right team and only a copied salary; the verified row fixes the number.)

  3. KICKER / NO-TRADE-CLAUSE MERGE. The verified table carries salary + option_type but not the
     trade_kicker_pct or no_trade_clause the matching engine needs, so those are merged in from the
     legacy nba_contracts_2026_27.csv by nba_player_id.

    python verified_contracts.py            # resolve + report; --write emits the verified CSV
"""

import os
import sys
import csv
import re
import argparse
import unicodedata
import collections

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
from lib import db          # noqa: E402

SEASONS = ["2026-27", "2027-28", "2028-29", "2029-30", "2030-31"]
ACQUIRE_TYPES = ("Signing", "Trade", "ContractConverted", "AwardOnWaivers")
# A waived-then-signed player carries his OLD contract value as dead money on the WAIVING team; his
# new team signs a separate, smaller deal. BBR lists the same original number on both rows, so when
# the active team's figure equals the dead twin, replace it with a new-deal proxy (the 10+ yos vet
# minimum) so the dollars are not double-counted. The real new deal is a Pass-2 lookup.
NEW_DEAL_PROXY = 3_877_000
# names the bio authority cannot match even after the encoding repair (its own copy of the name is
# corrupted too). Keyed by the repaired+normalized CONTRACT name -> verified nba_player_id from bio.
MANUAL_PID = {
    "egor dmin": 1642856,      # Egor Demin (BRK), Cyrillic e; bio name is also mojibake
    "ron holland": 1641842,    # bio lists him as "Ronald Holland II"
}
# Thomas Sorber (OKC, 2025 #15) has not debuted, so he is absent from nba_player_bio and stays
# unresolved. He is a min-salary rookie with no trade relevance; documented, not silently dropped.


def repair(s):
    """Undo the latin-1 -> utf-8 double-encoding in the contract table; no-op on clean ASCII."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        return s


def norm(s):
    s = unicodedata.normalize("NFKD", repair(s or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[.\-']", "", s)
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _ascii(x):
    return str(x).encode("ascii", "backslashreplace").decode()


# BBR / bio position strings -> the model's slot convention (matches BIG_POSITIONS in the engine)
def _pos(p):
    p = (p or "").strip().lower()
    if p.startswith("center") or p in ("c",):
        return "C"
    if "forward" in p and "center" in p:
        return "F-C"
    if p.startswith("forward") or p in ("f",):
        return "F"
    if p.startswith("guard") or p in ("g",):
        return "G"
    return p.upper()[:3]


def name_authority():
    """norm_name -> set(nba_player_id); pid -> recent team_abbreviation; pid -> position; from
    nba_player_bio (clean NBA-sourced names) unioned with recent season bios for new rookies."""
    byname = collections.defaultdict(set)
    pid_team, pid_pos = {}, {}
    rows = db.query("SELECT player_id, display_first_last nm, team_abbreviation tm, position pos FROM nba_player_bio")
    for _, r in rows.iterrows():
        pid = int(r.player_id)
        byname[norm(r.nm)].add(pid)
        if r.tm:
            pid_team[pid] = r.tm
        if r.pos:
            pid_pos[pid] = _pos(r.pos)
    rows = db.query("""SELECT DISTINCT player_id, player_name nm, team_abbreviation tm
                       FROM nba_player_season_bio WHERE season_year >= '2024-25'""")
    for _, r in rows.iterrows():
        byname[norm(r.nm)].add(int(r.player_id))
        pid_team.setdefault(int(r.player_id), r.tm)
    return byname, pid_team, pid_pos


def active_team_map():
    """nba_player_id -> team_id of the most recent acquisition (Signing/Trade/...). A waive is NOT an
    acquisition, so a waived-then-signed player maps to the team that re-signed him."""
    import pandas as pd
    rows = db.query(f"""
        SELECT DISTINCT ON (player_id) player_id, team_id, transaction_type, transaction_date
        FROM nba_transactions
        WHERE transaction_type IN {ACQUIRE_TYPES} AND player_id IS NOT NULL AND team_id IS NOT NULL
        ORDER BY player_id, transaction_date DESC, additional_sort DESC""")
    return {int(r.player_id): int(r.team_id) for _, r in rows.iterrows()
            if pd.notna(r.player_id) and pd.notna(r.team_id)}


def legacy_kicker_ntc():
    """nba_player_id -> (trade_kicker_pct, no_trade_clause_flag) from the legacy scrape."""
    out = {}
    path = os.path.join(DATA, "nba_contracts_2026_27.csv")
    for r in csv.DictReader(open(path, encoding="utf-8")):
        pid = (r.get("nba_player_id") or "").strip()
        if not pid:
            continue
        try:
            k = float(r.get("trade_kicker_pct") or 0) or 0.0
        except ValueError:
            k = 0.0
        ntc = str(r.get("no_trade_clause_flag") or "").strip().upper() in ("TRUE", "1", "YES")
        out[str(int(float(pid)))] = (k, ntc)
    return out


def resolve(byname, pid_team, name, team_abbr):
    """Repaired+normalized name -> nba_player_id, disambiguating a name collision by team."""
    key = norm(name)
    if key in MANUAL_PID:
        return MANUAL_PID[key], "manual"
    ids = byname.get(key)
    if not ids:
        return None, "unresolved"
    if len(ids) == 1:
        return next(iter(ids)), "unique"
    # collision: prefer the id whose recent bio team matches the contract team
    for pid in ids:
        if pid_team.get(pid) == team_abbr:
            return pid, "team-disambiguated"
    return sorted(ids)[0], "collision-firstid"     # last resort, flagged in the report


def load_verified():
    """Returns players: pid(str) -> dict with active team, per-season salary/option, years_left,
    dead-money rows, and the merged kicker/NTC. Plus diagnostics."""
    byname, pid_team, pid_pos = name_authority()
    active = active_team_map()
    kn = legacy_kicker_ntc()

    rows = db.query(f"""SELECT br_player_id, player_name, team_abbr, nba_team_id, nba_team_tricode,
                               season, salary, option_type
                        FROM nba_player_contracts WHERE season = ANY(%s)""", (SEASONS,))
    tri_of_team = {int(r.nba_team_id): r.nba_team_tricode for _, r in rows.iterrows() if r.nba_team_id}

    # group contract rows by resolved pid
    by_pid = collections.defaultdict(lambda: {"rows": [], "name": "", "teams": set()})
    diag = {"unresolved": [], "collision_firstid": []}
    for _, r in rows.iterrows():
        pid, how = resolve(byname, pid_team, r.player_name, r.team_abbr)
        if pid is None:
            if r.season == "2026-27":
                diag["unresolved"].append((_ascii(r.player_name), r.team_abbr))
            continue
        if how == "collision-firstid" and r.season == "2026-27":
            diag["collision_firstid"].append((_ascii(r.player_name), r.team_abbr, pid))
        e = by_pid[str(pid)]
        e["rows"].append({"team": r.team_abbr, "tri": r.nba_team_tricode, "team_id": int(r.nba_team_id),
                          "season": r.season, "salary": int(r.salary or 0), "option": r.option_type})
        e["name"] = repair(r.player_name)
        e["teams"].add(r.team_abbr)

    players = {}
    for pid, e in by_pid.items():
        active_team_id = active.get(int(pid))
        active_tri = tri_of_team.get(active_team_id) if active_team_id else None
        # choose the team whose rows are "active": the most-recently-acquired team; if unknown or not
        # among this player's contract teams, fall back to the single team (no dead money) or the
        # row with the largest 2026-27 salary (the real contract, not a stretched remnant).
        row_teams = {r["tri"] for r in e["rows"]}
        if active_tri in row_teams:
            chosen = active_tri
        elif len(row_teams) == 1:
            chosen = next(iter(row_teams))
        else:
            s26 = [r for r in e["rows"] if r["season"] == "2026-27"]
            chosen = max(s26, key=lambda r: r["salary"])["tri"] if s26 else sorted(row_teams)[0]
        active_rows = [r for r in e["rows"] if r["tri"] == chosen]
        dead_rows = [r for r in e["rows"] if r["tri"] != chosen]
        sal = {r["season"]: r["salary"] for r in active_rows}
        opt = {r["season"]: r["option"] for r in active_rows}
        # waive-and-stretch: if the active figure equals a dead twin (BBR duplicated the old contract),
        # the player's real obligation on the new team is a small new deal, not the old number.
        dead_by_season = collections.defaultdict(set)
        for r in dead_rows:
            dead_by_season[r["season"]].add(r["salary"])
        new_deal_proxy = False
        for s in SEASONS:
            if sal.get(s, 0) and sal[s] in dead_by_season.get(s, set()):
                sal[s] = NEW_DEAL_PROXY
                new_deal_proxy = True
        years_left = sum(1 for s in SEASONS if sal.get(s, 0) > 0)
        k, ntc = kn.get(pid, (0.0, False))
        players[pid] = {
            "nba_player_id": pid, "player": e["name"], "team_abbr": chosen,
            "position": pid_pos.get(int(pid), ""),
            "salary_2026_27": sal.get("2026-27", 0),
            "salary_2027_28": sal.get("2027-28", 0), "salary_2028_29": sal.get("2028-29", 0),
            "salary_2029_30": sal.get("2029-30", 0),
            "option_2026_27": opt.get("2026-27", ""), "option_2027_28": opt.get("2027-28", ""),
            "option_2028_29": opt.get("2028-29", ""), "option_2029_30": opt.get("2029-30", ""),
            "years_left": years_left,
            "trade_kicker_pct": k, "no_trade_clause_flag": "TRUE" if ntc else "FALSE",
            "dead_money_teams": ";".join(sorted({r["tri"] for r in dead_rows})),
            "dead_money_2026_27": sum(r["salary"] for r in dead_rows if r["season"] == "2026-27"),
        }
    return players, diag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="emit data/nba_contracts_2026_27_verified.csv")
    args = ap.parse_args()

    players, diag = load_verified()
    print(f"=== verified_contracts: {len(players)} players resolved ===")
    print(f"  unresolved 2026-27 rows: {len(diag['unresolved'])} {diag['unresolved']}")
    print(f"  collision-firstid (verify): {diag['collision_firstid']}")

    print("\n  dead-money (waive-and-stretch) cases -> active team / cap-charge team:")
    for pid, p in players.items():
        if p["dead_money_teams"]:
            print(f"    {p['player']:22} active {p['team_abbr']}  ${p['salary_2026_27']/1e6:.1f}M | "
                  f"dead money on {p['dead_money_teams']} (${p['dead_money_2026_27']/1e6:.1f}M)")

    print("\n  spot-checks:")
    bypid = {p["player"]: p for p in players.values()}
    for nm in ("Nikola Jokic", "Luka Doncic", "Ivica Zubac", "Bradley Beal", "Damian Lillard"):
        key = next((k for k in bypid if norm(k) == norm(nm)), None)
        if key:
            p = bypid[key]
            print(f"    {nm:18} -> id {p['nba_player_id']:8} team {p['team_abbr']:4} "
                  f"${p['salary_2026_27']/1e6:5.1f}M opt={p['option_2026_27']:14} yrs={p['years_left']} "
                  f"kicker={p['trade_kicker_pct']}")

    if args.write:
        fields = ["team_abbr", "player", "nba_player_id", "position", "salary_2026_27", "salary_2027_28",
                  "salary_2028_29", "salary_2029_30", "years_left", "option_2026_27", "option_2027_28",
                  "option_2028_29", "option_2029_30",
                  "trade_kicker_pct", "no_trade_clause_flag", "dead_money_teams", "dead_money_2026_27"]
        out = os.path.join(DATA, "nba_contracts_2026_27_verified.csv")
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for p in sorted(players.values(), key=lambda r: (r["team_abbr"], -r["salary_2026_27"])):
                # blank 0-salary out-years so the legacy non-blank-count years_left logic still works
                row = {k: (("" if (k.startswith("salary_") and not p.get(k)) else p.get(k, ""))) for k in fields}
                w.writerow(row)
        print(f"\n  wrote {out} ({len(players)} players)")


if __name__ == "__main__":
    main()
