"""
Sim layer (alebron / LeBron-to-MIN): title-odds and Q2 quantities, BOTH metric forks,
CRN-paired (current post-LaMelo roster vs +LeBron share the same random draws so the delta
isolates the LeBron signing).

Baseline chaining: the Q2 baseline here is the COMPLETED post-LaMelo roster, not run-it-back.
So MIN's baseline net = field run-it-back net + BETA * (LaMelo trade raw delta), read from the
LaMelo project's team_strength.json, which reproduces that project's post-trade net exactly
(2.183 rapm / 3.008 box). The treatment adds BETA * (LeBron raw delta) from THIS project's
team_strength.json. This keeps the two analyses consistent and auditable.

FIELD: run on BOTH (1) the calibrated 2025-26-anchored field (matches the LaMelo methodology
exactly; the low-researcher-DOF choice) and (2) that field with a documented set of the biggest
VERIFIED 2026 offseason moves applied (Jaylen Brown trade etc.; field_2026_offseason.json). The
CRN-paired LeBron delta is reported under both to SHOW it is field-robust; the absolute title %
shifts with the field, the delta does not. Title % stays gated on identifiability regardless.

Output: alebron/data/sim/sim_results.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "offseason" / "scripts"))
import build_team_ratings as A  # noqa: E402
import bracket_sim as E         # noqa: E402

OUT = REPO / "alebron" / "data" / "sim"
OUT.mkdir(parents=True, exist_ok=True)

imp_df = pd.read_csv(REPO / "alebron" / "data" / "impact" / "player_impact.csv")
ts_lebron = json.loads((REPO / "alebron" / "data" / "impact" / "team_strength.json").read_text())
ts_lamelo = json.loads((REPO / "lamelo" / "data" / "impact" / "team_strength.json").read_text())
BETA = float(E.load_e_params()["beta"])
SEEDS = [1, 2, 3, 4, 5]
N = 20000

# Documented field update: the biggest VERIFIED 2026 moves not in the calibrated field, as net
# adjustments (RS scale). Directional, high-confidence, title-relevant only. A SENSITIVITY, not
# the primary basis. Rationale in field_2026_offseason.json.
FIELD_2026_UPDATES = {
    "BOS": -2.0,   # Jaylen Brown to PHI for aging Paul George; Tatum still diminished
    "PHI": +2.0,   # Jaylen Brown in, Paul George out (Brown/Maxey/Embiid/Edgecombe)
    "LAC": -3.0,   # Kawhi Leonard to TOR; Kawhi/PG era blown up
    "TOR": +2.5,   # Kawhi Leonard in (from a low base)
    "POR": +2.0,   # Ja Morant in
    "MEM": -1.5,   # Ja Morant out
    "LAL": -1.0,   # LeBron out (removes his 2025-26 double-count on LAL), partly offset by Kessler/retool
}


def make_imp(fork):
    imp = {}
    for _, r in imp_df.iterrows():
        pid = str(int(r.player_id))
        if fork == "rapm":
            off, dff = float(r.off_rapm), float(r.def_rapm)
        else:
            off, dff = float(r.box_off_prior), float(r.box_def_prior)
        imp[pid] = {"off": off, "def": dff, "off_sd": float(r.off_sd), "def_sd": float(r.def_sd),
                    "def_div": abs(float(r.def_rapm) - float(r.box_def_prior)), "read": ""}
    return imp


def run_fork(fork, field_updated):
    imp = make_imp(fork)
    strengths = E.build_2026_27_league(imp)
    if field_updated:
        for tm, d in FIELD_2026_UPDATES.items():
            if tm in strengths:
                strengths[tm]["net"] = round(strengths[tm]["net"] + d, 3)
    runitback = float(strengths["MIN"]["net"])                       # field MIN (pre-LaMelo)
    lamelo_delta = float(ts_lamelo["forks"][fork]["trade_delta_raw"])
    lebron_delta = float(ts_lebron["forks"][fork]["lebron_add_delta_raw"])
    min_baseline = runitback + BETA * lamelo_delta                   # completed post-LaMelo roster
    min_lebron = min_baseline + BETA * lebron_delta                  # + LeBron
    rows = {"min_runitback_net": round(runitback, 3), "min_baseline_postlamelo_net": round(min_baseline, 3),
            "min_with_lebron_net": round(min_lebron, 3),
            "deflated_lebron_delta": round(BETA * lebron_delta, 3)}
    dt, dcf, pt, pcf, pf, pt0 = [], [], [], [], [], []
    for s in SEEDS:
        strengths["MIN"]["net"] = min_baseline
        base = E.simulate_league(strengths, n_sims=N, seed=s, use_overlay=True)["teams"]["MIN"]
        strengths["MIN"]["net"] = min_lebron
        post = E.simulate_league(strengths, n_sims=N, seed=s, use_overlay=True)["teams"]["MIN"]
        dt.append(post["title"] - base["title"])
        dcf.append(post["cf"] - base["cf"])
        pt.append(post["title"]); pcf.append(post["cf"]); pf.append(post["finals"]); pt0.append(base["title"])
    rows.update({
        "baseline_title": float(np.mean(pt0)), "with_lebron_title": float(np.mean(pt)),
        "with_lebron_cf": float(np.mean(pcf)), "with_lebron_finals": float(np.mean(pf)),
        "title_delta_pp": float(np.mean(dt)) * 100, "title_delta_mc_sd_pp": float(np.std(dt)) * 100,
        "cf_delta_pp": float(np.mean(dcf)) * 100,
    })
    return rows


def main():
    res = {"n_sims": N, "seeds": SEEDS, "beta": BETA,
           "gate_note": "TITLE % GATED on identifiability (same engine, same noise floor as the LaMelo "
                        "project). The CRN-paired delta and Q2 ordinals are field-robust and reported.",
           "field_2026_updates": FIELD_2026_UPDATES, "fields": {}}
    for field_key, updated in [("calibrated_primary", False), ("field_2026_updated_sensitivity", True)]:
        res["fields"][field_key] = {"forks": {}}
        print(f"\n########## FIELD: {field_key} ##########")
        for fork in ["rapm", "box"]:
            f = run_fork(fork, updated)
            res["fields"][field_key]["forks"][fork] = f
            print(f"[{fork:4}] MIN post-LaMelo {f['min_baseline_postlamelo_net']:+.2f} -> +LeBron "
                  f"{f['min_with_lebron_net']:+.2f} (LeBron {f['deflated_lebron_delta']:+.3f})")
            print(f"       baseline title {f['baseline_title']*100:.2f}%  +LeBron title {f['with_lebron_title']*100:.2f}%"
                  f"  CF {f['with_lebron_cf']*100:.1f}%  Finals {f['with_lebron_finals']*100:.1f}%")
            print(f"       title DELTA {f['title_delta_pp']:+.3f}pp (MC sd {f['title_delta_mc_sd_pp']:.3f}pp)  "
                  f"CF delta {f['cf_delta_pp']:+.2f}pp")
    pj = res["fields"]["calibrated_primary"]["forks"]
    lo = min(pj["rapm"]["title_delta_pp"], pj["box"]["title_delta_pp"])
    hi = max(pj["rapm"]["title_delta_pp"], pj["box"]["title_delta_pp"])
    res["title_delta_structural_band_pp_primary"] = [round(lo, 3), round(hi, 3)]
    res["band_note"] = ("Inter-fork point spread on the primary field ONLY. Does NOT include the "
                        "retention x availability fork (sweep_lebron_availability.py) or MC/parametric "
                        "uncertainty. The single-season noise (sigma_t ~ 5.5) dwarfs a ~+0.9 net add, so "
                        "the title delta is NOT identifiable to a point regardless of field.")
    (OUT / "sim_results.json").write_text(json.dumps(res, indent=2))
    print(f"\nTITLE DELTA structural band (primary field, across forks): [{lo:+.3f}, {hi:+.3f}] pp")
    print(f"wrote {OUT/'sim_results.json'}")


if __name__ == "__main__":
    main()
