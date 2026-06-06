"""
Q1 v2: PBP-derived splits.

Computes halfcourt vs transition offensive and defensive rating, clutch
performance, and shot distribution by zone for the Wolves and league
comparators. Uses lib.pbp for possession reconstruction.

Outputs:
    outputs/tables/q1_pbp_splits.parquet         per team-season-type splits
    outputs/tables/q1_shot_zones.parquet         shot zone distribution rows
    outputs/tables/q1_possessions_wolves.parquet raw possessions for the Wolves

Caveat: possession reconstruction in lib.pbp has known ~2% point drift from
edge cases (team rebounds, period-boundary shots, some technical scenarios).
The halfcourt vs transition ratio is not materially affected by this; absolute
ORtg numbers should be read with that error band in mind.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import db
from lib.pbp import (
    classify_shot_zone,
    reconstruct_possessions,
    tag_clutch,
    tag_garbage_time,
    tag_transition,
)


REPO = Path(__file__).resolve().parents[2]
TABLES_DIR = REPO / "outputs" / "tables"


_PBP_SQL = """
SELECT
    pbp.game_id, pbp.action_number, pbp.period, pbp.clock,
    pbp.team_id, pbp.team_tricode,
    pbp.action_type, pbp.sub_type, pbp.shot_result, pbp.shot_value,
    pbp.shot_distance, pbp.x_legacy, pbp.y_legacy,
    pbp.score_home, pbp.score_away, pbp.description
FROM nba_play_by_play pbp
WHERE pbp.game_id = ANY(%(game_ids)s)
ORDER BY pbp.game_id, pbp.action_number
"""


_GAMES_SQL = """
SELECT g.game_id, g.team_id, g.team_abbreviation, g.season_type, g.matchup,
       (g.season_id %% 10000)::int AS season_start_year
FROM nba_games g
WHERE g.season_type IN ('Regular Season','Playoffs')
  AND (g.season_id %% 10000) = %(year)s
  AND g.team_abbreviation = ANY(%(teams)s)
"""


def _pull_games(year: int, teams: list[str]) -> pd.DataFrame:
    return db.query(_GAMES_SQL, {"year": year, "teams": teams})


def _pull_pbp(game_ids: list[str]) -> pd.DataFrame:
    df = db.query(_PBP_SQL, {"game_ids": game_ids})
    # Cast to nullable types where useful
    for c in ("score_home", "score_away"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    return df


def reconstruct_all(pbp_all_games: pd.DataFrame) -> pd.DataFrame:
    """Run possession reconstruction game by game; return concatenated frame."""
    out = []
    for gid, sub in pbp_all_games.groupby("game_id", sort=False):
        _, poss = reconstruct_possessions(sub)
        if len(poss):
            out.append(poss)
    if not out:
        return pd.DataFrame()
    return pd.concat(out, ignore_index=True)


def attach_score_margins(
    possessions: pd.DataFrame,
    pbp: pd.DataFrame,
    games: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute start_score_diff (offense_score - defense_score at the start of
    each possession) using the PBP score_home/score_away snapshots and the
    home/away assignment from nba_games.matchup.

    Updates possessions.start_score_diff in place and returns the frame.
    """
    # Determine home_team_id per game from matchup string. "MIN @ SAS" -> MIN is away.
    g = games[["game_id", "team_id", "team_abbreviation", "matchup"]].drop_duplicates()
    home_map: dict[str, int] = {}
    for gid, sub in g.groupby("game_id", sort=False):
        # For each team-row, check whether their own matchup says "vs." (home) or "@" (away)
        for _, row in sub.iterrows():
            m = row.matchup or ""
            if " vs. " in m:
                home_map[gid] = int(row.team_id)
                break
            elif " @ " in m:
                # this row is the away team; the other row is home
                continue
        if gid not in home_map and len(sub) == 2:
            # if only "@" rows seen, derive home as the team that wasn't "@"
            for _, row in sub.iterrows():
                if " vs. " in (row.matchup or ""):
                    home_map[gid] = int(row.team_id)
                    break

    # Get score_home/score_away at the action just before start_action_number
    # (use the value at start_action_number itself; it's the running score
    # when the possession opens). Build a lookup dict keyed by (game_id, action_number).
    score_idx = pbp[["game_id", "action_number", "score_home", "score_away"]].copy()
    score_idx["score_home"] = pd.to_numeric(score_idx["score_home"], errors="coerce").fillna(method="ffill").fillna(0)
    score_idx["score_away"] = pd.to_numeric(score_idx["score_away"], errors="coerce").fillna(method="ffill").fillna(0)
    # Pad: forward-fill within game so non-shot actions inherit prior score
    score_idx = score_idx.sort_values(["game_id", "action_number"])
    score_idx["score_home"] = score_idx.groupby("game_id")["score_home"].ffill().fillna(0)
    score_idx["score_away"] = score_idx.groupby("game_id")["score_away"].ffill().fillna(0)

    p = possessions.copy()
    p = p.merge(
        score_idx,
        left_on=["game_id", "start_action_number"],
        right_on=["game_id", "action_number"],
        how="left",
    )
    p["home_team_id"] = p["game_id"].map(home_map)
    p["off_is_home"] = p["offense_team_id"] == p["home_team_id"]
    p["start_score_diff"] = np.where(
        p["off_is_home"],
        p["score_home"] - p["score_away"],
        p["score_away"] - p["score_home"],
    ).astype(float)
    keep_cols = [c for c in possessions.columns]
    # overwrite start_score_diff with computed value
    p_out = p[keep_cols].copy()
    p_out["start_score_diff"] = p["start_score_diff"].values
    return p_out


def aggregate_team_game_splits(
    possessions: pd.DataFrame,
    games: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach team-game context to each possession (team_abbreviation, season_type)
    and aggregate into one row per (team, season_type, split).

    Splits computed:
        all              all possessions
        halfcourt        transition flag False
        transition       transition flag True
        non_garbage      garbage-time flag False
        halfcourt_ng     halfcourt + non-garbage (the rigorous default)
        transition_ng    transition + non-garbage
    """
    p = possessions.copy()
    p["is_transition"] = tag_transition(p)
    p["is_garbage"] = tag_garbage_time(p)
    p["is_clutch"] = tag_clutch(p)

    # Attach offense and defense team_abbreviation via games
    # games has one row per (game_id, team_id). We need offense and defense per possession.
    g = games[["game_id", "team_id", "team_abbreviation", "season_type"]].drop_duplicates()
    p = p.merge(
        g.rename(columns={"team_id": "offense_team_id", "team_abbreviation": "off_team"}),
        on=["game_id", "offense_team_id"],
        how="left",
    )
    # Defense team_abbreviation: the other team in the same game
    pair = g.rename(columns={"team_id": "_tid", "team_abbreviation": "_abbr"})
    p = p.merge(
        pair[["game_id", "_tid", "_abbr"]].rename(columns={"_tid": "def_team_id", "_abbr": "def_team"}),
        left_on=["game_id"], right_on=["game_id"], how="left",
    )
    # Drop rows where def == off; we want the opposite team only.
    # (Merge above produced 2 rows per possession; filter to the opposing-team row.)
    p = p[p["def_team_id"] != p["offense_team_id"]].copy()

    splits = []

    def _agg(frame: pd.DataFrame, label: str, key_team: str) -> None:
        if len(frame) == 0:
            return
        g_off = frame.groupby([key_team, "season_type"], dropna=False)
        agg = pd.DataFrame({
            "possessions": g_off.size(),
            "points":      g_off["points"].sum(),
            "fga":         g_off["fga"].sum(),
            "fgm":         g_off["fgm"].sum(),
            "fg3a":        g_off["fg3a"].sum(),
            "fg3m":        g_off["fg3m"].sum(),
            "fta":         g_off["fta"].sum(),
            "ftm":         g_off["ftm"].sum(),
        }).reset_index().rename(columns={key_team: "team_abbreviation"})
        agg["split"] = label
        agg["side"]  = "offense" if key_team == "off_team" else "defense"
        agg["ortg_or_drtg"] = 100.0 * agg["points"] / agg["possessions"]
        agg["efg_pct"] = (agg["fgm"] + 0.5 * agg["fg3m"]) / agg["fga"]
        splits.append(agg)

    # Offense splits (group by offense team)
    _agg(p,                                "all_off",                 "off_team")
    _agg(p[~p["is_transition"]],           "halfcourt_off",           "off_team")
    _agg(p[ p["is_transition"]],           "transition_off",          "off_team")
    _agg(p[~p["is_garbage"]],              "all_off_ng",              "off_team")
    _agg(p[(~p["is_transition"]) & (~p["is_garbage"])], "halfcourt_off_ng", "off_team")
    _agg(p[( p["is_transition"]) & (~p["is_garbage"])], "transition_off_ng","off_team")

    # Defense splits (group by defense team; "points" here means opponent's points scored against us)
    _agg(p,                                "all_def",                 "def_team")
    _agg(p[~p["is_transition"]],           "halfcourt_def",           "def_team")
    _agg(p[ p["is_transition"]],           "transition_def",          "def_team")
    _agg(p[~p["is_garbage"]],              "all_def_ng",              "def_team")
    _agg(p[(~p["is_transition"]) & (~p["is_garbage"])], "halfcourt_def_ng", "def_team")
    _agg(p[( p["is_transition"]) & (~p["is_garbage"])], "transition_def_ng","def_team")

    # Clutch splits (last 5 min of period >= 4, |margin| <= 5)
    _agg(p[ p["is_clutch"]], "clutch_off", "off_team")
    _agg(p[ p["is_clutch"]], "clutch_def", "def_team")

    return pd.concat(splits, ignore_index=True)


def shot_zone_distribution(pbp_all_games: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame:
    """
    For each (team_abbreviation, season_type, side), compute shot zone counts and
    eFG. side='offense' counts a team's own shots; side='defense' counts shots
    by the opposing team in the games that team played.
    """
    shots = pbp_all_games[pbp_all_games.action_type.isin(["2pt", "3pt"])].copy()
    shots["zone"] = shots.apply(
        lambda r: classify_shot_zone(r["shot_distance"], r["x_legacy"], r["y_legacy"], r["shot_value"]),
        axis=1,
    )
    shots["made"] = (shots["shot_result"] == "Made").astype(int)
    shots["is_three"] = (shots["shot_value"] == 3).astype(int)

    # Attach team_abbreviation
    g = games[["game_id", "team_id", "team_abbreviation", "season_type"]].drop_duplicates()
    s_off = shots.merge(
        g.rename(columns={"team_id": "shooter_team_id", "team_abbreviation": "shooter"}),
        left_on=["game_id", "team_id"], right_on=["game_id", "shooter_team_id"], how="left",
    )
    s_off["side"] = "offense"
    s_off["team_abbreviation"] = s_off["shooter"]

    s_def = shots.merge(
        g[["game_id", "team_id", "team_abbreviation", "season_type"]],
        on=["game_id"], how="left",
    )
    s_def = s_def[s_def["team_id_x"] != s_def["team_id_y"]].copy()
    s_def["side"] = "defense"
    s_def["team_abbreviation"] = s_def["team_abbreviation"]
    s_def["season_type"] = s_def["season_type"]

    s_off = s_off[["team_abbreviation", "season_type", "side", "zone", "made", "is_three"]]
    s_def = s_def.rename(columns={"team_id_x": "team_id"})
    s_def = s_def[["team_abbreviation", "season_type", "side", "zone", "made", "is_three"]]

    s = pd.concat([s_off, s_def], ignore_index=True)
    g_s = s.groupby(["team_abbreviation", "season_type", "side", "zone"], dropna=False)
    out = pd.DataFrame({
        "attempts": g_s.size(),
        "makes":    g_s["made"].sum(),
        "threes":   g_s["is_three"].sum(),
    }).reset_index()
    out["pct"] = out["makes"] / out["attempts"]
    return out


def main_wolves_only() -> None:
    """Wolves-only v1. Skip league comparators for now to keep iteration tight."""
    print("[Q1 PBP] Pulling Wolves 25-26 games...")
    games = _pull_games(year=2025, teams=["MIN"])
    print(f"[Q1 PBP]   games: {len(games)}")
    # We also need the opposing teams for these games to do defense splits properly,
    # so pull rows for both teams in those games.
    game_ids = games["game_id"].unique().tolist()
    print("[Q1 PBP] Pulling all team-rows for those games...")
    games_full = db.query(
        "SELECT game_id, team_id, team_abbreviation, season_type, matchup FROM nba_games WHERE game_id = ANY(%(g)s)",
        {"g": game_ids},
    )
    print(f"[Q1 PBP]   team-game rows: {len(games_full)}")

    print(f"[Q1 PBP] Pulling PBP for {len(game_ids)} games...")
    pbp_all = _pull_pbp(game_ids)
    print(f"[Q1 PBP]   PBP rows: {len(pbp_all):,}")

    print("[Q1 PBP] Reconstructing possessions across all games...")
    possessions = reconstruct_all(pbp_all)
    print(f"[Q1 PBP]   possessions: {len(possessions):,}")

    print("[Q1 PBP] Attaching score margins for garbage-time / clutch tagging...")
    possessions = attach_score_margins(possessions, pbp_all, games_full)

    print("[Q1 PBP] Aggregating splits...")
    splits = aggregate_team_game_splits(possessions, games_full)

    print("[Q1 PBP] Computing shot zone distribution...")
    zones = shot_zone_distribution(pbp_all, games_full)

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    splits_path = TABLES_DIR / "q1_pbp_splits.parquet"
    zones_path  = TABLES_DIR / "q1_shot_zones.parquet"
    poss_path   = TABLES_DIR / "q1_possessions_wolves.parquet"

    splits.to_parquet(splits_path)
    zones.to_parquet(zones_path)
    possessions.to_parquet(poss_path)

    print(f"[Q1 PBP] Wrote {splits_path.relative_to(REPO)}")
    print(f"[Q1 PBP] Wrote {zones_path.relative_to(REPO)}")
    print(f"[Q1 PBP] Wrote {poss_path.relative_to(REPO)}")

    print()
    print("=== Wolves halfcourt vs transition (offense), by season_type ===")
    pick = splits[(splits.team_abbreviation == "MIN") & (splits.side == "offense")
                  & splits.split.isin(["halfcourt_off_ng", "transition_off_ng", "all_off_ng"])]
    print(pick.sort_values(["season_type", "split"])[
        ["season_type", "split", "possessions", "points", "ortg_or_drtg", "efg_pct"]
    ].to_string(index=False))
    print()
    print("=== Wolves halfcourt vs transition (defense), by season_type ===")
    pick = splits[(splits.team_abbreviation == "MIN") & (splits.side == "defense")
                  & splits.split.isin(["halfcourt_def_ng", "transition_def_ng", "all_def_ng"])]
    print(pick.sort_values(["season_type", "split"])[
        ["season_type", "split", "possessions", "points", "ortg_or_drtg", "efg_pct"]
    ].to_string(index=False))
    print()
    print("=== Wolves shot zones (offense) ===")
    z = zones[(zones.team_abbreviation == "MIN") & (zones.side == "offense")]
    print(z.sort_values(["season_type", "zone"])[["season_type", "zone", "attempts", "makes", "pct"]].to_string(index=False))
    print()
    print("=== Wolves clutch performance ===")
    clutch = splits[(splits.team_abbreviation == "MIN") & splits.split.isin(["clutch_off", "clutch_def"])]
    print(clutch.sort_values(["season_type", "side"])[
        ["season_type", "side", "split", "possessions", "points", "ortg_or_drtg", "efg_pct"]
    ].to_string(index=False))
    print()
    print("=== Garbage-time check: how many possessions tagged as garbage ===")
    p = pd.read_parquet(TABLES_DIR / "q1_possessions_wolves.parquet") if False else possessions
    n_gt = int((p["start_score_diff"].abs() > 15).sum())
    print(f"   total possessions: {len(p):,}; |margin| > 15 at start: {n_gt:,}")


if __name__ == "__main__":
    main_wolves_only()
