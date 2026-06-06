"""Component 4: Action Poverty (20% LAFI weight).

Whether the offense runs a diverse, frequent set of recognizable actions or
the same two or three things every time down. Spec section 2.5.

**v1 vs v2 note (important).** The spec calls for sub-metrics that require a
custom action classifier from PBP. That classifier does not yet exist in this
project. v1 of Component 4 substitutes Synergy-derived proxies. The proxies
capture the same conceptual idea (how diverse is the playbook, how much
designed off-ball architecture does the offense run) but at a coarser grain.

If v1 confirms what the eye test suggests, the finding is suggestive. v2 with
the full action classifier will sharpen the result. If v1 disagrees with the
eye test, the disagreement might be a v1 artifact and v2 is required to
resolve.

Sub-metrics (sign convention: higher = more pickup):

  1. inv_play_type_entropy
       Shannon entropy of Synergy play-type frequencies (11 types) for the
       team. Low entropy = team concentrates in few play types = repetitive
       playbook = more pickup. Sign-flipped so higher = more pickup.

  2. inv_designed_action_share
       Sum of Cut + OffScreen + Handoff + Spotup poss_pct. The "designed
       off-ball and motion" action types. Lower share = less designed.
       Sign-flipped.

  3. ball_dominant_action_share
       Sum of Iso + PRBallHandler + Postup poss_pct. The "give it to the guy"
       action types. Higher share = more pickup. No flip.

Sub-metric 4 from the spec (off-ball action share) is captured indirectly
through sub-metric 2; not split out separately in v1 to avoid double-counting.

Action diversity annotation (eye-test only):
  Count of Synergy play types with non-trivial team usage (poss_pct >= 0.03,
  i.e., at least 3% of possessions). This is the v1 analog of "unique action
  types per game." A team that uses only 4 play types at >3% usage is much
  more pickup-like than a team using 8.

Inputs:
  nba_synergy_team_play_types   all 11 play_types, type_grouping='Offensive'
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd

from analyses.q0a_lafi import config, data, util


COMPONENT_NAME = "action_poverty"

DESIGNED_PLAY_TYPES = ("Cut", "OffScreen", "Handoff", "Spotup")
BALL_DOMINANT_PLAY_TYPES = ("Isolation", "PRBallHandler", "Postup")
ACTION_DIVERSITY_THRESHOLD = 0.03  # 3% of possessions to count as a "used" action


def _shannon_entropy(p: np.ndarray) -> float:
    """Natural-log Shannon entropy. Returns 0 for empty/uniform-zero inputs."""
    p = np.asarray(p, dtype=float)
    p = p[p > 0]
    if p.size == 0 or p.sum() <= 0:
        return 0.0
    p = p / p.sum()
    return float(-np.sum(p * np.log(p)))


def _action_diversity_count(p: np.ndarray, threshold: float = ACTION_DIVERSITY_THRESHOLD) -> int:
    """Count of play types used at or above the threshold share."""
    p = np.asarray(p, dtype=float)
    return int(np.sum(p >= threshold))


def compute(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = ("Regular Season",),
) -> pd.DataFrame:
    season_types = list(season_types) if season_types is not None else list(config.SEASON_TYPES)

    syn = data.load_synergy_team(
        years=years, season_types=season_types, type_grouping="Offensive"
    )
    # Pivot to wide: one row per (team, season, season_type), 11 play_type cols.
    pivot = (syn
             .pivot_table(index=["team_id", "team_abbreviation", "season_year",
                                 "season_type", "season_start_year"],
                          columns="play_type", values="poss_pct", aggfunc="first")
             .reset_index())
    pivot.columns.name = None

    play_type_cols = [pt for pt in data.SYNERGY_PLAY_TYPES if pt in pivot.columns]
    pivot[play_type_cols] = pivot[play_type_cols].fillna(0.0)

    # Entropy across the play-type vector, per team-season.
    pivot["play_type_entropy"] = pivot[play_type_cols].apply(
        lambda row: _shannon_entropy(row.values), axis=1
    )

    # Action diversity count (eye-test annotation).
    pivot["action_diversity_count"] = pivot[play_type_cols].apply(
        lambda row: _action_diversity_count(row.values), axis=1
    )

    # Designed-action share and ball-dominant-action share.
    designed_cols = [c for c in DESIGNED_PLAY_TYPES if c in pivot.columns]
    bd_cols = [c for c in BALL_DOMINANT_PLAY_TYPES if c in pivot.columns]
    pivot["designed_action_share"] = pivot[designed_cols].sum(axis=1)
    pivot["ball_dominant_action_share"] = pivot[bd_cols].sum(axis=1)

    # Top handler annotation for the trajectory chart.
    player_poss = data.load_player_tracking_season(
        years=years, season_types=season_types, measure_types=["Possessions"]
    )[["team_id", "season_year", "season_type", "player_name", "time_of_poss"]]
    top_handler = util.top_handler_per_team_season(player_poss)[[
        "team_id", "season_year", "season_type", "top_handler_name"]]

    df = pivot.merge(top_handler, on=["team_id", "season_year", "season_type"], how="left")

    # Sub-metrics, sign-oriented so higher = more pickup.
    sub = {}
    sub["inv_play_type_entropy"] = -1.0 * df["play_type_entropy"]
    sub["inv_designed_action_share"] = -1.0 * df["designed_action_share"]
    sub["ball_dominant_action_share"] = df["ball_dominant_action_share"]

    base = df[["team_id", "team_abbreviation", "season_start_year",
               "season_year", "season_type", "top_handler_name",
               "play_type_entropy", "action_diversity_count",
               "designed_action_share", "ball_dominant_action_share"]].rename(
                   columns={"season_year": "season_label"})

    out = util.assemble_component_output(base, sub)
    return out


PRIORS_MD = """
- Wolves 2025-26 prediction: **80th to 95th percentile**, updated after
  Component 3 landed at 89. If Action Poverty lands below 70, that warrants
  investigation: either the v1 proxy isn't catching what feels obvious from the
  eye test, or the Q4 diagnosis needs refining.
- The action_diversity_count annotation should show Wolves using fewer distinct
  Synergy play types at >=3% than the championship-archetype teams (Pacers,
  Celtics, Warriors usually run 7-8 distinct actions at meaningful frequency).
- Expected high pickup-side: ball-dominant single-star offenses (PHI, OKC, NOP,
  LAC, MIL, MIN).
- Expected low pickup-side: motion offenses (GSW, IND, BOS, ATL post-Trae).

**v1 vs v2 transparency.** This component uses Synergy-derived proxies because
the action classifier from PBP doesn't exist yet. If v1 confirms the eye-test,
the finding is suggestive. v2 with the full classifier will sharpen it.
"""

INVESTIGATION_MD = """
**Wolves 2025-26 landed at 45th percentile. The user's prior was 80-95.**

This is below the user's "investigate if below 70" threshold. The first move is
to check whether the v1 proxy is the issue or whether the diagnosis needs
refining.

**Drill-in: Wolves 2025-26 Synergy play-type distribution vs the league.**

| Team | Cut | OffScr | Cut+OffScr | Handoff | Spotup | Iso | PRBH | Post | Trans |
|---|---|---|---|---|---|---|---|---|---|
| **MIN** | 0.052 | 0.050 | **0.102** | 0.057 | 0.229 | **0.096** | **0.131** | 0.041 | 0.190 |
| LAC  | 0.067 | 0.022 | 0.089 | 0.034 | 0.219 | 0.116 | 0.151 | 0.056 | 0.162 |
| LAL  | 0.078 | 0.052 | 0.130 | 0.022 | 0.199 | 0.085 | 0.170 | 0.055 | 0.177 |
| PHI  | 0.062 | 0.033 | 0.095 | 0.040 | 0.230 | 0.099 | 0.141 | 0.039 | 0.185 |
| BOS  | 0.054 | 0.049 | 0.103 | 0.053 | 0.231 | 0.096 | 0.183 | 0.020 | 0.150 |
| GSW  | 0.096 | 0.065 | 0.161 | 0.041 | 0.267 | 0.055 | 0.128 | 0.028 | 0.160 |
| IND  | 0.059 | 0.045 | 0.104 | 0.041 | 0.258 | 0.050 | 0.163 | 0.040 | 0.193 |
| ATL  | 0.076 | 0.056 | 0.132 | 0.060 | 0.223 | 0.042 | 0.147 | 0.028 | 0.216 |

**Wolves on Cut + OffScreen (pure off-ball motion architecture): 10.2%. That is
within 1 percentage point of BOS, IND, and PHI. Not low.** Even excluding Handoff
(which is on-ball) and Spotup (which is mixed), the Wolves are league-average
on designed off-ball motion.

**Where the Wolves ARE distinctive:**

- **Low PR-Ball-Handler share: 13.1%.** League high-iso teams run 14-18% PR-BH.
  The Wolves run less pick-and-roll than most contenders.
- **High Iso share: 9.6%.** Top quartile (matches what Component 3 found).
- **Low Spotup share: 22.9%.** Below league average. Surprising given the iso-
  ends-in-kickout intuition.

**Wolves year-over-year Synergy detail:**

| Season | Cut+OffScr | Handoff | Spotup | Iso | PRBH | Post |
|---|---|---|---|---|---|---|
| 2021-22 | 0.109 | 0.043 | 0.250 | 0.078 | 0.140 | 0.038 |
| 2022-23 | 0.110 | 0.044 | 0.252 | 0.070 | 0.153 | 0.031 |
| 2023-24 | 0.109 | 0.038 | 0.272 | 0.074 | 0.144 | 0.054 |
| 2024-25 | 0.108 | 0.045 | 0.256 | 0.078 | 0.163 | 0.033 |
| **2025-26** | **0.102** | **0.057** | **0.229** | **0.096** | **0.131** | **0.041** |

Off-ball motion (Cut + OffScreen) has been flat across all five seasons at 10-11%.
Iso rose from 7-8% to 9.6%. PR-Ball-Handler fell from 14-16% to 13.1%. **The
Wolves substituted iso for pick-and-roll, while leaving off-ball motion unchanged.**

**What this means: the v1 result is honest, but the diagnosis needs refining.**

The Q4 framing was: low stickiness, high motion death, very high iso, low action
diversity. The data says the first three hold, but the fourth does NOT. The
Wolves are not action-poor. They have a playbook of normal breadth. They are
**iso-overweighted within a normal-breadth playbook.**

That is a more specific diagnosis. Action-poor offenses (only 4 distinct
actions) are easy to recognize. The Wolves' issue is harder to see because they
DO run all the actions, just disproportionately iso.

**Where the v1 proxy is genuinely limited.**

The spec's Action Poverty includes "multi-action possession rate" (chained
actions like PnR -> flare -> cut). Synergy gives us frequencies, not chains. A
team that runs PR -> flare -> cut chains has more actions per possession than a
team that runs PR -> shot, but Synergy reports both as "1 PR possession." v2
with the full action classifier would let us check this directly. It's possible
the Wolves have a chaining problem v1 cannot see.

**Recommended interpretation.** Treat Component 4 as a refinement of the Q4
diagnosis, not a contradiction. The synthesis becomes:

Wolves' Q4 pathology = high motion death (C2) + very high iso reliance with
decentralized load (C3) + normal-breadth playbook but with iso substituting
for PR-Ball-Handler. NOT "they only run a couple of things." More precisely:
"they run plenty of things, but they choose iso when other choices would be
better."

**No metric change warranted in v1.** v2 with the action classifier should
add multi-action density. If that comes back low for the Wolves, the
"action poverty" framing reattaches; if it doesn't, the refined diagnosis
holds permanently.
"""


def validate(df: pd.DataFrame) -> None:
    util.eye_test_report(df, COMPONENT_NAME)
    print("\nPriors:")
    print("  Wolves 2025-26: predicted 80-95 percentile.")
    print("  If <70, investigate: v1 proxy issue or Q4 diagnosis needs refining.")
    print("\nAction diversity annotation (Wolves trajectory):")
    wolves = df[(df["team_id"] == config.WOLVES_TEAM_ID)
                & (df["season_type"] == "Regular Season")].sort_values("season_start_year")
    for _, r in wolves.iterrows():
        yr = int(r["season_start_year"])
        ent = r.get("play_type_entropy")
        n = r.get("action_diversity_count")
        ent_s = f"{ent:.3f}" if pd.notna(ent) else "    -"
        print(f"  {yr}-{(yr+1)%100:02d}  entropy={ent_s}  play_types_at_3pct={int(n) if pd.notna(n) else '-'}  designed_share={r['designed_action_share']:.3f}  ball_dom_share={r['ball_dominant_action_share']:.3f}")
    print("\nSub-metric sanity (latest RS, top 5 by raw score):")
    latest = df[df["season_start_year"] == df["season_start_year"].max()]
    latest = latest[latest["season_type"] == "Regular Season"].nlargest(5, "raw_score")
    cols = ["team_abbreviation",
            "inv_play_type_entropy_raw", "inv_designed_action_share_raw",
            "ball_dominant_action_share_raw",
            "action_diversity_count", "raw_score", "percentile_rank"]
    print(latest[cols].to_string(index=False, float_format=lambda x: f"{x:.4f}"))


def write(df: pd.DataFrame) -> None:
    util.write_component_csv(df, COMPONENT_NAME, config.TABLE_DIR)
    util.write_eye_test_markdown(
        COMPONENT_NAME, df, config.TABLE_DIR,
        priors_md=PRIORS_MD,
        investigation_md=INVESTIGATION_MD,
    )
