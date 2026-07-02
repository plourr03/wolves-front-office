"""G1 reconciliation harness — the F1 definition-of-done instrument.

Per game: run the FORKED pipeline (floor_state.process_game +
stint_builder.derive_stints), integrate per-player on-floor seconds from
stint durations, join official boxscore minutes, and score:

  minutes reconciliation   TWO REFERENCES (memo 2026-07-02, supersedes the
                           truncation-only memo of the same date):
                           PRIMARY: nba_player_advanced_stats.minutes_float
                           is SECONDS-PRECISE official minutes (mm:ss from
                           the nba_api advanced boxscore, already ingested;
                           coverage verified complete for all 15,669 panel
                           games). The gate metric is the spec's ORIGINAL
                           criterion |r - o_true| <= 0.5 min, >= 99.5% of
                           player-games. This satisfies rider 1's seconds-
                           precise verification stratum with FULL-PANEL
                           coverage instead of the planned >= 200-game
                           targeted nba_api pulls -- same source data,
                           same criterion, strictly larger sample.
                           SECONDARY: nba_player_stats.minutes_played is an
                           INTEGER FLOOR of true minutes, gated with the
                           truncation-aware relaxed metric
                           |r - (o + 0.5)| <= 1.0. FINAL G1 GREEN REQUIRES
                           BOTH. AM-3: the denominator is ALL player-games
                           -- quarantine never launders the gate. Bench
                           discipline (rider 3): fixes iterate on the
                           208-game bench; gate claims come only from
                           full-panel runs.
  team-seconds identity    sum of player-seconds == 5 * (2880 + 300*nOT)
                           exactly, per team-game (floor-size correctness
                           stated as an assertion).
  possession parity        stint-aggregated possession counts vs the
                           canonical parser's count for the same game,
                           within 0.5% at the season level.
  quarantine rate          games/periods that fail to process, < 0.5%.

AM-4 strata: every metric reports legacy-format and live-format rows
alongside pooled. Format is detected PER GAME (2026-07-02 census: the
2025-26 warehouse load is mixed -- 27,436 legacy-format sub events and
88,302 live-format across the season), so the stratum comes from
process_game's detection, never from the season prefix. (AM-5's backfill
stratum is empty: the 2013-14 gap was a query artifact; retained for
future gap fills.)

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


def truncation_interval(official_min: float) -> tuple[float, float]:
    """Rider 2 (2026-07-02): official minutes are FLOOR-truncated, so the
    only valid consistency bound derived from them is the HALF-OPEN cell
    [m, m+1) in minutes. Repair logic must use this, never m +/- tolerance
    -- otherwise the repair bakes in the exact error the yardstick fix
    removed."""
    return (official_min, official_min + 1.0)


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
    """Both references per the two-reference memo: integer minutes_played
    (nba_player_stats) + seconds-precise minutes_float (advanced boxscore,
    played players only -- DNP rows carry NULL minutes there)."""
    return query("""
        SELECT s.player_id, s.team_id, s.minutes_played, a.minutes_float
        FROM nba_player_stats s
        LEFT JOIN nba_player_advanced_stats a
          ON a.game_id = s.game_id AND a.person_id = s.player_id
        WHERE s.game_id = %s
    """, (game_id,))


def reconcile_game(game_id: str, stints_dir: str | None = None) -> dict:
    """Score one game. Never raises on processing failure: failures come
    back as quarantine records with every player-game counted failed (AM-3).
    With stints_dir set, also writes the per-game stint parquet (the F1
    cache the DuckDB load consumes) — quarantined games write nothing."""
    try:
        result = floor_state.process_game(game_id)
        stints = stint_builder.derive_stints(result["annotated"], result["possessions"])
        if stints_dir is not None:
            stints.to_parquet(Path(stints_dir) / f"{game_id}.parquet", index=False)
        ps = player_seconds_from_stints(stints)
        off = official_minutes(game_id)
        n_periods = int(result["pbp"].period.max())
        expected_team_secs = 5 * (REG_SECONDS + OT_SECONDS * max(0, n_periods - 4))

        m = off.merge(ps, on=["player_id", "team_id"], how="outer")
        m["secs"] = m.secs.fillna(0.0)
        m["official_min"] = m.minutes_played.fillna(0.0).astype(float)
        # PRIMARY: seconds-precise reference, original 0.5-min criterion
        m["official_true"] = m.minutes_float.astype(float).fillna(m.official_min + 0.5)
        m["delta_true"] = (m.secs / 60.0 - m.official_true).abs()
        # SECONDARY: truncation-aware relaxed metric vs integer reference
        m["delta_min"] = (m.secs / 60.0 - (m.official_min + 0.5)).abs()
        team_secs = ps.groupby("team_id").secs.sum()
        team_exact = bool(np.allclose(team_secs.values, expected_team_secs, atol=0.5))

        n_poss_stints = float(stints.possessions_off.sum())
        n_poss_parser = float(len(result["possessions"]))

        return {
            "game_id": game_id, "quarantined": False,
            "pbp_format": result.get("pbp_format", "unknown"),
            "n_player_games": len(m),
            "n_within_half_true": int((m.delta_true <= 0.5).sum()),
            "n_within_tol": int((m.delta_min <= 1.0).sum()),
            "worst_delta_true": float(m.delta_true.max()),
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
                "pbp_format": _format_from_db(game_id),
                "n_player_games": n_pg, "n_within_half_true": 0, "n_within_tol": 0,
                "worst_delta_true": float("nan"), "team_seconds_exact": False,
                "poss_stints": 0.0, "poss_parser": 0.0,
                "n_validation_errors": -1, "error": f"{type(e).__name__}: {e}"}


def _format_from_db(game_id: str) -> str:
    """Format stratum for quarantined games (process_game never returned):
    one cheap probe for a legacy-format sub event."""
    probe = query("""
        SELECT 1 FROM nba_play_by_play
        WHERE game_id = %s AND action_type = 'Substitution' LIMIT 1
    """, (game_id,))
    return "legacy" if len(probe) else "live"


def summarize(scorecard: pd.DataFrame) -> pd.DataFrame:
    """G1 summary, pooled + AM-4 strata. Denominator = ALL player-games."""
    rows = []
    for name, g in [("pooled", scorecard)] + list(scorecard.groupby("stratum")):
        tot_pg = g.n_player_games.sum()
        pp = g.poss_parser.sum()
        rows.append({
            "stratum": name,
            "games": len(g),
            # quarantine is real evidence now (LegacySubResolutionError and
            # kin raise instead of guessing); team-seconds and possession
            # parity remain STRUCTURAL INVARIANTS (directive 2026-07-02
            # item 1) -- tautological while five bodies always exist /
            # lossless partition blind to identity. G1 green claims come
            # from the FULL panel.
            "quarantine_rate": g.quarantined.mean(),
            "recon_rate_TRUE_0p5": g.n_within_half_true.sum() / tot_pg if tot_pg else np.nan,
            "recon_rate_relaxed": g.n_within_tol.sum() / tot_pg if tot_pg else np.nan,
            "team_seconds_exact_INVARIANT": g.team_seconds_exact.mean(),
            "poss_parity_pct_PARTITION": abs(g.poss_stints.sum() - pp) / pp * 100 if pp else np.nan,
            "median_worst_delta_true": g.worst_delta_true.median(),
        })
    return pd.DataFrame(rows)


def run(game_ids: list[str], tag: str) -> pd.DataFrame:
    recs = []
    for i, gid in enumerate(game_ids):
        recs.append(reconcile_game(gid))
        if (i + 1) % 25 == 0:
            print(f"  {i + 1}/{len(game_ids)}", flush=True)
    sc = pd.DataFrame(recs)
    sc["stratum"] = sc.pbp_format  # per-game detection, never season prefix
    out = FITENGINE_ROOT / "outputs" / f"reconciliation_{tag}.parquet"
    sc.to_parquet(out, index=False)
    summ = summarize(sc)
    print(summ.to_string(index=False))
    return sc


def main():
    """208-game bench (rider 3): stratified sample across eras, fixed rng.
    Tag from argv so repair iterations never overwrite the baseline profile
    (reconciliation_baseline.parquet = pre-repair starting point)."""
    tag = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    uni = pd.read_parquet(FITENGINE_ROOT / "data" / "staged" / "game_universe.parquet")
    rs = uni[uni.include_train].sort_values("game_id")
    rng = np.random.default_rng(20260702)
    sample = []
    for yy, g in rs.groupby(rs.game_id.str[3:5]):
        sample.extend(rng.choice(g.game_id, size=min(16, len(g)), replace=False))
    print(f"bench reconciliation [{tag}] on {len(sample)} games "
          f"({len(set(s[3:5] for s in sample))} seasons x ~16)")
    run(sorted(sample), tag)


if __name__ == "__main__":
    main()
