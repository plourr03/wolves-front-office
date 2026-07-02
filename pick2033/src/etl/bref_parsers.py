"""Pure HTML -> records parsers for B-Ref pages. No network access here;
tests run these against cached fixtures (tests/test_bref_parsers.py).

Observed structure (probed 2026-07-01, cached under data/raw/bref/):
- Season pages: standings in divs_standings_E / divs_standings_W across all
  eras 1980-2026; rows carry data-stat cells (team_name th with /teams/ABBR/
  link, wins, losses, win_loss_pct, srs). Division header rows have no link.
- Advanced pages: table#advanced, modern data-stat vocabulary backported to
  all seasons (name_display, age, team_name_abbr, pos, games, mp, per, ows,
  dws, ws, obpm, dbpm, bpm, vorp, awards). Multi-team seasons: combined row
  with team_name_abbr in {2TM,3TM,4TM,5TM,TOT}, then stint rows (class
  partial_table) in chronological order. Player slug via data-append-csv or
  the /players/x/slug.html href.
- Draft pages: table#stats, data-stats pick_overall / team_id / player /
  college_name; separator rows carry class thead/over_header.
- All-league page: table#awards_all_league; rows season / lg_id / all_team
  plus five player cells with /players/ links; blank spacer rows.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

COMBINED_MARKERS = {"TOT", "2TM", "3TM", "4TM", "5TM"}
_SLUG_RE = re.compile(r"/players/\w/([^./]+)\.html")
_TEAM_RE = re.compile(r"/teams/([A-Z]{3})/\d{4}\.html")


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def _stat(row, name):
    cell = row.find(attrs={"data-stat": name})
    return cell.get_text(strip=True) if cell else None


def _num(row, name, cast=float):
    txt = _stat(row, name)
    if txt in (None, ""):
        return None
    try:
        return cast(txt)
    except ValueError:
        return None


def _player_slug(cell) -> str | None:
    a = cell.find("a") if cell else None
    if a and (m := _SLUG_RE.search(a.get("href", ""))):
        return m.group(1)
    return None


def parse_season_standings(html: str, season: int) -> list[dict]:
    """W/L + SRS + conference for every team in a season page (ending-year)."""
    soup = _soup(html)
    out = []
    for conf in ("E", "W"):
        table = soup.find("table", id=f"divs_standings_{conf}")
        if table is None:
            raise ValueError(f"divs_standings_{conf} missing for season {season}")
        for row in table.find_all("tr"):
            th = row.find("th", attrs={"data-stat": "team_name"})
            a = th.find("a") if th else None
            if not a:
                continue  # division/conference header row
            m = _TEAM_RE.search(a.get("href", ""))
            if not m:
                continue
            out.append({
                "season": season,
                "bref_abbr": m.group(1),
                "team_name": a.get_text(strip=True),
                "conference": conf,
                "wins": _num(row, "wins", int),
                "losses": _num(row, "losses", int),
                "win_loss_pct": _num(row, "win_loss_pct"),
                "srs": _num(row, "srs"),
            })
    if len(out) < 20:
        raise ValueError(f"only {len(out)} standings rows parsed for {season}")
    return out


def parse_advanced_players(html: str, season: int, table_id: str = "advanced") -> list[dict]:
    """Player-season advanced rows (regular season by default; 'advanced_post'
    for playoffs). Emits combined rows (is_combined=True) AND stint rows with
    stint_order (1-based, chronological; last stint = final team)."""
    soup = _soup(html)
    table = soup.find("table", id=table_id)
    if table is None:
        raise ValueError(f"table #{table_id} missing for season {season}")
    out = []
    stint_counter = {}
    for row in table.find("tbody").find_all("tr"):
        classes = row.get("class") or []
        if "thead" in classes or "over_header" in classes:
            continue
        name_cell = row.find(attrs={"data-stat": "name_display"})
        if name_cell is None or not name_cell.get_text(strip=True):
            continue
        slug = row.get("data-append-csv") or _player_slug(name_cell)
        team = _stat(row, "team_name_abbr")
        if slug is None or not team:
            continue
        is_combined = team in COMBINED_MARKERS
        if is_combined:
            stint_counter[slug] = 0
            stint_order = None
        elif "partial_table" in classes:
            stint_counter[slug] = stint_counter.get(slug, 0) + 1
            stint_order = stint_counter[slug]
        else:
            stint_order = None  # single-team season
        out.append({
            "season": season,
            "player_id": slug,
            "player_name": name_cell.get_text(strip=True),
            "bref_abbr": None if is_combined else team,
            "pos": _stat(row, "pos"),
            "age": _num(row, "age", int),
            "games": _num(row, "games", int),
            "mp": _num(row, "mp", int),
            "per": _num(row, "per"),
            "ows": _num(row, "ows"),
            "dws": _num(row, "dws"),
            "ws": _num(row, "ws"),
            "obpm": _num(row, "obpm"),
            "dbpm": _num(row, "dbpm"),
            "bpm": _num(row, "bpm"),
            "vorp": _num(row, "vorp"),
            "is_combined": is_combined,
            "stint_order": stint_order,
            "awards": _stat(row, "awards"),
        })
    if len(out) < 100:
        raise ValueError(f"only {len(out)} advanced rows parsed for {season}")
    return out


def parse_draft(html: str, draft_year: int) -> list[dict]:
    """(draft_year, slot, player) for every pick on a draft page."""
    soup = _soup(html)
    table = soup.find("table", id="stats")
    if table is None:
        raise ValueError(f"draft table missing for {draft_year}")
    out = []
    for row in table.find("tbody").find_all("tr"):
        classes = row.get("class") or []
        if "thead" in classes or "over_header" in classes:
            continue
        slot = _num(row, "pick_overall", int)
        if slot is None:
            continue
        player_cell = row.find(attrs={"data-stat": "player"})
        out.append({
            "draft_year": draft_year,
            "slot": slot,
            "player_id": _player_slug(player_cell),
            "player_name": player_cell.get_text(strip=True) if player_cell else None,
            "team_abbr": _stat(row, "team_id"),
            "college": _stat(row, "college_name"),
        })
    if not (50 <= len(out) <= 62):
        raise ValueError(f"{len(out)} draft rows parsed for {draft_year}; expected 50-62")
    return out


DEEP_ROUNDS = {"Finals", "Eastern Conference Finals", "Western Conference Finals"}


def parse_playoff_deep_runs(html: str, season: int) -> list[dict]:
    """Teams reaching the conference finals or better (from the season page's
    all_playoffs bracket table). Series header rows carry the round name and
    /teams/ABBR/ links for both participants."""
    soup = _soup(html)
    table = soup.find("table", id="all_playoffs")
    if table is None:
        return []  # lockout pages still have it; missing table = no playoffs parsed
    out = []
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if not cells:
            continue
        round_name = cells[0].get_text(strip=True)
        if round_name not in DEEP_ROUNDS:
            continue
        for a in row.find_all("a"):
            m = _TEAM_RE.search(a.get("href", ""))
            if m:
                out.append({"season": season, "round": round_name, "bref_abbr": m.group(1)})
    return out


def parse_all_league(html: str) -> list[dict]:
    """(season, tier, player) for every NBA All-League selection."""
    soup = _soup(html)
    table = soup.find("table", id="awards_all_league")
    if table is None:
        raise ValueError("awards_all_league table missing")
    out = []
    for row in table.find("tbody").find_all("tr"):
        season_txt = _stat(row, "season")
        if not season_txt or _stat(row, "lg_id") != "NBA":
            continue
        season = int(season_txt.split("-")[0]) + 1  # "2025-26" -> 2026
        tier = _stat(row, "all_team")
        for cell in row.find_all("td"):
            slug = _player_slug(cell)
            if slug and cell.get("data-stat") not in ("season", "lg_id", "all_team", "voting"):
                out.append({
                    "season": season,
                    "tier": tier,
                    "player_id": slug,
                    "player_name": cell.get_text(strip=True),
                })
    if len(out) < 500:
        raise ValueError(f"only {len(out)} all-league rows parsed")
    return out
