#!/usr/bin/env python3
"""C4: the in/out ledger for Part 1. Every player and pick in and out of Minnesota since the
end of last season (the 2026 Finals ended 2026-06-13), with dollars and dates, as one table;
and the compile of national outlets' offseason grades with source URLs.

WHO IS IN THE LEDGER. The union of last season's final roster (warehouse `nba_team_rosters`
on 2026-06-13 and the Basketball-Reference 2025-26 team page), the current roster book
(`data/roster_snapshot_2026_27_v3.csv`, Spotrac), every player named in an NBA.com
transaction for Minnesota since 2026-06-14 (warehouse `nba_transactions`), and the 2026
draft picks (Basketball-Reference draft page). Each player's Basketball-Reference
transaction log is read for events after 2026-06-13, classified on the player's own leg of
the event (the clause before the first semicolon, so a four-team trade reads as the
player's move, not the whole deal); the NBA.com feed is the second record of the same
event. A signing by a player who finished last season here is a re-signing (retained). A
player whose last in-season event was a departure (traded or waived before the Finals) is
not an offseason move and is left out. Picks come from `data/traded_picks_2026_offseason.csv`
(two sources per row already) and the draft page.

DOLLARS. 2026-27 salary from the Basketball-Reference contract book in the warehouse
(`nba_player_contracts`) and, as the second source, Spotrac cap hits from the roster book for
players on Minnesota; remaining years and total from the contract book; for a player who
left, his 2026-27 salary on the new team. A waived player carries the Spotrac dead-money
figure (Konchar's book rows predate the waive-and-stretch). Kuminga's terms are also in
`data/transaction_supplement.csv` (two sources there).

SOURCES PER ROW (R8: two URLs per transaction fact). The Basketball-Reference player page
and the rows of `data/c4_transaction_sources.csv`, a hand-built table of reported terms with
two URLs and quotes per move, plus the Spotrac player page for players on Minnesota; a row
with fewer than two URLs is flagged.

    python kuminga/scripts/c4_ledger.py
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

import pandas as pd
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from kuminga.lib import bref, runlog  # noqa: E402
from lib import db                    # noqa: E402

DATA = os.path.join(REPO, "kuminga", "data")
OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
DOCS = os.path.join(REPO, "kuminga", "docs")
ROSTER_V3 = os.path.join(DATA, "roster_snapshot_2026_27_v3.csv")
PICKS = os.path.join(DATA, "traded_picks_2026_offseason.csv")
GRADES = os.path.join(DATA, "c4_offseason_grades.csv")
SOURCES = os.path.join(DATA, "c4_transaction_sources.csv")
MIN_ID = 1610612750
SEASON_END = pd.Timestamp("2026-06-13")
SEASON_START = pd.Timestamp("2025-10-01")
AS_OF = "2026-09-22"
FRANCHISE = "Minnesota Timberwolves"
BREF_TEAM = "/teams/MIN/2026.html"
BREF_DRAFT = "/draft/NBA_2026.html"
ALIASES = {"nahshon hyland": "bones hyland"}


def norm(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    s = re.sub(r"[.'\-]", "", s.lower())
    s = re.sub(r"\b(jr|sr|ii|iii|iv)\b", "", s)
    s = " ".join(s.split())
    return ALIASES.get(s, s)


def bref_roster():
    soup = BeautifulSoup(bref.strip_comments(bref.fetch(BREF_TEAM)), "lxml")
    out = {}
    for tr in soup.find("table", id="roster").tbody.find_all("tr"):
        a = tr.find("td", {"data-stat": "player"}).find("a")
        out[norm(a.get_text(strip=True))] = (a.get_text(strip=True), a["href"])
    return out


def draft_picks():
    soup = BeautifulSoup(bref.strip_comments(bref.fetch(BREF_DRAFT)), "lxml")
    out = []
    for tr in soup.find("table", id="stats").tbody.find_all("tr"):
        team = tr.find("td", {"data-stat": "team_id"})
        pl = tr.find("td", {"data-stat": "player"})
        if team is None or pl is None or not pl.find("a"):
            continue
        out.append(dict(pick=int(tr.find("td", {"data-stat": "pick_overall"}).get_text(strip=True)),
                        team=team.get_text(strip=True), name=pl.get_text(strip=True), href=pl.find("a")["href"]))
    return pd.DataFrame(out)


def transactions(href, name):
    h = bref.strip_comments(bref.fetch(href))
    title = re.search(r"<title>([^<]*)", h)
    if not title or norm(name).split()[-1] not in norm(title.group(1)):
        raise bref.BrefError("%s is not %s's page" % (href, name))
    i = h.find('id="all_transactions"')
    out = []
    for p in BeautifulSoup(h[i:i + 40000] if i >= 0 else "", "lxml").select("p.transaction"):
        txt = p.get_text(" ", strip=True)
        m = re.match(r"([A-Z][a-z]+ \d{1,2}, \d{4})\s*:\s*(.*)", txt)
        if m:
            out.append((pd.Timestamp(m.group(1)), m.group(2)))
    return sorted(out, key=lambda x: x[0])


def classify(t):
    """(how, direction) from the player's own leg of the event."""
    F = re.escape(FRANCHISE)
    leg = t.split(";")[0]
    if re.search(r"Drafted by the %s" % F, leg):
        return "drafted", "in"
    if re.search(r"[Tt]raded by the %s" % F, leg):
        return "traded away", "out"
    if re.search(r"to the %s\b" % F, leg) and re.search(r"traded", leg, re.I):
        return "traded for", "in"
    if re.search(r"Re-signed[^;]*with the %s" % F, leg):
        return "re-signed", "retained"
    if re.search(r"Signed[^;]*with the %s" % F, leg) or re.search(r"Claimed[^;]*by the %s" % F, leg):
        return "signed", "in"
    if re.search(r"(Waived|Released) by the %s" % F, leg):
        return "waived", "out"
    if re.search(r"(Signed|Re-signed)[^;]*with the (?!%s)" % F, leg):
        return "signed elsewhere", "out"
    if re.search(r"Retired", leg):
        return "retired", "out"
    return None, None


def salaries():
    c = db.query("select br_player_id, player_name, team_abbr, season, salary, option_type from nba.nba_player_contracts "
                 "where season >= '2026-27' order by br_player_id, season")
    out = {}
    for (pid, team), gg in c.groupby(["br_player_id", "team_abbr"]):
        out[(pid, team)] = dict(salary_2026_27=int(gg[gg.season == "2026-27"].salary.sum()),
                                years=int(gg.season.nunique()), total=int(gg.salary.sum()),
                                options="; ".join("%s %s" % (x.season, x.option_type) for _, x in gg.iterrows()
                                                  if pd.notna(x.option_type) and x.option_type != "guaranteed"))
    return out


def money(v):
    return "" if v is None or pd.isna(v) else "$" + "{:,.0f}".format(float(v))


def main():
    with runlog.run("c4_ledger", inputs={"roster_v3": ROSTER_V3, "picks": PICKS, "sources": SOURCES}) as r:
        june = db.query("select player, player_id from nba.nba_team_rosters where team_id = %(t)s and season = 2025 "
                        "and roster_date = %(d)s", {"t": MIN_ID, "d": SEASON_END.strftime("%Y-%m-%d")})
        v3 = pd.read_csv(ROSTER_V3)
        v3 = v3[(v3.team_abbr == "MIN") & v3.status.isin(["standard", "pending", "non_guaranteed", "dead_money"])]
        tx = db.query("select transaction_date, transaction_type, transaction_description, player_id, player_slug "
                      "from nba.nba_transactions where team_id = %(t)s and transaction_date > %(d)s order by 1",
                      {"t": MIN_ID, "d": SEASON_END.strftime("%Y-%m-%d")})
        r.note("NBA.com transactions for Minnesota since %s: %d" % (SEASON_END.strftime("%Y-%m-%d"), len(tx)))
        roster = bref_roster()
        draft = draft_picks()
        slugs = db.query("select distinct player_name, br_player_id from nba.nba_player_contracts")
        slug_of = {norm(x.player_name): "/players/%s/%s.html" % (x.br_player_id[0], x.br_player_id) for _, x in slugs.iterrows()}
        for k, (nm, href) in roster.items():
            slug_of.setdefault(k, href)
        for _, x in draft[draft.team == "MIN"].iterrows():
            slug_of.setdefault(norm(x["name"]), x.href)
        june_keys = {norm(x.player) for _, x in june.iterrows()}
        names = {}
        for _, x in june.iterrows():
            names[norm(x.player)] = x.player
        for nm, _ in roster.values():
            names.setdefault(norm(nm), nm)
        for _, x in v3.iterrows():
            names.setdefault(norm(x.player_name), x.player_name)
        for _, x in tx.iterrows():
            nm = " ".join(w.capitalize() for w in str(x.player_slug).split("-"))
            names.setdefault(norm(nm), nm)
        for _, x in draft[draft.team == "MIN"].iterrows():
            names.setdefault(norm(x["name"]), x["name"])
        sal = salaries()
        src = pd.read_csv(SOURCES, dtype=str)
        src["key"] = src.player.map(norm)
        v3_hit = {norm(x.player_name): float(x.cap_hit_2026_27) for _, x in v3.iterrows()}
        v3_status = {norm(x.player_name): x.status for _, x in v3.iterrows()}
        v3_url = {norm(x.player_name): x.spotrac_player_url for _, x in v3.iterrows()}

        rows = []
        for key, nm in sorted(names.items(), key=lambda kv: kv[1].split()[-1]):
            href = slug_of.get(key)
            guessed = href is None
            if guessed:
                last, first = key.split()[-1], key.split()[0]
                href = "/players/%s/%s%s01.html" % (last[0], last[:5], first[:2])
            try:
                ev = transactions(href, nm)
            except bref.BrefError as e:
                ev = None
                r.note("%s: %s" % (nm, e))
            was_here = key in june_keys or key in roster
            is_here = key in v3_hit and v3_status.get(key) != "dead_money"
            srow = src[src.key == key]
            events = []
            if ev is not None:
                season_events = [classify(t)[1] for d, t in ev if SEASON_START <= d <= SEASON_END]
                if season_events and season_events[-1] == "out" and not any(d > SEASON_END for d, _ in ev):
                    continue                              # left in-season, before the Finals
                gone = False
                for d, t in ev:
                    if d <= SEASON_END:
                        continue
                    how, direction = classify(t)
                    if not how:
                        continue
                    if how == "signed" and any(x[2] == "in" and abs((d - x[0]).days) <= 45 for x in events):
                        continue                          # the rookie deal after the draft or the rights trade
                    if how == "signed" and was_here:
                        how, direction = "re-signed", "retained"
                    if direction == "out" and how == "signed elsewhere" and gone:
                        continue                          # his next team's signing is not a Minnesota move
                    if direction == "out":
                        gone = True
                    same = [k for k, e in enumerate(events) if e[0] == d and e[2] == direction]
                    if same:
                        if how.startswith("traded") and not events[same[0]][1].startswith("traded"):
                            events[same[0]] = (d, how, direction, t.split(";")[0][:200])   # the trade names the move
                        continue                          # same day, same direction: recorded once
                    events.append((d, how, direction, t.split(";")[0][:200]))
            if not events:
                if len(srow):
                    q = srow.iloc[0]
                    events.append((pd.to_datetime(q.date, errors="coerce"), q.how, q.direction, q.reported_terms))
                elif was_here and not is_here:
                    events.append((pd.NaT, "no transaction on record since the season ended", "out (status unverified)",
                                   "on the 2025-26 roster, not in the 2026-27 roster book"))
                elif not was_here and is_here:
                    events.append((pd.NaT, "no transaction on record", "in (unverified)", "in the 2026-27 roster book only"))
                else:
                    continue
            elif len(srow) and all(e[1] == "drafted" for e in events) and not is_here:
                q = srow.iloc[0]                          # drafted and unsigned: the sources row says what happened
                events = [(events[0][0], "drafted and unsigned, rights retained", q.direction, q.reported_terms)]
            slug = re.sub(r".*/([a-z0-9]+)\.html$", r"\1", href)
            for d, how, direction, t in events:
                here = direction.startswith("in") or direction == "retained"
                s = sal.get((slug, "MIN")) if here else None
                if s is None and how != "drafted" and not (direction == "out" and not was_here):
                    others = [v for (p, tm), v in sal.items() if p == slug and tm != "MIN"]
                    s = others[0] if others else sal.get((slug, "MIN"))
                salary = s["salary_2026_27"] if s else (v3_hit.get(key) if is_here else None)
                salary_source = ("contract book" + (" + Spotrac" if key in v3_hit else "")) if s else ("Spotrac only" if key in v3_hit else "none")
                if how == "waived" and v3_status.get(key) == "dead_money":
                    salary, salary_source = v3_hit[key], "Spotrac dead money (stretched)"
                urls = ["https://www.basketball-reference.com" + href] if ev is not None else []
                terms = []
                for _, q in srow.iterrows():
                    for col in ("source_1_url", "source_2_url"):
                        if isinstance(q[col], str) and q[col].strip() and q[col] not in urls:
                            urls.append(q[col].strip())
                    if isinstance(q.reported_terms, str):
                        terms.append(q.reported_terms)
                if key in v3_url and isinstance(v3_url[key], str) and v3_url[key] not in urls:
                    urls.append(v3_url[key])
                rows.append(dict(
                    player=nm, direction=direction, how=how, date=d.strftime("%Y-%m-%d") if pd.notna(d) else "", detail=t,
                    salary_2026_27=salary, salary_source=salary_source, spotrac_cap_hit=v3_hit.get(key),
                    contract_years=s["years"] if s else None, contract_total=s["total"] if s else None,
                    options=s["options"] if s else "", reported_terms=" | ".join(terms), sources=" ".join(urls),
                    n_sources=len(urls), bref=href if ev is not None else "", slug_guessed=guessed))
        L = pd.DataFrame(rows)

        picks = pd.read_csv(PICKS)
        prow = []
        for _, x in picks.iterrows():
            direction = "out" if x.from_team == "MIN" else "in"
            prot = x.protection if isinstance(x.protection, str) and x.protection and not x.protection.startswith("n/a") else ""
            label = "%d %s %s" % (x.year, {1: "first-round", 2: "second-round"}.get(x.rnd, str(x.rnd)), x.asset_type.replace("_", " "))
            if prot:
                label += " (%s)" % prot
            prow.append(dict(player=label, direction=direction,
                             how=("to %s" % x.to_team) if direction == "out" else ("from %s" % x.from_team),
                             date="2026-07-10", detail=str(x.condition)[:200] if isinstance(x.condition, str) else "",
                             salary_2026_27=None, salary_source="n/a", spotrac_cap_hit=None, contract_years=None,
                             contract_total=None, options="", reported_terms="",
                             sources=" ".join(u for u in (x.source_url, x.source_url_2) if isinstance(u, str) and u.strip()),
                             n_sources=sum(1 for u in (x.source_url, x.source_url_2) if isinstance(u, str) and u.strip()),
                             bref="", slug_guessed=False))
        L = pd.concat([L, pd.DataFrame(prow)], ignore_index=True)
        L["date_sort"] = pd.to_datetime(L.date, errors="coerce")
        L = L.sort_values(["date_sort", "direction", "player"]).drop(columns="date_sort")
        p_l = os.path.join(OUT_DIR, "c4_ledger.csv")
        L.to_csv(p_l, index=False)
        ins = L[(L.direction == "in") & L.salary_2026_27.notna()]
        outs = L[(L.direction == "out") & L.salary_2026_27.notna()]
        r.note("in: %d players with a 2026-27 salary, %s; out: %d, %s; retained: %d; rows %d; single-sourced %d; "
               "guessed slugs %d" % (len(ins), money(ins.salary_2026_27.sum()), len(outs), money(outs.salary_2026_27.sum()),
                                     int((L.direction == "retained").sum()), len(L), int((L.n_sources < 2).sum()),
                                     int(L.slug_guessed.fillna(False).astype(bool).sum())))
        for _, x in L.iterrows():
            r.note("  %s | %-9s | %-42s | %-38s | %s" % (x.date or "          ", x.direction, x.player[:42], x.how[:38], money(x.salary_2026_27)))
        r.output(p_l, rows=len(L))
        write_doc(r, L, ins, outs)


def write_doc(r, L, ins, outs):
    G = pd.read_csv(GRADES, dtype=str)
    Lines = ["# C4: the in/out ledger and the grades\n",
             "*As of %s. Every player and pick in and out of Minnesota since the 2026 Finals ended on 2026-06-13, "
             "from the Basketball-Reference transaction logs and the NBA.com feed, dollars from the contract book "
             "and Spotrac. Run `%s`.*\n" % (AS_OF, r.run_id)]
    Lines.append("## The ledger\n")
    Lines.append("| date | direction | player or pick | how | 2026-27 salary | years, total | options | reported terms | sources |")
    Lines.append("|---|---|---|---|---:|---|---|---|---|")
    for _, x in L.iterrows():
        urls = str(x.sources).split() if isinstance(x.sources, str) else []
        srcs = " ".join("[%d](%s)" % (i + 1, u) for i, u in enumerate(urls))
        if len(urls) < 2:
            srcs += " (single-sourced)"
        yt = ("%d, %s" % (x.contract_years, money(x.contract_total))) if pd.notna(x.contract_years) else ""
        Lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            x.date, x.direction, x.player, x.how, money(x.salary_2026_27), yt, x.options if isinstance(x.options, str) else "",
            (x.reported_terms if isinstance(x.reported_terms, str) else "")[:200], srcs))
    Lines.append("")
    Lines.append("**Totals, 2026-27 salary.** In: %s across %d players (Green counts on both sides: in on July 10, out on "
                 "August 29). Out: %s across %d players, at their 2026-27 salary on the new team or, for a waived player, "
                 "the dead money carried. Rows marked unverified have no transaction on record in either source since the "
                 "season ended.\n" % (money(ins.salary_2026_27.sum()), len(ins), money(outs.salary_2026_27.sum()), len(outs)))
    Lines.append("## National outlets' grades\n")
    whole = G[(G.status.str.startswith("read")) & G.scope.str.startswith("national") & G.what_was_graded.str.contains("whole offseason", na=False)]
    Lines.append("Every piece fetched and read is listed with the grade exactly as written and what it graded; pieces "
                 "found but not read are listed with the reason. The whole-offseason grades from national outlets: %s.\n"
                 % "; ".join("%s %s" % (x.outlet, x.grade_or_rank) for _, x in whole.iterrows()))
    Lines.append("| outlet | scope | author | date | grade or rank | what was graded | rationale | source | status |")
    Lines.append("|---|---|---|---|---|---|---|---|---|")
    for _, x in G.iterrows():
        Lines.append("| %s | %s | %s | %s | %s | %s | %s | [link](%s) | %s |" % (
            x.outlet, x.scope, x.author, x.date, x.grade_or_rank, x.what_was_graded,
            ('"%s"' % x.rationale_quote) if isinstance(x.rationale_quote, str) and x.rationale_quote else "", x.url, x.status))
    Lines.append("")
    Lines.append("*Method.* Ledger membership and classification in the script docstring. Salary: `nba.nba_player_contracts` "
                 "(Basketball-Reference contract book, scraped 2026-09-22) with Spotrac cap hits from the roster book as the "
                 "second source for players on Minnesota. Picks: `data/traded_picks_2026_offseason.csv`. Grades: "
                 "`data/c4_offseason_grades.csv`, compiled 2026-09-22 from pages fetched that day. Reported terms and the "
                 "second and third URLs per move: `data/c4_transaction_sources.csv`.")
    path = os.path.join(DOCS, "c4_ledger.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(Lines) + "\n")
    r.output(path)


if __name__ == "__main__":
    main()
