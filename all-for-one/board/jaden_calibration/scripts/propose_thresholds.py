"""Per-marker BEFORE->AFTER movement distributions + PROPOSED thresholds.

Reads marker_movements.parquet and jd_cover.parquet. Reports mean/median/spread
and quantiles for every marker, where the three seeds land, and the fraction of
the class satisfying candidate rungs. Derives PROPOSED (TUNE, frozen NOTHING)
threshold bands for the offensive ladder and the defensive gate from where the
calibration-class distribution sits. No p-values; exact counts everywhere.

Writes data/threshold_proposals.json and prints the full readout that the report
quotes verbatim.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
OUTDIR = REPO / "all-for-one" / "board" / "jaden_calibration" / "data"

SEEDS = {203932: "Aaron Gordon", 1628969: "Mikal Bridges", 1628384: "OG Anunoby"}
Q = [0.10, 0.25, 0.50, 0.75, 0.90]


def dist(s: pd.Series) -> dict:
    s = s.dropna()
    return {
        "n": int(s.size), "mean": float(s.mean()), "median": float(s.median()),
        "sd": float(s.std(ddof=1)) if s.size > 1 else float("nan"),
        "q10": float(s.quantile(.10)), "q25": float(s.quantile(.25)),
        "q75": float(s.quantile(.75)), "q90": float(s.quantile(.90)),
        "min": float(s.min()), "max": float(s.max()),
    }


def line(name, s, fmt="{:+.3f}"):
    d = dist(s)
    def f(x):
        return fmt.format(x)
    print(f"  {name:30s} n={d['n']:2d} | mean {f(d['mean'])} median {f(d['median'])} "
          f"sd {d['sd']:.3f} | q10 {f(d['q10'])} q25 {f(d['q25'])} q75 {f(d['q75'])} q90 {f(d['q90'])} "
          f"| [{f(d['min'])}, {f(d['max'])}]")
    return d


def seedvals(df, col, fmt="{:+.3f}"):
    out = []
    for pid, nm in SEEDS.items():
        r = df[df.player_id == pid]
        if len(r) and pd.notna(r.iloc[0][col]):
            out.append(f"{nm.split()[-1]} {fmt.format(r.iloc[0][col])}")
    return ", ".join(out)


def main() -> None:
    m = pd.read_parquet(OUTDIR / "marker_movements.parquet")
    cov = pd.read_parquet(OUTDIR / "jd_cover.parquet")
    n = len(m)
    print(f"CALIBRATION CLASS n = {n} (marker-usable). Descriptive only; movement is")
    print("confounded by age, role, health. No p-values. Exact counts throughout.\n")

    prop = {"class_n": n, "notes": "PROPOSED / TUNE. Freezes nothing.", "markers": {}}

    # ================= OFFENSIVE LADDER =================
    print("=" * 110)
    print("OFFENSIVE LADDER")
    print("=" * 110)

    print("\nJO-EFF  true shooting movement")
    d_ts = line("ts_delta (after-before)", m.ts_delta)
    d_tslg = line("ts_vs_league AFTER", m.ts_vs_lg_after)
    d_tslg_mv = line("d(ts_vs_league) after-before", m.ts_vs_lg_after - m.ts_vs_lg_before)
    d_tr3 = line("ts_after_vs_trail3", m.ts_after_vs_trail3)
    print("  seeds ts_delta:", seedvals(m, "ts_delta"))
    print("  seeds ts_after_vs_trail3:", seedvals(m, "ts_after_vs_trail3"))
    # bands from class quantiles of the two climb measures
    leap_tr3 = round(d_tr3["q75"], 3)
    leap_lgmv = round(d_tslg_mv["q75"], 3)
    decl_tr3 = round(d_tr3["q25"], 3)
    print(f"\n  PROPOSED JO-EFF bands (clears BOTH league-relative and own trailing-3):")
    print(f"    LEAP    : ts_after_vs_trail3 >= {leap_tr3:+.3f} AND d(ts_vs_league) >= {leap_lgmv:+.3f}  (~class 75th pct)")
    print(f"    FLAT    : ts_after_vs_trail3 in ({decl_tr3:+.3f}, {leap_tr3:+.3f})")
    print(f"    DECLINE : ts_after_vs_trail3 <= {decl_tr3:+.3f}  (~class 25th pct)")
    prop["markers"]["JO-EFF"] = {
        "dist_ts_delta": d_ts, "dist_ts_after_vs_trail3": d_tr3,
        "dist_d_ts_vs_league": d_tslg_mv,
        "proposed": {"leap_ts_after_vs_trail3_ge": leap_tr3,
                     "leap_d_ts_vs_league_ge": leap_lgmv,
                     "decline_ts_after_vs_trail3_le": decl_tr3}}

    print("\nJO-FLOOR  scoring attempts / 75 poss (anti-vanishing)")
    d_fl = line("sa75 % change", m.sa75_pctchg, fmt="{:+.1f}")
    print("  seeds sa75_pctchg:", seedvals(m, "sa75_pctchg", "{:+.1f}"))
    broke15 = int((m.sa75_pctchg <= -15).sum())
    broke20 = int((m.sa75_pctchg <= -20).sum())
    print(f"  members with volume drop > 15%: {broke15}/{n};  > 20%: {broke20}/{n}")
    print(f"\n  PROPOSED JO-FLOOR: caps offense at NOT-LEAP if sa75 falls > 15% vs trailing baseline")
    print(f"    (spec draft = -15%; class median move {d_fl['median']:+.1f}%, q25 {d_fl['q25']:+.1f}%; "
          f"a -15% floor trips {broke15}/{n})")
    prop["markers"]["JO-FLOOR"] = {"dist_sa75_pctchg": d_fl,
                                   "proposed_floor_pct": -15.0,
                                   "n_break_15": broke15, "n_break_20": broke20}

    print("\nJO-GROWTH  three rungs (LEAP needs >= 1)")
    d_pu = line("pull_up_efg delta", m.pull_up_efg_delta)
    d_dr = line("drive_fg_pct delta", m.drive_fg_pct_delta)
    d_sc = line("selfcreate_ppfga delta", m.selfcreate_ppfga_delta)
    d_ftr = line("FT rate delta", m.ftr_delta)
    d_3a = line("fg3a/g delta", m.fg3a_pg_delta, fmt="{:+.2f}")
    d_3p = line("fg3_pct delta", m.fg3_pct_delta)
    # rung satisfaction with a real-margin definition (TUNE)
    SC_MARGIN = 0.010   # self-created efficiency "real" rise
    FTR_MARGIN = 0.010
    rung_a = ((m.pull_up_efg_delta >= SC_MARGIN) | (m.drive_fg_pct_delta >= SC_MARGIN))
    rung_b = (m.ftr_delta >= FTR_MARGIN)
    rung_c = ((m.fg3a_pg_delta > 0) & (m.fg3_pct_delta > 0))
    any_rung = rung_a | rung_b | rung_c
    print(f"\n  rung (a) self-created eff rising (pull-up eFG OR drive FG% up >= {SC_MARGIN:+.3f}): "
          f"{int(rung_a.sum())}/{n}")
    print(f"  rung (b) FT rate rising (>= {FTR_MARGIN:+.3f}): {int(rung_b.sum())}/{n}")
    print(f"  rung (c) 3P vol AND acc both rising: {int(rung_c.sum())}/{n}")
    print(f"  AT LEAST ONE rung: {int(any_rung.sum())}/{n}")
    for pid, nm in SEEDS.items():
        i = m.player_id == pid
        if i.any():
            print(f"    {nm}: a={bool(rung_a[i].iloc[0])} b={bool(rung_b[i].iloc[0])} c={bool(rung_c[i].iloc[0])}")
    prop["markers"]["JO-GROWTH"] = {
        "dist_pull_up_efg_delta": d_pu, "dist_drive_fg_pct_delta": d_dr,
        "dist_selfcreate_ppfga_delta": d_sc, "dist_ftr_delta": d_ftr,
        "dist_fg3a_pg_delta": d_3a, "dist_fg3_pct_delta": d_3p,
        "proposed": {"selfcreate_margin": SC_MARGIN, "ftr_margin": FTR_MARGIN,
                     "n_rung_a": int(rung_a.sum()), "n_rung_b": int(rung_b.sum()),
                     "n_rung_c": int(rung_c.sum()), "n_any": int(any_rung.sum())}}

    # ================= DEFENSIVE GATE =================
    print("\n" + "=" * 110)
    print("DEFENSIVE GATE")
    print("=" * 110)

    print("\nJD-LOAD  share of defensive possessions vs primary perimeter creators")
    d_lb = line("jd_load BEFORE", m.jd_load_before, fmt="{:.3f}")
    d_la = line("jd_load AFTER", m.jd_load_after, fmt="{:.3f}")
    d_ld = line("jd_load delta", m.jd_load_delta)
    print("  seeds jd_load_after:", seedvals(m, "jd_load_after", "{:.3f}"))
    pass_load = round(d_la["median"], 3)
    print(f"\n  PROPOSED JD-LOAD pass (deployment): after-share >= class median {pass_load:.3f} "
          f"(TUNE; the board's real test is 'leads the roster', a team-relative rank the panel can add)")
    prop["markers"]["JD-LOAD"] = {"dist_before": d_lb, "dist_after": d_la,
                                  "proposed_pass_share_ge": pass_load}

    print("\nJD-HOLD  pts allowed per poss vs opponent baseline (negative = suppression)")
    d_hb = line("jd_hold BEFORE", m.jd_hold_before)
    d_ha = line("jd_hold AFTER", m.jd_hold_after)
    d_hd = line("jd_hold delta", m.jd_hold_delta)
    print("  seeds jd_hold_after:", seedvals(m, "jd_hold_after"))
    n_supp = int((m.jd_hold_after < 0).sum())
    pass_hold = round(d_ha["median"], 3)
    print(f"  members holding opponents below baseline AFTER (jd_hold<0): {n_supp}/{n}")
    print(f"\n  PROPOSED JD-HOLD pass: jd_hold_after < 0 (below-baseline); class median {pass_hold:+.3f}, "
          f"q75 {d_ha['q75']:+.3f}. Strong pass <= {round(d_ha['q25'],3):+.3f} (~class 25th pct).")
    prop["markers"]["JD-HOLD"] = {"dist_before": d_hb, "dist_after": d_ha,
                                  "n_suppress_after": n_supp,
                                  "proposed_pass_lt": 0.0,
                                  "proposed_strong_le": round(d_ha["q25"], 3)}

    print("\nJD-COVER  team DRTG in creator minutes, wing on-off (negative = wing helps)")
    v = cov[cov.jd_cover_onoff.notna()]
    d_cov = line("jd_cover on-off", v.jd_cover_onoff, fmt="{:+.2f}")
    print("  seeds jd_cover_onoff:", seedvals(cov, "jd_cover_onoff", "{:+.2f}"))
    n_better3 = int((v.jd_cover_onoff <= -3.0).sum())
    n_better = int((v.jd_cover_onoff < 0).sum())
    print(f"  members better with wing on by >= 3.0/100 (on-off <= -3.0): {n_better3}/{len(v)}")
    print(f"  members any-better (on-off < 0): {n_better}/{len(v)}")
    print(f"\n  PROPOSED JD-COVER pass: on-off <= -3.0/100 (spec draft). CLASS SAYS this is DEMANDING:")
    print(f"    only {n_better3}/{len(v)} historical wings cleared it; distribution centers near "
          f"{d_cov['median']:+.2f} (on-off is confounded by who replaces the wing). Possession floor TUNE.")
    prop["markers"]["JD-COVER"] = {"dist_onoff": d_cov, "n_le_-3": n_better3,
                                   "n_lt_0": n_better, "computed_n": int(len(v)),
                                   "proposed_pass_le": -3.0}

    # gate composite reminder
    print("\nGATE (spec): fails only if JD-LOAD fails AND (JD-COVER fails OR JD-HOLD fails).")
    print("If deployment drops but effectiveness holds -> STEADY + REALLOCATED flag, not a fail.")

    with open(OUTDIR / "threshold_proposals.json", "w", encoding="utf-8") as f:
        json.dump(prop, f, indent=2, default=float)
    print(f"\nwrote {OUTDIR/'threshold_proposals.json'}")


if __name__ == "__main__":
    main()
