"""
The load-bearing fork for the LeBron evaluation, the analogue of the LaMelo audit's Gueye
fork. There, one contested low-sample number (Gueye's defensive RAPM) propped up the 'wash.'
Here, the contested number is LeBron's AGE-AND-ROLE RETENTION x AVAILABILITY: a 41-turning-42
body whose year-ahead value and games-played are the least certain inputs in the model and
which, if credited at the optimistic end, do most of the work in any positive delta.

Two axes, swept jointly (mirrors sweep_gueye.py's structure):
  1. RETENTION (per-minute value): optimistic 1.00 (defies age), central 0.80, pessimistic 0.55.
  2. AVAILABILITY (minutes on the floor): full (30 mpg) vs reduced (20 mpg, freed minutes revert
     to replacement-level fill, i.e. the games/minutes he misses at 41-42).

Run: python alebron/impact/sweep_lebron_availability.py
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "alebron" / "impact"))
import build_team_strength as ts  # reuse rotations, data, shrinkage

LEBRON = "LeBron James"
RAW = {which: ts.imp.loc[LEBRON].net_rapm if which == "rapm" else ts.imp.loc[LEBRON].box_net_bpm
       for which in ["rapm", "box"]}
RETENTIONS = {"optimistic 1.00 (defies age)": 1.00, "central 0.80": 0.80,
              "pessimistic 0.55 (cliff)": 0.55}
AVAIL = {"full (30 mpg)": 30, "reduced (20 mpg)": 20}


def team_net_with(rotation, which, lebron_val, lebron_min):
    """Team raw net with LeBron valued at lebron_val over lebron_min minutes; the (30 - lebron_min)
    minutes he loses to availability revert to replacement-level fill."""
    tot = 0.0
    for n, m in rotation.items():
        if n == LEBRON:
            tot += lebron_val * lebron_min + ts.REPLACEMENT * (30 - lebron_min)
        else:
            tot += ts.player_net(n, which) * m
    return tot / 48.0


def main():
    pre = {w: ts.team_raw_net(ts.PRE, w) for w in ["rapm", "box"]}
    for which in ["rapm", "box"]:
        print(f"=== {which} fork (raw LeBron net {float(RAW[which]):+.2f}; current baseline "
              f"{pre[which]:+.3f}) ===")
        for rlab, r in RETENTIONS.items():
            val = round(r * float(RAW[which]), 3)
            row = []
            for alab, mins in AVAIL.items():
                d = team_net_with(ts.POST, which, val, mins) - pre[which]
                row.append(f"{alab}: delta {d:+.3f}")
            print(f"  retention {rlab:28} (net {val:+.2f})  ->  " + "   ".join(row))
    print("\nReading: the +LeBron delta is positive only when LeBron is credited near the optimistic")
    print("retention AND stays available. At pessimistic retention with reduced availability it goes")
    print("to ~zero or small, one contested number (his age-42 value) drives the size, exactly the")
    print("Gueye pattern. This is why the title delta is declined as not identifiable.")


if __name__ == "__main__":
    main()
