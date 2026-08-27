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
        b_out = state("12 players, Dosunmu gone", pre - sal, 12)
        # honest version: they still have to reach the 14-man floor
        b_out14 = state("14 players, Dosunmu gone + 2 minimums",
                        pre - sal + 2 * rookie_min, 14)
        # --- with Kuminga signed -------------------------------------------------
        state("14 players, Kuminga signed (actual)", withk, 14)
        state("13 players, Kuminga signed, Dosunmu gone", withk - sal, 13)

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)

        r.note(f"{PLAYER}: {money(sal)} in 2026-27, {money(known)} of known salary over "
               f"{int(d.years_left)} years, rising to {money(float(d.salary_2028_29))} "
               f"by 2028-29")
        r.note(f"TAX. On the book they are {money(pre - tax_line)} over the tax line and "
               f"owe about {money(b_with)}. Take his salary off and they are "
               f"{money(tax_line - (pre - sal))} UNDER it, owing nothing.")
        r.note(f"  So the marginal tax cost of the contract is about {money(b_with - b_out)}, "
               f"i.e. the whole bill: his contract is the only reason they are a taxpayer "
               f"on this basis.")
        r.note(f"  Filling to the 14-man floor with two minimums instead: "
               f"{money(pre - sal + 2 * rookie_min - tax_line)} vs the tax line, bill "
               f"about {money(b_out14)}.")
        room1 = ap1 - (pre - sal)
        r.note(f"EXCEPTION TIER. Without him, pre-Kuminga salary is "
               f"{money(pre - sal)}, which is {money(room1)} under the FIRST apron. The "
               f"non-taxpayer mid-level is {money(full_mle)} and using it hard-caps at the "
               f"first apron, so they could have spent up to {money(min(full_mle, room1))} "
               f"on a free agent instead of the {money(tmle)} taxpayer exception.")
        r.note(f"  That is the sharpest version of the cap claim: his contract is why the "
               f"tool available to sign Kuminga was {money(tmle)} rather than up to "
               f"{money(min(full_mle, room1))}.")
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
