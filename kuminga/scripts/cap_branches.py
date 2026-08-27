#!/usr/bin/env python3
"""Item 16: Minnesota's cap position under both Green branches, 2026-27 to 2028-29.

R3 branches:
  A  TRADE   Green traded as a pure salary dump, nothing back. $14,679,012 leaves the
             books outright in 2026-27 and there is no future charge.
  B  STRETCH Green waived and stretched. One year remaining stretches over
             (2 x 1) + 1 = 3 seasons at $4,893,004 per season, charged to 2026-27,
             2027-28 and 2028-29.

Both branches put the same team on the floor, so the strength work runs once (see
build_rotations). Only the money forks, which is what this computes.

Everything downstream of 2026-27 is a projection: the league has set 2026-27 but not
2027-28 or 2028-29, so those thresholds are the constants file's forward scale and are
flagged as such.

    python kuminga/scripts/cap_branches.py
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
CONTRACTS = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27_verified.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "cap_branches.csv")
OUT_MD = os.path.join(REPO, "kuminga", "outputs", "cap_branches.md")

GREEN_SALARY = 14_679_012
GREEN_YEARS_LEFT = 1
SEASONS = ["2026-27", "2027-28", "2028-29"]


def stretch_schedule(salary: float, years_left: int) -> tuple[float, int]:
    n = 2 * years_left + 1
    return salary / n, n


UNLIKELY_BONUSES = 1_750_000.0   # McDaniels $1.0M + DiVincenzo $750k, 2026-27


def tax_bill(over: float, brackets: list) -> float:
    """Non-repeater luxury tax, marginal brackets. Approximate: the constants file
    flags the exact rates as CONFIRM."""
    if over <= 0:
        return 0.0
    bill, prev = 0.0, 0.0
    for b in brackets:
        cap_ = b["over_by_max"]
        hi = over if cap_ is None else min(over, cap_)
        if hi > prev:
            bill += (hi - prev) * b["rate"]
            prev = hi
        if cap_ is not None and over <= cap_:
            break
    return bill


def main():
    with runlog.run("cap_branches", inputs={"contracts": CONTRACTS, "branches": ["trade", "stretch"]}) as r:
        const = json.load(open(CONST, encoding="utf-8"))["seasons"]
        ct = pd.read_csv(CONTRACTS)
        mn = ct[ct.team_abbr == "MIN"].copy()

        per_season, dead = stretch_schedule(GREEN_SALARY, GREEN_YEARS_LEFT)
        r.note(f"Green stretch: ${GREEN_SALARY:,} over {dead} seasons = ${per_season:,.0f}/yr")

        c26 = const["2026-27"]
        stretch_ceiling = 0.15 * c26["salary_cap"]
        r.note(f"stretch ceiling (15% of the 2026-27 cap): ${stretch_ceiling:,.0f}; "
               f"this stretch uses ${per_season:,.0f} of it "
               f"({per_season/stretch_ceiling*100:.1f}%)")

        rows = []
        for season in SEASONS:
            k = const[season]
            col = "salary_" + season.replace("-", "_")
            if col not in mn.columns:
                r.note(f"{season}: no salary column in the contract file, skipped")
                continue
            committed = float(pd.to_numeric(mn[col], errors="coerce").fillna(0).sum())
            n_under = int((pd.to_numeric(mn[col], errors="coerce").fillna(0) > 0).sum())

            for branch, label in (("trade", "A: Green traded (pure dump)"),
                                  ("stretch", "B: Green waived + stretched")):
                if season == "2026-27":
                    # APRON basis: unlikely bonuses count toward the apron even though
                    # they are excluded from cap and tax salary. Omitting them is what
                    # produced the 8x error in the published lede.
                    base = committed + UNLIKELY_BONUSES - GREEN_SALARY
                    extra = per_season if branch == "stretch" else 0.0
                else:
                    base = committed
                    extra = per_season if branch == "stretch" else 0.0
                total = base + extra
                # R2: tax is charged on REGULAR team salary, so the unlikely bonuses
                # added above for the apron come back out for the tax calculation.
                tax_basis = total - (UNLIKELY_BONUSES if season == "2026-27" else 0.0)
                over_tax = tax_basis - k["luxury_tax"]
                rows.append(dict(
                    season=season, branch=branch, branch_label=label,
                    is_projection=k["is_projection"],
                    committed_before_green=committed,
                    green_adjustment=(-GREEN_SALARY if season == "2026-27" else 0.0),
                    dead_money=extra,
                    team_salary=total,
                    n_under_contract=n_under,
                    salary_cap=k["salary_cap"], luxury_tax=k["luxury_tax"],
                    first_apron=k["first_apron"], second_apron=k["second_apron"],
                    dist_to_tax=k["luxury_tax"] - total,
                    dist_to_apron1=k["first_apron"] - total,
                    dist_to_apron2=k["second_apron"] - total,
                    over_tax_by=max(over_tax, 0.0),
                    est_tax_bill=tax_bill(over_tax, k["tax_brackets_nonrepeater_approx"]),
                    taxpayer_mle=k["taxpayer_mle"],
                ))

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)

        for _, x in df[df.season == "2026-27"].iterrows():
            r.note(f"2026-27 [{x.branch}]: ${x.team_salary:,.0f} | to apron1 "
                   f"${x.dist_to_apron1:,.0f} | to apron2 ${x.dist_to_apron2:,.0f} | "
                   f"tax bill ~${x.est_tax_bill/1e6:.1f}M")

        # ---- the 14th and 15th man math ----------------------------------------
        min_scale = c26["min_salary_by_yos"]
        rookie_min = min_scale["0"]
        vet_min = min_scale["10+"]
        lines = []
        for _, x in df[df.season == "2026-27"].iterrows():
            room = x.dist_to_apron2
            lines.append(dict(branch=x.branch,
                              room_under_apron2=room,
                              can_add_rookie_min=room >= rookie_min,
                              n_rookie_min_slots=int(room // rookie_min),
                              can_add_vet_min=room >= vet_min))
            r.note(f"14th/15th man [{x.branch}]: ${room:,.0f} under the second apron = "
                   f"{int(room // rookie_min)} more rookie-minimum bodies "
                   f"(${rookie_min:,} each)")

        # ---- the calendar the money lands on ------------------------------------
        notes = [
            f"Gobert's 2027-28 season is a ${38_000_000:,} PLAYER option, not a team "
            "option. The 2027-28 stretch charge lands in the same season he can choose "
            "to opt in, so Minnesota does not control both sides of that year.",
            "Edwards is signed through 2028-29 at $48,924,624 / $52,298,736 / "
            "$55,672,848 and becomes an unrestricted free agent after it. He was NOT "
            "supermax-eligible in 2026 (six years of service, one short, and he missed "
            "the 65-game threshold at 61 games so no All-NBA trigger). First eligible "
            "in the 2027 offseason, and only with a 2026-27 performance trigger.",
            "So under branch B the third stretch year (2028-29) sits in Edwards's walk "
            "year, alongside whatever an extension costs. That is the year the branch "
            "choice actually bites.",
            "2027-28 and 2028-29 thresholds are the constants file's forward scale, "
            "not league-set figures. Treat distances in those seasons as directional.",

            "REPEATER TRIGGER. Minnesota is NOT a repeater in 2026-27: it paid the tax "
            "in 2024-25 and 2025-26 but not in 2022-23 or 2023-24, which is two of the "
            "last four against a three-of-four rule. But BOTH branches pay the tax in "
            "2026-27, which makes it three of the last four and turns Minnesota into a "
            "REPEATER in 2027-28. The tax bills above use non-repeater rates, so they "
            "are a floor for any future season, not a forecast. The constants file "
            "also flags the exact bracket rates as needing a primary-source check.",

            "OUT-YEAR TOTALS ARE COMMITTED SALARY, NOT A ROSTER. The 2027-28 and "
            "2028-29 figures count only players already under contract (nine and seven "
            "respectively), so they sit far below the tax line purely because the "
            "roster is not filled yet. They are not a projection that Minnesota escapes "
            "the tax; they are the floor those seasons start from. The stretch charge, "
            "by contrast, IS fully known in both of those years.",
        ]
        for n in notes:
            r.note("NOTE: " + n)

        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write("# Cap position by Green branch\n\n")
            fh.write(f"Green stretch schedule: ${GREEN_SALARY:,} over {dead} seasons "
                     f"= ${per_season:,.0f} per season.\n\n")
            fh.write(f"Stretch ceiling (15% of the 2026-27 cap): ${stretch_ceiling:,.0f}. "
                     f"This uses {per_season/stretch_ceiling*100:.1f}% of it.\n\n")
            fh.write(df.to_markdown(index=False, floatfmt=",.0f"))
            fh.write("\n\n## The 14th and 15th man\n\n")
            fh.write(pd.DataFrame(lines).to_markdown(index=False, floatfmt=",.0f"))
            fh.write("\n\n## Notes\n\n")
            for n in notes:
                fh.write(f"- {n}\n")

        r.output(OUT, rows=len(df))
        r.output(OUT_MD)

    print()
    print(df[["season", "branch", "team_salary", "dist_to_apron1", "dist_to_apron2",
              "est_tax_bill", "is_projection"]].to_string(index=False,
                                                          formatters={
                                                              "team_salary": "{:,.0f}".format,
                                                              "dist_to_apron1": "{:,.0f}".format,
                                                              "dist_to_apron2": "{:,.0f}".format,
                                                              "est_tax_bill": "{:,.0f}".format}))


if __name__ == "__main__":
    main()
