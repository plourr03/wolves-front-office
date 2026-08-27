#!/usr/bin/env python3
"""Item 9: the signing evaluator, cap side and value side.

The engine models trades only. `evaluate_move` can gate a signing against the hard
cap, but nothing in the repo scores the VALUE of a signing, which is the central move
in this analysis. This adds the value side and wires the cap side.

CAP SIDE. `evaluate_move` with `exception_used="taxpayer_mle"`, run against the
rebuilt team_state, under both Green branches (R3).

VALUE SIDE. Surplus is computed the way the series already defines it, but refit
SEPARATELY UNDER EACH OF THE FOUR VIEWS (R1) rather than on the consensus alone:

    par_net(salary)     = c + d * salary        fit over market-priced veterans
    surplus_net         = player_net - par_net(salary)
    par_dollars(net)    = a + b * player_net
    dollar_gap          = par_dollars(net) - salary

The curves are fit on reliable rotation players earning at least $8,000,000, i.e.
players whose price the open market actually set. Minimums and rookie-scale deals are
excluded because their salary carries no information about their value.

The headline this produces is a PRICE argument, not an impact argument: the same
impact estimate that made Kuminga roughly fair value at $24.3M makes him a large
positive at $6.06M. That is true under every view, which is the point.

    python kuminga/scripts/eval_signing.py
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
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import kfreeze, market, runlog  # noqa: E402
import evaluate_move as EM      # noqa: E402

VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
CONTRACTS = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27_verified.csv")
TEAMSTATE = os.path.join(REPO, "offseason", "data", "team_state.csv")
CONST = os.path.join(REPO, "offseason", "data", "league_year_constants.json")
OUT_CURVES = os.path.join(REPO, "kuminga", "outputs", "par_curves_by_fork.csv")
OUT_SURPLUS = os.path.join(REPO, "kuminga", "outputs", "kuminga_surplus_by_fork.csv")
OUT_GATE = os.path.join(REPO, "kuminga", "outputs", "kuminga_cap_gate.json")
SUPP = os.path.join(REPO, "kuminga", "data", "transaction_supplement.csv")
OUT_MKT = os.path.join(REPO, "kuminga", "outputs", "market_comparison.csv")
AGE_LO, AGE_HI = 22, 25

PRICED_MIN_SALARY = 8_000_000
KUMINGA_ID = 1630228
TPMLE_2026_27 = 6_064_000
ATL_OPTION = 24_300_000
FORKS = ["consensus", "rapm", "box", "darko"]


def nkey(name) -> str:
    import re
    import unicodedata
    s = str(name)
    try:
        s = s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    drop = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv"}
    s = " ".join(t for t in s.split() if t not in drop)
    return re.sub(r"[^a-z0-9]+", "", s)


def fork_net(value: pd.DataFrame, darko: pd.DataFrame) -> pd.DataFrame:
    """One net-impact column per fork, keyed on nba player id."""
    df = value[["player_id", "player_name", "reliable"]].copy()
    df["consensus"] = value.consensus_net
    df["rapm"] = value.off_rapm - value.def_rapm
    df["box"] = value.box_off_prior - value.box_def_prior

    dk = darko.copy()
    dk.columns = [c.strip().lstrip("﻿") for c in dk.columns]
    dk["k"] = dk["Player"].map(nkey)
    dk_net = dk.drop_duplicates("k").set_index("k")["DPM"]
    df["k"] = df.player_name.map(nkey)
    df["darko"] = df.k.map(dk_net)
    return df


def fit_curves(df: pd.DataFrame, salary: pd.Series, fork: str):
    """(a, b, c, d, r2, n) for one fork over market-priced veterans."""
    m = df[(df.reliable.astype(str).str.lower() == "true")
           & df[fork].notna()].copy()
    m["salary"] = m.player_id.map(salary)
    m = m[m.salary.notna() & (m.salary >= PRICED_MIN_SALARY)]
    x, y = m[fork].to_numpy(dtype=float), m.salary.to_numpy(dtype=float)
    b, a = np.polyfit(x, y, 1)          # salary = a + b*net
    d, c = np.polyfit(y, x, 1)          # net    = c + d*salary
    pred = c + d * y
    r2 = 1 - np.sum((x - pred) ** 2) / np.sum((x - x.mean()) ** 2)
    return a, b, c, d, r2, len(m)


def main():
    with runlog.run("eval_signing", inputs={"value": VALUE, "contracts": CONTRACTS}) as r:
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        ct = pd.read_csv(CONTRACTS)
        const = json.load(open(CONST, encoding="utf-8"))["seasons"]["2026-27"]

        salary = (ct[ct.nba_player_id.astype(str).str.isdigit()]
                  .assign(pid=lambda d: d.nba_player_id.astype(float).astype(int))
                  .drop_duplicates("pid").set_index("pid").salary_2026_27)

        nets = fork_net(value, darko)
        kum = nets[nets.player_id == KUMINGA_ID].iloc[0]
        r.note(f"Kuminga net by fork: " +
               ", ".join(f"{f}={kum[f]:+.2f}" for f in FORKS if pd.notna(kum[f])))

        curve_rows, surp_rows = [], []
        for fork in FORKS:
            if pd.isna(kum[fork]):
                r.note(f"  fork {fork}: Kuminga has no value, skipped")
                continue
            a, b, c, d, r2, n = fit_curves(nets, salary, fork)
            curve_rows.append(dict(fork=fork, dollar_a=a, dollar_b=b,
                                   net_c=c, net_d=d, r2_net=r2, n_players=n))
            r.note(f"  {fork}: salary = {a:,.0f} + {b:,.0f}*net | "
                   f"net = {c:.3f} + {d:.3e}*salary | R2={r2:.3f} n={n}")

            knet = float(kum[fork])
            mc = market.build(nets.rename(columns={fork: "_net"}).assign(**{fork: nets[fork]}),
                              salary, fork, label=fork)
            mkt = float(mc.salary(knet))
            for label, sal in (("taxpayer_mle_2026_27", TPMLE_2026_27),
                               ("atl_option_declined", ATL_OPTION)):
                par_net = c + d * sal
                surp_rows.append(dict(
                    fork=fork, price_label=label, salary=sal,
                    kuminga_net=knet,
                    par_net_for_salary=par_net,
                    surplus_net=knet - par_net,
                    market_salary_pctile=mkt,
                    dollar_gap=mkt - sal,
                    market_pctile=mc.percentile(knet),
                    linear_par_dollars=a + b * knet,
                ))

        curves = pd.DataFrame(curve_rows)
        surp = pd.DataFrame(surp_rows)
        curves.to_csv(OUT_CURVES, index=False)
        surp.to_csv(OUT_SURPLUS, index=False)

        r.note("KUMINGA SURPLUS, impact units (positive = better than his price buys):")
        for _, x in surp.iterrows():
            r.note(f"  [{x.fork:9s}] at ${x.salary/1e6:5.2f}M -> surplus_net "
                   f"{x.surplus_net:+.2f} | market ${x.market_salary_pctile/1e6:.1f}M "
                   f"| dollar_gap ${x.dollar_gap/1e6:+.1f}M")

        # ---------------- A2: age-restricted market curve ---------------------
        # Kuminga is 23. The all-ages curve prices him against a distribution whose
        # upper reaches are 28-to-32-year-olds on second and third contracts, which
        # biases his estimate UPWARD if young players are systematically underpaid
        # relative to impact (they are, because rookie-scale and early-extension deals
        # are below market by construction). Restricting the reference set to players
        # aged 22 to 25 on NON-rookie-scale deals removes most of that.
        bio, _ = kfreeze.load("player_bio")
        bio = bio.copy()
        bio["age"] = ((pd.Timestamp("2026-10-01") - pd.to_datetime(bio.birthdate)).dt.days
                      / 365.25)
        bio["season_exp"] = pd.to_numeric(bio.season_exp, errors="coerce")
        bio["draft_round"] = pd.to_numeric(bio.draft_round, errors="coerce")
        # A first-round pick is on the rookie scale for his first four seasons.
        bio["on_rookie_scale"] = (bio.draft_round == 1) & (bio.season_exp <= 3)
        age_by_pid = bio.set_index("player_id").age
        rookie_by_pid = bio.set_index("player_id").on_rookie_scale

        nets_age = nets.copy()
        nets_age["age"] = nets_age.player_id.map(age_by_pid)
        nets_age["on_rookie_scale"] = nets_age.player_id.map(rookie_by_pid).fillna(False)
        young = nets_age[(nets_age.age.between(AGE_LO, AGE_HI))
                         & (~nets_age.on_rookie_scale)]
        r.note(f"age-restricted reference set ({AGE_LO}-{AGE_HI}, non-rookie-scale): "
               f"{len(young)} players")

        # ---------------- A1: the real bids -----------------------------------
        sup = pd.read_csv(SUPP)
        bids = sup[sup.transaction_type == "RejectedOffer"]
        best_bid = float(bids.salary.max()) if len(bids) else float("nan")
        r.note(f"observed rejected bids: " + ", ".join(
            f"{b.team_abbr} ${b.salary/1e6:.1f}M/yr x{int(b.years)}"
            if b.salary > 0 else f"{b.team_abbr} (terms undisclosed)"
            for _, b in bids.iterrows()))

        mkt_rows = []
        for fork in FORKS:
            if pd.isna(kum[fork]):
                continue
            knet = float(kum[fork])
            mc_all = market.build(nets, salary, fork, label=f"{fork}_all_ages")
            mc_young = market.build(young, salary, fork, label=f"{fork}_age{AGE_LO}_{AGE_HI}")
            v_all, v_young = float(mc_all.salary(knet)), float(mc_young.salary(knet))
            mkt_rows.append(dict(
                fork=fork, kuminga_net=knet,
                market_all_ages=v_all,
                market_age_restricted=v_young,
                age_bias=v_young - v_all,
                n_all=mc_all.n, n_young=mc_young.n,
                actual_salary=TPMLE_2026_27,
                best_real_bid=best_bid,
                model_vs_best_bid=v_all - best_bid,
                agrees_with_best_bid=abs(v_all - best_bid) / best_bid < 0.25,
            ))
        mk = pd.DataFrame(mkt_rows)
        mk.to_csv(OUT_MKT, index=False)
        r.note("MARKET COMPARISON (model market value vs the best real bid):")
        for _, x in mk.iterrows():
            r.note(f"  [{x.fork:9s}] all-ages ${x.market_all_ages/1e6:5.1f}M | "
                   f"age {AGE_LO}-{AGE_HI} ${x.market_age_restricted/1e6:5.1f}M "
                   f"(bias {x.age_bias/1e6:+.1f}M) | best real bid "
                   f"${x.best_real_bid/1e6:.1f}M | "
                   f"{'AGREES' if x.agrees_with_best_bid else 'disagrees'} (within 25%)")
        n_agree = int(mk.agrees_with_best_bid.sum())
        r.note(f"  => {n_agree} of {len(mk)} views agree with the Lakers bid within 25%")
        r.output(OUT_MKT, rows=len(mk))

        # ---------------- cap side -------------------------------------------
        ts = pd.read_csv(TEAMSTATE)
        base = ts[(ts.team_abbr == "MIN") & (ts.season == "2026-27")
                  & (ts.scenario_id == "base")].iloc[0].to_dict()
        gate = {}
        apron2 = const["second_apron"]

        # team_state's apron_team_salary ALREADY contains Kuminga (patch_contracts put
        # him in the contract book) and the R4 placeholder. Adding the exception on top
        # of it double-counts the signing, which is what produced the "$7.7M over the
        # apron" figure in the first morning report. The gate is rebuilt on the
        # CANONICAL basis instead: contracted salary only, Kuminga removed, then added
        # back exactly once. See cap_reconciliation.py.
        PLACEHOLDER = 1_358_000
        # Canonical APRON basis: contracted + unlikely bonuses, cap holds excluded.
        # Deriving it from team_state omitted $1,750,000 of unlikely bonuses and is what
        # produced the 8x error in the published lede.
        _canon = json.load(open(os.path.join(REPO, "kuminga", "outputs",
                                             "cap_canonical.json"), encoding="utf-8"))
        pre_kuminga = float(_canon["pre_kuminga_apron"])
        r.note(f"canonical pre-Kuminga apron salary: ${pre_kuminga:,.0f} "
               f"(team_state ${float(base['apron_team_salary']):,.0f} minus Kuminga "
               f"${TPMLE_2026_27:,} minus the ${PLACEHOLDER:,} placeholder)")

        def tier_for(salary):
            if salary > const["second_apron"]:
                return "second_apron"
            if salary > const["first_apron"]:
                return "first_apron"
            if salary > const["luxury_tax"]:
                return "taxpayer"
            if salary > const["salary_cap"]:
                return "over_cap_under_tax"
            return "under_cap"

        for branch, green_out in (("green_on_books", False), ("green_removed", True)):
            before = pre_kuminga - (14_679_012 if green_out else 0.0)
            state = dict(base)
            state["apron_team_salary"] = before
            state["distance_to_second_apron"] = apron2 - before
            state["distance_to_first_apron"] = const["first_apron"] - before
            # The tier must be recomputed for the branch. Leaving the base row's tier
            # in place made evaluate_move refuse BOTH branches with "taxpayer_mle not
            # available at tier second_apron", including the one that is legal.
            state["tier"] = tier_for(before)
            state["taxpayer_mle_available"] = state["tier"] != "second_apron"
            res = EM.evaluate_move(
                state, const, outgoing=[],
                incoming=[{"salary": TPMLE_2026_27, "label": "Jonathan Kuminga"}],
                exception_used="taxpayer_mle")
            post = before + TPMLE_2026_27
            gate[branch] = {
                "basis": "canonical: contracted salary only, no placeholder",
                "tier_before_signing": state["tier"],
                "apron_salary_before": before,
                "apron_salary_after_signing": post,
                "second_apron": apron2,
                "room_after_signing": apron2 - post,
                "fits_under_hard_cap": bool(post <= apron2),
                "evaluate_move_legal": bool(res["legal"]),
                "failing_constraint": res["failing_constraint"],
                "hard_cap_level": res["hard_cap_level"],
            }
            verdict = "FITS" if post <= apron2 else f"OVER by ${post - apron2:,.0f}"
            r.note(f"CAP [{branch}, tier {state['tier']}]: ${before:,.0f} + "
                   f"${TPMLE_2026_27:,} = ${post:,.0f} vs apron2 ${apron2:,} -> {verdict}")

        json.dump(gate, open(OUT_GATE, "w", encoding="utf-8"), indent=2)
        r.output(OUT_CURVES, rows=len(curves))
        r.output(OUT_SURPLUS, rows=len(surp))
        r.output(OUT_GATE)

    print()
    print(surp[["fork", "price_label", "salary", "kuminga_net", "surplus_net",
                "market_salary_pctile", "dollar_gap", "linear_par_dollars"]].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
