#!/usr/bin/env python3
"""S3: the loophole in the lede.

"Could not legally sign him" is too strong, and the piece has to say so before a
reader with a calculator does. Minnesota sits $5,814,171 below the second apron.
The taxpayer mid-level exception is worth $6,064,000, but an exception may be used
PARTIALLY. So a first-year salary of $5,814,171 fits, and the accurate sentence is
"could not sign him to the FULL taxpayer mid-level exception".

This script prices the loophole, prices what it would have cost Kuminga, and prices
the roster it locks Minnesota into for the rest of the league year.

CBA basis, both verified 2026-08-27:
  Roster minimum  Article XXIX, Section 2(a): each Team agrees to have "either
                  fourteen (14) or fifteen (15) players, in aggregate, on its Active
                  List and Inactive List" during the Regular Season. Section 2(b)(i)
                  permits twelve or thirteen "for no more than (A) two (2) consecutive
                  weeks at a time, and (B) a total of twenty-eight (28) days".
                  https://atlhawksfanatic.github.io/NBA-CBA/miscellaneous.html
                  https://cbaguide.com/eligibility/rosters/
  Hard cap        The operative verb is EXCEED. A hard-capped team "cannot exceed the
                  Apron under any circumstance" (Larry Coon, NBA Salary Cap FAQ Q'
                  on the apron). Team salary exactly EQUAL to the apron is therefore
                  legal, which is what makes the loophole land on the dollar.
                  http://www.cbafaq.com/salarycap17.htm

    python kuminga/scripts/lede_loophole.py
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

CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")
RECON = os.path.join(REPO, "kuminga", "outputs", "cap_reconciliation.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "lede_loophole.csv")
OUT_MD = os.path.join(REPO, "kuminga", "outputs", "lede_loophole.md")

REPORTED_Y1 = 6_064_000       # R4, as reported
REPORTED_Y2 = 6_367_200       # player option
CONTRACTED_PLAYERS = 13       # Green in, Kuminga out


def money(x):
    return f"${x:,.0f}"


def main():
    with runlog.run("lede_loophole", inputs={"basis": "cap_reconciliation canonical"}) as r:
        k = json.load(open(CONST))["seasons"]["2026-27"]
        apron2 = float(k["second_apron"])
        tmle = float(k["taxpayer_mle"])
        raise_pct = float(k["exception_terms"]["taxpayer_mle"]["max_raise_pct"])
        rookie_min = float(k["min_salary_by_yos"]["0"])

        rec = pd.read_csv(RECON)
        pre = float(rec[rec.component.str.startswith(str(CONTRACTED_PLAYERS))].amount.iloc[0])

        room = apron2 - pre
        shortfall = tmle - room
        assert abs(shortfall - 249_829) < 1, f"shortfall drifted: {shortfall}"

        # --- the 14-man version: Kuminga IS the 14th man --------------------
        max14 = room
        pct14 = max14 / tmle
        # --- the 15-man version: a rookie-minimum 15th man eats the room ----
        max15 = room - rookie_min
        pct15 = max15 / tmle

        # --- what the loophole costs the player -----------------------------
        loop_y2 = max14 * (1 + raise_pct)
        loop_total = max14 + loop_y2
        reported_total = REPORTED_Y1 + REPORTED_Y2
        player_cost = reported_total - loop_total

        rows = [
            dict(item="second apron, 2026-27", amount=apron2,
                 note="league_year_constants, verified against NBA.com"),
            dict(item=f"contracted salary, {CONTRACTED_PLAYERS} players", amount=pre,
                 note="canonical apron basis; Green in, Kuminga out"),
            dict(item="ROOM under the second apron", amount=room,
                 note="this is the number the lede has to survive"),
            dict(item="full taxpayer MLE", amount=tmle, note="the exception as a whole"),
            dict(item="shortfall against the FULL exception", amount=shortfall,
                 note="the $249,829 already in the piece"),
            dict(item="max first-year salary, 14-man roster", amount=max14,
                 note=f"{pct14:.1%} of the exception; lands exactly ON the apron, "
                      f"which is legal because the rule prohibits EXCEEDING it"),
            dict(item="max first-year salary, 15-man roster", amount=max15,
                 note=f"{pct15:.1%} of the exception, after a rookie-minimum 15th man "
                      f"at {money(rookie_min)}"),
            dict(item="two-year value of the loophole deal", amount=loop_total,
                 note=f"{money(max14)} then {money(loop_y2)} at the {raise_pct:.0%} "
                      f"maximum raise"),
            dict(item="two-year value as reported", amount=reported_total,
                 note=f"{money(REPORTED_Y1)} then {money(REPORTED_Y2)} player option"),
            dict(item="what the loophole costs KUMINGA", amount=player_cost,
                 note="the reason it is a loophole and not a plan"),
        ]
        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)

        r.note(f"room under the second apron: {money(room)}")
        r.note(f"full taxpayer MLE {money(tmle)}, so short by {money(shortfall)} "
               f"({shortfall / tmle:.1%} of the exception)")
        r.note(f"PARTIAL MLE AT 14 MEN: {money(max14)} = {pct14:.1%} of the exception, "
               f"team salary lands at exactly {money(pre + max14)} = the apron to the dollar")
        r.note(f"PARTIAL MLE AT 15 MEN: {money(max15)} = {pct15:.1%} of the exception")
        r.note(f"cost to Kuminga over two years: {money(player_cost)}")
        r.note("ROSTER CONSEQUENCE: at exactly the apron with 14 men, Minnesota cannot "
               "add a 15th player, absorb a dollar in any trade, or sign a hardship "
               "replacement for the rest of the league year. Article XXIX Sec 2(b)(i) "
               "lets them sit at 13 for two weeks at a time and 28 days total, so the "
               "14th man is required but not required every single day.")
        r.note("RULING: the lede changes from 'could not legally sign him' to 'could not "
               "sign him to the full taxpayer mid-level exception'. The Green move buys "
               "the last $249,829 AND the room to carry a normal roster.")

        with open(OUT_MD, "w", encoding="utf-8") as f:
            f.write("# The loophole in the lede (S3)\n\n")
            f.write(df.to_markdown(index=False, floatfmt=",.0f"))
            f.write("\n\n**Roster minimum:** CBA Article XXIX, Section 2(a) requires 14 or "
                    "15 players on the Active and Inactive Lists during the regular season; "
                    "Section 2(b)(i) permits 12 or 13 for no more than two consecutive "
                    "weeks at a time and 28 days in total.\n\n")
            f.write("**Hard cap:** the rule prohibits *exceeding* the apron, so a team "
                    "salary exactly equal to it is legal. That is why the partial-exception "
                    "figure lands on the dollar.\n")
        r.output(OUT, rows=len(df))
        r.output(OUT_MD)

    print()
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
