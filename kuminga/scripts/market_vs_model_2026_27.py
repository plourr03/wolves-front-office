#!/usr/bin/env python3
"""A3 (forward half): this season's model against this season's market, all 30 teams.

BLOCKED UNTIL THE ODDS EXIST. Every candidate source forbids automated retrieval, so
`offseason/data/2026-27-preseason-odd.csv` has to be pasted in by hand, in the same
three-column shape as the 2023-24, 2024-25 and 2025-26 files already in that folder:

    Team,Odds,,W-L O/U,Result
    Oklahoma City Thunder,+240,,62.5,

The Result column can be left empty; nothing here reads it.

This script exits cleanly with a message if the file is absent, so it can simply be
re-run once it appears.

DISAGREEMENT THRESHOLDS, stated rather than tuned:
  win totals   flagged at 4.0 wins, which is roughly half the model's own
               out-of-sample error against the market (pooled MAE 8.80 across three
               backtested seasons), so a flag means the gap is large relative to
               what this model can actually resolve.
  title odds   flagged at 2.5pp, just above the worst single-season title MAE from
               the same backtest (2.35pp). Anything inside that is noise by the
               model's own measured standard.

    python kuminga/scripts/market_vs_model_2026_27.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
sys.path.insert(0, HERE)

from kuminga.lib import runlog  # noqa: E402
from backtest_calibration import NAME_TO_ABBR, american_to_prob  # noqa: E402

ODDS = os.path.join(REPO, "offseason", "data", "2026-27-preseason-odd.csv")
SIM = os.path.join(REPO, "kuminga", "outputs", "sim_all30_2026_27.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "market_vs_model_2026_27.csv")
FORKS = ["consensus", "rapm", "box", "darko"]

WINS_THRESHOLD = 4.0
TITLE_THRESHOLD_PP = 2.5


def main():
    if not os.path.exists(ODDS):
        print(f"BLOCKED: {os.path.relpath(ODDS, REPO)} does not exist.")
        print("Paste the VegasInsider futures table into it (Team,Odds,,W-L O/U,Result)")
        print("and re-run. See gaps_remaining.md, item 7.")
        return

    with runlog.run("market_vs_model_2026_27",
                    inputs={"odds": ODDS, "wins_threshold": WINS_THRESHOLD,
                            "title_threshold_pp": TITLE_THRESHOLD_PP}) as r:
        odds = pd.read_csv(ODDS)
        odds["team_abbr"] = odds.Team.map(NAME_TO_ABBR)
        bad = odds[odds.team_abbr.isna()].Team.tolist()
        if bad:
            r.note(f"UNMAPPED team names, fix before trusting this: {bad}")
        odds = odds[odds.team_abbr.notna()].copy()
        odds["p_raw"] = odds.Odds.map(american_to_prob)
        odds["market_title"] = odds.p_raw / odds.p_raw.sum()
        odds["market_wins"] = pd.to_numeric(odds["W-L O/U"], errors="coerce")
        r.note(f"market table: {len(odds)} teams, vig "
               f"{(odds.p_raw.sum() - 1) * 100:.1f}%")

        sim = pd.read_csv(SIM)
        w = sim.pivot_table(index="team_abbr", columns="fork", values="wins_current")
        t = sim.pivot_table(index="team_abbr", columns="fork", values="title_current")
        m = odds.set_index("team_abbr")

        rows = []
        for team in w.index:
            if team not in m.index:
                r.note(f"{team}: no market row")
                continue
            wv = w.loc[team, FORKS].to_numpy(dtype=float)
            tv = t.loc[team, FORKS].to_numpy(dtype=float) * 100
            mw, mt = float(m.loc[team, "market_wins"]), float(m.loc[team, "market_title"]) * 100
            # A disagreement only counts if the market sits OUTSIDE the whole fork
            # band. Inside the band the model does not have a single opinion to
            # disagree with, which is the point of carrying four views.
            wins_out = mw < wv.min() or mw > wv.max()
            title_out = mt < tv.min() or mt > tv.max()
            wins_gap = (mw - wv.mean())
            title_gap = (mt - tv.mean())
            rows.append(dict(
                team_abbr=team,
                model_wins_mean=wv.mean(), model_wins_lo=wv.min(), model_wins_hi=wv.max(),
                market_wins=mw, wins_gap=wins_gap,
                model_title_mean=tv.mean(), model_title_lo=tv.min(), model_title_hi=tv.max(),
                market_title=mt, title_gap_pp=title_gap,
                wins_market_outside_band=wins_out, title_market_outside_band=title_out,
                flag_wins=abs(wins_gap) >= WINS_THRESHOLD and wins_out,
                flag_title=abs(title_gap) >= TITLE_THRESHOLD_PP and title_out,
                direction_wins="model higher" if wins_gap < 0 else "market higher",
                direction_title="model higher" if title_gap < 0 else "market higher",
            ))
        df = pd.DataFrame(rows).sort_values("title_gap_pp")
        df.to_csv(OUT, index=False)

        fw = df[df.flag_wins]
        ft = df[df.flag_title]
        r.note(f"flagged on WIN TOTALS ({WINS_THRESHOLD:+.1f} and outside the band): "
               f"{len(fw)} teams")
        for _, x in fw.iterrows():
            r.note(f"  {x.team_abbr}: model {x.model_wins_lo:.1f}-{x.model_wins_hi:.1f} "
                   f"vs market {x.market_wins:.1f} ({x.direction_wins})")
        r.note(f"flagged on TITLE ODDS ({TITLE_THRESHOLD_PP:+.1f}pp and outside the band): "
               f"{len(ft)} teams")
        for _, x in ft.iterrows():
            r.note(f"  {x.team_abbr}: model {x.model_title_lo:.2f}-{x.model_title_hi:.2f}% "
                   f"vs market {x.market_title:.2f}% ({x.direction_title})")
        mn = df[df.team_abbr == "MIN"]
        if len(mn):
            x = mn.iloc[0]
            r.note(f"MINNESOTA: model wins {x.model_wins_lo:.1f}-{x.model_wins_hi:.1f} vs "
                   f"market {x.market_wins:.1f}; model title "
                   f"{x.model_title_lo:.2f}-{x.model_title_hi:.2f}% vs market "
                   f"{x.market_title:.2f}%")
        r.output(OUT, rows=len(df))

    print()
    print(df[["team_abbr", "model_wins_mean", "market_wins", "wins_gap",
              "model_title_mean", "market_title", "title_gap_pp",
              "flag_wins", "flag_title"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
