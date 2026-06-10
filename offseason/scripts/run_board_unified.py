#!/usr/bin/env python3
"""
run_board_unified.py  -- the CONSISTENCY PASS (rider 4): the entire board on ONE spine.

Headline treatment: age-adjusted spine + incumbent-default lineups (the acquired player
inherits the traded player's role where positionally sensible). Sensitivities, labeled:
no-aging, and (for young-player scenarios) the decline-only floor of the asymmetric band
(old-age decline is reliable -> tight; young-age improvement is a long-tail -> wide band,
floor = no improvement). Nothing cross-compares until it is all here on one spine.

    python run_board_unified.py
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
import run_f_slate as S
import run_pairs as P
import age_curve as AC

F.NS = 6000
PVROW = {r["player_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "..", "data", "player_value.csv"), encoding="utf-8"))}


def dp(scenario, imp, base, pre, dims, ar, an, replace=None, synergy=0.0):
    s = scenario
    if replace:
        s = copy.deepcopy(scenario)
        for p in s["post_rotations"]["MIN"]:
            if p["nba_player_id"] in (replace if isinstance(replace, (set, list)) else {replace}):
                p["nba_player_id"] = G.REPL_ID
    post = F.apply_trade(s, base, imp, dims, ar, an, synergy_uplift=synergy)
    return (F._sim(post, 5.5)["teams"]["MIN"]["title"] - pre) * 100


def single_ev(sc, pid, imp, base, pre, dims, ar, an):
    av = G.availability(pid)[0]
    read = PVROW.get(pid, {}).get("translation_read", "")
    po = G.PO_MULT.get(read, 0.98); um = G.usage_mult(pid, dims)
    wr = dp(sc, imp, base, pre, dims, ar, an) * po * um
    wo = dp(sc, imp, base, pre, dims, ar, an, replace=pid)
    return av * wr + (1 - av) * wo


def pair_ev(sc, gid, wid, imp, base, pre, dims, ar, an):
    ag, aw = G.availability(gid)[0], G.availability(wid)[0]
    po = 0.5 * (G.PO_MULT.get(PVROW.get(gid, {}).get("translation_read", ""), 0.98)
                + G.PO_MULT.get(PVROW.get(wid, {}).get("translation_read", ""), 0.98))
    both = dp(sc, imp, base, pre, dims, ar, an) * po
    g_only = dp(sc, imp, base, pre, dims, ar, an, replace=wid) * po
    w_only = dp(sc, imp, base, pre, dims, ar, an, replace=gid) * po
    neither = dp(sc, imp, base, pre, dims, ar, an, replace={gid, wid})
    return ag * aw * both + ag * (1 - aw) * w_only + (1 - ag) * aw * g_only + (1 - ag) * (1 - aw) * neither


def build_board(ar):
    ad = {s["slug"]: s for s in F.ad_scenarios(ar)}
    mk_B = {"name": "Markkanen-B", "slug": "mkB", "team_state_scenario": "base",
            "outgoing": [{"label": "r", "salary": 33_333_334}], "incoming": [{"label": "m", "salary": 46_113_154}],
            "override_ids": ["1628374", P.M["Randle"], P.M["Gobert"]],
            "post_rotations": {"MIN": __import__("run_cluster_sensitivity").mk_B()}}
    pairs = {}
    for pr in P.PAIRS:
        if pr["ceiling"]:
            continue
        sc, gid, wid = P.scenario_for(pr)
        pairs[pr["slug"]] = (sc, gid, wid)
    return ad, mk_B, pairs


def main():
    base_imp = A.load_impacts(); dims = B.load_dims(); G.inject_replacement(base_imp, dims)
    ar = BH.actual_top_rotations("2025-26"); an = BH.actual_team_net(2025)
    ad, mk_B, pairs = build_board(ar)

    def safe(s): return str(s).encode("ascii", "replace").decode()

    SINGLES = [("Giannis", "203507", S.make_scenario("Giannis", "203507", 58_456_566, "MIL", "F", "both"), False),
               ("AD+Kessler", "203076", ad["ad_kessler"], False),
               ("Morant", "1629630", S.make_scenario("Morant", "1629630", 42_166_510, "MEM", "G", "randle"), False),
               ("Kyrie", "202681", S.make_scenario("Kyrie", "202681", 39_491_282, "DAL", "G", "randle"), False),
               ("Markkanen-B", "1628374", mk_B, False)]
    PAIRSL = [("TreJones+Smith", "1630200", "1630188", pairs["pair_chi_tjsmith"][0], True),
              ("ONeale+Allen", "1628960", "1626220", pairs["pair_phx_shooters"][0], False),
              ("Giddey+Smith", "1630581", "1630188", pairs["pair_chi_giddey"][0], True)]
    #                                                                              ^young (band)

    spines = {"AGED (headline)": AC.aged_impacts(base_imp),
              "no-age (sens.)": base_imp,
              "aged decline-only (band floor)": AC.aged_impacts(base_imp, decline_only=True)}
    board = {}
    for label, imp in spines.items():
        base = E.build_2026_27_league(imp); pre = F._sim(base, 5.5)["teams"]["MIN"]["title"]
        # decline-only only needed for young scenarios; skip the rest there
        for nm, pid, sc, young in SINGLES:
            if "decline-only" in label and not young:
                continue
            board.setdefault(nm, {})[label] = single_ev(sc, pid, imp, base, pre, dims, ar, an)
        for nm, gid, wid, sc, young in PAIRSL:
            if "decline-only" in label and not young:
                continue
            board.setdefault(nm, {})[label] = pair_ev(sc, gid, wid, imp, base, pre, dims, ar, an)
        board.setdefault("_pre", {})[label] = pre * 100

    print("=== UNIFIED BOARD (one spine): risk-adjusted dP(title), incumbent-default lineups ===")
    print(f"baseline title: aged {board['_pre']['AGED (headline)']:.2f}% vs no-age {board['_pre']['no-age (sens.)']:.2f}% (baseline DECAYS with aging)\n")
    print(f"{'target':16}{'AGED (headline)':>17}{'no-age':>10}{'young band (floor-headline)':>30}")
    order = sorted([n for n in board if n != "_pre"], key=lambda n: -board[n]["AGED (headline)"])
    for nm in order:
        b = board[nm]; head = b["AGED (headline)"]; na = b.get("no-age (sens.)")
        band = ""
        if "aged decline-only (band floor)" in b:
            band = f"[{b['aged decline-only (band floor)']:+.2f} .. {head:+.2f}]  WIDE (projection-heavy)"
        print(f"  {safe(nm):16}{head:>+16.2f}{na:>+10.2f}{band:>30}")
    print("\nNOTE: young-player scenarios (Giddey+Smith, TreJones+Smith) carry a WIDE asymmetric band")
    print("(floor = no young improvement); old-player declines are tight. Do NOT headline the band top.")


if __name__ == "__main__":
    main()
