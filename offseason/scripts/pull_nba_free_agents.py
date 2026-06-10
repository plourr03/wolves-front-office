#!/usr/bin/env python3
"""
pull_nba_free_agents.py

Pulls the full 2026 NBA free-agent board from Spotrac into a CSV.

SOURCE: https://www.spotrac.com/nba/free-agents/available/_/year/2026
This page is server-rendered HTML (a single table), so a plain GET plus
BeautifulSoup is enough. Each row carries clean data-* attributes
(player id, name, position) and a status pill, so we parse structured
fields rather than scraping flattened text.

The board lists everyone who could reach the 2026 market, tagged by type:
  UFA   unrestricted free agent
  RFA   restricted free agent (prior team can match)
  PLYR  player option (FA only if the player declines)
  CLUB  team/club option (FA only if the team declines)

Fields captured per player: type, name, position, previous team, years of
experience, age, and the previous contract's average annual value (AAV).
Salary projections and Bird-rights detail are a targeted Pass-2 fill.

Run it in your environment (needs internet). No API key required.
    python pull_nba_free_agents.py
"""

import os
import re
import csv
import sys
import time

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("pip install requests beautifulsoup4")

URL = "https://www.spotrac.com/nba/free-agents/available/_/year/2026"
HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(HERE, "..", "data")
CSV_PATH = os.path.join(OUTPUT_DIR, "nba_free_agents_2026.csv")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research"}

# Spotrac pill label -> human-readable free-agency category.
FA_TYPE_LABELS = {
    "UFA": "Unrestricted",
    "RFA": "Restricted",
    "PLYR": "Player Option",
    "CLUB": "Team Option",
}

FIELDNAMES = [
    "player", "player_id", "nba_player_id", "position",
    "fa_type", "fa_type_label", "counts_on_books_until_declined",
    "previous_team", "years_experience", "age",
    "previous_aav",
    "player_url", "source", "last_verified",
]


def _clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def _money_to_int(text):
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else ""


def parse_row(tr):
    """Turn one <tr class='fa-row'> into a normalized dict, or None."""
    pid = tr.get("data-player-id", "")
    name = _clean(tr.get("data-name", ""))
    pos = _clean(tr.get("data-position", ""))
    if not name:
        return None

    pill = tr.select_one(".pill-start")
    fa_type = _clean(pill.get_text()) if pill else ""

    tds = tr.find_all("td", recursive=False)
    left = tds[0] if tds else tr

    # Previous team: the abbreviation text sitting next to the team logo.
    prev_team = ""
    img = left.find("img")
    if img and img.parent:
        prev_team = _clean(img.parent.get_text())
    if not prev_team and img and img.get("src"):
        m = re.search(r"nba_(\w+)\.png", img["src"])
        if m:
            prev_team = m.group(1).upper()

    block_text = left.get_text(" ", strip=True)
    yoe_m = re.search(r"YOE:\s*([\d.]+)", block_text)
    age_m = re.search(r"Age:\s*([\d.]+)", block_text)

    link = left.find("a")
    url = link["href"] if link and link.has_attr("href") else ""

    prev_aav = _money_to_int(tds[1].get_text()) if len(tds) > 1 else ""

    return {
        "player": name,
        "player_id": pid,
        "position": pos,
        "fa_type": fa_type,
        "fa_type_label": FA_TYPE_LABELS.get(fa_type, fa_type),
        "previous_team": prev_team,
        "years_experience": yoe_m.group(1) if yoe_m else "",
        "age": age_m.group(1) if age_m else "",
        "previous_aav": prev_aav,
        "player_url": url,
        "source": "Spotrac",
        "last_verified": time.strftime("%Y-%m-%d"),
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Fetching {URL} ...")
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = []
    for tr in soup.select("tr.fa-row"):
        row = parse_row(tr)
        if row:
            rows.append(row)

    if not rows:
        sys.exit("No free-agent rows parsed. The page layout likely changed.")

    # Unrestricted first, then by previous AAV descending (biggest names up top).
    type_order = {"UFA": 0, "RFA": 1, "PLYR": 2, "CLUB": 3}
    rows.sort(key=lambda r: (
        type_order.get(r["fa_type"], 9),
        -(r["previous_aav"] if isinstance(r["previous_aav"], int) else 0),
    ))

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    counts = {}
    for r in rows:
        counts[r["fa_type"]] = counts.get(r["fa_type"], 0) + 1
    print(f"Wrote {len(rows)} free agents -> {CSV_PATH}")
    print("By type: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
