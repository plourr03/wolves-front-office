#!/usr/bin/env python3
"""R3: reconcile our Apron Team Salary against Spotrac's, for all 30 teams.

WHY THIS EXISTS. The independent check (V1) found our apron basis was understated by
$1,750,000 for Minnesota because it omitted UNLIKELY BONUSES. Apron Team Salary is
regular Team Salary minus cap holds PLUS unlikely bonuses, and we were carrying
contracted salary only. That error was found for one team. This asks whether it is
one team or thirty, and it is the check that should have run before anything shipped.

CITATIONS for the rule, both verified 2026-08-27:
  Hoops Rumors, tax-apron glossary: "the Aprons make adjustments to Team Salary by
    removing Cap Holds and adding Unlikely Bonuses, which is called Apron Team Salary"
    https://www.hoopsrumors.com/2025/01/hoops-rumors-glossary-tax-aprons-2.html
  The CBA Guide, The Aprons: https://cbaguide.com/thresholds/apron/

INPUT. `spotrac_apron_2026_27.csv`, transcribed from Spotrac's 2026-27 apron tracker
(columns: rank, team, allocation, first_apron_space, second_apron_space). Spotrac
publishes the apron figure directly, so the comparison is like-for-like once we add
unlikely bonuses to ours.

    python kuminga/scripts/apron_reconcile_all30.py
"""
from __future__ import annotations

import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")
CONTRACTS = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27_verified.csv")
SPOTRAC = os.path.join(REPO, "offseason", "data", "spotrac_apron_2026_27.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "apron_reconcile_all30.csv")
TOL = 2_000.0


def main():
    with runlog.run("apron_reconcile_all30", inputs={"tolerance": TOL,
                                                     "source": "spotrac 2026-27"}) as r:
        k = json.load(open(CONST, encoding="utf-8"))["seasons"]["2026-27"]
        ap1, ap2, tax = (float(k["first_apron"]), float(k["second_apron"]),
                         float(k["luxury_tax"]))
        sp = pd.read_csv(SPOTRAC)
        ct = pd.read_csv(CONTRACTS)
        # our basis: contracted salary only, excluding the synthetic placeholder rows
        real = ct[~ct.player.astype(str).str.startswith("[")]
        ours = real.groupby("team_abbr").salary_2026_27.sum().rename("ours_contracted")
        cnt = real.groupby("team_abbr").size().rename("n_contracts")

        m = sp.set_index("team").join([ours, cnt], how="outer")
        m["spotrac_apron"] = m.allocation
        # Spotrac's own space figures are the cross-check on their allocation
        m["spotrac_implied_ap2"] = ap2 - m.allocation
        m["diff"] = m.ours_contracted - m.spotrac_apron
        m["abs_diff"] = m["diff"].abs()

        r.note(f"teams matched: {int(m.ours_contracted.notna().sum())} of {len(m)}")
        internal = (m.spotrac_implied_ap2 - m.second_apron_space).abs()
        r.note(f"Spotrac internal consistency (apron2 - allocation vs their own 2nd "
               f"apron space): max mismatch ${internal.max():,.0f}")

        off = m[m.abs_diff > TOL].sort_values("abs_diff", ascending=False)
        r.note(f"teams differing by more than ${TOL:,.0f}: {len(off)} of {len(m)}")
        for t, x in off.iterrows():
            r.note(f"  {t}: ours ${x.ours_contracted:,.0f} vs Spotrac "
                   f"${x.spotrac_apron:,.0f} = {x['diff']:+,.0f} "
                   f"({int(x.n_contracts)} contracts)")

        r.note("")
        r.note("CAUSE. Our figure is CONTRACTED SALARY ONLY. Spotrac's is APRON TEAM "
               "SALARY, which adds unlikely bonuses. Every negative difference is "
               "consistent with unlikely bonuses we do not carry; the size of the gap "
               "IS the league-wide scale of the omission.")
        neg = m[m["diff"] < -TOL]
        r.note(f"  teams where ours is LOWER (missing incentives): {len(neg)}, "
               f"total ${-neg['diff'].sum():,.0f}, median ${-neg['diff'].median():,.0f}")
        pos = m[m["diff"] > TOL]
        if len(pos):
            r.note(f"  teams where ours is HIGHER ({len(pos)}), which incentives cannot "
                   f"explain and needs a roster-level check: "
                   + ", ".join(f"{t} +{x['diff']:,.0f}" for t, x in pos.iterrows()))

        # ---- tier flags on each basis ---------------------------------------
        def tier(v):
            if v >= ap2:
                return "second_apron"
            if v >= ap1:
                return "first_apron"
            if v >= tax:
                return "taxpayer"
            return "under_tax"

        m["tier_ours"] = m.ours_contracted.map(tier)
        m["tier_spotrac"] = m.spotrac_apron.map(tier)
        m["tier_changed"] = m.tier_ours != m.tier_spotrac
        ch = m[m.tier_changed & m.ours_contracted.notna()]
        r.note("")
        r.note(f"APRON TIER on our basis vs the corrected basis: {len(ch)} teams change "
               f"tier")
        for t, x in ch.iterrows():
            r.note(f"  {t}: {x.tier_ours} -> {x.tier_spotrac} "
                   f"(ours ${x.ours_contracted:,.0f}, apron ${x.spotrac_apron:,.0f})")
        r.note("  tier counts, corrected basis: "
               + ", ".join(f"{k2}={v}" for k2, v in
                           m.tier_spotrac.value_counts().items()))
        m.reset_index().to_csv(OUT, index=False)
        r.output(OUT, rows=len(m))

    print()
    print(m.rename_axis("team").reset_index()[["team", "n_contracts", "ours_contracted", "spotrac_apron",
                           "diff", "tier_ours", "tier_spotrac"]]
          .sort_values("diff").to_string(index=False))


if __name__ == "__main__":
    main()
