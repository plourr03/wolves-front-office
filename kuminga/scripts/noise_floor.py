#!/usr/bin/env python3
"""U2: the noise floor, and which verdicts clear it.

A sign agreement across four views means nothing if all four magnitudes are smaller
than the machinery's own error. This computes that error at Minnesota's odds level and
re-tests every verdict against twice it.

TWO SOURCES OF ERROR, combined in quadrature:

  MONTE CARLO. The f-curve is built from simulated seasons, and `fcurve_min.csv` carries
  `title_sd` at every grid point, which is the across-seed standard deviation of the
  title probability there. Read at Minnesota's own net rating.

  F-CURVE INTERPOLATION. Marginals are priced by linear interpolation on a grid of 0.5
  net-rating points. Linear interpolation of a smooth function has error bounded by
  h^2/8 * max|f''| on the interval, and f'' is estimated by second differences of the
  grid itself.

A marginal contribution is a DIFFERENCE of two interpolations on the same curve, so the
curve's own Monte Carlo error is common to both endpoints and largely cancels for small
differences. This does NOT take that credit: the floor is computed as if the two
evaluations were independent, which is the conservative direction.

    python kuminga/scripts/noise_floor.py [--aged]
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

AGED = "--aged" in sys.argv
SRC = os.path.join(REPO, "kuminga", "outputs") if AGED else \
      os.path.join(REPO, "kuminga", "outputs", "preaging")
OUTDIR = os.path.join(REPO, "kuminga", "outputs")
OUT = os.path.join(OUTDIR, f"noise_floor{'_AGED' if AGED else ''}.csv")
FORKS = ["consensus", "rapm", "box", "darko"]
FLOOR_MULT = 2.0


def main():
    tag = "aged" if AGED else "un-aged primary"
    with runlog.run("noise_floor", inputs={"basis": tag, "mult": FLOOR_MULT}) as r:
        fc = pd.read_csv(os.path.join(SRC, "fcurve_min.csv"))
        st = pd.read_csv(os.path.join(SRC, "team_strengths_2026_27.csv"))
        sh = pd.read_csv(os.path.join(SRC, "shapley_min_POOLED.csv"), index_col=0)

        rows = []
        for f in FORKS:
            g = fc[fc.fork == f].sort_values("min_net").reset_index(drop=True)
            net = float(st[(st.fork == f) & (st.team_abbr == "MIN")].net_current.iloc[0])
            mc = float(np.interp(net, g.min_net, g.title_sd)) * 100      # pp
            h = float(g.min_net.diff().median())
            # second difference -> f'' on the grid, in probability per net^2
            d2 = np.abs(np.diff(g.title.to_numpy(), 2)) / (h ** 2)
            # take f'' near MIN's net rather than the global max
            idx = int(np.clip(np.searchsorted(g.min_net.to_numpy(), net) - 1,
                              0, len(d2) - 1))
            lo, hi = max(0, idx - 2), min(len(d2), idx + 3)
            f2 = float(np.max(d2[lo:hi])) if hi > lo else float(np.max(d2))
            interp = (h ** 2) / 8.0 * f2 * 100                            # pp
            single = float(np.hypot(mc, interp))
            diff_err = single * np.sqrt(2)          # two endpoints, treated independent
            rows.append(dict(fork=f, min_net=net, mc_pp=mc, interp_pp=interp,
                             single_pp=single, diff_pp=diff_err,
                             floor_pp=FLOOR_MULT * diff_err))
            r.note(f"  {f:10s} net {net:+.2f} | MC {mc:.4f}pp | interp {interp:.4f}pp "
                   f"| combined {single:.4f}pp | difference {diff_err:.4f}pp "
                   f"| FLOOR {FLOOR_MULT * diff_err:.4f}pp")
        nf = pd.DataFrame(rows)
        floors = dict(zip(nf.fork, nf.floor_pp))
        worst = float(nf.floor_pp.max())
        r.note(f"MATERIALITY FLOOR (worst fork): {worst:.4f}pp")

        # ---- re-test every verdict ------------------------------------------
        res = []
        for mv, x in sh.iterrows():
            vals = {f: float(x[f]) for f in FORKS}
            agreed = x.sign_agreement != "MIXED"
            clears = {f: abs(v) >= floors[f] for f, v in vals.items()}
            all_clear = all(clears.values())
            res.append(dict(move=mv, sign_agreement=x.sign_agreement,
                            mean_pp=float(x.mean_pp),
                            min_abs_pp=min(abs(v) for v in vals.values()),
                            n_forks_clearing=sum(clears.values()),
                            survives=bool(agreed and all_clear),
                            **{f"clears_{f}": clears[f] for f in FORKS}))
        rr = pd.DataFrame(res).sort_values("mean_pp", ascending=False)
        rr.to_csv(OUT, index=False)

        r.note("")
        r.note("VERDICTS RE-TESTED against the floor (agreed sign AND every view clearing):")
        for _, x in rr.iterrows():
            mark = "SURVIVES" if x.survives else ("fails floor" if x.sign_agreement != "MIXED"
                                                  else "no agreed sign")
            r.note(f"  {x.move:18s} {x.sign_agreement:13s} smallest |view| "
                   f"{x.min_abs_pp:.3f}pp, {int(x.n_forks_clearing)}/4 clear -> {mark}")
        surv = rr[rr.survives].move.tolist()
        lost = rr[(rr.sign_agreement != "MIXED") & (~rr.survives)].move.tolist()
        r.note(f"SURVIVE the floor: {surv if surv else 'none'}")
        r.note(f"HAD an agreed sign but FAIL the floor: {lost if lost else 'none'}")
        r.output(OUT, rows=len(rr))

    print()
    print(nf.round(4).to_string(index=False))
    print()
    print(rr[["move", "sign_agreement", "mean_pp", "min_abs_pp",
              "n_forks_clearing", "survives"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
