"""Regression tests for star_spells_builder (bugfix 2026-07-01: mid-season
ARRIVAL years must not auto-close spells as departures).

Root cause: the departure test included a same-season stint count
(n_franchises > 1), which carries no direction. Direction comes only from
cross-season final-stint franchise comparison.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
REVIEW = PROJECT_ROOT / "outputs" / "star_spells_review.csv"
CANDIDATE = PROJECT_ROOT / "data" / "staged" / "star_spell_seasons_candidate.parquet"


@pytest.fixture(scope="module")
def rev():
    if not REVIEW.exists():
        pytest.skip("review CSV not built; run src/etl/star_spells_builder.py")
    df = pd.read_csv(REVIEW)
    df["player_id"] = df.spell_id.str.rsplit("_", n=1).str[0]
    return df


def test_no_adjacent_same_franchise_spells(rev):
    """A spell continues while the final-stint franchise is unchanged, so two
    spells of one player at one franchise can never be season-adjacent."""
    bad = []
    for pid, g in rev.sort_values("entry_season").groupby("player_id"):
        rows = g.to_dict("records")
        for a, b in zip(rows, rows[1:]):
            if (a["franchise_id"] == b["franchise_id"]
                    and b["entry_season"] <= a["exit_season"] + 1):
                bad.append((pid, a["franchise_id"], a["exit_season"], b["entry_season"]))
    assert not bad, f"adjacent same-franchise spell pairs: {bad}"


def test_ray_allen_sea_single_spell(rev):
    """Ray Allen arrived in Seattle mid-season Feb 2003 and stayed through
    2007: exactly one OKC-franchise spell, 2003-2007, ending in departure."""
    okc = rev[(rev.player_id == "allenra02") & (rev.franchise_id == "OKC")]
    assert len(okc) == 1
    r = okc.iloc[0]
    assert (r.entry_season, r.exit_season, r.n_seasons) == (2003, 2007, 5)
    assert r.exit_type == "departure"


def test_anthony_davis_dal_censored(rev):
    """AD arrived in Dallas mid-season Feb 2025 and remained through 2025-26:
    the DAL spell is alive at the data boundary, hence censored."""
    dal = rev[(rev.player_id == "davisan02") & (rev.franchise_id == "DAL")]
    assert len(dal) == 1
    r = dal.iloc[0]
    assert r.exit_type == "censored"
    assert r.exit_season == 2026


@pytest.mark.parametrize("pid,franchise,expect_exit,expect_type", [
    ("vucevni01", "CHI", 2025, "departure"),   # arrival Mar 2021, stayed years
    ("hardeja01", "CLE", 2026, "censored"),    # arrival mid-2026, data boundary
    ("butleji01", "GSW", 2026, "censored"),    # arrival Feb 2025, still on GSW
])
def test_arrival_year_spells_extend(rev, pid, franchise, expect_exit, expect_type):
    sub = rev[(rev.player_id == pid) & (rev.franchise_id == franchise)]
    assert len(sub) == 1
    r = sub.iloc[0]
    assert (r.exit_season, r.exit_type) == (expect_exit, expect_type)


def test_data_boundary_exits_are_censored(rev):
    """Departure cannot be observed at the data edge: every spell whose last
    season is the final data season must be censored (never departure)."""
    edge = rev[rev.exit_season == rev.exit_season.max()]
    assert set(edge.exit_type) <= {"censored"}, (
        f"non-censored boundary exits: {edge[edge.exit_type != 'censored'][['spell_id', 'exit_type']].values}")


from src.etl.star_spells_builder import boundary_exit_type


class TestBoundaryRule:
    """One test per branch of Bobby's boundary rule (2026-07-01)."""

    def test_same_franchise_contract_censored(self):
        assert boundary_exit_type("IND", {"IND"}, "IND", 25) == "censored"   # Haliburton shape
        assert boundary_exit_type(None, {"DAL"}, "DAL", 33) == "censored"    # contract-only fallback

    def test_different_franchise_departure(self):
        # Lillard shape: MIL cap charge is dead money; the roster row (POR) wins
        assert boundary_exit_type("POR", {"MIL", "POR"}, "MIL", 34) == "departure"
        assert boundary_exit_type(None, {"HOU"}, "WAS", 28) == "departure"

    def test_no_contract_age_split(self):
        assert boundary_exit_type(None, set(), "MIA", 36) == "retire"
        assert boundary_exit_type(None, set(), "MIA", 29) == "review"

    def test_ambiguous_cap_charges_review(self):
        assert boundary_exit_type(None, {"MIL", "POR"}, "MIL", 34) == "review"


@pytest.mark.parametrize("pid,franchise,expect_type", [
    ("halibty01", "IND", "censored"),    # Achilles, under contract with IND
    ("irvinky01", "DAL", "censored"),    # ACL, under contract with DAL
    ("lillada01", "MIL", "departure"),   # waived-and-stretched, roster row POR
])
def test_boundary_rule_real_cases(rev, pid, franchise, expect_type):
    sub = rev[(rev.player_id == pid) & (rev.franchise_id == franchise)
              & (rev.exit_season == 2025)]
    assert len(sub) == 1
    assert sub.iloc[0].exit_type == expect_type


def test_all_nba_count_includes_pre_spell_honors():
    """Alvin Robertson's 1986 2nd team must count on his 1991-92 MIL spell
    rows (the old exact-season merge + ffill lost it); Barkley's HOU rows
    keep the full career count."""
    if not CANDIDATE.exists():
        pytest.skip("candidate parquet not built")
    sp = pd.read_parquet(CANDIDATE)
    rob = sp[(sp.player_id == "roberal01") & (sp.season == 1991)]
    assert len(rob) == 1 and int(rob.all_nba_count_career.iloc[0]) >= 1
    bark = sp[(sp.player_id == "barklch01") & (sp.season == 2000)]
    assert len(bark) == 1 and int(bark.all_nba_count_career.iloc[0]) == 11


def test_bosh_2016_entry_is_legitimate(rev):
    """Verified against the qualification log: 1,778 mp (over the 1,500
    floor) with BPM rank 17 in 2015-16. The MIA spell stands, entry 2016."""
    bosh = rev[(rev.player_id == "boshch01") & (rev.franchise_id == "MIA")]
    assert len(bosh) == 1
    assert bosh.iloc[0].entry_season == 2016


def test_deep_run_recent_populated():
    """deep_run_recent must vary and hit known cases (a positional-tuple
    mismatch once silently zeroed it): Duncan SAS 2004 True (2003 title run),
    KG MIN 2005 True (2004 WCF), KG MIN 2003 False (no CF+ 2001-2003)."""
    if not CANDIDATE.exists():
        pytest.skip("candidate parquet not built")
    sp = pd.read_parquet(CANDIDATE)
    assert sp.deep_run_recent.any() and not sp.deep_run_recent.all()
    def val(pid, season):
        r = sp[(sp.player_id == pid) & (sp.season == season)]
        return bool(r.deep_run_recent.iloc[0])
    assert val("duncati01", 2004) is True
    assert val("garneke01", 2005) is True
    assert val("garneke01", 2003) is False


def test_tenure_spans_same_franchise_gaps():
    """Jordan's CHI tenure clock starts 1985 and survives the 1994 gap year:
    years_with_franchise on the 1998 row is 14, not reset-at-1995."""
    if not CANDIDATE.exists():
        pytest.skip("candidate parquet not built")
    sp = pd.read_parquet(CANDIDATE)
    mj = sp[(sp.player_id == "jordami01") & (sp.season == 1998)]
    assert len(mj) == 1
    assert int(mj.years_with_franchise.iloc[0]) == 14
