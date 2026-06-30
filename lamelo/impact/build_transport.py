"""
Transport layer: adjust imported/departing impacts for the move into MIN's context,
under BOTH metric forks (box-prior RAPM and box-only BPM), with the two pre-registered
guards (defensive-divergence reporting, no double-counting). See 01_transport_framework.md.

HALT-for-review layer: this decides LaMelo's valuation before it feeds the sim.

Output: lamelo/data/impact/transport.json
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
IMP = REPO / "lamelo" / "data" / "impact" / "player_impact.csv"
OUT = REPO / "lamelo" / "data" / "impact" / "transport.json"

SURV, SURV_LO, SURV_HI = 0.75, 0.50, 0.90  # committed survival fraction + band

imp = pd.read_csv(IMP).set_index("player_name")


def fork(name, which):
    r = imp.loc[name]
    if which == "rapm":
        off, defp, net = float(r.off_rapm), -float(r.def_rapm), float(r.net_rapm)
    else:  # box-only BPM
        off, defp, net = float(r.box_off_prior), -float(r.box_def_prior), float(r.box_net_bpm)
    return {"off": round(off, 2), "def_contrib": round(defp, 2), "net": round(net, 2)}


def lamelo_transport(which):
    raw = fork("LaMelo Ball", which)
    # A: survival on NET
    a_net = round(SURV * raw["net"], 2)
    a_band = [round(SURV_LO * raw["net"], 2), round(SURV_HI * raw["net"], 2)]
    # B: survival on OFFENSE, carry measured defense (double-count guard)
    b_off = SURV * raw["off"]
    b_net = round(b_off + raw["def_contrib"], 2)
    b_band = [round(SURV_LO * raw["off"] + raw["def_contrib"], 2),
              round(SURV_HI * raw["off"] + raw["def_contrib"], 2)]
    b_net_survival = round(b_net / raw["net"], 2) if raw["net"] else None
    return {
        "raw": raw,
        "A_surv_on_net": {"net_center": a_net, "net_band": a_band,
                          "def_contrib_carried": raw["def_contrib"]},
        "B_surv_on_off": {"off_center": round(b_off, 2), "def_contrib": raw["def_contrib"],
                          "net_center": b_net, "net_band": b_band,
                          "implied_net_survival": b_net_survival},
    }


def departing(name, which):
    raw = fork(name, which)
    return {"raw": raw, "impact_lost_net": raw["net"], "def_contrib_lost": raw["def_contrib"],
            "note": "no survival haircut; measured in MIN context, lost in full"}


def importing(name, which, surv=1.0):
    raw = fork(name, which)
    return {"raw": raw, "transported_net": round(surv * raw["net"], 2),
            "surv": surv, "note": "near face value, role close to prior"}


def gobert_fragility(which):
    g = fork("Rudy Gobert", which)["def_contrib"]
    backups = {n: fork(n, which)["def_contrib"] for n in ["Mouhamed Gueye", "Joan Beringer"]}
    best_backup = max(backups.values())
    return {"gobert_def_contrib": g, "backup5_def_contrib": backups,
            "best_backup_def_contrib": round(best_backup, 2),
            "defensive_cliff_when_gobert_sits": round(g - best_backup, 2),
            "note": "points of team defense lost per 100 when Gobert is off and the best "
                    "available backup-5 plays; the fragility the Reid+Randle exits widen"}


def main():
    out = {"survival_fraction": {"center": SURV, "band": [SURV_LO, SURV_HI]}, "forks": {}}
    for which in ["rapm", "box"]:
        out["forks"][which] = {
            "LaMelo_in": lamelo_transport(which),
            "Reid_out": departing("Naz Reid", which),
            "Randle_out": departing("Julius Randle", which),
            "Green_in": importing("Josh Green", which),
            "Gueye_in": importing("Mouhamed Gueye", which),
            "gobert_fragility": gobert_fragility(which),
        }
    # defensive fork divergence summary (RAPM def-contrib minus box def-contrib)
    div = {}
    for n in ["LaMelo Ball", "Naz Reid", "Julius Randle", "Rudy Gobert", "Anthony Edwards",
              "Jaden McDaniels", "Josh Green"]:
        dr = fork(n, "rapm")["def_contrib"]
        db = fork(n, "box")["def_contrib"]
        div[n] = {"rapm_def_contrib": dr, "box_def_contrib": db, "fork_gap": round(dr - db, 2)}
    out["defensive_fork_divergence"] = div
    OUT.write_text(json.dumps(out, indent=2))

    # console summary
    print("=== LaMelo transported net (the decision-relevant number) ===")
    for which in ["rapm", "box"]:
        lm = out["forks"][which]["LaMelo_in"]
        print(f"  [{which:4}] raw net {lm['raw']['net']:+.2f} (off {lm['raw']['off']:+.2f}, "
              f"def {lm['raw']['def_contrib']:+.2f})")
        print(f"         A (0.75 on net):  center {lm['A_surv_on_net']['net_center']:+.2f} "
              f"band {lm['A_surv_on_net']['net_band']}")
        print(f"         B (0.75 on off):  center {lm['B_surv_on_off']['net_center']:+.2f} "
              f"band {lm['B_surv_on_off']['net_band']}  implied net-survival "
              f"{lm['B_surv_on_off']['implied_net_survival']}")
    print("\n=== Reid / Randle departing (impact MIN loses) ===")
    for which in ["rapm", "box"]:
        ro = out["forks"][which]["Reid_out"]["impact_lost_net"]
        ra = out["forks"][which]["Randle_out"]["impact_lost_net"]
        print(f"  [{which:4}] Reid-out net lost {ro:+.2f}   Randle-out net lost {ra:+.2f}")
    print("\n=== Gobert fragility (defensive cliff when he sits) ===")
    for which in ["rapm", "box"]:
        gf = out["forks"][which]["gobert_fragility"]
        print(f"  [{which:4}] Gobert def {gf['gobert_def_contrib']:+.2f}, best backup "
              f"{gf['best_backup_def_contrib']:+.2f}, cliff {gf['defensive_cliff_when_gobert_sits']:+.2f}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
