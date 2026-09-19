"""Lineup-level possession pipeline.

Foundational infrastructure for Q2, Q6, Q8, and downstream lineup-grain analyses.

PBP format support: the pipeline handles BOTH the modern NBA Live PBP format
(used in the 2025-26 season) and the legacy NBA Stats API format (used in
2024-25 and earlier). `load_pbp()` detects the format and applies
`_normalize_legacy_pbp()` to map legacy action_type values to modern ones.
Synthesized two-event substitutions (legacy has one event per sub with the
OUT player as person_id; the IN player is parsed from the description and
resolved via an in-file name->id map) bring legacy data up to the modern
pipeline contract.

Between-period substitution handling: NBA PBP does not record substitutions
that happen between periods. The pipeline reconstructs each period's
starting floor by identifying players who appeared in non-sub events
BEFORE their first sub-in event in that period. See
`_identify_period_start_floors()`.

This module is intentionally scoped to the foundational pieces:

1. `derive_starters(game_id)` -- identify the 5 starters per team from PBP.
2. `derive_floor_state_per_event(game_id)` -- annotate every PBP event with the
   5-player lineup on the floor for each team at the moment of the event.
3. `validate_floor_state(annotated_df)` -- sanity check that there are always
   exactly 5 players per team on the floor.
4. `derive_possessions(annotated_df)` -- identify possession boundaries from
   PBP events and associate each possession with the offensive lineup.

Validation expectations:
- Most games (modern + legacy) pass with 0 actor-not-on-floor events.
- A small fraction of games (~10% in sampled tests) have 1-30 actor-not-on-
  floor events, typically when the starter-detection or period-boundary
  reconstruction misclassifies edge cases (e.g., a player who appears in a
  steal event before their first explicit non-sub touch). For aggregate
  lineup-level analysis these are noise (<5% of all events); for clean per-
  game lineup attribution, sampled games with high error counts should be
  inspected individually.

Per-lineup aggregation (computing per-lineup possessions, points, ratings)
builds on these foundations and lives in a follow-on module. This module
focuses on getting the floor state and possession boundaries correct.

Possession definition for v1: a possession ends on a made field goal (with
all subsequent free throws on the same trip absorbed), on a defensive
rebound, on a turnover, or on end of period. An offensive rebound continues
the same possession. This matches the NBA.com convention closely.

**FIXED 2026-09-19 (D89), was a v1 caveat:** and-one free throws and other
free-throw sequences following a made field goal were attributed to the wrong
possession's offensive team. Game totals matched the box score, per-TEAM
totals were off by 3 to 5 points a game, mirrored between the two teams, and
the old note called that noise the consumers could average out. It was not
noise: the points were credited to the other team, so anything fitted on
possession points (RAPM above all) inherited a systematic error.

Points are now credited to the team that scored them. The scorer is the
offense for the open possession in the ordinary case; when he is not, the
points go to that team's most recent possession, and anything still homeless
is held for that team's next possession. Per-team possession points now
reconcile to `nba_games.pts` exactly (`scripts/validate_possession_points.py`).
`points_scored_legacy` keeps the old rule's value for diagnosis, and is
approximate because the old rule also let an and-one free throw close the
wrong possession.

Starter derivation logic:

  For each team in the game, a player is a starter if:
  (a) their first substitution event in the game is sub_type='out'
      (they were on the floor when subbed out, so they had to be starting), OR
  (b) they appear in non-substitution events during period 1 but never get
      subbed (they played without coming off, which is only possible if they
      started).

  This is robust to starters who do not touch the ball early.

Floor state walk:

  Initialize floor state with the 5 starters for each team.
  Iterate through PBP events in action_number order.
  When a substitution event is encountered, swap the players involved.
  Every other event inherits the current floor state.
  After period boundaries, the floor state carries forward (NBA convention).

All functions take `game_id` (or a pre-loaded PBP DataFrame) and return
pandas DataFrames. Connection to the warehouse is via `lib.db`.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from lib import db


# ---------------------------------------------------------------------------
# Loading raw PBP for a game
# ---------------------------------------------------------------------------


_PBP_SQL = """
SELECT
    game_id,
    action_number,
    action_id,
    period,
    clock,
    team_id,
    team_tricode,
    person_id,
    player_name,
    description,
    action_type,
    sub_type,
    shot_result,
    points_total,
    score_home,
    score_away
FROM nba_play_by_play
WHERE game_id = %s
ORDER BY action_number
"""


def _parse_clock_to_seconds(clock_str: str) -> float:
    """Parse an ISO-8601 duration like 'PT07M20.00S' to seconds remaining in period."""
    if not isinstance(clock_str, str) or not clock_str.startswith("PT"):
        return float("nan")
    try:
        s = clock_str[2:]
        minutes = 0
        seconds = 0.0
        if "M" in s:
            m_part, _, rest = s.partition("M")
            minutes = int(m_part)
            s = rest
        if "S" in s:
            sec_part = s.replace("S", "")
            seconds = float(sec_part) if sec_part else 0.0
        return minutes * 60 + seconds
    except Exception:
        return float("nan")


def load_pbp(game_id: str) -> pd.DataFrame:
    """Load PBP for a single game.

    Returns rows ordered chronologically by (period ascending, clock seconds
    descending, action_number ascending). NBA PBP action_number is insertion
    order, not always game order; some stat corrections get inserted later
    with higher action_numbers but represent earlier game moments. Sorting by
    period + clock gives true chronological order, with action_number as the
    tie-breaker for events at the same clock time.

    Format normalization: if the PBP is in the legacy NBA Stats API format
    (action_type values like 'Made Shot', 'Rebound', etc.), it is normalized
    in-place to the modern Live PBP format ('2pt'/'3pt', 'rebound', etc.)
    so the downstream pipeline can parse seasons before 2025-26.
    """
    df = db.query(_PBP_SQL, (game_id,))
    for c in ("action_number", "period", "team_id", "person_id", "points_total"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    df["clock_seconds_remaining"] = df["clock"].apply(_parse_clock_to_seconds)

    # Format detection + normalization.
    if _is_legacy_format(df):
        df = _normalize_legacy_pbp(df)

    # Sort chronologically.
    df = df.sort_values(
        by=["period", "clock_seconds_remaining", "action_number"],
        ascending=[True, False, True],
        kind="stable",
    ).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Legacy PBP format normalization
# ---------------------------------------------------------------------------


_LEGACY_ACTION_MARKERS = {"Made Shot", "Missed Shot", "Rebound", "Free Throw",
                          "Substitution", "Turnover", "Foul", "Jump Ball"}


def _is_legacy_format(df: pd.DataFrame) -> bool:
    """Detect the legacy NBA Stats API PBP format by checking action_type
    values. Modern Live PBP uses lowercase short tokens ('2pt', 'rebound',
    'substitution'); legacy uses CamelCase descriptive labels ('Made Shot',
    'Missed Shot', 'Rebound', 'Substitution').
    """
    if df.empty or "action_type" not in df.columns:
        return False
    types = set(df["action_type"].dropna().unique())
    return bool(types & _LEGACY_ACTION_MARKERS)


def _build_name_to_id_map(df: pd.DataFrame) -> dict[str, int]:
    """Build a mapping from PBP-style player name (as stored in the
    player_name column, typically just the last name or last+suffix) to
    person_id, drawing on non-sub events where both fields are populated.
    """
    out: dict[str, int] = {}
    valid = df[
        df["person_id"].notna()
        & (df["person_id"] != 0)
        & df["player_name"].notna()
        & (df["player_name"].astype(str).str.strip() != "")
    ]
    for _, row in valid.iterrows():
        name = str(row["player_name"]).strip()
        pid = int(row["person_id"])
        if name and name not in out:
            out[name] = pid
    return out


def _parse_in_player_name_from_sub(description: str) -> str | None:
    """Parse the IN player name from a legacy substitution description.

    Format: 'SUB: <IN_NAME> FOR <OUT_NAME>'. The IN name can contain spaces
    (e.g., 'Williams III'). Returns None if the pattern is not found.
    """
    if not isinstance(description, str):
        return None
    if not description.startswith("SUB:"):
        return None
    rest = description[len("SUB:"):].strip()
    if " FOR " not in rest:
        return None
    in_part, _, _out_part = rest.partition(" FOR ")
    return in_part.strip()


def _parse_ft_sub_type(legacy_sub_type: str) -> str | None:
    """Parse legacy free throw sub_type ('Free Throw 1 of 2') into modern
    sub_type ('1 of 2'). Returns None if not parseable.
    """
    if not isinstance(legacy_sub_type, str):
        return None
    s = legacy_sub_type.strip()
    if s.startswith("Free Throw "):
        return s[len("Free Throw "):].strip()
    return None


def _is_three_pointer(description: str) -> bool:
    return isinstance(description, str) and "3PT" in description


def _is_offensive_rebound(description: str) -> bool:
    """Legacy rebound description is 'X REBOUND (Off:M Def:N)'. The team's
    season totals at this point are appended; offensive vs defensive is
    encoded by whether the description mentions a personal rebound count
    that maps to the off vs def count. Simpler heuristic: rebounds where
    the player who rebounded is on the same team as the shooter (we don't
    know the shooter inline). Instead use the convention that the legacy
    sub_type is uniformly 'Unknown' and we infer from neighboring events.

    Refined approach: legacy rebounds can be classified by looking at the
    immediately preceding shot event. If the shot is by the same team as
    the rebounder, it's offensive; otherwise defensive. This requires the
    rebound row to be processed in context, not in isolation.

    For per-row normalization we leave sub_type as None here and let the
    contextual pass (`_classify_legacy_rebounds`) fill it in.
    """
    return False  # placeholder; context-dependent


def _classify_legacy_rebounds(df: pd.DataFrame) -> pd.Series:
    """Walk the legacy PBP and classify each Rebound row as 'offensive' or
    'defensive' based on the most recent prior shot event's team.

    Returns a Series aligned with df.index of 'offensive' | 'defensive' |
    None for non-rebound rows.
    """
    out = [None] * len(df)
    last_shot_team = None
    df_sorted = df.sort_values(
        by=["period", "clock_seconds_remaining", "action_number"],
        ascending=[True, False, True],
        kind="stable",
    ).reset_index()
    for new_idx, row in df_sorted.iterrows():
        atype = row.get("action_type")
        if atype in ("Made Shot", "Missed Shot", "Free Throw"):
            if pd.notna(row.get("team_id")) and row["team_id"] != 0:
                last_shot_team = int(row["team_id"])
        elif atype == "Rebound":
            rebound_team = (int(row["team_id"]) if pd.notna(row.get("team_id"))
                             and row["team_id"] != 0 else None)
            if rebound_team is not None and last_shot_team is not None:
                if rebound_team == last_shot_team:
                    out[row["index"]] = "offensive"
                else:
                    out[row["index"]] = "defensive"
    return pd.Series(out, index=df.index)


def _normalize_legacy_pbp(df: pd.DataFrame) -> pd.DataFrame:
    """Convert a legacy-format PBP DataFrame to modern format.

    For each legacy row, emit one or two modern rows:
      - Most rows: one modern row with mapped action_type / sub_type /
        shot_result.
      - Substitution rows: two modern rows (one 'out', one 'in') because
        the modern pipeline expects two substitution events per swap. The
        IN player is parsed from the description and resolved to person_id
        via the in-file name→id map.

    The action_number is preserved for the OUT half of a substitution; the
    synthesized IN half gets action_number + 0.5 so it sorts immediately
    after the OUT and before subsequent events.
    """
    name_to_id = _build_name_to_id_map(df)
    rebound_class = _classify_legacy_rebounds(df)

    out_rows = []
    for idx, row in df.iterrows():
        atype = row.get("action_type")
        new_atype = atype
        new_sub_type = row.get("sub_type")
        new_shot_result = row.get("shot_result")
        description = row.get("description") or ""

        if atype in ("Made Shot", "Missed Shot"):
            new_atype = "3pt" if _is_three_pointer(description) else "2pt"
            new_shot_result = "Made" if atype == "Made Shot" else "Missed"
            new_sub_type = "Jump Shot"  # generic placeholder; downstream doesn't depend on it
        elif atype == "Free Throw":
            new_atype = "freethrow"
            parsed = _parse_ft_sub_type(new_sub_type)
            if parsed:
                new_sub_type = parsed
            # The legacy description encodes made/missed via the prefix
            # ('MISS Player Free Throw 1 of 2' vs 'Player Free Throw 1 of 2 (1 PTS)').
            if isinstance(description, str) and description.lstrip().startswith("MISS"):
                new_shot_result = "Missed"
            else:
                new_shot_result = "Made"
        elif atype == "Rebound":
            new_atype = "rebound"
            cls = rebound_class.get(idx)
            new_sub_type = cls if cls else "defensive"
        elif atype == "Turnover":
            new_atype = "turnover"
            # legacy sub_type already descriptive (Bad Pass, Lost Ball, etc.)
        elif atype == "Foul":
            new_atype = "foul"
            new_sub_type = (new_sub_type or "").lower() if isinstance(new_sub_type, str) else new_sub_type
        elif atype == "Timeout":
            new_atype = "timeout"
        elif atype == "Jump Ball":
            new_atype = "jumpball"
        elif atype == "Substitution":
            # Emit OUT first.
            out_row = row.copy()
            out_row["action_type"] = "substitution"
            out_row["sub_type"] = "out"
            out_rows.append(out_row)
            # Synthesize IN.
            in_name = _parse_in_player_name_from_sub(description)
            in_pid = name_to_id.get(in_name) if in_name else None
            in_row = row.copy()
            in_row["action_type"] = "substitution"
            in_row["sub_type"] = "in"
            in_row["person_id"] = in_pid if in_pid is not None else row.get("person_id")
            in_row["player_name"] = in_name if in_name else row.get("player_name")
            # action_number+0.5 to preserve chronological order
            try:
                orig = float(row.get("action_number"))
                in_row["action_number"] = orig + 0.5
            except (TypeError, ValueError):
                pass
            out_rows.append(in_row)
            continue
        elif atype == "Ejection":
            new_atype = "ejection"
        elif atype == "Instant Replay":
            new_atype = "replay"
        elif atype == "Violation":
            new_atype = "violation"
        # action_type == 'period' and others fall through unchanged.

        nr = row.copy()
        nr["action_type"] = new_atype
        nr["sub_type"] = new_sub_type
        nr["shot_result"] = new_shot_result
        out_rows.append(nr)

    out = pd.DataFrame(out_rows).reset_index(drop=True)
    # action_number may have fractional .5 values now; that's fine because
    # downstream sorts by (period, clock_seconds_remaining, action_number)
    # and the .5 only matters for tiebreaking within the same clock instant.
    return out


def _team_ids_for_game(pbp: pd.DataFrame) -> list[int]:
    """Return the two team_ids in the game (excluding zero/null)."""
    teams = sorted(set(t for t in pbp["team_id"].dropna().unique() if t and t != 0))
    return list(teams)


# ---------------------------------------------------------------------------
# Starter derivation
# ---------------------------------------------------------------------------


def derive_starters(game_id: str, pbp: pd.DataFrame | None = None) -> dict[int, list[int]]:
    """Return {team_id: [5 player_ids]} of the starters for each team.

    Algorithm:
      For each team, iterate substitution events in chronological order.
      The first time a player is involved in a sub, look at the sub_type:
        - 'out' means they were on the floor before this sub: starter (or
          previously subbed in, but we walk chronologically so we know it's
          their first sub).
        - 'in' means they were not on the floor before this sub: not starter.
      Players who never appear in a sub event but do appear in another
      action (e.g., shoot) during period 1: starters.
      Players who never appear at all: not on the active roster for this game.
    """
    if pbp is None:
        pbp = load_pbp(game_id)
    team_ids = _team_ids_for_game(pbp)
    starters: dict[int, list[int]] = {tid: [] for tid in team_ids}

    for tid in team_ids:
        team_pbp = pbp[pbp["team_id"] == tid].copy()
        team_starters: list[int] = []

        # Walk substitution events in order; classify each player by their
        # FIRST sub event (with the action_number it occurred at).
        first_sub_per_player: dict[int, tuple[str, float]] = {}
        for _, row in team_pbp[team_pbp["action_type"] == "substitution"].iterrows():
            pid = int(row["person_id"])
            if pid not in first_sub_per_player:
                an = float(row["action_number"]) if pd.notna(row["action_number"]) else float("inf")
                first_sub_per_player[pid] = (row["sub_type"], an)

        # First pass: a player whose first sub is 'out' was a starter.
        for pid, (first_sub, _an) in first_sub_per_player.items():
            if first_sub == "out":
                team_starters.append(pid)

        # Second pass: a player whose first sub is 'in' but who has non-sub
        # events BEFORE that sub was on the floor without being subbed --
        # i.e., a starter who played a long stretch without a substitution.
        # (Common for high-minute stars in low-foul-trouble games.)
        for pid, (first_sub, first_sub_an) in first_sub_per_player.items():
            if first_sub == "in" and pid not in team_starters:
                earlier = team_pbp[
                    (team_pbp["person_id"] == pid)
                    & (team_pbp["action_type"] != "substitution")
                    & (team_pbp["action_number"] < first_sub_an)
                ]
                if len(earlier) > 0:
                    team_starters.append(pid)

        # Third pass: players who never appear in any sub event but have
        # period 1 non-sub events. They started and played the whole game.
        p1_actors = team_pbp[
            (team_pbp["period"] == 1)
            & (team_pbp["action_type"] != "substitution")
            & (team_pbp["person_id"].notna())
            & (team_pbp["person_id"] != 0)
        ]["person_id"].dropna().astype(int).unique()

        for pid in p1_actors:
            if pid not in first_sub_per_player and pid not in team_starters:
                team_starters.append(pid)

        # Expect exactly 5 starters. If more or fewer, fall back defensively.
        if len(team_starters) != 5:
            # Defensive: pick the 5 with the most appearances in period 1.
            counts = (team_pbp[team_pbp["period"] == 1]
                      .groupby("person_id").size().sort_values(ascending=False))
            counts = counts[counts.index.notna() & (counts.index != 0)]
            team_starters = list(counts.head(5).index.astype(int))

        starters[tid] = sorted(team_starters)

    return starters


# ---------------------------------------------------------------------------
# Floor state derivation
# ---------------------------------------------------------------------------


def derive_floor_state_per_event(
    game_id: str, pbp: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Return the PBP DataFrame with two new columns added:
      - team{tid}_floor: a frozenset of 5 player_ids for that team at the
        moment of the event (one column per team in the game).

    The floor state walks through PBP in action_number order. Substitution
    events update the floor state; all other events inherit it.

    Between-period adjustment: NBA PBP does NOT record substitutions that
    happen between periods (e.g., a team brings out a fresh lineup at the
    start of Q2 without recording subs at clock=720). For each period > 1
    we re-anchor the floor by identifying the first 5 distinct players to
    appear per team in that period's non-sub events. The pre-pass
    `_identify_period_start_floors` returns this state for each period.
    """
    if pbp is None:
        pbp = load_pbp(game_id)
    starters = derive_starters(game_id, pbp=pbp)
    team_ids = list(starters.keys())

    period_floor_starts = _identify_period_start_floors(pbp, team_ids, starters)

    # Current floor state, mutable during the walk.
    floor: dict[int, set[int]] = {tid: set(period_floor_starts[1].get(tid, starters[tid])) for tid in team_ids}
    current_period = 1

    cols = {f"team{tid}_floor": [] for tid in team_ids}

    for _, row in pbp.iterrows():
        new_period = row.get("period")
        if pd.notna(new_period):
            np_int = int(new_period)
            if np_int != current_period and np_int in period_floor_starts:
                # Re-anchor the floor at the period boundary.
                for tid in team_ids:
                    floor[tid] = set(period_floor_starts[np_int].get(tid, set()))
                current_period = np_int

        if row["action_type"] == "substitution":
            tid = int(row["team_id"]) if pd.notna(row["team_id"]) else None
            pid = int(row["person_id"]) if pd.notna(row["person_id"]) else None
            if tid is not None and pid is not None and tid in floor:
                if row["sub_type"] == "out":
                    floor[tid].discard(pid)
                elif row["sub_type"] == "in":
                    floor[tid].add(pid)
        for tid in team_ids:
            cols[f"team{tid}_floor"].append(frozenset(floor[tid]))

    out = pbp.copy()
    for k, v in cols.items():
        out[k] = v
    return out


def _identify_period_start_floors(
    pbp: pd.DataFrame, team_ids: list[int], starters: dict[int, list[int]]
) -> dict[int, dict[int, set[int]]]:
    """For each period in the game, identify the set of 5 players per team
    who were on the floor at the period's start.

    Algorithm:
      - Period 1: floor = starters.
      - Period N>1: walk events in chronological order within the period.
        Apply sub events to a running state initialized with the previous
        period's end state. Track each player's first appearance in a
        non-sub event of the period. After all events are seen, fill any
        gaps in the floor by adding the first 5 distinct actors per team
        (those who appeared in non-sub events) and removing anyone in the
        starting state who never appeared.

    Returns: dict mapping period -> {team_id: set(5 player_ids)}.
    """
    result: dict[int, dict[int, set[int]]] = {}
    result[1] = {tid: set(starters[tid]) for tid in team_ids}

    periods = sorted(p for p in pbp["period"].dropna().unique() if int(p) > 0)

    # Track end-of-period floor as we go (used as the prior-period seed).
    prior_floor: dict[int, set[int]] = {tid: set(starters[tid]) for tid in team_ids}

    for p in periods:
        p_int = int(p)
        period_events = pbp[pbp["period"] == p].copy()

        # Per-team: identify players who appeared in a non-sub event BEFORE
        # their first sub-in event of this period. Those are start-of-period
        # floor players.
        per_team_start_players: dict[int, list[int]] = {tid: [] for tid in team_ids}
        seen_non_sub: dict[int, set[int]] = {tid: set() for tid in team_ids}
        first_sub_in: dict[int, dict[int, int]] = {tid: {} for tid in team_ids}
        for _, row in period_events.iterrows():
            atype = row["action_type"]
            if pd.isna(row.get("team_id")) or row["team_id"] == 0:
                continue
            if pd.isna(row.get("person_id")) or row["person_id"] == 0:
                continue
            tid = int(row["team_id"])
            pid = int(row["person_id"])
            if tid not in seen_non_sub:
                continue
            if atype == "substitution":
                if row["sub_type"] == "in" and pid not in first_sub_in[tid]:
                    first_sub_in[tid][pid] = 1
                    # If this player hasn't appeared in a non-sub event yet,
                    # they came off the bench and are not a start-of-period
                    # floor player. If they appeared in a non-sub event
                    # earlier, they're already in per_team_start_players.
            else:
                if pid not in seen_non_sub[tid]:
                    seen_non_sub[tid].add(pid)
                    # If they have not been subbed in this period yet, they
                    # were on the floor at period start.
                    if pid not in first_sub_in[tid]:
                        per_team_start_players[tid].append(pid)

        if p_int > 1:
            start_floor: dict[int, set[int]] = {}
            for tid in team_ids:
                candidates = per_team_start_players[tid]
                if len(candidates) >= 5:
                    start_floor[tid] = set(candidates[:5])
                else:
                    # Pad with prior-period end state, then with starters as
                    # ultimate fallback.
                    pool = list(candidates)
                    for p_ in prior_floor[tid]:
                        if p_ not in pool:
                            pool.append(p_)
                    for p_ in starters[tid]:
                        if p_ not in pool:
                            pool.append(p_)
                    start_floor[tid] = set(pool[:5])
            result[p_int] = start_floor
        else:
            result[p_int] = {tid: set(starters[tid]) for tid in team_ids}

        # Walk the period's events to update prior_floor for the next period.
        running = {tid: set(result[p_int][tid]) for tid in team_ids}
        for _, row in period_events.iterrows():
            if row["action_type"] != "substitution":
                continue
            tid = int(row["team_id"]) if pd.notna(row["team_id"]) else None
            pid = int(row["person_id"]) if pd.notna(row["person_id"]) else None
            if tid is None or pid is None or tid not in running:
                continue
            if row["sub_type"] == "out":
                running[tid].discard(pid)
            elif row["sub_type"] == "in":
                running[tid].add(pid)
        prior_floor = running

    return result


def validate_floor_state(annotated: pd.DataFrame) -> dict:
    """Sanity check the floor state.

    The floor-size check is applied only to NON-substitution events. During a
    multi-sub sequence at the same clock time (e.g., five subs at a timeout),
    the intermediate states between SUB out and SUB in have less than 5
    players, which is expected and not a bug. The check is on the resolved
    state at the moment of every non-sub event.

    Returns a dict with:
      - is_valid: bool overall pass/fail (both checks pass)
      - bad_event_count_per_team: {team_id: count of non-sub events where the
        floor state did not have exactly 5 players}
      - first_bad_event_per_team: {team_id: (action_number, floor_size,
        description)} of the first violation
      - actor_not_on_floor_count: number of non-sub events where the acting
        person was not in the floor state (data inconsistency)
      - actor_not_on_floor_examples: first 10 violating events
      - intermediate_sub_states: count of substitution-event rows where floor
        was not size 5. Cosmetic, reported for transparency.
    """
    team_cols = [c for c in annotated.columns if c.startswith("team") and c.endswith("_floor")]
    team_ids = [int(c.replace("team", "").replace("_floor", "")) for c in team_cols]

    bad_count: dict[int, int] = {tid: 0 for tid in team_ids}
    first_bad: dict[int, tuple | None] = {tid: None for tid in team_ids}
    intermediate_count = 0

    non_sub = annotated[annotated["action_type"] != "substitution"]
    sub_rows = annotated[annotated["action_type"] == "substitution"]

    for tid, col in zip(team_ids, team_cols):
        for _, row in non_sub.iterrows():
            fl = row[col]
            if not isinstance(fl, (frozenset, set)) or len(fl) != 5:
                bad_count[tid] += 1
                if first_bad[tid] is None:
                    first_bad[tid] = (
                        int(row["action_number"]) if pd.notna(row["action_number"]) else None,
                        len(fl) if isinstance(fl, (frozenset, set)) else None,
                        row["description"],
                    )

    for _, row in sub_rows.iterrows():
        for col in team_cols:
            fl = row[col]
            if not isinstance(fl, (frozenset, set)) or len(fl) != 5:
                intermediate_count += 1
                break  # one count per row, not per team

    actor_issues = []
    # Skip events that are administrative or paper-only and may involve players
    # not currently on the floor (e.g., ejections after the game ends,
    # double technicals called at the end of a period, heaves with no shooter).
    SKIP_ACTOR_CHECK = ("substitution", "period", "timeout", "game", "jumpball",
                        "ejection", "heave")
    for _, row in annotated.iterrows():
        if row["action_type"] in SKIP_ACTOR_CHECK:
            continue
        # Technical fouls can be called after the action has moved on; skip these
        # in the actor check (they are real but not always tied to floor state).
        if row["action_type"] == "foul" and row["sub_type"] == "technical":
            continue
        if pd.isna(row["person_id"]) or row["person_id"] == 0 or pd.isna(row["team_id"]):
            continue
        tid = int(row["team_id"])
        pid = int(row["person_id"])
        if tid in team_ids:
            fl = row[f"team{tid}_floor"]
            if isinstance(fl, (frozenset, set)) and pid not in fl:
                actor_issues.append((
                    int(row["action_number"]) if pd.notna(row["action_number"]) else None,
                    pid,
                    row["player_name"],
                    row["action_type"],
                    row["description"],
                ))

    return {
        "is_valid": all(c == 0 for c in bad_count.values()) and len(actor_issues) == 0,
        "bad_event_count_per_team": bad_count,
        "first_bad_event_per_team": first_bad,
        "actor_not_on_floor_count": len(actor_issues),
        "actor_not_on_floor_examples": actor_issues[:10],
        "intermediate_sub_states": intermediate_count,
    }


# ---------------------------------------------------------------------------
# Possession derivation
# ---------------------------------------------------------------------------


def derive_possessions(
    annotated: pd.DataFrame | None = None, game_id: str | None = None
) -> pd.DataFrame:
    """Identify possession boundaries from PBP events.

    Possession ends on:
      - Made field goal (and all free throws on the same trip)
      - Defensive rebound
      - Turnover
      - End of period

    Offensive rebound continues the same possession.

    Returns a DataFrame with one row per possession:
      - possession_number (sequential within the game)
      - period
      - offensive_team_id
      - defensive_team_id
      - start_action_number, end_action_number
      - points_scored (by the offensive team on this possession)
      - points_scored_legacy (what the pre-D89 rule credited; diagnosis only)
      - end_reason (made_fg, def_rebound, turnover, end_of_period)
      - offensive_floor (frozenset of 5 player_ids)
      - defensive_floor (frozenset of 5 player_ids)

    v1 simplification: free throws are not perfectly bucketed if they cross
    action_number gaps unusually. For most plays this is accurate. Edge
    cases (technical fouls, flagrant free throws by a different team) are
    flagged but not perfectly attributed.
    """
    if annotated is None:
        if game_id is None:
            raise ValueError("Pass either annotated DataFrame or game_id")
        annotated = derive_floor_state_per_event(game_id)

    team_cols = [c for c in annotated.columns if c.startswith("team") and c.endswith("_floor")]
    team_ids = [int(c.replace("team", "").replace("_floor", "")) for c in team_cols]
    if len(team_ids) != 2:
        raise ValueError(f"Expected 2 teams, got {team_ids}")
    floor_col = {tid: f"team{tid}_floor" for tid in team_ids}

    possessions = []
    current_off_team = None
    current_start_action = None
    current_period = None
    current_points = 0
    current_points_legacy = 0
    pending_points: dict[int, int] = {}
    poss_num = 0

    for _, row in annotated.iterrows():
        atype = row["action_type"]
        period = int(row["period"]) if pd.notna(row["period"]) else None
        action_num = int(row["action_number"]) if pd.notna(row["action_number"]) else None
        team_id = int(row["team_id"]) if pd.notna(row["team_id"]) and row["team_id"] != 0 else None

        # Period start: identify the offensive team from the next non-period
        # event. For now, mark a possession boundary and reset.
        if atype == "period" and row["sub_type"] == "start":
            if current_off_team is not None:
                # Close the prior possession at the end of the prior period.
                possessions.append({
                    "possession_number": poss_num,
                    "period": current_period,
                    "offensive_team_id": current_off_team,
                    "defensive_team_id": [t for t in team_ids if t != current_off_team][0],
                    "start_action_number": current_start_action,
                    "end_action_number": action_num,
                    "points_scored": current_points,
                    "points_scored_legacy": current_points_legacy,
                    "end_reason": "end_of_period",
                    "offensive_floor": row[floor_col[current_off_team]],
                    "defensive_floor": row[floor_col[[t for t in team_ids if t != current_off_team][0]]],
                })
            current_off_team = None
            current_start_action = None
            current_period = period
            current_points = 0
            current_points_legacy = 0
            continue

        if atype == "period" and row["sub_type"] == "end":
            # Already handled by next 'start' or fall through.
            continue

        if team_id is None or atype in ("substitution", "timeout", "game"):
            continue

        # Initialize first possession of the period.
        if current_off_team is None:
            current_off_team = team_id
            current_start_action = action_num
            current_period = period
            current_points = pending_points.pop(team_id, 0)
            current_points_legacy = 0
            poss_num += 1

        # D89: AND-ONE FREE THROWS BELONG TO THE POSSESSION THAT JUST CLOSED.
        #
        # A made field goal ends the possession, so the bonus free throw arrives when the
        # other team is already on offense. Crediting it to the open possession gave the
        # point to the WRONG TEAM, which is why possession points missed the box score by
        # about 3.9% with the error mirrored between the two teams. `lib/pbp.py` has always
        # handled this by retro-crediting; this is the same rule.
        #
        # `points_scored_legacy` keeps what the old rule would have credited, for diagnosis.
        # It is an approximation: the old rule also let an and-one free throw close the new
        # possession, so legacy boundaries differ. The measured size of the old error comes
        # from the frozen pre-D89 cache, not from this column.
        # Points are credited to the team that SCORED them. The scorer is on offense for
        # the open possession in the ordinary case; when he is not, the points belong to
        # that team's most recent possession (the and-one, and any tracker slip). Anything
        # that still finds no home is held and credited to that team's next possession, so
        # every point lands on a possession of the team that scored it and the per-team
        # totals reconcile to the box score exactly.
        def credit(team: int, pts: int) -> None:
            nonlocal current_points
            if team == current_off_team:
                current_points += pts
                return
            for prev in reversed(possessions):
                if prev["offensive_team_id"] == team:
                    prev["points_scored"] += pts
                    return
            pending_points[team] = pending_points.get(team, 0) + pts

        scored = 0
        if atype in ("2pt", "3pt") and row["shot_result"] == "Made":
            scored = int(row.get("shot_value") or (3 if atype == "3pt" else 2))
        elif atype == "freethrow" and row["shot_result"] == "Made":
            scored = 1
        if scored:
            current_points_legacy += scored
            credit(int(team_id), scored)

        # An and-one free throw must not close the possession that is now open: the one it
        # belongs to already closed on the made field goal (D89, as `lib/pbp.py` does).
        if (atype == "freethrow" and possessions and team_id is not None
                and team_id != current_off_team
                and team_id == possessions[-1]["offensive_team_id"]):
            continue

        # End-of-possession events.
        def_team = [t for t in team_ids if t != current_off_team][0] if current_off_team else None
        ended = False
        end_reason = None

        if atype in ("2pt", "3pt") and row["shot_result"] == "Made":
            ended = True
            end_reason = "made_fg"
        elif atype == "turnover":
            ended = True
            end_reason = "turnover"
        elif atype == "rebound":
            # Defensive rebound switches possession.
            if team_id != current_off_team:
                ended = True
                end_reason = "def_rebound"
        elif atype == "freethrow":
            # The last free throw of a trip ends the possession (if made) or
            # results in a rebound (if missed, the next rebound event handles
            # the possession transition). The sub_type encodes which FT of
            # how many (e.g., "2 of 2", "1 of 1"). We end the possession on
            # the last made FT of the trip; missed last FTs fall through to
            # the rebound logic.
            sub = (row["sub_type"] or "").lower()
            # Parse "X of Y" pattern.
            is_last = False
            if " of " in sub:
                try:
                    parts = sub.split(" of ")
                    cur = int(parts[0].strip())
                    total = int(parts[1].strip())
                    is_last = (cur == total)
                except (ValueError, IndexError):
                    is_last = False
            if is_last and row["shot_result"] == "Made":
                ended = True
                end_reason = "made_ft"

        if ended and current_off_team is not None:
            possessions.append({
                "possession_number": poss_num,
                "period": current_period,
                "offensive_team_id": current_off_team,
                "defensive_team_id": def_team,
                "start_action_number": current_start_action,
                "end_action_number": action_num,
                "points_scored": current_points,
                "points_scored_legacy": current_points_legacy,
                "end_reason": end_reason,
                "offensive_floor": row[floor_col[current_off_team]],
                "defensive_floor": row[floor_col[def_team]] if def_team else None,
            })
            # Switch possession (the other team is now on offense).
            current_off_team = def_team if end_reason in ("made_fg", "turnover", "def_rebound") else None
            # Made FG: ball goes to the other team after inbound.
            # Turnover: usually goes to the team that didn't turn it over.
            # Def rebound: rebounding team is now on offense.
            if end_reason == "def_rebound":
                current_off_team = team_id  # the rebounding team
            current_start_action = action_num + 1 if action_num is not None else None
            current_points = 0
            current_points_legacy = 0
            poss_num += 1

    return pd.DataFrame(possessions)


# ---------------------------------------------------------------------------
# Driver / convenience
# ---------------------------------------------------------------------------


def process_game(game_id: str) -> dict:
    """End-to-end processing for one game. Returns a dict with:
      - pbp: raw PBP DataFrame
      - starters: dict of team_id -> [5 player_ids]
      - annotated: PBP with floor-state columns
      - validation: dict from validate_floor_state
      - possessions: per-possession DataFrame
    """
    pbp = load_pbp(game_id)
    starters = derive_starters(game_id, pbp=pbp)
    annotated = derive_floor_state_per_event(game_id, pbp=pbp)
    validation = validate_floor_state(annotated)
    possessions = derive_possessions(annotated=annotated)
    return {
        "pbp": pbp,
        "starters": starters,
        "annotated": annotated,
        "validation": validation,
        "possessions": possessions,
    }
