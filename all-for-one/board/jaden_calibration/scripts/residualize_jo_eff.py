"""Jaden markers v0.2 -- residualize JO-EFF against usage change (section-2b fix).

The v0.1 headline (report section 2b) found that the JO-EFF "leap" band on the
defense-screened class is populated by offense-first scorers who raised true
shooting by CUTTING usage next to the star (fewer, easier shots), not by a
two-way skill jump. A bare TS climb is therefore usage-compression gravity, not
growth.

v0.2 fixes the measure directly. Across the 19 defense-screened wings we:
  1. pull usg_pct (nba_player_season_bio, a FRACTION) for each wing's before_ss
     and after_ss (join on nba_player_id; max-gp stint per player-season, exactly
     the row compute_markers.py used for ts_after), and form usg_delta.
  2. fit OLS of the own-baseline efficiency climb (ts_after_vs_trail3) on
     usg_delta, and report slope / intercept / R^2 / residual SD.
  3. define the JO-EFF leap band on the RESIDUAL -- the efficiency gain IN EXCESS
     of what the usage change predicts -- and propose a residual threshold.
  4. report the residualized leap-band composition (names) and check whether it
     STILL selects usage-cutters.

Also reconciles the JO-GROWTH rung definitions to the report's stated class
counts (20/14/6/27 full-38), recomputes the growth signals on the screened 19
under those canonical definitions, builds the LEAP tier, and runs the
one-vs-two growth-signal sensitivity. All thresholds PROPOSED / TUNE; freezes
nothing. Descriptive, not causal; n=19 is small -- read as priors.

Writes data/jo_eff_residuals.parquet and data/leap_tier_v02.json. No p-values.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "board" / "jaden_calibration" / "data"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 100)
pd.set_option("display.max_rows", 100)

SEEDS = {203932: "Aaron Gordon", 1628969: "Mikal Bridges", 1628384: "OG Anunoby"}
GORDON_ID = 203932


def med(s):
    return float(pd.Series(s).dropna().median())


def q(s, p):
    return float(pd.Series(s).dropna().quantile(p))


# ---- canonical JO-GROWTH rungs (reproduce report class counts 20/14/6/27) ----
def rung_a(d):  # self-created efficiency: pull-up eFG% OR drive FG% up by >= +0.010
    pu = (d.pull_up_efg_after - d.pull_up_efg_before) >= 0.010
    dr = (d.drive_fg_pct_after - d.drive_fg_pct_before) >= 0.010
    return (pu.fillna(False) | dr.fillna(False))


def rung_b(d):  # FT rate: FTA/FGA up by >= +0.010
    return ((d.ftr_after - d.ftr_before) >= 0.010).fillna(False)


def rung_c(d):  # 3P volume AND accuracy both rising
    return ((d.fg3a_pg_after > d.fg3a_pg_before) & (d.fg3_pct_after > d.fg3_pct_before)).fillna(False)


def growth_count(d):
    return rung_a(d).astype(int) + rung_b(d).astype(int) + rung_c(d).astype(int)


def main():
    m = pd.read_parquet(DATA / "marker_movements.parquet")

    # sanity: canonical rung defs reproduce the report's full-38 counts
    a, b, c = rung_a(m), rung_b(m), rung_c(m)
    assert (a.sum(), b.sum(), c.sum(), (a | b | c).sum()) == (20, 14, 6, 27), (
        "growth rung defs drifted from report class counts")

    # -------- defense screen: jd_load_before >= class median (BEFORE deployment) --------
    thr = med(m.jd_load_before)
    scr = m[m.jd_load_before >= thr].copy().reset_index(drop=True)
    print(f"defense screen jd_load_before >= class median {thr:.4f}: "
          f"full {len(m)} -> screened {len(scr)}")
    print(f"  Gordon jd_load_before = "
          f"{float(m[m.player_id==GORDON_ID].jd_load_before.iloc[0]):.4f} "
          f"(< {thr:.4f}: OUT of class, appendix row)")

    # -------- 1. pull usage, form usg_delta --------
    pids = sorted(scr.player_id.unique().tolist())
    bio = query(
        """SELECT player_id, LEFT(season_year,4)::int AS ss, gp, usg_pct
           FROM nba.nba_player_season_bio
           WHERE season_type = %s AND player_id = ANY(%s)""",
        ("Regular Season", pids),
    )
    bio["usg_pct"] = pd.to_numeric(bio.usg_pct, errors="coerce")  # FRACTION
    bio_ps = bio.sort_values("gp").groupby(["player_id", "ss"], as_index=False).last()
    usg = {(int(r.player_id), int(r.ss)): r.usg_pct for r in bio_ps.itertuples() if pd.notna(r.usg_pct)}
    scr["usg_before"] = [usg.get((int(p), int(s))) for p, s in zip(scr.player_id, scr.before_ss)]
    scr["usg_after"] = [usg.get((int(p), int(s))) for p, s in zip(scr.player_id, scr.after_ss)]
    scr["usg_delta"] = scr.usg_after - scr.usg_before
    assert scr.usg_delta.notna().all(), "missing usg for a screened member"

    # -------- 2. OLS: ts_after_vs_trail3 ~ usg_delta --------
    y = scr.ts_after_vs_trail3.to_numpy(float)
    x = scr.usg_delta.to_numpy(float)
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    intercept, slope = float(beta[0]), float(beta[1])
    yhat = X @ beta
    resid = y - yhat
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot
    resid_sd = float(np.std(resid, ddof=1))   # sample SD, used for the +1 SD band
    scr["ts_climb_pred_from_usg"] = yhat
    scr["jo_eff_residual"] = resid

    print("\n=== 1-2. RESIDUALIZE JO-EFF (n=19) ===")
    print(f"  OLS  ts_after_vs_trail3 = {intercept:+.5f} + ({slope:+.5f}) * usg_delta")
    print(f"  slope      {slope:+.5f}   (efficiency-climb change per +1.00 usage fraction)")
    print(f"  per +0.01 usage: {slope*0.01:+.5f} TS-climb")
    print(f"  intercept  {intercept:+.5f}")
    print(f"  R^2        {r2:.4f}")
    print(f"  residual SD {resid_sd:.5f}  (mean resid {resid.mean():+.2e})")

    # -------- 3. residual leap band: two proposed thresholds --------
    thr_1sd = resid_sd            # residual >= +1 SD (mean resid ~ 0)
    thr_p75 = q(resid, 0.75)      # residual 75th percentile
    scr["leap_resid_1sd"] = scr.jo_eff_residual >= thr_1sd
    scr["leap_resid_p75"] = scr.jo_eff_residual >= thr_p75
    band_1sd = list(scr[scr.leap_resid_1sd].sort_values("jo_eff_residual", ascending=False).wing)
    band_p75 = list(scr[scr.leap_resid_p75].sort_values("jo_eff_residual", ascending=False).wing)

    # v0.1 bare-TS leap band for contrast (section 2b defs)
    bare = scr[(scr.ts_after_vs_trail3 >= 0.019) &
               ((scr.ts_vs_lg_after - scr.ts_vs_lg_before) >= 0.021)]
    print("\n=== 3. residual leap band ===")
    print(f"  PROPOSED thr A: residual >= +1 SD  ({thr_1sd:+.4f}) -> {len(band_1sd)}/19  {band_1sd}")
    print(f"  PROPOSED thr B: residual >= 75th pct ({thr_p75:+.4f}) -> {len(band_p75)}/19  {band_p75}")
    print(f"  v0.1 bare-TS leap band (for contrast): {list(bare.wing)}")

    # residual table sorted
    scr["growth_signals"] = growth_count(scr)
    show = ["wing", "before_ss", "after_ss", "usg_delta", "ts_after_vs_trail3",
            "ts_climb_pred_from_usg", "jo_eff_residual", "growth_signals"]
    print("\n  residuals (sorted desc):")
    with pd.option_context("display.float_format", lambda v: f"{v:+.4f}"):
        print(scr.sort_values("jo_eff_residual", ascending=False)[show].to_string(index=False))

    # -------- 4. LEAP tier --------
    # defensive gate PASS per section 5 composite, JD-COVER de-weighted to supporting:
    #   gate FAILS only if JD-LOAD fails AND JD-HOLD fails; else PASS.
    # JD-LOAD pass at after-share >= screened median; JD-HOLD pass at jd_hold_after < 0.
    load_pass_thr = med(scr.jd_load_after)
    scr["jd_load_pass"] = scr.jd_load_after >= load_pass_thr
    scr["jd_hold_pass"] = scr.jd_hold_after < 0
    scr["gate_pass_composite"] = ~((~scr.jd_load_pass) & (~scr.jd_hold_pass))
    scr["gate_pass_strict"] = scr.jd_load_pass & scr.jd_hold_pass  # both, for reference
    # JO-FLOOR intact: sa75 not down more than 15%
    scr["floor_intact"] = scr.sa75_pctchg > -15.0

    def leap_set(resid_col, n_growth, gate_col="gate_pass_composite"):
        mask = (scr[gate_col] & scr[resid_col] & scr.floor_intact &
                (scr.growth_signals >= n_growth))
        return scr[mask]

    print("\n=== 4. LEAP tier ===")
    print(f"  JD-LOAD pass thr (screened median jd_load_after) = {load_pass_thr:.4f}")
    print(f"  gate PASS (composite, JD-LOAD+JD-HOLD): {int(scr.gate_pass_composite.sum())}/19")
    print(f"  gate PASS (strict both):                {int(scr.gate_pass_strict.sum())}/19")
    print(f"  JO-FLOOR intact (sa75 > -15%):          {int(scr.floor_intact.sum())}/19")
    print(f"  >=1 growth signal: {int((scr.growth_signals>=1).sum())}/19   "
          f">=2: {int((scr.growth_signals>=2).sum())}/19")

    results = {}
    for rlabel, rcol in [("resid>=+1SD", "leap_resid_1sd"), ("resid>=p75", "leap_resid_p75")]:
        for ng in (1, 2):
            s1 = leap_set(rcol, ng)
            results[(rlabel, ng)] = list(s1.wing)
            print(f"  LEAP [{rlabel}, >={ng} growth, composite gate]: "
                  f"{len(s1)}  {list(s1.wing)}")

    # -------- persist --------
    keep = ["player_id", "wing", "before_ss", "after_ss", "creator", "new_team",
            "usg_before", "usg_after", "usg_delta",
            "ts_after_vs_trail3", "ts_vs_lg_before", "ts_vs_lg_after",
            "ts_climb_pred_from_usg", "jo_eff_residual",
            "leap_resid_1sd", "leap_resid_p75",
            "growth_signals", "sa75_pctchg", "floor_intact",
            "jd_load_after", "jd_hold_after", "jd_load_pass", "jd_hold_pass",
            "gate_pass_composite", "gate_pass_strict"]
    scr[keep].to_parquet(DATA / "jo_eff_residuals.parquet", index=False)

    out = {
        "n_screened": len(scr),
        "screen_threshold_jd_load_before": thr,
        "residualization": {
            "model": "ts_after_vs_trail3 ~ usg_delta (OLS, n=19)",
            "slope": slope, "intercept": intercept, "r2": r2,
            "residual_sd": resid_sd,
            "slope_per_0.01_usage": slope * 0.01,
        },
        "residual_leap_band": {
            "PROPOSED_primary": "residual >= +1 SD (primary); >= 75th pct alternative -- identical LEAP set",
            "thr_1sd": thr_1sd, "band_1sd": band_1sd,
            "thr_p75": thr_p75, "band_p75": band_p75,
            "v01_bare_ts_band": list(bare.wing),
        },
        "growth_rungs_canonical": {
            "a": "pull-up eFG% OR drive FG% up by >= +0.010",
            "b": "FTA/FGA up by >= +0.010",
            "c": "fg3a/g up AND fg3_pct up",
            "screened_any": int((scr.growth_signals >= 1).sum()),
            "screened_two": int((scr.growth_signals >= 2).sum()),
        },
        "leap_tier": {
            "definition": "gate PASS (composite JD-LOAD+JD-HOLD) AND residual leap band "
                          "AND JO-FLOOR intact (sa75 > -15%) AND >=1 growth signal",
            "jd_load_pass_thr": load_pass_thr,
            "gate_pass_composite_n": int(scr.gate_pass_composite.sum()),
            "gate_pass_strict_n": int(scr.gate_pass_strict.sum()),
            "sets": {f"{r}|>={g}growth": v for (r, g), v in results.items()},
        },
        "jd_cover_coverage": "34/38 computed, 4 panel-pending (2025-26 AFTERs)",
        "gordon_appendix": {
            "jd_load_before": float(m[m.player_id == GORDON_ID].jd_load_before.iloc[0]),
            "screen_threshold": thr,
            "status": "adjacent-informative, OUT of calibration class",
        },
    }
    (DATA / "leap_tier_v02.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"\nwrote {DATA/'jo_eff_residuals.parquet'}")
    print(f"wrote {DATA/'leap_tier_v02.json'}")


if __name__ == "__main__":
    main()
