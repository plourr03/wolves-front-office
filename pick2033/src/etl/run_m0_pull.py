"""M0 driver: fetch + parse + stage all B-Ref training data.

Pages (~126 network fetches on first run, permanent cache thereafter):
  season standings 1980-2026, player advanced 1979-2026,
  drafts 1990-2019, All-League awards.
Outputs (data/staged/):
  franchise_seasons_raw.parquet   one row per franchise-season (W/L, SRS, conf)
  player_impact_seasons.parquet   combined + stint rows, franchise-mapped
  draft_picks.parquet             (draft_year, slot, player_id)
  all_nba.parquet                 (season, tier, player_id)
Derived fields (core_age, continuity_pct, had_star, draft value_4yr) are
computed in the warehouse build step, not here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.etl.bref_client import fetch, strip_comment_tables
from src.etl.bref_parsers import (
    parse_advanced_players,
    parse_all_league,
    parse_draft,
    parse_season_standings,
)
from src.etl.franchise_map import to_franchise

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGED = PROJECT_ROOT / "data" / "staged"

SEASONS_STANDINGS = range(1980, 2027)   # ending-year convention
SEASONS_ADVANCED = range(1979, 2027)    # 1979 feeds 1980 continuity
DRAFT_YEARS = range(1990, 2020)


def stage_franchise_seasons() -> pd.DataFrame:
    rows = []
    for season in SEASONS_STANDINGS:
        html = strip_comment_tables(fetch(f"/leagues/NBA_{season}.html", f"leagues_NBA_{season}"))
        rows.extend(parse_season_standings(html, season))
        print(f"standings {season} ok", flush=True)
    df = pd.DataFrame(rows)
    df["franchise_id"] = [to_franchise(a, s) for a, s in zip(df.bref_abbr, df.season)]
    df.to_parquet(STAGED / "franchise_seasons_raw.parquet", index=False)
    return df


def stage_player_seasons() -> pd.DataFrame:
    rows = []
    for season in SEASONS_ADVANCED:
        html = strip_comment_tables(
            fetch(f"/leagues/NBA_{season}_advanced.html", f"advanced_NBA_{season}")
        )
        rows.extend(parse_advanced_players(html, season))
        print(f"advanced {season} ok", flush=True)
    df = pd.DataFrame(rows)
    df["franchise_id"] = [
        to_franchise(a, s) if a else None for a, s in zip(df.bref_abbr, df.season)
    ]
    df.to_parquet(STAGED / "player_impact_seasons.parquet", index=False)
    return df


def stage_drafts() -> pd.DataFrame:
    rows = []
    for year in DRAFT_YEARS:
        html = strip_comment_tables(fetch(f"/draft/NBA_{year}.html", f"draft_NBA_{year}"))
        rows.extend(parse_draft(html, year))
        print(f"draft {year} ok", flush=True)
    df = pd.DataFrame(rows)
    df.to_parquet(STAGED / "draft_picks.parquet", index=False)
    return df


def stage_all_nba() -> pd.DataFrame:
    html = strip_comment_tables(fetch("/awards/all_league.html", "awards_all_league"))
    df = pd.DataFrame(parse_all_league(html))
    df.to_parquet(STAGED / "all_nba.parquet", index=False)
    return df


def main():
    STAGED.mkdir(parents=True, exist_ok=True)
    fs = stage_franchise_seasons()
    ps = stage_player_seasons()
    dr = stage_drafts()
    al = stage_all_nba()
    print("\n=== STAGED ===")
    print(f"franchise_seasons_raw: {len(fs)} rows, seasons {fs.season.min()}-{fs.season.max()}, "
          f"{fs.franchise_id.nunique()} franchises")
    print(f"player_impact_seasons: {len(ps)} rows ({ps.is_combined.sum()} combined), "
          f"seasons {ps.season.min()}-{ps.season.max()}, {ps.player_id.nunique()} players")
    print(f"draft_picks: {len(dr)} rows, years {dr.draft_year.min()}-{dr.draft_year.max()}")
    print(f"all_nba: {len(al)} rows, seasons {al.season.min()}-{al.season.max()}")


if __name__ == "__main__":
    main()
