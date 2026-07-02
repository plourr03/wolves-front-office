"""Historical replays (spec 8.5). ON-7 scope: DATA CUTS ONLY -- the replay
fits run after the final spells freeze (overnight directive constraint).

As-of discipline: every input is filtered to information available at the
as-of date. This module centralizes those cuts so the replay runner cannot
accidentally leak the future:
  - franchise panel: seasons <= as_of season (trajectory fit via
    fit(through=...) which keys its own cache)
  - draft outcomes for E1: draft_year <= as_of - 4 (full 4-yr value window
    observable at the time)
  - star spells: spell-season rows with season <= as_of, censoring flags
    recomputed at the boundary (a spell alive in as_of is censored there,
    whatever happened later)
  - lottery era: pre_2019_weighted (k=3)
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
STAGED = PROJECT_ROOT / "data" / "staged"


def panel_cut(as_of_season: int) -> pd.DataFrame:
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    df = con.execute("SELECT * FROM franchise_seasons WHERE season <= ?",
                     [as_of_season]).fetchdf()
    con.close()
    return df


def draft_cut(as_of_season: int) -> pd.DataFrame:
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    df = con.execute("SELECT * FROM draft_outcomes WHERE draft_year <= ?",
                     [as_of_season - 4]).fetchdf()
    con.close()
    return df


def spells_cut(as_of_season: int, source: str = "star_spells_provisional.parquet") -> pd.DataFrame:
    """Spell rows visible at as_of, with boundary censoring recomputed:
    any spell whose last visible row is as_of becomes censored there."""
    sp = pd.read_parquet(STAGED / source)
    cut = sp[sp.season <= as_of_season].copy()
    last_idx = cut.sort_values("season").groupby("spell_id").tail(1).index
    at_edge = cut.loc[last_idx, "season"] == as_of_season
    edge_idx = last_idx[at_edge]
    cut.loc[edge_idx, ["event_departure", "event_retire", "censored"]] = [False, False, True]
    return cut


def main():
    for s in (2013, 2019):
        p, d, sp = panel_cut(s), draft_cut(s), spells_cut(s)
        print(f"as-of {s}: panel {len(p)} rows (max {p.season.max()}), "
              f"drafts {d.draft_year.min()}-{d.draft_year.max()} ({len(d)}), "
              f"spells {sp.spell_id.nunique()} "
              f"({int(sp.groupby('spell_id').tail(1).censored.sum())} censored at edge)")
        assert p.season.max() == s and d.draft_year.max() == s - 4


if __name__ == "__main__":
    main()
