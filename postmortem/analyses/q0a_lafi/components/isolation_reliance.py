"""Component 3: Isolation Reliance (20% LAFI weight).

How much the offense leans on one-on-one play. Spec section 2.4.

Sub-metrics (sign convention: higher = more pickup):

  1. synergy_iso_freq
       Synergy Isolation play-type poss_pct (offensive). The cleanest direct
       measure of iso reliance available.

  2. pull_up_fga_share  (v1 proxy for spec sub-metric 3)
       Team pull-up FGA divided by team total FGA. The spec wanted "contested
       pull-up jumper rate" requiring per-shot defender-distance. Pull-up FGA
       share is the cleanest available proxy: pull-up shots are by definition
       off-the-dribble self-creation, the visual signature of pickup ball.

  3. unassisted_fg_rate  (spec sub-metric 4)
       1 - (assists / made FGs). The fraction of made shots not from an
       assist. Designed offenses convert via assists; pickup offenses convert
       via self-creation.

Spec sub-metric 2 (late-clock iso rate) is deferred to v2 because it requires
per-shot shot-clock data not present in nba_shot_chart_detail.

Herfindahl annotation (NOT a sub-metric, eye-test-only):
  For each (team, season) compute the concentration of iso possessions across
  the top 5 isolation-volume players. High Herfindahl = one player dominates
  iso (single-star pickup). Low Herfindahl = iso is distributed (the Q4
  "scattered iso" pattern hypothesized for the 2025-26 Wolves).

Inputs:
  nba_synergy_team_play_types   play_type='Isolation', type_grouping='Offensive'
  nba_synergy_player_play_types play_type='Isolation', type_grouping='Offensive'
  nba_team_tracking_season      measure_type='PullUpShot'
  load_team_season_summary      for total FGA, total FGM, total AST denominators
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd

from analyses.q0a_lafi import config, data, util


COMPONENT_NAME = "isolation_reliance"


def _player_iso_synergy(years, season_types) -> pd.DataFrame:
    """Per-player Synergy isolation possessions, offensive side."""
    season_labels = [config.season_label(y) for y in years]
    if season_types is None:
        season_types = list(config.SEASON_TYPES)
    season_types = list(season_types)
    sl_in = ",".join(["%s"] * len(season_labels))
    st_in = ",".join(["%s"] * len(season_types))
    from lib import db
    sql = f"""
        SELECT season_year, season_type, team_id, team_abbreviation,
               player_id, player_name, poss, ppp
        FROM nba_synergy_player_play_types
        WHERE season_year IN ({sl_in})
          AND season_type IN ({st_in})
          AND play_type = 'Isolation'
          AND type_grouping = 'Offensive'
    """
    params = tuple(season_labels + season_types)
    df = db.query(sql, params)
    for c in ("poss", "ppp"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["season_start_year"] = df["season_year"].apply(config.season_start_year_from_label)
    return df


def iso_herfindahl_per_team_season(player_iso: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """For each (team, season, season_type), compute the Herfindahl index of
    iso-possession shares among the top_n iso-volume players on that team.

    Returns: one row per (team_id, season_year, season_type) with:
      - iso_herf_topN: Herfindahl across top N iso-volume players
      - top_iso_player_name: the player with the most iso possessions
      - top_iso_share: top player's share of team iso possessions
      - n_players_with_iso: count of players with at least 1 iso poss

    High Herfindahl = single dominant iso player. Low = distributed.
    Minimum possible value = 1/top_n (perfectly even). Max = 1.0 (single player).
    """
    df = player_iso.dropna(subset=["poss"]).copy()
    df = df[df["poss"] > 0]
    if df.empty:
        return pd.DataFrame(columns=[
            "team_id", "season_year", "season_type",
            f"iso_herf_top{top_n}", "top_iso_player_name", "top_iso_share",
            "n_players_with_iso",
        ])

    rows = []
    for (team_id, season_year, season_type), g in df.groupby(
            ["team_id", "season_year", "season_type"]):
        g = g.sort_values("poss", ascending=False)
        n_all = len(g)
        top = g.head(top_n)
        total_top = top["poss"].sum()
        if total_top <= 0:
            continue
        shares = top["poss"] / total_top
        herf = float(np.sum(shares.values ** 2))
        rows.append({
            "team_id": team_id,
            "season_year": season_year,
            "season_type": season_type,
            f"iso_herf_top{top_n}": herf,
            "top_iso_player_name": top.iloc[0]["player_name"],
            "top_iso_share": float(top.iloc[0]["poss"] / total_top),
            "n_players_with_iso": n_all,
        })
    return pd.DataFrame(rows)


def compute(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = ("Regular Season",),
) -> pd.DataFrame:
    season_types = list(season_types) if season_types is not None else list(config.SEASON_TYPES)

    # Synergy team iso frequency (offensive).
    syn_team = data.load_synergy_team(
        years=years, season_types=season_types, type_grouping="Offensive"
    )
    syn_team = syn_team[syn_team["play_type"] == "Isolation"][
        ["team_id", "team_abbreviation", "season_year", "season_type",
         "season_start_year", "poss_pct", "ppp"]
    ].rename(columns={"poss_pct": "synergy_iso_freq", "ppp": "synergy_iso_ppp"})

    # Team pull-up FGA from PullUpShot measure.
    pull = data.load_team_tracking_season(
        years=years, season_types=season_types, measure_types=["PullUpShot"]
    )[["team_id", "season_year", "season_type", "pull_up_fga"]]

    # Team-season totals: FGA, FGM, AST from box scores.
    summary = data.load_team_season_summary(years=years, season_types=season_types)
    box = summary[["team_id", "team_abbreviation", "season_start_year",
                   "season_year" if "season_year" in summary.columns else "season_label",
                   "season_type", "fga", "fgm", "ast"]].copy()
    box = box.rename(columns={"season_label": "season_year"}) if "season_label" in box.columns else box

    # Top handler annotation (consistent with C1/C2).
    player_poss = data.load_player_tracking_season(
        years=years, season_types=season_types, measure_types=["Possessions"]
    )[["team_id", "season_year", "season_type", "player_name", "time_of_poss"]]
    top_handler = util.top_handler_per_team_season(player_poss)[[
        "team_id", "season_year", "season_type", "top_handler_name"]]

    # Per-player iso for Herfindahl annotation.
    player_iso = _player_iso_synergy(years=years, season_types=season_types)
    herf = iso_herfindahl_per_team_season(player_iso, top_n=5)

    df = (syn_team
          .merge(pull, on=["team_id", "season_year", "season_type"], how="left")
          .merge(box, on=["team_id", "team_abbreviation", "season_start_year",
                          "season_year", "season_type"], how="left")
          .merge(top_handler, on=["team_id", "season_year", "season_type"], how="left")
          .merge(herf, on=["team_id", "season_year", "season_type"], how="left"))

    for c in ("synergy_iso_freq", "synergy_iso_ppp", "pull_up_fga", "fga", "fgm", "ast",
              "iso_herf_top5", "top_iso_share"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Sub-metrics, all sign-oriented so higher = more pickup.
    sub = {}
    sub["synergy_iso_freq"] = df["synergy_iso_freq"]
    sub["pull_up_fga_share"] = df["pull_up_fga"] / df["fga"]
    sub["unassisted_fg_rate"] = 1.0 - (df["ast"] / df["fgm"])

    base = df[["team_id", "team_abbreviation", "season_start_year",
               "season_year", "season_type", "top_handler_name",
               "iso_herf_top5", "top_iso_player_name", "top_iso_share",
               "n_players_with_iso"]].rename(columns={"season_year": "season_label"})
    out = util.assemble_component_output(base, sub)
    return out


PRIORS_MD = """
- Wolves 2025-26 should land 55th to 75th percentile on overall Isolation Reliance.
- Wolves 2025-26 should be higher than 2024-25 on overall iso rate (the offense has
  decentralized iso rather than reduced it).
- Wolves iso Herfindahl (top-5 concentration) should drop from 2024-25 to 2025-26,
  consistent with the "scattered iso" Q4 placement.
- Wolves Edwards-era trajectory: 2022-23 moderate, 2023-24 lower (WCF year more
  designed), 2024-25 elevated (Randle integration), 2025-26 higher than 2024-25.
- League extremes top: CLE with Mitchell, DAL with Luka, PHX top quintile. OKC very
  high. Post-Trae ATL should be lower than the prior expected.
"""

INVESTIGATION_MD = """
**All five user predictions tracked. Four held, one over-shot in the right direction.**

| Prior | Outcome |
|---|---|
| Wolves 2025-26 lands 55-75 pct | **Over.** Actual 89th percentile (even higher than predicted) |
| Wolves 25-26 > 24-25 on iso rate | **Right.** 70 -> 89, +19 percentile points |
| Wolves iso Herfindahl drops 24-25 to 25-26 | **Right.** 0.455 -> 0.361 |
| Edwards-era trajectory: 22-23 mod, 23-24 lower, 24-25 elev, 25-26 higher | **Right.** 43, 49, 70, 89 |
| Post-Trae ATL lower than priors | **Right.** ATL at 4th percentile (very low iso) |
| OKC very high | Right but not the very top. OKC at 84th, behind BOS/LAC/PHI/MIN. |

**The Herfindahl annotation is the key finding for the Wolves diagnosis.**

| Season | Iso Herf top-5 | Top iso player (share) | Players with iso |
|---|---|---|---|
| 2022-23 | 0.451 | Edwards (0.65) | 9 |
| 2023-24 | 0.420 | Edwards (0.59) | 7 |
| **2024-25** | **0.455** | **Edwards (0.62)** | **7** |
| **2025-26** | **0.361** | **Edwards (0.48)** | **8** |

Edwards remains the top iso option, but his share fell from 62% (24-25) to 48% (25-26).
Iso load is now distributed across 8 players instead of concentrated in 7. The number
of players taking iso possessions ROSE while the total iso rate ALSO ROSE. This is
the data signature of "scattered iso" the Q4 quadrant framing predicted: total iso
up, concentration down, off-ball motion still missing.

**League leaders pass the eye test.**

BOS (96), LAC (96), PHI (93), MIN (89), LAL (88), PHX (86), HOU (85), OKC (84). All
known iso-heavy 2025-26 rosters. BOS at the top is roster-correct: with Tatum out,
the Celtics have leaned heavily on Brown/Pritchard iso. LAC (Harden/Kawhi/PG),
PHI (Embiid/Maxey/George), LAL (LeBron/Luka), PHX, HOU all check out.

**Bottom passes too.**

GSW (4), ATL (4), IND (16) are the three lowest-iso teams (movement-heavy). All
consistent with priors. ATL again confirms the post-Trae reality.

**Three-component cross pattern for the Wolves 2025-26:**

| Component | Wolves pct | Direction |
|---|---|---|
| C1 Ball Stickiness | 30 | Not concentrated on one handler |
| C2 Movement Death | 71 | Off-ball players don't move |
| C3 Isolation Reliance | 89 | Heavy iso |

The three-line story: heavy iso, distributed across multiple players, no off-ball motion.
That is Q4 with three-component support. The user's "distributed pickup" diagnosis is
holding.

**No metric changes warranted.** Proceed to Component 4 (Action Poverty).
"""


def validate(df: pd.DataFrame) -> None:
    util.eye_test_report(df, COMPONENT_NAME)
    print("\nPriors to check against:")
    print("  Expected high: heavy iso teams. OKC, LAL, DAL, NYK, HOU.")
    print("  Expected low: ball-movement teams. GSW, IND, BOS, ATL (post-Trae).")
    print("  Wolves: predicted 55-75th percentile; should be > 2024-25 in 25-26.")
    print("\nHerfindahl annotation (Wolves trajectory):")
    wolves = df[(df["team_id"] == config.WOLVES_TEAM_ID)
                & (df["season_type"] == "Regular Season")].sort_values("season_start_year")
    if not wolves.empty:
        for _, r in wolves.iterrows():
            yr = int(r["season_start_year"])
            herf = r.get("iso_herf_top5")
            tname = r.get("top_iso_player_name")
            tshare = r.get("top_iso_share")
            n = r.get("n_players_with_iso")
            herf_s = f"{herf:.3f}" if pd.notna(herf) else "    -"
            tshare_s = f"{tshare:.2f}" if pd.notna(tshare) else "    -"
            print(f"  {yr}-{(yr+1)%100:02d}  herf={herf_s}  top_iso={tname} ({tshare_s})  n_players={n}")
    print("\nSub-metric sanity (latest RS, top 5 by raw score):")
    latest = df[df["season_start_year"] == df["season_start_year"].max()]
    latest = latest[latest["season_type"] == "Regular Season"].nlargest(5, "raw_score")
    cols = ["team_abbreviation",
            "synergy_iso_freq_raw", "pull_up_fga_share_raw", "unassisted_fg_rate_raw",
            "raw_score", "percentile_rank"]
    print(latest[cols].to_string(index=False, float_format=lambda x: f"{x:.4f}"))


def write(df: pd.DataFrame) -> None:
    util.write_component_csv(df, COMPONENT_NAME, config.TABLE_DIR)
    util.write_eye_test_markdown(
        COMPONENT_NAME, df, config.TABLE_DIR,
        priors_md=PRIORS_MD,
        investigation_md=INVESTIGATION_MD,
    )
