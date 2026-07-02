"""ON-3 runner: Engine D at full path count, both variants, gates 8.4 under
the ratified operationalization. Outputs tagged PROVISIONAL.

Variants:
  two_tier   MIN/CHA roster-informed (Model C aging + PROVISIONAL Model B
             departures + blend), other 28 under Model A v2
  pure_a     all 30 under Model A v2 (no roster tier) -- comparison run

Artifacts per variant (outputs/sims/):
  slots_<variant>_PROVISIONAL.npz      (n_paths, 7, 30) int8 pick slots + fr_ids
  winpct_<variant>_PROVISIONAL.npz     (n_paths, 7, 30) float32 win pct
  manifest_<variant>.json              seed, calibrations, departure rates, gates
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import duckdb
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.sim.league_sim import SEASONS, EngineD  # noqa: E402
from src.validation.gates_84 import DISCLOSURE, evaluate_tail_gate  # noqa: E402

SIMS = PROJECT_ROOT / "outputs" / "sims"
OUT_VAL = PROJECT_ROOT / "outputs" / "validation"


def hist_win_pct():
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    fs = con.execute("SELECT franchise_id, season, win_pct FROM franchise_seasons").fetchdf()
    con.close()
    return fs


def autocorr_envelope(fs) -> dict:
    """Historical lag-k win-pct autocorrelation per decade; envelope = min/max."""
    out = {}
    for lag in (1, 2, 3):
        vals = []
        for lo in range(1980, 2020, 10):
            sub = fs[(fs.season >= lo) & (fs.season < lo + 10 + lag)]
            pairs = sub.merge(sub.assign(season=sub.season + lag),
                              on=["franchise_id", "season"], suffixes=("_b", "_a"))
            if len(pairs) > 50:
                vals.append(float(np.corrcoef(pairs.win_pct_a, pairs.win_pct_b)[0, 1]))
        out[lag] = {"min": min(vals), "max": max(vals), "by_decade": vals}
    return out


def sim_autocorr(wpct, lag):
    a = wpct[:, :-lag, :].ravel()
    b = wpct[:, lag:, :].ravel()
    return float(np.corrcoef(a, b)[0, 1])


def run_variant(name: str, n_paths: int, seed: int, use_roster_tier: bool,
                fs, env) -> dict:
    t0 = time.time()
    eng = EngineD(n_paths=n_paths, seed=seed, use_roster_tier=use_roster_tier)
    res = eng.run()
    runtime = time.time() - t0
    wins = res["win_paths"]
    wpct = (wins / 82).astype(np.float32)
    slots = res["slots"]

    # gates
    conservation = bool(np.allclose(wins.sum(axis=2), 1230.0, atol=1e-3))
    perm_ok = bool((np.sort(slots, axis=2) == np.arange(1, 31, dtype=np.int8)).all())
    tail = evaluate_tail_gate(wpct, fs.win_pct.values)
    ac = {lag: sim_autocorr(wpct, lag) for lag in (1, 2, 3)}
    ac_ok = all(env[lag]["min"] - 0.05 <= ac[lag] <= env[lag]["max"] + 0.05
                for lag in (1, 2, 3))

    SIMS.mkdir(parents=True, exist_ok=True)
    dep_arrays = ({f"dep_{k.replace(' ', '_')}": v
                   for k, v in res["departures"].items()}
                  if use_roster_tier else {})
    np.savez_compressed(SIMS / f"slots_{name}_PROVISIONAL.npz",
                        slots=slots, fr_ids=np.array(res["fr_ids"]),
                        seasons=np.array(SEASONS), **dep_arrays)
    np.savez_compressed(SIMS / f"winpct_{name}_PROVISIONAL.npz",
                        winpct=wpct, fr_ids=np.array(res["fr_ids"]))
    manifest = {
        "tag": "PROVISIONAL", "variant": name, "n_paths": n_paths, "seed": seed,
        "runtime_s": round(runtime, 1),
        "gates": {
            "conservation": conservation,
            "slot_permutation": perm_ok,
            "tail_terminal_pass": tail.terminal_pass,
            "tail_transient_pass": tail.transient_pass,
            "autocorr_pass": ac_ok,
        },
        "tail": {"terminal_top": tail.terminal_top, "terminal_bottom": tail.terminal_bottom,
                 "hist_top": tail.hist_top, "hist_bottom": tail.hist_bottom,
                 "yearly_top": tail.yearly_top, "pooled_top": tail.pooled_top,
                 "pooled_bottom": tail.pooled_bottom},
        "autocorr": {"sim": ac, "envelope": {k: {kk: vv for kk, vv in v.items()
                                                 if kk != "by_decade"}
                                             for k, v in env.items()}},
        "disclosure": DISCLOSURE,
    }
    if use_roster_tier:
        manifest["roster_cal"] = eng.roster_cal
        manifest["star_exit_prior_shift"] = eng.exit_shift
        manifest["departure_rates"] = {k: float(v.mean())
                                       for k, v in res["departures"].items()}
    (SIMS / f"manifest_{name}.json").write_text(json.dumps(manifest, indent=1))
    return manifest


def main():
    import yaml
    cfg = yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())
    n_paths = int(sys.argv[1]) if len(sys.argv) > 1 else cfg["simulation"]["n_paths"]
    seed = cfg["seed"] + 5
    fs = hist_win_pct()
    env = autocorr_envelope(fs)
    lines = [f"# Engine D run (PROVISIONAL), {n_paths} paths"]
    for name, tier in [("two_tier", True), ("pure_a", False)]:
        m = run_variant(name, n_paths, seed, tier, fs, env)
        g = m["gates"]
        lines.append(
            f"- **{name}** ({m['runtime_s']}s): conservation {g['conservation']}, "
            f"slots-perm {g['slot_permutation']}, tail terminal "
            f"{'PASS' if g['tail_terminal_pass'] else 'FAIL'}, transient "
            f"{'PASS' if g['tail_transient_pass'] else 'FAIL'}, autocorr "
            f"{'PASS' if g['autocorr_pass'] else 'FAIL'} {m['autocorr']['sim']}")
        if tier:
            lines.append(f"  departures: {m['departure_rates']}  "
                         f"exit_shift {m['star_exit_prior_shift']:.2f}  "
                         f"roster_cal r={m['roster_cal']['r']:.3f}")
        print(lines[-1], flush=True)
    OUT_VAL.mkdir(parents=True, exist_ok=True)
    (OUT_VAL / "engine_d_gates_PROVISIONAL.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
