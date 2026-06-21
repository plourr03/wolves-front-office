#!/usr/bin/env python3
"""Phase 2 (FROZEN v1.3): maturity-bridge outcomes -> Joan's per-year impact distribution.

Membership decided the class (build_comp_class.py); impact is taken ONLY from career years
that cleared the Phase-1 reliability bar (map applied on reliable samples only); washout
years are floored to a TRUE replacement set from the washout COMPOSITION. Each measured
impact carries the map's residual uncertainty. Reported for the FULL N=28 class and the
binding Joan-like sub-class (rookie minutes <= 600), with per-year MEASURED counts, the
replacement bracket as a sensitivity, and the out-year real-option treated with wide
humility. Joan's rookie RAPM is near-uninformative for his future (unvalidatable
development gap) and touches nothing in the out-year. See core_max/docs/phase2_plan.md.

    python core_max/impact/build_dev_distribution.py
"""
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SMB = os.path.join(REPO, "offseason", "data", "cache", "season_min_blk_2001_2026.csv")
PV = os.path.join(REPO, "offseason", "data", "player_value.csv")
COMP = os.path.join(REPO, "core_max", "outputs", "phase2", "comp_class.csv")
OUTDIR = os.path.join(REPO, "core_max", "outputs", "phase2")

SEED = 20260620
BOX = ["PTS", "REB", "AST", "BLK", "STL"]
JOAN = {"net_rapm": 2.82, "net_sd": 2.43}
SUBCLASS_MIN = 600
RELIAB_POSS = 3000
NDRAW = 400
YEARS = [2, 3, 4, 5, 6]
V_UNDER, V_OUT = -0.97, -2.83        # bracket anchors: marginal-but-present vs out-of-league
GAP_SD_GRID = [2.0, 3.5, 5.0]        # unvalidatable rookie->future development gap (baseline = widest)


def reliable_mask(s):
    return s.astype(str).str.upper().isin(["TRUE", "1"])


def main():
    rng = np.random.default_rng(SEED)
    smb = pd.read_csv(SMB)
    smb["yr"] = smb["season"].str[:4].astype(int)
    for c in BOX:
        smb[c + "36"] = smb[c] / smb["MIN"].clip(lower=1) * 36.0
    pv = pd.read_csv(PV)
    comp = pd.read_csv(COMP)

    cur_min = smb[smb["yr"].isin([2023, 2024, 2025])].groupby("PLAYER_ID")["MIN"].sum().rename("min3")
    rel = pv.merge(cur_min, left_on="player_id", right_index=True)
    rel = rel[reliable_mask(rel["reliable"])]
    ratio = float((rel["possessions"] / rel["min3"]).median())
    floor_min = RELIAB_POSS / ratio
    print(f"measured floor = {floor_min:.0f} min/season (= 3000 poss, Phase-1 bar; ratio {ratio:.2f})")

    # era per-season per-36 mean/std for z-scoring; basic-box -> impact map
    elig = smb[smb["MIN"] >= floor_min]
    era_mu = elig.groupby("yr")[[c + "36" for c in BOX]].mean()
    era_sd = elig.groupby("yr")[[c + "36" for c in BOX]].std()

    def zbox(row):
        y = int(row["yr"])
        if y not in era_mu.index:
            return None
        return np.array([((row[c + "36"] - era_mu.loc[y, c + "36"]) / era_sd.loc[y, c + "36"])
                         if era_sd.loc[y, c + "36"] > 0 else 0.0 for c in BOX])

    fit = smb[(smb["yr"] == 2025) & (smb["MIN"] >= floor_min)].merge(
        pv[["player_id", "consensus_net", "reliable"]], left_on="PLAYER_ID", right_on="player_id")
    fit = fit[reliable_mask(fit["reliable"])]
    Z = np.array([zbox(r) for _, r in fit.iterrows()])
    yv = fit["consensus_net"].to_numpy()
    A = np.column_stack([np.ones(len(Z)), Z])
    coef, *_ = np.linalg.lstsq(A, yv, rcond=None)
    map_sd = float(np.sqrt(((yv - A @ coef) ** 2).sum() / (len(yv) - A.shape[1])))
    print(f"basic-box->impact map: residual sd {map_sd:.2f} (within-comp uncertainty), n={len(Z)}")

    # per-comp per-career-year: measured impact, or washout (tagged out-of-league vs under-floor)
    rookie_yr = dict(zip(comp["PLAYER_ID"], comp["season"].str[:4].astype(int)))
    bycp = {pid: g for pid, g in smb[smb["PLAYER_ID"].isin(comp["PLAYER_ID"])].groupby("PLAYER_ID")}
    base = []   # (pid, cy, measured_impact_or_None, kind)  kind in {measured, under_floor, out_of_league}
    for pid in comp["PLAYER_ID"]:
        g = bycp.get(pid)
        for cy in YEARS:
            syr = rookie_yr[pid] + (cy - 1)
            srow = g[g["yr"] == syr] if g is not None else None
            if srow is not None and len(srow):
                if float(srow.iloc[0]["MIN"]) >= floor_min:
                    base.append((pid, cy, float(coef[0] + zbox(srow.iloc[0]) @ coef[1:]), "measured"))
                else:
                    base.append((pid, cy, None, "under_floor"))
            else:
                base.append((pid, cy, None, "out_of_league"))
    bdf = pd.DataFrame(base, columns=["pid", "cy", "imp", "kind"])

    # washout composition -> replacement center (whole bucket floored to one value)
    wash = bdf[bdf["kind"] != "measured"]
    frac_out = float((wash["kind"] == "out_of_league").mean())
    repl_center = frac_out * V_OUT + (1 - frac_out) * V_UNDER
    print(f"\nwashout composition: out-of-league {100*frac_out:.0f}%, under-floor {100*(1-frac_out):.0f}% "
          f"-> replacement center {repl_center:+.2f}  (bracket {V_UNDER:+.2f} .. {V_OUT:+.2f})")

    sub_ids = set(comp[comp["MIN"] <= SUBCLASS_MIN]["PLAYER_ID"])

    def per_year(replacement, ids=None):
        d = bdf if ids is None else bdf[bdf["pid"].isin(ids)]
        res = {}
        for cy in YEARS:
            dy = d[d["cy"] == cy]
            draws, meas = [], 0
            for _, r in dy.iterrows():
                if r["kind"] == "measured":
                    draws.append(rng.normal(r["imp"], map_sd, NDRAW)); meas += 1
                else:
                    draws.append(rng.normal(replacement, 0.5, NDRAW))
            draws = np.concatenate(draws)
            res[cy] = {"measured": meas, "n": len(dy), "p": np.percentile(draws, [10, 25, 50, 75, 90]),
                       "mean": float(draws.mean()), "draws": draws}
        return res

    def show(res, label):
        print(f"\n--- {label} ---")
        print(f"{'cy':>3} {'measured':>10} {'wash%':>6} {'p10':>6} {'p25':>6} {'med':>6} {'p75':>6} {'p90':>6}")
        for cy in YEARS:
            r = res[cy]
            print(f"{cy:>3} {r['measured']:>5}/{r['n']:<4} {100*(1-r['measured']/r['n']):>5.0f}% "
                  + " ".join(f"{v:>+6.1f}" for v in r["p"]))

    full = per_year(repl_center)
    sub = per_year(repl_center, sub_ids)
    show(full, "FULL CLASS (N=28), replacement at center")
    show(sub, f"JOAN-LIKE SUB-CLASS (N={len(sub_ids)}), replacement at center")

    # replacement bracket sensitivity (sub-class median/p25, the bust-tail-sensitive cells)
    print("\nreplacement-bracket sensitivity (sub-class cy2 median | cy2 p25):")
    for rv, lab in [(V_UNDER, "generous -0.97"), (repl_center, f"center {repl_center:+.2f}"), (V_OUT, "harsh -2.83")]:
        s = per_year(rv, sub_ids)[2]["p"]
        print(f"  replacement {lab:16s}: median {s[2]:+.2f} | p25 {s[1]:+.2f}")

    # Joan: rookie RAPM is near-uninformative for the future (unvalidatable development gap)
    print("\n=== JOAN ===")
    print("rookie-RAPM nudge to Year-1 prior across development-gap assumptions (baseline = widest gap):")
    mu_p = float(full[2]["draws"].mean()); sd_p = float(full[2]["draws"].std())
    for gsd in GAP_SD_GRID:
        sx = (JOAN["net_sd"] ** 2 + gsd ** 2) ** 0.5
        post = (mu_p / sd_p ** 2 + JOAN["net_rapm"] / sx ** 2) / (1 / sd_p ** 2 + 1 / sx ** 2)
        tag = " <- baseline (gap unvalidatable -> widest)" if gsd == GAP_SD_GRID[-1] else ""
        print(f"  gap_sd {gsd:>3}: effective sd {sx:.1f}, nudge {post-mu_p:+.2f}{tag}")
    gsd = GAP_SD_GRID[-1]
    print("\nJoan's per-year impact (prior = comp class; rookie nudge near-zero; OUT-YEAR gets NO nudge):")
    for cy, lab in [(2, "Year 1 (2026-27)"), (3, "Year 2 (2027-28)")]:
        for cls, clab in [(full, "full"), (sub, "sub ")]:
            mp = float(cls[cy]["draws"].mean()); sp = float(cls[cy]["draws"].std())
            sx = (JOAN["net_sd"] ** 2 + gsd ** 2) ** 0.5
            post = (mp / sp ** 2 + JOAN["net_rapm"] / sx ** 2) / (1 / sp ** 2 + 1 / sx ** 2)
            wr = 100 * (1 - cls[cy]["measured"] / cls[cy]["n"])
            print(f"  {lab} [{clab}]: median {cls[cy]['p'][2]:+.2f}, p90 {cls[cy]['p'][4]:+.2f}, "
                  f"washout {wr:.0f}% | with rookie nudge {post:+.2f} (shift {post-mp:+.2f})")
    print("\n  OUT-YEAR REAL-OPTION (career yrs 4-6; NO rookie nudge; thin -> wide humility):")
    for cy in [4, 5, 6]:
        f, s = full[cy], sub[cy]
        print(f"   cy{cy}: full med {f['p'][2]:+.1f} p90 {f['p'][4]:+.1f} (measured {f['measured']}/{f['n']}) | "
              f"sub med {s['p'][2]:+.1f} p90 {s['p'][4]:+.1f} (measured {s['measured']}/{s['n']})")

    bdf.to_csv(os.path.join(OUTDIR, "dev_distribution_percomp.csv"), index=False)
    print(f"\nwrote {os.path.join(OUTDIR, 'dev_distribution_percomp.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
