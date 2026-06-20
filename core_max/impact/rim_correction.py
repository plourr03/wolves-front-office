#!/usr/bin/env python3
"""Phase 1b: the box-to-RAPM rim correction.

Box-BPM systematically UNDER-rates rim protection (a shot-alterer who does not block gets
little box credit), so a uniform box prior buries rim protectors like Joan on the exact
dimension the bet is about. This learns, from established players, how much box underrates
a player as a function of a MEASURED rim-protection signal (rim deterrence + block rate
from the frozen warehouse snapshot), never from def_rapm. The correction is therefore
box-computable and small-sample-stable, so it applies to a prior-dominated rookie (Joan)
using only his measurable rim stats, with no dependence on his unreliable RAPM.

Validated LEAVE-ONE-OUT (not in-sample): does the corrected box estimate pull genuine rim
protectors (Gobert, Wembanyama) toward their RAPM and leave a nominal-but-weak
rim-protecting center (Claxton) alone, out of sample, without overcorrecting the mid-pack.

    python core_max/impact/rim_correction.py
"""
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "core_max"))
from data_pull import frozen  # noqa: E402

PV = os.path.join(REPO, "offseason", "data", "player_value.csv")
OUTDIR = os.path.join(REPO, "core_max", "outputs", "phase1")
RELIABLE_POSS = 3000     # the FIT population: established players (matches build_rapm)
MIN_RIM_FGA = 50         # require a usable rim-contest sample to carry a rim signal
FEATS = ["rim_stops_per_g", "blk_per_g"]
JOAN_PID = 1642866


def rim_signal(snapshot_id=None):
    """Aggregate the 3 frozen rim-defense seasons into per-player, small-sample-stable
    signals: rim_stops_per_g (deterrence vs league-average rim D) and blk_per_g."""
    rim, sid = frozen.load("rim_defense", snapshot_id)
    rim = rim.copy()
    for c in ("gp", "def_rim_fgm", "def_rim_fga", "blk", "def_rim_fg_pct"):
        rim[c] = pd.to_numeric(rim[c], errors="coerce")
    g = (rim.groupby("player_id")
            .agg(gp=("gp", "sum"), fgm=("def_rim_fgm", "sum"),
                 fga=("def_rim_fga", "sum"), blk=("blk", "sum"))
            .reset_index())
    g = g[g["fga"] >= MIN_RIM_FGA].copy()
    lg = g["fgm"].sum() / g["fga"].sum()                       # league rim FG% (volume-weighted)
    g["rim_fgpct"] = g["fgm"] / g["fga"]
    g["fga_per_g"] = g["fga"] / g["gp"].clip(lower=1)
    g["blk_per_g"] = g["blk"] / g["gp"].clip(lower=1)
    g["rim_stops_per_g"] = g["fga_per_g"] * (lg - g["rim_fgpct"])   # FGs prevented vs lg-avg rim D
    return g, lg, sid


def fit_correction(df):
    """Center features, fit (net_rapm - box_net_bpm) ~ features with intercept, so an
    average rim protector gets ~0 correction and only genuine rim protection moves the box
    estimate. Returns (intercept, coef, feature means)."""
    mu = df[FEATS].mean()
    Xc = (df[FEATS] - mu).to_numpy()
    y = df["resid"].to_numpy()
    X1 = np.column_stack([np.ones(len(Xc)), Xc])
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    return beta[0], beta[1:], mu


def predict(df, b0, coef, mu):
    return b0 + (df[FEATS] - mu).to_numpy() @ coef


def main():
    pv = pd.read_csv(PV)
    sig, lg, sid = rim_signal()
    print(f"frozen snapshot: {sid} | league rim FG% = {lg:.3f} | players with a rim signal: {len(sig)}")

    d = pv.merge(sig[["player_id"] + FEATS], on="player_id", how="left")
    d["resid"] = d["net_rapm"] - d["box_net_bpm"]
    fitpop = d.dropna(subset=FEATS)
    fitpop = fitpop[fitpop["possessions"] >= RELIABLE_POSS].copy().reset_index(drop=True)
    print(f"fit population (reliable established players with a rim signal): {len(fitpop)}")

    b0, coef, mu = fit_correction(fitpop)
    terms = " + ".join(f"{c:+.3f}*({f} - {mu[f]:.3f})" for c, f in zip(coef, FEATS))
    print(f"correction model: (net_rapm - box) ~ {b0:+.3f} {terms}")

    # LEAVE-ONE-OUT validation (never in-sample)
    loo = np.zeros(len(fitpop))
    for i in range(len(fitpop)):
        sub = fitpop.drop(i)
        bb0, bcoef, bmu = fit_correction(sub)
        loo[i] = predict(fitpop.iloc[[i]], bb0, bcoef, bmu)[0]
    fitpop["corr_loo"] = loo
    fitpop["corrected_loo"] = fitpop["box_net_bpm"] + fitpop["corr_loo"]

    rmse_box = float(np.sqrt(((fitpop["net_rapm"] - fitpop["box_net_bpm"]) ** 2).mean()))
    rmse_cor = float(np.sqrt(((fitpop["net_rapm"] - fitpop["corrected_loo"]) ** 2).mean()))
    print(f"\nLOO box-to-RAPM gap: RMSE {rmse_box:.3f} (raw box) -> {rmse_cor:.3f} (corrected) "
          f"= {100*(rmse_box-rmse_cor)/rmse_box:+.1f}% out-of-sample")

    # directional checks: rim protectors should be lifted toward RAPM; a weak-rim center should not
    print(f"\n{'player':22s} {'net_rapm':>9s} {'box':>7s} {'+corr(LOO)':>11s} {'corrected':>10s} {'rim_stops/g':>12s}")
    for nm in ["Rudy Gobert", "Victor Wembanyama", "Chet Holmgren", "Bam Adebayo", "Nic Claxton"]:
        r = fitpop[fitpop["player_name"].str.contains(nm, na=False)]
        if len(r):
            r = r.iloc[0]
            print(f"{nm:22s} {r['net_rapm']:>+9.2f} {r['box_net_bpm']:>+7.2f} {r['corr_loo']:>+11.2f} "
                  f"{r['corrected_loo']:>+10.2f} {r['rim_stops_per_g']:>12.2f}")

    # mid-pack must not be overcorrected: |correction| for near-average rim protection
    midmask = fitpop["rim_stops_per_g"].between(fitpop["rim_stops_per_g"].quantile(0.4),
                                                fitpop["rim_stops_per_g"].quantile(0.6))
    print(f"\nmid-pack (40-60th pct rim_stops): mean |correction| = {fitpop.loc[midmask,'corr_loo'].abs().mean():.3f} "
          f"(should be near zero)")

    # apply the correction, GATED on reliability (a GATE, not a guideline). The correction was
    # validated LOO on the RELIABLE population; applying it to an unreliable small sample is
    # out-of-domain extrapolation into the regime where the box-vs-RAPM relationship INVERTS
    # (young bigs with inflated per-36 box readings). So it is switched OFF for unreliable
    # players, full stop; their value comes from the Phase 2 development module, never here.
    allrim = d.dropna(subset=FEATS).copy()
    allrim["reliable_bool"] = allrim["reliable"].astype(str).str.upper().isin(["TRUE", "1"])
    raw_corr = predict(allrim, b0, coef, mu)
    allrim["correction"] = np.where(allrim["reliable_bool"], raw_corr, 0.0)
    allrim["correction_suppressed"] = ~allrim["reliable_bool"]
    allrim["corrected_box"] = allrim["box_net_bpm"] + allrim["correction"]
    os.makedirs(OUTDIR, exist_ok=True)
    cols = ["player_id", "player_name", "possessions", "reliable", "net_rapm", "box_net_bpm"] + \
        FEATS + ["correction", "correction_suppressed", "corrected_box"]
    out = os.path.join(OUTDIR, "rim_correction.csv")
    allrim[cols].sort_values("correction", ascending=False).to_csv(out, index=False)
    print(f"\nwrote {out} ({len(allrim)} players)")

    # Joan: unreliable sample, so the gate SUPPRESSES the correction. Show the would-be
    # correction for transparency, but it is NOT applied; his box prior is left untouched for
    # the Phase 2 development module (his value is a development wager, not a box-underrating
    # rescue, and the box-vs-RAPM relationship inverts in his small-sample regime).
    jr = sig[sig["player_id"] == JOAN_PID]
    jpv = pv[pv["player_id"] == JOAN_PID]
    if len(jr) and len(jpv):
        jr = jr.iloc[0]
        reliable = str(jpv.iloc[0]["reliable"]).upper() in ("TRUE", "1")
        would = float(b0 + (np.array([jr[f] for f in FEATS]) - mu.to_numpy()) @ coef)
        jbox = float(jpv.iloc[0]["box_net_bpm"])
        state = "APPLIED" if reliable else "SUPPRESSED (unreliable: out of the validated domain)"
        print(f"\nJoan Beringer: reliable={reliable}, box prior {jbox:+.2f}, would-be rim correction "
              f"{would:+.2f} -> {state}. The gate keeps the correction off Joan; his box prior is left "
              f"for the Phase 2 development module.")
    else:
        print(f"\nJoan (pid {JOAN_PID}) not resolvable in the rim signal / player_value at the floor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
