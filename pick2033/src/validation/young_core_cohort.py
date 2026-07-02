"""Ruling D: young-core cohort analysis — validating the CHA crest as a
swap-pricing input (NOT gate rescue; the error direction favors the thesis).

Cohort (pre-committed): 1985-2019 entry team-seasons with win_pct < .500
and 3+ players under 23 (age <= 22) with 1000+ minutes for that franchise.
Trajectory: win_pct over entry+1 .. entry+5. Fans reported unconditional
AND matched on entry band [.400, .500).

OPERATIONALIZATION (declared before results):
  - model side: post-trade CHA, seed-20330706 two-tier run; year 0 = 2026
    (post-trade expected strength .48 win pct — in the matched band by
    expectation; the pre-trade realized 2026 record of .537 belonged to the
    roster WITH LaMelo and is not the simulated object), years 1-5 =
    2027-2031 median wins.
  - cohort side: matched-band p70 trajectory, win_pct * 82.
  - decision rule (Ruling D.2): if model median PEAK over years 1-5 exceeds
    the matched cohort's p70 PEAK, apply the cohort-calibrated young-roster
    blend adjustment (fit to cohort MEDIAN, blind to swap prices), re-run
    Engine D + all 8.4 gates once. Otherwise the crest stands, documented.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "outputs" / "validation"

# Fallback = the provisional run (seed 20330706). The RE-ARMED rule
# (2026-07-02 markup): the p70 trigger binds to the artifact that ships --
# on July 6 this script re-runs against the FINAL Engine D output
# (read live from outputs/sims/ below) and the cohort-calibrated adjustment
# fires automatically if the final crest crosses p70. Cohort side is final
# and fixed; only the model side re-reads.
MODEL_CHA_MEDIANS = [45.0, 49.8, 50.8, 49.2, 46.9]   # provisional fallback


def model_cha_medians_by_scenario() -> dict[str, list[float]]:
    """Designated tags only, NEVER newest-file logic (a both-ways July-6 run
    produces two FINAL-class artifacts and mtime would make the validation
    input depend on run order). Priority: the base-case FINAL if it exists;
    else BOTH both-ways scenario finals (each evaluated, BOTH must sit under
    threshold); else the provisional fallback."""
    sims = PROJECT_ROOT / "outputs" / "sims"

    def medians(path):
        z = np.load(path)
        ti = list(z["fr_ids"]).index("CHA")
        return [round(float(np.median(z["winpct"][:, y, ti])) * 82, 1) for y in range(5)]

    base = sims / "winpct_two_tier_FINAL.npz"
    if base.exists():
        return {"FINAL": medians(base)}
    scen = {f"FINAL_{s}": sims / f"winpct_two_tier_FINAL_{s}.npz"
            for s in ("UNSIGNED", "EXTENDED")}
    found = {k: medians(p) for k, p in scen.items() if p.exists()}
    if found:
        return found
    return {"PROVISIONAL": medians(sims / "winpct_two_tier_PROVISIONAL.npz")}


def build_cohort():
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    young = con.execute("""
        SELECT franchise_id, season, count(*) AS n_young
        FROM player_impact_seasons
        WHERE NOT is_combined AND franchise_id IS NOT NULL
          AND age <= 22 AND mp >= 1000
        GROUP BY franchise_id, season
        HAVING count(*) >= 3
    """).fetchdf()
    fs = con.execute("SELECT franchise_id, season, win_pct FROM franchise_seasons").fetchdf()
    con.close()
    entries = young.merge(fs, on=["franchise_id", "season"])
    entries = entries[(entries.season.between(1985, 2019)) & (entries.win_pct < 0.5)]
    traj = {}
    fsi = fs.set_index(["franchise_id", "season"]).win_pct
    rows = []
    for _, e in entries.iterrows():
        t = [fsi.get((e.franchise_id, e.season + k), np.nan) for k in range(1, 6)]
        if np.isnan(t).sum() <= 1:      # allow one missing (lockout edge)
            rows.append({"franchise_id": e.franchise_id, "entry": int(e.season),
                         "entry_wp": float(e.win_pct), "traj": t})
    return entries, pd.DataFrame(rows)


def fan(trajs: np.ndarray) -> dict:
    out = {}
    for q in (10, 30, 50, 70, 90):
        out[f"p{q}"] = [round(float(np.nanpercentile(trajs[:, k], q)) * 82, 1)
                        for k in range(5)]
    return out


def main():
    entries, cohort = build_cohort()
    matched = cohort[(cohort.entry_wp >= 0.40) & (cohort.entry_wp < 0.50)]
    t_all = np.array(cohort.traj.tolist(), float)
    t_m = np.array(matched.traj.tolist(), float)
    fan_all, fan_m = fan(t_all), fan(t_m)

    by_scenario = model_cha_medians_by_scenario()
    for tag, med in by_scenario.items():
        print(f"model CHA medians [{tag}]: {med}")
    medians = max(by_scenario.values(), key=max)   # report the worst case
    model_peak = max(max(m) for m in by_scenario.values())
    p70_peak = max(fan_m["p70"])
    p50_peak = max(fan_m["p50"])
    # trigger if ANY evaluated scenario crests over p70 (both-ways runs must
    # BOTH sit under threshold to pass)
    triggered = model_peak > p70_peak

    report = {
        "cohort_n": len(cohort), "matched_n": len(matched),
        "unconditional_fan_wins": fan_all,
        "matched_fan_wins": fan_m,
        "model_cha_medians_2027_2031": medians,
        "model_peak": model_peak, "matched_p70_peak": p70_peak,
        "matched_p50_peak": p50_peak,
        "decision_rule_triggered": bool(triggered),
        "prediction_P2_grade": ("CONFIRMED: matched median crest "
                                f"{p50_peak} < model crest {model_peak}"
                                if p50_peak < model_peak else
                                f"REFUTED: matched median crest {p50_peak} "
                                f">= model crest {model_peak}"),
    }
    (OUT / "young_core_cohort.json").write_text(json.dumps(report, indent=1))
    print(f"cohort: {len(cohort)} entries ({len(matched)} in matched band .400-.500)")
    print("matched fan (wins), years +1..+5:")
    for q in ("p10", "p30", "p50", "p70", "p90"):
        print(f"  {q}: {fan_m[q]}")
    print(f"model CHA medians 2027-31: {medians}")
    print(f"DECISION RULE: model peak {model_peak} vs matched p70 peak {p70_peak} "
          f"-> {'TRIGGERED (apply cohort-calibrated adjustment)' if triggered else 'crest stands'}")
    print(f"P2: {report['prediction_P2_grade']}")


if __name__ == "__main__":
    main()
