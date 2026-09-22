#!/usr/bin/env python3
"""C2: the Edwards clock. The hazard and walk-year finding from pick2033 Part 1 ("Pricing the
LaMelo Trade, Part 1: The Tenure Bet"), pulled forward and restated against Anthony
Edwards's current contract and the CBA's dates. One table, one paragraph, and the backing.

WHAT IS PULLED FORWARD. The Part 1 model is a league-wide discrete-time hazard on star
tenures (Model B, M2 FINAL: contract covariates included, C-index 0.907 on the sealed
holdout, calibration slope 1.413 outside the 0.8 to 1.2 window and printed as a red cell).
Its Edwards export gives, season by season 2026-27 to 2032-33, the probability he departs
that season and the cumulative probability he has departed, under two team-success
scenarios: the Wolves winning at a .600 clip and sagging to .450. That is the conditional
the piece needs, P(on another team within N seasons | contention status). Beside it, the
RAW departure rates from the same spells at the same contract stage (two seasons left
after the current one) and in the walk year itself, split by the team's two-year win
percentage, with the counts. Nothing is refit here.

THE CLOCK. Contract from two sources (Basketball-Reference contracts via the warehouse,
HoopsHype), the extension signing date from two (NBA.com transactions via the warehouse,
the Basketball-Reference player page), the rules from the 2023 CBA text itself (NBPA copy,
sha256 in data/c2_pick2033_inputs.sha256, page numbers cited) and the 65-game consequence
from two reports. No date here is derived from memory.

    python kuminga/scripts/c2_edwards_clock.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from kuminga.lib import bref, runlog  # noqa: E402
from lib import db                    # noqa: E402

DATA = os.path.join(REPO, "kuminga", "data")
OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
DOCS = os.path.join(REPO, "kuminga", "docs")
HAZARD = os.path.join(DATA, "c2_edwards_hazard_FINAL.json")
META = os.path.join(DATA, "c2_star_spells_final.meta.json")
VALID = os.path.join(DATA, "c2_model_b_hazard_M2_FINAL.md")
STATS = os.path.join(DATA, "c2_hazard_m2_stats.json")
SPELLS = os.path.join(DATA, "c2_star_spell_seasons_with_contract.csv")
CBA_PDF = os.path.join(DATA, "c2_cba_2023.pdf")
CBA_URL = ("https://imgix.cosmicjs.com/25da5eb0-15eb-11ee-b5b3-fbd321202bdf-Final-2023-NBA-"
           "Collective-Bargaining-Agreement-6-28-23.pdf")
HOOPSHYPE = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27.csv")
EDWARDS = 1630162
BREF_EDWARDS = "/players/e/edwaran01.html"
AS_OF = "2026-09-22"
STAGE_YEARS_LEFT = 2          # seasons remaining after the current one, Edwards in 2026-27

# the CBA pages quoted (PDF page numbers of the NBPA copy; the printed folio differs by 24)
CBA_PAGES = {
    "dvpe_definition": (27, "Article I, Section 1(r)"),
    "higher_max": (60, "Article II, Section 7(a)(i)"),
    "dvpe_conditions": (62, "Article II, Section 7(c)(ii)"),
    "veteran_ext_timing": (274, "Article VII, Section 7(a)(1)"),
    "games_played_honors": (456, "Article XXIX, Section 6(a)"),
}
REPORTS = [
    ("Fadeaway World, syndicated by Yahoo Sports, 2026-05-30 (Vishwesha Kumar)",
     "https://sports.yahoo.com/articles/anthony-edwards-loses-eligibility-300m-113622348.html",
     "Edwards played in just 61 regular-season games, falling short of the NBA's mandatory 65-game "
     "threshold required to qualify for All-NBA teams and major end-of-season awards. [...] Edwards is "
     "no longer eligible for a four-year supermax extension worth roughly $300 million this summer [and] "
     "is currently eligible for a much smaller two-year extension worth approximately $122 million. [...] "
     "If Edwards reaches the 65-game threshold next season and earns another All-NBA selection, he would "
     "immediately become eligible for the same four-year, $300 million supermax extension in 2027."),
    ("Heavy, 2026-08-05 (Michael Kaskey-Blomain)",
     "https://heavy.com/sports/nba/minnesota-timberwolves/how-anthony-edwards-can-become-eligible-supermax-extension-timberwolves/",
     "the Timberwolves' superstar was ineligible for All-NBA because he fell short of the 65-games-played "
     "threshold. [...] If Edwards had played four more games, he would have been eligible to sign a "
     "four-year, $301 million supermax extension next summer. [...] Edwards will need All-NBA, MVP or "
     "Defensive Player of the Year honors in 2026-27 to become eligible for that deal."),
]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def cba_excerpts(r):
    """Pull the quoted clauses out of the PDF by page so the doc cites text, not memory."""
    from pypdf import PdfReader
    rd = PdfReader(CBA_PDF)
    out = {}
    want = {
        "dvpe_definition": ("Designated Veteran Player Extension", 900),
        "higher_max": ("Higher Max Criteria", 900),
        "dvpe_conditions": ("has one Season, or two Seasons", 1100),
        "veteran_ext_timing": ("a Player Contract covering a", 1500),
        "games_played_honors": ("Games Played Requirement", 900),
    }
    for k, (page, cite) in CBA_PAGES.items():
        txt = " ".join((rd.pages[page - 1].extract_text() or "").split())
        needle, n = want[k]
        i = txt.find(needle)
        if i < 0:
            raise RuntimeError("CBA excerpt anchor not found on page %d: %s" % (page, needle))
        start = max(0, txt.rfind(".", 0, i) + 1) if k != "veteran_ext_timing" else max(0, i - 260)
        out[k] = dict(page=page, cite=cite, text=txt[start:start + n].strip())
    r.note("CBA excerpts extracted from %d pages of the 2023 CBA (sha256 %s)" % (len(out), sha(CBA_PDF)[:16]))
    return out


def contract(r):
    wh = db.query("select season, salary, option_type, source_url, scraped_at from nba.nba_player_contracts "
                  "where br_player_id = 'edwaran01' order by season")
    hh = pd.read_csv(HOOPSHYPE)
    hh = hh[hh.nba_player_id.astype(str).str.replace(".0", "", regex=False) == str(EDWARDS)].iloc[0]
    hh_years = {"2026-27": hh.salary_2026_27, "2027-28": hh.salary_2027_28, "2028-29": hh.salary_2028_29}
    for _, x in wh.iterrows():
        assert int(hh_years[x.season]) == int(x.salary), "contract sources disagree on %s" % x.season
    assert (wh.option_type == "guaranteed").all() and str(hh.player_option_flag).upper() == "FALSE" \
        and str(hh.team_option_flag).upper() == "FALSE", "an option appears in one source"
    assert pd.isna(hh.salary_2029_30), "HoopsHype shows a 2029-30 salary"
    r.note("contract: %s, no options, both sources agree; walk year 2028-29" %
           ", ".join("%s $%s" % (x.season, "{:,}".format(int(x.salary))) for _, x in wh.iterrows()))
    tx = db.query("select transaction_date, transaction_description from nba.nba_transactions "
                  "where player_id = %(p)s and transaction_description ilike '%%Extension%%' order by 1",
                  {"p": EDWARDS})
    assert len(tx) == 1, "expected one extension transaction"
    ext_date = pd.Timestamp(tx.transaction_date.iloc[0]).strftime("%Y-%m-%d")
    html = bref.strip_comments(bref.fetch(BREF_EDWARDS))
    m = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})\s*</strong>?:?\s*Signed a contract extension with the Minnesota", html)
    if m is None:
        m = re.search(r"Signed extension ([A-Z][a-z]+, [A-Z][a-z]+ \d{1,2}, \d{4})", html)
    assert m, "B-Ref extension date not found"
    bref_date = pd.Timestamp(m.group(1).split(", ", 1)[1] if m.group(1).count(",") == 2 else m.group(1)).strftime("%Y-%m-%d")
    assert bref_date == ext_date, "extension date disagrees: NBA.com %s vs B-Ref %s" % (ext_date, bref_date)
    games = int(db.query("select count(*) from nba.nba_player_stats s join nba.nba_games g on g.game_id = s.game_id "
                         "and g.team_id = s.team_id where s.player_id = %(p)s and g.season_type = 'Regular Season' "
                         "and s.season_year = '2025-26' and s.minutes_played > 0", {"p": EDWARDS}).iloc[0, 0])
    r.note("rookie scale extension signed %s (NBA.com transactions and B-Ref agree); 2025-26 regular-season games %d" % (ext_date, games))
    return wh, ext_date, games, bref.manifest()[bref.key_of(BREF_EDWARDS)]


def stage_table(r):
    d = pd.read_csv(SPELLS).sort_values(["spell_id", "season"])
    rec = {}
    for sid, g in d.groupby("spell_id"):
        ev = g.event_departure.tolist()
        n = len(g)
        for i, s in enumerate(g.season.tolist()):
            for N in (1, 2, 3):
                win = ev[i:i + N]
                rec[(sid, s, N)] = (any(win), (i + N <= n) or any(win))
    for N in (1, 2, 3):
        d["dep%d" % N] = [rec[(s, y, N)][0] for s, y in zip(d.spell_id, d.season)]
        d["obs%d" % N] = [rec[(s, y, N)][1] for s, y in zip(d.spell_id, d.season)]

    def tier(w):
        return ".600 or better" if w >= 0.6 else (".500 to .600" if w >= 0.5 else "under .500")
    d["tier"] = d.team_win_pct_2yr.map(tier)
    rows = []
    st = d[d.contract_years_remaining == STAGE_YEARS_LEFT]
    for N in (1, 2, 3):
        o = st[st["obs%d" % N]]
        rows.append(dict(stage="two seasons left after this one", horizon="within %d season%s" % (N, "" if N == 1 else "s"),
                         tier="all", n=len(o), spells=o.spell_id.nunique(), departed=int(o["dep%d" % N].sum()),
                         rate=float(o["dep%d" % N].mean())))
        for t, g in o.groupby("tier"):
            rows.append(dict(stage="two seasons left after this one", horizon="within %d season%s" % (N, "" if N == 1 else "s"),
                             tier=t, n=len(g), spells=g.spell_id.nunique(), departed=int(g["dep%d" % N].sum()),
                             rate=float(g["dep%d" % N].mean())))
    w = d[d.contract_years_remaining == 0]
    rows.append(dict(stage="walk year", horizon="that season", tier="all", n=len(w), spells=w.spell_id.nunique(),
                     departed=int(w.event_departure.sum()), rate=float(w.event_departure.mean())))
    for t, g in w.groupby("tier"):
        rows.append(dict(stage="walk year", horizon="that season", tier=t, n=len(g), spells=g.spell_id.nunique(),
                         departed=int(g.event_departure.sum()), rate=float(g.event_departure.mean())))
    R = pd.DataFrame(rows)
    r.note("stage rows: %d star-seasons with two seasons left (%d spells); walk-year rows: %d" %
           (len(st), st.spell_id.nunique(), len(w)))
    return R, d


def clock_table(hz, ext_date, games):
    seasons = {2027: "2026-27", 2028: "2027-28", 2029: "2028-29", 2030: "2029-30", 2031: "2030-31",
               2032: "2031-32", 2033: "2032-33"}
    ages = {2027: 25, 2028: 26, 2029: 27, 2030: 28, 2031: 29, 2032: 30, 2033: 31}   # age on Feb 1, B-Ref convention
    markers = {
        2027: "Standard veteran extension window open since %s, the third anniversary of the %s rookie scale "
              "extension (5- or 6-season contracts extend after the third anniversary, Art. VII Sec. 7(a)(1)); "
              "reported at two years, about $122 million. The supermax (Designated Veteran) window is closed this "
              "summer: the 61-game 2025-26 fell short of the 65 games All-NBA requires (Art. XXIX Sec. 6)."
              % (pd.Timestamp(ext_date).replace(year=pd.Timestamp(ext_date).year + 3).strftime("%B %-d, %Y")
                 if os.name != "nt" else pd.Timestamp(ext_date).replace(year=pd.Timestamp(ext_date).year + 3).strftime("%B %d, %Y").replace(" 0", " "),
                 pd.Timestamp(ext_date).strftime("%B %d, %Y").replace(" 0", " ")),
        2028: "July 2027: Designated Veteran Player Extension window opens (seven Years of Service, one or two "
              "seasons left, drafted by the team, Art. II Sec. 7(c)(ii)) IF he is All-NBA in 2026-27, which needs "
              "65 games; six seasons from signing (Art. I Sec. 1(r)), so two remaining plus four new, the reported "
              "four-year deal.",
        2029: "Walk year. July 2028: the last extension window before free agency; the Designated Veteran version "
              "needs All-NBA in 2027-28 (the two-of-three route is closed by the 2025-26 miss). Contract ends "
              "June 30, 2029; unrestricted free agent July 2029.",
        2030: "Model assumption from Part 1: a star who survives his walk year re-signs on a fresh four-year deal, "
              "so the clock restarts.",
        2031: "", 2032: "", 2033: "Fresh deal's own cliff approaches; the hazard climbs back."}
    rows = []
    for scen, sname in (("central_win60", "win600"), ("decline_win45", "win450")):
        s = hz["scenarios"][scen]
        for a, c in zip(s["annual"], s["cumulative"]):
            assert a["season"] == c["season"]
            rows.append(dict(season=seasons[a["season"]], model_season=a["season"], age=ages[a["season"]],
                             seasons_left_after=s["contract_years_remaining_path"][str(a["season"])],
                             scenario=sname, team_win_pct_2yr=s["scenario_team_win_pct_2yr"],
                             hazard=a["hazard_mean"], hazard_lo80=a["lo80"], hazard_hi80=a["hi80"],
                             cumulative=c["p_departed_by_mean"], cumulative_lo80=c["lo80"], cumulative_hi80=c["hi80"],
                             cba_marker=markers[a["season"]]))
    return pd.DataFrame(rows)


def pct(x):
    return "%.0f%%" % (100 * x) if x >= 0.095 else "%.1f%%" % (100 * x)


def walk_multiple(valid_lines):
    """The walk-year odds multiple from the M2 coefficient on standardized contract years
    remaining and the standardization constant: two seasons left against zero."""
    import math
    b = float(re.search(r"b_contract_z ([-+]?\d+\.\d+)", " ".join(valid_lines)).group(1))
    sd = float(json.load(open(STATS, encoding="utf-8"))["cyr_sd"])
    return dict(b=b, sd=sd, ratio=math.exp(-b * STAGE_YEARS_LEFT / sd))


def write_doc(r, T, S, meta, valid_lines, wh, ext_date, games, ex, bman):
    mult = walk_multiple(valid_lines)
    L = ["# C2: the Edwards clock\n",
         "*As of %s. Pulled forward from pick2033 Part 1 (Model B, M2 FINAL, freeze `%s`), restated against the "
         "contract and the 2023 CBA. Run `%s`.*\n" % (AS_OF, meta["freeze_hash"], r.run_id)]
    L.append("## The table\n")
    L.append("P(Anthony Edwards departs) by season, from the league-wide star-tenure hazard model, under two team paths. "
             "The hazard is the chance he leaves in that season given he is still here; the cumulative column is the "
             "chance he has left by then. 80%% intervals in brackets. Sample: %d star spells, %d player-seasons, "
             "%d departures, 1990 to 2026.\n" % (meta["n_spells"], meta["n_rows"], 228))
    L.append("| season | age | seasons left after this one | hazard, team at .600 | hazard, team at .450 | departed by then, .600 | departed by then, .450 | the clock |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---|")
    a = T[T.scenario == "win600"].set_index("model_season")
    b = T[T.scenario == "win450"].set_index("model_season")
    for ms in a.index:
        x, y = a.loc[ms], b.loc[ms]
        L.append("| %s | %d | %d | %s [%s, %s] | %s [%s, %s] | %s [%s, %s] | %s [%s, %s] | %s |" % (
            x.season, x.age, x.seasons_left_after, pct(x.hazard), pct(x.hazard_lo80), pct(x.hazard_hi80),
            pct(y.hazard), pct(y.hazard_lo80), pct(y.hazard_hi80), pct(x.cumulative), pct(x.cumulative_lo80),
            pct(x.cumulative_hi80), pct(y.cumulative), pct(y.cumulative_lo80), pct(y.cumulative_hi80), x.cba_marker))
    L.append("")
    L.append("## The paragraph\n")
    c29a, c29b = a.loc[2029], b.loc[2029]
    c33a, c33b = a.loc[2033], b.loc[2033]
    st2 = S[(S.stage == "two seasons left after this one") & (S.horizon == "within 3 seasons")].set_index("tier")
    wy = S[S.stage == "walk year"].set_index("tier")
    L.append("Edwards is two seasons from his walk year. His deal runs %s, with no options in it, so the summer "
             "of 2029 is the first time he can leave on his own terms, and the history of stars in exactly that "
             "position says the leaving, when it happens, happens then: across %d star spells since 1990, the "
             "departure odds in a walk year run about seventy times the mid-contract odds. Run his profile through "
             "the model with the Wolves winning at a .600 clip and his chance of departing is %s this season, %s next, "
             "and %s at the 2029 cliff, %s cumulative by that summer and %s by 2033 [%s, %s]. Let the team sag to .450 "
             "and the cliff is %s, the cumulative %s by 2029 and %s by 2033 [%s, %s]. The raw history says the same "
             "thing without a model: of %d star-seasons with two years left, %s had departed within three seasons, "
             "and in the walk year itself stars on .600 teams left %s of the time (%d cases) against %s on sub-.500 "
             "teams (%d). What the clock adds is the CBA's dates. He has been eligible for a standard extension "
             "since %s, two years and about $122 million by the reporting; the supermax window opens in July 2027 "
             "only if he makes All-NBA in 2026-27, which after a 61-game 2025-26 means playing 65 games first; and "
             "if that window closes too, the last one before free agency is July 2028, which needs an All-NBA "
             "2027-28. Every one of those dates is a place where a season that goes wrong turns into a departure "
             "probability, which is why the title odds in this series and the retention odds in Part 1 are the same "
             "bet."
             % (" through ".join(["2026-27", "2028-29"]), meta["n_spells"],
                pct(a.loc[2027].hazard), pct(a.loc[2028].hazard), pct(c29a.hazard), pct(c29a.cumulative),
                pct(c33a.cumulative), pct(c33a.cumulative_lo80), pct(c33a.cumulative_hi80),
                pct(c29b.hazard), pct(c29b.cumulative), pct(c33b.cumulative), pct(c33b.cumulative_lo80), pct(c33b.cumulative_hi80),
                int(st2.loc["all", "n"]), pct(st2.loc["all", "rate"]),
                pct(wy.loc[".600 or better", "rate"]), int(wy.loc[".600 or better", "n"]),
                pct(wy.loc["under .500", "rate"]), int(wy.loc["under .500", "n"]),
                pd.Timestamp(ext_date).replace(year=pd.Timestamp(ext_date).year + 3).strftime("%B %d, %Y").replace(" 0", " ")))
    L.append("")
    L.append("## Backing: the raw rates at his stage, by the team's two-year win percentage\n")
    L.append("| stage | horizon | team | star-seasons | spells | departed | rate |")
    L.append("|---|---|---|---:|---:|---:|---:|")
    for _, x in S.iterrows():
        L.append("| %s | %s | %s | %d | %d | %d | %s |" % (x.stage, x.horizon, x.tier, x.n, x.spells, x.departed, pct(x.rate)))
    L.append("")
    L.append("The stage rows are read forward from every star-season with exactly two seasons left on the contract "
             "after that one; a window is counted only when it is fully observed or the departure falls inside it. "
             "The .500-to-.600 tier is not monotone in the middle row, which is what %d-to-%d-case cells do; the model "
             "smooths across all of it. The walk-year rows are the cleaner conditional.\n"
             % (int(S[(S.stage != "walk year") & (S.tier != "all")].n.min()), int(S[(S.stage != "walk year") & (S.tier != "all")].n.max())))
    L.append("## Backing: the model's scorecard, unchanged from Part 1\n")
    for ln in valid_lines:
        L.append("- " + ln.lstrip("- ").strip())
    L.append("- the walk-year multiple, recomputed here from the M2 coefficient and the standardization constant: "
             "exp(%.3f x 2 / %.4f) = %.0f times the odds with two seasons left, against Part 1's \"roughly seventy\" "
             "(80%% interval 43 to 104 in the draft, from the full posterior)" % (-mult["b"], mult["sd"], mult["ratio"]))
    L.append("")
    L.append("## Sources\n")
    L.append("**Contract.** Basketball-Reference contracts via the warehouse `nba.nba_player_contracts` (scraped %s): %s; "
             "HoopsHype contract file (`offseason/data/nba_contracts_2026_27.csv`, 2026-06-06) agrees on every figure and "
             "shows no option. Rookie scale extension signed %s: NBA.com transactions (warehouse `nba.nba_transactions`) "
             "and the Basketball-Reference player page (cached, sha256 `%s`, fetched %s) agree. 2025-26 regular-season "
             "games: %d, warehouse box scores.\n"
             % (str(wh.scraped_at.iloc[0])[:10], "; ".join("%s $%s" % (x.season, "{:,}".format(int(x.salary))) for _, x in wh.iterrows()),
                ext_date, bman["sha256"][:16], bman["fetched_at"][:10], games))
    L.append("**CBA.** 2023 NBA-NBPA Collective Bargaining Agreement, NBPA copy (`%s`, sha256 in `data/c2_pick2033_inputs.sha256`). "
             "Quoted, by PDF page:\n" % CBA_URL)
    for k, v in ex.items():
        L.append("- *%s (PDF p. %d):* \"%s\"" % (v["cite"], v["page"], v["text"]))
    L.append("")
    L.append("**Reporting on the 65-game consequence.**\n")
    for who, url, quote in REPORTS:
        L.append("- %s: \"%s\" (%s)" % (who, quote, url))
    L.append("")
    L.append("**Model.** pick2033 `outputs/json/edwards_hazard_FINAL.json`, `outputs/validation/model_b_hazard_M2_FINAL.md`, "
             "`data/staged/star_spells_final.parquet` with `contract_years_backfill.parquet` (copies and hashes under "
             "`kuminga/data/c2_*`). The Part 1 draft's own wording of the sample and the walk-year multiple is in "
             "`pick2033/docs/drafts/stage1_edwards_hazard_draft_v4.md`.")
    path = os.path.join(DOCS, "c2_edwards_clock.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def main():
    with runlog.run("c2_edwards_clock", inputs={"hazard": HAZARD, "spells": SPELLS, "cba": CBA_PDF,
                                                "hazard_sha256": sha(HAZARD), "spells_sha256": sha(SPELLS)}) as r:
        hz = json.load(open(HAZARD, encoding="utf-8"))
        meta = json.load(open(META, encoding="utf-8"))
        assert hz["tag"] == "FINAL" and hz["freeze_hash"] == meta["freeze_hash"], "hazard export and spells freeze differ"
        valid_lines = [ln for ln in open(VALID, encoding="utf-8").read().splitlines() if ln.startswith("- ")]
        r.note("model: %s; %s" % (hz["contract_covariate"], "; ".join(valid_lines[:3])))
        ex = cba_excerpts(r)
        mult = walk_multiple(valid_lines)
        wh, ext_date, games, bman = contract(r)
        S, _ = stage_table(r)
        T = clock_table(hz, ext_date, games)
        p_t = os.path.join(OUT_DIR, "c2_edwards_clock.csv")
        p_s = os.path.join(OUT_DIR, "c2_stage_departures.csv")
        T.to_csv(p_t, index=False)
        S.to_csv(p_s, index=False)
        for scen in ("win600", "win450"):
            x = T[T.scenario == scen].set_index("model_season")
            r.note("%s: hazard 2027 %s, 2028 %s, 2029 %s; cumulative by 2029 %s, by 2033 %s [%s, %s]" % (
                scen, pct(x.loc[2027].hazard), pct(x.loc[2028].hazard), pct(x.loc[2029].hazard),
                pct(x.loc[2029].cumulative), pct(x.loc[2033].cumulative), pct(x.loc[2033].cumulative_lo80),
                pct(x.loc[2033].cumulative_hi80)))
        for _, x in S[S.tier == "all"].iterrows():
            r.note("raw %s, %s: %d star-seasons, %s departed" % (x.stage, x.horizon, x.n, pct(x.rate)))
        facts = [("ext_signed", ext_date), ("games_2025_26", games), ("walk_year", "2028-29"),
                 ("free_agency", "2029-07-01"), ("n_spells", meta["n_spells"]), ("n_rows", meta["n_rows"]),
                 ("n_departures", 228), ("walk_multiple", round(mult["ratio"], 1)),
                 ("c_index", 0.907), ("calibration_slope", 1.413)]
        for _, x in wh.iterrows():
            facts.append(("salary_%s" % x.season.replace("-", "_"), int(x.salary)))
        p_f = os.path.join(OUT_DIR, "c2_facts.csv")
        pd.DataFrame(facts, columns=["key", "value"]).to_csv(p_f, index=False)
        r.output(p_f, rows=len(facts))
        r.output(p_t, rows=len(T))
        r.output(p_s, rows=len(S))
        path = write_doc(r, T, S, meta, valid_lines, wh, ext_date, games, ex, bman)
        r.output(path)


if __name__ == "__main__":
    main()
