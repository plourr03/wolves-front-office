#!/usr/bin/env python3
"""Phase 3 verdict: status-quo vs Fork B title-equity, across the full sweep grid.

Per-iteration sampling (locked): Joan from his Phase-2 comp DISTRIBUTION (not his naive +2.29),
established players from Phase-1a Normal(point_y1, sd as-is), returns from their impact +/- real
availability/collapse tail. Common random numbers across scenarios for SHARED players, so the
Fork-B-minus-status-quo DELTA is low-noise and driven only by the pieces that differ. Symmetric,
data-bounded, swept FIT term applied to BOTH rosters by composition (auto-penalizes MPJ's usage
stacking). Veteran-collapse left-tail (aging vets) symmetric with Joan's bust tail. Returns land
BELOW what we send (opens room; gate-clean). MIN net anchored to the engine's +1.36.

Primary verdict = the DELTA vs the noise floor; if its CI spans 0, the honest verdict is
"title-odds math cannot separate these; decide on flexibility, timeline, development."

    python core_max/engine/run_scenarios.py
"""
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
sys.path.insert(0, os.path.join(REPO, "core_max"))
import bracket_sim as BS
import build_team_ratings as A
import build_rotation_model as RM
import age_curve as AC

PV = os.path.join(REPO, "offseason", "data", "player_value.csv")
DEV = os.path.join(REPO, "core_max", "outputs", "phase2", "dev_distribution_percomp.csv")
COMP = os.path.join(REPO, "core_max", "outputs", "phase2", "comp_class.csv")
OUTDIR = os.path.join(REPO, "core_max", "outputs", "phase3")
SEED, NDRAW, NSIM = 20260621, 4000, 8000
BASE_NET = 1.36
REPL0 = -1.70
MAP_SD = 1.70

PID = {"Edwards": "1630162", "McDaniels": "1630183", "Naz": "1629675", "Gobert": "203497",
       "Randle": "203944", "Conley": "201144", "Ayo": "1630245", "TSJ": "1630545", "Joan": "1642866",
       "MPJ": "1629008", "Jrue": "201950", "Cam": "1629661", "ONeale": "1626220", "DFS": "1627827"}
AGE = {"Edwards": 25, "McDaniels": 26, "Naz": 27, "Gobert": 34, "Randle": 32, "Conley": 39,
       "Ayo": 27, "TSJ": 25, "Joan": 20, "MPJ": 27, "Jrue": 36, "Cam": 30, "ONeale": 33, "DFS": 33}
ROT_SQ = {"Edwards": 36, "McDaniels": 33, "Randle": 31, "Gobert": 30, "Naz": 28,
          "Ayo": 28, "Conley": 18, "TSJ": 18, "Joan": 10}
ROT_FB = {"Edwards": 36, "McDaniels": 33, "Naz": 30, "Joan": 26, "Ayo": 28,
          "CREATOR": 30, "WING": 24, "TSJ": 22, "Conley": 11}
SHARED = ("Edwards", "McDaniels", "Naz", "Ayo", "TSJ", "Conley")


def load_inputs():
    pv = pd.read_csv(PV); pv["player_id"] = pv["player_id"].astype(str)
    val = {r["player_id"]: (float(r["consensus_net"]), float(r["net_sd"])) for _, r in pv.iterrows()}
    dims = RM.load_dims()
    smb = pd.read_csv(os.path.join(REPO, "offseason", "data", "cache", "season_min_blk_2001_2026.csv"))
    smb["yr"] = smb["season"].str[:4].astype(int)
    g = smb[smb["yr"].isin([2023, 2024, 2025])].groupby("PLAYER_ID")["GP"].sum()
    avail = {str(k): min(1.0, v / 246.0) for k, v in g.items()}
    dev = pd.read_csv(DEV); dev = dev[dev["cy"] == 2]
    comp = pd.read_csv(COMP); sub_ids = set(comp[comp["MIN"] <= 600]["PLAYER_ID"])
    return val, dims, avail, dev, sub_ids


def joan_pool(dev, sub_ids, sub, repl):
    d = dev[dev["pid"].isin(sub_ids)] if sub else dev
    rng = np.random.default_rng(SEED)
    parts = [rng.normal(r["imp"], MAP_SD, 1500) if pd.notna(r["imp"]) else rng.normal(repl, 0.5, 1500)
             for _, r in d.iterrows()]
    return np.concatenate(parts)


def point_sd(name, val):
    base, sd = val.get(PID[name], (REPL0, 1.6))
    return base + AC.age_delta(AGE[name]), sd


def ret_spec(name, val, avail):
    pt, sd = val[PID[name]]
    return (pt + AC.age_delta(AGE[name]), sd, AGE[name], PID[name], avail.get(PID[name], 0.7))


def build_fcurve():
    imp = A.load_impacts()
    base = BS.build_2026_27_league(imp)
    grid = np.round(np.arange(-2.0, 6.01, 0.5), 2)
    P = []
    for gnet in grid:
        s = {k: dict(v) for k, v in base.items()}
        s["MIN"]["net"] = float(gnet)
        # zero MIN's EPISTEMIC strength uncertainty in the sim (munc + net_sd); our per-draw impact
        # sampling supplies it (richer, with Joan's non-normal shape). Keeps the sim's aleatoric
        # season/playoff variance (sigma_unobs). Avoids double-counting MIN's strength uncertainty.
        s["MIN"]["munc"] = 0.0
        s["MIN"]["net_sd"] = 0.0
        P.append(BS.simulate_league(s, n_sims=NSIM, seed=SEED, use_overlay=True)["teams"]["MIN"]["title"])
    return grid, np.array(P)


def _profile(rot_pid_mpg, dims):
    num = {d: 0.0 for d in RM.DIMS}; w = 0.0
    for pid, mpg in rot_pid_mpg.items():
        d = dims.get(pid)
        if not d:
            continue
        for k in RM.DIMS:
            num[k] += mpg * d[k]
        w += mpg
    return {k: (num[k] / w if w else 0.5) for k in RM.DIMS}


def fit_delta(sq_pids, fb_pids, dims, bound):
    """MARGINAL, need-based fit applied to Fork B vs status quo (symmetric in construction).
    REWARD: Fork B raising MIN's genuine GAP dims (status-quo profile below the contender
    benchmark; off-ball shooting / spacing is MIN's real LAFI deficiency). PENALIZE: Fork B
    stacking ON-BALL creation that MIN already has in surplus (this is what flags MPJ). The
    'fit over splash' thesis must EARN a positive delta; a usage-stacking return earns a
    negative one. Bounded to `bound` (the C1-anchored, additive-residual-cross-checked cap)."""
    if bound <= 0:
        return 0.0
    sq, fb = _profile(sq_pids, dims), _profile(fb_pids, dims)
    improve = sum(max(0.0, fb[d] - sq[d]) for d in RM.DIMS if sq[d] < RM.BENCHMARK[d])
    stack = 0.0
    for d in ("hc_creation", "secondary_playmaking"):
        if sq[d] >= RM.BENCHMARK[d]:                      # already a surplus on-ball skill
            stack += max(0.0, fb[d] - sq[d])
    return float(np.clip((improve - stack) / 0.5, -1.0, 1.0)) * bound


def draw_contrib(impact, age, av, rng, collapse, repl):
    asd = (0.06 + (0.10 if age >= 33 else 0.04)) * collapse
    a = float(np.clip(rng.normal(av, asd), 0.4, 1.0))
    return a * impact + (1 - a) * repl


def run_cell(val, dims, avail, dev, sub_ids, returns, joan_class="full", repl=REPL0,
             fit_bound=0.75, collapse=1.0, fcurve=None):
    grid, P = fcurve
    f = lambda x: np.interp(x, grid, P)
    rng = np.random.default_rng(SEED)
    jp = joan_pool(dev, sub_ids, joan_class == "sub", repl)
    creator, wing = returns

    # Fit as a MARGINAL FB-vs-SQ delta (need-based; penalizes MPJ stacking). SQ baseline 0.
    sq_pids = {PID[k]: v for k, v in ROT_SQ.items()}
    fb_pids = {PID[k]: v for k, v in ROT_FB.items() if k in PID}
    if creator:
        fb_pids[creator[3]] = ROT_FB["CREATOR"]
    if wing:
        fb_pids[wing[3]] = ROT_FB["WING"]
    sq_fit = 0.0
    fb_fit = fit_delta(sq_pids, fb_pids, dims, fit_bound)

    sq_net = np.empty(NDRAW); fb_net = np.empty(NDRAW)
    for i in range(NDRAW):
        shared = {nm: draw_contrib(rng.normal(*point_sd(nm, val)), AGE[nm],
                                   avail.get(PID[nm], 0.85), rng, collapse, repl) for nm in SHARED}
        jd = rng.choice(jp)
        joan_c = jd            # Joan: full availability (rookie-scale, the distribution IS his risk)
        gob = draw_contrib(rng.normal(*point_sd("Gobert", val)), AGE["Gobert"],
                           avail.get(PID["Gobert"], 0.9), rng, collapse, repl)
        ran = draw_contrib(rng.normal(*point_sd("Randle", val)), AGE["Randle"],
                           avail.get(PID["Randle"], 0.85), rng, collapse, repl)
        cre = (draw_contrib(rng.normal(creator[0], creator[1]), creator[2], creator[4], rng, collapse, repl)
               if creator else repl)
        win = (draw_contrib(rng.normal(wing[0], wing[1]), wing[2], wing[4], rng, collapse, repl)
               if wing else repl)
        c_sq = {**shared, "Randle": ran, "Gobert": gob, "Joan": joan_c}
        c_fb = {**shared, "Joan": joan_c, "CREATOR": cre, "WING": win}
        sq_net[i] = sum(ROT_SQ[k] / 48.0 * c_sq[k] for k in ROT_SQ)
        fb_net[i] = sum(ROT_FB[k] / 48.0 * c_fb[k] for k in ROT_FB)

    anchor = BASE_NET - sq_net.mean()
    sq_P = f(sq_net + anchor + sq_fit)
    fb_P = f(fb_net + anchor + fb_fit)
    delta = (fb_P - sq_P) * 100
    return {"sq": sq_P.mean() * 100, "fb": fb_P.mean() * 100, "delta": delta.mean(),
            "lo": np.percentile(delta, 5), "hi": np.percentile(delta, 95),
            "p_pos": float((delta > 0).mean()) * 100, "sq_fit": sq_fit, "fb_fit": fb_fit,
            "fb_net": (fb_net + anchor).mean()}


def main():
    val, dims, avail, dev, sub_ids = load_inputs()
    print("building f-curve (P(title) vs MIN net) ...", flush=True)
    fcurve = build_fcurve()
    grid, P = fcurve
    print(f"  sanity: f(+1.36)={np.interp(1.36, grid, P)*100:.2f}% (status-quo anchor ~1.8%)\n")

    CRE = {"MPJ": ret_spec("MPJ", val, avail), "Jrue": ret_spec("Jrue", val, avail), "Cam": ret_spec("Cam", val, avail)}
    WIN = {"relief": None, "ONeale": ret_spec("ONeale", val, avail), "DFS": ret_spec("DFS", val, avail)}
    med = (CRE["Jrue"], WIN["ONeale"])

    def row(lab, **kw):
        r = run_cell(val, dims, avail, dev, sub_ids, fcurve=fcurve, **kw)
        print(f"  {lab:44s} SQ {r['sq']:.2f}% FB {r['fb']:.2f}% (net {r['fb_net']:+.2f}) "
              f"dP {r['delta']:+.2f}pp [{r['lo']:+.2f},{r['hi']:+.2f}] P(FB>SQ) {r['p_pos']:>3.0f}%")
        return r

    print("=== PRIMARY (central: Jrue + O'Neale, full class, repl -1.70, fit 0.75) ===")
    base = row("central", returns=med)
    print(f"    fit: SQ {base['sq_fit']:+.2f}  FB {base['fb_fit']:+.2f}  (FB should be >= SQ if it fills gaps)")

    print("\n=== RETURN-QUALITY sweep (the biggest driver) ===")
    row("conservative: MPJ + relief", returns=(CRE["MPJ"], WIN["relief"]))
    row("median: Jrue + O'Neale", returns=med)
    row("optimistic*: Cam + DFS (LOW-PROB deals)", returns=(CRE["Cam"], WIN["DFS"]))
    print("  -- decoupled (which side carries it?) --")
    row("creator only: Jrue + relief wing", returns=(CRE["Jrue"], WIN["relief"]))
    row("wing only: MPJ(flat) + O'Neale", returns=(CRE["MPJ"], WIN["ONeale"]))

    print("\n=== one-at-a-time sensitivities (around median) ===")
    row("Joan sub-class (faithful, 64% bust)", returns=med, joan_class="sub")
    row("replacement -0.97 (generous)", returns=med, repl=-0.97)
    row("replacement -2.83 (harsh)", returns=med, repl=-2.83)
    row("fit 0 (no fit term)", returns=med, fit_bound=0.0)
    row("fit 1.5 (max data bound)", returns=med, fit_bound=1.5)
    row("veteran collapse x2", returns=med, collapse=2.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
