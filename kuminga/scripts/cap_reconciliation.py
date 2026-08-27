#!/usr/bin/env python3
"""Cap reconciliation: one canonical pre-Kuminga apron figure, and the Green branches
restated on it with roster fill made explicit.

WHY THIS EXISTS. Two of our own numbers disagreed. Phase 0 reported Minnesota's
2026-27 book at $215,871,829 across 13 players; the first morning report said
$223,293,829. The gap is exactly $7,422,000 and it decomposes cleanly:

    $215,871,829   13 actual contracts from nba_player_contracts (Green in, Kuminga out)
    +  6,064,000   Jonathan Kuminga at the taxpayer MLE (reported, not yet official)
    +  1,358,000   the R4 "14th man" modelling placeholder
    = $223,293,829

WHAT COUNTS TOWARD THE APRON, AND WHAT DOES NOT

  COUNTS   contracted salary (guaranteed, plus options counted at value, plus
           non-guaranteed treated as guaranteed), dead money from waived players,
           and likely incentives.
  COUNTS   an INCOMPLETE ROSTER CHARGE, but only when a team is below TWELVE players:
           the rookie minimum is added for each slot short of 12, in the offseason
           only. Minnesota is at 13 contracts, so this charge is ZERO, and team_state
           agrees (incomplete_roster_charges = $0).
  DOES NOT free-agent cap holds. Those sit in the CAP basis, not the apron basis.
           Minnesota carries $16,484,548 of them, which is why its cap-basis figure
           ($239,778,377) is larger again and should never be quoted as an apron number.
  DOES NOT two-way contracts.
  DOES NOT a body the team has not signed yet.

So the R4 placeholder is NOT a CBA charge. It is a projection of a signing that has
not happened. It must not appear in an apron figure. It is still a real future cost,
because a team must carry 14 or 15 players in the regular season (a grace period
allows 12 or 13 for at most two consecutive weeks and 28 total days), so the roster
fill is shown as an explicit row instead of being buried in the total.

CANONICAL: apron team salary = contracted salary only.

    python kuminga/scripts/cap_reconciliation.py
"""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import kfreeze, runlog  # noqa: E402

CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")
SNAP = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27.csv")
TEAMSTATE = os.path.join(REPO, "offseason", "data", "team_state.csv")
OUT_REC = os.path.join(REPO, "kuminga", "outputs", "cap_reconciliation.csv")
OUT_BR = os.path.join(REPO, "kuminga", "outputs", "cap_branches_canonical.csv")
OUT_MD = os.path.join(REPO, "kuminga", "outputs", "cap_reconciliation.md")

GREEN = 14_679_012
KUMINGA = 6_064_000
STRETCH_YEARS = 3


def main():
    with runlog.run("cap_reconciliation", inputs={"basis": "contracted salary only"}) as r:
        k = json.load(open(CONST, encoding="utf-8"))["seasons"]["2026-27"]
        apron1, apron2, tax = k["first_apron"], k["second_apron"], k["luxury_tax"]
        rookie_min = k["min_salary_by_yos"]["0"]

        contracts, _ = kfreeze.load("contracts")
        raw = contracts[(contracts.team_abbr == "MIN") & (contracts.season == "2026-27")]
        base_13 = float(raw.salary.sum())
        n_13 = len(raw)

        ts = pd.read_csv(TEAMSTATE)
        t = ts[(ts.team_abbr == "MIN") & (ts.season == "2026-27")
               & (ts.scenario_id == "base")].iloc[0]

        rec = [
            dict(component="13 contracted players (nba_player_contracts, 2026-08-26)",
                 amount=base_13, counts_toward_apron=True,
                 note="Green in, Kuminga out. This is the Phase 0 A.11 figure."),
            dict(component="Jonathan Kuminga, taxpayer MLE",
                 amount=KUMINGA, counts_toward_apron=True,
                 note="Counts once signed. Status: reported, not officially announced."),
            dict(component="R4 14th-man placeholder",
                 amount=1_358_000, counts_toward_apron=False,
                 note="NOT a CBA charge. A team is charged for empty slots only below "
                      "TWELVE players; Minnesota is at 13. Shown separately as roster fill."),
            dict(component="incomplete roster charge",
                 amount=float(t.incomplete_roster_charges), counts_toward_apron=True,
                 note="Zero, correctly: the charge applies only below 12 players."),
            dict(component="dead money",
                 amount=float(t.dead_money), counts_toward_apron=True,
                 note="Zero on the current book. Non-zero only in the stretch branch."),
            dict(component="free-agent cap holds",
                 amount=float(t.cap_holds), counts_toward_apron=False,
                 note="CAP basis only. Never quote the cap-basis total as an apron figure."),
            dict(component="two-way contracts (Enrique Freeman)",
                 amount=0.0, counts_toward_apron=False,
                 note="Excluded from team salary."),
        ]
        rc = pd.DataFrame(rec)
        rc.to_csv(OUT_REC, index=False)

        canonical_pre = base_13
        canonical_with_k = base_13 + KUMINGA
        r.note(f"CANONICAL pre-Kuminga apron salary: ${canonical_pre:,.0f} ({n_13} contracts)")
        r.note(f"CANONICAL with Kuminga signed:      ${canonical_with_k:,.0f} (14 contracts)")
        gap = canonical_with_k - apron2
        side = "OVER" if gap > 0 else "under"
        r.note(f"  vs second apron ${apron2:,}: {side} by ${abs(gap):,.0f}")
        r.note(f"  previously reported as ${float(t.apron_team_salary):,.0f}, which "
               "included the placeholder; and the cap gate then added Kuminga a SECOND "
               "time, producing $229,357,829. Both corrected here.")

        # ---- Green branches, canonical basis, with roster fill explicit ----------
        rows = []
        for branch, label in (("trade", "A: Green traded (pure salary dump)"),
                              ("stretch", "B: Green waived and stretched")):
            after_green = base_13 - GREEN + KUMINGA          # 13 players
            dead = GREEN / STRETCH_YEARS if branch == "stretch" else 0.0
            for n_players in (13, 14, 15):
                fills = max(0, n_players - 13)
                total = after_green + dead + fills * rookie_min
                rows.append(dict(
                    branch=branch, branch_label=label, n_players=n_players,
                    contracted=after_green, dead_money=dead,
                    roster_fill=fills * rookie_min, apron_team_salary=total,
                    vs_first_apron=apron1 - total, vs_second_apron=apron2 - total,
                    under_first_apron=total <= apron1,
                    under_second_apron=total <= apron2,
                    legal_roster_size=n_players >= 14,
                ))
        br = pd.DataFrame(rows)
        br.to_csv(OUT_BR, index=False)

        for _, x in br.iterrows():
            r.note(f"[{x.branch:7s}] {x.n_players} players: ${x.apron_team_salary:,.0f} | "
                   f"first apron {'+' if x.vs_first_apron >= 0 else ''}{x.vs_first_apron:,.0f} | "
                   f"second apron +{x.vs_second_apron:,.0f}"
                   f"{'' if x.legal_roster_size else '  (below the 14-man season minimum)'}")

        legal_trade = br[(br.branch == "trade") & (br.n_players == 14)].iloc[0]
        room14 = legal_trade.vs_first_apron
        r.note(f"HEADLINE: at a legal 14-man roster the TRADE branch sits "
               f"${room14:,.0f} under the first apron. Any salary coming back in a "
               f"Green trade above ${room14:,.0f} crosses it, and the smallest possible "
               f"incoming contract is the rookie minimum ${rookie_min:,}, which is "
               f"{'MORE' if rookie_min > room14 else 'less'} than that room. So a Green "
               "trade that returns ANY player crosses the first apron.")
        legal_15 = br[(br.branch == "trade") & (br.n_players == 15)].iloc[0]
        r.note(f"And a 15th man pushes the trade branch ${-legal_15.vs_first_apron:,.0f} "
               "OVER the first apron by itself.")

        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write("# Cap reconciliation and the Green branches\n\n")
            fh.write("## Reconciling $215,871,829 against $223,293,829\n\n")
            fh.write(rc.to_markdown(index=False, floatfmt=",.0f"))
            fh.write(f"\n\n**Canonical pre-Kuminga apron salary: ${canonical_pre:,.0f}** "
                     f"({n_13} contracted players).\n\n")
            fh.write(f"**Canonical with Kuminga signed: ${canonical_with_k:,.0f}** "
                     f"(14 contracted players), which is "
                     f"${abs(canonical_with_k - apron2):,.0f} "
                     f"{'over' if canonical_with_k > apron2 else 'under'} the second apron "
                     f"of ${apron2:,}.\n\n")
            fh.write("## The Green branches, roster fill made explicit\n\n")
            fh.write(br[["branch", "n_players", "contracted", "dead_money", "roster_fill",
                         "apron_team_salary", "vs_first_apron", "vs_second_apron",
                         "legal_roster_size"]].to_markdown(index=False, floatfmt=",.0f"))
            fh.write("\n\nThresholds: first apron "
                     f"${apron1:,}, second apron ${apron2:,}, tax ${tax:,}, "
                     f"rookie minimum ${rookie_min:,}.\n")

        r.output(OUT_REC, rows=len(rc))
        r.output(OUT_BR, rows=len(br))
        r.output(OUT_MD)

    print()
    print(br[["branch", "n_players", "apron_team_salary", "vs_first_apron",
              "vs_second_apron", "under_first_apron", "legal_roster_size"]]
          .to_string(index=False, formatters={
              "apron_team_salary": "{:,.0f}".format,
              "vs_first_apron": "{:,.0f}".format,
              "vs_second_apron": "{:,.0f}".format}))


if __name__ == "__main__":
    main()
