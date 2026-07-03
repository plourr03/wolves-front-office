# FORKED from postmortem/lib/lineups.py at AM-1 pinned blob 23587a1d0a0a (repo commit 1e56b4c4,
# 2026-07-02) for G1 hardening. The pinned original remains the comparison
# baseline and is NEVER edited by fitengine; every behavioral change here is
# quantified against it by the reconciliation harness. Attribution: original
# implementation by the postmortem/LAFI project.
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

**Known v1 possession-accounting caveat:** AND-1 free throws and other
free-throw sequences that follow a made FG can be attributed to the wrong
possession's offensive team in this v1. The total points per game match the
box score exactly; the per-team attribution can be off by 3-5 points in a
typical game. The lineup-level work that consumes possessions should be
robust to this (per-lineup stats over many possessions will average out the
per-game noise). v2 will refine FT attribution with explicit shooting-foul
sequence tracking. This caveat is documented in the validation output for
each game processed.

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

import unicodedata
from typing import Iterable

import numpy as np
import pandas as pd

from src.adapters.postmortem_lib import query as _adapter_query


class _DB:  # fork shim: db access through the AM-1 fence
    query = staticmethod(_adapter_query)


db = _DB()


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

    # Format detection + normalization. AM-4 note (2026-07-02): format is a
    # PER-GAME property, not a season property -- the 2025-26 warehouse load
    # is mixed (some games legacy Stats-API format, some Live format), so
    # the era stratum must key on this detection, exposed via df.attrs.
    was_legacy = _is_legacy_format(df)
    if was_legacy:
        df = _normalize_legacy_pbp(df)

    # Sort chronologically.
    df = df.sort_values(
        by=["period", "clock_seconds_remaining", "action_number"],
        ascending=[True, False, True],
        kind="stable",
    ).reset_index(drop=True)
    df.attrs["pbp_format"] = "legacy" if was_legacy else "live"
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


class LegacySubResolutionError(ValueError):
    """A legacy substitution's IN player could not be resolved to a
    person_id. Raised instead of guessing: the old fallback (inherit the
    OUTGOING player's id) was a silent identity swap that preserved
    team-seconds and possession parity while corrupting per-player minutes
    and downstream period-start inference. An unresolvable sub means the
    floor state is genuinely unknown -> the game quarantines with a legible
    reason (AM-3 counts it against the gate either way)."""


_GEN_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}

# Retro-renames: the source feed regenerates player_name (and the boxscore
# roster) from the CURRENT player registry, while description strings keep
# the name as called at the time. Token-level alias applied at lookup.
# (Enes Kanter -> Enes Kanter Freedom, Nov 2021 — 7 of 22 bench quarantines.)
# Panel-scale additions (2026-07-03, each verified against source data):
#   mcclellan -> mac   Sheldon McClellan -> Sheldon Mac (2016-17 WAS renames;
#                      registry says 'Mac', 25 panel quarantines said
#                      'McClellan'). No other NBA McClellan/Mac.
#   zhou -> qi         Not a rename: Chinese family-name ordering. Sub
#                      descriptions use the family name 'Zhou'; the
#                      registry's surname form is 'Qi' ('Zhou Qi', 2017-18
#                      HOU, 18 panel quarantines). No other NBA Zhou.
#   yongxi -> cui      Cui Yongxi, 2024-25 BKN (2 panel quarantines). Descs
#                      use the given name 'Yongxi'; the registry row is
#                      'Cui Cui' (its own duplication quirk), so the bare
#                      surname key is 'cui'. No other NBA Yongxi/Cui.
_NAME_ALIASES = {"kanter": "freedom", "mcclellan": "mac", "zhou": "qi",
                 "yongxi": "cui"}


def _translit_variant(s: str) -> str:
    """German umlaut transliteration BEFORE diacritic folding: desc 'Pöltl'
    must reach registry form 'Poeltl' (16 panel quarantines, 2024-25 TOR
    legacy-format games). Applied as an ADDITIONAL lookup form, never the
    only one: 'Schröder' still matches registry 'Schroder' via the plain
    NFKD fold, which stays first in the form list."""
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"),
                 ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue")):
        s = s.replace(a, b)
    return s


def _norm_name(s: str) -> str:
    """Fold diacritics to ASCII and normalize for matching. G1 HARDENING
    (fix-order 2, 2026-07-02): PBP player_name stores diacritic spellings
    ('Porziņģis') while sub descriptions use ASCII ('SUB: Porzingis FOR
    Noah'); an exact-string map misses and misresolves."""
    folded = unicodedata.normalize("NFKD", s)
    ascii_s = "".join(c for c in folded if not unicodedata.combining(c))
    # Commas fold like periods: desc 'Jones, Jr.' vs PBP form 'Jones Jr.'
    # (20 panel quarantines, 2016-17 PHX).
    return " ".join(
        ascii_s.replace(".", " ").replace(",", " ").replace("'", "").lower().split())


def _strip_gen_suffix(toks: list[str]) -> list[str]:
    toks = list(toks)
    while len(toks) > 1 and toks[-1] in _GEN_SUFFIXES:
        toks = toks[:-1]
    return toks


def _build_name_to_id_map(df: pd.DataFrame) -> dict:
    """Build TEAM-SCOPED name-resolution state for legacy sub descriptions.

    G1 HARDENING (fix-order 2, 2026-07-02; staged design after the
    208-game bench): the original map was game-global first-wins on exact
    strings — cross-team surname collisions, diacritic mismatches, and
    fallback-to-out-pid identity swaps. Bench round 1 exposed a second
    layer: within a game, PBP name forms are MINIMAL-UNIQUE ('Williams'
    means Grant precisely because Robert is 'Williams III'), so flat
    roster-derived surname keys POISONED already-correct PBP keys with
    false ambiguity. Hence two tiers consulted in order by the resolver:

      pbp:    (team_id, exact normalized player_name form) -> {pids}.
              Never blended with roster keys.
      roster: (team_id, alias form) -> {pids} from the official boxscore
              full names — full name, suffix-stripped variants, bare
              surname, 'smith jr' two-part, 'j johnson' initialed.
      players: [(team_id, pid, roster name tokens)] for the prefix stage
              ('Jal. Williams' -> first name starting 'jal' + surname
              'williams' -> Jalen not Jaylin).
    """
    pbp_map: dict[tuple[int, str], set[int]] = {}
    roster_map: dict[tuple[int, str], set[int]] = {}
    players: list[tuple[int, int, list[str]]] = []
    pbp_forms: dict[int, set[str]] = {}   # pid -> its exact PBP forms
    played: set[int] = set()              # pids with non-null minutes_float

    def _add(m: dict, tid: int, key: str, pid: int) -> None:
        if key:
            m.setdefault((tid, key), set()).add(pid)

    valid = df[
        df["person_id"].notna()
        & (df["person_id"] != 0)
        & df["player_name"].notna()
        & (df["player_name"].astype(str).str.strip() != "")
        & df["team_id"].notna()
        & (df["team_id"] != 0)
    ]
    for _, row in valid.iterrows():
        form = _norm_name(str(row["player_name"]))
        pid = int(row["person_id"])
        _add(pbp_map, int(row["team_id"]), form, pid)
        pbp_forms.setdefault(pid, set()).add(form)

    game_ids = df["game_id"].dropna().unique() if "game_id" in df.columns else []
    if len(game_ids) == 1:
        roster = db.query(
            """
            SELECT player_id, player_name, team_id
            FROM nba_player_stats WHERE game_id = %s
            """,
            (str(game_ids[0]),),
        )
        for _, r in roster.iterrows():
            tid, pid = int(r["team_id"]), int(r["player_id"])
            toks = _norm_name(str(r["player_name"])).split()
            base = _strip_gen_suffix(toks)
            players.append((tid, pid, toks))
            _add(roster_map, tid, " ".join(toks), pid)      # full as printed
            if base != toks:
                _add(roster_map, tid, " ".join(base), pid)  # sans suffix
            _add(roster_map, tid, base[-1], pid)            # bare surname
            if len(toks) >= 2:
                _add(roster_map, tid, " ".join(toks[-2:]), pid)  # 'smith jr'
            if len(base) >= 2:
                _add(roster_map, tid, " ".join(base[-2:]), pid)
                # initialed form ('j johnson') — how legacy descriptions
                # disambiguate same-surname teammates
                _add(roster_map, tid, f"{base[0][0]} {base[-1]}", pid)
            if len(base) >= 3:
                # multi-token surname: desc 'Mbah a Moute' vs roster 'Luc
                # Mbah a Moute' (bare-surname key 'moute' misses; 3 panel
                # quarantines where he has no other PBP events to map)
                _add(roster_map, tid, " ".join(base[1:]), pid)
            if "-" in base[-1]:
                # hyphenated-surname parts: desc 'Hayes' vs retro-renamed
                # roster 'Nigel Hayes-Davis' (2 panel quarantines). A part
                # colliding with a real teammate surname surfaces as
                # AMBIGUOUS via _settle, never a coin flip.
                for part in base[-1].split("-"):
                    _add(roster_map, tid, part, pid)
        # Who actually logged floor time: seconds-precise minutes_float
        # (NULL = DNP). NEVER the integer minutes_played -- a 36-second
        # cameo truncates to 0 and would read as a DNP (rider 2's lesson,
        # reconfirmed on Grant Williams, game 0022000936, 0.60 true
        # minutes vs integer 0). Feeds the played-elimination in
        # _resolve_sub_in.
        adv = db.query(
            """
            SELECT person_id FROM nba_player_advanced_stats
            WHERE game_id = %s AND minutes_float IS NOT NULL
            """,
            (str(game_ids[0]),),
        )
        played = {int(p) for p in adv["person_id"]}
    return {"pbp": pbp_map, "roster": roster_map, "players": players,
            "pbp_forms": pbp_forms, "played": played}


def _resolve_sub_in(state: dict, tid: int, in_name: str, out_pid: int | None) -> int:
    """Resolve a legacy sub description's IN name to a person_id, or raise
    LegacySubResolutionError. Stages, most-trustworthy first:

      1-2. PBP exact-form map, then with generational suffix stripped
           (desc 'Martin Jr.' vs retro-renamed PBP form 'Martin').
      3-4. Roster map, same two forms.
      5.   Prefix match against roster full names ('jal'+'williams').

    At every stage a multi-pid hit tries OUT-pid elimination (the player
    entering cannot be the one leaving on the same event: 'SUB: Williams
    FOR Williams III' -> plain Williams is not Robert). Residual ambiguity
    RAISES — never a coin flip, never the out-pid fallback.
    """
    def _alias_key(raw_norm: str) -> str:
        return " ".join(_NAME_ALIASES.get(t, t) for t in raw_norm.split())

    key = _alias_key(_norm_name(in_name))
    toks = key.split()
    stripped = " ".join(_strip_gen_suffix(toks))
    forms = [key] + ([stripped] if stripped != key else [])
    # German transliteration variants (Pöltl -> poeltl), tried AFTER the
    # plain folds so Schröder-style names keep hitting their plain form
    key_de = _alias_key(_norm_name(_translit_variant(in_name)))
    if key_de != key:
        stripped_de = " ".join(_strip_gen_suffix(key_de.split()))
        forms += [key_de] + ([stripped_de] if stripped_de != key_de else [])

    def _eliminate(cands: set[int], lookup_form: str) -> set[int]:
        """Evidence-based elimination for roster/prefix hits, each pass
        reverted if it would empty the candidate set:
        (1) minimal-uniqueness: a candidate whose exact PBP forms in THIS
            game exist and do NOT include the lookup form is called
            something else by the feed ('Williams III' is never plain
            'Williams' within a game);
        (2) the entering player logged floor time: candidates absent from
            the seconds-precise minutes_float column (true DNPs) cannot be
            the one subbing in."""
        forms_of = state.get("pbp_forms", {})
        kept = {p for p in cands
                if not forms_of.get(p) or lookup_form in forms_of[p]}
        if kept:
            cands = kept
        played = state.get("played", set())
        if played:
            kept = {p for p in cands if p in played}
            if kept:
                cands = kept
        return cands

    def _settle(cands: set[int], stage: str,
                lookup_form: str | None = None) -> int | None:
        # UNCONDITIONAL out-pid elimination (panel find, game 0022300106):
        # 'SUB: Williams Jr. FOR Williams' -- the suffix-stripped lookup
        # 'williams' hits the OUT player's own PBP form as a SINGLE
        # candidate, and a len>1 guard would return the leaving player as
        # the enterer (a self-sub identity swap). The entering player can
        # never be the leaving player, at any candidate count.
        if out_pid is not None:
            cands = cands - {out_pid}
        if len(cands) > 1 and stage in ("roster", "prefix") and lookup_form:
            cands = _eliminate(cands, lookup_form)
        if len(cands) == 1:
            return next(iter(cands))
        if len(cands) > 1:
            raise LegacySubResolutionError(
                f"legacy sub IN player AMBIGUOUS at {stage}: {in_name!r} "
                f"(team_id={tid}, candidates={sorted(cands)})")
        return None

    for map_name in ("pbp", "roster"):
        for form in forms:
            hit = state[map_name].get((tid, form))
            if hit:
                got = _settle(set(hit), map_name, lookup_form=form)
                if got is not None:
                    return got

    stoks = stripped.split()
    if len(stoks) >= 2:
        prefix, surname = "".join(stoks[:-1]), stoks[-1]
        cands = {
            pid for (t, pid, ptoks) in state["players"]
            if t == tid
            and _strip_gen_suffix(ptoks)[-1] == surname
            and ptoks[0].startswith(prefix)
        }
        got = _settle(cands, "prefix", lookup_form=stripped)
        if got is not None:
            return got

    # Final fallback: leading-token surname. Some desc forms carry MORE of
    # the legal name than any registry form ('Louzada Silva' vs PBP form
    # 'Louzada' / roster 'Didi Louzada', 1 panel game). Tried dead last,
    # team-scoped, eliminations on, ambiguity still raises; the length
    # guard keeps initialed forms ('w johnson') away from it.
    if len(stoks) >= 2 and len(stoks[0]) >= 3:
        lead = stoks[0]
        for map_name in ("pbp", "roster"):
            hit = state[map_name].get((tid, lead))
            if hit:
                got = _settle(set(hit), "roster", lookup_form=lead)
                if got is not None:
                    return got

    raise LegacySubResolutionError(
        f"legacy sub IN player unresolved: {in_name!r} "
        f"(team_id={tid}, key={key!r})")


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
    if " FOR " in rest:
        in_part, _, _out_part = rest.partition(" FOR ")
        return in_part.strip()
    if rest.endswith(" FOR"):
        # Truncated feed description ('SUB: Jones FOR', 3 events in game
        # 0021500624): the OUT name is missing from the TEXT, but the OUT
        # player was never parsed from it anyway — the event's person_id
        # carries the OUT pid (verified on all 3 events). The IN name is
        # intact, so resolution proceeds normally.
        return rest[: -len(" FOR")].strip() or None
    return None


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
            # Synthesize IN. G1 HARDENING (fix-order 2, 2026-07-02):
            # staged team-scoped resolution (see _resolve_sub_in); NEVER
            # fall back to the OUT player's id (silent identity swap) —
            # unresolved raises and the game quarantines legibly.
            in_name = _parse_in_player_name_from_sub(description)
            tid = int(row["team_id"]) if pd.notna(row.get("team_id")) else None
            if not in_name or tid is None:
                raise LegacySubResolutionError(
                    f"legacy sub unparseable: {description!r} (team_id={tid})")
            out_pid = int(row["person_id"]) if pd.notna(row.get("person_id")) else None
            in_pid = _resolve_sub_in(name_to_id, tid, in_name, out_pid)
            in_row = row.copy()
            in_row["action_type"] = "substitution"
            in_row["sub_type"] = "in"
            in_row["person_id"] = in_pid
            in_row["player_name"] = in_name
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

    G1 HARDENING (2026-07-02): the OFFICIAL boxscore is the primary source.
    nba_player_advanced_stats.position is non-null for exactly the five
    starters per team (verified 10/10 in all 15,669 panel games). The PBP
    inference below survives only as a fallback for games absent from that
    table. Its old defensive fallback ("top 5 by P1 appearance count")
    silently seated active bench players over quiet starters and broke
    count ties by unstable sort order -- game 0022500001 seated Jaylin
    Williams over the actual starter Cason Wallace on a 5-vs-5 tie whose
    winner flipped with an unrelated upstream fix.
    """
    official = db.query(
        """
        SELECT person_id, team_id FROM nba_player_advanced_stats
        WHERE game_id = %s AND position IS NOT NULL AND position <> ''
        """,
        (game_id,),
    )
    if len(official) == 10:
        by_team = {
            int(tid): sorted(int(p) for p in g["person_id"])
            for tid, g in official.groupby("team_id")
        }
        if len(by_team) == 2 and all(len(v) == 5 for v in by_team.values()):
            return by_team

    # FALLBACK: PBP inference (original fork logic).
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
            # G1 HARDENING (2026-07-02): deterministic tie-break (count desc,
            # person_id asc). The unstable default sort resolved count ties
            # by array-content accident, so unrelated fixes flipped starters.
            counts = (team_pbp[team_pbp["period"] == 1]
                      .groupby("person_id").size())
            counts = counts[counts.index.notna() & (counts.index != 0)]
            ranked = counts.reset_index()
            ranked.columns = ["person_id", "n"]
            ranked = ranked.sort_values(
                ["n", "person_id"], ascending=[False, True], kind="stable")
            team_starters = list(ranked.head(5)["person_id"].astype(int))

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
                elif (row["sub_type"] == "out"
                      and pid not in first_sub_in[tid]
                      and pid not in seen_non_sub[tid]):
                    # G1 HARDENING (fix-order 1, 2026-07-02): a player whose
                    # FIRST sub event this period is an OUT, with no prior
                    # sub-in and no prior non-sub appearance, was necessarily
                    # on the floor at period start. Without this evidence a
                    # quiet starter (plays minutes, registers no event, subs
                    # out) is invisible and gets padded from prior-period
                    # state -- the dominant baseline failure mode.
                    seen_non_sub[tid].add(pid)
                    per_team_start_players[tid].append(pid)
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
                    # ultimate fallback. G1 HARDENING (negative evidence,
                    # 2026-07-02): a player whose FIRST event this period is
                    # a sub-IN provably did NOT start the period -- exclude
                    # from padding (padding wrong players cascades through
                    # the running end-of-period state into every later
                    # period; the 20-30 min baseline residuals).
                    # banned = subbed IN this period with no prior non-sub
                    # appearance (candidates holds exactly the players whose
                    # evidence PRECEDES any sub-in, so the complement within
                    # first_sub_in is the provably-benched set)
                    banned = set(first_sub_in[tid]) - set(candidates)
                    pool = list(candidates)
                    for p_ in prior_floor[tid]:
                        if p_ not in pool and p_ not in banned:
                            pool.append(p_)
                    for p_ in starters[tid]:
                        if p_ not in pool and p_ not in banned:
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
                    "end_reason": "end_of_period",
                    "offensive_floor": row[floor_col[current_off_team]],
                    "defensive_floor": row[floor_col[[t for t in team_ids if t != current_off_team][0]]],
                })
            current_off_team = None
            current_start_action = None
            current_period = period
            current_points = 0
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
            current_points = 0
            poss_num += 1

        # Score tracking.
        if atype in ("2pt", "3pt") and row["shot_result"] == "Made":
            current_points += int(row.get("shot_value") or (3 if atype == "3pt" else 2))
        if atype == "freethrow" and row["shot_result"] == "Made":
            current_points += 1

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
            # NaN is truthy, so `or ""` alone does not guard it: team-rebound
            # rows in a handful of legacy games carry sub_type the normalizer
            # nulls ('Normal Rebound'/'Unknown'), and NaN.lower() raised
            # AttributeError (3 panel quarantines). Unknown FT ordinal ->
            # not-last, same as any unparseable sub_type.
            sub = row["sub_type"]
            sub = sub.lower() if isinstance(sub, str) else ""
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
        "pbp_format": pbp.attrs.get("pbp_format", "unknown"),
        "starters": starters,
        "annotated": annotated,
        "validation": validation,
        "possessions": possessions,
    }
