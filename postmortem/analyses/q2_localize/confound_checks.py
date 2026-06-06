"""Confound checks for Q2 cohort findings: Gobert+Naz and Gobert+Randle
pairings, with Edwards-injury context propagated through each.

For each cohort:
  - Minutes distribution by series (R1 DEN vs R2 SAS)
  - Minutes distribution by Edwards availability (Normal / Limited / DNP)
  - Edwards on-floor vs off-floor distribution within the cohort
  - Score margin at stint start (Wolves leading vs trailing)
  - Bootstrap CI on net rating

Output: outputs/findings/lineup_pipeline/02_pairing_confound_checks.md
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

import numpy as np
import pandas as pd

from lib import db, lineups, lineup_aggregation as agg
from analyses.q2_localize import config, analysis, batch, edwards_timeline


def load_wolves_po_stints() -> pd.DataFrame:
    cache = config.CACHE_DIR / "wolves_2025_stints"
    df = batch.load_cached_stints(cache)
    wolves = df[df["team_id"] == config.WOLVES_TEAM_ID].copy()
    splits = analysis.split_stints_by_season_type(wolves, season_year=2025)
    po = splits.get("Playoffs", pd.DataFrame()).copy()
    po = po[~po["in_garbage_time"]].copy()
    return po


def annotate_stints_with_context(stints: pd.DataFrame) -> pd.DataFrame:
    """For each stint add: matchup, opponent, series_label, edwards_status
    (from edwards_timeline), score_margin_at_start (Wolves perspective).
    """
    df = stints.copy()
    game_ids = sorted(df["game_id"].unique())
    placeholders = ",".join(["%s"] * len(game_ids))
    meta = db.query(
        f"""SELECT game_id, game_date, matchup, plus_minus
            FROM nba_games
            WHERE team_id = %s AND game_id IN ({placeholders})
            ORDER BY game_date""",
        (config.WOLVES_TEAM_ID, *game_ids),
    )
    meta["game_date"] = pd.to_datetime(meta["game_date"])
    meta = meta.reset_index(drop=True)
    meta["series_label"] = meta["matchup"].apply(_classify_series)
    meta["game_seq_in_series"] = meta.groupby("series_label").cumcount() + 1

    # Edwards timeline for status lookup.
    et = edwards_timeline.build_timeline(2025)
    et_po = et[et["season_type"] == "Playoffs"].copy()
    edwards_status = dict(zip(et_po["game_id"], et_po["status"]))
    edwards_min = dict(zip(et_po["game_id"], et_po["minutes_played"]))

    df = df.merge(meta[["game_id", "game_date", "matchup", "series_label",
                          "game_seq_in_series"]], on="game_id", how="left")
    df["edwards_status"] = df["game_id"].map(edwards_status).fillna("Unknown")
    df["edwards_minutes"] = df["game_id"].map(edwards_min).fillna(0)
    df["edwards_on_floor"] = df["lineup_id"].apply(
        lambda lid: analysis.player_in_lineup(lid, config.ANT_ID))

    # Score margin at stint start: re-load PBP per game and look up.
    margin_map = {}
    for gid in game_ids:
        annotated = lineups.derive_floor_state_per_event(gid)
        # Use the score columns directly.
        if "score_home" not in annotated.columns:
            continue
        annotated["score_home"] = pd.to_numeric(annotated["score_home"], errors="coerce").ffill().fillna(0)
        annotated["score_away"] = pd.to_numeric(annotated["score_away"], errors="coerce").ffill().fillna(0)
        # Determine which is the Wolves' score using matchup.
        m_row = meta[meta["game_id"] == gid].iloc[0]
        wolves_home = "vs." in m_row["matchup"]
        if wolves_home:
            annotated["wolves_score"] = annotated["score_home"]
            annotated["opp_score"] = annotated["score_away"]
        else:
            annotated["wolves_score"] = annotated["score_away"]
            annotated["opp_score"] = annotated["score_home"]
        annotated["wolves_margin"] = annotated["wolves_score"] - annotated["opp_score"]
        margin_map[gid] = annotated[["period", "clock_seconds_remaining", "wolves_margin"]]

    def _margin_at_start(row):
        gid = row["game_id"]
        if gid not in margin_map:
            return np.nan
        ann = margin_map[gid]
        period = row["period_start"]
        clock = row["clock_start_sec"]
        if pd.isna(period) or pd.isna(clock):
            return np.nan
        # Find the first event in the same period at clock <= clock_start
        mask = (ann["period"] == int(period)) & (ann["clock_seconds_remaining"].fillna(-1) <= float(clock))
        sub = ann[mask]
        if sub.empty:
            # Look at events earlier in the period
            mask2 = ann["period"] == int(period)
            sub2 = ann[mask2]
            if sub2.empty:
                return np.nan
            return float(sub2.iloc[-1]["wolves_margin"])
        return float(sub.iloc[0]["wolves_margin"])

    df["margin_at_start"] = df.apply(_margin_at_start, axis=1)
    return df


def _classify_series(matchup: str) -> str:
    """Coarse series labeler from matchup string."""
    if "DEN" in matchup:
        return "R1_vs_DEN"
    if "SAS" in matchup:
        return "R2_vs_SAS"
    return "Other"


# ---------------------------------------------------------------------------
# Cohort filters
# ---------------------------------------------------------------------------


def filter_gobert_naz_no_randle(stints: pd.DataFrame) -> pd.DataFrame:
    return stints[
        stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.GOBERT_ID))
        & stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.NAZ_ID))
        & stints["lineup_id"].apply(lambda lid: not analysis.player_in_lineup(lid, config.RANDLE_ID))
    ].copy()


def filter_gobert_randle_no_naz(stints: pd.DataFrame) -> pd.DataFrame:
    return stints[
        stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.GOBERT_ID))
        & stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.RANDLE_ID))
        & stints["lineup_id"].apply(lambda lid: not analysis.player_in_lineup(lid, config.NAZ_ID))
    ].copy()


def filter_triple_big(stints: pd.DataFrame) -> pd.DataFrame:
    return stints[
        stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.GOBERT_ID))
        & stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.NAZ_ID))
        & stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.RANDLE_ID))
    ].copy()


# ---------------------------------------------------------------------------
# Confound check summary
# ---------------------------------------------------------------------------


def cohort_summary(stints: pd.DataFrame) -> dict:
    if stints.empty:
        return {"n_stints": 0, "minutes": 0.0}
    total_min = stints["duration_sec"].sum() / 60.0
    poss_off = stints["possessions_off"].sum()
    poss_def = stints["possessions_def"].sum()
    pts_for = stints["points_for"].sum()
    pts_against = stints["points_against"].sum()
    net = 100 * pts_for / poss_off - 100 * pts_against / poss_def if poss_off and poss_def else np.nan
    off_rtg = 100 * pts_for / poss_off if poss_off else np.nan
    def_rtg = 100 * pts_against / poss_def if poss_def else np.nan
    fga = stints["fga_off"].sum()
    fg3a = stints["fg3a_off"].sum()
    fg3a_per_100 = 100 * fg3a / poss_off if poss_off else np.nan
    tpa_rate = fg3a / fga if fga else np.nan

    # Bootstrap CI on net rating
    bs = analysis.bootstrap_lineup_metric(stints, analysis.m_net_rating)

    # Breakdowns
    by_series = (stints.groupby("series_label", dropna=False)
                   .agg(stints_n=("duration_sec", "count"),
                        minutes=("duration_sec", lambda x: x.sum() / 60),
                        poss_off=("possessions_off", "sum"),
                        poss_def=("possessions_def", "sum"),
                        pts_for=("points_for", "sum"),
                        pts_against=("points_against", "sum"))
                   .reset_index())
    by_series["net"] = 100 * by_series["pts_for"] / by_series["poss_off"].replace(0, np.nan) \
                        - 100 * by_series["pts_against"] / by_series["poss_def"].replace(0, np.nan)

    by_edwards = (stints.groupby("edwards_status", dropna=False)
                    .agg(stints_n=("duration_sec", "count"),
                         minutes=("duration_sec", lambda x: x.sum() / 60),
                         poss_off=("possessions_off", "sum"),
                         poss_def=("possessions_def", "sum"),
                         pts_for=("points_for", "sum"),
                         pts_against=("points_against", "sum"))
                    .reset_index())
    by_edwards["net"] = 100 * by_edwards["pts_for"] / by_edwards["poss_off"].replace(0, np.nan) \
                          - 100 * by_edwards["pts_against"] / by_edwards["poss_def"].replace(0, np.nan)

    by_edwards_on_floor = (stints.groupby("edwards_on_floor", dropna=False)
                             .agg(stints_n=("duration_sec", "count"),
                                  minutes=("duration_sec", lambda x: x.sum() / 60),
                                  poss_off=("possessions_off", "sum"),
                                  poss_def=("possessions_def", "sum"),
                                  pts_for=("points_for", "sum"),
                                  pts_against=("points_against", "sum"))
                             .reset_index())
    by_edwards_on_floor["net"] = 100 * by_edwards_on_floor["pts_for"] / by_edwards_on_floor["poss_off"].replace(0, np.nan) \
                                  - 100 * by_edwards_on_floor["pts_against"] / by_edwards_on_floor["poss_def"].replace(0, np.nan)

    # Margin distribution: bucketed
    margin_buckets = stints["margin_at_start"].apply(_bucket_margin).value_counts().sort_index()

    return {
        "n_stints": len(stints),
        "minutes": float(total_min),
        "possessions_off": int(poss_off),
        "possessions_def": int(poss_def),
        "net_rating": float(net),
        "net_ci_lo": bs["ci_lo"],
        "net_ci_hi": bs["ci_hi"],
        "off_rating": float(off_rtg),
        "def_rating": float(def_rtg),
        "off_3pa_rate": float(tpa_rate),
        "fg3a_per_100": float(fg3a_per_100),
        "by_series": by_series,
        "by_edwards_status": by_edwards,
        "by_edwards_on_floor": by_edwards_on_floor,
        "margin_buckets": margin_buckets,
    }


def _bucket_margin(m: float) -> str:
    if pd.isna(m):
        return "?"
    if m <= -10:
        return "Trailing 10+"
    if m <= -3:
        return "Trailing 3-10"
    if m < 3:
        return "Close (-2..+2)"
    if m < 10:
        return "Leading 3-10"
    return "Leading 10+"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def render_summary(name: str, summary: dict) -> str:
    if summary["n_stints"] == 0:
        return f"### {name}: empty cohort\n\n"
    lines = [f"### {name}\n"]
    lines.append(f"- **Stints:** {summary['n_stints']}  ")
    lines.append(f"- **Minutes:** {summary['minutes']:.1f}  ")
    lines.append(f"- **Possessions (off/def):** {summary['possessions_off']} / {summary['possessions_def']}  ")
    lines.append(f"- **Net rating:** **{summary['net_rating']:+.2f}** (95% CI [{summary['net_ci_lo']:+.2f}, {summary['net_ci_hi']:+.2f}])  ")
    lines.append(f"- **Off rating:** {summary['off_rating']:.1f}  /  **Def rating:** {summary['def_rating']:.1f}  ")
    lines.append(f"- **Off 3PA rate:** {summary['off_3pa_rate']:.3f}  ")
    lines.append(f"- **fg3a per 100:** {summary['fg3a_per_100']:.1f}\n")
    lines.append("**By series:**\n")
    lines.append("```\n" + summary["by_series"][["series_label", "stints_n", "minutes", "poss_off", "poss_def", "pts_for", "pts_against", "net"]].round(2).to_string(index=False) + "\n```\n")
    lines.append("**By Edwards game-status (the game the stint was played in):**\n")
    lines.append("```\n" + summary["by_edwards_status"][["edwards_status", "stints_n", "minutes", "poss_off", "poss_def", "pts_for", "pts_against", "net"]].round(2).to_string(index=False) + "\n```\n")
    lines.append("**By Edwards on the floor (was Ant in this lineup_id):**\n")
    lines.append("```\n" + summary["by_edwards_on_floor"][["edwards_on_floor", "stints_n", "minutes", "poss_off", "poss_def", "pts_for", "pts_against", "net"]].round(2).to_string(index=False) + "\n```\n")
    lines.append("**Score margin at stint start (Wolves perspective):**\n")
    lines.append("```\n" + summary["margin_buckets"].to_string() + "\n```\n")
    return "\n".join(lines) + "\n"


def run():
    print("Loading Wolves 2025-26 PO stints and annotating with context...")
    stints = load_wolves_po_stints()
    stints = annotate_stints_with_context(stints)
    print(f"  {len(stints)} stints across {stints['game_id'].nunique()} games")

    # Cohorts of interest
    gn = filter_gobert_naz_no_randle(stints)
    gr = filter_gobert_randle_no_naz(stints)
    triple = filter_triple_big(stints)

    sgn = cohort_summary(gn)
    sgr = cohort_summary(gr)
    stb = cohort_summary(triple)

    out_md = []
    out_md.append("# Confound checks: Gobert+Naz and Gobert+Randle pairings\n")
    out_md.append("**Date:** 2026-05-17\n")
    out_md.append("**Cohorts:** 2025-26 playoffs, gt-filtered Wolves stints.\n")
    out_md.append("**Context variables:** series (R1 vs DEN / R2 vs SAS), Edwards game-availability status (DNP / Limited / Normal), Edwards on-floor flag (whether Ant was actually in this specific lineup_id), score margin at stint start.\n")
    out_md.append("**Bootstrap:** 1000 resamples of stints with replacement, seed=42.\n\n")

    out_md.append("## Cohort A: Gobert+Naz on floor, Randle OFF\n")
    out_md.append(render_summary("Gobert+Naz, no Randle", sgn))

    out_md.append("## Cohort B: Gobert+Randle on floor, Naz OFF\n")
    out_md.append(render_summary("Gobert+Randle, no Naz", sgr))

    out_md.append("## Cohort C: All three bigs on floor (triple-big)\n")
    out_md.append(render_summary("Gobert+Naz+Randle", stb))

    out_path = Path("outputs/findings/lineup_pipeline/02_pairing_confound_checks.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(out_md), encoding="utf-8")
    print(f"\nWrote {out_path}")

    # Also stdout
    for line in out_md:
        print(line)


if __name__ == "__main__":
    run()
