#!/usr/bin/env python3
"""
backtest_tune.py  -- Acceptance calibration: wire decide() over real trades, then tune.

Sits on backtest_harness (reconstruction + packages + fleeces). For each labeled trade it rebuilds
each side's as-of-D state (need vector + posture + urgency, recomputed from the reconstructed roster,
2025-26 salaries, and 2025-26 net), injects it into partner_acceptance, and runs decide() from BOTH
sides (accept iff both say yes). Then it tunes the load-bearing coefficients against the deadline
trades (fit set, 19 at the current snapshot), holding the offseason trades out (11) as a generalization
check, with synthetic fleeces backstopping precision. The fit/held counts grow as nba_transactions
stays fresh; the split is by DEADLINE_CUTOFF.

Tunable (Bobby's call): K_WINNOW_VALUE, K_WINNOW_NEED, K_ABSORB_DISCOUNT, SURPLUS_MARGIN_FLOOR,
NEED_MARGIN_FLOOR (plus PICK_PTS_PER, the pick-to-surplus conversion). Frozen: the base margins
(0.6 / 0.12) and the validated heat star-gate. The news coefficients are left hand-set (no historical
news to fit). Objective: maximize leave-one-out recall on the fit set, subject to rejecting >= 90% of
fleeces, inside sane bounds.

    python backtest_tune.py            # baseline + tune + held-out check + report

CONCLUSION (2026-06-17): this backtest is RETAINED AS A DIAGNOSTIC, not an active calibration. It
established that partner_acceptance is scoped to Minnesota ACQUIRING a player and does not generalize
to scoring arbitrary two-team trades (real-trade recall topped out at 16% even with picks restored and
their value tuned to the ceiling; the dominant failure is the value-negative side of a zero-sum
trade). The decision was to accept the model as Minnesota-acquisition-specific and leave the Phase 2-C
coefficients hand-set. See docs/acceptance_model_scope_and_limitation.md. Re-run this only if the
model is ever generalized (a selling-side acceptance path plus a relaxed value-channel fit gate).
"""

import os
import sys
import csv
import collections
from datetime import date

import backtest_harness as H
import partner_acceptance as PA
import build_need_layer as NL          # BENCHMARK, DIMS
import age_curve as AC

DATA = H.DATA
db = H.db
DIMS = NL.DIMS
BENCH = NL.BENCHMARK
_PICK_PTS = [1.5]      # asset-points per vague 'draft consideration'; tuned (mutable cell, read in run_trade)


# ----------------------------- shared, roster-independent inputs ------------------------------ #
def _load_csv(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def shared_inputs():
    dims = {str(int(float(r["player_id"]))): {d: float(r[d]) for d in DIMS} for r in _load_csv("player_dimensions.csv")}
    minutes = {}
    for _, r in db.query("""SELECT player_id, SUM(minutes_played) m FROM nba_player_stats
                            WHERE season_year='2025-26' GROUP BY player_id""").iterrows():
        minutes[str(int(r.player_id))] = float(r.m or 0)
    net2526 = {r.t: float(r.net) for _, r in db.query(
        """SELECT g.team_abbreviation t, AVG(a.net_rating) net FROM nba_team_advanced_stats a
           JOIN nba_games g ON a.game_id=g.game_id AND a.team_tricode=g.team_abbreviation
           WHERE (g.season_id % 10000)=2025 GROUP BY g.team_abbreviation""").iterrows()}
    ages = AC.ages_2026_27([p for p in dims])     # ~as-of approximation for youth_share
    import json
    const = json.load(open(os.path.join(DATA, "league_year_constants.json"), encoding="utf-8"))["seasons"]
    c26 = const["2026-27"]
    return dims, minutes, net2526, ages, c26


def _minmax(d):
    vals = list(d.values())
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-9:
        return {k: 0.0 for k in d}
    return {k: (v - lo) / (hi - lo) for k, v in d.items()}


# ----------------------------- as-of-D league state (cached per date) ------------------------- #
_CACHE = {}


def league_state(D, tri_of, sal_map, shared):
    if D in _CACHE:
        return _CACHE[D]
    dims, minutes, net2526, ages, c26 = shared
    rosters, _conf = H.rosters_as_of(D, tri_of)
    TAX, FA1, FA2 = 201.0, 209.1, 222.0
    floor = c26["min_team_salary"]
    need, posture, total = {}, {}, {}
    shed_raw, winnow_raw, hunger, exp_raw, age_w = {}, {}, {}, {}, {}
    for team, pids in rosters.items():
        # team total (apron basis) summing 2025-26 salaries of the as-of-D roster
        tot = sum(H.player_salary(p, team, sal_map) for p in pids)
        total[team] = tot
        # need vector: minutes-weighted dim profile vs BENCHMARK
        wsum = sum(minutes.get(str(p), 0.0) for p in pids) or 1.0
        prof = {d: sum(minutes.get(str(p), 0.0) * dims.get(str(p), {}).get(d, 0.5) for p in pids) / wsum
                for d in DIMS}
        need[team] = {d: BENCH[d] - prof[d] for d in DIMS}
        # posture inputs
        net = net2526.get(team, 0.0)
        wins = max(15.0, min(67.0, 41.0 + 2.7 * net))
        young = sum(H.player_salary(p, team, sal_map) for p in pids if (ages.get(str(p)) or 99) <= 23.0)
        youth = young / (tot or 1)
        sal_m = tot / 1e6
        shed_raw[team] = 1.0 * max(0, sal_m - TAX) + 2.0 * max(0, sal_m - FA1) + 4.0 * max(0, sal_m - FA2)
        winnow_raw[team] = wins
        w_score = max(0.0, min(1.0, (45.0 - wins) / 20.0))
        youth_s = max(0.0, min(1.0, (youth - 0.10) / 0.30))
        slack_s = max(0.0, min(1.0, (floor - tot) / 40_000_000))
        reb = round((w_score + youth_s + slack_s) / 3.0, 3)
        ppost = ("rebuilder" if reb >= 0.45 else "retooler" if reb >= 0.25
                 else "contender" if wins >= 52 else "mid")
        floor_seek = tot < floor
        over_cut = sal_m >= FA1
        posture[team] = {"posture": ppost, "rebuild_score": reb,
                         "floor_seeking": "TRUE" if floor_seek else "FALSE",
                         "over_apron_cutter": "TRUE" if over_cut else "FALSE",
                         "absorbs_dumps": "TRUE" if (reb >= 0.45 or (floor_seek and ppost in ("rebuilder", "retooler", "mid"))) else "FALSE",
                         "apron_team_salary": tot, "tier": ("second_apron" if sal_m >= FA2 else "first_apron" if sal_m >= FA1 else "over_cap_under_tax")}
        hunger[team] = reb
        age_w[team] = sum(H.player_salary(p, team, sal_map) * (ages.get(str(p)) or 28.0) for p in pids) / (tot or 1)
    shed_n, hunger_n = _minmax(shed_raw), _minmax(hunger)
    wins_n, agew_n = _minmax(winnow_raw), _minmax(age_w)
    urgency = {}
    for team in rosters:
        urgency[team] = {"shed_pressure": shed_n[team], "asset_hunger": hunger_n[team],
                         "win_now_pressure": 0.6 * wins_n[team] + 0.4 * agew_n[team], "expiring_risk": 0.0}
    state = {"need": need, "posture": posture, "urgency": urgency}
    _CACHE[D] = state
    return state


# ----------------------------- inject as-of-D state + run decide ------------------------------ #
def run_trade(pkg, tri_of, sal_map, shared):
    """Inject both teams' as-of-D need/posture/urgency into PA and run decide() from both sides."""
    PA.load_layers()
    st = league_state(date.fromisoformat(pkg["date"]), tri_of, sal_map, shared)
    A, B = pkg["A"], pkg["B"]
    for t in (A, B):
        if t in st["need"]:
            PA._NEEDS[t] = st["need"][t]
            PA._POSTURE[t] = {**PA._POSTURE.get(t, {}), **st["posture"][t]}
            PA._URGENCY[t] = st["urgency"][t]
    va = PA.decide(A, sends=pkg["A_sends"], receives=pkg["A_receives"], sweetener_pts=pkg["A_pick_count"] * _PICK_PTS[0])
    vb = PA.decide(B, sends=pkg["B_sends"], receives=pkg["B_receives"], sweetener_pts=pkg["B_pick_count"] * _PICK_PTS[0])
    return {"accepted": va["accepted"] and vb["accepted"], "A": va, "B": vb}


def augment_surplus(sal_map, shared):
    """Surplus must be roster-INDEPENDENT: a player traded mid-season or now a FA is absent from the
    current player_surplus (which joins 2026-27 rosters), so reading it returns 0 and the gate sees a
    phantom even-value deal. Compute surplus for EVERY valued player from player_value.consensus_net
    minus the par net for his 2025-26 salary, and add any the live layer is missing."""
    PA.load_layers()
    import build_value_layer as BV
    _a, _b, c, d, _r, _n = BV.fit_par_curves(BV.load_contracts(), BV.load_value())
    ages = shared[3]
    sal_by_pid = {}
    for (pid, _team), s in sal_map.items():
        sal_by_pid[str(pid)] = max(sal_by_pid.get(str(pid), 0), s)
    for r in _load_csv("player_value.csv"):
        pid = str(int(float(r["player_id"])))
        net = r.get("consensus_net", "")
        if net == "" or pid in PA._SURPLUS:
            continue
        net = float(net)
        sal = sal_by_pid.get(pid, 0)
        surplus = round(net - (c + d * sal), 2) if sal > 0 else ""
        PA._SURPLUS[pid] = {"player_id": pid, "player_name": r.get("player_name", ""), "team_abbr": "",
                            "position": "", "salary_2026_27": sal, "years_left": "1",
                            "age": round(ages.get(pid, 28.0), 1) if ages.get(pid) else "",
                            "consensus_net": round(net, 2),
                            "surplus_net": surplus if surplus != "" else "", "option_2026_27": ""}


def run_fleece(fl):
    """Fleeces use current rosters/values (synthetic). Reject iff the fleeced side says no."""
    PA.load_layers()
    v = PA.decide(fl["team"], sends=fl["sends"], receives=fl["receives"])
    return not v["accepted"]


# ----------------------------- tuning ---------------------------------------------------------- #
TUNABLE = {
    "K_WINNOW_VALUE": [0.15, 0.30, 0.45], "K_WINNOW_NEED": [0.3, 0.5, 0.7],
    "K_ABSORB_DISCOUNT": [0.3, 0.5, 0.7], "SURPLUS_MARGIN_FLOOR": [0.05, 0.10, 0.20],
    "NEED_MARGIN_FLOOR": [0.02, 0.04, 0.08],
    # the pick-to-surplus conversion, added per Bobby: if sellers do not clear with picks restored,
    # let the backtest fit how much a vague draft consideration is worth (bounded so it cannot dominate)
    "PICK_PTS_PER": [1.5, 3.0, 5.0, 8.0],
}
SANE = {"K_WINNOW_VALUE": (0.0, 0.6), "K_WINNOW_NEED": (0.0, 0.9), "K_ABSORB_DISCOUNT": (0.0, 0.9),
        "SURPLUS_MARGIN_FLOOR": (0.0, 0.4), "NEED_MARGIN_FLOOR": (0.0, 0.12), "PICK_PTS_PER": (0.0, 10.0)}


def set_params(p):
    for k, v in p.items():
        if k == "PICK_PTS_PER":
            _PICK_PTS[0] = v
        else:
            setattr(PA, k, v)


def evaluate(fit_pkgs, fleeces, tri_of, sal_map, shared, exclude=None):
    acc = [run_trade(p, tri_of, sal_map, shared)["accepted"] for i, p in enumerate(fit_pkgs) if i != exclude]
    recall = sum(acc) / len(acc) if acc else 0.0
    rej = sum(run_fleece(f) for f in fleeces) / len(fleeces) if fleeces else 0.0
    return recall, rej


def main():
    tri_of = H.team_tricode_map()
    sal_map = H.salaries_2025_26()
    shared = shared_inputs()
    augment_surplus(sal_map, shared)        # roster-independent surplus (covers traded/FA players)
    trades = H.two_team_trades()
    pkgs = H.build_packages(trades, tri_of, sal_map)
    fit = [p for p in pkgs if p["fit_set"]]
    held = [p for p in pkgs if not p["fit_set"]]
    fleeces = H.generate_fleeces()

    base = {k: (_PICK_PTS[0] if k == "PICK_PTS_PER" else getattr(PA, k)) for k in TUNABLE}
    set_params(base)
    r0, j0 = evaluate(fit, fleeces, tri_of, sal_map, shared)
    print(f"=== baseline (pre-tune) ===  fit recall {r0*100:.0f}% ({len(fit)} trades) | fleece reject {j0*100:.0f}% ({len(fleeces)})")

    # coordinate descent: maximize fit recall s.t. fleece reject >= 0.90, inside sane bounds
    best = dict(base)
    set_params(best)
    best_r, best_j = evaluate(fit, fleeces, tri_of, sal_map, shared)
    for _ in range(2):
        for k, grid in TUNABLE.items():
            for v in grid:
                if not (SANE[k][0] <= v <= SANE[k][1]):
                    continue
                trial = dict(best); trial[k] = v
                set_params(trial)
                r, j = evaluate(fit, fleeces, tri_of, sal_map, shared)
                if j >= 0.90 and (r > best_r or (r == best_r and j > best_j)):
                    best, best_r, best_j = trial, r, j
        set_params(best)
    print(f"=== tuned ===  fit recall {best_r*100:.0f}% | fleece reject {best_j*100:.0f}%")
    for k in TUNABLE:
        print(f"    {k:22} {base[k]} -> {best[k]}")

    # leave-one-out recall on the fit set with tuned params
    set_params(best)
    loo = []
    for i in range(len(fit)):
        acc = run_trade(fit[i], tri_of, sal_map, shared)["accepted"]
        loo.append(acc)
    loo_recall = sum(loo) / len(loo)
    print(f"\n=== leave-one-out recall (tuned): {loo_recall*100:.0f}% ===")

    # held-out 9 offseason trades (generalization check, NOT in the fit)
    set_params(best)
    held_acc = [run_trade(p, tri_of, sal_map, shared)["accepted"] for p in held]
    print(f"=== held-out offseason generalization: {sum(held_acc)}/{len(held)} accepted ===")

    # unexplained real trades the tuned model still rejects (the informative misses)
    print("\n=== unexplained real trades (tuned model rejects a deal that happened) ===")
    fail_modes = collections.Counter()
    for p in fit:
        res = run_trade(p, tri_of, sal_map, shared)
        if not res["accepted"]:
            why = []
            for side, tag in ((res["A"], p["A"]), (res["B"], p["B"])):
                if not side["accepted"]:
                    # classify the dominant reason this side said no
                    if not side["balanced"]:
                        fail_modes["unbalanced salary (>$10M take-back)"] += 1
                        mode = "unbalanced"
                    elif side["delta_value"] < 0:
                        fail_modes["value-negative side (zero-sum surplus)"] += 1
                        mode = "value-neg"
                    else:
                        fail_modes["positive value but gate (fit/need/absorb) blocks"] += 1
                        mode = "gated"
                    why.append(f"{tag} [{mode} dv={side['delta_value']} bal={side['balanced']} "
                               f"fit={side['best_recv_fit']} need={side['need_gain']} absorb={side['net_absorb']/1e6:.0f}M]")
            print(f"  {p['date']} {p['A']}<->{p['B']}: {'; '.join(why)}")
    print("\n=== failure-mode tally (per rejecting side) ===")
    for m, n in fail_modes.most_common():
        print(f"  {n:2}  {m}")


if __name__ == "__main__":
    main()
