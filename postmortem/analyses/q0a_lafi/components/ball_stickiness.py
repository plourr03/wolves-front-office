"""Component 1: Ball Stickiness (25% LAFI weight).

How much one player dominates each possession. The defining trait of pickup
ball. See spec section 2.2.

Sub-metrics (sign convention: higher = stickier):

  1. lead_handler_top_share
       max(player time_of_poss for team) / team time_of_poss.
       The fraction of the team's total ball-handling seconds owned by its
       single most ball-dominant player.

  2. avg_sec_per_touch  (v1 proxy for spec sub-metric 2)
       Team-level average seconds per touch. The spec wanted "% of possessions
       with a 4+ second hold" which requires possession-level PBP analysis.
       avg_sec_per_touch is a clean, pre-computed proxy for the same idea:
       longer holds on average means more sticky possessions in the mix.
       Flagged as a v1 proxy; v2 with possession-level PBP can replace it.

  3. avg_drib_per_touch
       Team-level average dribbles per touch. One-on-one play even within
       possessions that move the ball.

  4. inv_passes_per_possession  (sign-flipped passes per possession)
       Negative of (passes_made / team_possessions). Fewer passes per
       possession means more pickup-like, so we negate so that higher = stickier.

Inputs:
  nba_team_tracking_season   measure_type IN ('Possessions','Passing')
  nba_player_tracking_season measure_type='Possessions'
  nba_team_advanced_stats    (aggregated to season total_possessions)
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd

from analyses.q0a_lafi import config, data, util


COMPONENT_NAME = "ball_stickiness"


def _team_possessions_season(years, season_types) -> pd.DataFrame:
    """Total possessions per (team, season, season_type) from advanced stats."""
    summary = data.load_team_season_summary(years=years, season_types=season_types)
    return summary[["team_id", "team_abbreviation", "season_start_year",
                    "season_label", "season_type", "poss_total"]].copy()


def compute(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = ("Regular Season",),
) -> pd.DataFrame:
    season_types = list(season_types) if season_types is not None else list(config.SEASON_TYPES)

    # Team possessions (Possessions measure) and Passing measure.
    team_poss = data.load_team_tracking_season(
        years=years, season_types=season_types, measure_types=["Possessions"]
    )[["team_id", "team_abbreviation", "season_year", "season_type",
       "season_start_year", "gp", "time_of_poss", "touches",
       "avg_sec_per_touch", "avg_drib_per_touch"]]
    team_poss = team_poss.rename(columns={
        "time_of_poss": "team_time_of_poss",
        "touches": "team_touches",
    })

    team_pass = data.load_team_tracking_season(
        years=years, season_types=season_types, measure_types=["Passing"]
    )[["team_id", "season_year", "season_type", "passes_made"]]

    # Player-level Possessions for the lead-handler share and the top-handler
    # annotation (who that player is by name).
    player_poss = data.load_player_tracking_season(
        years=years, season_types=season_types, measure_types=["Possessions"]
    )[["team_id", "season_year", "season_type", "player_name", "time_of_poss"]]
    top = util.top_handler_per_team_season(player_poss).rename(
        columns={"top_handler_top": "lead_player_top"}
    )
    lead = top[["team_id", "season_year", "season_type", "lead_player_top", "top_handler_name"]]

    # Team season totals of possessions, for the passes-per-possession denominator.
    pos_total = _team_possessions_season(years=years, season_types=season_types)

    # Merge.
    df = (team_poss
          .merge(team_pass, on=["team_id", "season_year", "season_type"], how="left")
          .merge(lead, on=["team_id", "season_year", "season_type"], how="left")
          .merge(pos_total[["team_id", "season_start_year", "season_type", "poss_total"]],
                 on=["team_id", "season_start_year", "season_type"], how="left"))

    for c in ("team_time_of_poss", "team_touches", "avg_sec_per_touch",
              "avg_drib_per_touch", "passes_made", "lead_player_top", "poss_total"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Sub-metrics, all sign-oriented so higher = stickier.
    sub = {}
    sub["lead_handler_top_share"] = df["lead_player_top"] / df["team_time_of_poss"]
    sub["avg_sec_per_touch"] = df["avg_sec_per_touch"]
    sub["avg_drib_per_touch"] = df["avg_drib_per_touch"]
    # Passes per possession: lower = stickier, so we negate.
    sub["inv_passes_per_possession"] = -1.0 * (df["passes_made"] / df["poss_total"])

    base = df[["team_id", "team_abbreviation", "season_start_year",
               "season_year", "season_type", "gp", "top_handler_name"]].rename(
                   columns={"season_year": "season_label"})

    out = util.assemble_component_output(base, sub)
    return out


def validate(df: pd.DataFrame) -> None:
    """Eye-test the component. Print top/bottom and Wolves trajectory."""
    util.eye_test_report(df, COMPONENT_NAME)
    print("\nPriors to check against:")
    print("  Expected high (sticky): teams with heavy iso stars")
    print("    Hawks (Trae), Mavs (Luka), Bulls/Hornets in down years, Wolves (per thesis)")
    print("  Expected low (designed): pass-heavy systems")
    print("    Pacers, Celtics, Thunder, Nuggets, prior-Warriors")
    print("\nSub-metric sanity (latest RS, top 5 by raw score):")
    latest = df[df["season_start_year"] == df["season_start_year"].max()]
    latest = latest[latest["season_type"] == "Regular Season"].nlargest(5, "raw_score")
    cols = ["team_abbreviation",
            "lead_handler_top_share_raw", "avg_sec_per_touch_raw",
            "avg_drib_per_touch_raw", "inv_passes_per_possession_raw",
            "raw_score", "percentile_rank"]
    print(latest[cols].to_string(index=False, float_format=lambda x: f"{x:.3f}"))


PRIORS_MD = """
- The thesis predicts the 2025-26 Wolves should rank high (top 5) on stickiness.
- Expected high: heavy ball-dominant stars. Hawks (Trae), Mavs (Luka), Knicks (Brunson).
- Expected low: pass-heavy systems. Pacers, prior-Warriors (Steph/Draymond), Thunder pre-2024-25.
- Wolves trajectory prior: should dip in 2023-24 (WCF year, KAT gravity), rise in 2024-25 and 2025-26 post-Randle.
"""

INVESTIGATION_MD = """
The eye-test surfaced three rankings that defied the priors. All three turned out
to be data-correct and prior-incorrect.

**ATL at 26th percentile (predicted high).** ATL's top time-of-possession players
in 2025-26 are Jalen Johnson, CJ McCollum, Dyson Daniels, Nickeil Alexander-Walker.
Trae Young is no longer on the roster. The "Hawks should be sticky" prior was
based on a Trae-centric offense that no longer exists.

**OKC at 92nd percentile (predicted moderate).** SGA owns 25.5% of team time-of-
possession with 5.51 dribbles per touch. The team avg is 2.61 drib/touch (elevated).
Compared to 2024-25 when Jalen Williams handled more, 2025-26 OKC has concentrated
around SGA. The "OKC is a movement team" mental model is from prior seasons.

**BOS at 77th percentile (predicted lower).** Top time-of-possession players are
Pritchard, White, Brown. Jayson Tatum is absent from the top of the list (recovering
from Finals injury). Without Tatum's gravity, the Celtics have leaned on Brown/
Pritchard iso, raising stickiness.

In all three cases the metric was right and the prior was based on outdated rosters.

**Wolves trajectory finding (the headline of this component).**

The 2024-25 -> 2025-26 drop from 68th to 30th percentile contradicts the LAFI thesis
on this component. The thesis predicted 2025-26 should be high on stickiness.

Possible explanations for Phase 5 to investigate:

1. The "feels like pickup" perception lives in the other four components
   (no off-ball motion, no actions, predictable shots) rather than ball stickiness.
2. The 2024-25 stickiness was driven by Randle integration year 1, when he dominated
   the ball as the new offensive hub. In 2025-26 the iso load may have decentralized
   across Ant + Randle + others, which would lower the lead-handler concentration
   metric without actually making the team more designed.
3. A team can be more "pickup" while being less "sticky" if the iso load is spread
   across three or four players instead of dominated by one.

**Open hypothesis for Phase 5 (do not change Component 1 over this):**

Compute the variance of time-of-possession share across the top 5 rotation players
for each Wolves season. If 2025-26 has lower lead-handler share but more uniform
distribution among the top 5 (versus 2024-25 where Randle dominated), that is a
different kind of pickup ball. This belongs in the Wolves writeup, not in the
metric construction.

**Conclusion for the build.** Component 1 measures what it claims to measure. Its
top/bottom rankings are internally consistent and roster-accurate. The Wolves'
2025-26 stickiness ranking is an honest finding even if it complicates the thesis.
Proceed to Component 2 and let the composite tell the full story.
"""


def write(df: pd.DataFrame) -> None:
    util.write_component_csv(df, COMPONENT_NAME, config.TABLE_DIR)
    util.write_eye_test_markdown(
        COMPONENT_NAME, df, config.TABLE_DIR,
        priors_md=PRIORS_MD,
        investigation_md=INVESTIGATION_MD,
    )
