"""ON-5: one-time CRN-paired marginal-equity curve precompute (adapter F).

For each reference tier (rebuild / mid / playoff / contender -- chosen from
the actual 2026-27 field by net rating) x net-delta grid, run CRN-paired
bracket_sim.simulate_league pre/post (same seeds; the lamelo/sim/run_sim.py
pattern) and record the delta in P(title) percentage points.

Per the gate ruling: ONLY deltas are stored; absolute levels never leave
this script. Cache: outputs/posteriors/equity_curve.json with version hash.

Perspective note (plan D3, Bobby amendment 1): the curve serves BOTH
co-equal outputs (value-to-CHA at CHA's tier path, MIN-forgone at MIN's) --
tier interpolation happens in the adapter, not here.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(REPO_ROOT / "offseason" / "scripts"))

import bracket_sim as E  # noqa: E402
from build_team_ratings import load_impacts  # noqa: E402

TIERS = {"rebuild": None, "mid": None, "playoff": None, "contender": None}
DELTAS = [0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0]
SEEDS = [1, 2, 3, 4, 5]
N_SIMS = 20000
OUT = PROJECT_ROOT / "outputs" / "posteriors" / "equity_curve.json"


def pick_reference_teams(strengths) -> dict:
    """Choose actual teams nearest the tier archetypes by net rating."""
    nets = {t: float(v["net"]) for t, v in strengths.items()}
    ordered = sorted(nets, key=nets.get)
    n = len(ordered)
    return {
        "rebuild": ordered[2],                 # bottom tier, not the absolute floor
        "mid": ordered[n // 2],
        "playoff": ordered[int(n * 0.75)],
        "contender": ordered[-2],              # top tier, not the single best
    }


def main():
    imp = load_impacts()
    strengths = E.build_2026_27_league(imp)
    refs = pick_reference_teams(strengths)
    print("reference teams:", refs, flush=True)

    curve = {}
    for tier, team in refs.items():
        base_net = float(strengths[team]["net"])
        curve[tier] = {"team": team, "base_net": base_net, "points": []}
        for delta in DELTAS:
            dts = []
            for s in SEEDS:
                strengths[team]["net"] = base_net
                pre = E.simulate_league(strengths, n_sims=N_SIMS, seed=s)["teams"][team]["title"]
                strengths[team]["net"] = base_net + delta
                post = E.simulate_league(strengths, n_sims=N_SIMS, seed=s)["teams"][team]["title"]
                dts.append((post - pre) * 100.0)
            strengths[team]["net"] = base_net
            curve[tier]["points"].append({
                "net_delta": delta,
                "dtitle_pp_mean": float(np.mean(dts)),
                "dtitle_pp_se": float(np.std(dts, ddof=1) / np.sqrt(len(dts))),
            })
            print(f"{tier} +{delta}: {np.mean(dts):+.3f}pp (se {np.std(dts, ddof=1)/np.sqrt(len(dts)):.3f})",
                  flush=True)

    blob = json.dumps(curve, sort_keys=True)
    payload = {
        "version_hash": hashlib.sha256(blob.encode()).hexdigest()[:16],
        "n_sims": N_SIMS, "seeds": SEEDS,
        "gate_note": "deltas only; absolute P(title) levels are gated and never stored",
        "curve": curve,
    }
    OUT.write_text(json.dumps(payload, indent=1))
    print(f"equity curve cached -> {OUT.name} ({payload['version_hash']})")


if __name__ == "__main__":
    main()
