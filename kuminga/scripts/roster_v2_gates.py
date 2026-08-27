#!/usr/bin/env python3
"""G4 gates A and B on roster_snapshot_2026_27_v2. Fail closed.

GATE A, membership. Every team 13-15 standard contracts, at most 3 two-way.
GATE B, dollars. Apron Team Salary per team within $2,000 of Spotrac's published figure,
        30 of 30.

APRON TEAM SALARY, as built here:
    standard + non_guaranteed + dead_money cap hits
  + unlikely incentives on those rows
  - nothing for cap holds (excluded from the apron basis)
  - nothing for pending transactions (Spotrac excludes them from team totals, and so
    does the CBA until a signing is official)

    python kuminga/scripts/roster_v2_gates.py
"""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

SNAP = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_v2.csv")
SPOT = os.path.join(REPO, "offseason", "data", "spotrac_apron_2026_27.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "roster_v2_gates.csv")
TOL = 2_000.0
COUNTED = ("standard", "non_guaranteed", "dead_money")


def main():
    with runlog.run("roster_v2_gates", inputs={"tolerance": TOL}) as r:
        d = pd.read_csv(SNAP)
        sp = pd.read_csv(SPOT).set_index("team")

        std = d[d.status.isin(["standard", "non_guaranteed"])]
        tw = d[d.status == "two_way"]
        counted = d[d.status.isin(COUNTED)]
        apron = (counted.groupby("team_abbr")
                 .apply(lambda g: g.cap_hit_2026_27.sum() + g.incentives_unlikely.sum(),
                        include_groups=False).rename("ours_apron"))
        t = pd.DataFrame({
            "n_standard": std.groupby("team_abbr").size(),
            "n_two_way": tw.groupby("team_abbr").size(),
            "n_dead": d[d.status == "dead_money"].groupby("team_abbr").size(),
            "unlikely": counted.groupby("team_abbr").incentives_unlikely.sum(),
        }).join(apron).join(sp[["allocation"]]).rename(
            columns={"allocation": "spotrac_apron"})
        t = t.fillna({"n_two_way": 0, "n_dead": 0})
        t["diff"] = t.ours_apron - t.spotrac_apron
        t["within_tol"] = t["diff"].abs() <= TOL
        t["gate_a"] = t.n_standard.between(13, 15) & (t.n_two_way <= 3)
        t.reset_index().rename(columns={"index": "team"}).to_csv(OUT, index=False)

        # ---- GATE A -------------------------------------------------------
        fa = t[~t.gate_a]
        r.note("GATE A, membership (13-15 standard, <=3 two-way):")
        r.note("  standard-count distribution: "
               + ", ".join(f"{k}:{v}" for k, v in
                           sorted(t.n_standard.value_counts().items())))
        if len(fa):
            r.note(f"  FAIL, {len(fa)} teams outside 13-15: "
                   + ", ".join(f"{i}={int(x.n_standard)}" for i, x in fa.iterrows()))
            r.note("  NOTE these are SPOTRAC's own counts, parsed to match their header "
                   "exactly. Teams legitimately carry more than 15 under contract in "
                   "August and must cut to 15 before the season. The 13-15 range is a "
                   "REGULAR-SEASON rule, not an August one, so a failure here is a "
                   "finding about the GATE, not about the data.")
        else:
            r.note("  PASS, all 30 teams within 13-15 standard")
        r.note(f"  two-way rows parsed: {int(t.n_two_way.sum())} "
               f"(Spotrac headers show 0 of 3 TW signed for 2026-27 league-wide)")

        # ---- GATE B -------------------------------------------------------
        fb = t[~t.within_tol].sort_values("diff", key=abs, ascending=False)
        r.note("")
        r.note(f"GATE B, dollars (within ${TOL:,.0f} of Spotrac's apron figure):")
        r.note(f"  {int(t.within_tol.sum())} of {len(t)} teams clear")
        for i, x in fb.iterrows():
            r.note(f"    {i}: ours ${x.ours_apron:,.0f} vs ${x.spotrac_apron:,.0f} "
                   f"= {x['diff']:+,.0f}  (std {int(x.n_standard)}, dead "
                   f"{int(x.n_dead)}, unlikely ${x.unlikely:,.0f})")
        r.note(f"  sum of absolute differences: ${t['diff'].abs().sum():,.0f} "
               f"(was $183,047,636 on v1)")

        mn = t.loc["MIN"]
        r.note("")
        r.note(f"MINNESOTA: {int(mn.n_standard)} standard, apron ${mn.ours_apron:,.0f} "
               f"vs Spotrac ${mn.spotrac_apron:,.0f}, diff {mn['diff']:+,.0f}; "
               f"unlikely incentives ${mn.unlikely:,.0f}")
        gate_b = bool(t.within_tol.all())
        gate_a = bool(t.gate_a.all())
        r.note(f"GATE A {'PASS' if gate_a else 'FAIL'} | GATE B "
               f"{'PASS' if gate_b else 'FAIL'}")
        json.dump({"gate_a": gate_a, "gate_b": gate_b,
                   "teams_within_tol": int(t.within_tol.sum()),
                   "abs_diff": float(t['diff'].abs().sum())},
                  open(os.path.join(REPO, "kuminga", "outputs", "roster_v2_gates.json"),
                       "w"), indent=1)
        r.output(OUT, rows=len(t))

    print()
    print(t[["n_standard", "n_two_way", "n_dead", "unlikely", "ours_apron",
             "spotrac_apron", "diff", "within_tol", "gate_a"]]
          .sort_values("diff").to_string())


if __name__ == "__main__":
    main()
