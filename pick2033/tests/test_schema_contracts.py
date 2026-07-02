"""M0 schema contracts: warehouse tables exist with required columns, sane
coverage, and unique keys. JSON export contracts join this file at M4+."""

import sys
from pathlib import Path

import duckdb
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
DB = PROJECT_ROOT / "data" / "warehouse.duckdb"

REQUIRED = {
    "franchise_seasons": {"franchise_id", "season", "conference", "wins", "losses",
                          "win_pct", "srs", "core_age_min_weighted",
                          "continuity_pct", "had_star"},
    "player_impact_seasons": {"player_id", "season", "franchise_id", "pos", "age",
                              "mp", "ws", "bpm", "vorp", "is_combined", "stint_order"},
    "draft_outcomes": {"draft_year", "slot", "player_id", "value_4yr", "value_alt"},
    "all_nba": {"season", "tier", "player_id"},
    "lottery_odds": {"era", "position", "weight", "drawn_picks"},
    "rosters_current": {"team", "player", "nba_player_id", "age", "roster_state",
                        "salary_2026_27", "net_rapm", "bbr_bpm"},
}


@pytest.fixture(scope="module")
def con():
    if not DB.exists():
        pytest.skip("warehouse.duckdb not built; run src/etl/build_warehouse.py")
    c = duckdb.connect(str(DB), read_only=True)
    yield c
    c.close()


@pytest.mark.parametrize("table", sorted(REQUIRED))
def test_required_columns(con, table):
    cols = {r[0] for r in con.execute(f"DESCRIBE {table}").fetchall()}
    missing = REQUIRED[table] - cols
    assert not missing, f"{table} missing columns: {missing}"


def test_franchise_seasons_coverage(con):
    lo, hi, n_fr, n = con.execute(
        "SELECT min(season), max(season), count(DISTINCT franchise_id), count(*) "
        "FROM franchise_seasons").fetchone()
    assert lo == 1980 and hi >= 2026
    assert n_fr == 30
    assert 1250 <= n <= 1400
    dup = con.execute("""SELECT count(*) FROM (SELECT franchise_id, season, count(*) c
        FROM franchise_seasons GROUP BY 1,2 HAVING c > 1)""").fetchone()[0]
    assert dup == 0
    nulls = con.execute("""SELECT count(*) FROM franchise_seasons
        WHERE srs IS NULL OR wins IS NULL OR conference IS NULL""").fetchone()[0]
    assert nulls == 0


def test_charlotte_lineage_in_warehouse(con):
    # CHA franchise: CHH 1989-2002 + Bobcats/Hornets 2005+, with the 2003-04 gap
    seasons = [r[0] for r in con.execute(
        "SELECT season FROM franchise_seasons WHERE franchise_id='CHA' ORDER BY 1").fetchall()]
    assert min(seasons) == 1989
    assert 2003 not in seasons and 2004 not in seasons
    assert 2002 in seasons and 2005 in seasons
    # NOP starts 2003, no earlier rows
    nop_lo = con.execute(
        "SELECT min(season) FROM franchise_seasons WHERE franchise_id='NOP'").fetchone()[0]
    assert nop_lo == 2003


def test_draft_outcomes_contract(con):
    lo, hi, n = con.execute(
        "SELECT min(draft_year), max(draft_year), count(*) FROM draft_outcomes").fetchone()
    assert (lo, hi) == (1990, 2019)
    assert 1600 <= n <= 1900
    dup = con.execute("""SELECT count(*) FROM (SELECT draft_year, slot, count(*) c
        FROM draft_outcomes GROUP BY 1,2 HAVING c > 1)""").fetchone()[0]
    assert dup == 0
    # slot 1s should massively outproduce slot 60s on average
    top, bottom = con.execute("""SELECT
        avg(value_4yr) FILTER (slot <= 3), avg(value_4yr) FILTER (slot >= 45)
        FROM draft_outcomes""").fetchone()
    assert top > 5 * max(bottom, 0.01)


def test_player_impact_coverage(con):
    lo, hi = con.execute(
        "SELECT min(season), max(season) FROM player_impact_seasons").fetchone()
    assert lo == 1979 and hi >= 2026
    # BPM/VORP exist 1974+; every season in our window must have them
    missing = con.execute("""SELECT count(*) FROM (
        SELECT season FROM player_impact_seasons GROUP BY season
        HAVING count(vorp) = 0)""").fetchone()[0]
    assert missing == 0
    # stint rows must carry a franchise; combined rows must not
    bad = con.execute("""SELECT count(*) FROM player_impact_seasons
        WHERE (is_combined AND franchise_id IS NOT NULL)
           OR (NOT is_combined AND franchise_id IS NULL)""").fetchone()[0]
    assert bad == 0


def test_lottery_odds_rows(con):
    rows = con.execute("""SELECT era, count(*), sum(weight) FROM lottery_odds
        GROUP BY era ORDER BY era""").fetchall()
    d = {r[0]: (r[1], r[2]) for r in rows}
    assert d["pre_2019_weighted"] == (14, 1000)
    assert d["post_2019"] == (14, 1000)


def test_rosters_current_states(con):
    states = {r[0] for r in con.execute(
        "SELECT DISTINCT roster_state FROM rosters_current").fetchall()}
    assert states == {"pre_trade", "post_trade"}
    post_min = [r[0] for r in con.execute("""SELECT player FROM rosters_current
        WHERE roster_state='post_trade' AND team='MIN'""").fetchall()]
    assert any("LaMelo" in p for p in post_min)
    assert not any("Randle" in p for p in post_min)
    assert not any("Reid" in p for p in post_min)
