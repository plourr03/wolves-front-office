#!/usr/bin/env python3
"""
validate_contracts.py  -- Phase 2, Component D: salary data hygiene.

Acceptance and CBA matching are exact-number sensitive, and the contract book is Pass-1 scrape
quality with known errors (the Zubac-on-IND row, where a Clipper was mislabeled onto Indiana with
Andrew Nembhard's salary). This script automates the per-deal Spotrac verify the findings doc says
every surfaced trade needs: it checks the book for stale team assignments, duplicate or unjoinable
rows, and suspicious salary collisions, writes the hard-bad rows to data/contract_validation_flags.csv
(which the engine reads to refuse to surface a deal touching a bad number), and exits non-zero on any
hard error.

This does NOT invent salaries. Replacing the book with verified Spotrac-grade numbers is a data pull;
this tool only finds what is wrong and gates the engine so a wrong number cannot quietly produce a
"real" deal. Two truth inputs plug in when available, both optional:
  data/contract_known_bad.csv   curated (nba_player_id, team_abbr, reason) confirmed-bad rows.
  data/roster_truth.csv         verified (nba_player_id, team_abbr) 2026-27 rosters (Spotrac pull);
                                any contract row whose team disagrees is hard-flagged.

    python validate_contracts.py            # report + write flags; exit 1 on hard errors
    python validate_contracts.py --quiet     # flags + summary only
"""

import os
import sys
import csv
import argparse
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

SALARY_FLOOR = 4_000_000          # below this, a row is filler/min and not trade-relevant
TEAM_TOTAL_TOL = 12_000_000       # contract-sum vs apron_team_salary gap that is worth a look
MIN_ROSTER, MAX_ROSTER = 12, 21   # plausible rows-with-salary per team


def _sal(r):
    try:
        return int(float(r.get("salary_2026_27") or 0))
    except (ValueError, TypeError):
        return 0


def load_contracts():
    # prefer the verified warehouse source; fall back to the legacy scrape
    verified = os.path.join(DATA, "nba_contracts_2026_27_verified.csv")
    path = verified if os.path.exists(verified) else os.path.join(DATA, "nba_contracts_2026_27.csv")
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_optional(name, key_cols):
    """Read an optional truth CSV into a list of dicts; [] if the file is absent."""
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if all(r.get(c) for c in key_cols)]


def validate(rows):
    """Return (hard, warn): lists of {nba_player_id, team_abbr, player, issue, severity}."""
    hard, warn = [], []

    def flag(dst, r, issue):
        dst.append({"nba_player_id": (r.get("nba_player_id") or "").strip(),
                    "team_abbr": r.get("team_abbr", ""), "player": r.get("player", ""),
                    "issue": issue})

    # 1 (HARD): duplicate nba_player_id with more than one PRICED row -> genuine which-team ambiguity.
    #    (Blank-salary duplicates are FA/two-way candidates listed on several cap sheets; not an error.)
    by_id = collections.defaultdict(list)
    for r in rows:
        pid = (r.get("nba_player_id") or "").strip()
        if pid:
            by_id[pid].append(r)
    for pid, rs in by_id.items():
        priced = [r for r in rs if _sal(r) > 0]
        if len(priced) > 1 and len({r["team_abbr"] for r in priced}) > 1:
            for r in priced:
                flag(hard, r, f"duplicate nba_player_id {pid} priced on {len(priced)} teams")

    # 2 (HARD): a priced row that cannot be joined (blank nba_player_id).
    for r in rows:
        if not (r.get("nba_player_id") or "").strip() and _sal(r) > 0:
            flag(hard, r, "priced row has blank nba_player_id (cannot join to value/dimensions)")

    # 3 (HARD): curated confirmed-bad rows (the Zubac-on-IND class).
    known_bad = {(r["nba_player_id"].strip(), r["team_abbr"].strip()): r.get("reason", "")
                 for r in load_optional("contract_known_bad.csv", ("nba_player_id", "team_abbr"))}
    for r in rows:
        key = ((r.get("nba_player_id") or "").strip(), r.get("team_abbr", "").strip())
        if key in known_bad:
            flag(hard, r, f"known-bad: {known_bad[key]}")

    # 4 (HARD, only if a verified roster is supplied): team assignment disagrees with truth.
    truth = {r["nba_player_id"].strip(): r["team_abbr"].strip()
             for r in load_optional("roster_truth.csv", ("nba_player_id", "team_abbr"))}
    for r in rows:
        pid = (r.get("nba_player_id") or "").strip()
        if pid in truth and _sal(r) > 0 and r.get("team_abbr", "").strip() != truth[pid]:
            flag(hard, r, f"team {r['team_abbr']} disagrees with roster_truth ({truth[pid]})")

    # 5 (WARN): two different players on one team with the same exact salary above the floor.
    #    This is the Zubac=Nembhard salary-copy tell; it also fires on legit shared-max pairs
    #    (Holmgren/J.Williams), so it is a review flag, not a hard error.
    by_ts = collections.defaultdict(list)
    for r in rows:
        if _sal(r) > SALARY_FLOOR:
            by_ts[(r["team_abbr"], _sal(r))].append(r["player"])
    for (team, sal), plist in by_ts.items():
        if len(set(plist)) > 1:
            for r in rows:
                if r["team_abbr"] == team and _sal(r) == sal:
                    flag(warn, r, f"exact-salary collision on {team} ${sal:,}: {sorted(set(plist))}")

    # 6 (WARN): team contract-sum far from the apron_team_salary the cap layer recorded.
    posture = {r["team_abbr"]: r for r in load_optional("team_posture.csv", ("team_abbr",))}
    by_team_sum, by_team_n = collections.defaultdict(int), collections.defaultdict(int)
    for r in rows:
        s = _sal(r)
        by_team_sum[r["team_abbr"]] += s
        if s > 0:
            by_team_n[r["team_abbr"]] += 1
    for team, tot in by_team_sum.items():
        if team in posture:
            try:
                apron = int(float(posture[team]["apron_team_salary"]))
            except (ValueError, TypeError, KeyError):
                continue
            if abs(tot - apron) > TEAM_TOTAL_TOL:
                warn.append({"nba_player_id": "", "team_abbr": team, "player": "",
                             "issue": f"team salary-sum ${tot/1e6:.1f}M vs apron ${apron/1e6:.1f}M "
                                      f"(gap ${(tot-apron)/1e6:+.1f}M); often dup/FA rows"})
        n = by_team_n.get(team, 0)
        if team in posture and not (MIN_ROSTER <= n <= MAX_ROSTER):
            warn.append({"nba_player_id": "", "team_abbr": team, "player": "",
                         "issue": f"{n} priced rows (outside {MIN_ROSTER}-{MAX_ROSTER})"})

    return hard, warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    rows = load_contracts()
    hard, warn = validate(rows)

    # write the hard flags the engine reads to gate deals (dedup on player+team+issue)
    seen, flag_rows = set(), []
    for f in hard:
        k = (f["nba_player_id"], f["team_abbr"], f["issue"])
        if k not in seen:
            seen.add(k)
            flag_rows.append(f)
    with open(os.path.join(DATA, "contract_validation_flags.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["nba_player_id", "team_abbr", "player", "issue"])
        w.writeheader()
        w.writerows(flag_rows)

    if not args.quiet:
        print(f"=== validate_contracts: {len(rows)} contract rows ===")
        print(f"\nHARD errors ({len(flag_rows)}):" if flag_rows else "\nHARD errors: none")
        for f in flag_rows:
            print(f"  [HARD] {f['team_abbr']:4} {f['player']:24} {f['issue']}")
        print(f"\nWARNINGS ({len(warn)}, review; not blocking):")
        for f in warn[:40]:
            tag = f"{f['team_abbr']:4} {f['player']:24}".rstrip()
            print(f"  [warn] {tag}  {f['issue']}")
        if len(warn) > 40:
            print(f"  ... and {len(warn)-40} more")

    print(f"\nwrote data/contract_validation_flags.csv ({len(flag_rows)} hard-flagged rows)")
    if flag_rows:
        print(f"FAIL: {len(flag_rows)} hard contract error(s). The engine will refuse/flag deals "
              f"touching these rows.")
        return 1
    print("OK: no hard contract errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
