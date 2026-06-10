#!/usr/bin/env python3
"""
run_bothout.py  -- THE BOTH-OUT CONTINGENCY PLAYBOOK (companion to the capstone).

Built with the portfolio machinery, not the star lane. Headline output: the GOBERT RESERVATION
PRICE -- the minimum return at which trading Gobert this summer beats running Portfolio A/C and
holding the reverse option. Because Gobert's value is the widest four-view spread in the project
(box +1.48 / DARKO +2.00 / consensus +5.28 / rapm +5.76), the threshold is stated under EACH view.

Portfolios (unified aged spine, range-anchored four-view):
  B1 asset-harvest: Gobert -> CHA (Bridges + Kalkbrenner + picks, NON-rival), Randle -> Smith,
     Beringer runway + cheap vet rim companion (solves the rim-protection trap), cap-room FA.
  B1-LAL: the same harvest sent to a RIVAL (arms LAL) -- the two-sided destination cost.
  B2 cap-space reset: drop under the $165M cap (renounce TPEs+MLE for room exception), two FA
     signings, picks in -- modeled under BOTH Dosunmu regimes (keep his hold vs renounce it).
  B3 Giannis all-in: the labeled long shot (carried from the slate).

    python run_bothout.py
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
import risk_overlay as G
import evaluate_move as EM
import age_curve as AC
import run_portfolio as RP

F.NS = 6000
M = RP.M
GOB = "203497"; SMITH = "1630188"
KALK = "1641722"   # Ryan Kalkbrenner (young rim-running C from CHA) -- resolve from value layer below
BRIDGES = None; VANDO = "1629020"
VETRIM = "VET_RIM"          # cheap min/BAE backup rim vet (modeled)
import csv
PVN = {r["player_name"]: r["player_id"] for r in csv.DictReader(open(os.path.join(HERE, "..", "data", "player_value.csv"), encoding="utf-8"))}
KALK = PVN.get("Ryan Kalkbrenner", KALK); BRIDGES = PVN.get("Miles Bridges"); VANDO = PVN.get("Jarred Vanderbilt", VANDO)


def _r(pid, role): return {"nba_player_id": pid, "role": role}


def inject(imp, dims):
    RP.inject_synthetics(imp, dims)
    imp[VETRIM] = {"off": -0.6, "def": 0.9, "off_sd": 1.4, "def_sd": 1.4, "def_div": 0.0, "read": ""}  # ~+0.3 net, D-only backup C
    dims[VETRIM] = {d: (0.62 if d == "rim_protection" else 0.42) for d in B.DIMS}


def dp(rot, imp, base, pre):
    sc = {"name": "p", "slug": "p", "team_state_scenario": "base", "outgoing": [{"label": "G", "salary": 1}],
          "incoming": [{"label": "x", "salary": 1}], "override_ids": [], "post_rotations": {"MIN": rot}}
    return (F._sim(F.apply_trade(sc, base, imp, dims, ar, an), 5.5)["teams"]["MIN"]["title"] - pre) * 100


def four_view(rot, base_imp):
    out = {}
    ov = [p["nba_player_id"] for p in rot if str(p["nba_player_id"]).isdigit()]
    for v in ["consensus", "box", "rapm", "darko"]:
        im = AC.aged_impacts(base_imp) if v == "consensus" else F.build_impacts_view(v, ov, AC.aged_impacts(base_imp))
        bse = E.build_2026_27_league(im); pre = F._sim(bse, 5.5)["teams"]["MIN"]["title"]
        out[v] = dp(rot, im, bse, pre)
    return out


def main():
    global dims, ar, an
    base_imp = A.load_impacts(); dims = B.load_dims(); G.inject_replacement(base_imp, dims); inject(base_imp, dims)
    ar = BH.actual_top_rotations("2025-26"); an = BH.actual_team_net(2025)
    aged = AC.aged_impacts(base_imp)

    # --- A/C reference (recompute A's four-view headline for the comparison) ---
    portA = next(p for p in RP.portfolios() if p["slug"] == "portA")
    aviews = four_view(portA["rot"], base_imp)
    print("REFERENCE -- Portfolio A (keep Gobert, Smith-first stack): "
          + " / ".join(f"{k} {v:+.2f}" for k, v in aviews.items()))
    print(f"  A conservative DARKO anchor = {aviews['darko']:+.2f}, consensus {aviews['consensus']:+.2f}\n")

    # --- B1 asset-harvest (Gobert -> CHA, Randle -> Smith, rim = Kalkbrenner + Beringer + vet) ---
    b1 = [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
          _r(SMITH, "starter"), _r(KALK, "starter"), _r(M["Naz"], "sixth"),
          _r(BRIDGES, "rotation"), _r(M["Beringer"], "rotation"), _r(M["Conley"], "deep"), _r(VETRIM, "deep")]
    b1v = four_view(b1, base_imp)
    print("B1 asset-harvest (Gobert->CHA; rim = Kalkbrenner + Beringer + vet committee):")
    print("  four-view: " + " / ".join(f"{k} {v:+.2f}" for k, v in b1v.items()))
    print(f"  vs A: now-EV gap (A.darko - B1.darko) = {aviews['darko']-b1v['darko']:+.2f} (DARKO view), "
          f"{aviews['consensus']-b1v['consensus']:+.2f} (consensus), {aviews['rapm']-b1v['rapm']:+.2f} (RAPM)")

    # --- two-sided destination: same harvest, but Gobert ARMS a rival (LAL) ---
    base_cha = E.build_2026_27_league(aged); pre_cha = F._sim(base_cha, 5.5)["teams"]["MIN"]["title"]
    lal = copy.deepcopy(base_cha)
    # add Gobert to LAL's rotation (arm the rival): bump LAL net by Gobert's marginal rim value
    lal_net = lal["LAL"]["net"]; lal["LAL"] = {**lal["LAL"], "net": lal_net + 2.0}   # ~aged Gobert marginal on a rim-needy team
    title_cha = F._sim(base_cha, 5.5)["teams"]["MIN"]["title"] * 100
    title_lal = F._sim(lal, 5.5)["teams"]["MIN"]["title"] * 100
    print(f"  TWO-SIDED DESTINATION: arming LAL (rival) costs MIN ~{title_lal-title_cha:+.2f}pp of title vs sending to CHA (non-rival).")

    # --- B2 cap reset: gate under BOTH Dosunmu regimes ---
    c = EM.load_constants("2026-27"); ts = EM.load_team_state("MIN", "2026-27", "base")
    shed = 38_000_000 + 33_333_334   # Gobert + Randle out for expirings/picks
    room_keep_hold = c["salary_cap"] - (ts["cap_team_salary"] - shed + 16_500_000)   # Dosunmu hold kept
    room_renounce = c["salary_cap"] - (ts["cap_team_salary"] - shed)                  # Dosunmu hold renounced
    print(f"\nB2 cap-space reset (renounce TPEs+MLE for the room exception):")
    print(f"  regime KEEP Dosunmu hold:   cap room ~${room_keep_hold:,.0f} (Bird survives, less space)")
    print(f"  regime RENOUNCE hold:        cap room ~${room_renounce:,.0f} (max space, Dosunmu walks)")
    print(f"  -> two outright FA signings + picks in; rim still a committee (the trap persists).")

    # --- RESERVATION PRICE under each view ---
    print(f"\n=== GOBERT RESERVATION PRICE (min return to beat A/C + holding the reverse option) ===")
    print(f"  Gobert four-view net: box +1.48 / DARKO +2.00 / consensus +5.28 / rapm +5.76 (widest spread in the project)")
    HOLD_OPTION = 0.5   # value of preserving the reverse option (trade-later flexibility), pp-equivalent
    for view in ["box", "darko", "consensus", "rapm"]:
        gap = aviews[view] - b1v[view]        # now-EV MIN sacrifices by trading Gobert under this view
        need = gap + HOLD_OPTION              # return must cover the now-gap PLUS the destroyed reverse option
        firsts = max(0.0, need / 0.6)         # ~0.6pp title-equity per quality first (comp-anchored, rough)
        print(f"  {view:9}: now-EV sacrificed {gap:+.2f}pp; + lost option {HOLD_OPTION:+.2f} -> return must clear ~{need:+.2f}pp "
              f"(~{firsts:.1f} quality firsts + young big), threshold {'LOW (clearable)' if need<1.0 else 'HIGH (rarely met)' if need>2.5 else 'MODERATE'}")
    print("  READ: under box/DARKO Gobert is a good-not-irreplaceable center -> a CHA-type picks+young-big return clears it;")
    print("        under RAPM his rim is near-irreplaceable -> almost no realistic return clears the bar (hold him).")


if __name__ == "__main__":
    main()
