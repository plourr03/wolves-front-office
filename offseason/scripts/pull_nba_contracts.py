#!/usr/bin/env python3
"""
pull_nba_contracts.py

Pulls every NBA team's contract data into a single breadth CSV (Pass 1 of
the offseason data plan, section 5.2) plus a companion full-detail JSON.

SOURCE: HoopsHype team salary pages. The salary table is rendered client
side by a Next.js app, so the visible HTML is just loading skeletons. The
real data ships in the page's __NEXT_DATA__ JSON blob (React Query
dehydrated state). We fetch each team page, extract that blob, and read the
structured contract records straight out of it. This is cleaner and more
complete than scraping the rendered table: every season carries explicit
salary, playerOption, teamOption, qualifyingOffer, and twoWayContract
fields, and the JSON includes out-years the four-column table never shows.

WHAT THIS GIVES US (Pass 1 breadth):
  - per-season salary 2026-27 through 2029-30 for every rostered player
  - player option / team option flags, years, and amounts
  - two-way and qualifying-offer contract-type flags
  - future-years salary total and years remaining

WHAT IT DOES NOT GIVE (Pass 2, targeted manual fill from Spotrac/Coon):
  - trade kickers, no-trade clauses, partial-guarantee dates, Bird rights
These columns are written blank on purpose. Blanks are honest; a guessed
option flag breaks the matching logic downstream.

Run it in your environment (needs internet). No API key required.
    python pull_nba_contracts.py
"""

import os
import re
import csv
import json
import time
import sys

try:
    import requests
except ImportError:
    sys.exit("pip install requests")

# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------

# The 2026-27 league year is keyed as integer 2026 in HoopsHype's data
# (season N == the N..N+1 league year; e.g. 2025 == 2025-26).
BASE_SEASON = 2026
FUTURE_SEASONS = [2026, 2027, 2028, 2029]   # columns we surface in the CSV

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(HERE, "..", "data")
CSV_PATH = os.path.join(OUTPUT_DIR, "nba_contracts_2026_27.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "nba_contracts_2026_full.json")

REQUEST_SLEEP_SECONDS = 1.5   # be polite between team pages
MAX_RETRIES = 3
HEADERS = {"User-Agent": "Mozilla/5.0 (research; contract table pull)"}

# abbr -> (hoopshype slug, hoopshype numeric team id). Verified against the
# live /salaries/teams/ index. Note Charlotte's id is 5312, not in the 1-29
# block; everything else is sequential-ish but do not assume it.
TEAM_DIRECTORY = {
    "ATL": ("atlanta-hawks", "1"),
    "BOS": ("boston-celtics", "2"),
    "NOP": ("new-orleans-pelicans", "3"),
    "CHI": ("chicago-bulls", "4"),
    "CLE": ("cleveland-cavaliers", "5"),
    "DAL": ("dallas-mavericks", "6"),
    "DEN": ("denver-nuggets", "7"),
    "DET": ("detroit-pistons", "8"),
    "GSW": ("golden-state-warriors", "9"),
    "HOU": ("houston-rockets", "10"),
    "IND": ("indiana-pacers", "11"),
    "LAC": ("los-angeles-clippers", "12"),
    "LAL": ("los-angeles-lakers", "13"),
    "MIA": ("miami-heat", "14"),
    "MIL": ("milwaukee-bucks", "15"),
    "MIN": ("minnesota-timberwolves", "16"),
    "BKN": ("brooklyn-nets", "17"),
    "NYK": ("new-york-knicks", "18"),
    "ORL": ("orlando-magic", "19"),
    "PHI": ("philadelphia-76ers", "20"),
    "PHX": ("phoenix-suns", "21"),
    "POR": ("portland-trail-blazers", "22"),
    "SAC": ("sacramento-kings", "23"),
    "SAS": ("san-antonio-spurs", "24"),
    "OKC": ("oklahoma-city-thunder", "25"),
    "UTA": ("utah-jazz", "26"),
    "WAS": ("washington-wizards", "27"),
    "TOR": ("toronto-raptors", "28"),
    "MEM": ("memphis-grizzlies", "29"),
    "CHA": ("charlotte-hornets", "5312"),
}

# CSV schema. Per-season columns are generated from FUTURE_SEASONS so the
# header stays in sync if you extend the window.
SEASON_COLS = [f"salary_{s}_{(s + 1) % 100:02d}" for s in FUTURE_SEASONS]

FIELDNAMES = (
    ["team_abbr", "player", "player_id", "position"]
    + SEASON_COLS
    + [
        "future_total_2026_plus", "years_remaining",
        "player_option_flag", "player_option_year", "player_option_amount",
        "team_option_flag", "team_option_year", "team_option_amount",
        "two_way_flag", "qualifying_offer_flag",
        "trade_kicker_flag", "trade_kicker_pct", "no_trade_clause_flag",
        "guarantee_status", "guarantee_date",
        "fa_status_2026", "bird_rights",
        "source", "last_verified", "notes",
    ]
)

# --------------------------------------------------------------------------
# FETCH
# --------------------------------------------------------------------------

def _team_url(slug, team_id):
    return f"https://hoopshype.com/salaries/teams/{slug}/{team_id}/"


def _extract_next_data(html):
    """Pull and parse the __NEXT_DATA__ JSON blob from a HoopsHype page."""
    m = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    if not m:
        raise ValueError("no __NEXT_DATA__ blob found (page layout changed?)")
    return json.loads(m.group(1))


def _find_contracts(next_data):
    """Locate the contracts list inside the React Query dehydrated state.

    We search rather than hard-code the index, because query ordering is not
    guaranteed across page builds.
    """
    queries = (
        next_data.get("props", {})
        .get("pageProps", {})
        .get("dehydratedState", {})
        .get("queries", [])
    )
    for q in queries:
        data = q.get("state", {}).get("data", {})
        if isinstance(data, dict) and isinstance(data.get("contracts"), dict):
            inner = data["contracts"].get("contracts")
            if isinstance(inner, list):
                return inner
    raise ValueError("contracts list not found in __NEXT_DATA__")


def fetch_team_contracts(abbr, slug, team_id):
    """Return a list of raw HoopsHype contract dicts for one team, or []."""
    url = _team_url(slug, team_id)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return _find_contracts(_extract_next_data(resp.text))
        except Exception as exc:
            print(f"  ! {abbr}: attempt {attempt}/{MAX_RETRIES} failed ({exc})")
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_SLEEP_SECONDS * attempt)
    return []


# --------------------------------------------------------------------------
# NORMALIZE
# --------------------------------------------------------------------------

def _season_label(season_int):
    """2027 -> '2027-28'."""
    return f"{season_int}-{(season_int + 1) % 100:02d}"


def _season_index(seasons):
    """Map season-year int -> the season dict, keeping the latest entry if
    duplicates ever appear."""
    return {s["season"]: s for s in seasons if isinstance(s.get("season"), int)}


def normalize_player(abbr, raw):
    seasons = raw.get("seasons", []) or []
    by_year = _season_index(seasons)

    row = {f: "" for f in FIELDNAMES}
    row["team_abbr"] = abbr
    row["player"] = raw.get("playerName", "")
    row["player_id"] = raw.get("playerID", "")
    row["position"] = ""  # not in HoopsHype salary feed; filled from warehouse

    # Per-season salaries for the surfaced window.
    future_total = 0
    years_remaining = 0
    for season, col in zip(FUTURE_SEASONS, SEASON_COLS):
        s = by_year.get(season)
        if s and s.get("salary"):
            row[col] = s["salary"]
            future_total += s["salary"]
            years_remaining += 1

    row["future_total_2026_plus"] = future_total if future_total else ""
    row["years_remaining"] = years_remaining

    # Options: collect any future-year option seasons.
    po_years = [s["season"] for s in seasons
                if s.get("playerOption") and s["season"] >= BASE_SEASON]
    to_years = [s["season"] for s in seasons
                if s.get("teamOption") and s["season"] >= BASE_SEASON]

    if po_years:
        first = min(po_years)
        row["player_option_flag"] = "TRUE"
        row["player_option_year"] = _season_label(first)
        amt = by_year.get(first, {}).get("salary")
        row["player_option_amount"] = amt if amt else ""
    else:
        row["player_option_flag"] = "FALSE"

    if to_years:
        first = min(to_years)
        row["team_option_flag"] = "TRUE"
        row["team_option_year"] = _season_label(first)
        amt = by_year.get(first, {}).get("salary")
        row["team_option_amount"] = amt if amt else ""
    else:
        row["team_option_flag"] = "FALSE"

    # Contract-type flags (any future season).
    row["two_way_flag"] = "TRUE" if any(
        s.get("twoWayContract") and s["season"] >= BASE_SEASON for s in seasons
    ) else "FALSE"
    row["qualifying_offer_flag"] = "TRUE" if any(
        s.get("qualifyingOffer") and s["season"] >= BASE_SEASON for s in seasons
    ) else "FALSE"

    # Pass-2 fields HoopsHype does not expose: left blank deliberately.
    row["trade_kicker_flag"] = ""
    row["trade_kicker_pct"] = ""
    row["no_trade_clause_flag"] = ""
    row["guarantee_status"] = ""
    row["guarantee_date"] = ""

    # Light FA derivation: no guaranteed 2026-27 salary and no option year
    # means the player is heading to free agency in 2026 (defer to the
    # Spotrac free-agent table for the authoritative UFA/RFA split).
    has_2026 = bool(by_year.get(BASE_SEASON, {}).get("salary"))
    if not has_2026 and not po_years and not to_years:
        row["fa_status_2026"] = "FA (derived)"
    row["bird_rights"] = ""

    row["source"] = "HoopsHype"
    row["last_verified"] = time.strftime("%Y-%m-%d")
    notes = []
    if raw.get("updateDate"):
        notes.append(f"hh_update={raw['updateDate'][:10]}")
    if len(po_years) > 1:
        notes.append("multiple PO years: " + ",".join(map(str, sorted(po_years))))
    if len(to_years) > 1:
        notes.append("multiple TO years: " + ",".join(map(str, sorted(to_years))))
    row["notes"] = "; ".join(notes)
    return row


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = []
    full = {}   # abbr -> raw contract records, preserved verbatim for Pass 2

    for abbr, (slug, team_id) in TEAM_DIRECTORY.items():
        print(f"Fetching {abbr} ...")
        raw_players = fetch_team_contracts(abbr, slug, team_id)
        full[abbr] = raw_players
        for raw in raw_players:
            rows.append(normalize_player(abbr, raw))
        print(f"  {len(raw_players)} players")
        time.sleep(REQUEST_SLEEP_SECONDS)

    def _sort_key(r):
        s = r[SEASON_COLS[0]]
        # team, then 2026-27 salary high to low; blanks sort last.
        return (r["team_abbr"], -s if isinstance(s, int) else 1)

    rows.sort(key=_sort_key)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    with open(JSON_PATH, "w", encoding="utf-8") as fh:
        json.dump(
            {"pulled": time.strftime("%Y-%m-%d"),
             "base_season": BASE_SEASON,
             "teams": full},
            fh, indent=2,
        )

    teams_with_data = sum(1 for v in full.values() if v)
    print(f"\nWrote {len(rows)} rows across {teams_with_data}/{len(TEAM_DIRECTORY)} "
          f"teams -> {CSV_PATH}")
    print(f"Full per-season detail -> {JSON_PATH}")
    if teams_with_data < len(TEAM_DIRECTORY):
        empty = [a for a, v in full.items() if not v]
        print(f"WARNING: no data for: {', '.join(empty)} (re-run those teams).")


if __name__ == "__main__":
    main()
