"""Component 5: Shot Quality Decay (15% LAFI weight).

The downstream output of Components 1-4. What kind of shots does the offense
actually produce? Spec section 2.6.

**v1 limitations.** The spec wants per-shot defender distance, shot-clock
remaining, and an expected-eFG model. The warehouse has shot coordinates and
location-based zones but does NOT have defender distance or shot-clock-
remaining at the per-shot grain. v1 substitutes with:

  1. Catch-and-shoot vs Pull-up FGA split (tracking measure types).
  2. Pull-up three-point share within all threes (spec sub-metric 5).
  3. Restricted-area share of total FGA (shot quality proxy).
  4. Midrange share of total FGA (worse shot diet proxy).

v2 with tracking-shot-categorization data (Very Tight, Tight, Open, Wide Open)
would add the contested-rate piece directly.

Sub-metrics (sign convention: higher = more pickup = worse shot quality):

  1. inv_catch_shoot_share
       = -(catch_shoot_fga / (catch_shoot_fga + pull_up_fga))
       Lower catch-shoot fraction means more self-created shots, the signature
       of pickup ball. Sign-flipped so higher = more pickup.

  2. pull_up_fg3a_share
       = pull_up_fg3a / (pull_up_fg3a + catch_shoot_fg3a)
       Per spec sub-metric 5. Higher pull-up three share = more pickup.

  3. inv_restricted_area_share
       = -(restricted_area_fga / total_fga)
       Lower share of shots at the rim is a worse shot diet. Sign-flipped.

  4. midrange_share
       = midrange_fga / total_fga
       Higher midrange share is a worse shot diet by modern shooting math.

Note: sub-metrics 3 and 4 require nba_team_shot_locations_season, which only
covers 2018-19 onward. The 5-component canonical LAFI sample is bounded to
that window. The 4-component robustness LAFI drops Component 5 and uses the
wider 11-season window.

Inputs:
  nba_team_tracking_season   measure_type IN ('CatchShoot', 'PullUpShot')
  nba_team_shot_locations_season
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd

from analyses.q0a_lafi import config, data, util


COMPONENT_NAME = "shot_quality_decay"


def compute(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = ("Regular Season",),
) -> pd.DataFrame:
    season_types = list(season_types) if season_types is not None else list(config.SEASON_TYPES)

    # CatchShoot tracking.
    cs = data.load_team_tracking_season(
        years=years, season_types=season_types, measure_types=["CatchShoot"]
    )[["team_id", "team_abbreviation", "season_year", "season_type",
       "season_start_year", "catch_shoot_fga", "catch_shoot_fg3a", "catch_shoot_efg_pct"]]

    # PullUpShot tracking.
    pu = data.load_team_tracking_season(
        years=years, season_types=season_types, measure_types=["PullUpShot"]
    )[["team_id", "season_year", "season_type",
       "pull_up_fga", "pull_up_fg3a", "pull_up_efg_pct"]]

    # Shot locations (season-level zone aggregates).
    loc = data.load_team_shot_locations_season(years=years, season_types=season_types)
    # Total fga across zones, restricted area share, midrange share.
    loc["total_zone_fga"] = (
        loc[["restricted_area_fga", "paint_non_ra_fga", "midrange_fga",
             "above_break_3_fga", "corner_3_fga", "backcourt_fga"]]
        .fillna(0).sum(axis=1)
    )
    loc = loc[["team_id", "season_year", "season_type",
               "restricted_area_fga", "midrange_fga", "above_break_3_fga",
               "corner_3_fga", "total_zone_fga"]]

    # Top handler annotation (consistency with other components).
    player_poss = data.load_player_tracking_season(
        years=years, season_types=season_types, measure_types=["Possessions"]
    )[["team_id", "season_year", "season_type", "player_name", "time_of_poss"]]
    top_handler = util.top_handler_per_team_season(player_poss)[[
        "team_id", "season_year", "season_type", "top_handler_name"]]

    df = (cs
          .merge(pu, on=["team_id", "season_year", "season_type"], how="left")
          .merge(loc, on=["team_id", "season_year", "season_type"], how="left")
          .merge(top_handler, on=["team_id", "season_year", "season_type"], how="left"))

    for c in ("catch_shoot_fga", "catch_shoot_fg3a", "catch_shoot_efg_pct",
              "pull_up_fga", "pull_up_fg3a", "pull_up_efg_pct",
              "restricted_area_fga", "midrange_fga", "above_break_3_fga",
              "corner_3_fga", "total_zone_fga"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Sub-metrics.
    cs_share = df["catch_shoot_fga"] / (df["catch_shoot_fga"] + df["pull_up_fga"])
    pu_three_share = df["pull_up_fg3a"] / (df["pull_up_fg3a"] + df["catch_shoot_fg3a"])
    ra_share = df["restricted_area_fga"] / df["total_zone_fga"]
    mid_share = df["midrange_fga"] / df["total_zone_fga"]

    sub = {}
    sub["inv_catch_shoot_share"] = -1.0 * cs_share
    sub["pull_up_fg3a_share"] = pu_three_share
    sub["inv_restricted_area_share"] = -1.0 * ra_share
    sub["midrange_share"] = mid_share

    base = df[["team_id", "team_abbreviation", "season_start_year",
               "season_year", "season_type", "top_handler_name"]].rename(
                   columns={"season_year": "season_label"})

    # Annotate the raw zone shares for the eye-test.
    base["catch_shoot_share_raw_pct"] = cs_share
    base["pull_up_three_share_raw_pct"] = pu_three_share
    base["restricted_area_share_raw_pct"] = ra_share
    base["midrange_share_raw_pct"] = mid_share

    out = util.assemble_component_output(base, sub)
    return out


PRIORS_MD = """
- Wolves 2025-26 predicted: **55th to 75th percentile**, low confidence.
- Reasoning: late-clock contested shots inevitable given Q4 offense, but Ant
  manufactures decent shots even from bad situations, and the Wolves shoot
  threes at reasonable volume. Elevated but not extreme.
- Expected high pickup-side: heavy iso teams with pull-up-heavy shot diet
  (PHI, LAC, LAL, OKC, NOP).
- Expected low pickup-side: motion offenses with high catch-and-shoot share
  (GSW, IND, BOS).
- Component 5 has a tighter usable window (2018-19+) due to shot-locations
  table availability. Drops 2014-15 to 2017-18 from the 5-component sample.

**v1 vs v2 transparency.** No defender distance or shot-clock remaining at
per-shot grain. v1 uses tracking-derived CatchShoot vs PullUpShot plus zone
share proxies. v2 with tracking-shot-categorization would add contested-rate
directly.
"""

INVESTIGATION_MD = """
**Wolves 2025-26 landed at 82nd percentile. User prediction was 55-75 (low confidence).**
Slightly above the upper bound but in the right direction. The "Q4 produces bad
shots" causal chain is supported.

**Wolves shot-diet trajectory across the Edwards era:**

| Season | CS share | PU3 share | RA share | MID share | Pct |
|---|---|---|---|---|---|
| 2023-24 | 0.539 | 0.295 | 0.305 | 0.097 | 39 |
| 2024-25 | 0.505 | 0.372 | 0.287 | 0.073 | 71 |
| **2025-26** | **0.479** | **0.361** | **0.295** | **0.100** | **82** |

Catch-and-shoot share fell from 53.9% to 47.9%. More self-created shots.
Pull-up three share rose from 29.5% to 36.1%. More off-the-dribble threes
specifically. Midrange ticked up. Restricted-area share slipped slightly.
The shot diet got worse along every dimension the metric measures.

**League leaderboard 2025-26 (worst shot quality):**

BOS (98), PHX (98), SAC (97), LAL (94), WAS (88), MIN (82), DAL (78), LAC (77).

BOS at #1 is roster-correct: Tatum out, Brown and Pritchard pulling up off the
dribble. PHX, SAC, LAL all known iso-and-pull-up offenses. WAS rebuilding.

**League tail (best shot quality):**

CHI (0), BKN (7), MIA (10), **SAS (11)**, NOP (15), POR (16), ATL (17), GSW (19).

SAS at 11 is exactly what the Wembanyama hypothesis predicted: a team with
elite rim protection and designed motion produces a good shot diet at the
offensive end as well. The Spurs' shot diet is structurally clean. Their
defense is structurally clean. They are the structural counterargument to
the Wolves at both ends of the floor.

GSW at 19 is surprising. The Warriors actually have a high pull-up-three rate
(Steph), which hurts them on this metric even though the shots are good ones
because Steph hits them. The metric is noise-blind to who is taking the shot.
v2 with expected-eFG modeling would account for this.

**The takeaway: Q4 has a shot-quality signature.**

The Wolves' shot diet has degraded in lockstep with their migration through
the quadrants. 2023-24 (Q1-leaning) produced a 39th-percentile shot diet.
2024-25 (Q3-leaning) produced 71. 2025-26 (Q4) produced 82. Each step toward
Q4 made the shot diet worse.

This is the causal chain the spec hypothesized: pickup process produces pickup
results. The Wolves' offense doesn't just feel like pickup ball; it produces
the shot diet pickup ball produces.

**No metric change warranted.** The v1 component holds. v2 with defender-
distance data would refine it (catching the GSW false-positive) but the
Wolves diagnosis is already in line with the rest of the synthesis.
"""


def validate(df: pd.DataFrame) -> None:
    util.eye_test_report(df, COMPONENT_NAME)
    print("\nPriors:")
    print("  Wolves 2025-26 predicted 55-75th percentile (low confidence).")
    print("\nShot-diet annotation (Wolves trajectory):")
    wolves = df[(df["team_id"] == config.WOLVES_TEAM_ID)
                & (df["season_type"] == "Regular Season")].sort_values("season_start_year")
    for _, r in wolves.iterrows():
        yr = int(r["season_start_year"])
        cs = r.get("catch_shoot_share_raw_pct")
        pu3 = r.get("pull_up_three_share_raw_pct")
        ra = r.get("restricted_area_share_raw_pct")
        mid = r.get("midrange_share_raw_pct")
        def fmt(x):
            return f"{x:.3f}" if pd.notna(x) else "  -  "
        print(f"  {yr}-{(yr+1)%100:02d}  CS_share={fmt(cs)}  PU3_share={fmt(pu3)}  RA_share={fmt(ra)}  MID_share={fmt(mid)}")
    print("\nSub-metric sanity (latest RS, top 5 by raw score):")
    latest = df[df["season_start_year"] == df["season_start_year"].max()]
    latest = latest[latest["season_type"] == "Regular Season"].nlargest(5, "raw_score")
    cols = ["team_abbreviation",
            "inv_catch_shoot_share_raw", "pull_up_fg3a_share_raw",
            "inv_restricted_area_share_raw", "midrange_share_raw",
            "raw_score", "percentile_rank"]
    print(latest[cols].to_string(index=False, float_format=lambda x: f"{x:.4f}"))


def write(df: pd.DataFrame) -> None:
    util.write_component_csv(df, COMPONENT_NAME, config.TABLE_DIR)
    util.write_eye_test_markdown(
        COMPONENT_NAME, df, config.TABLE_DIR,
        priors_md=PRIORS_MD,
        investigation_md=INVESTIGATION_MD,
    )
