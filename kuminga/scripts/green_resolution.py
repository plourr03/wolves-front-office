#!/usr/bin/env python3
"""The Green branch resolved: Minnesota traded him, and the cap chain re-derives.

WHAT ACTUALLY HAPPENED, against every branch this project priced. On Saturday
2026-08-29 Minnesota sent Josh Green ($14,679,012, expiring) and cash to Utah for
Cody Williams ($6,015,600) and John Konchar ($6,165,000), then waived Konchar the
same day and stretched him to $2,055,000 across three seasons. NO DRAFT PICK AND NO
SWAP CHANGED HANDS. Every branch we priced assumed the dump would cost an asset; it
did not, and Minnesota took back a former No. 10 pick on a rookie deal as part of it.

WHY THE SAME DAY. A waived player must clear waivers (48 hours) by August 31 for the
stretch to apply to the current season, so the Saturday was the last day to do it.
Hoops Rumors states flatly, that day: "Today is the deadline to waive and stretch
contracts ahead of the upcoming season." The trade and the waiver had to be same-day.
The 48-hour mechanism is this project's INFERENCE for why Aug 29 rather than Aug 31;
the deadline itself is sourced. Flagged as an inference in decisions.md.

THE RECONCILIATION. Spotrac publishes two apron figures for every team, and they are
independent of each other and of us: 1st Apron Space and 2nd Apron Space. Our Apron
Team Salary must sit the right distance from BOTH lines. That is the external check
the must-not-change list now requires, and it is the check that failed silently for
weeks when we were carrying contracted salary alone.

    python kuminga/scripts/green_resolution.py <refreshed_MIN.md>
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

from kuminga.lib import runlog           # noqa: E402
from build_roster_v2 import parse, SLUG   # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 else None
CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")
FROZEN = os.path.join(REPO, "kuminga", "data", "frozen", "spotrac_min_post_trade")
OUT = os.path.join(REPO, "kuminga", "outputs", "green_resolution.csv")
OUT_MD = os.path.join(REPO, "kuminga", "outputs", "green_resolution.md")
CANON = os.path.join(REPO, "kuminga", "outputs", "cap_canonical.json")
TOL = 2_000.0

KUMINGA_Y1 = 6_064_000.0        # taxpayer MLE 2026-27, Spotrac pending row
KUMINGA_Y2 = 6_367_200.0        # 5% raise; 12,431,200 total = the reported "$12.4M"

GREEN_OUT = 14_679_012.0
WILLIAMS_IN = 6_015_600.0
KONCHAR_IN = 6_165_000.0
KONCHAR_STRETCH = 2_055_000.0
STRETCH_YEARS = 3

# Two source URLs per transaction fact, per R8.
SOURCES = [
    "https://www.hoopsrumors.com/2026/08/timberwolves-to-trade-josh-green-to-jazz.html",
    "https://www.espn.com/nba/story/_/id/49759209/wolves-trade-3-d-wing-josh-green-jazaz",
    "https://www.nba.com/news/jazz-trade-cody-williams-john-konchar-to-timberwolves-for-josh-green",
    "https://www.hoopsrumors.com/2026/08/timberwolves-waive-john-konchar.html",
]
TRADE_DATE = "2026-08-29"


def money(s):
    m = re.search(r"\$(-?[\d,]+)", s or "")
    return float(m.group(1).replace(",", "")) if m else None


def spotrac_anchors(txt):
    """Spotrac's own published figures, each an independent external anchor."""
    out = {}
    for label, key in (("1st Apron Space", "sp_first_apron_space"),
                       ("2nd Apron Space", "sp_second_apron_space"),
                       ("Total Cap Allocations", "sp_total_allocations")):
        m = re.search(r"#####\s*" + re.escape(label) + r"\s*\n+\s*(\$-?[\d,]+)", txt)
        out[key] = money(m.group(1)) if m else None
    return out


def main():
    assert SRC and os.path.exists(SRC), "pass the refreshed Spotrac MIN page"
    with runlog.run("green_resolution",
                    inputs={"source": SRC, "trade_date": TRADE_DATE}) as r:
        raw = open(SRC, encoding="utf-8", errors="replace").read()
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # ---- freeze the source, content-addressed --------------------------
        os.makedirs(FROZEN, exist_ok=True)
        h = hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()
        dest = os.path.join(FROZEN, "MIN_" + h[:16] + ".md")
        shutil.copyfile(SRC, dest)
        with open(os.path.join(FROZEN, "CURRENT"), "w") as fh:
            fh.write(os.path.basename(dest) + "\n" + h + "\n" + stamp + "\n")
        r.note("froze source -> " + os.path.relpath(dest, REPO)
               + " (sha256 " + h[:16] + "...)")

        k = json.load(open(CONST, encoding="utf-8"))["seasons"]["2026-27"]
        ap1, ap2 = float(k["first_apron"]), float(k["second_apron"])
        tax = float(k["luxury_tax"])

        SLUG["MIN"] = "https://www.spotrac.com/nba/minnesota-timberwolves/cap/_/year/2026"
        rows, counts = parse(SRC, "MIN", stamp)
        d = pd.DataFrame(rows)
        counted = d[d.status.isin(["standard", "non_guaranteed", "dead_money"])]
        n_std = int(d.status.isin(["standard", "non_guaranteed"]).sum())
        apron_now = float(counted.cap_hit_2026_27.sum()
                          + counted.incentives_unlikely.sum())

        r.note("post-trade roster parsed: %d standard (Spotrac header says %s), "
               "%d dead-money, %d pending"
               % (n_std, counts[0] if counts else "?",
                  int((d.status == "dead_money").sum()),
                  int((d.status == "pending").sum())))
        assert "Josh Green" not in set(d.player_name), "Green still on the book"
        assert "Cody Williams" in set(d.player_name), "Williams missing"

        # ---- EXTERNAL RECONCILIATION, two independent anchors --------------
        a = spotrac_anchors(raw)
        implied_ap1 = ap1 - a["sp_first_apron_space"]
        implied_ap2 = ap2 - a["sp_second_apron_space"]
        r.note("")
        r.note("EXTERNAL RECONCILIATION (Spotrac's own published apron spaces):")
        r.note("  ours, Apron Team Salary          ${:,.0f}".format(apron_now))
        r.note("  implied by their 1st-apron space ${:,.0f} (diff {:+,.0f})".format(
            implied_ap1, apron_now - implied_ap1))
        r.note("  implied by their 2nd-apron space ${:,.0f} (diff {:+,.0f})".format(
            implied_ap2, apron_now - implied_ap2))
        ok1 = abs(apron_now - implied_ap1) <= TOL
        ok2 = abs(apron_now - implied_ap2) <= TOL
        r.note("  the two anchors agree with each other: {}".format(
            abs(implied_ap1 - implied_ap2) <= 1.0))
        assert ok1 and ok2, "post-trade apron does not reconcile to Spotrac"
        r.note("  BOTH ANCHORS CLEAR. The apron basis is externally confirmed.")

        # ---- the chain ------------------------------------------------------
        with_k = apron_now + KUMINGA_Y1
        pre = json.load(open(CANON, encoding="utf-8"))
        pre_apron = float(pre["pre_kuminga_apron"])
        delta = apron_now - pre_apron
        stretch_credit = KONCHAR_IN - KONCHAR_STRETCH

        chain = [
            ("pre-trade Apron Team Salary (2026-08-27)", pre_apron),
            ("out: Josh Green", -GREEN_OUT),
            ("in: Cody Williams", WILLIAMS_IN),
            ("in: John Konchar", KONCHAR_IN),
            ("waive Konchar, stretch over 3 seasons", -stretch_credit),
            ("post-trade Apron Team Salary (%s)" % stamp[:10], apron_now),
            ("sign Kuminga, taxpayer MLE year 1", KUMINGA_Y1),
            ("final Apron Team Salary", with_k),
        ]
        r.note("")
        r.note("THE CAP CHAIN, post-trade:")
        for lab, v in chain:
            r.note("  {:48s} {:>16,.0f}".format(lab, v))

        r.note("")
        r.note("  the trade moved the apron by {:+,.0f}".format(delta))
        r.note("  room under the SECOND apron, pre-Kuminga  ${:,.0f} "
               "(Spotrac ${:,.0f})".format(ap2 - apron_now,
                                           a["sp_second_apron_space"]))
        r.note("  room under the SECOND apron, with Kuminga ${:,.0f}".format(
            ap2 - with_k))
        r.note("  vs the FIRST apron, with Kuminga          {:+,.0f} "
               "(positive = over)".format(with_k - ap1))
        r.note("")
        r.note("BEFORE the trade Minnesota could not sign him at all: with Kuminga "
               "on the books they were ${:,.0f} OVER the second-apron hard cap. They "
               "needed to shed $2.0M and shed ${:,.0f}.".format(
                   float(pre["overage_vs_second_apron"]), -delta))
        r.note("AFTER the trade they are a FIRST-APRON team, ${:,.0f} over that "
               "line, with ${:,.0f} of room beneath the hard cap.".format(
                   with_k - ap1, ap2 - with_k))

        # ---- what the dump actually cost ------------------------------------
        r.note("")
        r.note("ASSET COST OF THE DUMP (the lock addendum's open question, closed):")
        r.note("  draft picks attached: NONE. No pick, no swap, either direction.")
        r.note("  new dead money: $2,055,000 x 3 = $6,165,000, of which ${:,.0f} "
               "lands in 2027-28 and 2028-29, the two seasons the 2027 flex thesis "
               "depends on.".format(KONCHAR_STRETCH * 2))
        r.note("  asset RECEIVED: Cody Williams, No. 10 pick in 2024, rookie deal "
               "with a 2027-28 club option at $7,669,890.")
        r.note("  cash considerations changed hands; sources disagree on direction; "
               "cash does not count against team salary either way.")

        rowsout = [dict(step=lab, amount=v) for lab, v in chain]
        rowsout += [
            dict(step="room under second apron, pre-Kuminga", amount=ap2 - apron_now),
            dict(step="room under second apron, with Kuminga", amount=ap2 - with_k),
            dict(step="over first apron, with Kuminga", amount=with_k - ap1),
            dict(step="over tax line, with Kuminga", amount=with_k - tax),
            dict(step="dead money 2026-27", amount=KONCHAR_STRETCH),
            dict(step="dead money 2027-28", amount=KONCHAR_STRETCH),
            dict(step="dead money 2028-29", amount=KONCHAR_STRETCH),
        ]
        pd.DataFrame(rowsout).to_csv(OUT, index=False)

        canon = dict(pre)
        canon["post_trade"] = {
            "as_of": stamp[:10],
            "trade_date": TRADE_DATE,
            "basis": pre["basis"],
            "n_standard": n_std,
            "post_trade_apron": apron_now,
            "with_kuminga_apron": with_k,
            "kuminga_y1": KUMINGA_Y1,
            "kuminga_y2": KUMINGA_Y2,
            "room_under_second_apron_pre_kuminga": ap2 - apron_now,
            "room_under_second_apron_with_kuminga": ap2 - with_k,
            "over_first_apron_with_kuminga": with_k - ap1,
            "dead_money_2026_27": KONCHAR_STRETCH,
            "dead_money_2027_28": KONCHAR_STRETCH,
            "dead_money_2028_29": KONCHAR_STRETCH,
            "picks_attached": "none",
            "external_anchor_first_apron_space": a["sp_first_apron_space"],
            "external_anchor_second_apron_space": a["sp_second_apron_space"],
            "reconciles_both_anchors": bool(ok1 and ok2),
            "sources": SOURCES,
        }
        json.dump(canon, open(CANON, "w"), indent=1)
        r.note("cap_canonical.json updated with a post_trade block")

        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write("# The Green branch, resolved\n\n")
            fh.write("As of %s. Trade official %s.\n\n" % (stamp[:10], TRADE_DATE))
            fh.write("| step | amount |\n|---|---:|\n")
            for lab, v in chain:
                fh.write("| %s | %s |\n" % (lab, format(v, ",.0f")))
            fh.write("\n## External reconciliation\n\n")
            fh.write("- ours: $%s\n" % format(apron_now, ",.0f"))
            fh.write("- implied by Spotrac 1st-apron space: $%s\n"
                     % format(implied_ap1, ",.0f"))
            fh.write("- implied by Spotrac 2nd-apron space: $%s\n"
                     % format(implied_ap2, ",.0f"))
            fh.write("\n## Sources\n\n")
            for s in SOURCES:
                fh.write("- %s\n" % s)

        # L1c: build_final_numbers.py carries "PENDING GREEN RESOLUTION" on the sheet
        # until this file exists. Emitting it here is what closes the hole, and it must
        # carry the sources because R8 requires two URLs per transaction fact.
        AC = os.path.join(REPO, "kuminga", "outputs", "green_asset_cost.csv")
        pd.DataFrame([dict(
            cost="no draft pick and no swap, either direction",
            detail=("cash considerations (direction disputed), plus $2,055,000 a year "
                    "of Konchar dead money for three seasons ($4,110,000 of it in "
                    "2027-28 and 2028-29). Minnesota RECEIVED Cody Williams, the No. 10 "
                    "pick in 2024, on a rookie deal with a 2027-28 club option at "
                    "$7,669,890."),
            picks_attached="none",
            dead_money_total=KONCHAR_STRETCH * STRETCH_YEARS,
            dead_money_future=KONCHAR_STRETCH * 2,
            sources=" | ".join(SOURCES))]).to_csv(AC, index=False)
        r.note("wrote green_asset_cost.csv, which closes L1c on the final-numbers sheet")

        r.output(OUT, rows=len(rowsout))
        r.output(OUT_MD)
        r.output(AC, rows=1)
        r.output(CANON)

    print()
    print(pd.DataFrame(rowsout).to_string(index=False))


if __name__ == "__main__":
    main()
