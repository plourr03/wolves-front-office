#!/usr/bin/env python3
"""
apply_trade.py  -- Championship layer, Component F (two-sided trade application).

Applies a trade to BOTH sides, re-rates each through the same anchored pipeline as the
baseline (regressed measured net + realigned roster-change delta), and runs the bracket
sim pre/post to produce title equity. Every scenario is reported under MULTIPLE IMPACT
VIEWS, because a trade's verdict is often a referendum between our RAPM and the box:

  - consensus : the calibrated, defense-weighted RAPM+box blend (the headline).
  - box       : the traded players valued by Basketball-Reference BPM (box-first).
  - rapm      : the traded players valued by our possession RAPM.
  - darko     : optional fourth methodology, hand-entered from the public app, if it
                lands, used as the tiebreaker for metric-divergent players.
  - synergy   : OPTIONAL, scenario-specific. A bounded, documented PnR-partner uplift,
                shown as a SEPARATE view (never baked into the headline) and applied only
                to the historically-supported archetype (elite orchestrator + vertical roller).

Each view overrides ONLY the traded (divergent) players; the rest of the league stays on
consensus, so the spread across views isolates how much THIS trade's verdict depends on
which metric you trust.

DEEP-ROUND CAVEAT: the resolver is ~3pp too favorite-confident at the smallest net gaps,
so MIN's CF/Finals series odds are a slight UPPER bound. Lean on the title band.

    python apply_trade.py            # the Anthony Davis family (straight + two companions)
"""

import os
import sys
import csv
import copy

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
sys.path.insert(0, HERE)
import build_team_ratings as A          # noqa: E402
import build_rotation_model as B        # noqa: E402
import bracket_helpers as BH            # noqa: E402
import bracket_sim as E                 # noqa: E402
import evaluate_move as EM              # noqa: E402

NS = 14000
SIGMA_BAND = [4.5, 5.5, 6.5]
VIEWS_DEFAULT = ["consensus", "box", "rapm"]
_PV = None


def _load_darko():
    """{player_id: {o, d}} from the full-league DARKO leaderboard CSV (current values),
    matched by normalized name to the value-layer player_id. Falls back to the hand-pulled
    json if the CSV is absent. o = ODPM, d = DDPM (both higher=better; build_impacts_view
    sets def = -d since our def is lower=better)."""
    import unicodedata
    import re

    def norm(n):
        n = unicodedata.normalize("NFKD", str(n or ""))
        n = "".join(c for c in n if not unicodedata.combining(c))
        n = n.lower().replace(".", "").replace("'", "").replace("-", " ")
        n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
        return re.sub(r"\s+", " ", n).strip()

    csvp = os.path.join(DATA, "darko-dpm-leaderboard.csv")
    if os.path.exists(csvp):
        name2id = {norm(r["player_name"]): r["player_id"]
                   for r in csv.DictReader(open(os.path.join(DATA, "player_value.csv"), encoding="utf-8"))}
        out = {}
        for r in csv.DictReader(open(csvp, encoding="utf-8-sig")):
            pid = name2id.get(norm(r["Player"]))
            if pid:
                out[pid] = {"o": float(r["ODPM"].replace("+", "")), "d": float(r["DDPM"].replace("+", "")),
                            "rank": int(r["#"]), "surplus": r["Surplus Value"]}
        return out
    p = os.path.join(DATA, "darko_dpm.json")
    if os.path.exists(p):
        import json
        return json.load(open(p, encoding="utf-8"))["darko"]
    return None


_DARKO = _load_darko()


def safe(s): return str(s).encode("ascii", "replace").decode()


def pv():
    global _PV
    if _PV is None:
        _PV = {r["player_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "player_value.csv"), encoding="utf-8"))}
    return _PV


def build_impacts_view(view, override_ids, base_imp):
    """Return an impacts dict where ONLY override_ids are revalued per `view`."""
    if view == "consensus":
        return base_imp
    imp = copy.deepcopy(base_imp)
    P = pv()
    for pid in override_ids:
        if pid not in imp or pid not in P:
            continue
        r = P[pid]
        try:
            if view == "box":
                imp[pid]["off"] = float(r["bbr_obpm"]); imp[pid]["def"] = -float(r["bbr_dbpm"])
            elif view == "rapm":
                imp[pid]["off"] = float(r["off_rapm"]); imp[pid]["def"] = float(r["def_rapm"])
            elif view == "darko" and _DARKO and pid in _DARKO:
                imp[pid]["off"] = _DARKO[pid]["o"]; imp[pid]["def"] = -_DARKO[pid]["d"]
        except (ValueError, KeyError):
            pass
    return imp


def rerate_team(ab, post_rotation, imp, dims, actual_rot, actual_net, synergy=None):
    exp = E.regress_to_expectation(actual_net[ab])
    delta = E._realigned_delta(post_rotation, actual_rot.get(ab, []), imp)
    roll = A.rollup(E.roster_to_mpg(post_rotation), imp, "rs")
    net = exp + delta + (synergy or 0.0)
    return {"net": round(net, 2), "net_sd": roll["net_sd"], "munc": roll["method_uncertainty"],
            "delta": round(delta, 2), "exp": round(exp, 2),
            "profile": B.team_profile(E.roster_to_mpg(post_rotation), dims)}


def apply_trade(scenario, base, imp, dims, actual_rot, actual_net, synergy_uplift=0.0):
    post = copy.deepcopy(base)
    for ab, rot in scenario["post_rotations"].items():
        syn = synergy_uplift if ab == "MIN" else 0.0
        post[ab] = {**post[ab], **rerate_team(ab, rot, imp, dims, actual_rot, actual_net, syn),
                    "src": "post-trade"}
    return post


def feasibility(scenario):
    const = EM.load_constants("2026-27")
    ts = EM.load_team_state("MIN", "2026-27", scenario.get("team_state_scenario", "base"))
    return EM.evaluate_move(ts, const, scenario["outgoing"], scenario["incoming"],
                            exception_used=scenario.get("exception_used", "none"))


def _sim(strengths, sigma, seed=2027):
    ep = E.load_e_params()
    E._EP = {**ep, "sigma_unobs": sigma}
    r = E.simulate_league(strengths, n_sims=NS, use_overlay=True, seed=seed)
    E._EP = ep
    return r


def _band(team, league):
    """Per-sigma title for `team` across the band, plus the central (5.5) full result."""
    res = {sg: _sim(league, sg) for sg in SIGMA_BAND}
    return {sg: res[sg]["teams"][team]["title"] for sg in SIGMA_BAND}, res[5.5]


def dp_band(pre_band, post_band):
    """Delta-P band as min/center/max of the PER-SIGMA deltas, so the band always
    contains the headline (center = the 5.5 delta). Differencing sorted endpoints does
    not guarantee that and was wrong in the first F output."""
    deltas = {sg: post_band[sg] - pre_band[sg] for sg in SIGMA_BAND}
    return min(deltas.values()), deltas[5.5], max(deltas.values())


def run_scenario(scenario, imp_base, dims, actual_rot, actual_net, views=None, synergy_uplift=0.0):
    views = views or VIEWS_DEFAULT
    if _DARKO and any(pid in _DARKO for pid in scenario["override_ids"]):
        views = views + ["darko"]
    out = [f"=== Component F: {scenario['name']} ==="]

    def emit(s=""):
        print(safe(s)); out.append(s)

    fz = feasibility(scenario)
    emit(f"FEASIBILITY: legal={fz.get('legal')} tier={fz.get('new_tier')} "
         f"hardcap={fz.get('hard_cap_tripped')} | {fz.get('failing_constraint') or 'ok'}")
    emit(f"  {scenario.get('salary_note','')}")

    # consensus first (with band + gauntlet)
    base_c = E.build_2026_27_league(imp_base)
    post_c = apply_trade(scenario, base_c, imp_base, dims, actual_rot, actual_net)
    pre_band, pre_res = _band("MIN", base_c)
    post_band, post_res = _band("MIN", post_c)
    pre_mid, post_mid = pre_band[5.5], post_band[5.5]
    dlo, dmid, dhi = dp_band(pre_band, post_band)   # min/center/max of per-sigma deltas
    emit(f"\nMIN net (consensus): {base_c['MIN']['net']:+.2f} -> {post_c['MIN']['net']:+.2f} "
         f"(d{post_c['MIN']['net']-base_c['MIN']['net']:+.2f}; core {post_c['MIN']['exp']:+.2f} + delta {post_c['MIN']['delta']:+.2f})")
    emit(f"\n{'VIEW':12}{'MIN net pre->post':>22}{'title pre->post':>22}{'dP(title)':>12}")
    emit(f"{'consensus':12}{base_c['MIN']['net']:>9.2f} ->{post_c['MIN']['net']:>9.2f}"
         f"{pre_mid*100:>11.2f}% ->{post_mid*100:>7.2f}%{(post_mid-pre_mid)*100:>+11.2f}pp")
    view_rows = [("consensus", post_mid - pre_mid)]
    for v in [x for x in views if x != "consensus"]:
        imp_v = build_impacts_view(v, scenario["override_ids"], imp_base)
        base_v = E.build_2026_27_league(imp_v)
        post_v = apply_trade(scenario, base_v, imp_v, dims, actual_rot, actual_net)
        rp = _sim(base_v, 5.5); rq = _sim(post_v, 5.5)
        dp = (rq["teams"]["MIN"]["title"] - rp["teams"]["MIN"]["title"])
        emit(f"{v:12}{base_v['MIN']['net']:>9.2f} ->{post_v['MIN']['net']:>9.2f}"
             f"{rp['teams']['MIN']['title']*100:>11.2f}% ->{rq['teams']['MIN']['title']*100:>7.2f}%{dp*100:>+11.2f}pp")
        view_rows.append((v, dp))
    if synergy_uplift:
        post_s = apply_trade(scenario, base_c, imp_base, dims, actual_rot, actual_net, synergy_uplift)
        rq = _sim(post_s, 5.5)
        dp = rq["teams"]["MIN"]["title"] - pre_mid
        emit(f"{'synergy*':12}{base_c['MIN']['net']:>9.2f} ->{post_s['MIN']['net']:>9.2f}"
             f"{pre_mid*100:>11.2f}% ->{rq['teams']['MIN']['title']*100:>7.2f}%{dp*100:>+11.2f}pp")
        emit(f"  * synergy = base consensus + bounded PnR-partner uplift (+{synergy_uplift:.2f} net on Gobert), "
             f"a SEPARATE sensitivity, not baked into the headline.")

    pre_s, post_s = sorted(pre_band.values()), sorted(post_band.values())
    emit(f"\nTitle band (consensus, sigma 4.5-6.5): pre {pre_s[0]*100:.2f}-{pre_mid*100:.2f}-{pre_s[-1]*100:.2f}%  "
         f"-> post {post_s[0]*100:.2f}-{post_mid*100:.2f}-{post_s[-1]*100:.2f}%")
    emit(f"dP(title) BAND (min/center/max of per-sigma deltas): {dlo*100:+.2f} / {dmid*100:+.2f} / {dhi*100:+.2f} pp  (center always inside)")
    emit(f"MIN reach-CF: {pre_res['teams']['MIN']['cf']*100:.1f}% -> {post_res['teams']['MIN']['cf']*100:.1f}%")
    for cav in scenario.get("caveats", []):
        emit(f"CAVEAT: {cav}")

    # gauntlet (consensus)
    cpre = E.conditional_series("MIN", base_c, use_overlay=True)
    cpost = E.conditional_series("MIN", post_c, use_overlay=True)
    emit("\nGAUNTLET P(MIN wins series) pre->post [deep-round = upper bound]:")
    for o in ("OKC", "SAS", "BOS", "DET", "HOU", "DEN"):
        if o in cpre:
            emit(f"  vs {o}: {cpre[o]*100:.1f}% -> {cpost[o]*100:.1f}% ({(cpost[o]-cpre[o])*100:+.1f}pp)")

    verdicts = [f"{v} {d*100:+.2f}pp" for v, d in view_rows]
    emit(f"\nVERDICT (metric-dependent): {' | '.join(verdicts)}")
    flip = (min(d for _, d in view_rows) < 0 < max(d for _, d in view_rows))
    emit(f"  sign {'FLIPS across views (metric-dependent)' if flip else 'is consistent across views'}.")

    os.makedirs(os.path.join(HERE, "..", "outputs"), exist_ok=True)
    open(os.path.join(HERE, "..", "outputs", "f_" + scenario["slug"] + ".md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    return {"scenario": scenario["slug"], "views": dict(view_rows),
            "pre_mid": pre_mid, "flip": flip}


# ---------------------------------------------------------------------------
# The Anthony Davis family.
# ---------------------------------------------------------------------------
ID = {"Edwards": "1630162", "Dosunmu": "1630245", "McDaniels": "1630183",
      "Randle": "203944", "Gobert": "203497", "Naz": "1629675", "Conley": "201144",
      "Shannon": "1630545", "Beringer": "1642866", "Phillips": "1641763",
      "AD": "203076", "Kessler": "1631117", "CobyWhite": "1629632"}


def _r(pid, role): return {"nba_player_id": pid, "role": role}


def was_post(actual_rot, package_ids):
    base = [p for p in actual_rot.get("WAS", []) if p["nba_player_id"] != ID["AD"]][:7]
    return base + [_r(pid, "starter") for pid in package_ids]


def ad_scenarios(actual_rot):
    out_pkg = [ID["Gobert"], ID["Randle"]]
    common = dict(team_state_scenario="base",
                  outgoing=[{"label": "Gobert", "salary": 36_500_000}, {"label": "Randle", "salary": 33_333_334}],
                  incoming=[{"label": "Anthony Davis", "salary": 58_456_566}])
    straight = {**common, "name": "AD straight both-out (Gobert+Randle out, AD in, WAS)",
                "slug": "ad_straight", "salary_note": "$69.8M out / $58.5M in; MIN sheds ~$11.4M.",
                "override_ids": [ID["AD"], ID["Gobert"], ID["Randle"]],
                "post_rotations": {"MIN": [_r(ID["Edwards"], "starter"), _r(ID["Dosunmu"], "starter"),
                                           _r(ID["McDaniels"], "starter"), _r(ID["AD"], "starter"),
                                           _r(ID["Naz"], "starter"), _r(ID["Conley"], "sixth"),
                                           _r(ID["Shannon"], "rotation"), _r(ID["Beringer"], "rotation"),
                                           _r(ID["Phillips"], "deep")],
                                   "WAS": was_post(actual_rot, out_pkg)}}
    asset_caveat = ("The sim values the RESULTING ROSTER, not the acquisition cost. This is a TWO-trade "
                    "path, and a cheap rim-protecting 5 is exactly the piece contenders hoard, so the "
                    "realistic pick/asset cost of landing the companion is UNMODELED here until the "
                    "comp-anchored asset lens is laid over it.")
    rim5 = {**common, "name": "AD + rim-5 companion (Kessler, AD slides to the 4)",
            "slug": "ad_kessler", "salary_note": "AD via both-out + Kessler ($7.1M, fits freed room); AD at the 4, Kessler at the 5.",
            "caveats": [asset_caveat],
            "override_ids": [ID["AD"], ID["Gobert"], ID["Randle"], ID["Kessler"]],
            "post_rotations": {"MIN": [_r(ID["Edwards"], "starter"), _r(ID["Dosunmu"], "starter"),
                                       _r(ID["McDaniels"], "starter"), _r(ID["AD"], "starter"),
                                       _r(ID["Kessler"], "starter"), _r(ID["Naz"], "sixth"),
                                       _r(ID["Conley"], "rotation"), _r(ID["Shannon"], "rotation"),
                                       _r(ID["Beringer"], "deep"), _r(ID["Phillips"], "deep")],
                               "WAS": was_post(actual_rot, out_pkg)}}
    creator = {**common, "name": "AD + creator-shooter companion (Coby White on the DiVincenzo hole, AD at the 5)",
               "slug": "ad_creator", "salary_note": "AD via both-out + a creator-shooter (Coby White; UFA, would cost ABOVE the freed room -> harder to land than the rim-5).",
               "caveats": [asset_caveat.replace("a cheap rim-protecting 5", "a quality creator-shooter")
                           + " (and a UFA creator at this level realistically costs ABOVE the freed room)."],
               "override_ids": [ID["AD"], ID["Gobert"], ID["Randle"], ID["CobyWhite"]],
               "post_rotations": {"MIN": [_r(ID["Edwards"], "starter"), _r(ID["CobyWhite"], "starter"),
                                          _r(ID["McDaniels"], "starter"), _r(ID["Naz"], "starter"),
                                          _r(ID["AD"], "starter"), _r(ID["Dosunmu"], "sixth"),
                                          _r(ID["Conley"], "rotation"), _r(ID["Shannon"], "rotation"),
                                          _r(ID["Beringer"], "deep"), _r(ID["Phillips"], "deep")],
                                  "WAS": was_post(actual_rot, out_pkg)}}
    return [straight, rim5, creator]


def main():
    imp = A.load_impacts()
    dims = B.load_dims()
    actual_rot = BH.actual_top_rotations("2025-26")
    actual_net = BH.actual_team_net(2025)
    results = []
    for sc in ad_scenarios(actual_rot):
        print("\n" + "=" * 78)
        results.append(run_scenario(sc, imp, dims, actual_rot, actual_net))
    print("\n=== AD-family summary (dP title, consensus) ===")
    for r in results:
        print(f"  {r['scenario']:14} consensus {r['views']['consensus']*100:+.2f}pp | "
              f"box {r['views'].get('box',0)*100:+.2f}pp | rapm {r['views'].get('rapm',0)*100:+.2f}pp "
              f"| sign {'flips' if r['flip'] else 'consistent'}")


if __name__ == "__main__":
    main()
