"""
Team-strength layer: aggregate transported/measured player impacts into MIN's team net,
post-trade vs the run-it-back baseline, under BOTH metric forks consistently (the same
metric drives every player and the aggregate within a fork; never mixed).

Rotations are DOCUMENTED and CORRECTABLE (DiVincenzo confirmed OUT, Achilles). Deep-bench
and fill players are flagged; they are low-minute and low-leverage on the result. This
produces a RAW aggregated net (sum of on-court impacts); the SCALE deflation to a true
net rating happens in the sim layer. The robust quantity is the POST-minus-PRE delta,
where the baseline and most scaling cancel.

Output: lamelo/data/impact/team_strength.json
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
IMP = REPO / "lamelo" / "data" / "impact" / "player_impact.csv"
TRANSPORT = json.loads((REPO / "lamelo" / "data" / "impact" / "transport.json").read_text())
OUT = REPO / "lamelo" / "data" / "impact" / "team_strength.json"

imp = pd.read_csv(IMP).set_index("player_name")
REPLACEMENT = -1.5   # fill/unknown players (Clark, minimums) net level; documented
SHRINK_K = 3000      # possession-weighted shrinkage toward replacement (the reliability scale)

# DOCUMENTED rotations (mpg). DiVincenzo OUT (Achilles, confirmed). Correctable.
POST = {  # post-trade MIN, hard-capped, DiVincenzo out
    "LaMelo Ball": 33, "Anthony Edwards": 35, "Josh Green": 27, "Jaden McDaniels": 33,
    "Rudy Gobert": 30, "Ayo Dosunmu": 28, "Mouhamed Gueye": 18, "Joan Beringer": 14,
    "_fill_clark": 16, "_fill_min": 6,
}
PRE = {   # run-it-back: keep Randle + Reid, no LaMelo/Green, DiVincenzo out
    "Ayo Dosunmu": 30, "Anthony Edwards": 35, "Jaden McDaniels": 33, "Julius Randle": 32,
    "Rudy Gobert": 30, "Naz Reid": 26, "Joan Beringer": 16, "_fill_min": 38,
}


def player_net(name, which):
    if name.startswith("_fill"):
        return REPLACEMENT
    if name == "LaMelo Ball":
        # transported value (already from his reliable RAPM); not re-shrunk
        return TRANSPORT["forks"][which]["LaMelo_in"]["B_surv_on_off"]["net_center"]
    r = imp.loc[name]
    net = float(r.net_rapm) if which == "rapm" else float(r.box_net_bpm)
    # possession-weighted shrinkage toward replacement: noisy low-poss bigs (Beringer,
    # and partly Gueye) regress so a small-sample artifact cannot flatter either world
    poss = float(r.possessions)
    w = poss / (poss + SHRINK_K)
    return w * net + (1 - w) * REPLACEMENT  # full precision; rounding near zero is false precision


def team_raw_net(rotation, which):
    total_min = sum(rotation.values())
    assert abs(total_min - 240) < 1e-6, f"minutes sum to {total_min}, not 240"
    return sum(player_net(n, which) * m for n, m in rotation.items()) / 48.0


def main():
    out = {"replacement_level": REPLACEMENT, "rotations": {"post": POST, "pre": PRE},
           "note": "RAW aggregated net (pre-SCALE-deflation); the POST-minus-PRE delta is the robust quantity",
           "forks": {}}
    for which in ["rapm", "box"]:
        post = team_raw_net(POST, which)
        pre = team_raw_net(PRE, which)
        out["forks"][which] = {"post_raw_net": round(post, 4), "pre_raw_net": round(pre, 4),
                               "trade_delta_raw": round(post - pre, 5)}
    OUT.write_text(json.dumps(out, indent=2))

    print("Team raw net (sum of on-court impacts; pre-SCALE), and trade delta:")
    for which in ["rapm", "box"]:
        f = out["forks"][which]
        print(f"  [{which:4}] post {f['post_raw_net']:+.2f}  pre {f['pre_raw_net']:+.2f}  "
              f"trade delta {f['trade_delta_raw']:+.2f}")
    print("\nPer-player contribution to the post-trade team net (net x mpg/48):")
    for which in ["rapm", "box"]:
        print(f"  [{which}]")
        for n, m in sorted(POST.items(), key=lambda kv: -player_net(kv[0], which) * kv[1]):
            print(f"      {n:18} net {player_net(n, which):+.2f} x {m}min -> {player_net(n, which)*m/48:+.2f}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
