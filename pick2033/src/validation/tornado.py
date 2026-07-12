"""S7 tornado runner (spec Section 9 + accumulated ruling arms).
BUILT 2026-07-02; EXECUTION ENGINE IMPLEMENTED 2026-07-12 (post-July-6,
terms verified, priced runs unlocked).

Each arm = one Engine D run (20k paths) + one priced pass, reported as
deltas on the headline outputs (2033 pick EV, total asset cost, P(top4),
P(top10)) against a 20k BASE run with the SAME seed, so arm deltas are
CRN-paired and not confounded with path-count Monte Carlo error. The 50k
FINAL headline is reported alongside for reference. Per-arm definitions
are pre-declared in ARMS; no arm is tuned after seeing its result.

Pricing-only arms (currency, top1 flag) re-price the base run without a
re-sim. Refit arms (CHA lineage, S-CONTRACT) key their own posterior
caches via data-hash cache keys.

S-CONTRACT disclosure: the 2026-07-02 note routed "21 residual segments"
to this arm but did not persist the list. This runner uses the
reproducible definition: every glued contract segment of >= 6 seasons in
the backfill OUTSIDE the five ground-truth-verified careers
(Edwards/Garnett/LeBron/Duncan/Kobe), split at its midpoint. That yields
26 segments, a superset of the noted 21, which makes the perturbation
conservative (stronger, not weaker). Recorded in the output JSON.

Progress is checkpointed to outputs/json/tornado_progress.json after every
arm; a re-run skips completed arms (delete the file for a fresh pass).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.sim.pick_ledger import require_verified_terms  # noqa: E402

POSTERIORS = PROJECT_ROOT / "outputs" / "posteriors"
STAGED = PROJECT_ROOT / "data" / "staged"
OUT_JSON = PROJECT_ROOT / "outputs" / "json"
OUT_VAL = PROJECT_ROOT / "outputs" / "validation"
PROGRESS = OUT_JSON / "tornado_progress.json"

N_ARM_PATHS = 20_000
GROUND_TRUTH_CAREERS = {"edwaran01", "garneke01", "jamesle01", "duncati01", "bryanko01"}

ARMS = [
    # (name, kind, spec) -- kinds consumed by run_arm()
    ("hazard_scale_0.5x", "hazard_scale", 0.5),
    ("hazard_scale_1.5x", "hazard_scale", 1.5),
    ("blend_faster", "blend_shift", -1),          # roster trust decays one season faster
    ("blend_slower", "blend_shift", +1),
    ("trajectory_phi_p10", "posterior_pctile", ("phi", 10)),
    ("trajectory_phi_p90", "posterior_pctile", ("phi", 90)),
    ("shock_scale_p10", "posterior_pctile", ("sigma_shock", 10)),
    ("shock_scale_p90", "posterior_pctile", ("sigma_shock", 90)),
    ("slot_value_ws", "currency", "ws"),
    ("playin_crude_randomization", "playin", "crude"),
    ("top1_carries_false", "config", {"top1_carries_to_CHA": False}),
    ("pooled_dynamics", "posterior_swap", "trajectory_c0a9750162a046d3"),  # Ruling A cond. 1, fit-once
    ("cha_lineage_bobcats_fresh", "refit_lineage", "bobcats_fresh"),       # Bobby amendment 5 (plan)
    ("s_contract_midpoint_split", "hazard_refit_perturbed", "midpoint_split"),  # directive 3, ungated
    ("lamelo_extended", "config", {"lamelo_contract": "extended"}),
]


def load_params():
    return yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())


def headline(res, price_seed, currency="vorp", top1=True) -> dict:
    """Price a sim result and pull the tornado headline outputs."""
    from src.sim.league_sim import SEASONS
    from src.sim.swap_pricing import price_all
    slots, fr_ids = res["slots"], list(res["fr_ids"])
    dep = {"Anthony Edwards": np.asarray(res["departures"]["Anthony Edwards"], bool)}
    cha_win = res["win_paths"][:, SEASONS.index(2033), fr_ids.index("CHA")] / 82.0
    rep = price_all(slots, fr_ids, SEASONS, dep, cha_win, price_seed,
                    top1_carries_to_CHA=top1, currency=currency)
    s33 = slots[:, SEASONS.index(2033), fr_ids.index("MIN")]
    return {
        "pick_ev_2033": rep["outright_2033"]["mean"],
        "total_mean": rep["total_per_path"]["mean"],
        "total_q10": rep["total_per_path"]["q10"],
        "total_q90": rep["total_per_path"]["q90"],
        "p_top4": float((s33 <= 4).mean()),
        "p_top10": float((s33 <= 10).mean()),
        "currency": currency,
        "top1_carries_to_CHA": top1,
        "swap_means": {y: rep["swaps"][y]["mean"] for y in rep["swaps"]},
    }


def midpoint_split_backfill() -> tuple[pd.DataFrame, int]:
    """The S-CONTRACT perturbation: split every >= 6-season glued countdown
    segment (outside the ground-truth careers) into two contracts at the
    midpoint, creating a walk year where the Duncan-pattern re-sign would
    hide. Returns (perturbed backfill, n segments split)."""
    bf = pd.read_parquet(STAGED / "contract_years_backfill.parquet")
    bf = bf.sort_values(["player_id", "season"]).reset_index(drop=True)
    cyr = bf.contract_years_remaining.values.astype(float).copy()
    n_split = 0
    for pid, g in bf.groupby("player_id"):
        if pid in GROUND_TRUTH_CAREERS:
            continue
        idx = g.index.to_numpy()
        seasons = g.season.values
        c = g.contract_years_remaining.values
        seg = [0]
        for j in range(1, len(idx)):
            if seasons[j] - seasons[j - 1] != 1 or c[j] != c[j - 1] - 1:
                seg.append(j)
        seg.append(len(idx))
        for a, b in zip(seg[:-1], seg[1:]):
            L = b - a
            if L < 6:
                continue
            n_split += 1
            half = (L + 1) // 2           # first sub-contract gets the extra season
            # first half: countdown ending at the midpoint (a walk year appears)
            for k in range(half):
                cyr[idx[a + k]] = half - 1 - k
            # second half keeps the original contract end
    out = bf.copy()
    out["contract_years_remaining"] = cyr
    return out, n_split


def scontract_hazard_refit(params) -> tuple[pd.DataFrame, dict]:
    """Refit the M2-spec hazard on the FINAL freeze with the perturbed
    contract labels. Own cache tag (m2sc_full) so it can never be picked up
    by Engine D's hazard_m2_full_* glob."""
    import src.models.hazard as hz
    bf, n_split = midpoint_split_backfill()
    sp = pd.read_parquet(STAGED / "star_spells_final.parquet")
    d = sp.drop(columns=["contract_years_remaining"], errors="ignore").merge(
        bf[["player_id", "season", "contract_years_remaining"]],
        on=["player_id", "season"], how="left")
    d, stats = hz.prep(d)
    known = d.contract_years_remaining.notna()
    v = d.contract_years_remaining.fillna(0.0)
    stats["cyr_mean"] = float(v[known].mean())
    stats["cyr_sd"] = float(v[known].std())
    d["contract_z"] = np.where(known, (v - stats["cyr_mean"]) / stats["cyr_sd"], 0.0)
    d["contract_known"] = known.astype(float)
    stats["n_segments_split"] = n_split

    saved = hz.COVARS
    hz.COVARS = hz.M2_FINAL_SPEC["covariates"]
    try:
        post, health = hz.fit_m2_priors(d, "m2sc_full", params["seed"] + 2,
                                        hz.M2_FINAL_SPEC["coef_prior_sd"])
    finally:
        hz.COVARS = saved
    print(f"  s_contract refit: {n_split} segments split, "
          f"b_contract_z {post['b_contract_z'].mean():+.3f} "
          f"(health {health})", flush=True)
    return post, stats


def run_arm(name, kind, spec, base_res, params):
    """Execute one pre-declared arm; returns (headline dict, note)."""
    from src.models.trajectory import fit as fit_trajectory
    from src.models.trajectory import load_panel
    from src.sim.league_sim import EngineD
    eng_seed = params["seed"] + 5
    price_seed = params["seed"] + 7
    note = ""

    if kind == "currency":
        return headline(base_res, price_seed, currency=spec), "re-price of base run"
    if kind == "config" and "top1_carries_to_CHA" in spec:
        return headline(base_res, price_seed, top1=False), "re-price of base run"

    if kind == "hazard_scale":
        eng = EngineD(N_ARM_PATHS, eng_seed)
        orig = eng.hazard_for
        eng.hazard_for = lambda *a, **k: np.clip(orig(*a, **k) * spec, 0.0, 1.0)
    elif kind == "blend_shift":
        eng = EngineD(N_ARM_PATHS, eng_seed)
        w = eng.blend_w
        years = sorted(w)
        # spec -1 (faster): season t uses w(t+1); spec +1 (slower): w(t-1);
        # clamped at the schedule ends.
        eng.blend_w = {y: w[min(max(y + (1 if spec < 0 else -1), years[0]), years[-1])]
                       for y in years}
        note = f"blend_w shifted, clamped: {eng.blend_w}"
    elif kind == "posterior_pctile":
        var, pct = spec
        eng = EngineD(N_ARM_PATHS, eng_seed)
        val = float(np.percentile(eng.post_a[var].values, pct))
        setattr(eng, var, np.full(eng.n_paths, val))
        note = f"{var} pinned at posterior p{pct} = {val:.4f}"
    elif kind == "playin":
        eng = EngineD(N_ARM_PATHS, eng_seed, playin_mode="crude")
    elif kind == "config":
        eng = EngineD(N_ARM_PATHS, eng_seed)
        eng.lamelo_scenario = spec["lamelo_contract"]
        note = f"lamelo_contract = {spec['lamelo_contract']}"
    elif kind == "posterior_swap":
        path = POSTERIORS / f"{spec}.parquet"
        post = pd.read_parquet(path)
        base_eng = EngineD(4, eng_seed)          # tiny throwaway for fr_ids
        fr_ids = base_eng.fr_ids
        missing = [f for f in fr_ids if f"mu_{f}" not in post.columns]
        if missing:
            raise RuntimeError(f"pooled posterior missing mu columns: {missing}")
        eng = EngineD(N_ARM_PATHS, eng_seed, trajectory_post=(post, fr_ids))
        note = f"trajectory posterior swapped to {spec}"
    elif kind == "refit_lineage":
        panel = load_panel()
        panel = panel[~((panel.franchise_id == "CHA") & (panel.season < 2005))]
        post, fr_ids, cache = fit_trajectory(quiet=True, panel_override=panel)
        eng = EngineD(N_ARM_PATHS, eng_seed, trajectory_post=(post, fr_ids))
        note = f"CHA lineage starts 2005 (Bobcats fresh); trajectory cache {cache.name}"
    elif kind == "hazard_refit_perturbed":
        post_h, stats = scontract_hazard_refit(params)
        eng = EngineD(N_ARM_PATHS, eng_seed)
        eng.hazard_post = post_h
        eng.hazard_is_m2 = True
        eng.m2_stats = stats
        note = (f"S-CONTRACT midpoint split on {stats['n_segments_split']} residual "
                f"segments (26 reproducible vs 21 in the 7/2 note, superset, "
                f"conservative); b_contract_z {post_h['b_contract_z'].mean():+.3f}")
    else:
        raise ValueError(f"unknown arm kind {kind}")

    res = eng.run()
    return headline(res, price_seed), note


def main():
    require_verified_terms()   # hard gate: no tornado before pricing unlocks
    params = load_params()
    OUT_JSON.mkdir(parents=True, exist_ok=True)
    done = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}

    from src.sim.league_sim import EngineD
    print(f"tornado: base run ({N_ARM_PATHS} paths, seed {params['seed'] + 5})", flush=True)
    if "BASE_20K" in done:
        base_head = done["BASE_20K"]["headline"]
        print("  base headline from checkpoint", flush=True)
        base_res = None
    else:
        t0 = time.time()
        base_eng = EngineD(N_ARM_PATHS, params["seed"] + 5)
        base_res = base_eng.run()
        base_head = headline(base_res, params["seed"] + 7)
        done["BASE_20K"] = {"headline": base_head, "runtime_s": round(time.time() - t0, 1)}
        PROGRESS.write_text(json.dumps(done, indent=1))
        print(f"  base: pick EV {base_head['pick_ev_2033']:.2f}, "
              f"total {base_head['total_mean']:.2f} ({done['BASE_20K']['runtime_s']}s)", flush=True)

    # pricing-only arms need the base sim in memory; rebuild once if resuming
    needs_base = [a for a in ARMS
                  if a[0] not in done and (a[1] == "currency"
                                           or (a[1] == "config" and "top1_carries_to_CHA" in a[2]))]
    if base_res is None and needs_base:
        base_res = EngineD(N_ARM_PATHS, params["seed"] + 5).run()

    for name, kind, spec in ARMS:
        if name in done:
            print(f"arm {name}: checkpointed, skipping", flush=True)
            continue
        print(f"arm {name} ({kind}) ...", flush=True)
        t0 = time.time()
        head, note = run_arm(name, kind, spec, base_res, params)
        entry = {"kind": kind, "spec": str(spec), "headline": head, "note": note,
                 "runtime_s": round(time.time() - t0, 1)}
        if head["currency"] == base_head["currency"]:
            entry["delta"] = {k: round(head[k] - base_head[k], 4)
                              for k in ("pick_ev_2033", "total_mean", "p_top4", "p_top10")}
        else:
            entry["delta"] = {"note": "currency differs from base; compare shape, not level",
                              "total_over_pick_ratio_arm":
                                  round(head["total_mean"] / head["pick_ev_2033"], 3),
                              "total_over_pick_ratio_base":
                                  round(base_head["total_mean"] / base_head["pick_ev_2033"], 3)}
        done[name] = entry
        PROGRESS.write_text(json.dumps(done, indent=1))
        print(f"  {name}: total {head['total_mean']:.2f} "
              f"(delta {entry['delta'].get('total_mean', 'n/a')}), "
              f"{entry['runtime_s']}s", flush=True)

    # final artifact: arms sorted by |delta on total|, base + 50k reference
    final_50k = None
    swp = OUT_JSON / "swap_pricing_FINAL.json"
    if swp.exists():
        r = json.loads(swp.read_text())["runs"]["top1_true_vorp"]
        final_50k = {"pick_ev_2033": r["outright_2033"]["mean"],
                     "total_mean": r["total_per_path"]["mean"]}
    arms_sorted = sorted(
        (dict(v, name=k) for k, v in done.items() if k != "BASE_20K"),
        key=lambda e: -abs(e["delta"].get("total_mean", 0.0))
        if isinstance(e["delta"].get("total_mean", 0.0), (int, float)) else 0.0)
    payload = {
        "meta": {"tag": "FINAL", "n_arm_paths": N_ARM_PATHS,
                 "engine_seed": params["seed"] + 5, "price_seed": params["seed"] + 7,
                 "base_20k": base_head, "final_50k_reference": final_50k,
                 "pairing": "all arms share the base seed (CRN-paired deltas)"},
        "arms": arms_sorted,
    }
    (OUT_JSON / "tornado_FINAL.json").write_text(json.dumps(payload, indent=1))

    lines = ["# S7 tornado (FINAL)",
             f"- base 20k: pick EV {base_head['pick_ev_2033']:.2f}, "
             f"total {base_head['total_mean']:.2f} "
             f"(50k reference: {final_50k})",
             "- arms by |delta total| (4-yr VORP):"]
    for e in arms_sorted:
        d = e["delta"].get("total_mean", "n/a")
        lines.append(f"  - {e['name']}: total {e['headline']['total_mean']:.2f} "
                     f"(delta {d}), pick EV {e['headline']['pick_ev_2033']:.2f}"
                     + (f" -- {e['note']}" if e["note"] else ""))
    OUT_VAL.mkdir(parents=True, exist_ok=True)
    (OUT_VAL / "tornado_FINAL.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
