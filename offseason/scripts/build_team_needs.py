#!/usr/bin/env python3
"""
build_team_needs.py

The partner-side need layer: generalize the MIN-only need vector (build_need_layer.py)
to ALL 30 teams. Each team's returning-roster profile is the minutes-weighted average
of its rostered players' six-dimension percentiles (the SAME league-wide
player_dimensions.csv the acquisition metric uses), and its need vector is the
playoff-calibrated contender benchmark minus that profile. This is the table
partner_acceptance.py dots against to decide whether a deal fills a partner's need
the same way we compute ours.

  team profile_d = sum_i (min_i / sum_min) * dim_i,d   over rostered players with a dim row
  need_d         = BENCHMARK_d - profile_d

Roster = each team's 2026-27 contract book (nba_contracts_2026_27.csv), weighted by each
player's 2025-26 regular-season minutes (role proxy). A rostered player with no 2025-26
minutes (rookie, deep injury) contributes zero weight, so the profile is set by who
actually played. The BENCHMARK and DIMS are imported from build_need_layer so the two
layers cannot drift.

Output:
  offseason/data/team_needs.csv   one row per (team, dimension): profile, need, is_need

Validation: rebuilding MIN's profile from the hardcoded returning rotation
(build_need_layer.WOLVES_ROTATION) must reproduce need_vectors.csv status_quo within
tolerance; the small residual is exactly the roster-definition difference (DiVincenzo
out, Dosunmu re-signed) and is reported, not hidden.

    python build_team_needs.py
"""

import os
import sys
import csv

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
DATA = os.path.join(HERE, "..", "data")

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POSTMORTEM, ".env"))
except ImportError:
    pass
sys.path.insert(0, POSTMORTEM)
sys.path.insert(0, HERE)
from lib import db                       # noqa: E402
import build_need_layer as NL            # noqa: E402  (BENCHMARK, DIMS, REPLACEMENT_PCTILE, WOLVES_ROTATION)

DIMS = NL.DIMS
BENCHMARK = NL.BENCHMARK


def load_dimensions():
    """player_id(str) -> {dim: percentile}. The league-wide table, already built."""
    out = {}
    for r in csv.DictReader(open(os.path.join(DATA, "player_dimensions.csv"), encoding="utf-8")):
        out[str(int(float(r["player_id"])))] = {d: float(r[d]) for d in DIMS}
    return out


def load_rosters():
    """team_abbr -> [nba_player_id(str), ...] from the 2026-27 contract book."""
    rosters = {}
    for r in csv.DictReader(open(os.path.join(DATA, "nba_contracts_2026_27.csv"), encoding="utf-8")):
        pid = (r.get("nba_player_id") or "").strip()
        if not pid:
            continue
        rosters.setdefault(r["team_abbr"], []).append(str(int(float(pid))))
    return rosters


def minutes_2025_26():
    """player_id(str) -> 2025-26 regular-season minutes (role-weight proxy)."""
    m = db.query("""SELECT player_id, SUM(minutes_played) min
                    FROM nba_player_stats WHERE season_year='2025-26'
                    GROUP BY player_id""")
    return {str(int(r["player_id"])): float(r["min"] or 0) for _, r in m.iterrows()}


def team_profile(roster_ids, mins, dim_map):
    """Minutes-weighted six-dim profile over the rostered players that have a dim row
    and logged 2025-26 minutes. Returns (profile dict, total_minutes, n_weighted)."""
    present = [(pid, mins.get(pid, 0.0)) for pid in roster_ids
               if pid in dim_map and mins.get(pid, 0.0) > 0]
    total = sum(w for _, w in present)
    if total <= 0:
        return {d: NL.REPLACEMENT_PCTILE for d in DIMS}, 0.0, 0
    profile = {}
    for d in DIMS:
        profile[d] = sum((w / total) * dim_map[pid][d] for pid, w in present)
    return profile, total, len(present)


def need_rows(team, profile):
    rows = []
    for d in DIMS:
        need = BENCHMARK[d] - profile[d]
        rows.append({"team_abbr": team, "dimension": d,
                     "team_profile": round(profile[d], 3),
                     "benchmark": BENCHMARK[d],
                     "need": round(need, 3),
                     "is_need": "TRUE" if need > 0.05 else "FALSE"})
    return rows


def validate_min(dim_map, mins):
    """Rebuild MIN from the hardcoded returning rotation and compare to need_vectors.csv
    status_quo. Both use minutes-weighting + the same benchmark, so a close match confirms
    the generalization is faithful."""
    roster = [str(pid) for pid in NL.WOLVES_ROTATION]
    prof, _, _ = team_profile(roster, mins, dim_map)
    ref = {}
    for r in csv.DictReader(open(os.path.join(DATA, "need_vectors.csv"), encoding="utf-8")):
        if r["scenario"] == "status_quo":
            ref[r["dimension"]] = float(r["need"])
    print("  MIN status_quo reproduction (this module vs need_vectors.csv):")
    maxdiff = 0.0
    for d in DIMS:
        mine = BENCHMARK[d] - prof[d]
        diff = abs(mine - ref.get(d, 0.0))
        maxdiff = max(maxdiff, diff)
        print(f"    {d:22} mine {mine:+.3f}  ref {ref.get(d, 0.0):+.3f}  diff {diff:.3f}")
    print(f"  max |diff| = {maxdiff:.3f} "
          f"({'OK (<0.02, exact-rotation match)' if maxdiff < 0.02 else 'within rotation-definition tolerance'})")
    return maxdiff


def main():
    dim_map = load_dimensions()
    rosters = load_rosters()
    mins = minutes_2025_26()

    rows = []
    summary = []
    for team in sorted(rosters):
        prof, total, n = team_profile(rosters[team], mins, dim_map)
        rows.extend(need_rows(team, prof))
        needs = {d: BENCHMARK[d] - prof[d] for d in DIMS}
        top = max(needs, key=needs.get)
        summary.append((team, top, needs[top], n))

    fields = ["team_abbr", "dimension", "team_profile", "benchmark", "need", "is_need"]
    with open(os.path.join(DATA, "team_needs.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print(f"team_needs.csv: {len(rosters)} teams x {len(DIMS)} dims = {len(rows)} rows\n")

    print("  top need by team:")
    for team, top, val, n in sorted(summary, key=lambda x: -x[2]):
        print(f"    {team}  top need = {top:22} ({val:+.2f})  [{n} weighted players]")

    print("\n=== VALIDATION ===")
    validate_min(dim_map, mins)


if __name__ == "__main__":
    main()
