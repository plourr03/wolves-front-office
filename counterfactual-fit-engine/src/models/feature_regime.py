"""F3 prep: feature regimes + the leakage-safe feature service.

Two jobs:

1. REGIMES are data-driven availability masks over player_features:
   which feature columns actually exist per season (tracking is 2013-14
   onward but the warehouse currently has a 2020-21 hole; hustle-era
   columns appear later; RAPM columns are provisional until F2 lands).
   Nothing is assumed from documentation; the mask is computed from
   observed non-null shares.

2. THE LEAKAGE RULE (spec 8.4, binding, tested): every feature served for
   a season-s training or evaluation row comes from that player's most
   recent season STRICTLY BEFORE s. FeatureService.features_for is the
   single sanctioned access path for Layer 2 row assembly; it refuses
   same-season reads by construction, and tests/test_feature_regime.py
   proves it on synthetic data with a poisoned same-season column (the
   canary: if the pipeline ever serves season-s values for season-s rows,
   the canary column would leak a perfect copy of the target and the test
   fails).

Aging of served vectors (one year via Model C / A2 curves) is applied by
the caller at Layer 2 assembly; this module's contract is temporal
hygiene, not curve arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

META_COLS = {"player_id", "season", "end_year"}


def availability_mask(features: pd.DataFrame,
                      min_share: float = 0.5) -> pd.DataFrame:
    """Share of non-null values per (season, feature column); a column is
    'available' in a season when at least min_share of that season's rows
    carry it. Returns long frame: end_year, column, share, available."""
    rows = []
    feat_cols = [c for c in features.columns if c not in META_COLS]
    for yr, g in features.groupby("end_year"):
        for c in feat_cols:
            share = float(g[c].notna().mean())
            rows.append({"end_year": int(yr), "column": c,
                         "share": share, "available": share >= min_share})
    return pd.DataFrame(rows)


class SameSeasonReadError(RuntimeError):
    """A caller asked the feature service for season-s features to use in
    season-s rows. That is the circularity the leakage rule bans."""


@dataclass
class FeatureService:
    """Leakage-safe access to player-season features.

    features_for(target_end_year) returns, per player, the row from that
    player's most recent end_year STRICTLY LESS THAN target_end_year,
    optionally capped at max_lookback seasons stale. The returned frame
    carries source_end_year so callers can age vectors by the actual gap.
    """

    features: pd.DataFrame
    max_lookback: int = 3
    _by_year: dict = field(init=False, repr=False, default_factory=dict)

    def __post_init__(self) -> None:
        missing = META_COLS - set(self.features.columns)
        if missing:
            raise ValueError(f"features frame lacks {sorted(missing)}")

    def features_for(self, target_end_year: int) -> pd.DataFrame:
        eligible = self.features[
            (self.features.end_year < target_end_year)
            & (self.features.end_year >= target_end_year - self.max_lookback)
        ]
        if eligible.empty:
            return eligible.assign(source_end_year=pd.Series(dtype="int64"))
        latest = (eligible.sort_values("end_year")
                          .groupby("player_id", as_index=False).tail(1)
                          .rename(columns={"end_year": "source_end_year"}))
        assert (latest.source_end_year < target_end_year).all(), \
            "leakage invariant violated"
        return latest.reset_index(drop=True)

    def assert_no_same_season(self, target_end_year: int,
                              served: pd.DataFrame) -> None:
        if "source_end_year" not in served.columns:
            raise SameSeasonReadError("served frame lost its provenance column")
        if (served.source_end_year >= target_end_year).any():
            raise SameSeasonReadError(
                f"served features contain season >= {target_end_year}")
