#!/usr/bin/env python3
"""F1/F2: the Dosunmu counterfactual as two FINAL STATES, not as a subtraction.

The earlier versions priced "remove Dosunmu" and then asked what exception was left
over. That answers a question nobody faces. A general manager compares two finished
rosters, both legal, both with Kuminga on them. This does that.

  ACTUAL          Green traded out, Kuminga on the taxpayer MLE at $6,064,000,
                  14 players. This is the trade branch already in the piece.
  COUNTERFACTUAL  Dosunmu not re-signed, Green KEPT, a replacement guard on a
                  minimum, and Kuminga signed with the NON-taxpayer mid-level as the
                  14th man. His first-year salary is capped by the first apron,
                  because using that exception hard-caps the team there.

The replacement guard is priced two ways, because the charge is not obvious: a
veteran with 3+ years on a ONE-YEAR minimum is charged the two-year figure
($2,449,000) with the league paying the rest, while a rookie minimum is $1,358,000.

    python kuminga/scripts/dosunmu_final_states.py
"""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

from kuminga.lib import runlog      # noqa: E402
from cap_branches import tax_bill   # noqa: E402

CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")
CONTRACTS = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27_verified.csv")
RECON = os.path.join(REPO, "kuminga", "outputs", "cap_reconciliation.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "dosunmu_final_states.csv")

ACTUAL_TRADE_BRANCH = 208_614_817     # Green out, Kuminga at the taxpayer MLE, 14 men
PROBE_SALARIES = [8_000_000, 9_000_000]


def money(x):
    return f"${x:,.0f}"


def main():
    with runlog.run("dosunmu_final_states",
                    inputs={"actual_branch": ACTUAL_TRADE_BRANCH}) as r:
        k = json.load(open(CONST, encoding="utf-8"))["seasons"]["2026-27"]
        tax_line, ap1, ap2 = (float(k["luxury_tax"]), float(k["first_apron"]),
                              float(k["second_apron"]))
        full_mle, tmle = float(k["full_mle"]), float(k["taxpayer_mle"])
        rookie_min = float(k["min_salary_by_yos"]["0"])
        vet_min = float(k["min_salary_by_yos"]["2"])
        brackets = k["tax_brackets_nonrepeater_approx"]

        ct = pd.read_csv(CONTRACTS)
        dos = float(ct[ct.player == "Ayo Dosunmu"].salary_2026_27.iloc[0])
        green = float(ct[ct.player == "Josh Green"].salary_2026_27.iloc[0])
        rec = pd.read_csv(RECON)
        pre = float(rec[rec["component"].str.startswith("13")].amount.iloc[0])

        rows = []

        def st(state, roster, salary, note=""):
            over = salary - tax_line
            rows.append(dict(state=state, n_players=roster, payroll=salary,
                             vs_tax_line=over,
                             est_tax_bill=tax_bill(max(over, 0.0), brackets),
                             vs_first_apron=ap1 - salary, vs_second_apron=ap2 - salary,
                             note=note))

        # ---- why Green has to go, with BOTH contracts on the book -------------
        overage = pre + tmle - ap2
        r.note("WHY GREEN MUST BE SHED, arithmetic with Dosunmu AND Green on the book:")
        r.note(f"  13 contracted (Dosunmu {money(dos)} and Green {money(green)} both in): "
               f"{money(pre)}")
        r.note(f"  + Kuminga at the taxpayer MLE {money(tmle)} = {money(pre + tmle)}")
        r.note(f"  second apron {money(ap2)} -> {money(overage)} OVER. Cannot be signed.")
        r.note(f"  Dosunmu's {money(dos)} is larger than that overage by "
               f"{money(dos - overage)}, so with him off the book Green stays AND the "
               f"signing still fits. Green is being shed to pay for Dosunmu.")
        st("ACTUAL: Dosunmu + Green + Kuminga at the taxpayer MLE", 14, pre + tmle,
           "cannot be signed, over the second apron hard cap")
        st("ACTUAL: Green traded out, Kuminga at the taxpayer MLE", 14,
           float(ACTUAL_TRADE_BRANCH), "the trade branch in the piece")

        # ---- the counterfactual: Dosunmu gone, Green KEPT ---------------------
        base12 = pre - dos
        ceilings = {}
        r.note("")
        r.note(f"COUNTERFACTUAL, Dosunmu not re-signed, Green KEPT: 12 players at "
               f"{money(base12)}")
        for lab, repl in (("veteran min (2-yr charge)", vet_min),
                          ("rookie min", rookie_min)):
            at13 = base12 + repl
            room13 = ap1 - at13
            ceiling = min(room13, full_mle)
            ceilings[lab] = ceiling
            binds = "the first apron" if room13 < full_mle else "the exception itself"
            r.note(f"  [replacement guard on a {lab}, {money(repl)}]")
            r.note(f"    13 players: {money(at13)} | room under the first apron "
                   f"{money(room13)}")
            r.note(f"    => CEILING on Kuminga's first-year salary: {money(ceiling)} "
                   f"(binding constraint is {binds}; the exception is {money(full_mle)})")
            st(f"CF: {lab} + Kuminga at the ceiling", 14, at13 + ceiling,
               f"Kuminga at {money(ceiling)}; lands exactly on the first apron")
            for probe in PROBE_SALARIES:
                tot = at13 + probe
                room15 = ap1 - tot
                fits = room15 >= rookie_min
                r.note(f"    at {money(probe)}: 14-man payroll {money(tot)} | "
                       f"{money(tot - tax_line)} over the tax line (bill "
                       f"{money(tax_bill(tot - tax_line, brackets))}, est) | "
                       f"{money(room15)} left under the apron, so a 15th man on the "
                       f"rookie minimum {'FITS' if fits else 'does NOT fit'}")
                st(f"CF: {lab} + Kuminga at {money(probe)}", 14, tot,
                   f"15th man on the rookie min {'fits' if fits else 'does not fit'} "
                   f"({money(room15)} of apron room left)")

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)

        # ---- the comparison the piece actually makes -------------------------
        act = df[df.state.str.startswith("ACTUAL: Green traded")].iloc[0]
        cf_v = df[df.state == "CF: veteran min (2-yr charge) + Kuminga at the ceiling"].iloc[0]
        r.note("")
        r.note("THE TWO FINAL STATES, side by side:")
        r.note(f"  ACTUAL          {money(act.payroll)} at 14 | "
               f"{money(act.vs_tax_line)} over the tax line | est tax "
               f"{money(act.est_tax_bill)} | Kuminga at {money(tmle)} | Green GONE")
        r.note(f"  COUNTERFACTUAL  {money(cf_v.payroll)} at 14 | "
               f"{money(cf_v.vs_tax_line)} over the tax line | est tax "
               f"{money(cf_v.est_tax_bill)} | Kuminga up to "
               f"{money(ceilings['veteran min (2-yr charge)'])} | Green KEPT")
        r.note("")
        r.note("WHAT THE RE-SIGNING BOUGHT, the two things to write:")
        r.note(f"  1. It is why Green has to be shed at all. With both contracts on the "
               f"book, Kuminga at the full taxpayer MLE is {money(overage)} over the "
               f"second apron and cannot be signed.")
        r.note(f"  2. It cut Kuminga's first-year ceiling from up to "
               f"{money(ceilings['veteran min (2-yr charge)'])} to "
               f"{money(ceilings['rookie min'])} (non-taxpayer MLE, capped by the first "
               f"apron) down to {money(tmle)}.")
        r.note(f"  NOTE both final states are TAXPAYERS. The counterfactual is not a way "
               f"out of the tax: it sits {money(cf_v.vs_tax_line)} over the line against "
               f"{money(act.vs_tax_line)}. The tax saving is about "
               f"{money(act.est_tax_bill - cf_v.est_tax_bill)} (est), and it is NEGATIVE "
               f"if the counterfactual spends its bigger exception in full.")
        r.output(OUT, rows=len(df))

    print()
    print(df.to_string(index=False, float_format=lambda x: f"{x:,.0f}"))


if __name__ == "__main__":
    main()
