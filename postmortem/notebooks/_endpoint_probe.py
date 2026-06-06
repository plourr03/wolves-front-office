"""Quick probe of leaguedashplayerbiostats and commonplayerinfo.

Goal: see what columns each endpoint actually returns so we can decide
which fields to persist in the player_dim and stints tables.

Uses the same curl_cffi + Akamai bypass session the warehouse pipeline
uses, by importing nba_session from the sibling repo.
"""
import sys
import json
from pathlib import Path

# Make the warehouse's nba_session importable.
PIPELINE_DIR = Path(__file__).resolve().parents[2] / "nba-warehouse" / "pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

import nba_session  # noqa: E402

nba_session.patch_nba_api()

from nba_api.stats.endpoints import leaguedashplayerbiostats, commonplayerinfo  # noqa: E402


def section(title):
    print(f"\n{'='*72}\n{title}\n{'='*72}")


# 1. leaguedashplayerbiostats — one call per season, returns all players that season
section("leaguedashplayerbiostats: season=2025-26")
resp = leaguedashplayerbiostats.LeagueDashPlayerBioStats(
    season="2025-26",
    season_type_all_star="Regular Season",
)
ds = resp.get_dict()["resultSets"][0]
headers = ds["headers"]
rows = ds["rowSet"]
print(f"  total players returned: {len(rows)}")
print(f"  headers ({len(headers)}):")
for h in headers:
    print(f"    {h}")

print("\n  sample row (Anthony Edwards if present, else first):")
sample = None
for r in rows:
    name = r[headers.index("PLAYER_NAME")]
    if name == "Anthony Edwards":
        sample = r
        break
if sample is None:
    sample = rows[0]
for h, v in zip(headers, sample):
    print(f"    {h:<24} {v}")


# 2. commonplayerinfo — one call per player, deeper profile
section("commonplayerinfo: player_id=1630162 (Anthony Edwards)")
resp2 = commonplayerinfo.CommonPlayerInfo(player_id=1630162)
result_sets = resp2.get_dict()["resultSets"]
for rs in result_sets:
    name = rs["name"]
    headers = rs["headers"]
    rows = rs["rowSet"]
    print(f"\n  resultSet: {name}  ({len(rows)} rows, {len(headers)} cols)")
    for h in headers:
        print(f"    {h}")
    if rows:
        print(f"\n  sample row:")
        for h, v in zip(headers, rows[0]):
            print(f"    {h:<28} {v}")


# 3. Sanity check: do the two endpoints share fields, or are they complementary?
section("Field overlap analysis")
biostats_headers = leaguedashplayerbiostats.LeagueDashPlayerBioStats(
    season="2025-26", season_type_all_star="Regular Season"
).get_dict()["resultSets"][0]["headers"]
cpi_headers = []
for rs in commonplayerinfo.CommonPlayerInfo(player_id=1630162).get_dict()["resultSets"]:
    cpi_headers.extend(rs["headers"])

bs = set(biostats_headers)
cs = set(cpi_headers)
print(f"  in BOTH ({len(bs & cs)}):")
for h in sorted(bs & cs):
    print(f"    {h}")
print(f"\n  ONLY in leaguedashplayerbiostats ({len(bs - cs)}):")
for h in sorted(bs - cs):
    print(f"    {h}")
print(f"\n  ONLY in commonplayerinfo ({len(cs - bs)}):")
for h in sorted(cs - bs):
    print(f"    {h}")
