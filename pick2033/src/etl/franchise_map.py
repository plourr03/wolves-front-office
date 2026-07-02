"""Franchise ID mapping across relocations/renames (config/franchise_map.csv).

Rule: explicit (bref_abbr, season-range) rows win; anything unmapped falls back
to identity (the current 30 abbreviations that match our franchise IDs).
The load-bearing case is Charlotte: CHH 1989-2002 -> CHA (official NBA lineage),
NOH/NOK 2003+ -> NOP. Unit-tested in tests/test_franchise_map.py.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = PROJECT_ROOT / "config" / "franchise_map.csv"

# Identity abbrs we expect to see from B-Ref, 1979-2026, that need no mapping.
IDENTITY = {
    "ATL", "BOS", "CHI", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND",
    "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK", "OKC", "ORL",
    "PHI", "POR", "SAC", "SAS", "TOR", "UTA", "WAS", "BKN", "CHA", "PHX",
}


@lru_cache(maxsize=1)
def _rows() -> list[dict]:
    with open(MAP_PATH, newline="", encoding="utf-8") as f:
        return [
            {
                "bref_abbr": r["bref_abbr"],
                "first": int(r["season_first"]),
                "last": int(r["season_last"]),
                "franchise_id": r["franchise_id"],
            }
            for r in csv.DictReader(f)
        ]


def to_franchise(bref_abbr: str, season: int) -> str:
    """Map a B-Ref team abbreviation + season (ending-year) to a franchise ID."""
    for r in _rows():
        if r["bref_abbr"] == bref_abbr and r["first"] <= season <= r["last"]:
            return r["franchise_id"]
    if bref_abbr in IDENTITY:
        return bref_abbr
    raise KeyError(f"unmapped B-Ref abbr {bref_abbr!r} for season {season}")
