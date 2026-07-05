"""
Team-strength layer (alebron / LeBron-to-MIN): aggregate transported/measured player impacts
into MIN's team net, comparing the CURRENT completed post-LaMelo roster (baseline) to that
same roster PLUS LeBron (treatment), under BOTH metric forks consistently.

KEY STRUCTURAL DIFFERENCE FROM THE LAMELO BUILD: here the baseline (PRE) is NOT a run-it-back
counterfactual. It is the actual current roster (LaMelo already in, Reid/Randle already out).
So PRE here equals the LaMelo project's POST rotation, by construction, which keeps the
post-LaMelo baseline net identical to what that project used (2.183 rapm / 3.008 box after
deflation), so the two analyses chain cleanly. The treatment (POST) adds LeBron, whose minutes
come from the fill/bench spots and small trims off the starters, consistent with the cap
finding that LeBron can only be a minimum-for-minimum SWAP (he displaces near-replacement mins).

The robust quantity is the POST-minus-PRE delta (LeBron's marginal team-strength contribution);
baseline and most scaling cancel. Deflation to a true net rating happens in the sim layer.

Output: alebron/data/impact/team_strength.json
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
IMP = REPO / "alebron" / "data" / "impact" / "player_impact.csv"
TRANSPORT = json.loads((REPO / "alebron" / "data" / "impact" / "transport.json").read_text())
OUT = REPO / "alebron" / "data" / "impact" / "team_strength.json"

imp = pd.read_csv(IMP).set_index("player_name")
REPLACEMENT = -1.5   # fill/unknown players (Clark placeholder, minimums) net level; documented
SHRINK_K = 3000      # possession-weighted shrinkage toward replacement (same as LaMelo build)

# PRE equals the current completed post-LaMelo roster (identical to the LaMelo project's POST).
PRE = {
    "LaMelo Ball": 33, "Anthony Edwards": 35, "Josh Green": 27, "Jaden McDaniels": 33,
    "Rudy Gobert": 30, "Ayo Dosunmu": 28, "Mouhamed Gueye": 18, "Joan Beringer": 14,
    "_fill_clark": 16, "_fill_min": 6,
}
# POST equals + LeBron (30 mpg point-forward). His minutes come from _fill_min (the body he
# legally replaces under the hard cap), most of _fill_clark, and small trims off guards/wings.
POST = {
    "LeBron James": 30, "Anthony Edwards": 34, "LaMelo Ball": 32, "Jaden McDaniels": 32,
    "Rudy Gobert": 30, "Ayo Dosunmu": 25, "Josh Green": 21, "Mouhamed Gueye": 14,
    "Joan Beringer": 12, "_fill_clark": 10,
}


def player_net(name, which):
    if name.startswith("_fill"):
        return REPLACEMENT
    if name == "LeBron James":
        # transported (retention-adjusted) value from the transport layer; not re-shrunk
        return TRANSPORT["forks"][which]["LeBron_in"]["A_retention_on_net"]["net_center"]
    r = imp.loc[name]
    net = float(r.net_rapm) if which == "rapm" else float(r.box_net_bpm)
    poss = float(r.possessions)
    w = poss / (poss + SHRINK_K)
    return w * net + (1 - w) * REPLACEMENT


def team_raw_net(rotation, which):
    total_min = sum(rotation.values())
    assert abs(total_min - 240) < 1e-6, f"minutes sum to {total_min}, not 240"
    return sum(player_net(n, which) * m for n, m in rotation.items()) / 48.0


def main():
    out = {"replacement_level": REPLACEMENT, "rotations": {"post": POST, "pre": PRE},
           "note": "PRE = current post-LaMelo roster; POST = +LeBron. The POST-minus-PRE delta is "
                   "LeBron's marginal team-strength contribution (the robust quantity).",
           "forks": {}}
    for which in ["rapm", "box"]:
        post = team_raw_net(POST, which)
        pre = team_raw_net(PRE, which)
        out["forks"][which] = {"post_raw_net": round(post, 4), "pre_raw_net": round(pre, 4),
                               "lebron_add_delta_raw": round(post - pre, 5)}
    OUT.write_text(json.dumps(out, indent=2))

    print("Team raw net (sum of on-court impacts; pre-SCALE), and LeBron marginal delta:")
    for which in ["rapm", "box"]:
        f = out["forks"][which]
        print(f"  [{which:4}] +LeBron {f['post_raw_net']:+.3f}  current {f['pre_raw_net']:+.3f}  "
              f"LeBron add delta {f['lebron_add_delta_raw']:+.3f}")
    print("\nPer-player contribution to the +LeBron team net (net x mpg/48):")
    for which in ["rapm", "box"]:
        print(f"  [{which}]")
        for n, m in sorted(POST.items(), key=lambda kv: -player_net(kv[0], which) * kv[1]):
            print(f"      {n:18} net {player_net(n, which):+.2f} x {m}min -> {player_net(n, which)*m/48:+.3f}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
