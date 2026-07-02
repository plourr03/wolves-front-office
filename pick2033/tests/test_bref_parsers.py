"""Parser tests against permanently cached B-Ref HTML (data/raw/bref/).
No network access: if a fixture is missing the test skips with instructions."""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from src.etl.bref_client import CACHE_DIR, strip_comment_tables
from src.etl.bref_parsers import (
    parse_advanced_players,
    parse_all_league,
    parse_draft,
    parse_season_standings,
)


def _fixture(cache_key: str) -> str:
    f = CACHE_DIR / f"{cache_key}.html"
    if not f.exists():
        pytest.skip(f"fixture {cache_key} not cached; run src/etl/run_m0_pull.py")
    return strip_comment_tables(f.read_text(encoding="utf-8"))


def test_standings_2005():
    rows = parse_season_standings(_fixture("leagues_NBA_2005"), 2005)
    assert len(rows) == 30
    phx = next(r for r in rows if r["bref_abbr"] == "PHO")
    assert (phx["wins"], phx["losses"]) == (62, 20)
    assert phx["conference"] == "W"
    assert abs(phx["srs"] - 7.08) < 0.01


def test_standings_1985_era_abbrs():
    rows = parse_season_standings(_fixture("leagues_NBA_1985"), 1985)
    assert len(rows) == 23
    abbrs = {r["bref_abbr"] for r in rows}
    assert {"WSB", "NJN", "KCK", "SDC" if 1985 <= 1984 else "LAC", "SEA"} - abbrs == set()
    bos = next(r for r in rows if r["bref_abbr"] == "BOS")
    assert (bos["wins"], bos["losses"]) == (63, 19)


def test_advanced_2005_combined_and_stints():
    rows = parse_advanced_players(_fixture("advanced_NBA_2005"), 2005)
    lebron = [r for r in rows if r["player_id"] == "jamesle01"]
    assert len(lebron) == 1 and not lebron[0]["is_combined"]
    assert lebron[0]["vorp"] == pytest.approx(9.1)
    assert lebron[0]["bpm"] == pytest.approx(8.6)
    assert lebron[0]["ws"] == pytest.approx(14.3)
    walker = [r for r in rows if r["player_id"] == "walkean02"]
    assert len(walker) == 3
    combined = [r for r in walker if r["is_combined"]]
    stints = sorted((r for r in walker if not r["is_combined"]),
                    key=lambda r: r["stint_order"])
    assert len(combined) == 1 and combined[0]["bref_abbr"] is None
    assert [s["bref_abbr"] for s in stints] == ["ATL", "BOS"]  # chronological


def test_draft_1996():
    rows = parse_draft(_fixture("draft_NBA_1996"), 1996)
    assert rows[0]["slot"] == 1 and rows[0]["player_id"] == "iversal01"
    kobe = next(r for r in rows if r["player_id"] == "bryanko01")
    assert kobe["slot"] == 13
    assert max(r["slot"] for r in rows) <= 60


def test_all_league():
    rows = parse_all_league(_fixture("awards_all_league"))
    seasons = {r["season"] for r in rows}
    assert 1990 in seasons and 2026 in seasons
    r2026 = [r for r in rows if r["season"] == 2026]
    assert len(r2026) == 15
    assert any(r["player_id"] == "jokicni01" and r["tier"] == "1st" for r in r2026)
