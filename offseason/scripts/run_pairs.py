#!/usr/bin/env python3
"""
run_pairs.py  -- Component F/G for the Randle one-for-two DISAGGREGATION.

Trade Randle ($33.3M) for TWO durable, complementary role players (an assist-first guard +
a shooter/3-and-D wing), keeping Gobert. Construction rule: inbound sum <= $33.3M so there
is NO take-back-more hard cap and BOTH Dosunmu and Conley survive (the advantage Markkanen
and Kyrie lack). A clearly-superior over-line pair is priced hard-capped (A/B) like Kyrie.

THE THESIS (tested by G): the downside branch is much shallower than a star scenario, because
if ONE of the pair is hurt you still hold the other. G weights FOUR roster states:
  both healthy / only-guard / only-wing / neither, by each player's availability. The bad
  roster (neither) has probability (1-a1)(1-a2), which is tiny for two durable players, so
  the risk-adjusted EV should sit close to the raw dP (unlike the fragile stars, whose EV
  collapsed). Confirm or refute.

    python run_pairs.py
"""

import os
import sys
import copy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_team_ratings as A          # noqa: E402
import build_rotation_model as B        # noqa: E402
import bracket_helpers as BH            # noqa: E402
import bracket_sim as E                 # noqa: E402
import apply_trade as F                 # noqa: E402
import risk_overlay as G                # noqa: E402

F.NS = 8000
M = {"Edwards": "1630162", "Dosunmu": "1630245", "McDaniels": "1630183", "Randle": "203944",
     "Gobert": "203497", "Naz": "1629675", "Conley": "201144", "Shannon": "1630545", "Phillips": "1641763"}
PO = G.PO_MULT


def _r(pid, role): return {"nba_player_id": pid, "role": role}


def pair_rotation(guard_id, wing_id, wing_role="sixth", guard_at="guard"):
    """One-for-two: drop Randle, add guard + wing, KEEP Gobert/Dosunmu/Conley (deeper roster)."""
    if guard_at == "four":   # a point-forward (Avdija) takes Randle's 4 slot directly
        starters = [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
                    _r(guard_id, "starter"), _r(M["Gobert"], "starter")]
        bench = [_r(wing_id, wing_role), _r(M["Naz"], "rotation"), _r(M["Conley"], "rotation"), _r(M["Phillips"], "deep")]
    else:                    # a guard starts next to Edwards; Naz slides to the 4
        starters = [_r(M["Edwards"], "starter"), _r(guard_id, "starter"), _r(M["McDaniels"], "starter"),
                    _r(M["Naz"], "starter"), _r(M["Gobert"], "starter")]
        bench = [_r(wing_id, wing_role), _r(M["Dosunmu"], "rotation"), _r(M["Conley"], "rotation"), _r(M["Phillips"], "deep")]
    return starters + bench


# REALISTIC pairs only: surplus screen excludes cornerstone keeps (Avdija/Camara/Knueppel are
# high-surplus -> adverse selection, teams will not sell at par). Surfaced from sell-motivated
# teams (logjams, expirings, cost-cutters). availability tag = block-board discipline.
# (label, slug, guard(name,id,sal,avail,read), wing(...), guard_at, inbound, over, avail_tag, ceiling)
PAIRS = [
    {"label": "CHI: Tre Jones + Jalen Smith", "slug": "pair_chi_tjsmith",
     "g": ("Tre Jones", "1630200", 8_000_000, 0.75, "insufficient_po_sample"),
     "w": ("Jalen Smith", "1630188", 9_400_000, 0.71, "insufficient_po_sample"),
     "guard_at": "guard", "inbound": 17_400_000, "over": False,
     "avail_tag": "Reported/Analyst (backup PG in a guard logjam + an expiring stretch)", "ceiling": False},
    {"label": "PHX: Royce O'Neale + Grayson Allen", "slug": "pair_phx_shooters",
     "g": ("Grayson Allen", "1628960", 18_125_000, 0.73, "neutral"),     # shooter, not a true PG (note)
     "w": ("Royce O'Neale", "1626220", 10_875_000, 0.94, "neutral"),
     "guard_at": "guard", "inbound": 29_000_000, "over": False,
     "avail_tag": "Analyst (PHX second-apron cost-cutter; two durable vet shooters at/below par)", "ceiling": False},
    {"label": "CHI superior (OVER line): Giddey + Jalen Smith", "slug": "pair_chi_giddey",
     "g": ("Josh Giddey", "1630581", 25_000_000, 0.78, "insufficient_po_sample"),
     "w": ("Jalen Smith", "1630188", 9_400_000, 0.71, "insufficient_po_sample"),
     "guard_at": "guard", "inbound": 34_400_000, "over": True,
     "avail_tag": "Speculative (CHI moving its starting PG; mid-surplus)", "ceiling": False},
    {"label": "CEILING ILLUSTRATION (NOT acquirable): Avdija + Camara", "slug": "pair_ceiling_avdija",
     "g": ("Deni Avdija", "1630166", 13_100_000, 0.85, "neutral"),
     "w": ("Toumani Camara", "1641739", 18_100_000, 0.96, "insufficient_po_sample"),
     "guard_at": "four", "inbound": 31_200_000, "over": False,
     "avail_tag": "KEEP -- All-Star + 3-and-D cornerstone on value deals; HIGH surplus = adverse selection, Portland will not sell. Shown ONLY as the durable-pair ceiling.", "ceiling": True},
]
MARKKANEN_BAR = 2.00   # corrected: version B (lose Dosunmu, Conley promoted), not the infeasible +0.74


def scenario_for(pair):
    gid, wid = pair["g"][1], pair["w"][1]
    rot = pair_rotation(gid, wid, guard_at=pair["guard_at"])
    over = pair["over"]
    # under line: send Randle only (take back less, no hard cap). over line: Randle + filler, hard-capped.
    outgoing = [{"label": "Randle", "salary": 33_333_334}]
    note = (f"inbound ${pair['inbound']/1e6:.1f}M <= Randle $33.3M -> NO take-back-more, NO hard cap, "
            f"Dosunmu AND Conley both kept" if not over else
            f"inbound ${pair['inbound']/1e6:.1f}M > $33.3M -> take-back-more first-apron hard cap (price A/B)")
    return {"name": pair["label"], "slug": pair["slug"], "team_state_scenario": "base",
            "outgoing": outgoing, "incoming": [{"label": pair["g"][0], "salary": pair["g"][2]},
                                               {"label": pair["w"][0], "salary": pair["w"][2]}],
            "salary_note": note, "override_ids": [gid, wid, M["Randle"]],
            "post_rotations": {"MIN": rot}}, gid, wid


def four_state_ev(sc, gid, wid, ag, aw, base_c, imp, dims, ar, an, pomul):
    """Risk-adjusted EV weighting four roster states by the two availabilities."""
    def dp(replace):
        s = copy.deepcopy(sc)
        for p in s["post_rotations"]["MIN"]:
            if p["nba_player_id"] in replace:
                p["nba_player_id"] = G.REPL_ID
        post = F.apply_trade(s, base_c, imp, dims, ar, an)
        return (F._sim(post, 5.5)["teams"]["MIN"]["title"] - PRE) * 100
    both = dp(set()) * pomul
    g_only = dp({wid}) * pomul      # wing hurt, guard plays
    w_only = dp({gid}) * pomul      # guard hurt, wing plays
    neither = dp({gid, wid})        # both hurt -> bad roster
    ev = ag * aw * both + ag * (1 - aw) * w_only + (1 - ag) * aw * g_only + (1 - ag) * (1 - aw) * neither
    return ev, both, g_only, w_only, neither, (1 - ag) * (1 - aw)


PRE = None


def main():
    global PRE
    imp = A.load_impacts(); dims = B.load_dims(); G.inject_replacement(imp, dims)
    ar = BH.actual_top_rotations("2025-26"); an = BH.actual_team_net(2025)
    base_c = E.build_2026_27_league(imp)
    PRE = F._sim(base_c, 5.5)["teams"]["MIN"]["title"]

    def safe(s): return str(s).encode("ascii", "replace").decode()
    print(f"=== Randle one-for-two DISAGGREGATION (baseline title {PRE*100:.2f}%; Markkanen bar +{MARKKANEN_BAR:.2f}) ===\n")
    rows = []
    for pair in PAIRS:
        sc, gid, wid = scenario_for(pair)
        fz = F.feasibility(sc)
        # F: four views (consensus band + box/rapm/darko central)
        post = F.apply_trade(sc, base_c, imp, dims, ar, an)
        preb, _ = F._band("MIN", base_c); postb, _ = F._band("MIN", post)
        clo, cmid, chi = F.dp_band(preb, postb)
        views = {"consensus": cmid * 100}
        for v in ["box", "rapm", "darko"]:
            if v == "darko" and not any(p in F._DARKO for p in sc["override_ids"]):
                views[v] = None; continue
            iv = F.build_impacts_view(v, sc["override_ids"], imp)
            bv = E.build_2026_27_league(iv); pv2 = F.apply_trade(sc, bv, iv, dims, ar, an)
            views[v] = (F._sim(pv2, 5.5)["teams"]["MIN"]["title"] - F._sim(bv, 5.5)["teams"]["MIN"]["title"]) * 100
        cond = E.conditional_series("MIN", post, use_overlay=True)
        cpre = E.conditional_series("MIN", base_c, use_overlay=True)
        # G: four-state risk-adjusted EV
        ag, aw = pair["g"][3], pair["w"][3]
        pomul = 0.5 * (PO.get(pair["g"][4], 0.98) + PO.get(pair["w"][4], 0.98))
        ev, both, g_only, w_only, neither, p_neither = four_state_ev(sc, gid, wid, ag, aw, base_c, imp, dims, ar, an, pomul)
        rows.append((pair, views, (clo, cmid, chi), ev, both, neither, p_neither, ag, aw, fz, cond, cpre))

        print(f"--- {safe(pair['label'])} ---")
        print(f"  AVAILABILITY: {safe(pair['avail_tag'])}")
        print(f"  FEASIBILITY: legal={fz.get('legal')} take_back_more={fz.get('take_back_more')} "
              f"hard_cap_set={fz.get('hard_cap_set')} | {sc['salary_note']}")
        vv = "  ".join(f"{k} {views[k]:+.2f}" for k in ('consensus', 'box', 'rapm', 'darko') if views.get(k) is not None)
        print(f"  RAW F dP(title): {vv}   band {clo*100:+.2f}/{chi*100:+.2f}")
        print(f"  gauntlet: vs OKC {(cond['OKC']-cpre['OKC'])*100:+.1f}pp, vs SAS {(cond['SAS']-cpre['SAS'])*100:+.1f}pp")
        print(f"  G four-state (avail guard {ag*100:.0f}%, wing {aw*100:.0f}%): both {both:+.2f} | one-out ~{(g_only+w_only)/2:+.2f} | "
              f"neither {neither:+.2f} (P={p_neither*100:.0f}%)")
        print(f"  RISK-ADJUSTED EV: {ev:+.2f}pp  (raw consensus {cmid*100:+.2f}; gap to raw = {ev-cmid*100:+.2f}, "
              f"vs Markkanen-bar {ev-MARKKANEN_BAR:+.2f})")
        print()

    # --- Markkanen reconciliation (keep-all infeasible vs A vs B) ---
    print("=== Markkanen reconciliation (why +0.74 != B; superset/subset puzzle resolved) ===")
    MK = "1628374"; amk = G.availability(MK)[0]; pmk = G.PO_MULT.get("insufficient_po_sample", 0.98)
    mk_rosters = {
        "keep-all (INFEASIBLE; Dosunmu starts)": [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
            _r(MK, "starter"), _r(M["Gobert"], "starter"), _r(M["Naz"], "sixth"), _r(M["Conley"], "rotation"), _r(M["Shannon"], "rotation"), _r(M["Phillips"], "deep")],
        "A: lose Naz (keep Dosunmu start)": [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
            _r(MK, "starter"), _r(M["Gobert"], "starter"), _r(M["Conley"], "sixth"), _r(M["Shannon"], "rotation"), _r("1642866", "rotation"), _r(M["Phillips"], "deep")],
        "B: lose Dosunmu (Conley STARTS)": [_r(M["Edwards"], "starter"), _r(M["Conley"], "starter"), _r(M["McDaniels"], "starter"),
            _r(MK, "starter"), _r(M["Gobert"], "starter"), _r(M["Naz"], "sixth"), _r(M["Shannon"], "rotation"), _r("1642866", "rotation"), _r(M["Phillips"], "deep")],
    }
    for lab, rot in mk_rosters.items():
        sc = {"name": "mk", "slug": "mk", "team_state_scenario": "base", "outgoing": [{"label": "r", "salary": 33_333_334}],
              "incoming": [{"label": "m", "salary": 46_113_154}], "override_ids": [MK, M["Randle"], M["Gobert"]], "post_rotations": {"MIN": rot}}
        def d(replace=None):
            s = copy.deepcopy(sc)
            if replace:
                for p in s["post_rotations"]["MIN"]:
                    if p["nba_player_id"] == replace: p["nba_player_id"] = G.REPL_ID
            return (F._sim(F.apply_trade(s, base_c, imp, dims, ar, an), 5.5)["teams"]["MIN"]["title"] - PRE) * 100
        wr = d() * pmk; wo = d(replace=MK); adj = amk * wr + (1 - amk) * wo
        print(f"  {lab:38} raw {d():+.2f} | with {wr:+.2f}/without {wo:+.2f} | risk-adj {adj:+.2f}pp")
    print("  EXPLANATION: not a superset puzzle. keep-all STARTS Dosunmu (consensus_net -0.21); B starts Conley")
    print("  (+1.49) in the vacated slot -> a +1.7 net lineup swing. Dosunmu is a slightly-negative-impact starter,")
    print("  so the cap-forced loss is near addition-by-subtraction. The +0.74 used a SUBOPTIMAL lineup and was")
    print("  infeasible; CORRECTED Markkanen = B ~+2.00 (caveat: the model values Conley>Dosunmu; a coach may start")
    print("  Dosunmu for age/defense, so treat +2.00 as the upper end of a ~+1.3 to +2.0 range).\n")

    print("=== one-for-two summary (risk-adjusted EV vs raw, vs Markkanen +2.00 bar) ===")
    print(f"  {'pair':22}{'raw cons':>9}{'risk-adj EV':>13}{'P(both out)':>13}{'vs bar':>8}")
    for pair, views, band, ev, both, neither, pn, ag, aw, fz, cond, cpre in rows:
        print(f"  {safe(pair['slug']):22}{band[1]*100:>+8.2f}{ev:>+12.2f}{pn*100:>11.0f}%{ev-MARKKANEN_BAR:>+8.2f}")


if __name__ == "__main__":
    main()
