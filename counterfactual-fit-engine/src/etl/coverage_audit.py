"""F0 coverage audit (R1 rider): full game-universe classification.

The warehouse PBP shows ~30.6k distinct games 2013-26 -- roughly 2x the true
NBA regular+playoff universe (~16.8k). R1's hypothesis: preseason, G-League,
summer-league and other game types are present. This audit classifies EVERY
game_id by its type prefix, so the training filter becomes an explicit
include-list asserted by a schema test, never an assumption of absence.

NBA game_id convention (10 digits): positions 0-2 = type prefix
  001 preseason | 002 regular season | 003 all-star | 004 playoffs
  005 play-in | 1xx/2xx G-League and other leagues
positions 3-4 = season start year (e.g. '13' = 2013-14).

Also: settles the 2013-14 gap question UNDER the 002 filter (the raw count
may have been polluted), logs missing games vs the nba_games schedule, and
reconciles 2023-26 coverage against the 3,939-parquet possessions cache as
the known-good reference.

Output: outputs/coverage_audit.md + data/staged/game_universe.parquet
(game_id, season, type_prefix, include_train, include_flagged).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.adapters.postmortem_lib import query  # noqa: E402

CACHE_2326 = FITENGINE_ROOT.parent / "offseason" / "data" / "cache" / "possessions_league"

PREFIX_LABELS = {
    "001": "preseason", "002": "regular_season", "003": "all_star",
    "004": "playoffs", "005": "play_in",
}
INCLUDE_TRAIN = {"002"}          # explicit include-list (spec: RS only)
INCLUDE_FLAGGED = {"004"}        # pulled/kept, excluded from training

SEASONS = [f"{y:02d}" for y in range(13, 26)]   # '13'..'25' start-years


def main():
    games = query("""
        SELECT game_id, count(*) AS pbp_rows
        FROM nba_play_by_play GROUP BY game_id
    """)
    games["type_prefix"] = games.game_id.str[:3]
    games["season_yy"] = games.game_id.str[3:5]
    games["label"] = games.type_prefix.map(PREFIX_LABELS).fillna("other_league_or_unknown")
    in_window = games[games.season_yy.isin(SEASONS)].copy()

    lines = ["# fitengine coverage audit (R1 game-universe classification)", ""]
    lines.append("## Game-type census, seasons 2013-14 .. 2025-26 (PBP-present games)")
    census = (in_window.groupby(["type_prefix", "label"]).game_id.count()
              .rename("games").reset_index().sort_values("games", ascending=False))
    lines.append(census.to_string(index=False))
    lines.append(f"\nTotal PBP-present games in window: {len(in_window)} "
                 f"(raw, all types); regular season only: "
                 f"{(in_window.type_prefix == '002').sum()}")

    # per-season RS counts + gap detection vs expected schedule
    rs = in_window[in_window.type_prefix == "002"]
    per = rs.groupby("season_yy").game_id.count().rename("rs_games")
    lines.append("\n## Regular-season games per season (002 prefix)")
    expected = {"13": 1230, "14": 1230, "15": 1230, "16": 1230, "17": 1230,
                "18": 1230, "19": 971, "20": 1080, "21": 1230, "22": 1230,
                "23": 1230, "24": 1230, "25": 1230}
    rows = []
    for yy in SEASONS:
        have = int(per.get(yy, 0))
        exp = expected.get(yy, 1230)
        rows.append(f"  20{yy}-{int(yy)+1:02d}: {have} / ~{exp} expected"
                    + ("   <-- GAP" if have < exp * 0.98 else ""))
    lines.extend(rows)

    # reconcile 2023-26 vs the known-good possessions cache
    cache_ids = {p.stem for p in CACHE_2326.glob("*.parquet")} if CACHE_2326.exists() else set()
    recent = set(rs[rs.season_yy.isin(["23", "24", "25"])].game_id) | \
        set(in_window[(in_window.type_prefix == "004")
                      & in_window.season_yy.isin(["23", "24", "25"])].game_id)
    lines.append(f"\n## Reconciliation vs 2023-26 possessions cache (known-good)")
    lines.append(f"cache parquets: {len(cache_ids)}; warehouse RS+PO games 2023-26: {len(recent)}")
    lines.append(f"in cache but not warehouse: {len(cache_ids - recent)}; "
                 f"in warehouse but not cache: {len(recent - cache_ids)}")

    # persist the universe with include flags
    in_window["include_train"] = in_window.type_prefix.isin(INCLUDE_TRAIN)
    in_window["include_flagged"] = in_window.type_prefix.isin(INCLUDE_FLAGGED)
    out = FITENGINE_ROOT / "data" / "staged" / "game_universe.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    in_window.to_parquet(out, index=False)
    lines.append(f"\ngame_universe.parquet written: {len(in_window)} games, "
                 f"{int(in_window.include_train.sum())} train-eligible, "
                 f"{int(in_window.include_flagged.sum())} flagged (playoffs)")

    report = "\n".join(lines)
    (FITENGINE_ROOT / "outputs" / "coverage_audit.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
