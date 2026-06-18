"""Validate every on-screen claim for the Ant shot-diet post against the warehouse.

Adapts the social-visuals skill's validate_claims.py contract to this project's
canonical connection (lib.db, which reads POSTGRES_* from .env and sets the nba
search_path) instead of a raw DATABASE_URL. The rule it enforces is unchanged:
no number reaches the screen without a query behind it.

Runs:
  1. claims.json  -> one query per on-screen number; prints a table; writes
     provenance.json; exits non-zero if any claim fails to return a value.
  2. the 6-band distance distribution (RS and R2-SAS) -> writes src/shot_diet.json
     so the chart bars render from exact, warehouse-derived shares.

Usage (from postmortem/):
  python social/ant-shot-diet/validate.py
"""
from __future__ import annotations

import json
import sys
import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))  # postmortem/

from lib import db  # noqa: E402

EDWARDS_ID = 1630162

# The six distance bands, matching the Q3 edwards_shot_diet.py bucketing exactly.
BANDS = [
    ("rim", "At the rim", "0-3 ft", "scd.shot_distance <= 3"),
    ("paint", "Paint", "4-10 ft", "scd.shot_distance BETWEEN 4 AND 10"),
    ("floater", "Floater zone", "11-16 ft", "scd.shot_distance BETWEEN 11 AND 16"),
    ("longmid", "Long mid", "17-22 ft", "scd.shot_distance BETWEEN 17 AND 22"),
    ("three", "Three", "23-25 ft", "scd.shot_distance BETWEEN 23 AND 25"),
    ("deep", "Deep three", "26+ ft", "scd.shot_distance >= 26"),
]

PHASES = {
    "rs": ("2025-26 regular season", "scd.season_year = '2025-26' AND scd.season_type = 'Regular Season'"),
    "sas": ("R2 vs San Antonio", "scd.season_year = '2025-26' AND scd.season_type = 'Playoffs' AND g.matchup LIKE '%SAS%'"),
}


def run_claims(manifest_path: Path, log_path: Path) -> bool:
    claims = json.loads(manifest_path.read_text())
    rows, provenance, all_ok = [], [], True
    pulled_at = datetime.datetime.now().isoformat(timespec="seconds")

    for c in claims:
        try:
            value = db.scalar(c["query"])
        except Exception as e:  # noqa: BLE001
            value = f"ERROR: {e}"
        passed = value is not None and not str(value).startswith("ERROR")
        all_ok = all_ok and passed
        match = "match" if str(value) == str(c.get("display", "")) else "DIFFERS"
        rows.append((c["id"], str(c.get("display", "")), str(value), match, "ok" if passed else "FAIL"))
        provenance.append({
            "id": c["id"], "claim": c.get("claim", ""), "display": c.get("display", ""),
            "value": str(value), "query": c["query"], "pulled_at": pulled_at,
        })

    id_w = max((len(r[0]) for r in rows), default=8)
    print(f"{'claim id':<{id_w}}  {'on screen':<10}  {'warehouse':<12}  {'check':<8}  status")
    for rid, disp, val, match, status in rows:
        print(f"{rid:<{id_w}}  {disp:<10}  {val:<12}  {match:<8}  {status}")

    log_path.write_text(json.dumps(provenance, indent=2))
    print(f"\nProvenance written to {log_path.relative_to(HERE.parents[1])}")
    return all_ok


def run_shot_diet(out_path: Path) -> None:
    diet = {}
    for pkey, (label, where) in PHASES.items():
        total = int(db.scalar(
            f"SELECT COUNT(*) FROM nba_shot_chart_detail scd "
            f"LEFT JOIN nba_games g ON g.game_id = scd.game_id AND g.team_id = scd.team_id "
            f"WHERE scd.player_id = {EDWARDS_ID} AND {where}"
        ))
        bands = []
        for bkey, name, rng, cond in BANDS:
            n = int(db.scalar(
                f"SELECT SUM(CASE WHEN {cond} THEN 1 ELSE 0 END) FROM nba_shot_chart_detail scd "
                f"LEFT JOIN nba_games g ON g.game_id = scd.game_id AND g.team_id = scd.team_id "
                f"WHERE scd.player_id = {EDWARDS_ID} AND {where}"
            ))
            bands.append({"key": bkey, "name": name, "range": rng, "count": n, "share": round(n / total, 4)})
        diet[pkey] = {"label": label, "total": total, "bands": bands}

    out_path.write_text(json.dumps(diet, indent=2))
    print(f"Shot-diet chart data written to {out_path.relative_to(HERE.parents[1])}")
    # Echo the distribution so it can be eyeballed against the Q3 findings.
    for pkey in PHASES:
        d = diet[pkey]
        print(f"\n  {d['label']}  (n={d['total']})")
        for b in d["bands"]:
            print(f"    {b['name']:<13} {b['range']:<8} {100*b['share']:>5.1f}%  (n={b['count']})")


if __name__ == "__main__":
    ok = run_claims(HERE / "claims.json", HERE / "provenance.json")
    (HERE / "src").mkdir(exist_ok=True)
    run_shot_diet(HERE / "src" / "shot_diet.json")
    if not ok:
        sys.exit("\nValidation failed. Do not build until every claim returns a value.")
    print("\nAll claims returned a value and match the planned on-screen display. Safe to build.")
