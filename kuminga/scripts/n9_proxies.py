#!/usr/bin/env python3
"""N9 proxies (D113): observable stand-ins for the breadth of a team's odds, tested three ways.

The model cannot be run on past seasons, so N9's breadth is bridged to the eleven champion
seasons by correlates that exist for the eleven champions and the 48 preseason top-five
non-champions (the C1 machinery), and for every 2026-27 roster:

  1. top-eight mean age
  2. top-eight returning share of playoff minutes, by contract (2026-27: the non-movers' share
     of projected rotation minutes)
  3. in-season acquisitions among the eight (no preseason analogue for 2026-27)
  4. top-eight games missed THE PRIOR SEASON (new in D113): per player with an NBA season
     before, 82 x (1 - his share of team games in season t-1); a season missed entirely
     between two seasons played counts as 82; a player with no prior NBA season is left
     out and the count is stated. H3 tested games missed in the SAME season (regular season
     and playoffs); N9 version 1 tested the first three; neither tested the prior season.

THREE TESTS, one table:
  A. TENDENCY. Champions against the 48, Mann-Whitney two-sided; lean at p below 0.05,
     Bonferroni for four tests 0.0125.
  B. VALIDATION ON OUTCOMES. Spearman between each proxy and the absolute win-total error,
     82 x |actual win share - preseason over/under / scheduled games| (72 scheduled in
     2020-21), across the 59 teams. The over/unders come from the same cached
     Basketball-Reference preseason odds pages as the title odds (courtesy
     sportsoddshistory.com). A proxy for breadth should be larger where the season ran
     further from its price.
  C. VALIDATION ON THE MODEL. Spearman between each proxy, computed on the 2026-27 projected
     rotations, and N9's breadth across the 30 teams: the spread of expected wins (p90 - p10)
     and, for teams the model has at 0.5% or more, the p90 / p10 ratio of title odds.

    python kuminga/scripts/n9_proxies.py
"""
from __future__ import annotations

import io
import os
import re
import sys

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

from kuminga.lib import runlog  # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
HTML = os.path.join(REPO, "kuminga", "data", "bref", "html")
PANEL = os.path.join(OUT_DIR, "c3_player_seasons_panel.csv")
DOC = os.path.join(REPO, "kuminga", "docs", "n9_proxies.md")
LEAN_P = 0.05
N_TESTS = 4

NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN", "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE", "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND", "LA Clippers": "LAC",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM", "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP", "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA", "Washington Wizards": "WAS",
}


def win_totals():
    rows = []
    for y in range(2016, 2027):
        p = os.path.join(HTML, "leagues_NBA_%d_preseason_odds.html" % y)
        if not os.path.exists(p):
            continue
        t = io.open(p, encoding="utf-8", errors="replace").read()
        i = t.find('id="NBA_preseason_odds"')
        j = t.find("</table>", i)
        for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t[i:j], re.S)[1:]:
            c = {k: re.sub(r"<[^>]+>", "", v).replace("&nbsp;", " ").strip()
                 for k, v in re.findall(r'data-stat="([a-z_0-9]+)"[^>]*>(.*?)</t[dh]>', r, re.S)}
            if not c.get("team") or not c.get("wins_ou"):
                continue
            m = re.match(r"(\d+)-(\d+)", c.get("result", ""))
            if not m:
                continue
            w, l_ = int(m.group(1)), int(m.group(2))
            sched = 72 if y == 2021 else 82
            ou = float(c["wins_ou"])
            rows.append(dict(season="%d-%02d" % (y - 1, y % 100), team=NAME_TO_ABBR.get(c["team"], c["team"]), wins=w, losses=l_,
                             wins_ou=ou, scheduled=sched, win_error_82=82 * (w / (w + l_) - ou / sched)))
    d = pd.DataFrame(rows)
    d["abs_win_error_82"] = d.win_error_82.abs()
    return d


def prior_missed(top8, panel):
    S = {(int(p), int(t)): s for p, t, s in zip(panel.player_id, panel.t, panel.share)}
    span = panel.groupby("player_id").t.agg(["min", "max"])
    out = []
    for x in top8.itertuples():
        t = int(str(x.season)[:4])
        pid = int(x.player_id)
        if (pid, t - 1) in S:
            out.append(82 * (1 - min(1.0, S[(pid, t - 1)])))
        elif pid in span.index and span.loc[pid, "min"] < t - 1 and span.loc[pid, "max"] >= t:
            out.append(82.0)                     # in the league before and after, no game in t-1
        else:
            out.append(np.nan)                   # no prior NBA season
    return np.array(out)


def main():
    with runlog.run("n9_proxies", inputs={"proxies": 4, "tests": "tendency, win-total error, model breadth"}) as r:
        panel = pd.read_csv(PANEL)
        ch, co = pd.read_csv(os.path.join(OUT_DIR, "c1_champions.csv")), pd.read_csv(os.path.join(OUT_DIR, "c1_contenders.csv"))
        t8c, t8o = pd.read_csv(os.path.join(OUT_DIR, "c1_champion_top8.csv")), pd.read_csv(os.path.join(OUT_DIR, "c1_contender_top8.csv"))
        teams = pd.concat([ch.assign(group="champion"), co.assign(group="contender")], ignore_index=True)
        teams["n_in_season_moves"] = teams.in_season_moves.map(lambda s: 0 if str(s).strip() == "none" else str(s).count(";") + 1)
        t8 = pd.concat([t8c, t8o], ignore_index=True)
        t8["prior_missed"] = prior_missed(t8, panel)
        pm = t8.groupby(["season", "team"]).agg(top8_prior_missed=("prior_missed", "mean"),
                                                 top8_prior_n=("prior_missed", lambda v: int(v.notna().sum()))).reset_index()
        teams = teams.merge(pm, on=["season", "team"], how="left")
        wt = win_totals()
        teams = teams.merge(wt[["season", "team", "wins_ou", "scheduled", "win_error_82", "abs_win_error_82"]], on=["season", "team"], how="left")
        miss = teams[teams.abs_win_error_82.isna()]
        r.note("win totals: %d team-seasons parsed over %d seasons; %d of %d proxy teams matched" % (len(wt), wt.season.nunique(), len(teams) - len(miss), len(teams)))
        if len(miss):
            raise RuntimeError("win total missing for %s" % list(zip(miss.season, miss.team)))
        teams.to_csv(os.path.join(OUT_DIR, "n9_proxies_history.csv"), index=False)

        PROX = [("top-eight mean age", "top8_mean_age"),
                ("top-eight returning share of minutes, by contract", "returning_po_minutes_share_contract"),
                ("in-season acquisitions among the eight", "n_in_season_moves"),
                ("top-eight games missed the prior season (mean per player, 82-game basis)", "top8_prior_missed")]

        # ---- 2026-27 proxies and N9's breadth ---------------------------------------------------------
        pool = pd.read_csv(os.path.join(OUT_DIR, "player_pool_2026_27.csv"))
        pool = pool[pool.scenario == "current"]
        rot = pd.read_csv(os.path.join(OUT_DIR, "rotations_2026_27.csv"))
        rot = rot[rot.scenario == "current"]
        roster = pd.read_csv(os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_SIM.csv"))
        age = roster.dropna(subset=["nba_player_id"]).assign(pid=lambda d: d.nba_player_id.astype(int)).drop_duplicates("pid").set_index("pid").age
        moved = pool.dropna(subset=["player_id"]).assign(pid=lambda d: d.player_id.astype(int)).drop_duplicates("pid").set_index("pid").moved_teams
        S25 = panel[panel.t == 2025].set_index("player_id").share
        span = panel.groupby("player_id").t.agg(["min", "max"])
        cur = []
        for tm, g in rot.groupby("team_abbr"):
            g = g.sort_values("mpg", ascending=False)
            top = g.head(8)
            ids = [int(p) for p in top.player_id if not pd.isna(p)]
            miss_ = []
            for p in ids:
                if p in S25.index:
                    miss_.append(82 * (1 - min(1.0, float(S25[p]))))
                elif p in span.index and span.loc[p, "min"] < 2025:
                    miss_.append(82.0)
            mv = np.array([bool(moved.get(int(p), False)) if not pd.isna(p) else False for p in g.player_id])
            cur.append(dict(team=tm, top8_mean_age=float(np.nanmean([age.get(p, np.nan) for p in ids])),
                            returning_po_minutes_share_contract=float(g.mpg[~mv].sum() / g.mpg.sum()),
                            n_in_season_moves=np.nan, top8_prior_missed=float(np.mean(miss_)) if miss_ else np.nan))
        CUR = pd.DataFrame(cur).set_index("team")
        n9 = pd.read_csv(os.path.join(OUT_DIR, "n9_breadth_summary.csv")).set_index("team")
        CUR = CUR.join(n9[["wins_p10", "wins_p90", "title_mean", "breadth_ratio"]])
        CUR["wins_spread"] = CUR.wins_p90 - CUR.wins_p10
        CUR.to_csv(os.path.join(OUT_DIR, "n9_proxies_current.csv"))

        rows = []
        for lab, col in PROX:
            a = teams[teams.group == "champion"][col].dropna().astype(float)
            b = teams[teams.group == "contender"][col].dropna().astype(float)
            u, p = mannwhitneyu(a, b, alternative="two-sided")
            h = teams[[col, "abs_win_error_82"]].dropna()
            rho_h, p_h = spearmanr(h[col], h.abs_win_error_82)
            if CUR[col].notna().sum() >= 10:
                c1 = CUR[[col, "wins_spread"]].dropna()
                rho_w, p_w = spearmanr(c1[col], c1.wins_spread)
                c2 = CUR[CUR.title_mean >= 0.5][[col, "breadth_ratio"]].dropna()
                rho_t, p_t = spearmanr(c2[col], c2.breadth_ratio)
                n_w, n_t = len(c1), len(c2)
            else:
                rho_w = p_w = rho_t = p_t = np.nan
                n_w = n_t = 0
            rows.append(dict(proxy=lab, column=col, tested_before=("N9 version 1 (D112)" if col != "top8_prior_missed" else "no: H3 tested the same season, not the prior one"),
                             note=("mechanical: N9's availability draws are built from the same games history" if col == "top8_prior_missed" else ""),
                             champion_median=float(a.median()), contender_median=float(b.median()), n_champions=len(a), n_contenders=len(b),
                             tendency_p=float(p), leans=bool(p < LEAN_P), leans_bonferroni=bool(p < LEAN_P / N_TESTS),
                             win_error_rho=float(rho_h), win_error_p=float(p_h), win_error_n=len(h),
                             model_wins_rho=float(rho_w), model_wins_p=float(p_w), model_wins_n=n_w,
                             model_title_rho=float(rho_t), model_title_p=float(p_t), model_title_n=n_t))
        T = pd.DataFrame(rows)
        T.to_csv(os.path.join(OUT_DIR, "n9_proxy_tests.csv"), index=False)
        for x in T.itertuples():
            r.note("%-70s tendency %.2f vs %.2f p=%.3f | |win error| rho %+.2f p=%.3f n=%d | model wins spread rho %+.2f p=%.3f | model odds ratio rho %+.2f p=%.3f"
                   % (x.proxy, x.champion_median, x.contender_median, x.tendency_p, x.win_error_rho, x.win_error_p, x.win_error_n,
                      x.model_wins_rho, x.model_wins_p, x.model_title_rho, x.model_title_p))
        mn = CUR.loc["MIN"]
        r.note("Minnesota 2026-27: age %.1f, returning share %.0f%%, prior-season games missed %.1f per top-eight player"
               % (mn.top8_mean_age, 100 * mn.returning_po_minutes_share_contract, mn.top8_prior_missed))
        r.note("the eleven seasons' absolute win-total error: median %.1f wins (champions %.1f, contenders %.1f)"
               % (teams.abs_win_error_82.median(), teams[teams.group == "champion"].abs_win_error_82.median(),
                  teams[teams.group == "contender"].abs_win_error_82.median()))

        L = ["# N9 proxies: stand-ins for breadth, tested three ways", "",
             "Run `%s`. Design in D113. Tendency: champions (n=11) against the 48 top-five non-champions, Mann-Whitney two-sided, lean at p below %.2f, Bonferroni for %d tests %.4f. Win-total error: 82 x |actual win share - over/under / scheduled games| across the 59 teams. Model breadth: 2026-27 proxies against N9's spread of expected wins (30 teams) and its p90 / p10 odds ratio (teams at 0.5%% or more)." % (r.run_id, LEAN_P, N_TESTS, LEAN_P / N_TESTS), "",
             "| proxy | tested before | champions' median | contenders' median | tendency p | vs win-total error: rho (p) | vs model wins spread: rho (p) | vs model odds ratio: rho (p) |",
             "|---|---|---|---|---|---|---|---|"]
        for x in T.itertuples():
            f = lambda rho, p: "n/a" if np.isnan(rho) else "%+.2f (%.3f)" % (rho, p)
            L.append("| %s | %s | %.2f | %.2f | %.3f | %s | %s | %s |" % (x.proxy, x.tested_before, x.champion_median, x.contender_median, x.tendency_p,
                                                                     f(x.win_error_rho, x.win_error_p), f(x.model_wins_rho, x.model_wins_p), f(x.model_title_rho, x.model_title_p)))
        L += ["", "In-season acquisitions have no preseason analogue for 2026-27, so the model columns are n/a for that row. Prior-season games missed against the model's breadth is partly mechanical: N9's availability draws are built from the same games history, so that correlation is not independent evidence; the win-total column is the test that is.",
              "", "Minnesota 2026-27: top-eight mean age %.1f, returning share of rotation minutes %.0f%%, %.1f games missed last season per top-eight player." % (mn.top8_mean_age, 100 * mn.returning_po_minutes_share_contract, mn.top8_prior_missed)]
        io.open(DOC, "w", encoding="utf-8").write("\n".join(L) + "\n")
        for p in ("n9_proxies_history.csv", "n9_proxies_current.csv", "n9_proxy_tests.csv"):
            r.output(os.path.join(OUT_DIR, p))
        r.output(DOC)


if __name__ == "__main__":
    main()
