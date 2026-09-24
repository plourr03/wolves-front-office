#!/usr/bin/env python3
"""Audit the series prose number by number: bind every figure in the articles to the source
it came from, and fail if any number is unbound, misbound or wrongly rounded.

The prose gate (`gate_prose.py`) only asks whether a number exists SOMEWHERE in the
project's own figures. That catches invented numbers and it does not catch a number used
for the wrong claim, which is the failure that matters once the prose is written. This
script asks the harder question: for this sentence, is THIS the right figure?

HOW IT WORKS. `CLAIMS` binds a verbatim phrase from an article to one or more source keys.
For each binding the script checks that

  1. the phrase appears in the file exactly once,
  2. every number inside the phrase matches one of its bound keys, either digit for digit
     or as a correct rounding at the precision the prose uses (so "$33.3 million" may
     stand for $33,333,334 but "$33.4 million" may not), and
  3. every bound key is actually used by a number in its phrase, so a stale binding is a
     failure rather than dead weight.

Then the COVERAGE pass walks every number in every article and fails on any number that no
binding claims and no structural rule excuses (a season, a date, a heading, a list marker,
a code span, a league constant, or a number inside a per-champion section of Part 3, which
is scoped to that champion's own row instead of phrase by phrase).

SOURCES. Plain keys resolve against `outputs/final_numbers.csv`. `fact:` keys resolve
against `outputs/series_facts.csv` (records, series results, draft slots, derivations,
rebuilt from the warehouse by `series_facts.py`). `c1:<season>:<column>` and
`t8:<season>:<player>:<column>` resolve against the champions tables. `src:<player>` and
`supp:<group_sort>` resolve against the transaction source tables, which is how a reported
figure (a contract as the outlets published it) is bound to the report rather than to the
model.

    python kuminga/scripts/audit_series.py
"""
from __future__ import annotations

import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

OUT = os.path.join(REPO, "kuminga", "outputs")
DATA = os.path.join(REPO, "kuminga", "data")
SERIES = os.path.join(REPO, "kuminga", "docs", "series")

TOKEN = re.compile(r"[-+]?\$?\d[\d,]*(?:\.\d+)?%?")
# the prose spells small numbers out, so the audit reads them as numbers too
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
         "fourteen": 14, "fifteen": 15, "sixteen": 16, "twenty": 20, "first": 1,
         "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7,
         "eighth": 8, "tenth": 10}
WORD_RE = re.compile(r"\b(%s)\b" % "|".join(sorted(WORDS, key=len, reverse=True)), re.I)
# shares the prose writes as a phrase rather than a percentage
FRACTIONS = {"one in four": 25, "one in three": 33, "one in five": 20, "half of them": 50}
STRUCTURE = [r"\b\d{4}-\d{2}\b", r"\b(19|20)\d{2}-\d{2}-\d{2}\b",
             r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
             r"\.? \d{1,2}(, (19|20)\d{2})?\b",
             r"\b(19|20)\d{2}\b", r"^\s*#+.*$", r"^\s*\d+\.\s", r"`[^`]*`",
             r"\[\d+\]\([^)]*\)", r"\(https?://[^)]*\)", r"https?://\S+",
             r"\b(Part|Parts|Piece) \d\b", r"\bGame \d+\b", r"\bNo\. \d+\b"]
# A bound phrase is checked twice. STRICT: every digit the prose writes as a digit must
# match one of the phrase's keys, which is the check that catches a wrong or wrongly rounded
# figure. LOOSE: digits the prose spells out ("Six of the eleven"), and digits inside a game
# number or a draft slot, count towards showing that each bound key is actually used. The
# asymmetry is deliberate: "the second apron" and "three seasons" are English, not findings,
# so they must not have to match anything, while "$33.4 million" must.
LOOSE_EXTRA = [r"\bGame (\d+)\b", r"\bNo\. (\d+)\b"]
# structure, not findings: games in a season, minutes in a game, teams in the league, the
# per-hundred basis, games in a series, and the count of parts in the series
CONSTANTS = {"82", "48", "30", "100", "7", "4"}

# --------------------------------------------------------------------------- the bindings
CLAIMS = {
 "part1.md": [
  ("Two years, $12.4 million", ["k_total"]),
  ("roughly $12 million a year over three years from the Lakers", ["supp:SUPP_KUMINGA_REJECTED_LAL"]),
  ("The Lakers put roughly $12 million a year over three years on the table", ["supp:SUPP_KUMINGA_REJECTED_LAL"]),
  ("the team had 94 phone calls with Kuminga's agent", ["src:Jonathan Kuminga"]),
  ("Add his $6,064,000 to the money", ["k_y1"]),
  ("Minnesota sat $1,999,829 over the second apron", ["dos_stuck_over"]),
  ("cost him about $4.1 million over the two years", ["fact:kuminga_shave_cost_m"]),
  ("left the roster frozen at fourteen", ["fact:min_roster_count"]),
  ("That's a 49-win team", ["fact:min_wins_2025_26"]),
  ("a five-year, $112 million deal", ["src:Ayo Dosunmu"]),
  ("Julius Randle and his $33.3 million", ["c4_randlju01_out_salary"]),
  ("the 28th pick Minnesota had just made", ["fact:draft_joshua_jefferson_pick"]),
  ("in 2029 (protected 6 through 30)", ["picks:2029:protection"]),
  ("with three years and $130,746,840 left on his deal", ["c4_ballla01_in_total"]),
  ("Josh Green on a $14.68 million expiring contract", ["c4_greenjo02_out_salary"]),
  ("Isaiah Evans, the 33rd pick", ["fact:draft_isaiah_evans_pick"]),
  ("Jaylen Clark on three years and $10 million", ["c4_clarkja02_retained_total"]),
  ("The 59th pick, Trey Kaufman-Renn", ["fact:draft_trey_kaufman_renn_pick"]),
  ("tore his Achilles in Game 4 of the Denver series", ["fact:ddv_injury_game"]),
  ("Here's what they did with the $2 million problem", ["dos_stuck_over"]),
  ("Cody Williams, the No. 10 pick in 2024, on $6 million with a team option",
   ["fact:draft_cody_williams_pick", "c4_willico04_in_salary"]),
  ("John Konchar, on $6,165,000 and expiring", ["chain_konchar"]),
  ("$2,055,000 a year against the cap for three seasons", ["dead_year"]),
  ("Green out at $14.68 million", ["c4_greenjo02_out_salary"]),
  ("Williams and Konchar in at $6,015,600 and $6,165,000", ["chain_williams", "chain_konchar"]),
  ("the book lands at $211,013,416", ["chain_post"]),
  ("Add Kuminga and it's $217,077,416", ["chain_final"]),
  ("$4,608,584 under the hard cap", ["room_hard_cap"]),
  ("and $8,062,416 over the first apron", ["over_first"]),
  ("about $4.6 million to fill it with", ["room_hard_cap"]),
  ("to fit a $6 million forward", ["k_y1"]),
  ("Julius Randle ($33.3M)", ["c4_randlju01_out_salary"]),
  ("Naz Reid ($23.3M)", ["c4_reidna01_out_salary"]),
  ("Josh Green ($14.7M", ["c4_greenjo02_out_salary"]),
  ("on the books at $2.06M a year through 2029", ["dead_year"]),
  ("The rights to Joshua Jefferson (No. 28)", ["fact:draft_joshua_jefferson_pick"]),
  ("LaMelo Ball ($40.8M)", ["c4_ballla01_in_salary"]),
  ("Jonathan Kuminga ($6.1M)", ["c4_kuminjo01_in_salary"]),
  ("Cody Williams ($6.0M)", ["c4_willico04_in_salary"]),
  ("Isaiah Evans (No. 33)", ["fact:draft_isaiah_evans_pick"]),
  ("Ayo Dosunmu (five years, $112M)", ["src:Ayo Dosunmu"]),
  ("Jaylen Clark (three years, $10M)", ["c4_clarkja02_retained_total"]),
  ("$75.8 million came in across seven players and $80.8 million went out across seven",
   ["c4_in_total_m", "c4_out_total_m"]),
  ("Minnesota is 3.16% to win the title", ["mkt_min"]),
  ("who played 72 games last season and 105 in the three before that",
   ["c3_games_2025_26", "fact:ball_games_prior_three"]),
  ("the market's 3.16%", ["mkt_min"]),
  ("ran the season 200,000 times", ["sims"]),
 ],
 "part2.md": [
  ("the season was run 200,000 times per way", ["sims"]),
  ("the No. 10 pick two summers ago", ["fact:draft_cody_williams_pick"]),
  ("the model scores him at -4.39 points per hundred possessions", ["williams_bio"]),
  ("only one player in the league's projected rotations is rated lower", ["fact:williams_rated_below"]),
  ("gives Cody Williams 16.1 minutes a night", ["williams_mpg"]),
  ("Below 12.6 a night", ["williams_threshold"]),
  ("it costs 0.39 points of title odds on its own", ["v_ddv_injury_pooled_u"]),
  ("by 0.44 points of title odds, or 0.56 once you correct for how players age",
   ["v_A_c3_default_shannon_pooled_u", "v_A_c3_default_shannon_pooled_a"]),
  ("It says that on the strength of 7.9 minutes a game", ["beringer_prior"]),
  ("clearly positive: 0.79 points of title odds, 0.91 aged", ["v_ball_in_pooled_u", "v_ball_in_pooled_a"]),
  ("clearly negative: 0.33 points the other way, 0.40 aged", ["v_reid_out_pooled_u", "v_reid_out_pooled_a"]),
  ("Of the 150 highest-volume scorers last season, Edwards sits at the 1st percentile",
   ["e_n_off", "e_pct_shipped"]),
  ("three seasons and 245 scorers", ["k_scorer_ref"]),
  ("We counted 21 different primary defenders", ["e_pairings"]),
  ("61% of Ant's makes were unassisted", ["cr_edw"]),
  ("was at 55%", ["cr_ball"]),
  ("The league median is 35%", ["cr_median"]),
  ("1.5 points of usage, and true shooting actually went up 0.8 points, across nine cases",
   ["m5_star_usg", "m5_star_ts", "m5_star_n"]),
  ("at the 96th percentile of 7,380 starting fives", ["m5_kin_pct", "m5_league_fives"]),
  ("tested them on 195 playoff series", ["n3_series"]),
  ("loses 0.85 points a game in the playoffs", ["ds_coef"]),
  ("Of 79 real primary matchups", ["m3_rows"]),
  ("Minnesota at 1.68% to win the title on the primary basis, 2.39% once you correct for age",
   ["title", "title_aged"]),
  ("The market says 3.16% and sixth in the league. The model says 13th to 16th",
   ["mkt_min", "mkt_min_rank", "min_view_ranks"]),
  ("the Celtics at 18.33% to win the title against a market price of 5.47%",
   ["model_bos", "mkt_bos"]),
  ("below -1.7 through game 30", ["bos_dec_threshold", "bos_dec_game"]),
  ("the Hornets at 5.86%", ["cha_model_pre"]),
  ("the market prices at 0.81%", ["mkt_cha"]),
  ("3.36% of all points on the 578 team-games", ["misplaced_lineup", "val_lineup_teamgames"]),
  ("Charlotte came down to 3.44%", ["model_cha"]),
  ("the Wolves lose 54% of their title odds, 43% once you correct for age",
   ["n5_min_share", "n5_min_share_aged"]),
  ("costs 0.87 points of title odds on average", ["n5_min_drop"]),
  ("The most likely seed is 7th, at 31%", ["n2_modal", "n2_modal_p"]),
  ("Top six, 42%", ["n2_top6"]),
  ("is the first-round opponent 53% of the time", ["n2_sas_okc"]),
  ("They reach the second round 28% of the time", ["n2_r2"]),
  ("they win it all 6.1% of the time", ["n2_cond"]),
 ],
 "part4.md": [
  ("in games played: 51, 75, 36, 22, 47, 72",
   ["c3_games_2020_21", "c3_games_2021_22", "c3_games_2022_23", "c3_games_2023_24",
    "c3_games_2024_25", "c3_games_2025_26"]),
  ("Twenty player-seasons since 2001-02 match it; their median was 61.4 games, and one in four reached 70",
   ["c3_a_n", "c3_a_median", "c3_a_p70", "def:c3_a_p70"]),
  ("playing 50 instead of 82", ["def:c3_title_drop_50_u"]),
  ("the title odds barely move, 0.12 points", ["c3_title_drop_50_u"]),
  ("drops 16.6 points", ["c3_top6_drop_50_u"]),
  ("whether he plays 16.1 minutes a night or fewer than 12.6", ["williams_mpg", "williams_threshold"]),
  ("between a 0.53 and a 0.84 chance", ["k_optout_lo", "k_optout_hi"]),
  ("on Non-Bird rights, is $7,276,800", ["k_nonbird"]),
  ("Minnesota is $8,062,416 over the first apron", ["over_first"]),
  ("Konchar. $2,055,000 a year against the cap through 2028-29", ["dead_year"]),
  ("cost $6,712,836 of payroll this season and about $14.6M more in tax",
   ["dos_dump_payroll", "dos_dump_tax"]),
  ("sat $1,999,829 over the hard cap", ["dos_stuck_over"]),
  ("paid up to $8,254,095 out of the bigger mid-level", ["dos_nodos_kuminga"]),
  ("Taking a former No. 10 pick back", ["fact:draft_cody_williams_pick"]),
  ("a reported two years and about $122 million", ["c2_std_ext_reported"]),
  ("requires 65 games, and he played 61", ["c2_games_rule", "c2_games_2025_26"]),
  ("Four games.", ["fact:edwards_games_short"]),
  ("winning at a .600 clip and the chance he leaves is 0.8% this season, 7.3% next season, and 44% at the cliff",
   ["c2_scen_high", "c2_haz_2027_600", "c2_haz_2028_600", "c2_haz_2029_600"]),
  ("48% by that summer", ["c2_cum_2029_600"]),
  ("sagging to .450 and the cliff is 56%, with 62% gone by 2029",
   ["c2_scen_low", "c2_haz_2029_450", "c2_cum_2029_450"]),
  ("playing .600 or better left 31% of the time. On teams under .500, 56%",
   ["c2_scen_high", "c2_raw_walk_600", "c2_raw_walk_sub500", "def:c2_raw_walk_sub500"]),
  ("the needle moves from 31% toward 56%", ["c2_raw_walk_600", "c2_raw_walk_sub500"]),
  ("Thirteen verdicts went into the testing in Part 2 and seven came out", ["n_candidates", "n_ship"]),
  ("added title equity, 0.79 points of it", ["v_ball_in_pooled_u"]),
  ("by 0.44 points of title odds", ["v_A_c3_default_shannon_pooled_u"]),
  ("costs 54% of the odds", ["n5_min_share"]),
  ("none was worse than 11th in net rating after 20 games", ["w5_flip", "w_game"]),
  ("fewer than 12.6 minutes a night", ["williams_threshold"]),
  ("net rating is above +7.5 the model was too low; below -7.2", ["w2_flip"]),
  ("Boston below -2.4 at game 20 and below -1.7 at game 30",
   ["w3_flip", "w_game", "bos_dec_threshold", "bos_dec_game"]),
  ("San Antonio above +14.4", ["w3_flip"]),
  ("true shooting below 0.547, or LaMelo's below 0.476", ["w4_flip"]),
  ("or 7.9 minutes of noise", ["beringer_prior"]),
  ("Game 20. If Cody Williams", ["w_game"]),
  ("of the 29 champions since 1997-98, none was worse than 11th in net rating after 20 games",
   ["w5_now", "w_game"]),
  ("See you at game 20.", ["w_game"]),
 ],
}

# Part 3 is scoped per champion instead of phrase by phrase: every number in a champion's
# section must appear in that champion's own row of the champions table, its top-eight rows,
# or the narrative facts for that season.
P3_SECTIONS = {"2015-16 Cleveland": "2015-16", "2016-17 Golden State": "2016-17",
               "2017-18 Golden State": "2017-18", "2018-19 Toronto": "2018-19",
               "2019-20 Los Angeles": "2019-20", "2020-21 Milwaukee": "2020-21",
               "2021-22 Golden State": "2021-22", "2022-23 Denver": "2022-23",
               "2023-24 Boston": "2023-24", "2024-25 Oklahoma City": "2024-25",
               "2025-26 New York": "2025-26"}
# the rest of Part 3 (the pattern and the turn back to Minnesota) binds by phrase
CLAIMS["part3.md"] = [
  ("market had them fourth in the league at 8.27% to win it", ["nyk_rank", "nyk_mkt"]),
  ("The win total was 53.5. They won 53", ["nyk_wt", "nyk_wins"]),
  ("had them at 4.63%", ["nyk_model"]),
  ("+6.33 a game across the season, +6.16 before the break and +6.67 after it",
   ["nyk_rs", "nyk_pre", "nyk_post"]),
  ("They went 16-3 at +14.89 a game", ["nyk_po_rec", "nyk_po"]),
  ("Of the sixteen teams in the field", ["nyk_po_teams"]),
  ("had missed 46 games between them from October to April; in the playoffs they missed 2",
   ["nyk_top5_rs_games_missed", "nyk_top5_po_games_missed"]),
  ("went from 0.579 to 0.673", ["nyk_top5_share_rs", "nyk_top5_share_po"]),
  ("but on a team that had been merely good at 0.579", ["nyk_top5_share_rs"]),
  ("keep coming back to the 4.63%", ["nyk_model"]),
  ("playing 0.673 of the minutes, had barely existed", ["nyk_top5_share_po"]),
  ("those five had missed 46 games between them", ["nyk_top5_rs_games_missed"]),
  ("The market couldn't see it either, at 8.27%", ["nyk_mkt"]),
  ("Six of the eleven were No. 1 seeds", ["c1_seed_1_n"]),
  ("Ten of the eleven were top five in regular-season net rating", ["c1_top5_net_n"]),
  ("Denver, was 6th", ["c1_worst_rs_rank"]),
  ("Five were top three", ["c1_top3_net_n"]),
  ("as bad as 18th (the 2022 Warriors) and 16th twice",
   ["c1_worst_post_rank", "c1:2017-18:net_post_asb_rank"]),
  ("Age ran from 25.5 to 29.7, averaging 28.7",
   ["c1:2024-25:top8_mean_age", "c1:2016-17:top8_mean_age", "c1_mean_age"]),
  ("On average 5.8 of the eight", ["c1_mean_returning"]),
  ("1st in net rating in October and 1st in April",
   ["c1:2016-17:net_rs_rank", "c1:2023-24:net_rs_rank", "c1:2024-25:net_rs_rank",
    "c1:2016-17:net_post_asb_rank", "c1:2023-24:net_post_asb_rank", "c1:2024-25:net_post_asb_rank"]),
  ("the eight missed 101 regular-season games and 6.2 playoff games",
   ["c1_mean_missed_rs", "c1_mean_missed_po"]),
  ("went from an average of 56% in the regular season to 70% in the playoffs",
   ["c1_mean_top5_rs", "c1_mean_top5_po"]),
  ("touched the eight for 4 of the 11", ["c1_moves_n", "c1_n"]),
  ("the 2018 Warriors at 16th after the break, the 2022 Warriors at 18th, the 2023 Nuggets at 6th for the year and 16th after the break",
   ["c1:2017-18:net_post_asb_rank", "c1:2021-22:net_post_asb_rank", "c1:2022-23:net_rs_rank",
    "c1:2022-23:net_post_asb_rank"]),
  ("play five of them 70% of the minutes", ["c1_mean_top5_po"]),
  ("priced between 8.27% and 14.69%", ["h2_lo", "h2_hi"]),
  ("the fourteen teams the market had in its top five", ["h3_n_non"]),
  ("which of twenty measurable features", ["h3_n_feat"]),
  ("three did: offensive rank, defensive rank, and continuity", ["h3_n_sep"]),
  ("priced at 3.16% and sixth in the league", ["mkt_min", "mkt_min_rank"]),
  ("who can carry 70% of the minutes", ["c1_mean_top5_po"]),
]


def load():
    sheet = pd.read_csv(os.path.join(OUT, "final_numbers.csv"), dtype=str).set_index("key").value
    facts = pd.read_csv(os.path.join(OUT, "series_facts.csv"), dtype=str).set_index("key").value
    c1 = pd.read_csv(os.path.join(OUT, "c1_champions.csv"), dtype=str).set_index("season")
    t8 = pd.read_csv(os.path.join(OUT, "c1_champion_top8.csv"), dtype=str)
    src = pd.read_csv(os.path.join(DATA, "c4_transaction_sources.csv"), dtype=str)
    supp = pd.read_csv(os.path.join(DATA, "transaction_supplement.csv"), dtype=str)
    picks = pd.read_csv(os.path.join(DATA, "traded_picks_2026_offseason.csv"), dtype=str)
    return sheet, facts, c1, t8, src, supp, picks


def resolve(key, S):
    sheet, facts, c1, t8, src, supp, picks = S
    if key.startswith("fact:"):
        return facts[key[5:]]
    if key.startswith("c1:"):
        _, season, col = key.split(":")
        return c1.loc[season, col]
    if key.startswith("t8:"):
        _, season, player, col = key.split(":")
        row = t8[(t8.season == season) & (t8.player == player)]
        return row[col].iloc[0]
    if key.startswith("src:"):
        row = src[src.player == key[4:]]
        return " ".join(str(v) for v in row.values.ravel() if pd.notna(v))
    if key.startswith("supp:"):
        row = supp[supp.group_sort == key[5:]]
        return " ".join(str(v) for v in row.values.ravel() if pd.notna(v))
    if key.startswith("def:"):
        k = key[4:]
        row = pd.read_csv(os.path.join(OUT, "final_numbers.csv"), dtype=str).set_index("key").loc[k]
        return "%s %s %s" % (k.replace("_", " "), row.figure, row.value)
    if key.startswith("picks:"):
        _, year, col = key.split(":")
        row = picks[(picks.year == year) & (picks.rnd == "1")]
        return " ".join(str(v) for v in row[col] if pd.notna(v))
    return sheet[key]


def nums_in(text):
    """Every number in a source value, as floats."""
    out = []
    for m in TOKEN.finditer(str(text)):
        s = m.group(0).replace("$", "").replace(",", "").rstrip("%")
        try:
            out.append(float(s))
        except ValueError:
            pass
    return out


def matches(tok, tail, value):
    """Does a prose token match a source value, exactly or as a correct rounding?"""
    s = tok.replace("$", "").replace(",", "").rstrip("%")
    try:
        f = float(s)
    except ValueError:
        return False
    dec = len(s.split(".")[1]) if "." in s else 0
    scales = [1.0]
    if re.match(r"\s*(million|M\b)", tail):
        scales.append(1e6)
    raw = re.sub(r"[^\d.]", "", tok).strip(".")
    for v in nums_in(value):
        if re.sub(r"[^\d.]", "", ("%g" % v)).strip(".") == raw:
            return True
        for sc in scales:
            for w in (v, abs(v)):     # the prose often carries the sign in words
                if abs(round(w / sc, dec) - f) < 1e-9 or abs(round(w, dec) - f) < 1e-9:
                    return True
    return False


def loose_tokens(phrase):
    """Numbers a bound phrase states in words, or inside a game number or a draft slot."""
    out = []
    for p in LOOSE_EXTRA:
        for m in re.finditer(p, phrase):
            out.append((m.group(1), "", m.start()))
    for m in WORD_RE.finditer(phrase):
        out.append((str(WORDS[m.group(0).lower()]), "", m.start()))
    low = phrase.lower()
    for phr, pct in FRACTIONS.items():
        if phr in low:
            out.append(("%d" % pct, "%", low.index(phr)))
    return out


def scan_tokens(text, structure=None, words=False):
    """Every number in a block of prose that is not structural, with its trailing context.
    `words=True` also yields numbers the prose spells out, which is how the audit checks a
    phrase like "Six of the eleven were No. 1 seeds"."""
    clean = text
    for p in (STRUCTURE if structure is None else structure):
        clean = re.sub(p, lambda m: " " * len(m.group(0)), clean, flags=re.M)
    out = []
    for m in TOKEN.finditer(clean):
        out.append((m.group(0), text[m.end():m.end() + 12], m.start()))
    if words:
        for m in WORD_RE.finditer(clean):
            out.append((str(WORDS[m.group(0).lower()]), "", m.start()))
    return out


def main():
    with runlog.run("audit_series", inputs={"series": SERIES}) as r:
        S = load()
        problems, checked = [], 0
        covered = {}       # file -> set of covered character positions

        for fname, claims in CLAIMS.items():
            path = os.path.join(SERIES, fname)
            text = open(path, encoding="utf-8").read()
            covered[fname] = set()
            for phrase, keys in claims:
                n = text.count(phrase)
                if n != 1:
                    problems.append("%s: phrase appears %d times: %r" % (fname, n, phrase[:70]))
                    continue
                start = text.index(phrase)
                for tok, tail, pos in scan_tokens(phrase):
                    covered[fname].add(start + pos)
                strict = scan_tokens(phrase)
                loose = strict + loose_tokens(phrase)
                if not loose:
                    problems.append("%s: bound phrase has no number: %r" % (fname, phrase[:70]))
                used = set()
                for tok, tail, _ in strict:
                    hit = [k for k in keys if matches(tok, tail, resolve(k, S))]
                    checked += 1
                    if not hit:
                        problems.append("%s: %r in %r matches none of %s (values %s)"
                                        % (fname, tok, phrase[:60], keys,
                                           [str(resolve(k, S))[:28] for k in keys]))
                    used.update(hit)
                for tok, tail, _ in loose:
                    used.update(k for k in keys if matches(tok, tail, resolve(k, S)))
                for k in keys:
                    if k not in used:
                        problems.append("%s: key %s is bound to %r but no number uses it"
                                        % (fname, k, phrase[:60]))

        # ---- Part 3, scoped per champion -------------------------------------------------
        p3 = open(os.path.join(SERIES, "part3.md"), encoding="utf-8").read()
        covered.setdefault("part3.md", set())
        sheet, facts, c1, t8, src, supp, picks = S
        for head, season in P3_SECTIONS.items():
            m = re.search(r"^## %s\s*$" % re.escape(head), p3, flags=re.M)
            if m is None:
                problems.append("part3.md: section %r not found" % head)
                continue
            nxt = re.search(r"^## ", p3[m.end():], flags=re.M)
            body = p3[m.end(): m.end() + (nxt.start() if nxt else len(p3))]
            pool = " ".join(str(v) for v in c1.loc[season].values if pd.notna(v))
            pool += " " + " ".join(str(v) for v in t8[t8.season == season].values.ravel() if pd.notna(v))
            pool += " " + " ".join(str(v) for k, v in facts.items() if season in k)
            if season == "2025-26":   # the Knicks passage also uses the H1 sheet keys
                pool += " " + " ".join(str(v) for k, v in sheet.items() if k.startswith("nyk_"))
            for tok, tail, pos in scan_tokens(body):
                covered["part3.md"].add(m.end() + pos)
                checked += 1
                if not matches(tok, tail, pool):
                    problems.append("part3.md [%s]: %r is not in that champion's own row (context: %r)"
                                    % (season, tok, body[max(0, pos - 45):pos + 15].replace("\n", " ")))

        # ---- coverage: no number anywhere in the four parts is unaccounted for -----------
        for fname in ("part1.md", "part2.md", "part3.md", "part4.md"):
            text = open(os.path.join(SERIES, fname), encoding="utf-8").read()
            for tok, tail, pos in scan_tokens(text):
                if pos in covered.get(fname, set()):
                    continue
                if re.sub(r"[^\d.]", "", tok).strip(".") in CONSTANTS and "%" not in tok and "$" not in tok:
                    continue
                problems.append("%s: UNBOUND number %r at %r"
                                % (fname, tok, text[max(0, pos - 55):pos + 20].replace("\n", " ")))

        # ---- the short versions and the pull-quotes may only reuse their part's numbers ---
        for stem in ("part1", "part2", "part3", "part4"):
            base = set(re.sub(r"[^\d.]", "", t).strip(".") for t, _, _ in
                       scan_tokens(open(os.path.join(SERIES, "%s.md" % stem), encoding="utf-8").read()))
            for suffix in ("_short.md", "_quotes.md"):
                path = os.path.join(SERIES, stem + suffix)
                if not os.path.exists(path):
                    continue
                for tok, tail, pos in scan_tokens(open(path, encoding="utf-8").read()):
                    d = re.sub(r"[^\d.]", "", tok).strip(".")
                    checked += 1
                    if d not in base and d not in CONSTANTS:
                        problems.append("%s%s: %r is not in the article it summarizes" % (stem, suffix, tok))

        # ---- the slide configs: every tile figure must match the key it names -------------
        import json
        for stem in ("part1", "part2", "part3", "part4"):
            cfg = json.load(open(os.path.join(SERIES, "%s_slide.json" % stem), encoding="utf-8"))
            for tile in cfg["tiles"]:
                if "key" not in tile:
                    problems.append("%s_slide.json: tile %r has no key" % (stem, tile["label"]))
                    continue
                checked += 1
                val = resolve(tile["key"], S)
                toks = scan_tokens(tile["num"])
                if toks and not any(matches(t, ta, val) for t, ta, _ in toks):
                    problems.append("%s_slide.json: tile %r shows %r but %s is %r"
                                    % (stem, tile["label"], tile["num"], tile["key"], str(val)[:30]))
                if not toks and str(val).find(tile["num"]) < 0:
                    problems.append("%s_slide.json: tile %r shows %r, not in %s (%r)"
                                    % (stem, tile["label"], tile["num"], tile["key"], str(val)[:40]))

        r.note("%d number checks across the series" % checked)
        for p in problems:
            r.note("PROBLEM " + p)
        r.note("%d problems" % len(problems))
        rep = pd.DataFrame({"problem": problems})
        p_out = os.path.join(OUT, "audit_series.csv")
        rep.to_csv(p_out, index=False)
        r.output(p_out, rows=len(rep))
        if problems:
            raise RuntimeError("series audit failed with %d problems" % len(problems))


if __name__ == "__main__":
    main()
