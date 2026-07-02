"""One-off M0 probe: fetch one representative page of each type (through the
permanent cache) and report table ids + data-stat vocabularies, so parsers are
written against observed structure, not guessed structure."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup

from src.etl.bref_client import fetch, strip_comment_tables

PROBES = [
    ("/leagues/NBA_2005.html", "leagues_NBA_2005"),
    ("/leagues/NBA_1985.html", "leagues_NBA_1985"),
    ("/leagues/NBA_2026.html", "leagues_NBA_2026"),
    ("/leagues/NBA_2005_advanced.html", "advanced_NBA_2005"),
    ("/leagues/NBA_2026_advanced.html", "advanced_NBA_2026"),
    ("/draft/NBA_1996.html", "draft_NBA_1996"),
    ("/awards/all_league.html", "awards_all_league"),
]

for path, key in PROBES:
    html = strip_comment_tables(fetch(path, key))
    soup = BeautifulSoup(html, "lxml")
    print(f"\n=== {path}")
    for t in soup.find_all("table"):
        tid = t.get("id", "<no-id>")
        head_stats = [th.get("data-stat") for th in t.find_all("th", limit=40) if th.get("data-stat")]
        rows = t.find_all("tr")
        print(f"  table id={tid} rows={len(rows)} stats={head_stats[:18]}")
