#!/usr/bin/env python3
"""M3 confound check: Minnesota's scorers against primary defenders, four ways.

WHY THIS EXISTS. The M3 cards pool every 2025-26 pairing between one of Minnesota's top
five and a team's heaviest rotation defender on him, judged beyond the league norm for
such a pairing. Anthony Edwards came out at the 1st percentile of 150 top offenders. A
number that striking gets confound-checked before it carries weight. Two confounds are
plausible:

  BASELINE PADDING   an offender's baseline counts every defender he faced, bench and
                     garbage time included. A scorer who feasts on those would look
                     "held" by every real defender. Variant A rebuilds the baseline from
                     rotation defenders only (top 300 by partial possessions).
  PLAYOFF WEIGHT     a long playoff series against one designated stopper (Devin Vassell
                     in the Spurs series) could carry the whole result. Variant B drops
                     the playoffs.

Variant C applies both. Each variant re-derives the noise variance and the norm, and ranks
every top-150 offender with five or more primary pairings of 30+ possessions. The
percentile is the safer figure than the pooled z, because one player's pairings share his
baseline and are not independent; every offender carries that same structure, so the
rank is a like-for-like comparison.

    python kuminga/scripts/m3_primary_defender_check.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from kuminga.lib import runlog  # noqa: E402
from lib import db              # noqa: E402

OUT = os.path.join(REPO, "kuminga", "outputs", "m3_primary_defender_check.csv")
TOP_OFF = 150
ROT_DEF = 300
MIN_POSS = 30.0
MIN_PAIRINGS = 5
BANDS = [30, 60, 120, 100000]
PLAYERS = {1630162: "Anthony Edwards", 203497: "Rudy Gobert", 1630163: "LaMelo Ball",
           1630183: "Jaden McDaniels", 1630245: "Ayo Dosunmu"}


def rank(frame, rot_base):
    dtot = frame.groupby("d").poss.sum()
    rot_def = dtot.sort_values(ascending=False).head(ROT_DEF).index
    bframe = frame[frame.d.isin(rot_def)] if rot_base else frame
    otot = bframe.groupby("o").agg(P=("poss", "sum"), T=("pts", "sum"))
    cells = bframe[bframe.poss > 0].join(otot, on="o")
    var = float(((cells.pts - cells["T"] / cells.P * cells.poss) ** 2).sum()
                / cells.poss.sum())
    pr = frame.groupby(["o", "dteam", "d"]).agg(poss=("poss", "sum"),
                                                pts=("pts", "sum")).reset_index()
    pr = pr.join(otot, on="o")
    pr["dev"] = pr.pts / pr.poss - pr["T"] / pr.P
    top_off = frame.groupby("o").poss.sum().sort_values(ascending=False).head(TOP_OFF).index
    prim = pr[pr.o.isin(top_off) & pr.d.isin(rot_def) & (pr.poss >= MIN_POSS)]
    prim = prim.sort_values("poss", ascending=False).groupby(["o", "dteam"]).head(1)
    prim = prim.assign(band=pd.cut(prim.poss, BANDS, right=False))
    norm = prim.groupby("band", observed=True).dev.mean()
    prim = prim.assign(beyond=prim.dev - prim.band.map(norm).astype(float))
    pool = prim.groupby("o").apply(lambda g: pd.Series(dict(
        pairings=len(g), poss=g.poss.sum(),
        beyond=float(np.average(g.beyond, weights=g.poss)),
        z=float(np.average(g.beyond, weights=g.poss) / np.sqrt(var / g.poss.sum())))),
        include_groups=False)
    pool = pool[pool.pairings >= MIN_PAIRINGS].copy()
    pool["percentile"] = pool.z.rank(pct=True) * 100
    return pool, var, norm


def main():
    with runlog.run("m3_primary_defender_check",
                    inputs={"top_off": TOP_OFF, "rot_def": ROT_DEF, "min_poss": MIN_POSS,
                            "min_pairings": MIN_PAIRINGS}) as r:
        lg = db.query("""
            select game_id g, team_id oteam, person_id_off o, person_id_def d,
                   sum(partial_possessions) poss, sum(player_points) pts
            from nba.nba_boxscore_matchups
            where game_id like '00225%%' or game_id like '00425%%'
            group by 1, 2, 3, 4""")
        for c in ("poss", "pts"):
            lg[c] = pd.to_numeric(lg[c], errors="coerce").fillna(0.0)
        sides = lg[["g", "oteam"]].drop_duplicates()
        sides = sides.merge(sides.rename(columns={"oteam": "dteam"}), on="g")
        sides = sides[sides.oteam != sides.dteam]
        lg = lg.merge(sides, on=["g", "oteam"])
        rs = lg[lg.g.str.startswith("00225")]

        rows = []
        for key, lab, frame, rb in (
                ("shipped", "all-defender baseline, regular season + playoffs", lg, False),
                ("A", "rotation-defender baseline, regular season + playoffs", lg, True),
                ("B", "all-defender baseline, regular season only", rs, False),
                ("C", "rotation-defender baseline, regular season only", rs, True)):
            pool, var, norm = rank(frame, rb)
            r.note("%-8s %s: variance %.3f, norms %s, %d offenders"
                   % (key, lab, var, " ".join("%+.3f" % v for v in norm.values), len(pool)))
            for pid, nm in PLAYERS.items():
                if pid not in pool.index:
                    continue
                x = pool.loc[pid]
                rows.append(dict(variant=key, variant_label=lab, player_id=pid, player=nm,
                                 pairings=int(x.pairings), poss=float(x.poss),
                                 beyond_norm=float(x.beyond), z=float(x.z),
                                 percentile=float(x.percentile), n_offenders=len(pool)))
                r.note("    %-16s pairings %2d  poss %5.0f  beyond %+.3f  z %+.1f  pct %3.0f"
                       % (nm, x.pairings, x.poss, x.beyond, x.z, x.percentile))

        out = pd.DataFrame(rows)
        out.to_csv(OUT, index=False)
        e = out[out.player == "Anthony Edwards"]
        r.note("")
        r.note("EDWARDS: percentile %s across the four variants"
               % ", ".join("%s %.0f" % (v, p) for v, p in zip(e.variant, e.percentile)))
        r.output(OUT, rows=len(out))


if __name__ == "__main__":
    main()
