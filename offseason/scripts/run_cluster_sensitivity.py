#!/usr/bin/env python3
"""
run_cluster_sensitivity.py  -- items 1 (rotation policy) + 2 (age curve).

Re-runs the cluster under TWO lineup policies x WITH/WITHOUT the aging prior, because the
Markkanen reconciliation showed starter assignment (Dosunmu vs Conley) swings a scenario by
~1.7 net, the same order as the gaps between cluster members.

  - incumbent-default: roles as the realistic role-based lineup assigns them (Dosunmu, the
    re-signed partner, starts; vets in defined roles).
  - model-optimal: starter minutes go to the highest-net-impact players (Conley over Dosunmu
    if the spine rates him higher).

Reports RAW consensus dP (the lineup/age effect is cleanest there; availability haircuts are
applied per-player and do not change within-scenario ordering), flags any cluster ordering that
FLIPS across the four cells, and prints the Conley/Dosunmu gap with and without aging.

    python run_cluster_sensitivity.py
"""

import os
import sys
import copy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_team_ratings as A
import build_rotation_model as B
import bracket_helpers as BH
import bracket_sim as E
import apply_trade as F
import age_curve as AC

F.NS = 8000
M = {"Edwards": "1630162", "Dosunmu": "1630245", "McDaniels": "1630183", "Randle": "203944",
     "Gobert": "203497", "Naz": "1629675", "Conley": "201144", "Shannon": "1630545",
     "Beringer": "1642866", "Phillips": "1641763"}
ROLES = ["starter", "starter", "starter", "starter", "starter", "sixth", "rotation", "rotation", "deep", "deep"]


def _r(pid, role): return {"nba_player_id": pid, "role": role}


def optimize_roles(rotation, imp):
    """model-optimal: assign roles by net-impact rank (top 5 start, etc.)."""
    def net(p):
        d = imp.get(p["nba_player_id"]); return (d["off"] - d["def"]) if d else -9
    order = sorted(rotation, key=lambda p: -net(p))
    return [{"nba_player_id": p["nba_player_id"], "role": ROLES[i] if i < len(ROLES) else "deep"}
            for i, p in enumerate(order)]


def min_baseline_rotation():   # the no-trade MIN projected rotation (incumbent roles)
    return [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
            _r(M["Randle"], "starter"), _r(M["Gobert"], "starter"), _r(M["Naz"], "sixth"),
            _r(M["Conley"], "rotation"), _r(M["Shannon"], "rotation"), _r(M["Beringer"], "deep"),
            _r(M["Phillips"], "deep")]


# cluster scenarios: name -> post rotation (incumbent roles)
def mk_A():  # keep Dosunmu, lose Naz
    return [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
            _r("1628374", "starter"), _r(M["Gobert"], "starter"), _r(M["Conley"], "sixth"),
            _r(M["Shannon"], "rotation"), _r(M["Beringer"], "rotation"), _r(M["Phillips"], "deep")]
def mk_B():  # lose Dosunmu, Conley starts
    return [_r(M["Edwards"], "starter"), _r(M["Conley"], "starter"), _r(M["McDaniels"], "starter"),
            _r("1628374", "starter"), _r(M["Gobert"], "starter"), _r(M["Naz"], "sixth"),
            _r(M["Shannon"], "rotation"), _r(M["Beringer"], "rotation"), _r(M["Phillips"], "deep")]
def tj_smith():  # Tre Jones + Jalen Smith (keep Dosunmu+Conley)
    return [_r(M["Edwards"], "starter"), _r("1630200", "starter"), _r(M["McDaniels"], "starter"),
            _r(M["Naz"], "starter"), _r(M["Gobert"], "starter"), _r("1630188", "sixth"),
            _r(M["Dosunmu"], "rotation"), _r(M["Conley"], "rotation"), _r(M["Phillips"], "deep")]
def giddey_smith():
    return [_r(M["Edwards"], "starter"), _r("1630581", "starter"), _r(M["McDaniels"], "starter"),
            _r(M["Naz"], "starter"), _r(M["Gobert"], "starter"), _r("1630188", "sixth"),
            _r(M["Dosunmu"], "rotation"), _r(M["Conley"], "rotation"), _r(M["Phillips"], "deep")]

SCN = {"Markkanen-A (lose Naz)": mk_A, "Markkanen-B (lose Dosunmu)": mk_B,
       "TreJones+Smith": tj_smith, "Giddey+Smith": giddey_smith}


def main():
    base_imp = A.load_impacts(); dims = B.load_dims()
    ar = BH.actual_top_rotations("2025-26"); an = BH.actual_team_net(2025)

    def safe(s): return str(s).encode("ascii", "replace").decode()

    # Conley/Dosunmu gap
    aged = AC.aged_impacts(base_imp, [M["Conley"], M["Dosunmu"]])
    cg = lambda im, p: im[p]["off"] - im[p]["def"]
    print("=== Conley vs Dosunmu (the rotation swing) ===")
    print(f"  no-age: Conley {cg(base_imp,M['Conley']):+.2f}  Dosunmu {cg(base_imp,M['Dosunmu']):+.2f}  gap {cg(base_imp,M['Conley'])-cg(base_imp,M['Dosunmu']):+.2f}")
    print(f"  aged  : Conley {cg(aged,M['Conley']):+.2f}  Dosunmu {cg(aged,M['Dosunmu']):+.2f}  gap {cg(aged,M['Conley'])-cg(aged,M['Dosunmu']):+.2f}")

    cells = [("default", False), ("optimal", False), ("default", True), ("optimal", True)]
    results = {name: {} for name in SCN}
    for policy, age in cells:
        imp = AC.aged_impacts(base_imp) if age else base_imp
        base_rot = min_baseline_rotation()
        if policy == "optimal":
            base_rot = optimize_roles(base_rot, imp)
        league = E.build_2026_27_league(imp)
        # override MIN baseline net with the policy-applied baseline rotation
        league["MIN"] = {**league["MIN"], **F.rerate_team("MIN", base_rot, imp, dims, ar, an)}
        pre = F._sim(league, 5.5)["teams"]["MIN"]["title"]
        for name, mkrot in SCN.items():
            rot = mkrot()
            if policy == "optimal":
                rot = optimize_roles(rot, imp)
            post = copy.deepcopy(league)
            post["MIN"] = {**post["MIN"], **F.rerate_team("MIN", rot, imp, dims, ar, an)}
            dp = (F._sim(post, 5.5)["teams"]["MIN"]["title"] - pre) * 100
            results[name][(policy, age)] = dp

    print(f"\n=== RAW consensus dP(title) by lineup policy x aging ===")
    print(f"  {'scenario':26}{'def/noage':>11}{'opt/noage':>11}{'def/age':>10}{'opt/age':>10}{'flip?':>22}")
    for name in SCN:
        r = results[name]
        vals = [r[("default", False)], r[("optimal", False)], r[("default", True)], r[("optimal", True)]]
        print(f"  {safe(name):26}{vals[0]:>+10.2f}{vals[1]:>+10.2f}{vals[2]:>+9.2f}{vals[3]:>+9.2f}", end="")
        # flag if A/B ordering or any pair ordering flips across cells (checked below)
        print()

    # ordering-flip check across the four cells
    print("\n=== ordering across cells (does the cluster rank flip?) ===")
    for policy, age in cells:
        order = sorted(SCN, key=lambda n: -results[n][(policy, age)])
        tag = f"{policy}/{'age' if age else 'noage'}"
        print(f"  {tag:14}: " + " > ".join(f"{safe(n.split()[0])}({results[n][(policy,age)]:+.1f})" for n in order))


if __name__ == "__main__":
    main()
