"""Component 2: Movement Death (20% LAFI weight).

Whether the four off-ball players are actively contributing or standing and
watching. Spec section 2.3.

Sub-metrics (sign convention: higher = more pickup = less off-ball motion):

  1. inv_off_ball_miles_per_possession
       Total team offensive miles minus the lead handler's offensive miles,
       divided by 4 (the four off-ball players), divided by team possessions.
       Then sign-flipped because lower off-ball motion = more pickup.

       This is the v1 implementation of spec sub-metric 1. The spec wanted
       distance traveled per possession by the four off-ball players. We
       derive it by subtracting the lead handler's offensive distance from
       the team total and dividing by 4.

  2. inv_off_screen_frequency
       Synergy "OffScreen" play-type poss_pct, sign-flipped. Designed
       offenses run flares, pin-downs, staggers, hammers, wide pins. Pickup
       offenses don't.

  3. inv_cut_frequency
       Synergy "Cut" play-type poss_pct, sign-flipped. Designed offenses
       have many cuts. Pickup offenses have few.

Sub-metric 4 from the spec (inter-player spacing standard deviation from
court-coordinate tracking) is intentionally deferred to v2 per the spec's
section 2.3 note. v1 carries the component on the other three.

Inputs:
  nba_team_tracking_season   measure_type='SpeedDistance' (for team total miles)
  nba_player_tracking_season measure_type='SpeedDistance' (for lead-handler miles)
  nba_player_tracking_season measure_type='Possessions'   (to identify the lead)
  nba_synergy_team_play_types (for off-screen and cut frequencies)
  nba_team_advanced_stats    (aggregated to season possessions for denominator)
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd

from analyses.q0a_lafi import config, data, util


COMPONENT_NAME = "movement_death"


def _lead_handler_offense_miles(
    years, season_types
) -> pd.DataFrame:
    """For each (team, season, season_type) identify the lead handler (top
    time_of_poss from Possessions measure) and return their offensive miles
    (dist_miles_off from SpeedDistance measure).
    """
    poss = data.load_player_tracking_season(
        years=years, season_types=season_types, measure_types=["Possessions"]
    )[["player_id", "team_id", "season_year", "season_type", "player_name", "time_of_poss"]]
    top = util.top_handler_per_team_season(poss).rename(
        columns={"top_handler_top": "lead_top_of_poss"}
    )

    sd = data.load_player_tracking_season(
        years=years, season_types=season_types, measure_types=["SpeedDistance"]
    )[["player_id", "team_id", "season_year", "season_type", "dist_miles_off"]]

    # Match the lead handler (by player_id) to their SpeedDistance row.
    poss_id = poss.merge(
        top, on=["team_id", "season_year", "season_type"], how="inner"
    )
    poss_id = poss_id[poss_id["player_name"] == poss_id["top_handler_name"]]
    poss_id = poss_id[["player_id", "team_id", "season_year", "season_type",
                       "top_handler_name", "lead_top_of_poss"]]
    out = poss_id.merge(
        sd, on=["player_id", "team_id", "season_year", "season_type"], how="left"
    ).rename(columns={"dist_miles_off": "lead_dist_miles_off"})
    return out


def compute(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = ("Regular Season",),
) -> pd.DataFrame:
    season_types = list(season_types) if season_types is not None else list(config.SEASON_TYPES)

    # Team SpeedDistance for total offensive miles.
    team_sd = data.load_team_tracking_season(
        years=years, season_types=season_types, measure_types=["SpeedDistance"]
    )[["team_id", "team_abbreviation", "season_year", "season_type",
       "season_start_year", "gp", "dist_miles_off", "avg_speed_off"]]
    team_sd = team_sd.rename(columns={"dist_miles_off": "team_dist_miles_off"})

    # Lead handler offensive miles + name.
    lead = _lead_handler_offense_miles(years=years, season_types=season_types)

    # Team season-total possessions for the denominator.
    summary = data.load_team_season_summary(years=years, season_types=season_types)
    poss = summary[["team_id", "season_start_year", "season_type", "poss_total"]]

    # Synergy off-screen and cut frequencies (offensive play-type poss_pct).
    syn = data.load_synergy_team(years=years, season_types=season_types, type_grouping="Offensive")
    syn = syn[syn["play_type"].isin(["OffScreen", "Cut"])]
    syn_pivot = (syn
                 .pivot_table(index=["team_id", "season_year", "season_type"],
                              columns="play_type", values="poss_pct", aggfunc="first")
                 .reset_index())
    syn_pivot.columns.name = None
    for col in ("OffScreen", "Cut"):
        if col not in syn_pivot.columns:
            syn_pivot[col] = np.nan
    syn_pivot = syn_pivot.rename(columns={"OffScreen": "synergy_offscreen_pct",
                                          "Cut": "synergy_cut_pct"})

    # Merge.
    df = (team_sd
          .merge(lead, on=["team_id", "season_year", "season_type"], how="left")
          .merge(poss, on=["team_id", "season_start_year", "season_type"], how="left")
          .merge(syn_pivot, on=["team_id", "season_year", "season_type"], how="left"))

    for c in ("team_dist_miles_off", "lead_dist_miles_off", "poss_total",
              "synergy_offscreen_pct", "synergy_cut_pct"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Sub-metric 1: off-ball miles per possession (lead subtracted, /4), then negate.
    off_ball_miles = df["team_dist_miles_off"] - df["lead_dist_miles_off"]
    off_ball_miles_per_poss = (off_ball_miles / 4.0) / df["poss_total"]
    sub = {}
    sub["inv_off_ball_miles_per_possession"] = -1.0 * off_ball_miles_per_poss

    # Sub-metrics 2-3: Synergy off-screen and cut frequencies, sign-flipped.
    sub["inv_off_screen_frequency"] = -1.0 * df["synergy_offscreen_pct"]
    sub["inv_cut_frequency"] = -1.0 * df["synergy_cut_pct"]

    base = df[["team_id", "team_abbreviation", "season_start_year",
               "season_year", "season_type", "gp", "top_handler_name"]].rename(
                   columns={"season_year": "season_label"})
    out = util.assemble_component_output(base, sub)
    return out


def validate(df: pd.DataFrame) -> None:
    util.eye_test_report(df, COMPONENT_NAME)
    print("\nPriors to check against:")
    print("  Expected high (low movement): heavy iso teams without much off-ball motion")
    print("    Wolves 2024-25 and 2025-26, Hawks pre-Trae-trade, Mavs (Luka era), Nets")
    print("  Expected low (lots of movement): off-ball action systems")
    print("    Warriors (Steph era), Celtics (motion), Pacers (Carlisle), Nuggets (Jokic system)")
    print("\nSub-metric sanity (latest RS, top 5 by raw score):")
    latest = df[df["season_start_year"] == df["season_start_year"].max()]
    latest = latest[latest["season_type"] == "Regular Season"].nlargest(5, "raw_score")
    cols = ["team_abbreviation",
            "inv_off_ball_miles_per_possession_raw",
            "inv_off_screen_frequency_raw",
            "inv_cut_frequency_raw",
            "raw_score", "percentile_rank"]
    print(latest[cols].to_string(index=False, float_format=lambda x: f"{x:.4f}"))


PRIORS_MD = """
- The thesis predicts the 2025-26 Wolves should rise meaningfully on Movement Death
  versus the 2023-24 WCF year. "No off-ball motion" is one of the strongest pieces
  of the LA-Fitness perception.
- Expected high (low movement): heavy-iso teams, ball-dominant offenses.
- Expected low (lots of movement): Warriors with Steph, Celtics motion, Pacers,
  Nuggets system around Jokic.
- Stated prior for the Wolves: rise from 2023-24 (KAT era, motion) to 2025-26
  (Randle era, less motion).
"""

INVESTIGATION_MD = """
**The Wolves trajectory matches the stated prior cleanly.**

| Season | Pct | Top handler | Note |
|---|---|---|---|
| 2017-18 | 87 | Jeff Teague | Butler/Thibs peak iso era. |
| 2019-20 | 76 | D'Angelo Russell | KAT/Russell pre-Gobert. |
| 2022-23 | 63 | Mike Conley | First Gobert year. |
| 2023-24 | **43** | Anthony Edwards | WCF year, KAT gravity. Most movement of the Edwards era. |
| 2024-25 | **55** | Anthony Edwards | Randle year 1. Slight rise. |
| 2025-26 | **71** | Anthony Edwards | Randle year 2. Clear movement drop. |

The 28-percentile-point jump from 2023-24 (43) to 2025-26 (71) is a real signal. The
"no off-ball motion this year" perception is data-supported on this component.

**Cross-component pattern emerging.**

The Wolves' two-component profile so far:

- Component 1 (Ball Stickiness): 2025-26 RS = 30th percentile (moderate-low)
- Component 2 (Movement Death):  2025-26 RS = 71st percentile (high pickup)

The team is NOT especially sticky around a single handler, but the four off-ball
players are not moving. That is a specific kind of pickup ball: scattered iso
attempts by multiple players while the rest stand and watch. Different from
Brunson-NYK (sticky with motion) or Trae-era Hawks (sticky and no motion).

If Components 3 through 5 also show the Wolves elevated, the working synthesis
becomes: "The Wolves' LA Fitness problem is not ball stickiness; it's action
poverty and movement death." That is a sharper finding than the original thesis
and points to specific fixes (designed off-ball architecture) rather than the
vaguer "less iso."

**Other findings worth flagging.**

- **GSW at 2nd percentile.** Steph/Draymond motion. Sanity-passes the spec.
- **IND at 24th, BOS at 23rd, ATL at 15th.** The three lowest LAFI-pickup teams on
  movement. ATL's low rank confirms the post-Trae roster: not only did stickiness
  drop (Component 1, 26th pct), they actually move now.
- **MIA at 83rd percentile (predicted lower).** Heat were a movement team under
  prior rosters. The current iteration is more iso-driven than the brand suggests.
  Worth a roster check.
- **MIL at 88th, NOP at 85th, PHI at 86th.** Giannis, Zion, and Embiid-driven
  offenses respectively. All plausibly low on off-ball motion.

**No metric changes warranted.** The component is internally consistent, the
rankings are roster-plausible, and the Wolves trajectory directly supports a
working hypothesis. Proceed to Component 3 (Isolation Reliance).
"""


def write(df: pd.DataFrame) -> None:
    util.write_component_csv(df, COMPONENT_NAME, config.TABLE_DIR)
    util.write_eye_test_markdown(
        COMPONENT_NAME, df, config.TABLE_DIR,
        priors_md=PRIORS_MD,
        investigation_md=INVESTIGATION_MD,
    )
