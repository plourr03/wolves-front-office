"""
Fix 1 (audit): role-player valuation fork. The RAPM "wash" depends on crediting Gueye
(a near-minimum throw-in with the low-sample-big defensive-RAPM profile flagged unreliable
for Edey/Diabate) at his full shrunk value. Sweep Gueye across modeled / neutral(0.0) /
replacement(-1.5), report the team trade delta under both forks. Gueye is only in the
post-trade rotation, so this moves only the post side.

Run: python lamelo/impact/sweep_gueye.py
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "lamelo" / "impact"))
import build_team_strength as ts  # reuse the same rotations, data, shrinkage

GUEYE = "Mouhamed Gueye"
VALS = {"modeled (shrunk RAPM)": None, "neutral 0.0": 0.0, "replacement -1.5": -1.5}


def team_net(rotation, which, gueye_val):
    tot = 0.0
    for n, m in rotation.items():
        net = ts.player_net(n, which) if (n != GUEYE or gueye_val is None) else gueye_val
        tot += net * m
    return tot / 48.0


def main():
    for which in ["rapm", "box"]:
        modeled = ts.player_net(GUEYE, which)
        print(f"=== {which} fork (Gueye modeled value {modeled:+.3f}) ===")
        for label, v in VALS.items():
            d = team_net(ts.POST, which, v) - team_net(ts.PRE, which, v)
            print(f"  Gueye {label:22} -> trade delta {d:+.3f}")


if __name__ == "__main__":
    main()
