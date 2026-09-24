#!/usr/bin/env python3
"""C1: champions, extended. The H1 table for every champion from 2015-16 onward.

For each champion: the top eight by playoff minutes and how each was acquired (drafted,
traded for, signed, and when), the top eight's age, continuity with the season before,
regular-season and post-All-Star net rating rank, seed, playoff net rating against the
regular season, the top eight's games missed in the regular season and the playoffs, the
top five's share of minutes in both, and the in-season transactions that changed the top
eight. The preseason title price (American odds, proportional de-vig implied percentage,
rank of 30 with ties sharing a rank) from `offseason/data/{season}-preseason-odd.csv`, the
files `c1_preseason_odds.py` builds and checks. Then one paragraph per champion, written
from the numbers.

SOURCES. Warehouse box scores (`nba_player_stats`, `nba_games`, `nba_team_advanced_stats`,
`nba_player_bio`) for minutes, games, net ratings, standings and ages. Basketball-Reference
for the champion cross-check (the league season page), the roster with player slugs and the
conference finish (the team season page), and each player's transaction history (the player
page). Every page is cached once with its sha256 in `data/bref/manifest.json`.

CROSS-CHECK. A champion row is used only when the winner of the last playoff game in the
warehouse is the team the Basketball-Reference season page names as League Champion. A
mismatch is fatal, not skipped silently.

DEFINITIONS.
  top eight        the eight highest playoff minute totals for the champion that spring
  acquired         the first event that put the player on the franchise in his current
                   stint, read from his Basketball-Reference transaction log: drafted (draft
                   night, including draft rights traded in that night), traded for, or
                   signed (free agency, waivers, two-way or 10-day). A re-signing or rookie
                   contract inside an unbroken stint does not restart the clock.
  age              on February 1 of the season, the Basketball-Reference convention
  continuity       how many of the top eight appeared for the franchise in the previous
                   regular season, and the share of ALL playoff minutes that went to such
                   returning players
  net rating       possession-weighted mean of per-game NBA.com net rating; rank among 30
  post-All-Star    games after the longest gap in the league schedule between February 1
                   and March 15, derived from the schedule itself
  seed             the conference finish on the Basketball-Reference team page, checked
                   against the warehouse standings
  games missed     team games after the player's acquisition date minus his appearances
  top-five share   the five largest minute totals over the team's total minutes

    python kuminga/scripts/c1_champions.py [--first 2016] [--last 2026]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import bref, runlog  # noqa: E402
from lib import db                    # noqa: E402
import bracket_sim as E               # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
DOCS = os.path.join(REPO, "kuminga", "docs")
AS_OF = "2026-09-24"
ODDS_DIR = os.path.join(REPO, "offseason", "data")
ODDS_SOURCES = os.path.join(REPO, "kuminga", "data", "preseason_odds_sources.csv")
TOP = 8
BREF_CODE = {"BKN": "BRK", "CHA": "CHO", "PHX": "PHO"}
CONF = dict(E.TEAM_CONF)


def norm(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    s = re.sub(r"[.'\-]", "", s.lower())
    s = re.sub(r"\b(jr|sr|ii|iii|iv)\b", "", s)
    return " ".join(s.split())


def parse_date(s):
    return pd.Timestamp(s.strip())


# ---------------------------------------------------------------- Basketball-Reference
def league_champion(year):
    h = bref.fetch("/leagues/NBA_%d.html" % year)
    m = re.search(r"League Champion</strong>:\s*<a href=['\"]/teams/([A-Z]{3})/\d{4}\.html['\"]>([^<]+)</a>", h)
    if not m:
        raise RuntimeError("no League Champion line on the %d season page" % year)
    return m.group(1), m.group(2).strip()


def team_page(code, year):
    h = bref.strip_comments(bref.fetch("/teams/%s/%d.html" % (code, year)))
    soup = BeautifulSoup(h, "lxml")
    roster = {}
    tab = soup.find("table", id="roster")
    for tr in tab.tbody.find_all("tr"):
        a = tr.find("td", {"data-stat": "player"}).find("a")
        bd = tr.find("td", {"data-stat": "birth_date"})
        roster[norm(a.get_text(strip=True))] = dict(name=a.get_text(strip=True), href=a["href"],
                                                    birth_date=bd.get_text(strip=True) if bd else "")
    meta = " ".join(soup.find("div", id="meta").get_text(" ", strip=True).split())
    fin = re.search(r"Finished (\d+)(?:st|nd|rd|th) in NBA (Eastern|Western) Conference", meta)
    rec = re.search(r"Record:\s*(\d+)-(\d+)", meta)
    net = re.search(r"Net Rtg\s*:\s*([+-]?\d+\.\d+)\s*\((\d+)(?:st|nd|rd|th) of 30\)", meta)
    return dict(roster=roster, finish=int(fin.group(1)) if fin else None, conf=fin.group(2)[0] if fin else None,
                w=int(rec.group(1)) if rec else None, l=int(rec.group(2)) if rec else None,
                bref_net=float(net.group(1)) if net else None, bref_net_rank=int(net.group(2)) if net else None)


def transactions(href):
    h = bref.strip_comments(bref.fetch(href))
    i = h.find('id="all_transactions"')
    seg = h[i:i + 40000] if i >= 0 else ""
    out = []
    for p in BeautifulSoup(seg, "lxml").select("p.transaction"):
        txt = p.get_text(" ", strip=True)
        m = re.match(r"([A-Z][a-z]+ \d{1,2}, \d{4})\s*:\s*(.*)", txt)
        if m:
            out.append((parse_date(m.group(1)), m.group(2)))
    return sorted(out, key=lambda x: x[0])


def acquisition(events, franchise, cutoff):
    """The event that opened the player's current stint with the franchise, as of cutoff."""
    F = re.escape(franchise)
    stint = None
    for d, t in events:
        if d > cutoff:
            break
        joined = None
        if re.search(r"Drafted by the %s\b" % F, t):
            joined = "drafted"
        elif re.search(r"to the %s\b" % F, t) and re.search(r"traded|draft rights", t, re.I):
            joined = "traded for"
        elif re.search(r"(Signed|Re-signed|Claimed)[^;]*?(with|by) the %s\b" % F, t):
            joined = "signed"
        left = bool(re.search(r"(Traded|traded) by the %s\b" % F, t) and not re.search(r"to the %s\b" % F, t)) \
            or bool(re.search(r"(Waived|Released) by the %s\b" % F, t)) \
            or bool(re.search(r"(Signed|Re-signed|Claimed)[^;]*?(with|by) the (?!%s\b)" % F, t)) \
            or bool(re.search(r"Retired", t))
        if joined == "traded for" and stint is None and re.search(r"as a future .*draft pick", t, re.I):
            later = [(d2, t2) for d2, t2 in events if d2 >= d and re.search(r"Drafted by the %s\b" % F, t2)]
            if later:
                stint = dict(acq_type="drafted", acq_date=later[0][0], acq_text=later[0][1][:220])
                continue                               # the pick moved, then the team drafted him with it
        if joined and stint is None:
            kind = joined
            if joined == "traded for" and re.search(r"draft rights|as a future .* draft pick|drafted", t, re.I) \
                    and re.search(r"Drafted by", t) is None and any(abs((d - d2).days) <= 2 and "Drafted by" in t2 for d2, t2 in events):
                kind = "drafted (rights traded on draft night)"
            stint = dict(acq_type=kind, acq_date=d, acq_text=t[:220])
        elif joined and stint is not None:
            pass                                   # re-signing or rookie deal inside the stint
        elif left and stint is not None:
            stint = None
    return stint or dict(acq_type="unknown", acq_date=pd.NaT, acq_text="no joining event found before the playoffs")


# ---------------------------------------------------------------- warehouse
def preseason_odds(year, abbr):
    """The champion's preseason title price from the season's odds file: American odds,
    implied percentage after a proportional de-vig across all 30 teams, and rank of 30
    (tied prices share a rank)."""
    season = "%d-%s" % (year - 1, str(year)[2:])
    f = os.path.join(ODDS_DIR, "%s-preseason-odd.csv" % season)
    if not os.path.exists(f):
        return dict(preseason_title_odds="", preseason_odds_source="", preseason_odds_american="",
                    preseason_implied_pct=np.nan, preseason_rank=np.nan, preseason_rank_shared_by=np.nan,
                    preseason_favorite="", preseason_favorite_pct=np.nan)
    d = pd.read_csv(f)
    d["p_raw"] = d.Odds.map(lambda o: 100.0 / (float(o) + 100.0) if float(o) > 0 else -float(o) / (-float(o) + 100.0))
    d["p"] = d.p_raw / d.p_raw.sum()
    d["rank"] = d.p.rank(ascending=False, method="min").astype(int)
    d["abbr"] = d.Team.map(E.NAME_TO_ABBR)
    if d.abbr.isna().any() or len(d) != 30:
        raise RuntimeError("%s: odds file has %d teams, %d unmapped names" % (season, len(d), int(d.abbr.isna().sum())))
    c = d[d.abbr == abbr]
    if len(c) != 1:
        raise RuntimeError("%s: champion %s not in the odds file" % (season, abbr))
    c = c.iloc[0]
    src = ""
    if os.path.exists(ODDS_SOURCES):
        s = pd.read_csv(ODDS_SOURCES)
        s = s[s.season == season]
        if len(s) == 1:
            src = "%s sha256 %s" % (s.iloc[0].url, str(s.iloc[0].sha256)[:16])
    fav = d[d["rank"] == 1]
    return dict(preseason_title_odds="%+d (%.2f%%, rank %d of 30)" % (int(c.Odds), 100 * c.p, int(c["rank"])),
                preseason_odds_source=src, preseason_odds_american="%+d" % int(c.Odds),
                preseason_implied_pct=round(float(100 * c.p), 2), preseason_rank=int(c["rank"]),
                preseason_rank_shared_by=int((d["rank"] == int(c["rank"])).sum()),
                preseason_favorite=" / ".join(fav.Team), preseason_favorite_pct=round(float(100 * fav.p.iloc[0]), 2))


def champion_row(year):
    sid_po, sid_rs = 40000 + year - 1, 20000 + year - 1
    last = db.query("""select g.team_id, g.team_abbreviation, g.game_date from nba.nba_games g
                       where g.season_type = 'Playoffs' and g.season_id = %(s)s and g.wl = 'W'
                       and g.game_date = (select max(game_date) from nba.nba_games where season_type = 'Playoffs' and season_id = %(s)s)""",
                    {"s": sid_po})
    assert len(last) == 1, "last playoff game of %d has %d winners" % (year, len(last))
    return int(last.team_id.iloc[0]), str(last.team_abbreviation.iloc[0]), sid_po, sid_rs


def team_games(sid, tid):
    d = db.query("select game_id, game_date from nba.nba_games where season_id = %(s)s and team_id = %(t)s order by game_date",
                 {"s": sid, "t": tid})
    d["game_date"] = pd.to_datetime(d.game_date)
    return d


def player_minutes(sid, tid):
    return db.query("""select s.player_id, s.player_name, sum(s.minutes_played) mins,
                              count(*) filter (where s.minutes_played > 0) gp,
                              min(s.game_date) first_game, max(s.game_date) last_game
                       from nba.nba_player_stats s join nba.nba_games g on g.game_id = s.game_id and g.team_id = s.team_id
                       where g.season_id = %(s)s and s.team_id = %(t)s group by 1, 2 order by mins desc""", {"s": sid, "t": tid})


def net_ratings(sid, start=None):
    q = """select g.team_abbreviation team, sum(a.net_rating * a.possessions) / nullif(sum(a.possessions), 0) net,
                  count(*) n
           from nba.nba_team_advanced_stats a join nba.nba_games g on g.game_id = a.game_id and g.team_id = a.team_id
           where g.season_id = %(s)s and a.possessions > 0 """ + ("and g.game_date >= %(d)s " if start else "") + "group by 1"
    d = db.query(q, {"s": sid, "d": start})
    d["rank"] = d.net.rank(ascending=False, method="min").astype(int)
    return d.set_index("team")


def standings(sid):
    d = db.query("""select team_abbreviation team, sum(case when wl = 'W' then 1 else 0 end) w,
                           sum(case when wl = 'L' then 1 else 0 end) l, sum(plus_minus) pm
                    from nba.nba_games where season_id = %(s)s group by 1""", {"s": sid})
    d["conf"] = d.team.map(CONF)
    d["pct"] = d.w / (d.w + d.l)
    d = d.sort_values(["conf", "pct", "pm"], ascending=[True, False, False])
    d["conf_rank"] = d.groupby("conf").cumcount() + 1
    return d.set_index("team")


def all_star_break(sid, year):
    dates = db.query("select distinct game_date from nba.nba_games where season_id = %(s)s and season_type = 'Regular Season' "
                     "and game_date between %(a)s and %(b)s order by 1",
                     {"s": sid, "a": "%d-02-01" % year, "b": "%d-03-15" % year}).game_date
    dates = pd.to_datetime(dates).tolist()
    gaps = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    k = int(np.argmax(gaps))
    return dates[k], dates[k + 1], gaps[k]


def birthdates(pids):
    b = db.query("select player_id, birthdate from nba.nba_player_bio where player_id = any(%(p)s)", {"p": [int(x) for x in pids]})
    return {int(x.player_id): pd.Timestamp(x.birthdate) for _, x in b.iterrows() if pd.notna(x.birthdate)}


# ---------------------------------------------------------------- assembly
def build(year, r):
    tid, abbr, sid_po, sid_rs = champion_row(year)
    code, franchise = league_champion(year)
    if BREF_CODE.get(abbr, abbr) != code:
        raise RuntimeError("%d: warehouse champion %s, Basketball-Reference says %s (%s)" % (year, abbr, code, franchise))
    tp = team_page(code, year)
    rs_games, po_games = team_games(sid_rs, tid), team_games(sid_po, tid)
    rs_start, po_start = pd.Timestamp(rs_games.game_date.min()), pd.Timestamp(po_games.game_date.min())
    po = player_minutes(sid_po, tid)
    rs = player_minutes(sid_rs, tid).set_index("player_id")
    prior = set(player_minutes(sid_rs - 1, tid).player_id.astype(int))
    top = po.head(TOP).copy()
    bd = birthdates(top.player_id)
    feb1 = pd.Timestamp("%d-02-01" % year)
    players = []
    for _, x in top.iterrows():
        pid = int(x.player_id)
        key = norm(x.player_name)
        entry = tp["roster"].get(key)
        if entry is None:
            # last-name fallback for spellings the two sources disagree on
            cands = [v for k, v in tp["roster"].items() if k.split()[-1] == key.split()[-1]]
            if len(cands) == 1:
                entry = cands[0]
        if entry is None:
            raise RuntimeError("%d %s: %s not on the Basketball-Reference roster page" % (year, code, x.player_name))
        acq = acquisition(transactions(entry["href"]), franchise, po_start)
        in_rs = rs.loc[pid] if pid in rs.index else None
        age = (feb1 - bd[pid]).days / 365.25 if pid in bd else (
            (feb1 - pd.Timestamp(entry["birth_date"])).days / 365.25 if entry["birth_date"] else np.nan)
        acq_d = acq["acq_date"]
        in_season = pd.notna(acq_d) and acq_d >= rs_start
        eligible_rs = rs_games[rs_games.game_date >= (acq_d if in_season else rs_start)] if pd.notna(acq_d) else rs_games
        players.append(dict(
            season="%d-%s" % (year - 1, str(year)[2:]), team=abbr, player=x.player_name, player_id=pid, bref=entry["href"],
            po_minutes=float(x.mins), po_gp=int(x.gp), rs_minutes=float(in_rs.mins) if in_rs is not None else 0.0,
            rs_gp=int(in_rs.gp) if in_rs is not None else 0, age_feb1=round(age, 1),
            on_team_prior_season=pid in prior, acq_type=acq["acq_type"],
            acq_date=acq_d.strftime("%Y-%m-%d") if pd.notna(acq_d) else "", acq_text=acq["acq_text"],
            in_season_acquisition=bool(in_season),
            rs_games_missed=int(len(eligible_rs) - (in_rs.gp if in_rs is not None else 0)),
            po_games_missed=int(len(po_games) - x.gp)))
    P = pd.DataFrame(players)
    rs_all, po_all = player_minutes(sid_rs, tid), po
    top5_rs = rs_all.mins.sort_values(ascending=False).head(5).sum() / rs_all.mins.sum()
    top5_po = po_all.mins.sort_values(ascending=False).head(5).sum() / po_all.mins.sum()
    cont_share = po_all[po_all.player_id.astype(int).isin(prior)].mins.sum() / po_all.mins.sum()
    net_rs, net_po = net_ratings(sid_rs), net_ratings(sid_po)
    gap_a, gap_b, gap_days = all_star_break(sid_rs, year)
    net_post = net_ratings(sid_rs, gap_b.strftime("%Y-%m-%d"))
    st = standings(sid_rs)
    row = dict(
        season="%d-%s" % (year - 1, str(year)[2:]), team=abbr, franchise=franchise,
        record="%d-%d" % (st.loc[abbr].w, st.loc[abbr].l), conf=st.loc[abbr].conf,
        seed_bref=tp["finish"], seed_warehouse=int(st.loc[abbr].conf_rank),
        net_rs=round(float(net_rs.loc[abbr].net), 2), net_rs_rank=int(net_rs.loc[abbr]["rank"]),
        net_rs_bref=tp["bref_net"], net_rs_rank_bref=tp["bref_net_rank"],
        all_star_break="%s to %s (%d days)" % (gap_a.strftime("%Y-%m-%d"), gap_b.strftime("%Y-%m-%d"), gap_days),
        net_post_asb=round(float(net_post.loc[abbr].net), 2), net_post_asb_rank=int(net_post.loc[abbr]["rank"]),
        post_asb_games=int(net_post.loc[abbr].n),
        net_po=round(float(net_po.loc[abbr].net), 2), net_po_minus_rs=round(float(net_po.loc[abbr].net - net_rs.loc[abbr].net), 2),
        po_games=len(po_games),
        top8_drafted=int((P.acq_type.str.startswith("drafted")).sum()), top8_traded=int((P.acq_type == "traded for").sum()),
        top8_signed=int((P.acq_type == "signed").sum()), top8_unknown=int((P.acq_type == "unknown").sum()),
        top8_mean_age=round(float(P.age_feb1.mean()), 1), top8_oldest=round(float(P.age_feb1.max()), 1),
        top8_returning=int(P.on_team_prior_season.sum()), returning_po_minutes_share=round(float(cont_share), 3),
        top8_rs_games_missed=int(P.rs_games_missed.sum()), top8_po_games_missed=int(P.po_games_missed.sum()),
        top5_share_rs=round(float(top5_rs), 3), top5_share_po=round(float(top5_po), 3),
        in_season_moves="; ".join("%s (%s, %s)" % (x.player, x.acq_type, x.acq_date) for _, x in P[P.in_season_acquisition].iterrows()) or "none",
        preseason_title_odds="", preseason_odds_source="")
    row.update(preseason_odds(year, abbr))
    if tp["finish"] is not None and tp["finish"] != row["seed_warehouse"]:
        r.note("%s: conference finish differs, Basketball-Reference %d vs warehouse standings %d (tie-break approximated)"
               % (row["season"], tp["finish"], row["seed_warehouse"]))
    if tp["bref_net"] is not None and abs(tp["bref_net"] - row["net_rs"]) > 0.6:
        r.note("%s: net rating differs, Basketball-Reference %.1f vs warehouse %.2f" % (row["season"], tp["bref_net"], row["net_rs"]))
    return row, P


def paragraph(row, P):
    def nth(n):
        return "%d%s" % (n, "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))
    seed = row["seed_bref"] if row["seed_bref"] is not None else row["seed_warehouse"]
    conf = "West" if row["conf"] == "W" else "East"
    s = ("The %s %s went %s and finished %s in the %s, %s in net rating over the regular season (%+.1f per 100 possessions). "
         % (row["season"], row["franchise"], row["record"], nth(seed), conf, nth(row["net_rs_rank"]), row["net_rs"]))
    d = row["net_post_asb"] - row["net_rs"]
    s += ("After the All-Star break they were %s (%+.1f, %s), " % (
        nth(row["net_post_asb_rank"]), row["net_post_asb"],
        "up %.1f" % d if d >= 0.05 else ("down %.1f" % -d if d <= -0.05 else "unchanged")))
    s += ("and in the playoffs %+.1f, %s the regular season. " % (
        row["net_po"], "%.1f better than" % row["net_po_minus_rs"] if row["net_po_minus_rs"] >= 0.05
        else ("%.1f worse than" % -row["net_po_minus_rs"] if row["net_po_minus_rs"] <= -0.05 else "level with")))
    parts = []
    if row["top8_drafted"]:
        parts.append("%d drafted" % row["top8_drafted"])
    if row["top8_traded"]:
        parts.append("%d traded for" % row["top8_traded"])
    if row["top8_signed"]:
        parts.append("%d signed" % row["top8_signed"])
    if row["top8_unknown"]:
        parts.append("%d unresolved" % row["top8_unknown"])
    s += ("The top eight by playoff minutes: %s; average age %.1f, the oldest %.1f; %d of the eight had played for the "
          "franchise the season before and returning players took %.0f%% of the playoff minutes. "
          % (", ".join(parts), row["top8_mean_age"], row["top8_oldest"], row["top8_returning"],
             100 * row["returning_po_minutes_share"]))
    s += ("Those eight missed %d regular-season games between them and %d of the %d playoff games. "
          % (row["top8_rs_games_missed"], row["top8_po_games_missed"], row["po_games"]))
    s += ("The top five's share of the minutes went from %.0f%% in the regular season to %.0f%% in the playoffs. "
          % (100 * row["top5_share_rs"], 100 * row["top5_share_po"]))
    if row["in_season_moves"] == "none":
        s += "No in-season move touched the top eight; the roster that started in October was the one that won in June."
    else:
        s += "In-season moves that touched the top eight: %s." % row["in_season_moves"]
    return s


def write_doc(r, R, P, years):
    L = ["# C1: champions, extended\n",
         "*As of %s. Every champion from 2015-16, cross-checked against the Basketball-Reference season page before use. "
         "Warehouse box scores for minutes, games, net ratings and standings; Basketball-Reference for the roster "
         "construction; Basketball-Reference's preseason odds pages (courtesy sportsoddshistory.com) for the title price. Run `%s`.*\n" % (AS_OF, r.run_id)]
    L.append("## Construction and continuity\n")
    L.append("| season | champion | seed | top 8: drafted / traded for / signed | mean age (oldest) | returning of 8 | returning share of playoff minutes | in-season moves touching the top 8 | preseason title odds |")
    L.append("|---|---|---:|---|---|---:|---:|---|---|")
    for _, x in R.iterrows():
        L.append("| %s | %s | %s | %d / %d / %d%s | %.1f (%.1f) | %d | %.0f%% | %s | %s |" % (
            x.season, x.team, x.seed_bref if pd.notna(x.seed_bref) else x.seed_warehouse, x.top8_drafted, x.top8_traded,
            x.top8_signed, (" (+%d unresolved)" % x.top8_unknown) if x.top8_unknown else "", x.top8_mean_age, x.top8_oldest,
            x.top8_returning, 100 * x.returning_po_minutes_share, x.in_season_moves, x.preseason_title_odds or "open"))
    L.append("")
    L.append("## Performance, availability and concentration\n")
    L.append("| season | record | RS net (rank) | post-All-Star net (rank, games) | playoff net | playoff minus RS | top-8 games missed RS / playoffs | top-5 minutes share RS -> playoffs |")
    L.append("|---|---|---|---|---:|---:|---|---|")
    for _, x in R.iterrows():
        L.append("| %s | %s | %+.1f (%d) | %+.1f (%d, %d) | %+.1f | %+.1f | %d / %d of %d | %.0f%% -> %.0f%% |" % (
            x.season, x.record, x.net_rs, x.net_rs_rank, x.net_post_asb, x.net_post_asb_rank, x.post_asb_games, x.net_po,
            x.net_po_minus_rs, x.top8_rs_games_missed, x.top8_po_games_missed, x.po_games, 100 * x.top5_share_rs, 100 * x.top5_share_po))
    L.append("")
    L.append("## What changed between October and June\n")
    for _, x in R.iterrows():
        L.append("**%s %s.** %s\n" % (x.season, x.franchise, x.paragraph))
    L.append("## The top eight, every champion\n")
    L.append("| season | player | playoff minutes | acquired | when | age | returning | RS games missed | playoff games missed |")
    L.append("|---|---|---:|---|---|---:|---|---:|---:|")
    for _, x in P.iterrows():
        L.append("| %s | %s | %.0f | %s | %s | %.1f | %s | %d | %d |" % (
            x.season, x.player, x.po_minutes, x.acq_type, x.acq_date, x.age_feb1, "yes" if x.on_team_prior_season else "no",
            x.rs_games_missed, x.po_games_missed))
    L.append("")
    L.append("*Method.* Definitions in the script docstring. The All-Star break is the longest gap in the league schedule "
             "between February 1 and March 15 of each season, from the schedule itself. Net ratings are possession-weighted "
             "means of NBA.com per-game team net rating; the Basketball-Reference season net rating and rank are carried in "
             "the CSV as a cross-check. Seeds are the Basketball-Reference conference finish, checked against warehouse "
             "standings (tie-breaks approximated by point differential). Acquisition types come from each player's "
             "Basketball-Reference transaction log; pages and hashes in `data/bref/manifest.json`. Detail: "
             "`outputs/c1_champions.csv`, `outputs/c1_champion_top8.csv`.")
    path = os.path.join(DOCS, "c1_champions.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", type=int, default=2016)
    ap.add_argument("--last", type=int, default=2026)
    args = ap.parse_args()
    years = list(range(args.first, args.last + 1))
    with runlog.run("c1_champions", inputs={"years": years, "top": TOP}) as r:
        rows, tops = [], []
        for y in years:
            row, P = build(y, r)
            row["paragraph"] = paragraph(row, P)
            rows.append(row)
            tops.append(P)
            r.note("%s %s: seed %s, RS net %+.2f (%d), post-ASB %+.2f (%d), PO %+.2f; top 8 %d/%d/%d, age %.1f, returning %d, "
                   "missed %d/%d, top-5 %.0f%%->%.0f%%; moves: %s" % (
                       row["season"], row["team"], row["seed_bref"], row["net_rs"], row["net_rs_rank"], row["net_post_asb"],
                       row["net_post_asb_rank"], row["net_po"], row["top8_drafted"], row["top8_traded"], row["top8_signed"],
                       row["top8_mean_age"], row["top8_returning"], row["top8_rs_games_missed"], row["top8_po_games_missed"],
                       100 * row["top5_share_rs"], 100 * row["top5_share_po"], row["in_season_moves"]))
        R = pd.DataFrame(rows)
        P = pd.concat(tops, ignore_index=True)
        p_r = os.path.join(OUT_DIR, "c1_champions.csv")
        p_p = os.path.join(OUT_DIR, "c1_champion_top8.csv")
        R.to_csv(p_r, index=False)
        P.to_csv(p_p, index=False)
        unk = P[P.acq_type == "unknown"]
        r.note("acquisition unresolved for %d of %d top-eight players%s" % (
            len(unk), len(P), (": " + "; ".join("%s %s" % (x.season, x.player) for _, x in unk.iterrows())) if len(unk) else ""))
        r.output(p_r, rows=len(R))
        r.output(p_p, rows=len(P))
        path = write_doc(r, R, P, years)
        r.output(path)
        r.note("Basketball-Reference pages in the manifest: %d" % len(bref.manifest()))


if __name__ == "__main__":
    main()
