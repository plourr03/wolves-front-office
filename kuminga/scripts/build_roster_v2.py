#!/usr/bin/env python3
"""G4 rebuild: roster_snapshot_2026_27 v2, built from Spotrac team cap pages.

WHY v1 FAILED, corrected from the first diagnosis. The original read was that our book
had players on the wrong teams. It does not. Spotrac agrees James Harden is on
Cleveland and Giannis Antetokounmpo is on Miami. The real defects are two rules we
never modelled:

  PENDING TRANSACTIONS. Spotrac lists reported-but-unofficial moves in their own section
  and EXCLUDES them from team totals. Our book folded them into the roster at full
  value. Kuminga on Minnesota is one of these, and so are Harden on Cleveland and
  Giannis on Miami.

  DEAD MONEY. Waived players still count against the team that waived them. Spotrac
  carries them; our book largely did not. Phoenix's entire $19,383,010 discrepancy is
  Bradley Beal's waived salary, and Milwaukee's is mostly Damian Lillard's $21,311,053.

Both are membership rules, not roster errors, which is why the league aggregate was
within 0.63% while individual teams were tens of millions apart.

SECTIONS PARSED, in the order Spotrac emits them:
  "## 2026-27 Pending Transactions Cap"  -> status pending, EXCLUDED from totals
  "## 2026-27 Active Roster Cap"         -> status standard (or non_guaranteed)
  "## 2026-27 Dead Money Cap"            -> status dead_money, INCLUDED in totals
  "## 2026-27 Cap Hold Cap"              -> cap holds, excluded from the APRON basis

Columns: Player | Pos | Age | Type | Cap Hit | Pct | Base | Incentives Likely |
         Incentives Unlikely | Trade Bonus Proration | Guaranteed

    python kuminga/scripts/build_roster_v2.py
"""
from __future__ import annotations

import glob
import hashlib
import os
import re
import sys
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

SRC_DIR = sys.argv[1] if len(sys.argv) > 1 else None
OUT = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_v2.csv")
SLUG = {}

SECT = {
    "Pending Transactions": "pending",
    "Active Roster": "standard",
    "Dead Money": "dead_money",
    "Cap Hold": "cap_hold",
}
# A single rigid regex drops any row with empty cells, which is exactly what dead-money
# and waived rows look like (no position, no age, no type). Split on pipes instead and
# read positionally, tolerating short rows.
PLAYER_CELL = re.compile(r"\[([^\]]+)\]\((https://www\.spotrac\.com/nba/player/[^)]+)\)")


def split_row(line):
    if not line.startswith("|"):
        return None
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 5:
        return None
    m = PLAYER_CELL.search(cells[0])
    if not m:
        return None
    return m, cells


def num(s):
    s = (s or "").strip().replace("$", "").replace(",", "").strip()
    if s in ("", "-"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse(path, abbr, stamp):
    txt = open(path, encoding="utf-8", errors="replace").read()
    # split the page into the named cap sections, in document order
    # " Cap" is OPTIONAL: Memphis emits "## 2026-27 Active Roster" with no suffix, which
    # silently parsed to zero rows for that team.
    marks = [(m.start(), m.group(1))
             for m in re.finditer(r"^## 2026-27 ([A-Za-z ]+?)(?: Cap)?\s*$", txt, re.M)]
    if not marks:
        return [], None
    marks.append((len(txt), "END"))
    rows = []
    for i in range(len(marks) - 1):
        s0, name = marks[i]
        s1 = marks[i + 1][0]
        status = SECT.get(name.strip())
        if status is None:
            continue
        for line in txt[s0:s1].splitlines():
            got = split_row(line)
            if not got:
                continue
            m, c = got
            player, url = m.group(1).strip(), m.group(2)
            if player.lower() in ("player",):
                continue
            g = lambda i: c[i] if i < len(c) else ""
            flags = c[0]
            pos, age, ctype = g(1), g(2), g(3)
            cap_hit, base = g(4), g(6)
            lik, unlik, tbp, gtd = g(7), g(8), g(9), g(10)
            st = status
            if status == "standard" and "WAIVED" in flags.upper():
                st = "dead_money"
            elif status == "standard" and num(gtd) and num(gtd) < num(cap_hit) - 1:
                st = "non_guaranteed"
            rows.append(dict(
                as_of=stamp, season="2026-27", team_abbr=abbr,
                player_name=player, status=st, position=pos or None,
                age=int(age) if age.isdigit() else None, contract_type=ctype or None,
                cap_hit_2026_27=num(cap_hit), base_salary=num(base),
                incentives_likely=num(lik), incentives_unlikely=num(unlik),
                trade_bonus_proration=num(tbp), guaranteed=num(gtd),
                source_url=SLUG.get(abbr, ""), spotrac_player_url=url))
    # FALLBACK LAYOUT. Memphis is served a 3-column render ("| RK | Player | CAP HIT |")
    # with the position and age inline and NO incentives columns at all. Parse it so the
    # team is not silently absent, but mark incentives UNKNOWN rather than zero, so Gate B
    # flags Memphis instead of passing it on a false $0.
    if not rows:
        alt = re.compile(r"^\|\s*\d+\s*\|\s*\[([^\]]+)\]\((https://www\.spotrac\.com/nba/player/[^)]+)\)"
                         r"\s*\(([A-Z]{1,2}),\s*(\d+)\)\s*\|\s*\$?([\d,]+)\s*\|", re.M)
        for m in alt.finditer(txt):
            nm, url, pos, age, hit = m.groups()
            rows.append(dict(
                as_of=stamp, season="2026-27", team_abbr=abbr,
                player_name=nm.strip(), status="standard", position=pos,
                age=int(age), contract_type=None, cap_hit_2026_27=num(hit),
                base_salary=num(hit), incentives_likely=float("nan"),
                incentives_unlikely=float("nan"), trade_bonus_proration=0.0,
                guaranteed=float("nan"), source_url=SLUG.get(abbr, ""),
                spotrac_player_url=url))
        if rows:
            rows[0]["contract_type"] = "ALT_LAYOUT_incentives_unknown"

    hdr = re.search(r"\| Player \((\d+) of 15 \+ (\d+) of 3 TW\)", txt)
    counts = (int(hdr.group(1)), int(hdr.group(2))) if hdr else None
    return rows, counts


def main():
    with runlog.run("build_roster_v2", inputs={"source": "spotrac team cap pages",
                                               "dir": SRC_DIR}) as r:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        files = sorted(glob.glob(os.path.join(SRC_DIR, "*.md")))
        r.note(f"parsing {len(files)} team pages")
        all_rows, hdr_counts = [], {}
        for f in files:
            ab = os.path.basename(f)[:-3]
            SLUG[ab] = (f"https://www.spotrac.com/nba/.../cap/_/year/2026 "
                        f"(fetched {stamp[:10]})")
            rows, counts = parse(f, ab, stamp)
            if not rows:
                r.note(f"  {ab}: NO ROWS PARSED")
            all_rows += rows
            if counts:
                hdr_counts[ab] = counts
        d = pd.DataFrame(all_rows)
        assert len(d), "nothing parsed"
        r.note(f"parsed {len(d)} rows across {d.team_abbr.nunique()} teams")
        r.note("  by status: " + ", ".join(f"{k}={v}"
                                           for k, v in d.status.value_counts().items()))

        # cross-check the parse against Spotrac's own header count
        chk = d[d.status.isin(["standard", "non_guaranteed"])].groupby("team_abbr").size()
        bad = [(t, int(chk.get(t, 0)), c[0]) for t, c in hdr_counts.items()
               if int(chk.get(t, 0)) != c[0]]
        if bad:
            r.note(f"  PARSE MISMATCH vs Spotrac's own header count, {len(bad)} teams: "
                   + ", ".join(f"{t} parsed {p} vs header {h}" for t, p, h in bad))
        else:
            r.note("  parsed standard counts match Spotrac's header on all teams")

        d.to_csv(OUT, index=False)
        h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
        r.note(f"FROZEN: {os.path.relpath(OUT, REPO)}")
        r.note(f"  sha256 {h}")
        with open(OUT.replace(".csv", ".sha256"), "w") as fh:
            fh.write(h + "\n")
        r.output(OUT, rows=len(d))
    print()
    print(d.status.value_counts().to_string())


if __name__ == "__main__":
    main()
