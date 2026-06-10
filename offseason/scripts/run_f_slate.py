#!/usr/bin/env python3
"""
run_f_slate.py  -- Component F fan-out across the reported names + gettable vets.

Each target runs through F by its REALISTIC matching path, reported under every impact
view (consensus / box / rapm / darko-where-available), exactly like the AD runs, so the
metric-dependent verdicts are visible:

  - frontcourt-replacing bigs (Giannis, Zion): BOTH-OUT (Gobert+Randle out, like AD).
  - orchestrators / wings / stretch (Morant, Kyrie, Trae, Markkanen, MPJ, Quickley,
    Giddey, DeRozan): RANDLE-OUT keeping Gobert (gutting the frontcourt for a guard is
    not the real move; adding them next to Gobert is).
  - Morant gets the keep-Gobert-add-orchestrator SYNERGY view (below).

SYNERGY (Morant-Randle-out only, separate view, never in the headline): a bounded
PnR-partner uplift on Gobert, justified by his Utah roll-man peak with elite feeding
(Conley/Mitchell/Ingles) vs his Minnesota roll volume down 41% (postmortem Q0D). Pairing
him with an elite PnR orchestrator + lob target (Morant) restores part of that roll-man
offense. Capped at +1.0 net, applied ONLY to this archetype (elite orchestrator +
vertical-spacing roller), shown transparently as its own view.

Counterparty is modeled one-sided here (MIN only) for slate speed; the AD run confirmed
the counterparty effect is negligible when the outgoing pieces land on a non-contender.
Deep-round odds stay a slight upper bound; lean on the title band (carried from the gate).

    python run_f_slate.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_team_ratings as A          # noqa: E402
import build_rotation_model as B        # noqa: E402
import bracket_helpers as BH            # noqa: E402
import bracket_sim as E                 # noqa: E402
import apply_trade as F                 # noqa: E402

F.NS = 9000   # leaner for the slate
SYNERGY_UPLIFT = 1.0
# Synergy applies to the historically-supported archetype only: an elite PnR ORCHESTRATOR
# who would feed Gobert's vertical roll. Apples-to-apples: if Morant+Gobert gets the uplift,
# so do the other elite orchestrators kept alongside Gobert. Kyrie/Trae are elite PnR
# creators; Giddey is a genuine playmaker but a lesser scoring-gravity/lob threat (flagged).
ORCHESTRATORS = {"Morant", "Kyrie", "Trae", "Giddey"}

MIN_IDS = {"Edwards": "1630162", "Dosunmu": "1630245", "McDaniels": "1630183",
           "Randle": "203944", "Gobert": "203497", "Naz": "1629675", "Conley": "201144",
           "Shannon": "1630545", "Beringer": "1642866", "Phillips": "1641763"}


def _r(pid, role): return {"nba_player_id": pid, "role": role}


def randle_out_rotation(tid, pos):
    M = MIN_IDS
    if pos == "G":   # target joins the backcourt; Naz to the 4, Gobert stays
        return [_r(M["Edwards"], "starter"), _r(tid, "starter"), _r(M["McDaniels"], "starter"),
                _r(M["Naz"], "starter"), _r(M["Gobert"], "starter"), _r(M["Dosunmu"], "sixth"),
                _r(M["Conley"], "rotation"), _r(M["Shannon"], "rotation"), _r(M["Phillips"], "deep")]
    return [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
            _r(tid, "starter"), _r(M["Gobert"], "starter"), _r(M["Naz"], "sixth"),
            _r(M["Conley"], "rotation"), _r(M["Shannon"], "rotation"), _r(M["Phillips"], "deep")]


def both_out_rotation(tid):
    M = MIN_IDS
    return [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
            _r(tid, "starter"), _r(M["Naz"], "starter"), _r(M["Conley"], "sixth"),
            _r(M["Shannon"], "rotation"), _r(M["Beringer"], "rotation"), _r(M["Phillips"], "deep")]


# target: (name, id, salary, team, pos, path)
TARGETS = [
    ("Giannis",   "203507",  58_456_566, "MIL", "F", "both"),
    ("Zion",      "1629627", 42_166_510, "NOP", "F", "both"),
    ("Morant",    "1629630", 42_166_510, "MEM", "G", "randle"),
    ("Kyrie",     "202681",  39_491_282, "DAL", "G", "randle"),
    ("Trae",      "1629027", 48_967_380, "WAS", "G", "randle"),
    ("Markkanen", "1628374", 46_113_154, "UTA", "F", "randle"),
    ("MPJ",       "1629008", 38_000_000, "BKN", "F", "randle"),
    ("Quickley",  "1630193", 32_500_000, "TOR", "G", "randle"),
    ("Giddey",    "1630581", 25_000_000, "CHI", "G", "randle"),
    ("DeRozan",   "201942",  25_740_000, "SAC", "F", "randle"),
]


def make_scenario(name, tid, sal, team, pos, path):
    if path == "both":
        outgoing = [{"label": "Gobert", "salary": 36_500_000}, {"label": "Randle", "salary": 33_333_334}]
        rot = both_out_rotation(tid)
        ov = [tid, MIN_IDS["Gobert"], MIN_IDS["Randle"]]
        note = f"both-out (Gobert+Randle $69.8M out) for {name} (${sal/1e6:.1f}M)"
    else:  # randle-out, keep Gobert (filler to clear matching for pricier targets)
        outgoing = [{"label": "Randle", "salary": 33_333_334}, {"label": "filler", "salary": 9_000_000}]
        rot = randle_out_rotation(tid, pos)
        ov = [tid, MIN_IDS["Randle"], MIN_IDS["Gobert"]]
        note = f"Randle-out keep-Gobert (Randle + ~$9M filler) for {name} (${sal/1e6:.1f}M)"
    return {"name": f"{name} ({path})", "slug": f"slate_{name.lower()}", "team_state_scenario": "base",
            "outgoing": outgoing, "incoming": [{"label": name, "salary": sal}],
            "salary_note": note, "override_ids": ov, "post_rotations": {"MIN": rot}}


def main():
    imp = A.load_impacts()
    dims = B.load_dims()
    actual_rot = BH.actual_top_rotations("2025-26")
    actual_net = BH.actual_team_net(2025)

    def safe(s): return str(s).encode("ascii", "replace").decode()

    # shared consensus baseline: per-sigma pre-band (so dP bands always contain the headline)
    base_c = E.build_2026_27_league(imp)
    pre_band = {sg: F._sim(base_c, sg)["teams"]["MIN"]["title"] for sg in F.SIGMA_BAND}
    pre_title = pre_band[5.5]
    cond_pre = E.conditional_series("MIN", base_c, use_overlay=True)
    print(f"MIN baseline (consensus, no trade): net {base_c['MIN']['net']:+.2f}, title {pre_title*100:.2f}%, "
          f"reach-CF {F._sim(base_c,5.5)['teams']['MIN']['cf']*100:.1f}%\n")

    header = (f"{'target':10}{'path':8}{'feas':6}{'cons':>8}{'cons band':>13}"
              f"{'box':>7}{'rapm':>7}{'darko':>7}{'syn*':>7}{'sign':>7}{'vsOKC':>7}{'vsSAS':>7}")
    print(header)
    print("  (dP title in pp; cons band = min/max of per-sigma deltas; syn* = +synergy view, orchestrators only; "
          "sign = metric-view agreement)")
    for (name, tid, sal, team, pos, path) in TARGETS:
        sc = make_scenario(name, tid, sal, team, pos, path)
        fz = F.feasibility(sc)
        post_c = F.apply_trade(sc, base_c, imp, dims, actual_rot, actual_net)
        post_band = {sg: F._sim(post_c, sg)["teams"]["MIN"]["title"] for sg in F.SIGMA_BAND}
        clo, cmid, chi = F.dp_band(pre_band, post_band)
        views = {"consensus": cmid * 100}
        for v in ["box", "rapm", "darko"]:
            if v == "darko" and not (F._DARKO and any(p in F._DARKO for p in sc["override_ids"])):
                continue
            imp_v = F.build_impacts_view(v, sc["override_ids"], imp)
            base_v = E.build_2026_27_league(imp_v)
            post_v = F.apply_trade(sc, base_v, imp_v, dims, actual_rot, actual_net)
            rp = F._sim(base_v, 5.5); rq = F._sim(post_v, 5.5)
            views[v] = (rq["teams"]["MIN"]["title"] - rp["teams"]["MIN"]["title"]) * 100
        # synergy view (orchestrators kept alongside Gobert only) -- separate, never headline
        syn = ""
        if path == "randle" and name in ORCHESTRATORS:
            post_syn = F.apply_trade(sc, base_c, imp, dims, actual_rot, actual_net, synergy_uplift=SYNERGY_UPLIFT)
            syn_dp = (F._sim(post_syn, 5.5)["teams"]["MIN"]["title"] - pre_title) * 100
            syn = f"{syn_dp:+.2f}"
        cond_post = E.conditional_series("MIN", post_c, use_overlay=True)
        dvsokc = (cond_post["OKC"] - cond_pre["OKC"]) * 100
        dvssas = (cond_post["SAS"] - cond_pre["SAS"]) * 100
        metric_views = [views[k] for k in ("consensus", "box", "rapm", "darko") if k in views]
        flip = min(metric_views) < 0 < max(metric_views)
        print(f"{safe(name):10}{path:8}{str(fz.get('legal'))[:5]:6}"
              f"{views['consensus']:>+7.2f}{(str(round(clo*100,1))+'/'+str(round(chi*100,1))):>13}"
              f"{views.get('box',0):>+7.2f}{views.get('rapm',0):>+7.2f}"
              f"{views.get('darko',float('nan')):>+7.2f}{syn:>7}{'FLIP' if flip else 'same':>7}"
              f"{dvsokc:>+6.1f}{dvssas:>+6.1f}")
    print("  * synergy is a SEPARATE sensitivity (bounded +1.0 net PnR uplift on Gobert), not in the headline.")

    # ---- Kyrie keep-Gobert: explicit cap construction (version A vs B) ----
    M = MIN_IDS
    print("\n=== Kyrie keep-Gobert: cap construction (the Dosunmu take-back-more conflict) ===")
    print("  Kyrie $39.5M in vs Randle $33.3M out = +$6.2M taken back. Per CBA, a sub-apron team taking")
    print("  back MORE is hard-capped at the first apron ($209.1M). (evaluate_move models only exception-")
    print("  triggered hard caps, so it under-reports this; the trade is legal but the SEASON hard cap binds.)")
    print("  Base apron salary $194.0M; first apron $209.1M; Dosunmu re-sign ~$16.5M (Bird).")
    verA = [_r(M["Edwards"], "starter"), _r("202681", "starter"), _r(M["McDaniels"], "starter"),
            _r(M["Naz"], "starter"), _r(M["Gobert"], "starter"), _r(M["Dosunmu"], "sixth"),
            _r(M["Shannon"], "rotation"), _r(M["Beringer"], "rotation"), _r(M["Phillips"], "deep")]
    verB = [_r(M["Edwards"], "starter"), _r("202681", "starter"), _r(M["McDaniels"], "starter"),
            _r(M["Naz"], "starter"), _r(M["Gobert"], "starter"), _r(M["Conley"], "sixth"),
            _r(M["Shannon"], "rotation"), _r(M["Beringer"], "rotation"), _r(M["Phillips"], "deep")]
    for label, rot, capnote in [
        ("A: keep Dosunmu (send Randle+Conley)", verA,
         "send Randle+Conley ($44.1M out) > Kyrie in -> NO take-back-more, NO hard cap; +Dosunmu -> ~$205.9M, "
         "under the first apron. Dosunmu SURVIVES; Conley is the cost."),
        ("B: lose Dosunmu (send Randle only)", verB,
         "send Randle only -> take back +$6.2M -> first-apron hard cap $209.1M; land $200.2M, only $8.93M room "
         "-> Dosunmu (~$16.5M) does NOT fit. Dosunmu LOST (or a <=$9M replacement); Conley kept."),
    ]:
        sc = {"name": f"Kyrie {label}", "slug": "kyrie_" + label[0], "team_state_scenario": "base",
              "outgoing": [{"label": "pkg", "salary": 39_491_282}], "incoming": [{"label": "Kyrie", "salary": 39_491_282}],
              "override_ids": ["202681", M["Randle"], M["Gobert"]], "post_rotations": {"MIN": rot}}
        post = F.apply_trade(sc, base_c, imp, dims, actual_rot, actual_net)
        post_band = {sg: F._sim(post, sg)["teams"]["MIN"]["title"] for sg in F.SIGMA_BAND}
        clo, cmid, chi = F.dp_band(pre_band, post_band)
        post_syn = F.apply_trade(sc, base_c, imp, dims, actual_rot, actual_net, synergy_uplift=SYNERGY_UPLIFT)
        syn_dp = (F._sim(post_syn, 5.5)["teams"]["MIN"]["title"] - pre_title) * 100
        print(f"\n  {label}: MIN net {post['MIN']['net']:+.2f} | consensus dP {cmid*100:+.2f}pp "
              f"(band {clo*100:+.2f}/{chi*100:+.2f}) | +synergy {syn_dp:+.2f}pp")
        print(f"      cap: {capnote}")


if __name__ == "__main__":
    main()
