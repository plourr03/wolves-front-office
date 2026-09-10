#!/usr/bin/env python3
"""W2: the quotability gate. A verdict ships only if it holds under BOTH aging bases.

TWO BASES, and the difference between them is a modelling choice nobody can settle from
the data alone.

  UN-AGED   every player's 2026-27 impact is his measured 2025-26 impact. Wrong in a
            known direction: it assumes a 34-year-old centre and a 21-year-old wing both
            repeat themselves exactly.
  AGED      each player's impact is shifted by the ONE-YEAR expected change from a
            survivorship-corrected aging curve fitted on the warehouse's own year-over-
            year deltas, with drop-outs re-entered at the 25th percentile of same-age
            observed deltas so the curve is not fitted only on the players good enough
            to keep playing.

Neither is obviously right, so neither is allowed to carry a verdict alone. **A finding
ships only if it has the same sign under both.** Anything that flips is reported as
basis-dependent, which is a real property of the finding and not a failure of the run.

    python kuminga/scripts/w2_aging_gate.py
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
UN = os.path.join(OUTDIR, "preaging")
AG = os.path.join(OUTDIR, "aged")
OUT = os.path.join(OUTDIR, "w2_aging_gate.csv")
FORKS = ["consensus", "rapm", "box", "darko"]


def sign_of(v):
    return ("ALL POSITIVE" if min(v) > 0 else
            "ALL NEGATIVE" if max(v) < 0 else "MIXED")


def read(d, n):
    p = os.path.join(d, n)
    return pd.read_csv(p) if os.path.exists(p) else None


def main():
    with runlog.run("w2_aging_gate", inputs={"unaged": UN, "aged": AG}) as r:
        rows = []

        # ---- pooled Shapley verdicts -----------------------------------------
        for label, fn, idx in (("pooled shapley", "shapley_min_POOLED.csv", 0),):
            a = read(UN, fn)
            b = read(AG, fn)
            if a is None or b is None:
                r.note("MISSING %s in one basis; gate cannot run on it" % fn)
                continue
            a = a.set_index(a.columns[idx])
            b = b.set_index(b.columns[idx])
            for mv in a.index:
                if mv not in b.index:
                    continue
                sa, sb = str(a.loc[mv, "sign_agreement"]), str(b.loc[mv, "sign_agreement"])
                rows.append(dict(family=label, item=mv, unaged_sign=sa, aged_sign=sb,
                                 unaged_mean=float(a.loc[mv, "mean_pp"]),
                                 aged_mean=float(b.loc[mv, "mean_pp"]),
                                 holds=sa == sb))

        # ---- slot variants ----------------------------------------------------
        a, b = read(UN, "slot_robustness.csv"), read(AG, "slot_robustness.csv")
        if a is not None and b is not None:
            a = a.set_index("variant")
            b = b.set_index("variant")
            for v in a.index:
                if v not in b.index:
                    continue
                sa, sb = str(a.loc[v, "sign_agreement"]), str(b.loc[v, "sign_agreement"])
                rows.append(dict(family="slot variant", item=v, unaged_sign=sa,
                                 aged_sign=sb, unaged_mean=float(a.loc[v, "mean_pp"]),
                                 aged_mean=float(b.loc[v, "mean_pp"]), holds=sa == sb))

        # ---- headline: offseason delta, title, top-6 --------------------------
        sa_, sb_ = read(UN, "sim_all30_2026_27.csv"), read(AG, "sim_all30_2026_27.csv")
        if sa_ is not None and sb_ is not None:
            for lab, col in (("offseason delta", "title_delta"),):
                va = [float(sa_[(sa_.team_abbr == "MIN") & (sa_.fork == f)][col].iloc[0])
                      * 100 for f in FORKS]
                vb = [float(sb_[(sb_.team_abbr == "MIN") & (sb_.fork == f)][col].iloc[0])
                      * 100 for f in FORKS]
                rows.append(dict(family="headline", item=lab,
                                 unaged_sign=sign_of(va), aged_sign=sign_of(vb),
                                 unaged_mean=float(np.mean(va)),
                                 aged_mean=float(np.mean(vb)),
                                 holds=sign_of(va) == sign_of(vb)))
            ta = [float(sa_[(sa_.team_abbr == "MIN") & (sa_.fork == f)].title_current.iloc[0])
                  * 100 for f in FORKS]
            tb = [float(sb_[(sb_.team_abbr == "MIN") & (sb_.fork == f)].title_current.iloc[0])
                  * 100 for f in FORKS]
            r.note("MIN title probability: un-aged %.2f%% [%.2f, %.2f] | aged %.2f%% "
                   "[%.2f, %.2f]" % (np.mean(ta), min(ta), max(ta),
                                     np.mean(tb), min(tb), max(tb)))

        sd_a, sd_b = read(UN, "seed_distribution.csv"), read(AG, "seed_distribution.csv")
        if sd_a is not None and sd_b is not None:
            f_a = sd_a[(sd_a.team_abbr == "MIN") & (sd_a.field == "current")]
            f_b = sd_b[(sd_b.team_abbr == "MIN") & (sd_b.field == "current")]
            r.note("MIN P(top 6): un-aged %.3f [%.3f, %.3f] | aged %.3f [%.3f, %.3f]"
                   % (f_a.p_playoff_top6.mean(), f_a.p_playoff_top6.min(),
                      f_a.p_playoff_top6.max(), f_b.p_playoff_top6.mean(),
                      f_b.p_playoff_top6.min(), f_b.p_playoff_top6.max()))

        d = pd.DataFrame(rows)
        d.to_csv(OUT, index=False)

        r.note("")
        r.note("THE GATE. A verdict ships only if its SIGN is the same under both bases.")
        for fam in d.family.unique():
            sub = d[d.family == fam]
            r.note("  %s: %d of %d hold" % (fam, int(sub.holds.sum()), len(sub)))
        r.note("")
        r.note("SHIPS (same sign under both, and not MIXED):")
        ship = d[d.holds & (d.unaged_sign != "MIXED")]
        for _, x in ship.iterrows():
            # NB: x.item and x.family are pandas METHODS. Index by name.
            r.note("  %-14s %-22s %-13s | un-aged %+.3f, aged %+.3f"
                   % (x["family"], x["item"], x["unaged_sign"], x["unaged_mean"],
                      x["aged_mean"]))
        r.note("")
        r.note("DOES NOT SHIP (sign flips between bases, or MIXED in one):")
        no = d[~d.holds | (d.unaged_sign == "MIXED")]
        for _, x in no.iterrows():
            r.note("  %-14s %-22s un-aged %-13s -> aged %-13s (%+.3f -> %+.3f)"
                   % (x["family"], x["item"], x["unaged_sign"], x["aged_sign"],
                      x["unaged_mean"], x["aged_mean"]))
        r.output(OUT, rows=len(d))

    print()
    print(d.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
