"""G1 reconciliation harness — the F1 definition-of-done instrument.

Per game: run the FORKED pipeline (floor_state.process_game +
stint_builder.derive_stints), integrate per-player on-floor seconds from
stint durations, join official boxscore minutes, and score:

  minutes reconciliation   TRUNCATION-AWARE (memo 2026-07-02): official
                           minutes_played is an INTEGER FLOOR of true
                           minutes (0 fractional in 786k rows; team sums
                           short by ~0.5/player). A perfect reconstruction
                           satisfies o <= r < o+1, so the gate metric is
                           |r - (o + 0.5)| <= 1.0 (the 0.5 truncation cell
                           half-width + the spec's 0.5 model tolerance),
                           target >= 99.5% of player-games. The naive
                           |r - o| is kept as a diagnostic column. Final G1
                           on the full panel adds a seconds-precise
                           verification stratum via targeted nba_api
                           boxscore pulls. AM-3: the denominator is ALL
                           player-games -- quarantine never launders the
                           gate.
  team-seconds identity    sum of player-seconds == 5 * (2880 + 300*nOT)
                           exactly, per team-game (floor-size correctness
                           stated as an assertion).
  possession parity        stint-aggregated possession counts vs the
                           canonical parser's count for the same game,
                           within 0.5% at the season level.
  quarantine rate          games/periods that fail to process, < 0.5%.

AM-4 strata: every metric reports legacy-format (<= 2024-25) and
live-format (2025-26) rows alongside pooled. (AM-5's backfill stratum is
empty: the 2013-14 gap was a query artifact; retained for future gap fills.)

Output: per-game scorecard parquet + summary dict; the repair loop reads
the failure buckets (minutes-delta histogram, floor-size violations,
validation error details) to pick its next target.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.adapters.postmortem_lib import query  # noqa: E402
from src.stints import floor_state, stint_builder  # noqa: E402

REG_SECONDS = 2880.0
OT_SECONDS = 300.0


def player_seconds_from_stints(stints: pd.DataFrame) -> pd.DataFrame:
    """(player_id, seconds) per team from stint durations x lineup members."""
    import re
    rows = []
    for _, s in stints.iterrows():
        for pid in re.split(r"[,\-]", str(s.lineup_id)):
            rows.append((int(pid), s.team_id, s.duration_sec))
    df = pd.DataFrame(rows, columns=["player_id", "team_id", "secs"])
    return df.groupby(["player_id", "team_id"], as_index=False).secs.sum()


def official_minutes(game_id: str) -> pd.DataFrame:
    return query("""
        SELECT player_id, team_id, minutes_played
        FROM nba_player_stats WHERE game_id = %s
    """, (game_id,))


def reconcile_game(game_id: str) -> dict:
    """Score one game. Never raises on processing failure: failures come
    back as quarantine records with every player-game counted failed (AM-3)."""
    try:
        result = floor_state.process_game(game_id)
        stints = stint_builder.derive_stints(result["annotated"], result["possessions"])
        ps = player_seconds_from_stints(stints)
        off = official_minutes(game_id)
        n_periods = int(result["pbp"].period.max())
        expected_team_secs = 5 * (REG_SECONDS + OT_SECONDS * max(0, n_periods - 4))

        m = off.merge(ps, on=["player_id", "team_id"], how="outer")
        m["secs"] = m.secs.fillna(0.0)
        m["official_min"] = m.minutes_played.fillna(0.0).astype(float)
        # truncation-aware error (see module docstring); naive kept as diag
        m["delta_min"] = (m.secs / 60.0 - (m.official_min + 0.5)).abs()
        m["delta_naive"] = (m.secs / 60.0 - m.official_min).abs()
        team_secs = ps.groupby("team_id").secs.sum()
        team_exact = bool(np.allclose(team_secs.values, expected_team_secs, atol=0.5))

        n_poss_stints = float(stints.possessions_off.sum())
        n_poss_parser = float(len(result["possessions"]))

        return {
            "game_id": game_id, "quarantined": False,
            "n_player_games": len(m),
            "n_within_tol": int((m.delta_min <= 1.0).sum()),
            "n_within_half_naive": int((m.delta_naive <= 0.5).sum()),
            "worst_delta_min": float(m.delta_min.max()),
            "team_seconds_exact": team_exact,
            "poss_stints": n_poss_stints, "poss_parser": n_poss_parser,
            "n_validation_errors": sum(
                v.get("actor_not_on_floor", 0) if isinstance(v, dict) else 0
                for v in result["validation"].values()) if isinstance(
                    result["validation"], dict) else 0,
            "error": None,
        }
    except Exception as e:  # quarantine, never silently drop (AM-3)
        n_pg = len(official_minutes(game_id))
        return {"game_id": game_id, "quarantined": True,
                "n_player_games": n_pg, "n_within_tol": 0, "n_within_half_naive": 0,
                "worst_delta_min": float("nan"), "team_seconds_exact": False,
                "poss_stints": 0.0, "poss_parser": 0.0,
                "n_validation_errors": -1, "error": f"{type(e).__name__}: {e}"}


def format_stratum(game_id: str) -> str:
    return "live_2025_26" if game_id[3:5] == "25" else "legacy_pre_2025"


def summarize(scorecard: pd.DataFrame) -> pd.DataFrame:
    """G1 summary, pooled + AM-4 strata. Denominator = ALL player-games."""
    rows = []
    for name, g in [("pooled", scorecard)] + list(scorecard.groupby("stratum")):
        tot_pg = g.n_player_games.sum()
        ok_pg = g.n_within_tol.sum()
        pp = g.poss_parser.sum()
        rows.append({
            "stratum": name,
            "games": len(g),
            # STRUCTURAL INVARIANTS until repair logic gives them teeth
            # (directive 2026-07-02 item 1): quarantine fires only when a
            # period cannot resolve to 5v5, team-seconds is tautological
            # while five bodies always exist, and possession parity is a
            # lossless-partition check blind to identity errors. Labeled so
            # in every report; G1 green claims come from the FULL panel.
            "quarantine_rate_INVARIANT": g.quarantined.mean(),
            "minutes_recon_rate": ok_pg / tot_pg if tot_pg else np.nan,
            "team_seconds_exact_INVARIANT": g.team_seconds_exact.mean(),
            "poss_parity_pct_PARTITION": abs(g.poss_stints.sum() - pp) / pp * 100 if pp else np.nan,
            "median_worst_delta_min": g.worst_delta_min.median(),
        })
    return pd.DataFrame(rows)


def run(game_ids: list[str], tag: str) -> pd.DataFrame:
    recs = []
    for i, gid in enumerate(game_ids):
        recs.append(reconcile_game(gid))
        if (i + 1) % 25 == 0:
            print(f"  {i + 1}/{len(game_ids)}", flush=True)
    sc = pd.DataFrame(recs)
    sc["stratum"] = sc.game_id.map(format_stratum)
    out = FITENGINE_ROOT / "outputs" / f"reconciliation_{tag}.parquet"
    sc.to_parquet(out, index=False)
    summ = summarize(sc)
    print(summ.to_string(index=False))
    return sc


def main():
    """Baseline error profile: stratified sample across eras, BEFORE any
    hardening -- the quantified starting point the repair loop works from."""
    uni = pd.read_parquet(FITENGINE_ROOT / "data" / "staged" / "game_universe.parquet")
    rs = uni[uni.include_train].sort_values("game_id")
    rng = np.random.default_rng(20260702)
    sample = []
    for yy, g in rs.groupby(rs.game_id.str[3:5]):
        sample.extend(rng.choice(g.game_id, size=min(16, len(g)), replace=False))
    print(f"baseline reconciliation on {len(sample)} games "
          f"({len(set(s[3:5] for s in sample))} seasons x ~16)")
    run(sorted(sample), "baseline")


if __name__ == "__main__":
    main()
