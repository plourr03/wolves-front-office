#!/usr/bin/env python3
"""
pull_nba_draft_picks.py

Pulls the league-wide future draft-pick ledger from Spotrac into a CSV plus
a per-team JSON. This is the section 5.3 asset ledger: the hard gate for any
credible trade construction.

SOURCE: https://www.spotrac.com/nba/draft/future
The page is server-rendered. It is laid out as 30 team sections in fixed
order (Hawks -> Wizards), each with two draft-board grid tables: Round 1
first, then Round 2. So the 60 <table> elements pair up as
[team_0 R1, team_0 R2, team_1 R1, ...], which we assign by index and then
verify against the team name printed before each section.

Each grid places a pick under its projected slot via colspan, and carries
the protection / swap / chain detail in a small-font note div. We read the
PICK ORIGIN (the abbreviation shown), the colspan as a slot-span hint
(30 == whole round, i.e. unprotected or slot unknown), and the note
verbatim. The note is the load-bearing field: it states protections
("If 1-5"), swaps ("via X swap for Y"), and conveyance chains.

INTERPRETATION: a pick listed in a team's section is one that team currently
CONTROLS (its own picks plus picks acquired from others). A team's own picks
that it has traded away appear in the ACQUIRING team's section, not its own.
So this ledger answers "what can each team trade," which is what we need.

NOTE: this page covers 2027 onward. The 2026 first/second rounds are the
imminent draft (June 23-24) and live on the current-draft page; pull those
separately if needed. RealGM's equivalent pages are cleaner but hard-block
automated requests (403), so Spotrac is the practical source.

Run it in your environment (needs internet). No API key required.
    python pull_nba_draft_picks.py

Then validate constructed packages in a free trade machine (Fanspo) per the
plan; this ledger grounds the inputs, it does not check CBA legality.
"""

import os
import re
import csv
import sys
import json
import time
import html as ihtml

try:
    import requests
except ImportError:
    sys.exit("pip install requests")

URL = "https://www.spotrac.com/nba/draft/future"
HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(HERE, "..", "data")
CSV_PATH = os.path.join(OUTPUT_DIR, "nba_draft_picks_future.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "nba_draft_picks_future.json")

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Spotrac section order (document order) -> our standard abbreviation. The
# team name in the second column is what we verify each section against.
TEAM_ORDER = [
    ("ATL", "Hawks"), ("BOS", "Celtics"), ("BKN", "Nets"), ("CHA", "Hornets"),
    ("CHI", "Bulls"), ("CLE", "Cavaliers"), ("DAL", "Mavericks"),
    ("DEN", "Nuggets"), ("DET", "Pistons"), ("GSW", "Warriors"),
    ("HOU", "Rockets"), ("IND", "Pacers"), ("LAC", "Clippers"),
    ("LAL", "Lakers"), ("MEM", "Grizzlies"), ("MIA", "Heat"),
    ("MIL", "Bucks"), ("MIN", "Timberwolves"), ("NOP", "Pelicans"),
    ("NYK", "Knicks"), ("OKC", "Thunder"), ("ORL", "Magic"),
    ("PHI", "76ers"), ("PHX", "Suns"), ("POR", "Trail Blazers"),
    ("SAC", "Kings"), ("SAS", "Spurs"), ("TOR", "Raptors"),
    ("UTA", "Jazz"), ("WAS", "Wizards"),
]

FIELDNAMES = [
    "controlling_team", "round", "year",
    "pick_origin", "slot_span", "is_unprotected_or_unknown",
    "condition", "source", "last_verified",
]


def _text(fragment):
    """Strip tags, unescape entities, collapse whitespace."""
    return re.sub(r"\s+", " ", ihtml.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _split_tables(page):
    """Return the raw HTML of every <table>...</table> in document order."""
    return re.findall(r"<table.*?</table>", page, re.DOTALL)


def parse_table(tbl):
    """Parse one team-round grid into a list of pick dicts.

    Walks rows top to bottom, tracking the current year from year-label rows
    and skipping the slot-number rows. Every remaining cell that names a team
    becomes a pick entry.
    """
    picks = []
    current_year = None
    for tr in re.findall(r"<tr.*?</tr>", tbl, re.DOTALL):
        cells = re.findall(r"<t[dh][^>]*>.*?</t[dh]>", tr, re.DOTALL)
        parsed = []
        for cell in cells:
            cs = re.search(r'colspan="(\d+)"', cell)
            colspan = int(cs.group(1)) if cs else 1
            note_m = re.search(
                r'font-size:8px[^>]*>(.*?)</div>', cell, re.DOTALL
            )
            note = _text(note_m.group(1)) if note_m else ""
            body = cell
            if note_m:
                body = body.replace(note_m.group(0), "")
            parsed.append((_text(body), colspan, note))

        joined = " ".join(p[0] for p in parsed).strip()
        if re.fullmatch(r"(19|20)\d\d", joined):     # year-label row
            current_year = int(joined)
            continue
        if all(p[0] == "" or p[0].isdigit() for p in parsed):  # slot-number row
            continue

        for body, colspan, note in parsed:
            if body and not body.isdigit():
                picks.append({
                    "year": current_year,
                    "pick_origin": body,
                    "slot_span": colspan,
                    "condition": note,
                })
    return picks


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Fetching {URL} ...")
    resp = requests.get(URL, headers=HEADERS, timeout=40)
    resp.raise_for_status()
    page = resp.text

    tables = _split_tables(page)
    expected = len(TEAM_ORDER) * 2
    if len(tables) != expected:
        print(f"WARNING: found {len(tables)} tables, expected {expected} "
              f"(2 per team). Layout may have changed; verify output.")

    rows = []
    per_team = {}
    today = time.strftime("%Y-%m-%d")

    for i, tbl in enumerate(tables):
        abbr, name = TEAM_ORDER[i // 2]
        rnd = (i % 2) + 1

        # Sanity check on the R1 table for each team: its name should sit in
        # the HTML just before it. Skip team 0 (its gap is nav-polluted).
        if rnd == 1 and i > 0:
            gap = page[page.find(tables[i - 1]) + len(tables[i - 1]):page.find(tbl)]
            if name not in gap:
                print(f"  ! section check: expected '{name}' before table {i}; "
                      f"order may be off.")

        for p in parse_table(tbl):
            row = {
                "controlling_team": abbr,
                "round": rnd,
                "year": p["year"],
                "pick_origin": p["pick_origin"],
                "slot_span": p["slot_span"],
                "is_unprotected_or_unknown": "TRUE" if p["slot_span"] >= 30 else "FALSE",
                "condition": p["condition"],
                "source": "Spotrac",
                "last_verified": today,
            }
            rows.append(row)
            per_team.setdefault(abbr, []).append({
                "round": rnd, "year": p["year"], "pick_origin": p["pick_origin"],
                "slot_span": p["slot_span"], "condition": p["condition"],
            })

    rows.sort(key=lambda r: (r["controlling_team"], r["round"], r["year"] or 0))

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    with open(JSON_PATH, "w", encoding="utf-8") as fh:
        json.dump({"pulled": today, "source": URL, "teams": per_team}, fh, indent=2)

    print(f"Wrote {len(rows)} pick entries across {len(per_team)} teams -> {CSV_PATH}")
    print(f"Per-team detail -> {JSON_PATH}")
    yrs = sorted({r["year"] for r in rows if r["year"]})
    print(f"Years covered: {yrs}")


if __name__ == "__main__":
    main()
