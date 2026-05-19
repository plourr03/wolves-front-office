"""
PBP utilities: clock parsing, possession reconstruction, garbage-time tagging,
clutch tagging, shot-zone classification.

The possession reconstructor walks an in-order PBP frame for a single game and
tags each action with a possession_id, offense_team_id, and the possession's
running points/result. Downstream code aggregates possessions into team-game
metrics or further into team-season splits.

A possession ends on:
    * a made field goal (next possession to the defense)
    * the last successful FT of a shooting trip without an offensive rebound
    * a defensive rebound (next possession to the rebounding team)
    * a turnover (next possession to the defending team)
    * end of period

Known simplifications in v1:
    * And-one free throws and 3-shot fouls are handled by the "last FT of trip"
      check, but flagrant/technical FT trips that don't end possession are
      treated as possession-enders. This is a small fraction of actions.
    * Lane-violation rebounds and other edge cases default to "defensive
      rebound semantics."
    * Possessions ending in a turnover plus immediate steal-and-score are
      modeled as two distinct possessions, which is the standard convention.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------
# PBP normalization
# --------------------------------------------------------------------------
#
# The warehouse stores PBP from two sources with different conventions:
#   * cdn (newer, lowercase): action_type values are "2pt", "3pt", "rebound",
#     "freethrow", "foul", "turnover", etc. Rebound sub_type is "offensive"
#     or "defensive". Free throw sub_type is "1 of 1", "2 of 2", etc.
#   * stats_api (older or alternate fetch path, Title Case): action_type values
#     are "Made Shot", "Missed Shot", "Rebound", "Free Throw", etc. Rebound
#     sub_type is "Unknown" in roughly 95% of cases (NBA's API does not always
#     return the offensive/defensive flag for stats_api fetches). Free throw
#     sub_type is "Free Throw 1 of 1", etc.
#
# normalize_pbp() coerces both formats to a single canonical lowercase form
# so reconstruct_possessions() can work uniformly. It also infers rebound
# offensive/defensive when sub_type is "Unknown" by looking at the most recent
# shot's team.


_SUBTYPE_FT_RE = re.compile(r"(\d+) of (\d+)")


def normalize_pbp(pbp: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of pbp with action_type, sub_type, shot_result coerced to
    the canonical lowercase form expected by reconstruct_possessions."""
    if len(pbp) == 0:
        return pbp.copy()
    p = pbp.copy().reset_index(drop=True)

    at_orig = p["action_type"].fillna("").astype(str).values
    st_orig = p["sub_type"].astype(object).where(p["sub_type"].notna(), None).values
    sv = p["shot_value"].values
    sr_orig = p["shot_result"].astype(object).where(p["shot_result"].notna(), None).values
    desc = p["description"].astype(object).where(p["description"].notna(), "").values if "description" in p.columns else np.array([""] * len(p), dtype=object)

    at_new = np.empty(len(p), dtype=object)
    st_new = np.empty(len(p), dtype=object)
    sr_new = np.empty(len(p), dtype=object)

    action_map = {
        "Rebound": "rebound",
        "Free Throw": "freethrow",
        "Foul": "foul",
        "Turnover": "turnover",
        "Substitution": "substitution",
        "Timeout": "timeout",
        "Jump Ball": "jumpball",
        "Heave": "heave",
        "Ejection": "ejection",
        "Instant Replay": "instantreplay",
        "Violation": "violation",
    }

    # First pass: action_type and shot_result. For stats_api Free Throws,
    # shot_result is NULL in the raw data and the made/missed info lives in
    # the description ("MISS X Free Throw..." vs "X Free Throw ... (N PTS)").
    # Infer when shot_result is missing.
    for i in range(len(p)):
        at = at_orig[i]
        if at in ("Made Shot", "Missed Shot"):
            at_new[i] = "3pt" if sv[i] == 3 else "2pt"
            sr_new[i] = "Made" if at == "Made Shot" else "Missed"
        elif at in action_map:
            at_new[i] = action_map[at]
            sr = sr_orig[i]
            if sr is None and at_new[i] == "freethrow":
                d = desc[i]
                if isinstance(d, str) and d.startswith("MISS"):
                    sr_new[i] = "Missed"
                elif isinstance(d, str) and "Free Throw" in d:
                    sr_new[i] = "Made"
                else:
                    sr_new[i] = sr
            else:
                sr_new[i] = sr
        else:
            at_new[i] = at
            sr_new[i] = sr_orig[i]

    # Second pass: sub_type normalization (Free Throw prefix strip, casing)
    for i in range(len(p)):
        sub = st_orig[i]
        a = at_new[i]
        if not isinstance(sub, str):
            st_new[i] = sub
            continue
        if a == "freethrow":
            if sub.startswith("Free Throw "):
                rest = sub[len("Free Throw "):]
                m = _SUBTYPE_FT_RE.search(rest)
                if m:
                    st_new[i] = f"{m.group(1)} of {m.group(2)}"
                else:
                    st_new[i] = rest.lower()
            else:
                st_new[i] = sub.lower()
        elif a == "rebound":
            sl = sub.lower()
            if sl in ("offensive", "defensive"):
                st_new[i] = sl
            else:
                st_new[i] = "unknown"
        else:
            st_new[i] = sub.lower()

    # Third pass: infer rebound offensive/defensive from preceding shot context
    last_shot_team: int | None = None
    for i in range(len(p)):
        a = at_new[i]
        if a in ("2pt", "3pt"):
            t = p["team_id"].iloc[i]
            if pd.notna(t):
                last_shot_team = int(t)
        elif a == "rebound" and st_new[i] == "unknown":
            t = p["team_id"].iloc[i]
            if last_shot_team is not None and pd.notna(t):
                t = int(t)
                st_new[i] = "offensive" if t == last_shot_team else "defensive"
            else:
                st_new[i] = "defensive"

    p["action_type"] = at_new
    p["sub_type"] = st_new
    p["shot_result"] = sr_new
    return p


# --------------------------------------------------------------------------
# Clock parsing
# --------------------------------------------------------------------------

_CLOCK_RE = re.compile(r"PT(\d+)M([\d.]+)S")


def parse_clock_to_seconds(clock: str | None) -> float:
    """Return seconds remaining in the current period, or NaN if unparseable.

    Input format from NBA PBP is ISO 8601 duration, e.g. 'PT11M22.00S' meaning
    11 minutes 22 seconds left.
    """
    if clock is None or not isinstance(clock, str):
        return float("nan")
    m = _CLOCK_RE.match(clock)
    if not m:
        return float("nan")
    minutes = int(m.group(1))
    seconds = float(m.group(2))
    return minutes * 60.0 + seconds


# --------------------------------------------------------------------------
# Possession reconstruction
# --------------------------------------------------------------------------

# action_types that end the offense's possession (when their outcome holds).
# Free-throws handled separately because only the last in a trip ends it.

_POSS_ENDING_TYPES = {
    "2pt",       # if made, ends possession; if missed, depends on rebound
    "3pt",       # same
    "turnover",  # always ends possession
}


@dataclass
class _PossState:
    """In-progress possession being built up while walking actions."""

    possession_id: int
    period: int
    offense_team_id: int | None
    start_action_number: int
    start_clock_seconds: float
    start_score_diff: int                 # offense_score - defense_score at start
    points: int = 0
    fga: int = 0
    fg3a: int = 0
    fgm: int = 0
    fg3m: int = 0
    fta: int = 0
    ftm: int = 0
    ended_by: str = ""


def _infer_offense_team_from_action(row: pd.Series, team_a: int, team_b: int) -> int | None:
    """Best-guess offense team from an action row when we don't know it yet."""
    if pd.notna(row.team_id) and row.team_id in (team_a, team_b):
        return int(row.team_id)
    return None


def reconstruct_possessions(pbp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Walk PBP for ONE game in action_number order and tag each action with a
    possession_id. Returns (actions_with_possession_id, possessions_summary).

    Required pbp columns: game_id, action_number, period, clock, team_id,
        action_type, sub_type, shot_result, shot_value, score_home, score_away.

    The possessions_summary frame has one row per possession with:
        game_id, possession_id, period, offense_team_id,
        start_action_number, end_action_number,
        start_clock_seconds, end_clock_seconds, duration_seconds,
        start_score_diff (offense - defense at start of possession),
        points (points scored on this possession),
        fga, fg3a, fgm, fg3m, fta, ftm,
        ended_by (string label).
    """
    if len(pbp) == 0:
        return pbp.assign(possession_id=pd.Series(dtype="Int64")), pd.DataFrame()

    pbp = pbp.sort_values(["period", "action_number"]).reset_index(drop=True).copy()
    pbp = normalize_pbp(pbp)
    # Determine the two team ids in this game
    team_ids = pbp["team_id"].dropna().astype(int).unique().tolist()
    team_ids = [t for t in team_ids if t != 0]
    if len(team_ids) < 2:
        # Bail; we can't reconstruct
        return pbp.assign(possession_id=pd.Series([pd.NA] * len(pbp), dtype="Int64")), pd.DataFrame()
    # Coerce to two by frequency in case of weirdness
    team_counts = pbp["team_id"].value_counts()
    team_counts = team_counts[team_counts.index.isin(team_ids)].head(2)
    team_a, team_b = sorted(team_counts.index.astype(int).tolist())

    home_score = pbp["score_home"].astype("Int64").fillna(0).astype(int).values
    away_score = pbp["score_away"].astype("Int64").fillna(0).astype(int).values
    # We need to determine which team is home and which is away to attribute scores.
    # The team that ever scores via a made shot when score_home increments is home.
    # Simpler: just track combined score and attribute deltas to whichever team had the action.
    poss_ids = np.full(len(pbp), -1, dtype=int)
    possessions: list[_PossState] = []

    current: _PossState | None = None
    current_offense: int | None = None
    prev_period = None

    def open_possession(idx: int, row: pd.Series, offense: int | None) -> _PossState:
        nonlocal current
        # score diff at possession start: offense - defense
        home = int(row.score_home) if pd.notna(row.score_home) else 0
        away = int(row.score_away) if pd.notna(row.score_away) else 0
        # We don't know which team is home yet; we'll attribute later. Use 0 for now.
        diff = 0
        ps = _PossState(
            possession_id=len(possessions),
            period=int(row.period),
            offense_team_id=offense,
            start_action_number=int(row.action_number),
            start_clock_seconds=parse_clock_to_seconds(row.clock),
            start_score_diff=diff,
            points=0,
            fga=0, fg3a=0, fgm=0, fg3m=0, fta=0, ftm=0,
        )
        return ps

    def close_possession(ps: _PossState, end_idx: int, end_action: int, end_clock: float, ended_by: str) -> None:
        ps.ended_by = ended_by
        # store end info as attrs we'll add to dataclass via dict later
        ps.__dict__["end_action_number"] = int(end_action)
        ps.__dict__["end_clock_seconds"] = end_clock
        possessions.append(ps)

    for i, row in pbp.iterrows():
        period = int(row.period) if pd.notna(row.period) else 0
        action_type = row.action_type
        sub_type = row.sub_type
        shot_result = row.shot_result
        shot_value = row.shot_value

        # New period: close any open possession, start fresh
        if prev_period is not None and period != prev_period and current is not None:
            close_possession(current, i - 1, int(pbp.iloc[i - 1].action_number),
                             parse_clock_to_seconds(pbp.iloc[i - 1].clock), "period_end")
            current = None
            current_offense = None
        prev_period = period

        # Skip non-possession-relevant actions for offense determination
        if action_type in ("period", "substitution", "timeout", "ejection",
                            "stoppage", "instantreplay"):
            if current is not None:
                poss_ids[i] = current.possession_id
            continue

        # Determine offense team for current action
        action_team = None
        if pd.notna(row.team_id) and int(row.team_id) in (team_a, team_b):
            action_team = int(row.team_id)

        # If no open possession, open one keyed to this action's team
        if current is None:
            offense = action_team
            current = open_possession(i, row, offense)
            current_offense = offense

        # Assign action to current possession
        poss_ids[i] = current.possession_id

        # And-1 FT attribution: if this is a free throw and the shooter's team
        # is NOT the current offense but IS the offense of the previous (just
        # closed) possession, credit the FT to the previous possession instead.
        # This handles the case where a made FG closes possession A but the
        # bonus FT from the foul on the FG should still belong to possession A.
        credit_target = current
        retro_target_idx: int | None = None
        if (
            action_type == "freethrow"
            and action_team is not None
            and action_team != current.offense_team_id
            and len(possessions) > 0
            and action_team == possessions[-1].offense_team_id
        ):
            credit_target = possessions[-1]
            retro_target_idx = len(possessions) - 1
            # Re-tag this action to the previous possession id for downstream joins
            poss_ids[i] = credit_target.possession_id

        # Tally points and shot stats for the credit_target
        if action_team is not None and action_team == credit_target.offense_team_id:
            if action_type in ("2pt", "3pt"):
                credit_target.fga += 1
                if action_type == "3pt":
                    credit_target.fg3a += 1
                if shot_result == "Made":
                    credit_target.fgm += 1
                    if action_type == "3pt":
                        credit_target.fg3m += 1
                    credit_target.points += int(shot_value) if pd.notna(shot_value) else (3 if action_type == "3pt" else 2)
            elif action_type == "freethrow":
                credit_target.fta += 1
                if shot_result == "Made":
                    credit_target.ftm += 1
                    # FTs are always 1 point. shot_value is 0 for stats_api FTs
                    # and 1 for cdn FTs; don't trust it.
                    credit_target.points += 1

        # Decide whether this action ends the possession
        end_reason: str | None = None
        next_offense: int | None = None

        if action_type in ("2pt", "3pt") and shot_result == "Made":
            end_reason = "made_fg"
            # Next offense: the other team
            if current.offense_team_id is not None:
                next_offense = team_b if current.offense_team_id == team_a else team_a

        elif action_type == "rebound":
            if sub_type == "defensive":
                end_reason = "defensive_rebound"
                # Whoever made the rebound is now offense
                if action_team is not None:
                    next_offense = action_team
                elif current.offense_team_id is not None:
                    next_offense = team_b if current.offense_team_id == team_a else team_a
            # offensive rebound: possession continues, no end

        elif action_type == "turnover":
            end_reason = f"turnover_{sub_type}" if sub_type else "turnover"
            if current.offense_team_id is not None:
                next_offense = team_b if current.offense_team_id == team_a else team_a

        elif action_type == "freethrow" and retro_target_idx is None:
            # End if this is the last FT of the trip and it was either made or
            # missed without an immediate offensive rebound. We model: last-FT
            # ends the possession; if next action is offensive rebound, we will
            # actually have already classified this as the end. Simplification
            # accepted in v1.
            #
            # Skip when the FT was retro-credited to a previous possession (and-1
            # case): the previous possession already ended on made_fg, and the
            # current possession should continue, so no close fires here.
            is_last = isinstance(sub_type, str) and sub_type.startswith(
                tuple(f"{k} of {k}" for k in range(1, 6))
            )
            if is_last:
                # If the made FT was the last shot of the trip, end the possession.
                # If missed last FT, the next action (rebound) will end it; here
                # we only end on a made last FT.
                if shot_result == "Made":
                    end_reason = "made_last_ft"
                    if current.offense_team_id is not None:
                        next_offense = team_b if current.offense_team_id == team_a else team_a

        if end_reason is not None:
            close_possession(
                current,
                i,
                int(row.action_number),
                parse_clock_to_seconds(row.clock),
                end_reason,
            )
            current = None
            current_offense = next_offense
            # Open the next possession lazily on the next non-trivial action, but
            # we can pre-seed offense via current_offense above.
            if next_offense is not None:
                # Open a placeholder possession that will accumulate from the next action
                current = _PossState(
                    possession_id=len(possessions),
                    period=period,
                    offense_team_id=next_offense,
                    start_action_number=int(row.action_number) + 1,
                    start_clock_seconds=parse_clock_to_seconds(row.clock),
                    start_score_diff=0,
                )

    # Close any trailing possession at end of game
    if current is not None:
        close_possession(
            current,
            len(pbp) - 1,
            int(pbp.iloc[-1].action_number),
            parse_clock_to_seconds(pbp.iloc[-1].clock),
            "game_end",
        )

    pbp_out = pbp.copy()
    pbp_out["possession_id"] = pd.array(poss_ids, dtype="Int64")
    pbp_out.loc[pbp_out["possession_id"] < 0, "possession_id"] = pd.NA

    poss_rows = []
    for p in possessions:
        d = p.__dict__.copy()
        poss_rows.append(d)
    poss_df = pd.DataFrame(poss_rows)
    if len(poss_df):
        poss_df["duration_seconds"] = poss_df["start_clock_seconds"] - poss_df["end_clock_seconds"]
        poss_df["game_id"] = pbp_out["game_id"].iloc[0]
        col_order = [
            "game_id", "possession_id", "period", "offense_team_id",
            "start_action_number", "end_action_number",
            "start_clock_seconds", "end_clock_seconds", "duration_seconds",
            "start_score_diff",
            "points", "fga", "fg3a", "fgm", "fg3m", "fta", "ftm", "ended_by",
        ]
        poss_df = poss_df[col_order]

    return pbp_out, poss_df


# --------------------------------------------------------------------------
# Shot zones
# --------------------------------------------------------------------------

def classify_shot_zone(shot_distance: float | None, x_legacy: float | None,
                       y_legacy: float | None, shot_value: int | None) -> str:
    """Return one of: 'rim', 'midrange', 'corner_three', 'above_break_three', 'unknown'.

    x_legacy and y_legacy are NBA's legacy court coordinates (in tenths of a foot
    from the basket center, basket at (0, 0), positive y towards the offensive
    half).
    """
    if shot_value is not None and not pd.isna(shot_value):
        if int(shot_value) == 3:
            # Decide corner vs above-break by y position. Corner threes have
            # y_legacy near zero (along the baseline). Threshold: |y| <= 92
            # (legacy units, where the corner three line meets the arc).
            if x_legacy is not None and not pd.isna(x_legacy) and y_legacy is not None and not pd.isna(y_legacy):
                if abs(y_legacy) <= 92:
                    return "corner_three"
            return "above_break_three"
    if shot_distance is not None and not pd.isna(shot_distance):
        d = float(shot_distance)
        if d <= 4:
            return "rim"
        elif d < 22:
            return "midrange"
    if shot_value is not None and not pd.isna(shot_value) and int(shot_value) == 2:
        return "midrange"
    return "unknown"


# --------------------------------------------------------------------------
# Possession-level filters
# --------------------------------------------------------------------------

def tag_transition(possessions: pd.DataFrame, threshold_seconds: float = 7.0) -> pd.Series:
    """A possession is transition if its first scoring action occurs within
    threshold_seconds of the start of the possession. The "first scoring
    action" is approximated by the possession's duration so far when the shot
    fires; we use possession start clock minus end clock as a proxy and pair
    that with the action's shot-clock context. This v1 simply uses duration
    less-than-threshold AND at least one FGA. Refine when we add shot clock.
    """
    return (possessions["duration_seconds"] <= threshold_seconds) & (possessions["fga"] >= 1)


def tag_clutch(possessions: pd.DataFrame, abs_margin_threshold: int = 5,
               minutes_remaining_threshold: float = 5.0) -> pd.Series:
    """A possession is clutch if it starts in the 4th period or later with the
    absolute score margin at most abs_margin_threshold and at most
    minutes_remaining_threshold minutes left in the period.
    """
    in_clutch_period = possessions["period"] >= 4
    enough_time_left = (possessions["start_clock_seconds"] / 60.0) <= minutes_remaining_threshold
    # margin computation deferred: callers attach start_score_diff
    margin_ok = possessions["start_score_diff"].abs() <= abs_margin_threshold
    return in_clutch_period & enough_time_left & margin_ok


def tag_garbage_time(possessions: pd.DataFrame, margin_threshold: int = 15,
                     minutes_remaining_threshold: float = 3.0) -> pd.Series:
    """A possession is garbage time if it starts in period >= 4 with the
    absolute score margin greater than margin_threshold and at most
    minutes_remaining_threshold minutes left. CLAUDE.md default convention.
    """
    in_late_quarter = possessions["period"] >= 4
    little_time_left = (possessions["start_clock_seconds"] / 60.0) <= minutes_remaining_threshold
    blowout = possessions["start_score_diff"].abs() > margin_threshold
    return in_late_quarter & little_time_left & blowout
