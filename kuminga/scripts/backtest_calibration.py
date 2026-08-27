#!/usr/bin/env python3
"""A3 (backtest half): three seasons of model against market, on the historical odds.

WHAT THIS CAN AND CANNOT TEST. A full historical replay of this pipeline is not
possible and the reason is worth stating plainly: there are no historical preseason
ROSTERS in the warehouse (nba_team_rosters holds one season, 2025-26), and the impact
spine is a pooled 2023-26 fit, so using it to project 2023-24 would leak three years of
future information into the answer. Those two gaps are listed in gaps_remaining.md.

What IS testable, cleanly, is the CALIBRATION LAYER: the mapping from a team's measured
net rating in one season to its projected wins and title probability in the next. That
is the layer C4's decomposition left as a residual, and it needs no rosters at all,
because it is the "everyone stands pat" version of the model.

For each of 2023-24, 2024-25 and 2025-26:
    measured net in season Y-1
      -> regress_to_expectation()
      -> wins = wins_a + wins_b * net,  and title odds from simulate_league()
    compared against the preseason market win total, the de-vigged market title
    probability, and the realised win count.

    python kuminga/scripts/backtest_calibration.py
"""
from __future__ import annotations

import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import kfreeze, runlog  # noqa: E402
import bracket_sim as E                  # noqa: E402

DATA = os.path.join(REPO, "offseason", "data")
OUT = os.path.join(REPO, "kuminga", "outputs", "backtest_calibration.csv")
OUT_SUM = os.path.join(REPO, "kuminga", "outputs", "backtest_calibration_summary.csv")

SEASONS = {"2023-24": 2022, "2024-25": 2023, "2025-26": 2024}   # target -> prior start year
SEEDS = [1, 2, 3]
NSIMS = 10_000

NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "LA Clippers": "LAC", "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM", "Miami Heat": "MIA", "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX", "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA", "Washington Wizards": "WAS",
}


def american_to_prob(odds: str) -> float:
    o = float(str(odds).replace("+", "").replace(",", ""))
    return 100.0 / (o + 100.0) if o > 0 else abs(o) / (abs(o) + 100.0)


def parse_result(s: str):
    m = re.match(r"\s*(\d+)-(\d+)", str(s))
    return int(m.group(1)) if m else np.nan


def main():
    with runlog.run("backtest_calibration",
                    inputs={"seasons": list(SEASONS), "seeds": SEEDS, "nsims": NSIMS}) as r:
        tn, _ = kfreeze.load("team_net")
        tn["net_rating"] = pd.to_numeric(tn.net_rating, errors="coerce")
        rs = tn[tn.season_type == "Regular Season"]
        net_by = {y: g.set_index("team_abbr").net_rating.to_dict()
                  for y, g in rs.groupby("season_start_year")}

        p = E.load_e_params()
        wa, wb = float(p["wins_a"]), float(p["wins_b"])
        r.note(f"calibration under test: wins = {wa} + {wb} * net; "
               f"persistence {p['persist_int']} + {p['persist_slope']} * net")

        rows = []
        for season, prior_y in SEASONS.items():
            path = os.path.join(DATA, f"{season}-preseason-odd.csv")
            if not os.path.exists(path):
                r.note(f"{season}: odds file missing, skipped")
                continue
            odds = pd.read_csv(path)
            odds["team_abbr"] = odds.Team.map(NAME_TO_ABBR)
            unmapped = odds[odds.team_abbr.isna()].Team.tolist()
            if unmapped:
                r.note(f"{season}: UNMAPPED team names {unmapped}")
            odds = odds[odds.team_abbr.notna()].copy()
            odds["mkt_prob_raw"] = odds.Odds.map(american_to_prob)
            odds["mkt_title"] = odds.mkt_prob_raw / odds.mkt_prob_raw.sum()   # de-vig
            odds["mkt_wins"] = pd.to_numeric(odds["W-L O/U"], errors="coerce")
            odds["actual_wins"] = odds.Result.map(parse_result)

            prior = net_by.get(prior_y, {})
            missing = [t for t in odds.team_abbr if t not in prior]
            if missing:
                r.note(f"{season}: no prior-season net for {missing}")

            strengths = {}
            for _, x in odds.iterrows():
                if x.team_abbr not in prior:
                    continue
                strengths[x.team_abbr] = {
                    "net": E.regress_to_expectation(prior[x.team_abbr]),
                    "net_sd": 0.0, "munc": 0.0,
                    "conf": E.TEAM_CONF.get(x.team_abbr, "W"), "profile": None}
            if len(strengths) < 30:
                r.note(f"{season}: only {len(strengths)} teams, skipped")
                continue

            acc = {t: [] for t in strengths}
            for seed in SEEDS:
                res = E.simulate_league(strengths, n_sims=NSIMS, seed=seed,
                                        use_overlay=False)["teams"]
                for t in strengths:
                    acc[t].append(res[t]["title"])

            for _, x in odds.iterrows():
                t = x.team_abbr
                if t not in strengths:
                    continue
                net = strengths[t]["net"]
                rows.append(dict(
                    season=season, team_abbr=t, prior_net=prior[t], model_net=net,
                    model_wins=wa + wb * net, market_wins=x.mkt_wins,
                    actual_wins=x.actual_wins,
                    model_title=float(np.mean(acc[t])), market_title=x.mkt_title,
                ))

        df = pd.DataFrame(rows)
        if df.empty:
            r.note("no seasons could be backtested")
            return
        df["wins_err_model"] = df.model_wins - df.actual_wins
        df["wins_err_market"] = df.market_wins - df.actual_wins
        df["title_diff_pp"] = (df.model_title - df.market_title) * 100
        df.to_csv(OUT, index=False)

        summ = []
        for season, g in df.groupby("season"):
            summ.append(dict(
                season=season, n=len(g),
                model_wins_mae=g.wins_err_model.abs().mean(),
                market_wins_mae=g.wins_err_market.abs().mean(),
                model_wins_bias=g.wins_err_model.mean(),
                model_vs_market_wins_corr=g.model_wins.corr(g.market_wins),
                model_vs_actual_wins_corr=g.model_wins.corr(g.actual_wins),
                market_vs_actual_wins_corr=g.market_wins.corr(g.actual_wins),
                title_mae_pp=g.title_diff_pp.abs().mean(),
                title_corr=g.model_title.corr(g.market_title),
            ))
        sm = pd.DataFrame(summ)
        sm.to_csv(OUT_SUM, index=False)
        for _, x in sm.iterrows():
            r.note(f"{x.season}: wins MAE model {x.model_wins_mae:.2f} vs market "
                   f"{x.market_wins_mae:.2f} | model-actual r {x.model_vs_actual_wins_corr:.3f} "
                   f"vs market-actual r {x.market_vs_actual_wins_corr:.3f} | "
                   f"title MAE {x.title_mae_pp:.2f}pp, r {x.title_corr:.3f}")
        r.note(f"POOLED: wins MAE model {df.wins_err_model.abs().mean():.2f} vs market "
               f"{df.wins_err_market.abs().mean():.2f}; model bias "
               f"{df.wins_err_model.mean():+.2f} wins")
        r.note("Read this as a test of the CALIBRATION SPINE only. It holds rosters "
               "fixed at the prior season, so it cannot beat a market that knows about "
               "trades and signings; the useful question is whether it is close and "
               "unbiased, not whether it wins.")
        r.output(OUT, rows=len(df))
        r.output(OUT_SUM, rows=len(sm))

    print()
    print(sm.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
