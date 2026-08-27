#!/usr/bin/env python3
"""P1(b): the cap half of the Dosunmu finding.

The Shapley number (P1a) is an ON-COURT claim: his minutes against the guards
actually on the roster, negative under all four views. It says nothing about money.
This script computes the separate CAP claim, so the two can be labelled apart in the
piece instead of being blurred into one "bad contract" verdict.

THE COUNTERFACTUAL, STATED SO IT IS NOT OVERREAD. Minnesota was over the cap. Letting
Dosunmu go would NOT have handed them $19.3M to spend elsewhere; an over-the-cap team
has exceptions, not room. The counterfactual priced here is "lose him for nothing and
his minutes go to the guards already on the roster", which is also exactly what the
Shapley run models. What his salary buys is not a replacement player. It is tax
liability and apron distance, and that is what is measured below.

TAX ATTRIBUTION, ALSO STATED. The luxury tax is marginal, so no single contract "causes"
a particular bracket. The figure here is a clean counterfactual: how the bill changes if
his salary comes off the book and everything else stays. The same delta could be
attributed to any $19.3M on the roster.

    python kuminga/scripts/dosunmu_cap.py
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

from kuminga.lib import runlog          # noqa: E402
from cap_branches import tax_bill       # noqa: E402  (same brackets as the branch table)

CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")
CONTRACTS = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27_verified.csv")
RECON = os.path.join(REPO, "kuminga", "outputs", "cap_reconciliation.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "dosunmu_cap.csv")

PLAYER = "Ayo Dosunmu"


def money(x):
    return f"${x:,.0f}"


def main():
    with runlog.run("dosunmu_cap", inputs={"player": PLAYER,
                                           "basis": "canonical apron basis"}) as r:
        k = json.load(open(CONST, encoding="utf-8"))["seasons"]["2026-27"]
        tax_line = float(k["luxury_tax"])
        ap1, ap2 = float(k["first_apron"]), float(k["second_apron"])
        full_mle, tmle = float(k["full_mle"]), float(k["taxpayer_mle"])
        rookie_min = float(k["min_salary_by_yos"]["0"])
        brackets = k["tax_brackets_nonrepeater_approx"]

        ct = pd.read_csv(CONTRACTS)
        d = ct[ct.player == PLAYER]
        assert len(d) == 1, f"expected one {PLAYER} row, got {len(d)}"
        d = d.iloc[0]
        sal = float(d.salary_2026_27)
        years = [d.salary_2026_27, d.salary_2027_28, d.salary_2028_29,
                 d.salary_2029_30]
        known = float(pd.Series(years).dropna().sum())

        rec = pd.read_csv(RECON)
        pre = float(rec[rec["component"].str.startswith("13")].amount.iloc[0])
        withk = pre + tmle

        rows = []

        def state(label, salary, n_players):
            over_tax = salary - tax_line
            bill = tax_bill(max(over_tax, 0.0), brackets)
            rows.append(dict(scenario=label, n_players=n_players, team_salary=salary,
                             vs_tax_line=over_tax, est_tax_bill=bill,
                             vs_first_apron=ap1 - salary, vs_second_apron=ap2 - salary))
            return bill

        # --- pre-Kuminga basis, the cleanest read on what his salary does --------
        b_with = state("13 players, Dosunmu on the book", pre, 13)
        b_out = state("12 players, Dosunmu gone (NOT a legal roster)", pre - sal, 12)
        # --- D1: the counterfactual at a LEGAL roster ---------------------------
        # A veteran with 3+ years of service on a ONE-YEAR minimum is charged the
        # TWO-YEAR minimum against team salary; the league pays the difference. That
        # is the correct charge for a replacement guard, and it is not the rookie
        # minimum. One-year deals only; a multi-year minimum counts in full.
        #   https://www.hoopsrumors.com/2026/03/hoops-rumors-glossary-minimum-salary-exception-5.html
        vet_min = float(k["min_salary_by_yos"]["2"])
        base12 = pre - sal
        # the 14th man is the swing: cheapest possible, or another veteran
        s_cheap = base12 + vet_min + rookie_min
        s_vet = base12 + vet_min + vet_min
        b_cheap = state("14 players, Dosunmu gone + vet-min guard + rookie min",
                        s_cheap, 14)
        b_vet = state("14 players, Dosunmu gone + vet-min guard + vet min",
                      s_vet, 14)
        # --- with Kuminga signed -------------------------------------------------
        state("14 players, Kuminga signed (actual)", withk, 14)
        state("13 players, Kuminga signed, Dosunmu gone", withk - sal, 13)

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)

        r.note(f"{PLAYER}: {money(sal)} in 2026-27, {money(known)} of known salary over "
               f"{int(d.years_left)} years, rising to {money(float(d.salary_2028_29))} "
               f"by 2028-29")
        r.note(f"TAX. On the book they are {money(pre - tax_line)} over the tax line and "
               f"owe about {money(b_with)} (est).")
        r.note(f"  Bare subtraction leaves {money(tax_line - (pre - sal))} under the line, "
               f"but that is a 12-man roster and therefore not a team. See D1 below for "
               f"the figure that can actually be printed.")
        r.note("--- D1: THE SAME COUNTERFACTUAL AT A LEGAL 14-MAN ROSTER ---")
        r.note(f"  A 12-man roster is not legal, so the honest version replaces him. "
               f"Replacement guard at the veteran minimum is charged {money(vet_min)}, "
               f"the TWO-year figure, not the {money(3877000.0)} a long veteran actually "
               f"earns; the league pays the difference on a one-year deal.")
        for lab, tot, bill in (("14th man at the rookie minimum", s_cheap, b_cheap),
                               ("14th man at a veteran minimum", s_vet, b_vet)):
            d_tax = tot - tax_line
            r.note(f"  [{lab}] team salary {money(tot)} | "
                   f"{money(abs(d_tax))} {'OVER' if d_tax > 0 else 'under'} the tax line "
                   f"(bill about {money(bill)}, est) | "
                   f"{money(ap1 - tot)} under the first apron")
        lo, hi = min(ap1 - s_vet, ap1 - s_cheap), max(ap1 - s_vet, ap1 - s_cheap)
        r.note(f"  USABLE NON-TAXPAYER MLE at a full roster: the exception is "
               f"{money(full_mle)} but using it hard-caps at the first apron, so only "
               f"{money(min(full_mle, lo))} to {money(min(full_mle, hi))} of it is "
               f"actually spendable, depending on who fills the last spot.")
        r.note(f"  THE COMPARISON, stated as it must be written: up to "
               f"{money(min(full_mle, lo))} to {money(min(full_mle, hi))} at a full "
               f"roster, against the {money(tmle)} taxpayer exception they actually had.")
        r.note(f"  CORRECTION TO THE EARLIER FIGURE. The {money(min(full_mle, ap1 - base12))} "
               f"reported before was computed at a 12-man roster, which is not a legal "
               f"team. At 14 the usable exception is {money(min(full_mle, hi))} or less.")
        r.note("  AND THE TAX CLAIM SOFTENS. At a legal roster the no-Dosunmu team sits "
               f"{money(abs(s_cheap - tax_line))} under the line in the cheap version and "
               f"{money(abs(s_vet - tax_line))} OVER it in the veteran version. It "
               "straddles the tax line rather than clearing it. Do NOT write 'owing "
               "nothing'; write that his contract moves them from ~$15.4M over the line "
               "to roughly level with it.")
        r.note(f"APRON. With Kuminga signed they are {money(withk - ap2)} over the second "
               f"apron. Without Dosunmu the same roster sits {money(ap2 - (withk - sal))} "
               f"UNDER it.")
        r.note("COUNTERFACTUAL LABEL: 'lose him for nothing', NOT 'spend the money "
               "elsewhere'. Minnesota was over the cap, so his salary was never "
               "convertible into a free agent at that price.")
        r.output(OUT, rows=len(df))

    print()
    print(df.to_string(index=False, float_format=lambda x: f"{x:,.0f}"))


if __name__ == "__main__":
    main()
