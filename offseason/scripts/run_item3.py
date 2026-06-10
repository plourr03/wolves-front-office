#!/usr/bin/env python3
"""
run_item3.py  -- Randle conversions on the unified (aged, incumbent-default) spine.

  3a VALUE-EXTRACTION: Randle -> ONE trade-shooter + draft capital, then the full non-taxpayer
     MLE signs a SECOND shooter (priced as a second move). Picks go to the ASSET LENS, not
     priced here; Randle's NEGATIVE surplus (an overpaid +0.87 forward) means the sweetener
     realistically flows OUT (MIN attaches), not in.
  3b BAD-CONTRACT SWAP (5th flavor): Randle <-> another team's overpaid-but-need-fitting player
     (Jordan Poole: elite shooter off3 0.96, expiring), no picks either way. MIN gains the
     spacing the playoff field exposes + 2027 flexibility, at a net-impact downgrade.

Riders: risk-adjusted EV on the aged headline spine + no-age sensitivity; asymmetric bands;
DARKO reported where it exists (none of these acquired shooters are in the current DARKO set,
so they REST ON CONSENSUS ALONE, flagged). Cap/MLE/apron flags via evaluate_move.

    python run_item3.py
"""

import os
import sys
import copy
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_team_ratings as A
import build_rotation_model as B
import bracket_helpers as BH
import bracket_sim as E
import apply_trade as F
import risk_overlay as G
import evaluate_move as EM
import age_curve as AC

F.NS = 7000
M = {"Edwards": "1630162", "Dosunmu": "1630245", "McDaniels": "1630183", "Randle": "203944",
     "Gobert": "203497", "Naz": "1629675", "Conley": "201144", "Shannon": "1630545", "Phillips": "1641763"}
PVNAME = {r["player_name"]: r["player_id"] for r in csv.DictReader(open(os.path.join(HERE, "..", "data", "player_value.csv"), encoding="utf-8"))}
PVROW = {r["player_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "..", "data", "player_value.csv"), encoding="utf-8"))}
ALLEN = "1628960"; POOLE = PVNAME.get("Jordan Poole", "1629673"); ONEALE = "1626220"


def _r(pid, role): return {"nba_player_id": pid, "role": role}


def dp(scenario, imp, base, pre, dims, ar, an, replace=None):
    s = scenario
    if replace:
        s = copy.deepcopy(scenario)
        for p in s["post_rotations"]["MIN"]:
            if p["nba_player_id"] in (replace if isinstance(replace, set) else {replace}):
                p["nba_player_id"] = G.REPL_ID
    return (F._sim(F.apply_trade(s, base, imp, dims, ar, an), 5.5)["teams"]["MIN"]["title"] - pre) * 100


def risk_adj_pair(sc, gid, wid, imp, base, pre, dims, ar, an):
    ag, aw = G.availability(gid)[0], G.availability(wid)[0]
    po = 0.5 * (G.PO_MULT.get(PVROW.get(gid, {}).get("translation_read", ""), 0.98)
                + G.PO_MULT.get(PVROW.get(wid, {}).get("translation_read", ""), 0.98))
    both = dp(sc, imp, base, pre, dims, ar, an) * po
    g1 = dp(sc, imp, base, pre, dims, ar, an, replace=wid) * po
    w1 = dp(sc, imp, base, pre, dims, ar, an, replace=gid) * po
    nei = dp(sc, imp, base, pre, dims, ar, an, replace={gid, wid})
    return ag * aw * both + ag * (1 - aw) * w1 + (1 - ag) * aw * g1 + (1 - ag) * (1 - aw) * nei, (1 - ag) * (1 - aw)


def risk_adj_single(sc, pid, imp, base, pre, dims, ar, an):
    av = G.availability(pid)[0]; po = G.PO_MULT.get(PVROW.get(pid, {}).get("translation_read", ""), 0.98)
    um = G.usage_mult(pid, dims)
    wr = dp(sc, imp, base, pre, dims, ar, an) * po * um
    wo = dp(sc, imp, base, pre, dims, ar, an, replace=pid)
    return av * wr + (1 - av) * wo, av


def main():
    base_imp = A.load_impacts(); dims = B.load_dims(); G.inject_replacement(base_imp, dims)
    ar = BH.actual_top_rotations("2025-26"); an = BH.actual_team_net(2025)
    c = EM.load_constants("2026-27"); ts = EM.load_team_state("MIN", "2026-27", "base")

    def safe(s): return str(s).encode("ascii", "replace").decode()

    # 3a roster: Randle out, trade-shooter (Allen) + MLE-shooter (O'Neale-as-MLE-proxy) in.
    rot_3a = [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
              _r(ALLEN, "starter"), _r(M["Gobert"], "starter"), _r(ONEALE, "sixth"),
              _r(M["Naz"], "rotation"), _r(M["Conley"], "rotation"), _r(M["Phillips"], "deep")]
    sc_3a = {"name": "3a", "slug": "item3a", "team_state_scenario": "base",
             "outgoing": [{"label": "Randle", "salary": 33_333_334}],
             "incoming": [{"label": "Allen", "salary": 18_125_000}],
             "override_ids": [ALLEN, ONEALE, M["Randle"]], "post_rotations": {"MIN": rot_3a}}
    # 3b roster: Randle <-> Poole (1-for-1)
    rot_3b = [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
              _r(POOLE, "starter"), _r(M["Gobert"], "starter"), _r(M["Naz"], "sixth"),
              _r(M["Conley"], "rotation"), _r(M["Shannon"], "rotation"), _r(M["Phillips"], "deep")]
    sc_3b = {"name": "3b", "slug": "item3b", "team_state_scenario": "base",
             "outgoing": [{"label": "Randle", "salary": 33_333_334}],
             "incoming": [{"label": "Poole", "salary": 34_000_000}],
             "override_ids": [POOLE, M["Randle"]], "post_rotations": {"MIN": rot_3b}}

    # feasibility
    fz_3a_trade = EM.evaluate_move(ts, c, [{"label": "Randle", "salary": 33_333_334}], [{"label": "Allen", "salary": 18_125_000}])
    ts2 = dict(ts); ts2["apron_team_salary"] = ts["apron_team_salary"] - 33_333_334 + 18_125_000
    fz_3a_mle = EM.evaluate_move(ts2, c, [], [{"label": "MLE shooter", "salary": 15_048_000}], exception_used="full_mle")
    fz_3b = EM.evaluate_move(ts, c, [{"label": "Randle", "salary": 33_333_334}], [{"label": "Poole", "salary": 34_000_000}])

    print("=== Item 3: Randle conversions (unified aged spine; incumbent-default; DARKO where it exists) ===\n")
    for spine_lbl, imp in [("AGED (headline)", AC.aged_impacts(base_imp)), ("no-age (sens.)", base_imp)]:
        base = E.build_2026_27_league(imp); pre = F._sim(base, 5.5)["teams"]["MIN"]["title"]
        ev3a, pn = risk_adj_pair(sc_3a, ALLEN, ONEALE, imp, base, pre, dims, ar, an)
        ev3b, av = risk_adj_single(sc_3b, POOLE, imp, base, pre, dims, ar, an)
        raw3a = dp(sc_3a, imp, base, pre, dims, ar, an); raw3b = dp(sc_3b, imp, base, pre, dims, ar, an)
        print(f"[{spine_lbl}]  baseline {pre*100:.2f}%")
        print(f"  3a value-extraction (Randle->Allen + MLE shooter): raw {raw3a:+.2f} | risk-adj EV {ev3a:+.2f}pp (P both-out {pn*100:.0f}%)")
        print(f"  3b bad-contract swap (Randle<->Poole):            raw {raw3b:+.2f} | risk-adj EV {ev3b:+.2f}pp (Poole avail {av*100:.0f}%)")
        print()
    print("FEASIBILITY / CAP:")
    print(f"  3a trade (Randle->Allen): legal={fz_3a_trade['legal']} take_back_more={fz_3a_trade['take_back_more']} "
          f"-> lands ${fz_3a_trade['new_apron_team_salary']:,} ({fz_3a_trade['new_tier']}); sheds salary, UNDER apron.")
    print(f"  3a then full MLE ($15.0M): legal={fz_3a_mle['legal']} hard_cap_set={fz_3a_mle['hard_cap_set']} "
          f"-> lands ${fz_3a_mle['new_apron_team_salary']:,}; full non-taxpayer MLE PRESERVED + used, stays under the apron cap.")
    print(f"  3b swap (Randle<->Poole): legal={fz_3b['legal']} take_back_more={fz_3b['take_back_more']} "
          f"-> lands ${fz_3b['new_apron_team_salary']:,} ({fz_3b['new_tier']}); ~salary-neutral, no hard cap, keeps the rotation.")
    print("\nASSET LENS (not priced here): Randle's surplus is NEGATIVE (~-2.7: an overpaid +0.87 forward), so 3a's")
    print("  'draft capital' realistically flows OUT (MIN attaches a 2nd/late 1st to move him for a useful shooter),")
    print("  not in. 3b (bad-contract swap) is the realistic no-pick shape: trade overpaid-for-overpaid, win on FIT.")
    print("DARKO: Allen, O'Neale(MLE proxy), Poole are NOT in the current DARKO set -> these rest on CONSENSUS ALONE")
    print("  (winner's-curse caution); pending Bobby's cluster pull for corroboration.")
    print("BANDS/POLICY: shooters here are prime-age (Allen 31, O'Neale 33, Poole 27) -> tight bands; incumbent-default")
    print("  (acquired shooter starts in the vacated wing role). Model-optimal would bench the lower-net shooter (sens.).")


if __name__ == "__main__":
    main()
