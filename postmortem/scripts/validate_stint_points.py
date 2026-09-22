#!/usr/bin/env python3
"""D88: prove that stint points reconcile to the box score, and measure what they were.

`lib/lineup_aggregation.py` used to credit a possession's points to whichever stint
contained the possession's lookup timestamp. Points from a possession that spanned a
substitution, and and-1 free throws shot after the clock stopped, landed in the wrong
stint. The library now rebuilds points from made-shot events and keeps the old figures
as `points_*_possession_basis`, so both bases can be measured on the same stints.

  G1  on the MADE-SHOT basis, stint points equal the box score for every team-game.
  G2  on the POSSESSION basis they do not, and the error is mirrored between the two
      teams of a game, which is the and-1 signature.

Box score truth is `nba_games.pts`, one row per team-game, which is independent of the
play-by-play pipeline.

    python postmortem/scripts/validate_stint_points.py [--games N]
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from lib import db, lineup_aggregation as LA  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, ".."))
from kuminga.lib import runlog  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "tables", "validation", "stint_points_reconciliation.csv")
OUT_CACHE = os.path.join(ROOT, "outputs", "tables", "validation", "stint_points_reconciliation_cache.csv")
CACHES = [os.path.join(ROOT, "outputs", "cache", "q2_localize", d)
          for d in ("wolves_2023_stints", "wolves_2024_stints", "wolves_2025_stints")]


def sample_games(n_per_season: int) -> pd.DataFrame:
    """Wolves games across the seasons the pipeline covers, both season types."""
    return db.query(
        """
        with g as (
          select game_id, season_id, season_type, game_date,
                 row_number() over (partition by season_id order by game_date) rn
          from nba.nba_games
          where team_id = 1610612750 and season_id in (22023, 42023, 22024, 42024, 22025, 42025)
        )
        select game_id, season_id, season_type from g
        where rn <= %s order by season_id, game_id
        """,
        (n_per_season,),
    )


def box_points(game_ids: list[str]) -> pd.DataFrame:
    """Box score truth: one row per team-game from `nba_games`, independent of the
    play-by-play pipeline."""
    return db.query(
        """
        select game_id, team_id, pts::int box_points
        from nba.nba_games
        where game_id = any(%s)
        """,
        (list(game_ids),),
    )


def main():
    with runlog.run('validate_stint_points', inputs={"box_score": "nba_games.pts"}) as r:
        _main(r)


def _main(r):
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=6, help="games per season and season type")
    ap.add_argument("--from-cache", action="store_true",
                    help="measure the pre-fix error on the frozen stint caches (D92): a fresh "
                         "build no longer shows it, because both grains are fixed")
    args = ap.parse_args()
    if args.from_cache:
        return from_cache(r)

    games = sample_games(args.games)
    print(f"sample: {len(games)} games")
    for (sid, st), grp in games.groupby(["season_id", "season_type"]):
        print(f"  {sid} {st}: {len(grp)} games")

    stints = LA.process_games_to_stints(games.game_id.tolist())
    if stints.empty:
        raise SystemExit("no stints built; is the warehouse reachable?")
    have = sorted(stints.game_id.unique())
    print(f"stints built for {len(have)} of {len(games)} games ({len(stints)} stints)")

    box = box_points(have)
    agg = stints.groupby(["game_id", "team_id"], as_index=False).agg(
        made_shot_basis=("points_for", "sum"),
        possession_basis=("points_for_possession_basis", "sum"),
        possessions_off=("possessions_off", "sum"))
    m = agg.merge(box, on=["game_id", "team_id"], how="inner")
    m["err_made_shot"] = m.made_shot_basis - m.box_points
    m["err_possession"] = m.possession_basis - m.box_points
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    m.to_csv(OUT, index=False)

    print()
    print("PER TEAM-GAME ERROR AGAINST THE BOX SCORE (points)")
    for col, label in (("err_made_shot", "made-shot basis (now)"),
                       ("err_possession", "possession basis (before)")):
        e = m[col]
        print("  %-26s mean %+6.3f | mean abs %5.3f | sd %5.3f | max abs %5.1f | exact %d/%d"
              % (label, e.mean(), e.abs().mean(), e.std(), e.abs().max(),
                 int((e == 0).sum()), len(e)))

    # G2: the possession-basis error is mirrored within a game
    pair = m.groupby("game_id").err_possession.agg(["sum", "count"])
    pair = pair[pair["count"] == 2]
    print("  possession-basis error summed over both teams of a game: mean %+.3f, max abs %.1f "
          "(mirrored means this is ~0 while each team is off)"
          % (pair["sum"].mean(), pair["sum"].abs().max()))

    rate = 100 * m.err_possession.abs().sum() / m.box_points.sum()
    print("  possession-basis absolute error as a share of all points: %.2f%%" % rate)
    r.note("misplaced share, lineup grain, possession basis: %.2f%% of all points on %d team-games; "
           "made-shot basis exact on %d of %d" % (rate, len(m), int((m.err_made_shot == 0).sum()), len(m)))
    r.output(OUT, rows=len(m))

    print()
    bad = m[m.err_made_shot != 0]
    if len(bad):
        print("G1 FAILED: %d team-games do not reconcile on the made-shot basis" % len(bad))
        print(bad.head(10).to_string(index=False))
        raise SystemExit(1)
    print("G1 PASSED: stint points equal the box score for all %d team-games" % len(m))
    if np.isclose(m.err_possession.abs().sum(), 0):
        print("G2 NOTE: the possession basis also reconciles on this sample, so the defect "
              "does not show here")
    else:
        print("G2 PASSED: the possession basis does not reconcile (that is the defect)")
    print("wrote %s" % os.path.relpath(OUT, ROOT))


def from_cache(r):
    """The cached stints carry the OLD `points_for` (possession basis, credited to the
    tracked offence on the old possession grain) and the made-shot event columns. Sum both
    per team-game and compare to the box score."""
    import glob
    frames = []
    for d in CACHES:
        for f in glob.glob(os.path.join(d, "*.parquet")):
            frames.append(pd.read_parquet(f))
    st = pd.concat(frames, ignore_index=True)
    st["made_shot"] = 2 * st.fgm_off + st.fg3m_off + st.ftm_off
    agg = st.groupby(["game_id", "team_id"], as_index=False).agg(
        possession_basis=("points_for", "sum"), made_shot_basis=("made_shot", "sum"))
    box = box_points(sorted(agg.game_id.unique()))
    m = agg.merge(box, on=["game_id", "team_id"], how="inner")
    m["err_possession"] = m.possession_basis - m.box_points
    m["err_made_shot"] = m.made_shot_basis - m.box_points
    m.to_csv(OUT_CACHE, index=False)
    share = 100 * m.err_possession.abs().sum() / m.box_points.sum()
    exact = int((m.err_made_shot == 0).sum())
    pair = m.groupby("game_id").err_possession.sum()
    print("frozen caches: %d stints, %d team-games from %d games" % (len(st), len(m), m.game_id.nunique()))
    print("  old possession basis: mean abs error %.3f, largest %d, share of all points %.2f%%"
          % (m.err_possession.abs().mean(), int(m.err_possession.abs().max()), share))
    print("  made-shot basis from the same caches: exact on %d of %d" % (exact, len(m)))
    print("  error summed over both teams of a game: max abs %d" % int(pair.abs().max()))
    r.note("misplaced share, lineup grain, OLD possession basis on the frozen caches: %.2f%% of all "
           "points on %d team-games; made-shot basis exact on %d of %d" % (share, len(m), exact, len(m)))
    r.output(OUT_CACHE, rows=len(m))
    if exact != len(m):
        raise SystemExit("made-shot basis is not exact on the caches")


if __name__ == "__main__":
    main()
