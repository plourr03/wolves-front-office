"""
The two gates before any title number publishes.

GATE 1 (calibration re-validation, stop-if-fail): re-fit the series logit EXCLUDING the
sealed seasons and DIFF against the old params; re-fit net->wins (its SCALE anchor is
2023-26, which does not touch the sealed block) and diff. Pass if the re-fit reproduces
the old params within ~2 SE (a cross-validation), fail if it diverges.

GATE 2 (retrodiction on the sealed 2016-17/17-18/18-19/22-23 holdout):
  Case 2 (series-frequency): using the RE-FIT (sealed-excluded) resolver, predict the
    favorite-wins-series rate by net-gap bucket on the SEALED series; pass if at most 1 of
    5 buckets falls outside its 90% binomial interval and the signed error is not monotone.
  Case 3 (star-acquisition power): count qualifying sealed-era star acquisitions; report
    whether n >= 8 (full power) per the pre-registered rule.
  Case 1 (preseason board): cannot run, sealed-season de-vigged boards are not in the repo;
    flagged, not silently skipped. The SHAPE anchor used only non-sealed boards, so it is
    not leaked; the board-reproduction retrodiction simply awaits that data.

Run: python lamelo/sim/run_gates.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import statsmodels.api as sm
from scipy.stats import binom

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "offseason" / "scripts"))
sys.path.insert(0, str(REPO / "postmortem"))
import build_series_calibration as SC  # noqa: E402
import series_resolver as D            # noqa: E402

SEALED = {2016, 2017, 2018, 2022}      # 2016-17, 2017-18, 2018-19, 2022-23
OLD = {"b0": 0.5018, "b1": 0.1345, "wins_a": 41.0, "wins_b": 2.239}
# Hand-verified qualifying star acquisitions in the sealed seasons (All-Star prior 2 yrs,
# acquired by trade, >=20 games with the new team). The automated reconstruction from
# nba_transactions is a documented refinement; this list is decisive for the power verdict.
SEALED_STAR_ACQ = [
    ("2016-17", "DeMarcus Cousins -> NOP"),
    ("2017-18", "Paul George -> OKC"), ("2017-18", "Jimmy Butler -> MIN"),
    ("2017-18", "Kyrie Irving -> BOS"), ("2017-18", "Chris Paul -> HOU"),
    ("2017-18", "Blake Griffin -> DET"),
    ("2018-19", "Kawhi Leonard -> TOR"), ("2018-19", "Jimmy Butler -> PHI"),
    ("2018-19", "Kristaps Porzingis -> DAL"), ("2018-19", "Marc Gasol -> TOR"),
    ("2018-19", "Tobias Harris -> PHI"),
    ("2022-23", "Rudy Gobert -> MIN"), ("2022-23", "Donovan Mitchell -> CLE"),
    ("2022-23", "Dejounte Murray -> ATL"), ("2022-23", "Kevin Durant -> PHX"),
    ("2022-23", "Kyrie Irving -> DAL"),
]


def fit_logit(net, po, exclude):
    games = {}
    for _, r in po.iterrows():
        gid = r["game_id"]; g = games.setdefault(gid, {"yr": int(r["yr"])})
        if r["home"] == 1:
            g["home_tm"] = r["tm"]; g["home_won"] = (r["wl"] == "W")
        else:
            g["away_tm"] = r["tm"]
    diffs, ys = [], []
    for gid, g in games.items():
        if g["yr"] in exclude or "home_tm" not in g or "away_tm" not in g:
            continue
        kh, ka = (g["yr"], g["home_tm"]), (g["yr"], g["away_tm"])
        if kh not in net or ka not in net:
            continue
        diffs.append(net[kh] - net[ka]); ys.append(1 if g["home_won"] else 0)
    X = sm.add_constant(np.array(diffs))
    res = sm.Logit(np.array(ys), X).fit(disp=0)
    return float(res.params[0]), float(res.params[1]), float(res.bse[0]), float(res.bse[1]), len(ys)


def main():
    print("pulling 1997-2025 net/wins/playoff games ...", flush=True)
    net, wins, po = SC.pull()
    series = SC.assemble_series(net, wins, po)

    # ---- GATE 1a: series logit re-fit excluding sealed, diff vs old ----
    b0, b1, se0, se1, n = fit_logit(net, po, SEALED)
    d0, d1 = abs(b0 - OLD["b0"]) / se0, abs(b1 - OLD["b1"]) / se1
    g1a = (d0 < 2) and (d1 < 2)
    print("\n=== GATE 1a: series logit re-fit (FIT-era, sealed excluded) vs old ===")
    print(f"  b0 (HCA)   = {b0:+.4f} (se {se0:.4f}); old {OLD['b0']:+.4f}; diff {d0:.2f} SE")
    print(f"  b1 (slope) = {b1:+.4f} (se {se1:.4f}); old {OLD['b1']:+.4f}; diff {d1:.2f} SE")
    print(f"  n games {n}.  -> {'PASS' if g1a else 'FAIL'} (reproduces old within 2 SE)")

    # ---- GATE 1b: net->wins re-fit excluding sealed, diff vs old ----
    xs = [nt for (yr, tm), nt in net.items() if yr not in SEALED and (yr, tm) in wins]
    ys = [wins[(yr, tm)] for (yr, tm), nt in net.items() if yr not in SEALED and (yr, tm) in wins]
    wb, wa = np.polyfit(np.array(xs), np.array(ys), 1)
    g1b = abs(wa - OLD["wins_a"]) < 1.5 and abs(wb - OLD["wins_b"]) < 0.25
    print("\n=== GATE 1b: net->wins re-fit (FIT-era) vs old ===")
    print(f"  wins = {wa:.2f} + {wb:.3f} * net   (old {OLD['wins_a']} + {OLD['wins_b']})  "
          f"-> {'PASS' if g1b else 'FAIL'}")

    # ---- GATE 2 Case 2: series-frequency retrodiction on sealed, re-fit resolver ----
    D._PARAMS = {"b0": b0, "b1": b1, "b0_se": se0, "b1_se": se1}
    sealed_series = [s for s in series if s["yr"] in SEALED]
    bins = [(0, 2), (2, 4), (4, 6), (6, 9), (9, 99)]
    print(f"\n=== GATE 2 Case 2: series-frequency on {len(sealed_series)} sealed-era series ===")
    print(f"  {'gap':>7}{'n':>4}{'obs fav%':>10}{'pred fav%':>11}{'90% CI (count)':>18}{'':>6}")
    outside, signs = 0, []
    for lo, hi in bins:
        emp, pred = [], []
        for s in sealed_series:
            net_f = max(s["net_champ"], s["net_loser"]); net_d = min(s["net_champ"], s["net_loser"])
            gap = net_f - net_d
            if not (lo <= gap < hi):
                continue
            fav = s["champ"] if s["net_champ"] >= s["net_loser"] else s["loser"]
            emp.append(1 if s["champ"] == fav else 0)
            pred.append(D.base_series_prob(net_f, net_d, s["hc_team"] == fav))
        nb = len(emp)
        if nb == 0:
            continue
        k, pp = sum(emp), float(np.mean(pred))
        lo_ci, hi_ci = int(binom.ppf(0.05, nb, pp)), int(binom.ppf(0.95, nb, pp))
        within = lo_ci <= k <= hi_ci
        outside += 0 if within else 1
        signs.append(np.sign(k / nb - pp))
        lab = f"{lo}-{hi if hi < 99 else '+'}"
        print(f"  {lab:>7}{nb:>4}{k/nb*100:>9.0f}%{pp*100:>10.0f}%   [{lo_ci},{hi_ci}]{'  OK' if within else '  OUT':>6}")
    monotone = len(set(signs)) == 1 and len(signs) >= 4
    g2c2 = (outside <= 1) and not monotone
    print(f"  buckets outside 90% interval: {outside}; signed-error monotone: {monotone}  "
          f"-> {'PASS' if g2c2 else 'FAIL'}")

    # ---- GATE 2 Case 3: star-acquisition power ----
    n_star = len(SEALED_STAR_ACQ)
    g2c3_power = n_star >= 8
    # AUDIT FIX 5: clearance must use Case 3 PASS/FAIL, not power. Power is necessary, not
    # sufficient. The win-total backtest is run in run_case3.py and FAILED (5/8 sign, 2/8
    # within-4). Set the actual result here so the summary cannot read "CLEARED" on power alone.
    g2c3_pass = False
    print(f"\n=== GATE 2 Case 3: star-acquisition ===")
    print(f"  power: n = {n_star} qualifying ({'FULL, n>=8' if g2c3_power else 'LOW'}).")
    print(f"  RESULT (win-total backtest, run_case3.py): FAILED (5/8 sign, 2/8 within-4).")

    # ---- Case 1 flag ----
    print("\n=== GATE 2 Case 1: preseason-board retrodiction ===")
    print("  CANNOT RUN: sealed-season de-vigged boards are not in the repo. The SHAPE anchor used")
    print("  only non-sealed boards (no leak); the board-reproduction retrodiction awaits that data.")

    print("\n========== GATE SUMMARY ==========")
    print(f"  Gate 1a series logit diff : {'PASS' if g1a else 'FAIL'}")
    print(f"  Gate 1b net->wins diff    : {'PASS' if g1b else 'FAIL'}")
    print(f"  Gate 2 Case 2 series freq : {'PASS' if g2c2 else 'FAIL'}")
    print(f"  Gate 2 Case 3             : power {'FULL' if g2c3_power else 'LOW'} / result {'PASS' if g2c3_pass else 'FAILED'}")
    print(f"  Gate 2 Case 1 board       : DEFERRED (data missing)")
    overall = g1a and g1b and g2c2 and g2c3_pass  # AUDIT FIX 5: PASS, not power
    print(f"  -> title number {'CLEARED' if overall else 'STAYS GATED (Case 3 failed; and the delta is not identifiable)'}")


if __name__ == "__main__":
    main()
