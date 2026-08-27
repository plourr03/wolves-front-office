#!/usr/bin/env python3
"""S1: the Shapley verdict table before and after the slot constraint.

The slot-aware run allocates minutes within POSITION POOLS, using each team's own
prior-season share of minutes by pool. So removing a guard means another guard plays,
and removing a big means another big plays, rather than the minutes flowing to whoever
the model rates highest.

Bobby's rule: any PLAYER-SPECIFIC verdict that flips loses its QUOTABLE label. The
player-specific moves are ball_in, randle_out, reid_out, dosunmu_retained and
kuminga_in. depth and other_departures are bundles, and ddv_injury is an availability
change rather than a roster move, so they are reported but not subject to the rule.

    python kuminga/scripts/compare_slot_shapley.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

OUTDIR = os.path.join(REPO, "kuminga", "outputs")
FORKS = ["consensus", "rapm", "box", "darko"]
OUT = os.path.join(OUTDIR, "S1_shapley_slot_comparison.csv")

PLAYER_SPECIFIC = {"ball_in": "guard", "randle_out": "frontcourt",
                   "reid_out": "frontcourt", "dosunmu_retained": "guard",
                   "kuminga_in": "forward"}


def main():
    with runlog.run("compare_slot_shapley", inputs={"rule": "player-specific flips "
                                                            "lose QUOTABLE"}) as r:
        un = pd.read_csv(os.path.join(OUTDIR, "shapley_min.csv"), index_col=0)
        po = pd.read_csv(os.path.join(OUTDIR, "shapley_min_POOLED.csv"), index_col=0)

        rows = []
        for mv in sorted(set(un.index) | set(po.index)):
            u = un.loc[mv] if mv in un.index else None
            p = po.loc[mv] if mv in po.index else None
            ps = mv in PLAYER_SPECIFIC
            flipped = (u is not None and p is not None
                       and u.sign_agreement != p.sign_agreement)
            rows.append(dict(
                move=mv, player_specific=ps, pool=PLAYER_SPECIFIC.get(mv, "n/a"),
                verdict_unpooled=u.sign_agreement if u is not None else "n/a",
                verdict_slot_aware=p.sign_agreement if p is not None else "n/a",
                flipped=flipped,
                mean_unpooled=float(u.mean_pp) if u is not None else np.nan,
                mean_slot_aware=float(p.mean_pp) if p is not None else np.nan,
                lo_slot=min(float(p[f]) for f in FORKS) if p is not None else np.nan,
                hi_slot=max(float(p[f]) for f in FORKS) if p is not None else np.nan,
                quotable=(not flipped) and ps and (p is not None)
                         and p.sign_agreement != "MIXED",
            ))
        df = pd.DataFrame(rows).sort_values("mean_slot_aware", ascending=False)
        df.to_csv(OUT, index=False)

        r.note("VERDICTS, unpooled -> slot-aware:")
        for _, x in df.iterrows():
            tag = "  <-- FLIPPED" if x.flipped else ""
            ps = "player-specific" if x.player_specific else "bundle/availability"
            r.note(f"  {x.move:18s} [{ps:19s}] {x.verdict_unpooled:13s} -> "
                   f"{x.verdict_slot_aware:13s} | mean {x.mean_unpooled:+.3f} -> "
                   f"{x.mean_slot_aware:+.3f}{tag}")

        psd = df[df.player_specific]
        flipped = psd[psd.flipped].move.tolist()
        r.note(f"PLAYER-SPECIFIC moves flipped: {flipped if flipped else 'none'}")
        r.note(f"LOSE the QUOTABLE label: {flipped if flipped else 'none'}")
        keep = psd[(~psd.flipped) & (psd.verdict_slot_aware != "MIXED")].move.tolist()
        r.note(f"KEEP a quotable sign: {keep}")

        dos = df[df.move == "dosunmu_retained"].iloc[0]
        r.note(f"DOSUNMU (the one Bobby held back): {dos.verdict_unpooled} -> "
               f"{dos.verdict_slot_aware}, mean {dos.mean_unpooled:+.3f} -> "
               f"{dos.mean_slot_aware:+.3f}, band [{dos.lo_slot:+.3f}, {dos.hi_slot:+.3f}]. "
               f"{'SURVIVES, now quotable.' if not dos.flipped else 'FLIPPED, not quotable.'}")
        r.output(OUT, rows=len(df))

    print()
    print(df[["move", "player_specific", "pool", "verdict_unpooled",
              "verdict_slot_aware", "flipped", "mean_unpooled", "mean_slot_aware",
              "quotable"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
