"""F0 contracts: AM-1 hash pin verifies and refuses drift; golden possession
outputs reproduce exactly across both PBP formats; the R1 include-list is a
tested assertion, not an assumption."""

import sys
from pathlib import Path

import pandas as pd
import pytest

FITENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FITENGINE_ROOT))
FIXDIR = FITENGINE_ROOT / "tests" / "fixtures"


def test_am1_pin_verifies():
    from src.adapters.postmortem_lib import verify_pins
    pins = verify_pins()
    assert len(pins) == 4


def test_am1_pin_refuses_drift(tmp_path, monkeypatch):
    import src.adapters.postmortem_lib as adapter
    import yaml
    bad = {"pinned_files": {"postmortem/lib/db.py": "0" * 40}}
    p = tmp_path / "pinned_lib.yaml"
    p.write_text(yaml.safe_dump(bad))
    monkeypatch.setattr(adapter, "PIN_FILE", p)
    with pytest.raises(adapter.PinnedLibDriftError):
        adapter.verify_pins()


@pytest.mark.parametrize("gid", [
    "0021300001", "0021600001", "0021900001", "0022200001", "0022400001",
    "0022500001", "0022500247", "0022500493", "0022500739", "0022500985",
])
def test_golden_possessions_reproduce(gid):
    """Both formats: canonical parser output must match the frozen golden
    exactly (possession count, per-possession points and offense team)."""
    from src.adapters.postmortem_lib import normalize_pbp, reconstruct_possessions
    raw = pd.read_parquet(FIXDIR / f"pbp_{gid}.parquet")
    golden = pd.read_parquet(FIXDIR / f"golden_poss_{gid}.parquet")
    _, poss = reconstruct_possessions(normalize_pbp(raw))
    assert len(poss) == len(golden)
    for col in ("points_scored", "offensive_team_id"):
        if col in golden.columns:
            assert (poss[col].values == golden[col].values).all(), (gid, col)


def test_r1_include_list_asserted():
    """The training filter is an explicit include-list (R1): only 002 games
    are train-eligible; 004 flagged; preseason/all-star/play-in/other are
    NEITHER. Asserted against the audited game universe."""
    uni = pd.read_parquet(FITENGINE_ROOT / "data" / "staged" / "game_universe.parquet")
    assert (uni.loc[uni.include_train, "type_prefix"] == "002").all()
    assert (uni.loc[uni.include_flagged, "type_prefix"] == "004").all()
    neither = uni[~uni.include_train & ~uni.include_flagged]
    assert set(neither.type_prefix) <= {"001", "003", "005", "006"}
    # the audited facts this filter exists for:
    assert (uni.type_prefix == "001").sum() > 0       # preseason IS present
    assert int(uni.include_train.sum()) == 15669       # frozen census
    # per-season completeness under the filter (the "2013-14 gap" was a
    # query artifact; assert it stays dead)
    rs = uni[uni.include_train]
    per = rs.groupby(rs.game_id.str[3:5]).size()
    for yy, exp in [("13", 1230), ("19", 1059), ("20", 1080), ("25", 1230)]:
        assert per[yy] == exp, (yy, per[yy])
