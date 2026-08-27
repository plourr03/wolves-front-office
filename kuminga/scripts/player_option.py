#!/usr/bin/env python3
"""Item 14: the year-2 player option, first pass. And item 13's consequence, priced.

FIRST PASS, deliberately. This is not the pick2033 option machinery: that prices
path-dependent options on draft-pick ORDER, which is a different problem, and it has
no player-option module of any kind. Nothing here is calibrated against realised
opt-out behaviour, and the impact-to-salary mapping it leans on is weak (the market
explains between 12% and 34% of the variance in impact, depending on the view). Treat
the direction as informative and the levels as illustrative.

THE STRUCTURE

  Year 1  $6,064,000 guaranteed
  Year 2  $6,367,200 PLAYER option

Kuminga opts out if the market will pay him more than $6,367,200 in the summer of
2027. What Minnesota can do about it is set by item 13: because he would have spent
ONE season with the team, and a declined option year is never "covered by a player
contract", Minnesota holds NON-BIRD rights only. That caps a re-signing start at the
greater of 120% of his prior salary or 120% of the minimum:

  120% x $6,367,200 = $7,640,640

So there is a window. If his market lands between $6,367,200 and $7,640,640 he opts
out and Minnesota can still match. Above $7,640,640, Minnesota cannot, and the only
route back is cap space it will not have or a sign-and-trade it may not be permitted
to use. That gap, not the opt-out itself, is the risk.

METHOD. Draw his realised 2026-27 impact from each fork's posterior, map it to a 2027
market salary by EMPIRICAL PERCENTILE (see kuminga/lib/market.py), scale for cap
growth, and read off the three probabilities. The linear par-dollar curve is not used
here: its intercept near $19.6M prices a league-average player at $19.6M and put
Kuminga's 2027 market above $25M, which is an artefact of fitting only on $8M-plus
contracts rather than a finding.

    python kuminga/scripts/player_option.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import market, runlog  # noqa: E402

VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
CONTRACTS = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27_verified.csv")
CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")
OUT = os.path.join(REPO, "kuminga", "outputs", "player_option.csv")

KUMINGA_ID = 1630228
Y2_OPTION = 6_367_200
NON_BIRD_CAP = round(1.20 * Y2_OPTION)
N_DRAWS = 200_000
SEED = 20260827

# He turns 25 during 2026-27. The project's own age curve puts a player of that age on
# the improving side, but applying a point bump would smuggle a forecast into what is
# meant to be an uncertainty exercise. The draw is centred on his CURRENT estimate and
# the aging question is handled as a labelled scenario instead.
AGING_SCENARIOS = {"flat": 0.0, "improves": +0.5, "declines": -0.5}


def main():
    with runlog.run("player_option", inputs={"option": Y2_OPTION,
                                             "non_bird_cap": NON_BIRD_CAP,
                                             "draws": N_DRAWS}) as r:
        value = pd.read_csv(VALUE)
        ct = pd.read_csv(CONTRACTS)
        const = json.load(open(CONST, encoding="utf-8"))["seasons"]
        salary = (ct[ct.nba_player_id.astype(str).str.isdigit()]
                  .assign(pid=lambda d: d.nba_player_id.astype(float).astype(int))
                  .drop_duplicates("pid").set_index("pid").salary_2026_27)
        value["rapm_net"] = value.off_rapm - value.def_rapm
        value["box_net"] = value.box_off_prior - value.box_def_prior
        NET_COL = {"consensus": "consensus_net", "rapm": "rapm_net", "box": "box_net"}

        k = value[value.player_id == KUMINGA_ID].iloc[0]
        net_by_fork = {
            "consensus": float(k.consensus_net),
            "rapm": float(k.off_rapm - k.def_rapm),
            "box": float(k.box_off_prior - k.box_def_prior),
        }
        sd = float(np.sqrt(k.off_sd ** 2 + k.def_sd ** 2))
        r.note(f"Kuminga posterior sd on net (off+def in quadrature): {sd:.2f}")

        # Cap growth 2026-27 -> 2027-28 scales the par-dollar curve.
        growth = const["2027-28"]["salary_cap"] / const["2026-27"]["salary_cap"]
        r.note(f"cap growth to 2027-28: x{growth:.4f}")
        r.note(f"Non-Bird ceiling on a re-sign: ${NON_BIRD_CAP:,}")

        rng = np.random.default_rng(SEED)
        rows = []
        for fork, net0 in net_by_fork.items():
            mc = market.build(value, salary, NET_COL[fork], label=fork)
            r.note(f"market curve [{fork}]: {mc}")
            r2 = float("nan")
            for scen, bump in AGING_SCENARIOS.items():
                draws = rng.normal(net0 + bump, sd, N_DRAWS)
                # Percentile map, then scale for cap growth. The linear par-dollar
                # curve is NOT used: its ~$19.6M intercept prices a league-average
                # player at $19.6M and would put Kuminga's 2027 market near $25M.
                mkt = mc.salary(draws) * growth
                mkt = np.clip(mkt, const["2027-28"]["min_salary_by_yos"]["5"], None)

                p_optout = float((mkt > Y2_OPTION).mean())
                p_above_nonbird = float((mkt > NON_BIRD_CAP).mean())
                # Value of the option to the player: he takes the better of the two.
                ev_player = float(np.maximum(mkt, Y2_OPTION).mean()) - Y2_OPTION
                # Minnesota keeps him only if he opts in, or opts out into a market it
                # can still match with Non-Bird.
                p_retain = float(((mkt <= Y2_OPTION) | (mkt <= NON_BIRD_CAP)).mean())
                rows.append(dict(
                    fork=fork, aging=scen, net_center=net0 + bump, net_sd=sd,
                    curve_r2=r2,
                    median_market_2027=float(np.median(mkt)),
                    p_opt_out=p_optout,
                    p_market_above_non_bird=p_above_nonbird,
                    p_minnesota_retains=p_retain,
                    ev_of_option_to_player=ev_player,
                ))
                r.note(f"[{fork:9s}/{scen:8s}] median market ${np.median(mkt)/1e6:5.1f}M | "
                       f"P(opt out) {p_optout:.2f} | P(above Non-Bird) {p_above_nonbird:.2f} | "
                       f"P(MIN retains) {p_retain:.2f} | option EV to him "
                       f"${ev_player/1e6:.1f}M")

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)

        base = df[df.aging == "flat"]
        r.note("HEADLINE (flat aging, across forks): "
               f"P(opt out) {base.p_opt_out.min():.2f}-{base.p_opt_out.max():.2f}, "
               f"P(Minnesota retains) {base.p_minnesota_retains.min():.2f}-"
               f"{base.p_minnesota_retains.max():.2f}")
        r.output(OUT, rows=len(df))

    print()
    print(df[["fork", "aging", "median_market_2027", "p_opt_out",
              "p_market_above_non_bird", "p_minnesota_retains",
              "ev_of_option_to_player"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
