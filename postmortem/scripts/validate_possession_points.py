#!/usr/bin/env python3
"""D89: prove possession points reconcile to the box score, per team-game.

The same test the stint fix had to pass (`validate_stint_points.py`), one grain up.
`lib/lineups.derive_possessions` credited a possession's points to whichever team the
tracker had on offense, so and-one free throws landed on the other team. Points are now
credited to the team that scored them.

  G1  on the corrected basis, possession points equal the box score for EVERY sampled
      team-game. Any miss fails the run.
  G2  on the legacy basis they do not, and the error is mirrored between the two teams
      of a game, which is the and-one signature.

Box score truth is `nba_games.pts`, one row per team-game, independent of play-by-play.

    python postmortem/scripts/validate_possession_points.py [--games N] [--seasons ...]
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

from lib import db, lineups  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "tables", "validation", "possession_points_reconciliation.csv")
SEASONS = [22023, 42023, 22024, 42024, 22025, 42025]


def sample_games(n_per_season: int, seasons: list[int]) -> pd.DataFrame:
    """A spread of games, league-wide, not only Minnesota's."""
    return db.query(
        """
        with g as (
          select distinct game_id, season_id, season_type, game_date from nba.nba_games
          where season_id = any(%s)
        ), r as (
          select *, row_number() over (partition by season_id order by md5(game_id)) rn from g
        )
        select game_id, season_id, season_type from r where rn <= %s
        order by season_id, game_id
        """,
        (seasons, n_per_season),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=8, help="games per season")
    ap.add_argument("--seasons", type=int, nargs="*", default=SEASONS)
    args = ap.parse_args()

    games = sample_games(args.games, args.seasons)
    print("sample: %d games across %d seasons" % (len(games), games.season_id.nunique()))

    rows, failed = [], []
    for i, g in enumerate(games.itertuples(), 1):
        try:
            poss = lineups.process_game(g.game_id)["possessions"]
        except Exception as e:  # a game with no PBP, or a pipeline error
            failed.append((g.game_id, str(e)[:80]))
            continue
        if poss.empty:
            failed.append((g.game_id, "no possessions"))
            continue
        s = poss.groupby("offensive_team_id")[["points_scored", "points_scored_legacy"]].sum()
        box = db.query("select team_id, pts from nba.nba_games where game_id = %s",
                       (g.game_id,)).set_index("team_id")
        for tid, x in s.iterrows():
            if tid not in box.index:
                continue
            rows.append(dict(game_id=g.game_id, season_id=g.season_id, season_type=g.season_type,
                             team_id=int(tid), box_points=int(box.loc[tid, "pts"]),
                             corrected=int(x.points_scored), legacy=int(x.points_scored_legacy),
                             err_corrected=int(x.points_scored - box.loc[tid, "pts"]),
                             err_legacy=int(x.points_scored_legacy - box.loc[tid, "pts"]),
                             possessions=int((poss.offensive_team_id == tid).sum())))
        if i % 10 == 0:
            print("  %d/%d games" % (i, len(games)), flush=True)

    m = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    m.to_csv(OUT, index=False)
    print("\n%d team-games from %d games (%d games unusable)"
          % (len(m), m.game_id.nunique(), len(failed)))
    for gid, why in failed[:5]:
        print("  unusable: %s (%s)" % (gid, why))

    print("\nPER TEAM-GAME ERROR AGAINST THE BOX SCORE (points)")
    for col, label in (("err_corrected", "corrected (now)"), ("err_legacy", "legacy (before)")):
        e = m[col]
        print("  %-20s mean %+6.3f | mean abs %5.3f | sd %5.3f | max abs %4d | exact %d/%d"
              % (label, e.mean(), e.abs().mean(), e.std(), e.abs().max(),
                 int((e == 0).sum()), len(e)))
    pair = m.groupby("game_id").err_legacy.agg(["sum", "count"])
    pair = pair[pair["count"] == 2]
    print("  legacy error summed over both teams of a game: mean %+.3f, max abs %d"
          % (pair["sum"].mean(), pair["sum"].abs().max()))
    print("  legacy absolute error as a share of all points: %.2f%%"
          % (100 * m.err_legacy.abs().sum() / m.box_points.sum()))
    print("\nBY SEASON (corrected exact / team-games, legacy mean abs)")
    for sid, grp in m.groupby("season_id"):
        print("  %s  %3d/%3d exact   legacy %.2f"
              % (sid, int((grp.err_corrected == 0).sum()), len(grp), grp.err_legacy.abs().mean()))

    bad = m[m.err_corrected != 0]
    if len(bad):
        print("\nG1 FAILED: %d team-games do not reconcile" % len(bad))
        print(bad.head(15).to_string(index=False))
        raise SystemExit(1)
    print("\nG1 PASSED: possession points equal the box score for all %d team-games" % len(m))
    if np.isclose(m.err_legacy.abs().sum(), 0):
        print("G2 NOTE: the legacy basis also reconciles on this sample")
    else:
        print("G2 PASSED: the legacy basis does not reconcile (that is the defect)")
    print("wrote %s" % os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
