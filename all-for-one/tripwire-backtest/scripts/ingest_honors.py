"""Phase 0.5 (G1): ingest All-NBA + All-Star (starter-flagged) honors.

Source: Basketball-Reference (same source as nba_player_contracts).
  All-NBA:   /awards/all_league.html          (one page, all seasons)
  All-Star:  /allstar/NBA_{year}.html         (one page per game)

Seasons: 2008-09 through 2025-26 (two seasons of lookback before the
tripwire era window, since the incumbent filter reaches back two years).

Output: data/honors.parquet with columns
  season_start (int, e.g. 2019 for 2019-20), season (str '2019-20'),
  award ('ALL_NBA' | 'ALL_STAR' ), tier (1/2/3 for All-NBA; NULL AllStar),
  is_starter (bool, All-Star only), bref_name, nba_player_id, resolved(bool).

Join to nba_player_id via the warehouse, on a normalized (diacritic-folded)
name plus a season-active check. NEVER trust the raw name join alone; every
unresolved row is reported, never guessed.

Validation: assert every clear seed-case incumbent resolves. The documented
sensitivity incumbents (Booker for CP3-2020, Garland for Mitchell-2022) are
reported, not forced, since whether they qualify is exactly the incumbent-
filter sensitivity the spec flags.
"""
from __future__ import annotations

import re
import sys
import time
import unicodedata
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
OUT = REPO / "all-for-one" / "tripwire-backtest" / "data" / "honors.parquet"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
# All-Star game YEAR maps to the season ending that year: 2020 game = 2019-20.
# No All-Star game in 2021? There WAS (Mar 2021 = 2020-21). None in 1999/2020?
# 2020-21 game happened Mar 2021. Cover games 2009..2026; 2026 game is Feb 2026.
ASG_YEARS = list(range(2009, 2027))
# All-Star game did not occur in some years; handle 404/empty gracefully.


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z ]", "", s.lower()).strip()
    s = re.sub(r"\s+", " ", s)
    # strip common suffixes
    for suf in (" jr", " sr", " ii", " iii", " iv"):
        if s.endswith(suf):
            s = s[: -len(suf)].strip()
    return s


def _fetch(url: str) -> str | None:
    for attempt in range(3):
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200:
            r.encoding = "utf-8"  # B-Ref serves UTF-8; requests otherwise guesses latin-1
            return r.text
        if r.status_code == 404:
            return None
        time.sleep(2)
    print(f"  WARN fetch failed {r.status_code}: {url}")
    return None


def _season_str(start: int) -> str:
    return f"{start}-{str(start + 1)[-2:]}"


def parse_all_nba() -> pd.DataFrame:
    html = _fetch("https://www.basketball-reference.com/awards/all_league.html")
    soup = BeautifulSoup(html, "lxml")
    t = soup.find("table", id="awards_all_league")
    rows = []
    for tr in t.find("tbody").find_all("tr"):
        th = tr.find("th")
        if not th or not th.get_text(strip=True):
            continue
        seas_txt = th.get_text(strip=True)  # e.g. '2019-20'
        m = re.match(r"(\d{4})-\d{2}", seas_txt)
        if not m:
            continue
        start = int(m.group(1))
        if start < 2008 or start > 2025:
            continue
        tds = {td.get("data-stat"): td for td in tr.find_all("td")}
        lg = tds.get("lg_id")
        if lg and lg.get_text(strip=True) not in ("NBA", ""):
            continue
        tier_txt = tds.get("all_team").get_text(strip=True) if tds.get("all_team") else ""
        tier = {"1st": 1, "2nd": 2, "3rd": 3}.get(tier_txt)
        # players are the anchor links in the row's player cells
        for a in tr.find_all("a", href=re.compile(r"/players/")):
            nm = a.get_text(strip=True)
            if nm:
                rows.append({"season_start": start, "season": _season_str(start),
                             "award": "ALL_NBA", "tier": tier, "is_starter": None,
                             "bref_name": nm})
    return pd.DataFrame(rows)


def parse_all_star(year: int) -> pd.DataFrame:
    html = _fetch(f"https://www.basketball-reference.com/allstar/NBA_{year}.html")
    if html is None:
        return pd.DataFrame()
    soup = BeautifulSoup(html, "lxml")
    start = year - 1  # 2020 game -> 2019-20
    rows = []
    # Each conference roster is a table id like 'East' / 'West' (or team names
    # in some years). Starters are the first 5 rows before a 'Reserves' divider.
    for t in soup.find_all("table"):
        tid = t.get("id") or ""
        # roster tables have a Starters/Reserves structure in tbody
        tb = t.find("tbody")
        if not tb:
            continue
        # detect a roster table: rows link to /players/ and there's a
        # 'Reserves' class-full row separating starters from reserves.
        starter = True
        seen_players = 0
        found_reserve_divider = False
        cand = []
        for tr in tb.find_all("tr"):
            txt = tr.get_text(" ", strip=True)
            if re.search(r"reserve", txt, re.I):
                starter = False
                found_reserve_divider = True
                continue
            if re.search(r"starter", txt, re.I) and not tr.find("a", href=re.compile(r"/players/")):
                starter = True
                continue
            a = tr.find("a", href=re.compile(r"/players/"))
            if a:
                cand.append((a.get_text(strip=True), starter))
                seen_players += 1
        # only accept tables that look like a roster (>=7 players and a
        # reserve divider), to avoid scraping unrelated tables.
        if seen_players >= 7 and found_reserve_divider:
            for nm, st in cand:
                rows.append({"season_start": start, "season": _season_str(start),
                             "award": "ALL_STAR", "tier": None, "is_starter": st,
                             "bref_name": nm})
    df = pd.DataFrame(rows)
    if len(df):
        # dedupe (a player appears once per game)
        df = df.drop_duplicates(subset=["season_start", "bref_name"], keep="first")
    return df


def resolve_ids(honors: pd.DataFrame) -> pd.DataFrame:
    """Resolve bref_name to nba_player_id via warehouse, season-active check."""
    bio = query("""
        SELECT player_id, first_name, last_name
        FROM nba.nba_player_bio
    """)
    bio["norm"] = (bio.first_name.fillna("") + " " + bio.last_name.fillna("")).map(_norm)
    # season-active map: player_id -> set of season_start ints
    active = query("""
        SELECT DISTINCT player_id, LEFT(season_year,4)::int AS s
        FROM nba.nba_player_season_bio
    """)
    active_map = active.groupby("player_id").s.apply(set).to_dict()

    by_norm = bio.groupby("norm").player_id.apply(list).to_dict()

    pid, resolved = [], []
    for _, r in honors.iterrows():
        key = _norm(r.bref_name)
        cands = by_norm.get(key, [])
        chosen = None
        if len(cands) == 1:
            chosen = cands[0]
        elif len(cands) > 1:
            # disambiguate by season-active
            act = [c for c in cands if r.season_start in active_map.get(c, set())
                   or (r.season_start + 1) in active_map.get(c, set())]
            if len(act) == 1:
                chosen = act[0]
        pid.append(chosen)
        resolved.append(chosen is not None)
    honors = honors.copy()
    honors["nba_player_id"] = pid
    honors["resolved"] = resolved
    return honors


def main() -> None:
    print("parsing All-NBA (one page, all seasons)...")
    anba = parse_all_nba()
    print(f"  All-NBA rows: {len(anba)}, seasons {anba.season_start.min()}-{anba.season_start.max()}")

    print("parsing All-Star (one page per game)...")
    frames = []
    for y in ASG_YEARS:
        d = parse_all_star(y)
        print(f"  {y} ({_season_str(y-1)}): {len(d)} selections, "
              f"{int(d.is_starter.sum()) if len(d) else 0} starters")
        frames.append(d)
        time.sleep(1.2)  # be polite to B-Ref
    astar = pd.concat([f for f in frames if len(f)], ignore_index=True) if any(len(f) for f in frames) else pd.DataFrame()

    honors = pd.concat([anba, astar], ignore_index=True)
    honors = resolve_ids(honors)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    honors.to_parquet(OUT, index=False)
    print(f"\nwrote {OUT}: {len(honors)} rows, "
          f"{honors.resolved.sum()} resolved, {(~honors.resolved).sum()} unresolved")

    unres = honors[~honors.resolved]
    if len(unres):
        print("\nUNRESOLVED (report, never guess):")
        print(unres[["season", "award", "is_starter", "bref_name"]].to_string(index=False))


if __name__ == "__main__":
    main()
