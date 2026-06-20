#!/usr/bin/env python3
"""Phase 1a: established-player impact distributions over the 2-year horizon.

For each established (reliable-RAPM) player relevant to the three scenarios, the impact
distribution is Normal(point + age drift, sd), where:
  - point   = consensus_net (the externally triangulated 0.6 RAPM / 0.4 BBR estimate),
  - age drift = the standard deterministic aging prior (age_curve.py), Year 1 (2026-27)
                and Year 2 (2027-28),
  - sd      = net_sd transformed by the calibrated inflation (inflation_params.json).
              1c adopted a=1.0, b=0.0, so this is the analytic posterior SD as-is (no
              inflation, no shrink); the params file makes Phase 3-4 sweeps a one-line change.

These are distribution PARAMETERS; Phase 3 samples Normal(point, sd) per Monte Carlo
iteration (never collapsing to the mean). Young / prior-dominated players (Joan) are NOT
here; they are the Phase 2 development module, with the rim correction gated off.

    python core_max/impact/established_distributions.py
"""
import os
import sys
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
import age_curve as AC  # noqa: E402

PV = os.path.join(REPO, "offseason", "data", "player_value.csv")
OUTDIR = os.path.join(REPO, "core_max", "outputs", "phase1")
PARAMS = os.path.join(OUTDIR, "inflation_params.json")

# The established players in the three scenarios (Joan is young -> Phase 2, excluded here).
POOL = ["Anthony Edwards", "Jaden McDaniels", "Naz Reid", "Terrence Shannon", "Rudy Gobert",
        "Julius Randle", "Mike Conley", "Donte DiVincenzo", "Ayo Dosunmu"]


def main():
    pv = pd.read_csv(PV)
    point_col = "consensus_net" if "consensus_net" in pv.columns else "net_rapm"
    if point_col != "consensus_net":
        print("NOTE: consensus_net absent; falling back to net_rapm as the point estimate.")
    with open(PARAMS, encoding="utf-8") as fh:
        p = json.load(fh)
    a, b, zmu, zsd = p["a"], p["b"], p["zmu"], p["zsd"]
    print(f"inflation params: a={a}, b={b} (adopted: {p.get('decision','')[:48]}...)")

    rows = []
    for name in POOL:
        r = pv[pv["player_name"].str.contains(name, na=False)]
        if not len(r):
            print(f"  [missing] {name} not found in player_value.csv"); continue
        r = r.iloc[0]
        pid = str(int(r["player_id"]))
        age = AC.ages_2026_27([pid]).get(pid)
        point = float(r[point_col])
        div = abs(float(r["net_rapm"]) - float(r["box_net_bpm"]))
        sd_used = float(r["net_sd"]) * a * (1 + b * (div - zmu) / zsd)
        d1 = AC.age_delta(age) if age is not None else 0.0
        d2 = AC.age_delta(age + 1.0) if age is not None else 0.0
        rows.append({
            "player_id": pid, "player_name": r["player_name"],
            "age_2026_27": round(age, 1) if age is not None else None,
            "point": round(point, 2), "net_sd": round(float(r["net_sd"]), 2),
            "sd_used": round(sd_used, 2),
            "point_y1": round(point + d1, 2), "point_y2": round(point + d2, 2),
            "age_drift_y1": round(d1, 2), "age_drift_y2": round(d2, 2),
            "reliable": r["reliable"],
        })
    out = pd.DataFrame(rows)
    os.makedirs(OUTDIR, exist_ok=True)
    out.to_csv(os.path.join(OUTDIR, "established_distributions.csv"), index=False)

    print(f"\n{'player':22s} {'age':>4s} {'pt':>6s} {'sd':>5s} {'Y1':>6s} {'Y2':>6s} {'driftY1':>8s} {'driftY2':>8s}")
    for _, r in out.iterrows():
        print(f"{r['player_name'][:22]:22s} {r['age_2026_27']:>4} {r['point']:>+6.2f} {r['sd_used']:>5.2f} "
              f"{r['point_y1']:>+6.2f} {r['point_y2']:>+6.2f} {r['age_drift_y1']:>+8.2f} {r['age_drift_y2']:>+8.2f}")
    print(f"\nwrote {os.path.join(OUTDIR, 'established_distributions.csv')} ({len(out)} established players; "
          f"sd_used = net_sd (a=1,b=0 as-is). Phase 3 samples Normal(point_y*, sd_used).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
