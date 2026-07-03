"""The leakage canary (directive 2026-07-03 item 3): synthetic data where
a same-season feature column IS the target. If the feature service ever
serves season-s features for season-s rows, the canary column becomes a
perfect predictor and the equality assertions here would catch it. The
service must only ever return strictly-prior seasons."""

import numpy as np
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models.feature_regime import (  # noqa: E402
    FeatureService, SameSeasonReadError, availability_mask)


def synth_features(n_players=40, years=(2015, 2021), seed=3):
    rng = np.random.default_rng(seed)
    rows = []
    for pid in range(1, n_players + 1):
        for yr in range(*years):
            if rng.random() < 0.15:  # players miss seasons
                continue
            rows.append({
                "player_id": pid, "end_year": yr, "season": f"{yr-1}-{yr%100:02d}",
                "skill": rng.normal(),
                # the canary: exactly the season's outcome, poisoned on purpose
                "canary_same_season_outcome": float(yr * 1000 + pid),
            })
    return pd.DataFrame(rows)


def test_service_serves_only_strictly_prior_seasons():
    feats = synth_features()
    svc = FeatureService(feats, max_lookback=3)
    for target in (2016, 2018, 2020):
        served = svc.features_for(target)
        assert len(served) > 0
        assert (served.source_end_year < target).all()
        svc.assert_no_same_season(target, served)
        # the canary value served must NEVER equal the target-season value
        expected_if_leaking = target * 1000 + served.player_id
        assert not (served.canary_same_season_outcome
                    == expected_if_leaking).any()


def test_service_returns_most_recent_prior_within_lookback():
    feats = synth_features()
    svc = FeatureService(feats, max_lookback=2)
    served = svc.features_for(2019)
    for _, r in served.iterrows():
        prior = feats[(feats.player_id == r.player_id) & (feats.end_year < 2019)
                      & (feats.end_year >= 2017)]
        assert r.source_end_year == prior.end_year.max()
    # nobody staler than the lookback window sneaks in
    assert (served.source_end_year >= 2017).all()


def test_same_season_read_raises():
    feats = synth_features()
    svc = FeatureService(feats)
    served = svc.features_for(2018)
    poisoned = served.copy()
    poisoned.loc[poisoned.index[0], "source_end_year"] = 2018
    with pytest.raises(SameSeasonReadError):
        svc.assert_no_same_season(2018, poisoned)


def test_availability_mask_flags_missing_regime():
    feats = synth_features()
    feats.loc[feats.end_year == 2018, "skill"] = np.nan  # a 2020-21-style hole
    mask = availability_mask(feats)
    hole = mask[(mask.end_year == 2018) & (mask.column == "skill")]
    assert not hole.available.iloc[0]
    ok = mask[(mask.end_year == 2017) & (mask.column == "skill")]
    assert ok.available.iloc[0]
