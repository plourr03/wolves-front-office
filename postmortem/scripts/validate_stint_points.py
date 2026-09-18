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

OUT = os.path.join(ROOT, "outputs", "tables", "validation", "stint_points_reconciliation.csv")


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=6, help="games per season and season type")
    args = ap.parse_args()

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


if __name__ == "__main__":
    main()
