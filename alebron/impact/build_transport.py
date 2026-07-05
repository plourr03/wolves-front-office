"""
Transport layer (alebron / LeBron-to-MIN): adjust LeBron's imported impact for the move
into MIN's context AND the year-ahead age decline, under BOTH metric forks. Mirrors
lamelo/impact/build_transport.py but with the operationalization CHANGED for a documented
reason (this is the alebron analogue of the LaMelo Amendment-3 operationalization ruling).

WHY LeBron transports differently from LaMelo (the locked operationalization):

  LaMelo's value was OFFENSE-CONCENTRATED (raw RAPM off +4.18), so a survival fraction on
  OFFENSE isolated the usage/leverage risk on his own number. LeBron at 41 is the opposite:
  his RAPM OFFENSE is essentially zero (-0.18) and his value is diffuse (measured defense,
  connective playmaking, all-around net +1.27). Applying a survival fraction < 1 to a
  NEGATIVE offense number would perversely move it toward zero and RAISE his net. Nonsense.
  So for LeBron the retention factor is applied to NET (operationalization A). Documented so
  the fork choice is legible, not hidden.

The single widest term (LaMelo's analogue was the 0.75 survival fraction):
  RETENTION = age-and-role retention on NET impact, center 0.80, band [0.55, 1.00].
  Decomposition (reported, not smeared into one opaque number):
    - CONTEXT transfer ~ neutral (unlike LaMelo's big haircut): LeBron's raw already comes
      from a competitive, high-leverage, playoff LA context, so there is NO leverage penalty
      to apply (that was most of LaMelo's haircut). Usage compresses (tertiary behind Edwards
      and Ball), but lower usage tends to preserve per-possession value and LeBron is an
      elite off-ball cutter/passer; teammate quality rises (Gobert lobs, Edwards gravity).
    - AGE decline is the dominant term: the measured +1.27 is an age-40/41 (2025-26) number;
      2026-27 is his age-41-turning-42 season (b. 1984-12-30), unprecedented. Center docks
      ~20% for the year-ahead cliff; the band admits 'defies age again' (1.00) and 'the
      cliff/injury arrives' (0.55).
  AVAILABILITY (games/minutes on the floor) is handled SEPARATELY, in the rotation minutes
  (team-strength layer) and as the catastrophic-regret tail, NOT as a per-minute haircut.
  It is the load-bearing fork (see sweep_lebron_availability.py), the analogue of the Gueye
  fork in the LaMelo audit.

Output: alebron/data/impact/transport.json
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
IMP = REPO / "alebron" / "data" / "impact" / "player_impact.csv"
OUT = REPO / "alebron" / "data" / "impact" / "transport.json"

RET, RET_LO, RET_HI = 0.80, 0.55, 1.00  # committed age-and-role retention factor + band

imp = pd.read_csv(IMP).set_index("player_name")


def fork(name, which):
    r = imp.loc[name]
    if which == "rapm":
        off, defp, net = float(r.off_rapm), -float(r.def_rapm), float(r.net_rapm)
    else:
        off, defp, net = float(r.box_off_prior), -float(r.box_def_prior), float(r.box_net_bpm)
    return {"off": round(off, 2), "def_contrib": round(defp, 2), "net": round(net, 2)}


def lebron_transport(which):
    raw = fork("LeBron James", which)
    net_center = round(RET * raw["net"], 2)
    net_band = [round(RET_LO * raw["net"], 2), round(RET_HI * raw["net"], 2)]
    b_off = RET * raw["off"]
    b_net = round(b_off + raw["def_contrib"], 2)   # what survival-on-off WOULD give (rejected)
    return {
        "raw": raw,
        "A_retention_on_net": {"net_center": net_center, "net_band": net_band,
                               "def_contrib_carried": raw["def_contrib"]},
        "B_survival_on_off_REJECTED": {
            "net_center": b_net,
            "why_rejected": "RAPM offense is ~0/negative; a <1 factor on it moves net the WRONG "
                            "way. B is only sensible for an offense-concentrated player (LaMelo)."},
    }


def gobert_fragility(which):
    """Unchanged from the LaMelo build: LeBron does NOT fix rim protection behind Gobert.
    He can play emergency small-ball 4/5 minutes but is not a backup-5 rim anchor."""
    g = fork("Rudy Gobert", which)["def_contrib"]
    backups = {n: fork(n, which)["def_contrib"] for n in ["Mouhamed Gueye", "Joan Beringer"]}
    best_backup = max(backups.values())
    return {"gobert_def_contrib": g, "backup5_def_contrib": backups,
            "best_backup_def_contrib": round(best_backup, 2),
            "defensive_cliff_when_gobert_sits": round(g - best_backup, 2),
            "note": "LeBron does not address this; he is not a rim protector. The Reid+Randle "
                    "exits opened this cliff and adding LeBron leaves it open."}


def main():
    out = {"retention_factor": {"center": RET, "band": [RET_LO, RET_HI],
                                "applies_to": "NET (operationalization A); see module docstring"},
           "forks": {}}
    for which in ["rapm", "box"]:
        out["forks"][which] = {"LeBron_in": lebron_transport(which),
                               "gobert_fragility": gobert_fragility(which)}
    div = {}
    for n in ["LeBron James", "Rudy Gobert", "Anthony Edwards", "LaMelo Ball",
              "Jaden McDaniels", "Josh Green"]:
        dr = fork(n, "rapm")["def_contrib"]
        db = fork(n, "box")["def_contrib"]
        div[n] = {"rapm_def_contrib": dr, "box_def_contrib": db, "fork_gap": round(dr - db, 2)}
    out["defensive_fork_divergence"] = div
    OUT.write_text(json.dumps(out, indent=2))

    print("=== LeBron transported net (the decision-relevant number) ===")
    for which in ["rapm", "box"]:
        lb = out["forks"][which]["LeBron_in"]
        A = lb["A_retention_on_net"]
        print(f"  [{which:4}] raw net {lb['raw']['net']:+.2f} (off {lb['raw']['off']:+.2f}, "
              f"def {lb['raw']['def_contrib']:+.2f})  ->  A(0.80 on net) center {A['net_center']:+.2f} "
              f"band {A['net_band']}   [B-rejected would give {lb['B_survival_on_off_REJECTED']['net_center']:+.2f}]")
    print("=== Gobert fragility (unchanged; LeBron does not fix it) ===")
    for which in ["rapm", "box"]:
        gf = out["forks"][which]["gobert_fragility"]
        print(f"  [{which:4}] Gobert def {gf['gobert_def_contrib']:+.2f}, best backup "
              f"{gf['best_backup_def_contrib']:+.2f}, cliff {gf['defensive_cliff_when_gobert_sits']:+.2f}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
