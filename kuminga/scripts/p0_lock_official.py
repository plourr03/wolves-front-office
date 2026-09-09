#!/usr/bin/env python3
"""P0 (lock step L2): the Kuminga signing is official. Promote every pending row.

WHAT CHANGED IN THE WORLD. Minnesota announced the signing themselves and Kuminga will
wear No. 24. Until now every row for him carried `reported_pending_official`, because
the deal was agreed on 2026-08-26 and could not be executed until Josh Green moved on
2026-08-29. It has now been executed and announced.

    https://timberwolves.com/news/timberwolves-sign-jonathan-kuminga   (team release)
    https://heavy.com/sports/nba/minnesota-timberwolves/jonathan-kuminga-timberwolves-signing-number-24/

WHAT DID NOT CHANGE, AND THIS IS THE POINT OF THE TAG. **The team release discloses no
terms.** So the dollars in this project remain REPORTED figures, not club-confirmed
ones, and promoting the status must not be allowed to launder them into facts. Every
row that carries a Kuminga dollar figure is tagged `terms_not_released_by_team`.

The year-one figure is nonetheless corroborated from outside the reporting: Spotrac
carried the contract at $6,064,000, which is the 2026-27 taxpayer mid-level exception to
the dollar, and $6,064,000 plus the maximum 5% raise gives $12,431,200, which is the
widely reported "two years, $12.4 million". Two outlets carry roughly $13.0M instead.
That difference is $568,800, it changes no legality question under any branch, and it is
flagged rather than resolved.

    python kuminga/scripts/p0_lock_official.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

DATA = os.path.join(REPO, "kuminga", "data")
TARGETS = ["transaction_supplement.csv", "roster_snapshot_2026_27.csv",
           "roster_snapshot_2026_27_SIM.csv"]
OLD, NEW = "reported_pending_official", "official"
TAG = "terms_not_released_by_team"
ANNOUNCED = "2026-09-09"
SOURCES = ["https://timberwolves.com/news/timberwolves-sign-jonathan-kuminga",
           "https://heavy.com/sports/nba/minnesota-timberwolves/"
           "jonathan-kuminga-timberwolves-signing-number-24/"]


def main():
    with runlog.run("p0_lock_official",
                    inputs={"announced": ANNOUNCED, "sources": SOURCES}) as r:
        total = 0
        for fn in TARGETS:
            p = os.path.join(DATA, fn)
            if not os.path.exists(p):
                r.note("  %s: not present, skipped" % fn)
                continue
            d = pd.read_csv(p)
            if "status" not in d.columns:
                r.note("  %s: no status column, skipped" % fn)
                continue
            hit = (d.status.astype(str) == OLD)
            n = int(hit.sum())
            if n:
                d.loc[hit, "status"] = NEW
                # The tag rides with the row, not with a comment somewhere else, so a
                # consumer of the CSV cannot pick up the dollars without it.
                if "terms_status" not in d.columns:
                    d["terms_status"] = ""
                d.loc[hit, "terms_status"] = TAG
                if "official_announced" not in d.columns:
                    d["official_announced"] = ""
                d.loc[hit, "official_announced"] = ANNOUNCED
                d.to_csv(p, index=False)
            r.note("  %-38s %d row(s) promoted to '%s'" % (fn, n, NEW))
            total += n

        r.note("")
        r.note("promoted %d rows in total" % total)
        r.note("DOLLARS ARE STILL REPORTED, NOT CLUB-CONFIRMED. The team release "
               "discloses no terms, so every promoted row carries "
               "terms_status='%s'." % TAG)
        r.note("  corroboration that survives the missing release: Spotrac carried "
               "year one at $6,064,000, which is the taxpayer MLE exactly; "
               "$6,064,000 + 5% = $12,431,200 = the reported '$12.4M'.")
        r.note("  unresolved: two outlets report roughly $13.0M, a $568,800 "
               "difference. Flagged, not resolved. It changes no legality question.")
        for s in SOURCES:
            r.note("  source: %s" % s)

        left = 0
        for fn in TARGETS:
            p = os.path.join(DATA, fn)
            if os.path.exists(p):
                d = pd.read_csv(p)
                if "status" in d.columns:
                    left += int((d.status.astype(str) == OLD).sum())
        r.note("rows still pending after the promotion: %d" % left)
        assert left == 0, "some rows were not promoted"

    print("P0 complete: %d rows promoted, 0 left pending" % total)


if __name__ == "__main__":
    main()
