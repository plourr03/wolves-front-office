#!/usr/bin/env python3
"""D70: every headline figure before and after the position and identity fixes.

The fixes changed two things with different reach. The position rule is invisible to the
pool-blind headline allocator and reaches only the attribution layer. The identity fix
changed the Clippers' and Nets' rosters, which changes the field every Minnesota number
is priced against. So nothing here is assumed unchanged; everything is re-read from the
frozen pre-fix outputs in `outputs/_before_d70/` and set against the regenerated ones.

    python kuminga/scripts/d70_before_after.py
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

OUT = os.path.join(REPO, "kuminga", "outputs")
BEF = os.path.join(OUT, "_before_d70")
FORKS = ["consensus", "rapm", "box", "darko"]


def rd(*p):
    f = os.path.join(*p)
    return pd.read_csv(f) if os.path.exists(f) else None


def band(sim, col, scale=100):
    if sim is None:
        return None
    m = sim[sim.team_abbr == "MIN"].set_index("fork")
    v = [float(m.loc[f, col]) * scale for f in FORKS]
    return float(np.mean(v)), min(v), max(v)


def main():
    with runlog.run("d70_before_after", inputs={"before": BEF}) as r:
        rows = []

        def add(label, before, after, fmt="%.2f"):
            rows.append(dict(figure=label, before=before, after=after))
            b = fmt % before if isinstance(before, (int, float)) else str(before)
            a = fmt % after if isinstance(after, (int, float)) else str(after)
            flag = ""
            if isinstance(before, str) and before != after:
                flag = "   <-- CHANGED"
            r.note("  %-44s %-26s -> %-26s%s" % (label, b, a, flag))

        r.note("HEADLINE, un-aged basis")
        sb, sa = rd(BEF, "unaged", "sim_all30_2026_27.csv"), rd(OUT, "preaging",
                                                                "sim_all30_2026_27.csv")
        for lab, col in (("MIN title probability", "title_current"),
                         ("MIN offseason delta (pp)", "title_delta")):
            b, a = band(sb, col), band(sa, col)
            if b and a:
                add(lab, "%.2f [%.2f, %.2f]" % b, "%.2f [%.2f, %.2f]" % a, "%s")

        r.note("")
        r.note("THE SHIPPING LIST (sign holds under both aging bases)")
        gb, ga = rd(BEF, "w2_aging_gate.csv"), rd(OUT, "w2_aging_gate.csv")
        if gb is not None and ga is not None:
            gb = gb.set_index("item")
            ga = ga.set_index("item")
            for it in ga.index:
                sb_ = ("%s %s" % (gb.loc[it, "unaged_sign"], "SHIPS" if gb.loc[it, "holds"]
                       and gb.loc[it, "unaged_sign"] != "MIXED" else "no")
                       if it in gb.index else "n/a")
                sa_ = "%s %s" % (ga.loc[it, "unaged_sign"],
                                 "SHIPS" if ga.loc[it, "holds"]
                                 and ga.loc[it, "unaged_sign"] != "MIXED" else "no")
                add(it, sb_, sa_, "%s")
            n_b = int((gb.holds & (gb.unaged_sign != "MIXED")).sum())
            n_a = int((ga.holds & (ga.unaged_sign != "MIXED")).sum())
            r.note("  verdicts shipping: %d before, %d after" % (n_b, n_a))

        r.note("")
        r.note("NOISE FLOOR SURVIVORS, un-aged")
        for fn, key in (("noise_floor.csv", "move"), ("noise_floor_slot.csv", "variant")):
            b, a = rd(BEF, fn), rd(OUT, fn)
            if b is not None and a is not None:
                add(fn.replace(".csv", ""), ", ".join(b[b.survives][key]),
                    ", ".join(a[a.survives][key]), "%s")

        r.note("")
        r.note("KUMINGA SLOT, variant A")
        for lab, d in (("un-aged", "unaged"),):
            b = rd(BEF, d, "slot_robustness.csv")
            a = rd(OUT, "preaging", "slot_robustness.csv")
            if b is not None and a is not None:
                xb = b[b.variant == "A_c3_default_shannon"].iloc[0]
                xa = a[a.variant == "A_c3_default_shannon"].iloc[0]
                add("slot A mean pp (%s)" % lab, float(xb.mean_pp), float(xa.mean_pp), "%+.3f")
                add("slot A sign (%s)" % lab, str(xb.sign_agreement), str(xa.sign_agreement),
                    "%s")

        r.note("")
        r.note("W1c DECOMPOSITION")
        b, a = rd(BEF, "w1c_delta_decomposition.csv"), rd(OUT, "w1c_delta_decomposition.csv")
        if b is not None and a is not None:
            for c in ("offseason_delta", "injury_cost", "williams_cost", "interaction",
                      "remainder"):
                add(c, float(b[c].mean()), float(a[c].mean()), "%+.3f")

        r.note("")
        r.note("MARKET vs MODEL, Minnesota")
        b, a = rd(BEF, "market_devig_2026_27.csv"), rd(OUT, "market_devig_2026_27.csv")
        if b is not None and a is not None:
            xb = b.set_index("team_abbr").loc["MIN"]
            xa = a.set_index("team_abbr").loc["MIN"]
            add("MIN model rank", int(xb.model_rank), int(xa.model_rank), "%d")
            add("MIN model pct", float(xb.model_pct), float(xa.model_pct), "%.2f")
            add("teams off by more than floor", int((b.diff_pp.abs() > 0.5).sum()),
                int((a.diff_pp.abs() > 0.5).sum()), "%d")
            for tm in ("LAC", "BKN"):
                add("%s model pct (roster changed)" % tm,
                    float(b.set_index("team_abbr").loc[tm, "model_pct"]),
                    float(a.set_index("team_abbr").loc[tm, "model_pct"]), "%.2f")

        r.note("")
        r.note("N2 PATH")
        b, a = rd(BEF, "n2_round1_opponents.csv"), rd(OUT, "n2_round1_opponents.csv")
        if b is not None and a is not None:
            fb = b.set_index(b.columns[0]).iloc[:, 0].head(3)
            fa = a.set_index(a.columns[0]).iloc[:, 0].head(3)
            add("top round-1 opponents",
                ", ".join("%s %.3f" % kv for kv in fb.items()),
                ", ".join("%s %.3f" % kv for kv in fa.items()), "%s")

        pd.DataFrame(rows).to_csv(os.path.join(OUT, "d70_before_after.csv"), index=False)
        r.output(os.path.join(OUT, "d70_before_after.csv"), rows=len(rows))


if __name__ == "__main__":
    main()
