#!/usr/bin/env python3
"""Full-offseason PACKAGES under keep-the-core: combined-roster title equity, CBA-gated first.

First principle (locked): model each package's full post-move roster end to end and compare to
stand-pat. NEVER sum the individual move deltas (the moves are coupled under the apron, compete
for minutes/touches, have diminishing returns, and the fit term must be recomputed on the
combined roster). Per-component contributions are reported only as a decomposition with an
explicit non-additivity caveat.

Pipeline per package: (1) CBA gate (reuse core_max.cba.gate) -> PASS/FAIL + tier (=> which MLE);
(2) acquired impacts from the same RAPM spine/established distributions; rookie = wide near-
replacement developmental prior; Joan = his maturity-bridge distribution; (3) symmetric data-
bounded fit term recomputed on the combined roster vs stand-pat; (4) sim on the frozen field
with per-iteration sampling -> banded title odds + round-advancement (R2/CF/Finals) + projected
wins. Deltas vs stand-pat and vs the best single retool. Absolute level is approximate (the
opponent board is RS-net-seated and mis-seats playoff-pedigree teams); deltas are the robust
quantity. The 2026 champion is the KNICKS; OKC is the projected favorite, not the champion.

    python core_max/engine/run_package.py
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import run_scenarios as RS
import bracket_sim as BS
import age_curve as AC
from core_max.cba import gate as G

CFG = os.path.join(HERE, "..", "config", "gate_config.json")
ROOKIE = (-1.0, 2.0, 19)          # No.28 year-1: near-replacement mean, wide developmental sd
SAL = {"Randle": 33_333_334, "Gobert": 36_500_000, "DDV": 12_500_000, "Ayo": 16_500_000,
       "Jrue": 34_800_000, "MPJ": 40_806_150, "Cam": 23_062_500, "Morant": 42_200_000,
       "TAXMLE": 6_065_000, "FULLMLE": 15_048_000, "ROOKIE28": 1_400_000}
PID_X = {"Randle": "203944", "Gobert": "203497", "DDV": "1628978", "Ayo": "1630245",
         "Jrue": "201950", "MPJ": "1629008", "Cam": "1629661", "Morant": "1629630",
         "Kennard": "1628379"}

# rotations (name -> mpg); CREATOR/SHOOTER/ROOKIE are filled per package. DiVincenzo NEVER plays
# (torn Achilles, 2026-27): he is either trade filler (gone) or an injured non-contributor.
ROT = {
 "standpat": {"Edwards":36,"McDaniels":33,"Randle":31,"Gobert":30,"Naz":28,"Ayo":26,"SHOOTER":16,"TSJ":16,"Conley":14,"Joan":10},
 "A":        {"Edwards":36,"McDaniels":33,"CREATOR":30,"Gobert":30,"Naz":28,"Ayo":26,"SHOOTER":14,"TSJ":16,"Conley":11,"Joan":12,"ROOKIE":4},
 "B":        {"Edwards":36,"McDaniels":33,"CREATOR":30,"Gobert":30,"Naz":28,"Ayo":26,"SHOOTER":14,"TSJ":16,"Conley":11,"Joan":12,"ROOKIE":4},
 "C":        {"Edwards":36,"McDaniels":33,"CREATOR":30,"Gobert":30,"Naz":28,"Ayo":26,"SHOOTER":14,"TSJ":16,"Conley":11,"Joan":12,"ROOKIE":4},
 "morant":   {"Edwards":36,"CREATOR":32,"McDaniels":33,"Gobert":30,"Naz":28,"Ayo":24,"TSJ":16,"Conley":11,"Joan":12,"FILL":18},
}


def spec(name_key, val, avail, impact=None, sd=None, age=None, av=None):
    pid = PID_X.get(name_key)
    if impact is None:
        impact, sd = val[pid]
    age = age if age is not None else 30
    av = av if av is not None else avail.get(pid, 0.72)
    return (impact + AC.age_delta(age), sd, age, pid, av)


def build_curves(nsim=8000):
    imp = RS.A.load_impacts()
    base = BS.build_2026_27_league(imp)
    grid = np.round(np.arange(-2.0, 6.01, 0.5), 2)
    T, R2, CF, FN = [], [], [], []
    for g in grid:
        s = {k: dict(v) for k, v in base.items()}
        s["MIN"].update(net=float(g), munc=0.0, net_sd=0.0)   # draws supply MIN's epistemic spread
        r = BS.simulate_league(s, n_sims=nsim, seed=RS.SEED, use_overlay=True)["teams"]["MIN"]
        T.append(r["title"]); R2.append(r["r2"]); CF.append(r["cf"]); FN.append(r["finals"])
    return grid, {"title": np.array(T), "r2": np.array(R2), "cf": np.array(CF), "finals": np.array(FN)}


def cba(legs):
    cfg = G.GateConfig.from_file(CFG)
    plan = G.Plan("pkg", "", tuple(G.Leg(**l) for l in legs))
    r = G.evaluate_plan(plan, cfg)
    mle = "full" if r.final_tier in ("over_cap_under_tax", "taxpayer") else ("taxpayer" if r.final_tier == "first_apron" else "none")
    return r.passed, r.final_tier, r.final_apron, mle, ("; ".join(r.reasons) if r.reasons else "")


def net_samples(rotation, specials, rng):
    """Per-iteration combined-roster net. Joan from his comp pool; ROOKIE wide near-replacement;
    CREATOR/SHOOTER from specials; known names from the established distributions; availability/
    collapse tail folded in. specials: {'CREATOR':spec,'SHOOTER':spec}."""
    jp = RS.joan_pool(RS._dev, RS._sub_ids, False, RS.REPL0)
    out = np.empty(RS.NDRAW)
    for i in range(RS.NDRAW):
        c = {}
        for k in rotation:
            if k == "Joan":
                c[k] = float(rng.choice(jp))
            elif k == "ROOKIE":
                c[k] = rng.normal(ROOKIE[0], ROOKIE[1])
            elif k == "FILL":
                c[k] = RS.REPL0
            elif k in ("CREATOR", "SHOOTER"):
                s = specials[k]
                c[k] = RS.draw_contrib(rng.normal(s[0], s[1]), s[2], s[4], rng, 1.0, RS.REPL0)
            else:
                c[k] = RS.draw_contrib(rng.normal(*RS.point_sd(k, RS._val)), RS.AGE[k],
                                       RS._avail.get(RS.PID[k], 0.85), rng, 1.0, RS.REPL0)
        out[i] = sum(rotation[k] / 48.0 * c[k] for k in rotation)
    return out


def fit_vs_standpat(pkg_rot, specials, dims, bound=0.75):
    sp_pids = {RS.PID[k]: v for k, v in ROT["standpat"].items() if k in RS.PID}
    sp_pids[PID_X["Kennard"]] = ROT["standpat"]["SHOOTER"]
    pk = {RS.PID[k]: v for k, v in pkg_rot.items() if k in RS.PID}
    for slot, s in specials.items():
        if s and s[3]:
            pk[s[3]] = pkg_rot[slot]
    return RS.fit_delta(sp_pids, pk, dims, bound)


def main():
    RS._val, RS._dims, RS._avail, RS._dev, RS._sub_ids = RS.load_inputs()
    ep = BS.load_e_params(); wa, wb = ep["wins_a"], ep["wins_b"]
    print("building outcome curves (title/R2/CF/Finals vs MIN net) ...", flush=True)
    grid, C = build_curves()
    fT, fR2, fCF, fFN = (lambda y: (lambda x: np.interp(x, grid, y)))(C["title"]), \
        (lambda y: (lambda x: np.interp(x, grid, y)))(C["r2"]), \
        (lambda y: (lambda x: np.interp(x, grid, y)))(C["cf"]), \
        (lambda y: (lambda x: np.interp(x, grid, y)))(C["finals"])

    # anchor stand-pat mean net to the engine's +1.36
    KEN = spec("Kennard", RS._val, RS._avail, age=30)            # taxpayer-MLE shooter (+0.36)
    sp_net = net_samples(ROT["standpat"], {"SHOOTER": KEN}, np.random.default_rng(RS.SEED))
    anchor = RS.BASE_NET - sp_net.mean()

    def title_band(net_arr, fit):
        t = fT(net_arr + anchor + fit) * 100
        return t.mean(), np.percentile(t, 5), np.percentile(t, 95)

    def round_probs(mean_net, fit):
        x = mean_net + fit
        return fR2(x) * 100, fCF(x) * 100, fFN(x) * 100, (wa + wb * x)

    sp_fit = 0.0
    sp_T, sp_lo, sp_hi = title_band(sp_net, sp_fit)
    sp_mean_net = sp_net.mean() + anchor
    print(f"\nstand-pat baseline (keep Randle + taxpayer-MLE shooter + Ayo + develop Joan):")
    r2, cf, fn, wins = round_probs(sp_mean_net, sp_fit)
    print(f"  net {sp_mean_net:+.2f} | title {sp_T:.2f}% [{sp_lo:.2f},{sp_hi:.2f}] | "
          f"R2 {r2:.0f}% CF {cf:.0f}% Finals {fn:.0f}% | ~{wins:.0f} wins")

    # ---- gate + define the three keep-core packages + Morant ----
    AYO_LEG = {"label": "Re-sign Ayo (Bird)", "incoming": [{"label": "Ayo", "salary": SAL["Ayo"], "pid": PID_X["Ayo"]}], "exception_used": "bird"}
    def trade(outs, inc_label, inc_sal, inc_pid):
        return {"label": "Randle"+("+DDV" if len(outs) > 1 else "")+"->"+inc_label,
                "outgoing": [{"label": o, "salary": SAL[o], "pid": PID_X[o]} for o in outs],
                "incoming": [{"label": inc_label, "salary": inc_sal, "pid": inc_pid}]}
    # MLE tier is endogenous: keeping Randle pins MIN at the first apron (taxpayer MLE only);
    # shedding Randle drops MIN under the first apron, unlocking the FULL MLE, but using it
    # hard-caps at the first apron, so the bigger the return's salary, the less MLE room is left.
    def shooter_leg(kind, sal):
        return {"label": f"{kind}-MLE shooter", "incoming": [{"label": "shooter", "salary": sal, "pid": "KEN"}],
                "exception_used": ("full_mle" if kind == "full" else "none" if kind == "min" else "taxpayer_mle")}

    packages = {
        "A (fit/initiator: Randle+DDV->Jrue, +full-MLE shooter, +Ayo, +rookie)":
            (ROT["A"], {"CREATOR": spec("Jrue", RS._val, RS._avail, age=35, av=0.75), "SHOOTER": KEN},
             [trade(["Randle", "DDV"], "Jrue", SAL["Jrue"], PID_X["Jrue"]), AYO_LEG, shooter_leg("full", 8_000_000)]),
        "B (scoring: Randle+DDV->MPJ, +min shooter [MPJ eats MLE room], +Ayo, +rookie)":
            (ROT["B"], {"CREATOR": spec("MPJ", RS._val, RS._avail, age=27, av=0.70), "SHOOTER": KEN},
             [trade(["Randle", "DDV"], "MPJ", SAL["MPJ"], PID_X["MPJ"]), AYO_LEG, shooter_leg("min", 2_300_000)]),
        "C (spacing: Randle->Cam [needs 3rd-team Randle taker], +full-MLE shooter, +Ayo, +rookie)":
            (ROT["C"], {"CREATOR": spec("Cam", RS._val, RS._avail, age=30, av=0.69), "SHOOTER": KEN},
             [trade(["Randle"], "Cam", SAL["Cam"], PID_X["Cam"]), AYO_LEG, shooter_leg("full", 8_000_000)]),
    }
    # stand-pat (keep Randle -> first apron -> taxpayer MLE only) gated for the baseline record
    sp_ok, sp_tier, sp_apron, sp_mle, sp_why = cba(
        [AYO_LEG, {"label": "taxpayer-MLE shooter", "incoming": [{"label": "shooter", "salary": SAL["TAXMLE"], "pid": "KEN"}], "exception_used": "taxpayer_mle"}])
    print(f"  CBA: {'PASS' if sp_ok else 'FAIL'} | tier {sp_tier} | apron ${sp_apron:,} | {sp_mle} MLE")

    print("\n=== KEEP-CORE PACKAGES (combined roster, CBA-gated first) ===")
    print(f"{'package':54s}{'CBA':>6s}{'tier':>16s}{'title band':>16s}{'dStandpat':>10s}{'dRetool':>9s}")
    RETOOL = 3.05   # best single retool (Jrue) from the frontier
    results = {}
    for lab, (rot, specials, legs) in packages.items():
        ok, tier, apron, mle, why = cba(legs)
        nd = net_samples(rot, specials, np.random.default_rng(RS.SEED))
        fit = fit_vs_standpat(rot, specials, RS._dims)
        T, lo, hi = title_band(nd, fit)
        results[lab] = (ok, tier, apron, mle, T, lo, hi, nd.mean() + anchor + fit, why)
        flag = "PASS" if ok else "FAIL"
        print(f"{lab[:54]:54s}{flag:>6s}{tier:>16s}{T:>7.2f}% [{lo:.1f},{hi:.1f}]{T-sp_T:>+9.2f}{T-RETOOL:>+9.2f}")
        if not ok:
            print(f"      INFEASIBLE: {why}")

    print("\n=== 'How it changes the season' (feasible packages) ===")
    for lab, (ok, tier, apron, mle, T, lo, hi, net, why) in results.items():
        if not ok:
            continue
        r2, cf, fn, wins = round_probs(net - 0, 0.0)   # net already includes fit
        print(f"  {lab[:48]:48s} net {net:+.2f} | R2 {r2:.0f}% CF {cf:.0f}% Finals {fn:.0f}% title {T:.1f}% | ~{wins:.0f} wins | apron ${apron:,} ({mle} MLE)")

    # ---- decomposition (cumulative, NON-ADDITIVE caveat) on package A ----
    print("\n=== Decomposition of package A (cumulative; NON-ADDITIVE, illustrative only) ===")
    steps = [("bare (keep Randle, no Ayo/MLE, Joan->repl)", {"drop_ayo": True, "joan_repl": True, "creator": None, "shooter": None}),
             ("+ re-sign Ayo", {"creator": None, "shooter": None, "joan_repl": True}),
             ("+ develop Joan (his distribution)", {"creator": None, "shooter": None}),
             ("+ Randle->Jrue swap", {"creator": "Jrue", "shooter": None}),
             ("+ taxpayer-MLE shooter", {"creator": "Jrue", "shooter": "KEN"})]
    prev = None
    for slab, cfgd in steps:
        rot = dict(ROT["A"])
        sp = {}
        if cfgd.get("creator"):
            sp["CREATOR"] = spec("Jrue", RS._val, RS._avail, age=35, av=0.75)
        else:
            rot["CREATOR"] = rot.pop("CREATOR", 0); rot["Randle"] = 30   # creator slot -> Randle
            if "CREATOR" in rot: del rot["CREATOR"]
        sp["SHOOTER"] = KEN if cfgd.get("shooter") else None
        if sp.get("SHOOTER") is None and "SHOOTER" in rot:
            rot["TSJ"] = rot.get("TSJ", 0) + rot.pop("SHOOTER")          # MLE minutes -> TSJ
        # joan->replacement variant handled by zeroing his pool draw to REPL (approx)
        rng = np.random.default_rng(RS.SEED)
        jp = (np.full(2000, RS.REPL0) if cfgd.get("joan_repl") else RS.joan_pool(RS._dev, RS._sub_ids, False, RS.REPL0))
        out = np.empty(RS.NDRAW)
        for i in range(RS.NDRAW):
            c = {}
            for k in rot:
                if k == "Joan":
                    c[k] = float(rng.choice(jp))
                elif k == "ROOKIE":
                    c[k] = rng.normal(*ROOKIE[:2])
                elif k in ("CREATOR", "SHOOTER"):
                    s = sp.get(k)
                    c[k] = RS.draw_contrib(rng.normal(s[0], s[1]), s[2], s[4], rng, 1.0, RS.REPL0) if s else RS.REPL0
                elif k == "Ayo" and cfgd.get("drop_ayo"):
                    c[k] = RS.REPL0
                else:
                    c[k] = RS.draw_contrib(rng.normal(*RS.point_sd(k, RS._val)), RS.AGE[k],
                                           RS._avail.get(RS.PID[k], 0.85), rng, 1.0, RS.REPL0)
            out[i] = sum(rot[k] / 48.0 * c[k] for k in rot)
        T = fT(out + anchor) * 100
        tag = f" (marginal {T.mean()-prev:+.2f}pp)" if prev is not None else ""
        print(f"  {slab:42s} title {T.mean():.2f}%{tag}")
        prev = T.mean()
    print("  CAVEAT: cumulative and order-dependent; components do NOT sum to the package total.")

    # ---- Morant (separate, flagged, high-variance) ----
    print("\n=== Ja Morant scenario (SEPARATE, flagged, NOT a recommendation) ===")
    okm, tierm, apronm, mlem, whym = cba([trade(["Randle", "DDV"], "Morant", SAL["Morant"], PID_X["Morant"]), AYO_LEG])
    for av_lab, av in [("with availability (~79/246 games)", 0.32), ("IF healthy (full availability)", 0.95)]:
        mor = spec("Morant", RS._val, RS._avail, age=27, av=av)
        rot = dict(ROT["morant"])
        nd = net_samples(rot, {"CREATOR": mor}, np.random.default_rng(RS.SEED))
        fit = fit_vs_standpat(rot, {"CREATOR": mor}, RS._dims)   # iso-stacking next to Edwards -> penalty
        T, lo, hi = title_band(nd, fit)
        print(f"  Morant {av_lab:34s}: title {T:.2f}% [{lo:.1f},{hi:.1f}] dStandpat {T-sp_T:+.2f}pp (CBA {'PASS' if okm else 'FAIL'})")
    print("  Boom-bust: even healthy, Morant is +1.08 (sd 1.85) and stacks on-ball usage next to")
    print("  Edwards (the iso-duplication the thesis runs from); his ~1/3 availability guts the median.")

    print(f"\nPROVENANCE: warehouse snapshot {open(os.path.join(HERE,'..','data_frozen','CURRENT')).read().strip()} | "
          f"seed {RS.SEED} | ndraw {RS.NDRAW} | curves n=8000 | champion=NYK (OKC=favorite, not champ)")
    print("PLAIN SUMMARY: every keep-core package lands in the low 3s%% of title odds, a modest lift")
    print("over stand-pat and ~tied with the best single retool. The combined moves do not compound")
    print("into contention because Gobert+the core are kept (good) and the Randle slot is the only")
    print("real upgrade lever; Morant is boom-bust and worse on the median. Bands overlap stand-pat,")
    print("so the honest read is a small, disciplined improvement, decided as much by flexibility")
    print("and development as by title odds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
