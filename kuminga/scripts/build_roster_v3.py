#!/usr/bin/env python3
"""roster_snapshot_2026_27 v3: post-Green-trade, with Spotrac's apron anchors parsed.

WHY v3 EXISTS. v2 was scraped 2026-08-27. On 2026-08-29 Minnesota traded Josh Green,
so v2's Minnesota is stale, and a table with one team refreshed and twenty-nine frozen
is worse than either. All 30 pages were re-pulled on 2026-09-03.

WHAT IS NEW BESIDES THE DATE. v2's dollar gate compared against
`offseason/data/spotrac_apron_2026_27.csv`, a HAND-TRANSCRIBED file. A typo there would
have looked exactly like a roster defect. v3 parses Spotrac's own published figures
straight off each team page instead:

    1st Apron Space   -> implies their Apron Team Salary as (first apron  - space)
    2nd Apron Space   -> implies their Apron Team Salary as (second apron - space)

Those two are independent of each other, so they cross-check Spotrac as well as us, and
the transcription step leaves the chain entirely.

v2 is NOT overwritten. It stays as the record of what the G4 gates actually ran against.

    python kuminga/scripts/build_roster_v3.py <dir-of-30-team-pages>
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

from kuminga.lib import runlog          # noqa: E402
from build_roster_v2 import parse, SLUG  # noqa: E402

SRC_DIR = sys.argv[1] if len(sys.argv) > 1 else None
OUT = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_v3.csv")
OUT_ANCH = os.path.join(REPO, "kuminga", "data", "spotrac_anchors_2026_27_v3.csv")
CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")

ANCHORS = (("1st Apron Space", "first_apron_space"),
           ("2nd Apron Space", "second_apron_space"),
           ("Total Cap Allocations", "total_allocations"),
           ("Cap Space", "cap_space"))


def money(s):
    m = re.search(r"\$(-?[\d,]+)", s or "")
    return float(m.group(1).replace(",", "")) if m else None


def anchors(txt):
    out = {}
    for label, key in ANCHORS:
        m = re.search(r"#####\s*" + re.escape(label) + r"\s*\n+\s*(\$-?[\d,]+)", txt)
        out[key] = money(m.group(1)) if m else None

    # Spotrac's own itemised breakdown, at the foot of every page. This is what makes
    # the dollar gate meaningful: it splits their total into Active Roster and Dead
    # Money, the two components we build per player and can therefore actually be
    # tested on, leaving unlikely bonuses as the residual.
    blk = txt[txt.find("## 2026 Cap Totals"):]
    for label, key in (("Active Roster", "blk_active"), ("Dead Money", "blk_dead"),
                       ("Cap Hold", "blk_hold")):
        m = re.search(re.escape(label) + r"\s*(\$-?[\d,]+)", blk)
        out[key] = money(m.group(1)) if m else 0.0
    m = re.search(r"1st Apron Summary.*?\n\s*Total Allocations\s*(\$-?[\d,]+)",
                  blk, re.S)
    out["blk_apron"] = money(m.group(1)) if m else None
    return out


def main():
    assert SRC_DIR and os.path.isdir(SRC_DIR), "pass the directory of team pages"
    with runlog.run("build_roster_v3", inputs={"dir": SRC_DIR,
                                               "source": "spotrac team cap pages"}) as r:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        k = json.load(open(CONST, encoding="utf-8"))["seasons"]["2026-27"]
        ap1, ap2 = float(k["first_apron"]), float(k["second_apron"])

        files = sorted(glob.glob(os.path.join(SRC_DIR, "*.md")))
        r.note("parsing %d team pages" % len(files))
        all_rows, hdr, anch = [], {}, []
        for f in files:
            ab = os.path.basename(f)[:-3]
            SLUG[ab] = ("https://www.spotrac.com/nba/.../cap/_/year/2026 (fetched %s)"
                        % stamp[:10])
            txt = open(f, encoding="utf-8", errors="replace").read()
            # as_of is the SCRAPE time, not the parse time. Using the parse time made
            # the snapshot's sha256 change on every re-run of identical inputs, which
            # defeats content-addressing: the hash has to be a function of the content.
            scraped = datetime.fromtimestamp(os.path.getmtime(f), timezone.utc)
            rows, counts = parse(f, ab, scraped.strftime("%Y-%m-%dT%H:%M:%SZ"))
            if not rows:
                r.note("  %s: NO ROWS PARSED" % ab)
            all_rows += rows
            if counts:
                hdr[ab] = counts
            a = anchors(txt)
            a["team_abbr"] = ab
            a["implied_from_ap1"] = (ap1 - a["first_apron_space"]
                                     if a["first_apron_space"] is not None else None)
            a["implied_from_ap2"] = (ap2 - a["second_apron_space"]
                                     if a["second_apron_space"] is not None else None)
            a["header_standard"] = counts[0] if counts else None
            a["header_two_way"] = counts[1] if counts else None
            anch.append(a)

        d = pd.DataFrame(all_rows)
        assert len(d), "nothing parsed"
        an = pd.DataFrame(anch)
        r.note("parsed %d rows across %d teams" % (len(d), d.team_abbr.nunique()))
        r.note("  by status: " + ", ".join("%s=%d" % (kk, vv)
                                           for kk, vv in d.status.value_counts().items()))

        # Spotrac's two anchors must agree with EACH OTHER before we compare to them.
        an["anchor_spread"] = (an.implied_from_ap1 - an.implied_from_ap2).abs()
        bad_anchor = an[an.anchor_spread > 1.0]
        if len(bad_anchor):
            r.note("  SPOTRAC SELF-INCONSISTENT on %d teams: %s"
                   % (len(bad_anchor), ", ".join(
                       "%s spread %s" % (x.team_abbr, format(x.anchor_spread, ",.0f"))
                       for _, x in bad_anchor.iterrows())))
        else:
            r.note("  Spotrac's 1st- and 2nd-apron anchors agree with each other on "
                   "all %d teams" % len(an))

        chk = d[d.status.isin(["standard", "non_guaranteed"])].groupby("team_abbr").size()
        mism = [(t, int(chk.get(t, 0)), c[0]) for t, c in hdr.items()
                if int(chk.get(t, 0)) != c[0]]
        if mism:
            r.note("  PARSE MISMATCH vs Spotrac's own header, %d teams: " % len(mism)
                   + ", ".join("%s parsed %d vs header %d" % m for m in mism))
        else:
            r.note("  parsed standard counts match Spotrac's header on all teams")

        d.to_csv(OUT, index=False)
        an.to_csv(OUT_ANCH, index=False)
        h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
        open(OUT.replace(".csv", ".sha256"), "w").write(h + "\n")
        r.note("FROZEN: %s" % os.path.relpath(OUT, REPO))
        r.note("  sha256 %s" % h)

        mn = d[d.team_abbr == "MIN"]
        cm = mn[mn.status.isin(["standard", "non_guaranteed", "dead_money"])]
        r.note("MIN: %d standard, apron %s"
               % (int(mn.status.isin(["standard", "non_guaranteed"]).sum()),
                  format(cm.cap_hit_2026_27.sum() + cm.incentives_unlikely.sum(), ",.0f")))
        r.output(OUT, rows=len(d))
        r.output(OUT_ANCH, rows=len(an))

    print()
    print(d.status.value_counts().to_string())


if __name__ == "__main__":
    main()
