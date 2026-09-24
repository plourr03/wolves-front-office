#!/usr/bin/env python3
"""The final numbers sheet for piece 2, the season preview. Rebuilt for the eight-section
structure.

EVERY FIGURE THE PIECE MAY QUOTE, keyed, computed from an output file (never typed), with
the run that produced it, a label saying what kind of number it is, and a verdict saying
how it may be used. The skeleton is a template that pulls its numbers from this sheet by
key, and `reconcile_figures.py` fails if the rendered skeleton contains a digit that did not
come from here. Anything not on this sheet does not go in the piece.

Labels:   OBSERVED (happened)   MODELED (simulation or impact view)   COMPOSED (real
          measurements recombined by us)   ASSUMED (our choice)   FACT (sourced or
          arithmetic)
Verdicts: QUOTABLE   QUOTABLE AS BAND   DIRECTIONAL   NOT QUOTABLE   DESCRIPTIVE   WITHHELD

RUN IDS BY AGING BASIS. The run log does not record the basis, so runs are assigned by the
chain boundary: the aged leg of the D70 chain began with `build_strengths` at AGED_START.
An un-aged figure takes the last successful run before it, an aged figure the last after.

    python kuminga/scripts/build_final_numbers.py
"""
from __future__ import annotations

import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from kuminga.lib import runlog  # noqa: E402

OUT = os.path.join(REPO, "kuminga", "outputs")
AGED = os.path.join(OUT, "aged")
DOCS = os.path.join(REPO, "kuminga", "docs")
LOG = os.path.join(REPO, "kuminga", "logs", "runs.jsonl")
OUT_CSV = os.path.join(OUT, "final_numbers.csv")
OUT_MD = os.path.join(OUT, "final_numbers.md")
FORKS = ["consensus", "rapm", "box", "darko"]
# The aged leg of the CURRENT chain. Runs from 2026-09-19 onwards record their own basis
# (`aging` in the run record, D90), so these windows are only a fallback for older runs,
# which is why they name the chain they belong to.
AGED_START = "2026-09-19T19:51:35"
AGED_END = "2026-09-19T23:30:00"
LEGACY_AGED_START = "2026-09-16T19:58:59"
LEGACY_AGED_END = "2026-09-16T22:39:31"
# every candidate verdict, in table order. Whether each ships is COMPUTED (D85): same
# agreed sign on both aging bases and all four views clearing the floor on both.
VERDICTS = [("ball_in", "LaMelo Ball in"), ("reid_out", "Naz Reid out"),
            ("other_departures", "Other departures (a bundle of seven)"),
            ("randle_out", "Julius Randle out"), ("dosunmu_retained", "Ayo Dosunmu re-signed"),
            ("depth", "Depth signings and re-signings"), ("kuminga_in", "Kuminga in (pooled)"),
            ("ddv_injury", "DiVincenzo's Achilles (not a transaction)"),
            ("A_c3_default_shannon", "Kuminga slot, default allocation"),
            ("C_mcdaniels_slides", "Kuminga slot, McDaniels slides"),
            ("D_beringer_fills", "Kuminga slot, Beringer fills"),
            ("E_tight_rule_F_or_FC", "Kuminga slot, tight eligibility rule"),
            ("B_lyles_fills", "Kuminga slot, Lyles fills")]
PRE_D85 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs", "pre_d85")


def runs():
    out = []
    for line in open(LOG, encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("status") == "ok":
            out.append(d)
    return out


RUNS = runs()


def _basis_of(d):
    """A run's aging basis: recorded if the run wrote it, else inferred from which chain
    leg its clock falls in. D90: recording beats inferring, because the inferred version
    silently pointed at the previous chain once a new one ran."""
    rec = d.get("aging")
    if rec is not None:
        return "aged" if str(rec) == "1" else "unaged"
    ts = d["started_utc"][:19]
    if AGED_START <= ts < AGED_END or LEGACY_AGED_START <= ts < LEGACY_AGED_END:
        return "aged"
    return "unaged"


def rid(script, basis=None, minutes_rule=None):
    c = [d for d in RUNS if d.get("script") == script]
    if minutes_rule:
        c = [d for d in c if (d.get("inputs") or {}).get("minutes_rule") == minutes_rule]
    if basis in ("unaged", "aged"):
        c = [d for d in c if _basis_of(d) == basis]
    if not c:
        raise RuntimeError("no successful run for %s (%s)" % (script, basis))
    return c[-1]["run_id"]


def csv(name, d=OUT, **kw):
    return pd.read_csv(os.path.join(d, name), **kw)


def sgn(v, n=2):
    return ("%+." + str(n) + "f") % v


def pct(v, n=2):
    return ("%." + str(n) + "f%%") % v


def money(v):
    return "$" + "{:,.0f}".format(v)


def floors_for(fc, st):
    out = {}
    for f in FORKS:
        g = fc[fc.fork == f].sort_values("min_net").reset_index(drop=True)
        net = float(st[(st.fork == f) & (st.team_abbr == "MIN")].net_current.iloc[0])
        mc = float(np.interp(net, g.min_net, g.title_sd)) * 100
        h = float(g.min_net.diff().median())
        d2 = np.abs(np.diff(g.title.to_numpy(), 2)) / (h ** 2)
        idx = int(np.clip(np.searchsorted(g.min_net.to_numpy(), net) - 1, 0, len(d2) - 1))
        lo, hi = max(0, idx - 2), min(len(d2), idx + 3)
        f2 = float(np.max(d2[lo:hi])) if hi > lo else float(np.max(d2))
        out[f] = 2.0 * float(np.hypot(mc, (h ** 2) / 8.0 * f2 * 100)) * np.sqrt(2)
    return out


def main():
    with runlog.run("build_final_numbers", inputs={"aged_start": AGED_START}) as r:
        rows = []

        def F(key, section, figure, value, label, verdict, run, source):
            if any(x["key"] == key for x in rows):
                raise RuntimeError("duplicate key %s" % key)
            rows.append(dict(key=key, section=section, figure=figure, value=str(value),
                             label=label, verdict=verdict, run_id=run, source=source))

        # ================= 1. THE NUMBER ===============================================
        S = "1. The number"
        sim_u, sim_a = csv("sim_all30_2026_27.csv"), csv("sim_all30_2026_27.csv", AGED)
        ru, ra = rid("run_sim", "unaged"), rid("run_sim", "aged")
        for tag, sim, run in (("", sim_u, ru), ("_aged", sim_a, ra)):
            t = sim[sim.team_abbr == "MIN"].title_current * 100
            F("title" + tag, S, "MIN title probability, mean of four views" + tag, pct(t.mean()),
              "MODELED", "QUOTABLE AS BAND", run, "sim_all30_2026_27.csv")
            F("title_lo" + tag, S, "four-view low" + tag, pct(t.min()), "MODELED",
              "QUOTABLE AS BAND", run, "sim_all30_2026_27.csv")
            F("title_hi" + tag, S, "four-view high" + tag, pct(t.max()), "MODELED",
              "QUOTABLE AS BAND", run, "sim_all30_2026_27.csv")
        mk = csv("market_devig_2026_27.csv").set_index("team_abbr")
        rm = rid("market_devig")
        F("mkt_min", S, "MIN market title odds, proportional de-vig", pct(100 * mk.loc["MIN", "market_prop"]),
          "OBSERVED", "QUOTABLE", rm, "market_devig_2026_27.csv")
        F("mkt_min_rank", S, "MIN market rank", int(mk.loc["MIN", "market_rank"]), "OBSERVED",
          "QUOTABLE", rm, "market_devig_2026_27.csv")
        F("model_min_rank", S, "MIN model rank", int(mk.loc["MIN", "model_rank"]), "MODELED",
          "QUOTABLE", rm, "market_devig_2026_27.csv")
        F("overround", S, "six-book overround", pct(100 * (mk.p_raw.sum() - 1), 1), "OBSERVED",
          "FACT", rm, "market_devig_2026_27.csv")
        cors = [float(mk[f].rank().corr(mk.market_prop.rank())) for f in FORKS]
        F("rankcorr_lo", S, "model-market rank correlation, lowest view", "%.2f" % min(cors),
          "COMPOSED", "QUOTABLE AS BAND", rm, "market_devig_2026_27.csv (Spearman per view)")
        F("rankcorr_hi", S, "model-market rank correlation, highest view", "%.2f" % max(cors),
          "COMPOSED", "QUOTABLE AS BAND", rm, "market_devig_2026_27.csv (Spearman per view)")
        f4a = csv("f4a_per_view_disagreement.csv").set_index("team")
        dis = mk[mk.diff_pp.abs() > 0.5].index
        F("n_disagree", S, "teams where model and market differ by more than 0.5 points",
          len(dis), "COMPOSED", "QUOTABLE", rm, "market_devig_2026_27.csv")
        F("n_allviews", S, "of those, disagreements where all four views sit on one side",
          int((f4a.loc[dis, "label"] == "ALL-VIEWS").sum()), "COMPOSED", "QUOTABLE",
          rid("f4_per_view_disagreement"), "f4a_per_view_disagreement.csv")
        F("min_view_ranks", S, "MIN rank in each view", "%d to %d" % (
            f4a.loc["MIN", ["rank_consensus", "rank_rapm", "rank_box", "rank_darko"]].min(),
            f4a.loc["MIN", ["rank_consensus", "rank_rapm", "rank_box", "rank_darko"]].max()),
          "MODELED", "QUOTABLE", rid("f4_per_view_disagreement"), "f4a_per_view_disagreement.csv")
        # the honesty rail on the aged basis (R5): same definitions, recomputed
        r5 = csv("r5_honesty_rail_bases.csv").set_index("basis")
        r5t = csv("r5_disagreements_bases.csv").set_index(["basis", "team"])
        rr5 = rid("r5_honesty_rail_bases")
        src5 = "r5_honesty_rail_bases.csv"
        F("rankcorr_lo_aged", S, "model-market rank correlation, lowest view, aged", "%.2f" % r5.loc["aged", "rankcorr_lo"],
          "COMPOSED", "QUOTABLE AS BAND", rr5, src5)
        F("rankcorr_hi_aged", S, "model-market rank correlation, highest view, aged", "%.2f" % r5.loc["aged", "rankcorr_hi"],
          "COMPOSED", "QUOTABLE AS BAND", rr5, src5)
        F("n_disagree_aged", S, "disagreements over 0.5 points, aged", int(r5.loc["aged", "n_disagree"]),
          "COMPOSED", "QUOTABLE", rr5, src5)
        F("n_allviews_aged", S, "of those, all-views, aged", int(r5.loc["aged", "n_allviews"]),
          "COMPOSED", "QUOTABLE", rr5, src5)
        ma = r5t.loc[("aged", "MIN")]
        mranks = [int(ma["rank_" + f]) for f in FORKS]
        F("min_view_ranks_aged", S, "MIN rank in each view, aged", "%d to %d" % (min(mranks), max(mranks)),
          "MODELED", "QUOTABLE", rr5, "r5_disagreements_bases.csv")
        F("min_label_aged", S, "MIN disagreement label, aged", ma.label.lower(), "MODELED", "QUOTABLE", rr5,
          "r5_disagreements_bases.csv")
        F("min_above_aged", S, "MIN views above the market, aged", int(ma.views_above_market), "MODELED",
          "QUOTABLE", rr5, "r5_disagreements_bases.csv")
        F("min_box_aged", S, "MIN box view, aged", pct(ma.pct_box), "MODELED", "QUOTABLE AS BAND", rr5,
          "r5_disagreements_bases.csv")
        F("min_darko_aged", S, "MIN DARKO view, aged", pct(ma.pct_darko), "MODELED", "QUOTABLE AS BAND", rr5,
          "r5_disagreements_bases.csv")
        F("model_bos_aged", S, "BOS model title odds, mean of four views, aged", pct(r5t.loc[("aged", "BOS"), "mean_pct"]),
          "MODELED", "QUOTABLE AS BAND", rr5, "r5_disagreements_bases.csv")
        F("bos_label_aged", S, "BOS disagreement label, aged", r5t.loc[("aged", "BOS"), "label"].lower(), "MODELED",
          "QUOTABLE", rr5, "r5_disagreements_bases.csv")
        for tm in ("BOS", "SAS", "CHA"):
            F("model_%s" % tm.lower(), S, "%s model title odds" % tm,
              pct(100 * mk.loc[tm, "model_mean"]), "MODELED", "QUOTABLE AS BAND", rm,
              "market_devig_2026_27.csv")
            F("mkt_%s" % tm.lower(), S, "%s market title odds" % tm,
              pct(100 * mk.loc[tm, "market_prop"]), "OBSERVED", "QUOTABLE", rm,
              "market_devig_2026_27.csv")
        dec = csv("n8_watch_list_december.csv").set_index("team")
        rn8 = rid("n8_watch_list")
        F("bos_dec_threshold", S, "Boston December (game 30) threshold, net per 100",
          sgn(dec.loc["BOS", "threshold"], 1), "COMPOSED", "QUOTABLE", rn8,
          "n8_watch_list_december.csv")
        F("bos_dec_game", S, "December checkpoint game", int(dec.loc["BOS", "n_games"]),
          "ASSUMED", "FACT", rn8, "n8_watch_list_december.csv")
        F("bos_range_lo", S, "Boston model net range low", sgn(dec.loc["BOS", "range_lo"], 1),
          "MODELED", "QUOTABLE AS BAND", rn8, "n8_watch_list_december.csv")
        F("bos_range_hi", S, "Boston model net range high", sgn(dec.loc["BOS", "range_hi"], 1),
          "MODELED", "QUOTABLE AS BAND", rn8, "n8_watch_list_december.csv")
        F("dec_noise", S, "30-game net rating noise per 100", "%.1f" % dec.loc["BOS", "noise"],
          "OBSERVED", "QUOTABLE", rn8, "n8_watch_list_december.csv")

        gate = csv("w2_aging_gate.csv").set_index("item")
        rw2 = rid("w2_aging_gate")
        nf_u = pd.concat([csv("noise_floor.csv").set_index("move"),
                          csv("noise_floor_slot.csv").set_index("variant")])
        nf_a = pd.concat([csv("noise_floor_AGED.csv", AGED).set_index("move"),
                          csv("noise_floor_slot_AGED.csv", AGED).set_index("variant")])
        pre_gate = pd.read_csv(os.path.join(PRE_D85, "w2_aging_gate.csv")).set_index("item")
        pre_u = pd.concat([pd.read_csv(os.path.join(PRE_D85, "noise_floor.csv")).set_index("move"),
                           pd.read_csv(os.path.join(PRE_D85, "noise_floor_slot.csv")).set_index("variant")])
        pre_a = pd.concat([pd.read_csv(os.path.join(PRE_D85, "aged", "noise_floor_AGED.csv")).set_index("move"),
                           pd.read_csv(os.path.join(PRE_D85, "aged", "noise_floor_slot_AGED.csv")).set_index("variant")])

        def ships(g, u, a, item):
            return bool(g.loc[item, "unaged_sign"] != "MIXED" and g.loc[item, "unaged_sign"] == g.loc[item, "aged_sign"]
                        and int(u.loc[item, "n_forks_clearing"]) == 4 and int(a.loc[item, "n_forks_clearing"]) == 4)

        # D87: the shipping rule is four cells, two aging bases x two minutes allocators.
        # r7_allocator_agreement.py is the authority; its pooled cells must agree with the
        # two-cell computation above, or one of the two files is stale.
        r7 = csv("r7_allocator_verdicts.csv").set_index("item")
        rr7 = rid("r7_allocator_agreement")
        n_ship = n_retired = 0
        for order, (item, lab) in enumerate(VERDICTS):
            two_cell = ships(gate, nf_u, nf_a, item)
            pooled_two_cell = bool(
                r7.loc[item, "pooled_unaged_sign"] != "MIXED"
                and r7.loc[item, "pooled_unaged_sign"] == r7.loc[item, "pooled_aged_sign"]
                and int(r7.loc[item, "pooled_unaged_clear"]) == 4
                and int(r7.loc[item, "pooled_aged_clear"]) == 4)
            if two_cell != pooled_two_cell:
                raise RuntimeError("%s: the aging gate and r7 disagree on the pooled cells; one "
                                   "of the two is stale" % item)
            now, before = bool(r7.loc[item, "ships_all_four"]), ships(pre_gate, pre_u, pre_a, item)
            F("v_%s_pooled_u" % item, S, "%s, pooled un-aged mean pp" % lab,
              sgn(r7.loc[item, "pooled_unaged_mean"], 2), "MODELED", "QUOTABLE", rr7,
              "r7_allocator_verdicts.csv")
            F("v_%s_pooled_a" % item, S, "%s, pooled aged mean pp" % lab,
              sgn(r7.loc[item, "pooled_aged_mean"], 2), "MODELED", "QUOTABLE", rr7,
              "r7_allocator_verdicts.csv")
            F("v_%s_tr_u" % item, S, "%s, team-rank un-aged mean pp" % lab,
              sgn(r7.loc[item, "teamrank_unaged_mean"], 2), "MODELED", "QUOTABLE", rr7,
              "r7_allocator_verdicts.csv")
            F("v_%s_tr_a" % item, S, "%s, team-rank aged mean pp" % lab,
              sgn(r7.loc[item, "teamrank_aged_mean"], 2), "MODELED", "QUOTABLE", rr7,
              "r7_allocator_verdicts.csv")
            F("v_%s_cells" % item, S, "%s, views clearing in the four cells" % lab,
              "%d/4, %d/4, %d/4, %d/4" % tuple(int(r7.loc[item, c]) for c in (
                  "pooled_unaged_clear", "pooled_aged_clear", "teamrank_unaged_clear",
                  "teamrank_aged_clear")), "MODELED", "QUOTABLE", rr7, "r7_allocator_verdicts.csv")
            F("v_%s_two_cell" % item, S, "%s ships on the two-cell rule (pooled only)" % lab,
              "yes" if two_cell else "no", "MODELED", "QUOTABLE", rr7, "r7_allocator_verdicts.csv")
            n_ship += now
            n_retired += before and not now
            F("v_%s_label" % item, S, "verdict label", lab, "FACT", "FACT", rw2, "build_final_numbers VERDICTS")
            F("v_%s_u" % item, S, "%s, un-aged mean pp" % lab, sgn(gate.loc[item, "unaged_mean"], 2),
              "MODELED", "QUOTABLE", rw2, "w2_aging_gate.csv")
            F("v_%s_a" % item, S, "%s, aged mean pp" % lab, sgn(gate.loc[item, "aged_mean"], 2),
              "MODELED", "QUOTABLE", rw2, "w2_aging_gate.csv")
            F("v_%s_clear" % item, S, "%s, views clearing the floor un-aged / aged" % lab,
              "%d/4, %d/4" % (nf_u.loc[item, "n_forks_clearing"], nf_a.loc[item, "n_forks_clearing"]),
              "MODELED", "QUOTABLE", rw2, "noise_floor*.csv")
            F("v_%s_signs" % item, S, "%s, sign un-aged / aged" % lab,
              "%s / %s" % (gate.loc[item, "unaged_sign"].lower(), gate.loc[item, "aged_sign"].lower()),
              "MODELED", "QUOTABLE", rw2, "w2_aging_gate.csv")
            F("v_%s_ships" % item, S, "%s ships" % lab, "yes" if now else "no", "MODELED", "QUOTABLE", rw2,
              "w2_aging_gate.csv, noise_floor*.csv")
            F("v_%s_preship" % item, S, "%s shipped before D85" % lab, "yes" if before else "no", "MODELED",
              "QUOTABLE", rw2, "pre_d85/w2_aging_gate.csv, pre_d85/noise_floor*.csv")
        F("n_ship", S, "verdicts that ship", n_ship, "MODELED", "QUOTABLE", rw2, "w2_aging_gate.csv, noise_floor*.csv")
        F("n_ship_pre", S, "verdicts that shipped before D85",
          sum(ships(pre_gate, pre_u, pre_a, i) for i, _ in VERDICTS), "MODELED", "QUOTABLE", rw2,
          "pre_d85/w2_aging_gate.csv")
        F("n_retired", S, "verdicts that shipped before D85 and do not now", n_retired, "MODELED", "QUOTABLE",
          rw2, "pre_d85 vs current")
        F("n_ship_two_cell", S, "verdicts that ship on the two-cell rule (pooled only)",
          int(sum(ships(gate, nf_u, nf_a, i) for i, _ in VERDICTS)), "MODELED", "QUOTABLE", rr7,
          "w2_aging_gate.csv, noise_floor*.csv")
        F("n_candidates", S, "candidate verdicts tested", len(VERDICTS), "FACT", "FACT", rr7,
          "r7_allocator_verdicts.csv")
        r7s = csv("r7_allocator_slots.csv")
        for alloc, key in (("pooled", "k_min_pooled"), ("teamrank", "k_min_teamrank")):
            F(key, S, "Kuminga minutes under the %s allocator" % alloc,
              "%.1f" % r7s[r7s.allocator == alloc].kuminga_minutes.iloc[0], "MODELED", "QUOTABLE",
              rr7, "r7_allocator_slots.csv")
        r5v = csv("r5_shapley_williams_vall.csv")
        rr5w = rid("r5_shapley_williams")
        g4 = r5v[r5v.version == "after_d85_teamrank"]
        F("d85_residual", S, "post-D85 attribution roster vs direct simulation, worst view pp, both bases",
          "%.2f" % g4.v_all_minus_direct.abs().max(), "MODELED", "QUOTABLE", rr5w, "r5_shapley_williams_vall.csv")
        gp = r5v[r5v.version == "after_d85"]
        F("d85_pooled_gap", S, "post-D85 pooled attribution rule vs direct simulation, worst view pp, both bases",
          "%.2f" % gp.v_all_minus_direct.abs().max(), "MODELED", "QUOTABLE", rr5w, "r5_shapley_williams_vall.csv")
        g0 = r5v[(r5v.version == "before_d85_teamrank") & (r5v.basis == "unaged")]
        F("d85_gap_before", S, "pre-D85 attribution roster vs direct simulation, worst view pp, un-aged",
          "%.2f" % g0.v_all_minus_direct.abs().max(), "MODELED", "QUOTABLE", rr5w, "r5_shapley_williams_vall.csv")
        F("williams_bio", S, "Cody Williams consensus impact", "%+.2f" % csv("player_pool_2026_27.csv").set_index(
          "player_name").query("scenario == 'current'").loc["Cody Williams", "consensus_net"], "MODELED", "QUOTABLE",
          rid("build_rotations"), "player_pool_2026_27.csv")
        spv = csv("r2_departures_split_shapley_verdicts.csv").set_index("move")
        rr2 = rid("r2_departures")
        F("anderson_u", S, "Kyle Anderson departure, un-aged pp", sgn(spv.loc["dep:Kyle Anderson", "mean_pp_unaged"], 2),
          "MODELED", "QUOTABLE", rr2, "r2_departures_split_shapley_verdicts.csv")
        F("anderson_a", S, "Kyle Anderson departure, aged pp", sgn(spv.loc["dep:Kyle Anderson", "mean_pp_aged"], 2),
          "MODELED", "QUOTABLE", rr2, "r2_departures_split_shapley_verdicts.csv")
        F("anderson_clear", S, "Kyle Anderson departure, views clearing un-aged / aged",
          "%d/4, %d/4" % (spv.loc["dep:Kyle Anderson", "n_clear_unaged"], spv.loc["dep:Kyle Anderson", "n_clear_aged"]),
          "MODELED", "QUOTABLE", rr2, "r2_departures_split_shapley_verdicts.csv")
        F("n_dep_ship", S, "departures that ship on their own",
          int(spv[spv.index.str.startswith("dep:")].ships.astype(bool).sum()), "MODELED", "QUOTABLE", rr2,
          "r2_departures_split_shapley_verdicts.csv")
        F("n_departures", S, "players in the other-departures bundle",
          int(sum(1 for m_ in spv.index if m_.startswith("dep:"))), "FACT", "FACT", rr2,
          "r2_departures_split_shapley_verdicts.csv")

        F("sims", S, "simulations per f-curve view", "200,000", "ASSUMED", "FACT",
          rid("merge_fcurve_parts", "unaged"), "build_fcurve KUMINGA_FCURVE_NSIMS")
        F("per100", S, "rating basis, possessions", "100", "FACT", "FACT", rn8, "definition")

        # ================= 2. WHAT THE ODDS GET RIGHT ===================================
        S = "2. What the odds get right"
        m1 = csv("m1_style_model_fit.csv").set_index("sample")
        rm1 = rid("m1_style_model")
        F("m1_rs_gain", S, "style overlay held-out MAE gain, 2025-26 regular season",
          "%+.4f" % m1.loc["HELD OUT 2025-26 RS", "mae_gain"], "MODELED", "QUOTABLE", rm1, "m1_style_model_fit.csv")
        F("m1_rs_worse", S, "held-out MAE increase, regular season",
          "%.4f" % abs(m1.loc["HELD OUT 2025-26 RS", "mae_gain"]), "MODELED", "QUOTABLE", rm1, "m1_style_model_fit.csv")
        F("m1_po_worse", S, "held-out MAE increase, postseasons",
          "%.4f" % abs(m1.loc["HELD OUT postseasons", "mae_gain"]), "MODELED", "QUOTABLE", rm1, "m1_style_model_fit.csv")
        F("m1_rs_n", S, "held-out regular-season games", "{:,}".format(int(m1.loc["HELD OUT 2025-26 RS", "n_games"])),
          "OBSERVED", "FACT", rm1, "m1_style_model_fit.csv")
        F("m1_po_gain", S, "style overlay held-out MAE gain, three postseasons",
          "%+.4f" % m1.loc["HELD OUT postseasons", "mae_gain"], "MODELED", "QUOTABLE", rm1, "m1_style_model_fit.csv")
        F("m1_po_n", S, "held-out postseason games", int(m1.loc["HELD OUT postseasons", "n_games"]),
          "OBSERVED", "FACT", rm1, "m1_style_model_fit.csv")
        n3 = csv("n3_translation_tests.csv")
        rn3 = rid("n3_playoff_translation")
        lo3 = n3[n3["sample"] == "longer 2014-26"].set_index("feature")
        pr3 = n3[n3["sample"] == "primary 2024-26"].set_index("feature")
        F("n3_start", S, "first postseason in the longer N3 sample", "2014", "FACT", "FACT", rn3,
          "n3_playoff_translation.py FIRST")
        F("n3_series", S, "series, 2014-26", int(lo3.n_series.iloc[0]), "OBSERVED", "FACT", rn3, "n3_translation_tests.csv")
        F("n3_series_primary", S, "series, three project postseasons", int(pr3.n_series.iloc[0]), "OBSERVED", "FACT",
          rn3, "n3_translation_tests.csv")
        F("n3_mde_lo", S, "smallest detectable effect, 13 seasons, low", "%.2f" % lo3.mde80.min(), "COMPOSED", "QUOTABLE", rn3, "n3_translation_tests.csv")
        F("n3_mde_hi", S, "smallest detectable effect, 13 seasons, high", "%.2f" % lo3.mde80.max(), "COMPOSED", "QUOTABLE", rn3, "n3_translation_tests.csv")
        F("n3_n_translating", S, "features that translate", int(lo3.translates.sum()), "MODELED", "QUOTABLE", rn3, "n3_translation_tests.csv")
        F("n3_n_features", S, "candidate translation features", len(lo3), "ASSUMED", "FACT", rn3, "n3_translation_tests.csv")
        ds = lo3.loc["def_share"]
        F("ds_coef", S, "defence share, points per game per SD", "%+.2f" % ds.coef, "MODELED", "NOT QUOTABLE", rn3, "n3_translation_tests.csv")
        F("ds_se", S, "defence share SE", "%.2f" % ds.coef_se, "MODELED", "NOT QUOTABLE", rn3, "n3_translation_tests.csv")
        F("ds_p", S, "defence share permutation p", "%.3f" % ds.perm_p, "MODELED", "NOT QUOTABLE", rn3, "n3_translation_tests.csv")
        F("ds_bar", S, "Bonferroni bar", "%.4f" % (0.05 / len(lo3)), "ASSUMED", "FACT", rn3, "n3_translation_tests.csv")
        F("ds_ci_hi", S, "defence share single-test 95% interval upper end", "%+.2f" % (ds.coef + 1.96 * ds.coef_se),
          "MODELED", "NOT QUOTABLE", rn3, "n3_translation_tests.csv")
        ph = csv("n3_translation_tests_posthoc.csv").set_index("check")
        F("ds_early", S, "defence share 2014-23 only", "%+.2f" % ph.loc["2014-23 only (non-overlapping)", "def_share_coef"],
          "MODELED", "NOT QUOTABLE", rn3, "n3_translation_tests_posthoc.csv")
        F("ds_late", S, "defence share 2024-26 only", "%+.2f" % ph.loc["2024-26 only", "def_share_coef"],
          "MODELED", "NOT QUOTABLE", rn3, "n3_translation_tests_posthoc.csv")
        F("ds_luck", S, "defence share with three-point luck added",
          "%+.2f" % ph.loc["2014-26, + both teams' three-point luck", "def_share_coef"], "MODELED", "NOT QUOTABLE", rn3,
          "n3_translation_tests_posthoc.csv")
        n4 = csv("n4_matchup_repeatability.csv").iloc[0]
        rn4 = rid("n4_versatility_index")
        F("n4_sd13", S, "true matchup effect SD, 2013-26, points per game", "%.2f" % n4.primary_sd_true, "OBSERVED", "QUOTABLE", rn4, "n4_matchup_repeatability.csv")
        F("n4_sd13_up", S, "upper 95%, 2013-26", "%.2f" % n4.primary_sd_upper95, "OBSERVED", "QUOTABLE", rn4, "n4_matchup_repeatability.csv")
        F("n4_sd97", S, "true matchup effect SD, 1997-2026", "%.2f" % n4.extended_sd_true, "OBSERVED", "QUOTABLE", rn4, "n4_matchup_repeatability.csv")
        F("n4_sd97_up", S, "upper 95%, 1997-2026", "%.2f" % n4.extended_sd_upper95, "OBSERVED", "QUOTABLE", rn4, "n4_matchup_repeatability.csv")
        F("n4_series_up", S, "series points at the tighter upper bound",
          "%.0f" % (100 * (n4.p_series_upper - n4.p_series_even)), "MODELED", "QUOTABLE", rn4, "n4_matchup_repeatability.csv")
        F("n4_rankcorr", S, "spread vs own net rank correlation outside the field", "%.2f" % n4.spread_net_rankcorr_min,
          "MODELED", "QUOTABLE", rn4, "n4_matchup_repeatability.csv")
        F("n4_start13", S, "first season, primary window", str(n4.primary_window)[:7], "FACT", "FACT", rn4,
          "n4_matchup_repeatability.csv")
        F("n4_start97", S, "first season, extended window", str(n4.extended_window)[:7], "FACT", "FACT", rn4,
          "n4_matchup_repeatability.csv")
        F("n4_games97", S, "regular-season games, 1997-2026", "{:,}".format(int(n4.extended_games)), "OBSERVED", "FACT", rn4,
          "n4_matchup_repeatability.csv")
        km = csv("m3_key_matchups.csv")
        rm3 = rid("m3_opponent_cards")
        m3doc = open(os.path.join(DOCS, "m3_opponent_cards.md"), encoding="utf-8").read()
        se30 = re.search(r"measured at ([0-9.]+) points per matchup possession at 30", m3doc)
        norm = re.search(r"held him ([0-9.]+) to ([0-9.]+) below his own baseline", m3doc)
        chance = re.search(r"would produce about ([0-9.]+) above", m3doc)
        F("m3_se30", S, "matchup SE at 30 possessions", se30.group(1), "OBSERVED", "QUOTABLE", rm3, "m3_opponent_cards.md")
        F("m3_norm_lo", S, "primary-defender norm, low", norm.group(1), "OBSERVED", "QUOTABLE", rm3, "m3_opponent_cards.md")
        F("m3_norm_hi", S, "primary-defender norm, high", norm.group(2), "OBSERVED", "QUOTABLE", rm3, "m3_opponent_cards.md")
        F("m3_edges", S, "matchups beyond the norm by 2 SEs, above", int((km.z >= 2).sum()), "OBSERVED", "QUOTABLE", rm3,
          "m3_key_matchups.csv")
        F("m3_rows", S, "observed West-field primary matchups", int(km.z.notna().sum()), "OBSERVED", "FACT", rm3,
          "m3_key_matchups.csv")
        F("m3_chance", S, "expected by chance, above", chance.group(1), "OBSERVED", "QUOTABLE", rm3, "m3_opponent_cards.md")
        h2 = csv("champions_h2_base_rates.csv").iloc[0]
        rh = rid("champions_table")
        F("h2_n", S, "clean seasons", int(h2.n_seasons), "FACT", "FACT", rh, "champions_h2_base_rates.csv")
        F("h2_fav", S, "favourite won", int(round(h2.p_favorite_wins * h2.n_seasons)), "OBSERVED", "QUOTABLE", rh, "champions_h2_base_rates.csv")
        F("h2_top3", S, "champion from the top three", int(round(h2.p_champ_top3 * h2.n_seasons)), "OBSERVED", "QUOTABLE", rh,
          "champions_h2_base_rates.csv")
        F("h2_top5", S, "champion from the top five", int(round(h2.p_champ_top5 * h2.n_seasons)), "OBSERVED", "QUOTABLE", rh,
          "champions_h2_base_rates.csv")
        F("h2_lo", S, "champions' preseason price, low", pct(h2.champ_implied_min), "OBSERVED", "QUOTABLE", rh, "champions_h2_base_rates.csv")
        F("h2_hi", S, "champions' preseason price, high", pct(h2.champ_implied_max), "OBSERVED", "QUOTABLE", rh, "champions_h2_base_rates.csv")
        F("h2_median", S, "champions' preseason price, median", pct(h2.champ_implied_median), "OBSERVED", "QUOTABLE", rh, "champions_h2_base_rates.csv")
        F("h2_worst_rank", S, "worst preseason rank of a champion", int(h2.champ_rank_max), "OBSERVED", "QUOTABLE", rh, "champions_h2_base_rates.csv")
        h3 = csv("h3_separation.csv")
        rh3 = rid("h1_h3_h5_profile")
        F("h3_n_non", S, "preseason top-5 non-champions", int(h3.n_non.iloc[0]), "OBSERVED", "FACT", rh3, "h3_separation.csv")
        F("h3_n_sep", S, "features that separate", int(h3.separates.sum()), "OBSERVED", "DESCRIPTIVE", rh3, "h3_separation.csv")
        F("h3_n_feat", S, "features compared", len(h3), "OBSERVED", "FACT", rh3, "h3_separation.csv")
        kn = csv("h4_knicks_case_file.csv", index_col=0).value
        rk = rid("h4_knicks_case_file")
        F("nyk_mkt", S, "Knicks preseason market price", pct(float(kn["market_title_pct"])), "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_rank", S, "Knicks preseason market rank", int(float(kn["market_rank"])), "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_wt", S, "Knicks win total", "%.1f" % float(kn["market_win_total"]), "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_wins", S, "Knicks wins", int(float(kn["actual_wins"])), "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_model", S, "our model's Knicks price", pct(float(kn["model_title_pct"])), "MODELED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_rs", S, "Knicks regular-season margin", sgn(float(kn["rs_margin"])), "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_pre", S, "before the break", sgn(float(kn["pre_break_margin"])), "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_post", S, "after the break", sgn(float(kn["post_break_margin"])), "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_po_rec", S, "Knicks playoff record", kn["po_record"], "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_po", S, "Knicks playoff margin", sgn(float(kn["po_margin"])), "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_lift", S, "Knicks playoff lift", sgn(float(kn["lift"])), "OBSERVED", "QUOTABLE", rk, "h4_knicks_case_file.csv")
        F("nyk_po_teams", S, "playoff teams", int(float(kn["po_teams"])), "OBSERVED", "FACT", rk, "h4_knicks_case_file.csv")
        for key, fmt in (("lift_mean", "sgn"), ("cmp_lift", "sgn"), ("cmp_lift_rank", "int"),
                         ("n_positive_lift", "int"), ("top5_rs_games_missed", "int"),
                         ("top5_po_games_missed", "int"), ("top5_share_rs", "3"),
                         ("top5_share_po", "3")):
            v = float(kn[key])
            F("nyk_" + key, S, "Knicks " + key, sgn(v) if fmt == "sgn" else
              ("%d" % v if fmt == "int" else "%.3f" % v), "OBSERVED", "QUOTABLE", rk,
              "h4_knicks_case_file.csv")

        # ================= 3. WHAT THE ODDS CAN'T SEE ====================================
        S = "3. What the odds can't see"
        n5u, n5a = csv("n5_fragility.csv"), csv("n5_fragility_AGED.csv")
        nmu, nma = csv("n5_next_man_up.csv"), csv("n5_next_man_up_AGED.csv")
        r5u = [d["run_id"] for d in RUNS if d.get("script") == "n5_fragility" and
               (d.get("inputs") or {}).get("basis") == "unaged"][-1]
        r5a = [d["run_id"] for d in RUNS if d.get("script") == "n5_fragility" and
               (d.get("inputs") or {}).get("basis") == "aged"][-1]
        for tag, R_, N_, run in (("", n5u, nmu, r5u), ("_aged", n5a, nma, r5a)):
            top = R_[R_.why.str.startswith("top")]
            topn = N_[N_.why.str.startswith("top")]
            for tm in ("MIN", "OKC", "SAS"):
                d = top[top.team == tm]
                full = d.title_full.mean()
                drop = d.groupby("removed").drop_pp.mean().mean()
                F("n5_%s_full%s" % (tm.lower(), tag), S, "%s full-roster title odds%s" % (tm, tag), pct(full), "MODELED", "QUOTABLE AS BAND", run, "n5_fragility*.csv")
                F("n5_%s_drop%s" % (tm.lower(), tag), S, "%s mean drop%s" % (tm, tag), "%.2f" % drop, "MODELED", "QUOTABLE AS BAND", run, "n5_fragility*.csv")
                F("n5_%s_share%s" % (tm.lower(), tag), S, "%s share of odds lost%s" % (tm, tag), "%.0f%%" % (100 * drop / full), "MODELED", "QUOTABLE AS BAND", run, "n5_fragility*.csv")
                nd = topn[topn.team == tm].groupby("removed").team_net_drop.mean()
                F("n5_%s_net%s" % (tm.lower(), tag), S, "%s mean net lost per removal%s" % (tm, tag), "%.2f" % nd.mean(), "MODELED", "QUOTABLE", run, "n5_next_man_up*.csv")
                F("n5_%s_big%s" % (tm.lower(), tag), S, "%s largest single net loss%s" % (tm, tag), "%.2f" % nd.max(), "MODELED", "QUOTABLE", run, "n5_next_man_up*.csv")
                F("n5_%s_bigname%s" % (tm.lower(), tag), S, "%s largest single loss, player%s" % (tm, tag), nd.idxmax(), "MODELED", "QUOTABLE", run, "n5_next_man_up*.csv")
                if tag == "":
                    po = topn[topn.team == tm].groupby("removed").team_net_drop_playoff_rollup.mean().mean()
                    F("n5_%s_po" % tm.lower(), S, "%s mean net lost, playoff rollup" % tm, "%.2f" % po, "MODELED", "QUOTABLE", run, "n5_next_man_up.csv")
        rot = csv("rotations_2026_27.csv")
        rrot = rid("build_rotations", "unaged")
        cur = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN")].set_index("player_name")
        F("williams_mpg", S, "Cody Williams projected minutes", "%.1f" % cur.loc["Cody Williams", "mpg"], "ASSUMED", "NOT QUOTABLE", rrot, "rotations_2026_27.csv")
        pool = csv("player_pool_2026_27.csv")
        pm = pool[(pool.scenario == "current") & (pool.team_abbr == "MIN")].set_index("player_name")
        F("rs_williams", S, "Williams rank score", "%.4f" % pm.loc["Cody Williams", "rank_score"], "COMPOSED", "DESCRIPTIVE", rrot, "player_pool_2026_27.csv")
        F("rs_clark", S, "Jaylen Clark rank score", "%.4f" % pm.loc["Jaylen Clark", "rank_score"], "COMPOSED", "DESCRIPTIVE", rrot, "player_pool_2026_27.csv")
        F("rs_gap", S, "rank-score gap", "%.4f" % (pm.loc["Jaylen Clark", "rank_score"] - pm.loc["Cody Williams", "rank_score"]),
          "COMPOSED", "DESCRIPTIVE", rrot, "player_pool_2026_27.csv")
        n8 = csv("n8_watch_list.csv").set_index("n")
        F("williams_threshold", S, "Williams minutes below which the offseason verdict turns MIXED", "%.1f" % float(n8.loc[1, "value"]),
          "MODELED", "QUOTABLE", rn8, "n8_watch_list.csv")
        w1c = csv("w1c_delta_decomposition.csv")
        rw1c = rid("w1c_decompose")
        for c, lab in (("offseason_delta", "published offseason delta"), ("injury_cost", "DiVincenzo injury cost"),
                       ("williams_cost", "Williams minutes cost"), ("interaction", "interaction"), ("remainder", "remainder")):
            F("w1c_" + c, S, lab + ", mean pp", sgn(w1c[c].mean(), 3), "MODELED", "QUOTABLE AS BAND", rw1c, "w1c_delta_decomposition.csv")
        m4 = csv("m4_lineups.csv")
        rm4 = rid("m4_lineup_study")
        F("m4_fives", S, "legal fives, DiVincenzo excluded", len(m4), "COMPOSED", "FACT", rm4, "m4_lineups.csv")
        F("m4_double", S, "double-big fives", int((m4.n_bigs >= 2).sum()), "COMPOSED", "FACT", rm4, "m4_lineups.csv")
        F("m4_nogobert", S, "fives without Gobert", int((~m4.has_gobert).sum()), "COMPOSED", "FACT", rm4, "m4_lineups.csv")
        F("m4_observed", S, "fives that have played together", int((m4.label == "OBSERVED").sum()), "OBSERVED", "FACT", rm4, "m4_lineups.csv")
        top10 = m4[m4.rankable].sort_values("net_mean", ascending=False).head(10)
        F("m4_top10_beringer", S, "of the ten best rankable fives, how many include Beringer",
          int(top10.lineup.str.contains("Joan Beringer").sum()), "COMPOSED", "DESCRIPTIVE", rm4, "m4_lineups.csv")
        F("beringer_prior", S, "Beringer 2025-26 minutes per game", "%.1f" % pm.loc["Joan Beringer", "prior_mpg"], "OBSERVED",
          "FACT", rrot, "player_pool_2026_27.csv")
        le = csv("lineup_evidence.csv").set_index("label")
        rle = rid("lineup_evidence")
        F("reid_gobert", S, "Reid + Gobert net per 100, rebuilt points", sgn(le.loc["Reid+Gobert", "net_rating"], 1),
          "OBSERVED", "DESCRIPTIVE", rle, "lineup_evidence.csv")
        F("randle_gobert", S, "Randle + Gobert net per 100, rebuilt points", sgn(le.loc["Randle+Gobert", "net_rating"], 1),
          "OBSERVED", "DESCRIPTIVE", rle, "lineup_evidence.csv")
        uu = csv("m5_unit_usage.csv").set_index("unit")
        rm5 = rid("m5_usage_accounting")
        top = [u for u in uu.index if u.startswith("Projected top five")][0]
        kin = [u for u in uu.index if u.startswith("Kuminga in")][0]
        best = [u for u in uu.index if u.startswith("Highest-usage")][0]
        obs = [u for u in uu.index if "most-used" in u][0]
        F("m5_top", S, "projected top five usage sum", "%.3f" % uu.loc[top, "usg_sum"], "COMPOSED", "QUOTABLE", rm5, "m5_unit_usage.csv")
        F("m5_top_pct", S, "percentile", "%.0f" % uu.loc[top, "league_pct"], "COMPOSED", "QUOTABLE", rm5, "m5_unit_usage.csv")
        F("m5_kin", S, "Kuminga-in five usage sum", "%.3f" % uu.loc[kin, "usg_sum"], "COMPOSED", "QUOTABLE", rm5, "m5_unit_usage.csv")
        F("m5_kin_pct", S, "percentile", "%.0f" % uu.loc[kin, "league_pct"], "COMPOSED", "QUOTABLE", rm5, "m5_unit_usage.csv")
        F("m5_kin3_pct", S, "percentile at three-season rates", "%.0f" % uu.loc[kin, "league_pct_2023_26"], "COMPOSED", "QUOTABLE", rm5, "m5_unit_usage.csv")
        F("m5_obs_pct", S, "last season's actual five, percentile", "%.0f" % uu.loc[obs, "league_pct"], "OBSERVED", "QUOTABLE", rm5, "m5_unit_usage.csv")
        F("m5_league_fives", S, "league starting fives", "{:,}".format(int(uu.loc[top, "league_team_games"])), "OBSERVED", "FACT", rm5, "m5_unit_usage.csv")
        pb = csv("m5_pairing_base_rates.csv").set_index("group")
        adj = pb.loc["ADJUSTED pairing effect (prior usage, age, moved)"]
        star = pb.loc[[g_ for g_ in pb.index if "0.28" in g_][0]]
        F("m5_adj_usg", S, "adjusted pairing effect on usage, points", "%+.1f" % (100 * adj.d_usg), "OBSERVED", "DIRECTIONAL", rm5, "m5_pairing_base_rates.csv")
        F("m5_adj_ts", S, "adjusted pairing effect on true shooting, points", "%+.1f" % (100 * adj.d_ts), "OBSERVED", "DIRECTIONAL", rm5, "m5_pairing_base_rates.csv")
        F("m5_star_usg", S, "star-tier pairing effect on usage", "%+.1f" % (100 * star.d_usg), "OBSERVED", "DIRECTIONAL", rm5, "m5_pairing_base_rates.csv")
        F("m5_star_usg_se", S, "star-tier usage SE", "%.1f" % (100 * star.d_usg_se), "OBSERVED", "DIRECTIONAL", rm5, "m5_pairing_base_rates.csv")
        F("m5_star_ts", S, "star-tier pairing effect on true shooting", "%+.1f" % (100 * star.d_ts), "OBSERVED", "DIRECTIONAL", rm5, "m5_pairing_base_rates.csv")
        F("m5_star_n", S, "star-tier treated player-seasons", int(star.n_treated), "OBSERVED", "FACT", rm5, "m5_pairing_base_rates.csv")
        F("m5_treated", S, "player-seasons with a new high-usage partner", int(pb.loc["all, new high-usage partner", "n"]), "OBSERVED", "FACT", rm5, "m5_pairing_base_rates.csv")
        sd = csv("seed_distribution.csv")
        rsd = rid("seed_distribution", "unaged")
        ms = sd[(sd.team_abbr == "MIN") & (sd.field == "current")]
        seeds = {k: ms["p_seed%d" % k].mean() for k in range(1, 11)}
        modal = max(seeds, key=seeds.get)
        F("n2_modal", S, "modal seed", "%dth" % modal, "MODELED", "QUOTABLE", rsd, "seed_distribution.csv")
        F("n2_modal_p", S, "modal seed probability", "%.0f%%" % (100 * seeds[modal]), "MODELED", "QUOTABLE", rsd, "seed_distribution.csv")
        F("n2_top6", S, "P(top six)", "%.0f%%" % (100 * ms.p_playoff_top6.mean()), "MODELED", "QUOTABLE", rsd, "seed_distribution.csv")
        r1 = csv("n2_round1_opponents.csv")
        r1 = r1.set_index(r1.columns[0]).iloc[:, 0]
        rn2 = rid("n2_path")
        F("n2_sas_okc", S, "P(first-round opponent is SAS or OKC)", "%.0f%%" % (100 * (r1["SAS"] + r1["OKC"])), "MODELED", "QUOTABLE", rn2, "n2_round1_opponents.csv")
        path = csv("n2_path.csv")
        F("n2_r2", S, "P(reach round two)", "%.0f%%" % (100 * path.r2.mean()), "MODELED", "QUOTABLE AS BAND", rn2, "n2_path.csv")
        F("n2_cond", S, "P(title | escape round one)", "%.1f%%" % (100 * path.title.mean() / path.r2.mean()), "MODELED", "QUOTABLE AS BAND", rn2, "n2_path.csv")

        # ================= 4. KUMINGA ===================================================
        S = "4. Kuminga, better and worse"
        rn6 = rid("n6_kuminga_ledger")
        pdf = csv("n6_primary_defender.csv")
        k3 = pdf[(pdf.window == "2023-26 pooled") & (pdf.player == "Jonathan Kuminga")].set_index("role")
        e3 = pdf[(pdf.window == "2023-26 pooled") & (pdf.player == "Anthony Edwards")].set_index("role")
        for role in ("scorer", "defender"):
            F("k_%s_pct" % role, S, "Kuminga %s percentile, 2023-26" % role, "%.0f" % k3.loc[role, "percentile"], "OBSERVED", "DESCRIPTIVE", rn6, "n6_primary_defender.csv")
            F("k_%s_z" % role, S, "Kuminga %s SEs" % role, "%+.1f" % k3.loc[role, "z"], "OBSERVED", "DESCRIPTIVE", rn6, "n6_primary_defender.csv")
            F("k_%s_n" % role, S, "Kuminga %s pairings" % role, int(k3.loc[role, "pairings"]), "OBSERVED", "FACT", rn6, "n6_primary_defender.csv")
            F("k_%s_poss" % role, S, "Kuminga %s possessions" % role, "{:,}".format(int(round(k3.loc[role, "poss"]))), "OBSERVED", "FACT", rn6, "n6_primary_defender.csv")
            F("k_%s_ref" % role, S, "reference %ss" % role, int(k3.loc[role, "n_reference"]), "OBSERVED", "FACT", rn6, "n6_primary_defender.csv")
        k26 = pdf[(pdf.window == "2025-26") & (pdf.player == "Jonathan Kuminga")].set_index("role")
        F("k_scorer_n26", S, "Kuminga scorer pairings 2025-26", int(k26.loc["scorer", "pairings"]), "OBSERVED", "FACT", rn6, "n6_primary_defender.csv")
        F("e_scorer_pct3", S, "Edwards scorer percentile, 2023-26", "%.0f" % e3.loc["scorer", "percentile"], "OBSERVED", "QUOTABLE", rn6, "n6_primary_defender.csv")
        F("e_scorer_z3", S, "Edwards scorer SEs, 2023-26", "%+.1f" % e3.loc["scorer", "z"], "OBSERVED", "QUOTABLE", rn6, "n6_primary_defender.csv")
        F("e_scorer_n3", S, "Edwards scorer pairings, 2023-26", int(e3.loc["scorer", "pairings"]), "OBSERVED", "FACT", rn6, "n6_primary_defender.csv")
        gs = csv("n6_gsw_analog.csv")
        gp = gs[gs.window == "2022-26 pooled"].set_index("unit")
        w_, wo = gp.loc["with a non-shooting centre"], gp.loc["without one"]
        F("gsw_with", S, "GSW units with a non-shooting centre, net", sgn(w_.net100, 1), "OBSERVED", "DESCRIPTIVE", rn6, "n6_gsw_analog.csv")
        F("gsw_without", S, "without one, net", sgn(wo.net100, 1), "OBSERVED", "DESCRIPTIVE", rn6, "n6_gsw_analog.csv")
        F("gsw_with_poss", S, "possessions with", "{:,}".format(int(w_.poss_off)), "OBSERVED", "FACT", rn6, "n6_gsw_analog.csv")
        F("gsw_without_poss", S, "possessions without", "{:,}".format(int(wo.poss_off)), "OBSERVED", "FACT", rn6, "n6_gsw_analog.csv")
        F("gsw_with_3par", S, "3PA rate with", "%.3f" % w_.fg3a_rate, "OBSERVED", "DESCRIPTIVE", rn6, "n6_gsw_analog.csv")
        F("gsw_without_3par", S, "3PA rate without", "%.3f" % wo.fg3a_rate, "OBSERVED", "DESCRIPTIVE", rn6, "n6_gsw_analog.csv")
        led = csv("n6_ledger.csv")
        gline = led[led.line.str.startswith("Next to a non-shooting")].value.iloc[0]
        F("gsw_se", S, "difference game-bootstrap SE", re.search(r"SE ([0-9.]+)\)", gline).group(1), "OBSERVED", "DESCRIPTIVE", rn6, "n6_ledger.csv")
        ps = csv("n6_postseason.csv").set_index("window")
        F("po_games", S, "Kuminga postseason games", int(ps.loc["all", "games"]), "OBSERVED", "FACT", rn6, "n6_postseason.csv")
        F("po_poss", S, "postseason possessions", "{:,}".format(int(ps.loc["all", "poss"])), "OBSERVED", "FACT", rn6, "n6_postseason.csv")
        F("po_net", S, "postseason on-court net", sgn(ps.loc["all", "net"], 1), "OBSERVED", "DESCRIPTIVE", rn6, "n6_postseason.csv")
        pline = led[led.line.str.startswith("Every playoff possession")].value.iloc[0]
        mo = re.search(r"on-off ([-+0-9.]+) with a game-bootstrap SE of ([0-9.]+) \((\d+) games\)", pline)
        F("po_onoff", S, "postseason on-off, garbage time out", mo.group(1), "OBSERVED", "DESCRIPTIVE", rn6, "n6_ledger.csv")
        F("po_onoff_se", S, "on-off SE", mo.group(2), "OBSERVED", "DESCRIPTIVE", rn6, "n6_ledger.csv")
        F("po_onoff_games", S, "stint games", mo.group(3), "OBSERVED", "FACT", rn6, "n6_ledger.csv")
        cr = csv("m5_creation_shares.csv")
        c26 = cr[cr.window == "2025-26"].set_index("player")
        F("k_usg", S, "Kuminga usage 2025-26", "%.3f" % c26.loc["Jonathan Kuminga", "usg_2025_26"], "OBSERVED", "QUOTABLE", rm5, "m5_creation_shares.csv")
        F("k_unast", S, "Kuminga unassisted share 2025-26", "%.0f%%" % (100 * c26.loc["Jonathan Kuminga", "unast_share"]), "OBSERVED", "QUOTABLE", rm5, "m5_creation_shares.csv")
        F("k_unast_pct", S, "percentile", "%.0f" % c26.loc["Jonathan Kuminga", "league_pct"], "OBSERVED", "QUOTABLE", rm5, "m5_creation_shares.csv")
        F("k_makes", S, "Kuminga makes 2025-26", int(c26.loc["Jonathan Kuminga", "fgm"]), "OBSERVED", "FACT", rm5, "m5_creation_shares.csv")
        cap = json.load(open(os.path.join(OUT, "cap_canonical.json"), encoding="utf-8"))["post_trade"]
        rcap = rid("green_resolution")
        y1, y2 = cap["kuminga_y1"], cap["kuminga_y2"]
        F("k_y1", S, "Kuminga year one", money(y1), "FACT", "FACT", rcap, "cap_canonical.json")
        F("k_y2", S, "Kuminga year two, player option", money(y2), "FACT", "FACT", rcap, "cap_canonical.json")
        F("k_total", S, "Kuminga total", money(y1 + y2), "FACT", "FACT", rcap, "cap_canonical.json")
        F("k_nonbird", S, "Non-Bird ceiling after an opt-out", money(round(1.2 * y1)), "FACT", "FACT", rcap, "cap_canonical.json (120% of year one)")
        po_ = csv("player_option.csv")
        flat = po_[po_.aging == "flat"]
        rpo = rid("player_option")
        F("k_optout_lo", S, "P(opt out), low across views, flat aging", "%.2f" % flat.p_opt_out.min(), "MODELED", "QUOTABLE AS BAND", rpo, "player_option.csv")
        F("k_optout_hi", S, "P(opt out), high", "%.2f" % flat.p_opt_out.max(), "MODELED", "QUOTABLE AS BAND", rpo, "player_option.csv")

        # ================= 5. EDWARDS, AND WHY BALL IS HERE ==============================
        S = "5. Edwards, and why Ball is here"
        chk = csv("m3_primary_defender_check.csv")
        ed = chk[chk.player == "Anthony Edwards"].set_index("variant")
        rchk = rid("m3_primary_defender_check")
        for v, lab in (("shipped", "M3 basis"), ("A", "rotation-defender baseline"), ("B", "regular season only"),
                       ("C", "both")):
            F("e_pct_" + v, S, "Edwards percentile, " + lab, "%.0f" % ed.loc[v, "percentile"], "OBSERVED", "QUOTABLE", rchk, "m3_primary_defender_check.csv")
            F("e_z_" + v, S, "Edwards SEs, " + lab, "%+.1f" % ed.loc[v, "z"], "OBSERVED", "QUOTABLE", rchk, "m3_primary_defender_check.csv")
        F("e_n_off", S, "top scorers in the reference", int(ed.loc["shipped", "n_offenders"]), "OBSERVED", "FACT", rchk, "m3_primary_defender_check.csv")
        F("e_pairings", S, "Edwards primary pairings 2025-26", int(ed.loc["shipped", "pairings"]), "OBSERVED", "FACT", rchk, "m3_primary_defender_check.csv")
        for nm, key in (("Anthony Edwards", "edw"), ("LaMelo Ball", "ball"), ("Ayo Dosunmu", "dos")):
            F("cr_%s" % key, S, "%s unassisted share of makes, 2025-26" % nm, "%.0f%%" % (100 * c26.loc[nm, "unast_share"]),
              "OBSERVED", "QUOTABLE", rm5, "m5_creation_shares.csv")
            F("cr_%s_pct" % key, S, "%s percentile" % nm, "%.0f" % c26.loc[nm, "league_pct"], "OBSERVED", "QUOTABLE", rm5, "m5_creation_shares.csv")
            F("usg_%s" % key, S, "%s usage 2025-26" % nm, "%.3f" % c26.loc[nm, "usg_2025_26"], "OBSERVED", "QUOTABLE", rm5, "m5_creation_shares.csv")
        F("cr_median", S, "league median unassisted share", "%.0f%%" % (100 * c26.loc["Anthony Edwards", "league_median"]), "OBSERVED", "QUOTABLE", rm5, "m5_creation_shares.csv")

        # ================= 6. CLUTCH ====================================================
        S = "6. Clutch"
        sp = csv("n7_late_clock_splits.csv")
        g7 = csv("n7_gates.csv").iloc[0]
        rn7 = rid("n7_late_clock")
        lg = sp[(sp.window == "2023-26 pooled") & (sp.team == "LEAGUE")].iloc[0]
        F("cl_start", S, "first season in the pooled clutch window", "2023-24", "FACT", "FACT", rn7,
          "n7_late_clock.py PREFIXES")
        F("cl_efg_all", S, "league eFG, all shots 2023-26", "%.3f" % lg.all_efg, "OBSERVED", "QUOTABLE", rn7, "n7_late_clock_splits.csv")
        F("cl_efg_clutch", S, "league eFG, clutch", "%.3f" % lg.clutch_efg, "OBSERVED", "QUOTABLE", rn7, "n7_late_clock_splits.csv")
        F("cl_un_all", S, "league unassisted share, all", "%.0f%%" % (100 * lg.all_unast), "OBSERVED", "QUOTABLE", rn7, "n7_late_clock_splits.csv")
        F("cl_un_clutch", S, "league unassisted share, clutch", "%.0f%%" % (100 * lg.clutch_unast), "OBSERVED", "QUOTABLE", rn7, "n7_late_clock_splits.csv")
        shots = pd.read_parquet(os.path.join(OUT, "n7_shots.parquet"))
        shots["efg_pts"] = np.where(shots.made, np.where(shots.val == 3, 1.5, 1.0), 0.0)
        shots["clutch"] = (shots.period >= 4) & (shots.clock <= 300) & (shots.margin_before <= 5)
        lgdrop = lg.clutch_efg - lg.all_efg
        cre = sp[(sp.window == "2023-26 pooled") & (sp.team != "LEAGUE")]
        zs = {}
        for _, x in cre.iterrows():
            d = shots[shots.pid == x.pid]
            c = d[d.clutch].efg_pts
            diff = (c.mean() - d.efg_pts.mean()) - lgdrop
            zs[x.player] = (diff, diff / np.sqrt(c.var(ddof=1) / len(c)), bool(x.clutch_thin))
        ok = {k: v for k, v in zs.items() if not v[2]}
        big = sorted([(k, v[1]) for k, v in ok.items() if abs(v[1]) >= 2], key=lambda kv: -kv[1])
        F("cl_n_ok", S, "creators with enough clutch shots", len(ok), "OBSERVED", "FACT", rn7, "n7_late_clock_splits.csv, n7_shots.parquet")
        F("cl_n_big", S, "beyond the league drop by 2 SEs", len(big), "OBSERVED", "QUOTABLE", rn7, "n7_shots.parquet")
        F("cl_chance", S, "expected by chance", "%.1f" % (2 * 0.02275 * len(ok)), "COMPOSED", "QUOTABLE", rn7, "n7_shots.parquet")
        for i, (k, z) in enumerate(big):
            F("cl_big%d" % (i + 1), S, "creator beyond the drop", k, "OBSERVED", "QUOTABLE", rn7, "n7_shots.parquet")
            F("cl_big%d_z" % (i + 1), S, "SEs", "%+.1f" % z, "OBSERVED", "QUOTABLE", rn7, "n7_shots.parquet")
        for nm, key in (("Anthony Edwards", "edw"), ("LaMelo Ball", "ball")):
            x = cre[cre.player == nm].iloc[0]
            F("cl_%s_efg" % key, S, "%s clutch eFG" % nm, "%.3f" % x.clutch_efg, "OBSERVED", "QUOTABLE", rn7, "n7_late_clock_splits.csv")
            F("cl_%s_fga" % key, S, "%s clutch attempts" % nm, int(x.clutch_fga), "OBSERVED", "FACT", rn7, "n7_late_clock_splits.csv")
            F("cl_%s_z" % key, S, "%s beyond the drop, SEs" % nm, "%+.1f" % zs[nm][1], "OBSERVED", "QUOTABLE", rn7, "n7_shots.parquet")
        F("lc_g1", S, "late-clock reconstruction accuracy, within 2 s", "%.1f%%" % (100 * g7.g1_within2), "OBSERVED", "WITHHELD", rn7, "n7_gates.csv")
        F("lc_bar", S, "bar set in advance", "80%", "ASSUMED", "FACT", rn7, "n7_late_clock.py MIN_G1")

        # ================= 7. WHAT TO WATCH =============================================
        S = "7. What to watch"
        for n_, x in n8.iterrows():
            F("w%d_claim" % n_, S, "claim %d" % n_, x.claim, "COMPOSED", "QUOTABLE", rn8, "n8_watch_list.csv")
            F("w%d_now" % n_, S, "claim %d current value" % n_, x.current, x.label.split(",")[0].upper(), "QUOTABLE", rn8, "n8_watch_list.csv")
            F("w%d_flip" % n_, S, "claim %d flips if" % n_, x.threshold, "COMPOSED", "QUOTABLE", rn8, "n8_watch_list.csv")
        F("w_game", S, "checkpoint game", "20", "ASSUMED", "FACT", rn8, "n8_watch_list.py N_CHECK")

        # ================= 8. THE BILL ==================================================
        S = "8. The bill"
        gr = csv("green_resolution.csv").set_index("step")
        for key, step in (("chain_start", "pre-trade Apron Team Salary (2026-08-27)"), ("chain_green", "out: Josh Green"),
                          ("chain_williams", "in: Cody Williams"), ("chain_konchar", "in: John Konchar"),
                          ("chain_stretch", "waive Konchar, stretch over 3 seasons"),
                          ("chain_dollar", "McDaniels, our book $26,200,001 vs Spotrac $26,200,000"),
                          ("chain_post", "post-trade Apron Team Salary (2026-09-04)"), ("chain_kuminga", "sign Kuminga, taxpayer MLE year 1"),
                          ("chain_final", "final Apron Team Salary"), ("room_hard_cap", "room under second apron, with Kuminga"),
                          ("over_first", "over first apron, with Kuminga"), ("over_tax", "over tax line, with Kuminga"),
                          ("dead_year", "dead money 2026-27")):
            F(key, S, step, money(abs(gr.loc[step, "amount"])), "FACT", "FACT", rcap, "green_resolution.csv")
        ga = csv("green_asset_cost.csv").iloc[0]
        F("dead_future", S, "Konchar dead money in 2027-28 and 2028-29", money(ga.dead_money_future), "FACT", "FACT", rid("green_resolution"), "green_asset_cost.csv")
        F("williams_option", S, "Williams 2027-28 club option", "$7,669,890", "FACT", "FACT", rcap, "green_asset_cost.csv detail")
        dfs = csv("dosunmu_final_states.csv")
        rdfs = rid("dosunmu_final_states")
        happened = dfs[dfs.state.str.startswith("ACTUAL: Green traded out")].iloc[0]
        cheapest = dfs[dfs.state.str.startswith("MODELLED: Green traded out")].iloc[0]
        nodos = dfs[dfs.state.str.startswith("CF: veteran min (2-yr charge) + Kuminga at the ceiling")].iloc[0]
        stuck = dfs[dfs.state.str.startswith("ACTUAL: Dosunmu + Green")].iloc[0]
        F("dos_nodos_kuminga", S, "no-Dosunmu branch: most Kuminga could be paid from the non-taxpayer MLE",
          money(8254095), "FACT", "FACT", rdfs, "dosunmu_final_states.csv note")
        assert "8,254,095" in nodos.note
        F("dos_stuck_over", S, "Dosunmu + Green + Kuminga, over the hard cap by", money(-stuck.vs_second_apron), "FACT", "FACT", rdfs, "dosunmu_final_states.csv")
        for key, row_ in (("dos_happened", happened), ("dos_cheapest", cheapest), ("dos_nodos", nodos)):
            F(key + "_pay", S, key + " payroll, tax basis", money(row_.tax_basis_payroll), "FACT", "FACT", rdfs, "dosunmu_final_states.csv")
            F(key + "_apron", S, key + " payroll, apron basis", money(row_.apron_payroll), "FACT", "FACT", rdfs, "dosunmu_final_states.csv")
            F(key + "_tax", S, key + " estimated tax", "$%.1fM" % (row_.est_tax_bill / 1e6), "FACT", "FACT", rdfs, "dosunmu_final_states.csv")
        F("dos_dump_payroll", S, "extra payroll from taking Williams and Konchar", money(happened.apron_payroll - cheapest.apron_payroll),
          "FACT", "FACT", rdfs, "dosunmu_final_states.csv")
        F("dos_dump_tax", S, "extra tax", "$%.1fM" % ((happened.est_tax_bill - cheapest.est_tax_bill) / 1e6), "FACT", "FACT", rdfs,
          "dosunmu_final_states.csv")

        # ================= APPENDIX ====================================================
        S = "Appendix"
        # ---- D92: figures the drafts had to write around, now keyed ---------------------
        # The pre-refit state is the snapshot chain.py preserved before the D90 run; the
        # runs cited are the ones that produced those files at the time.
        PRE = os.path.join(OUT, ".pre_refit_snapshot")
        PRE_MARKET_RUN = "market_devig_20260916T195853Z"
        PRE_SIM_RUN, PRE_SIM_RUN_AGED = "run_sim_20260916T173222Z", "run_sim_20260916T195902Z"
        pre_m = pd.read_csv(os.path.join(PRE, "market_devig_2026_27.csv")).set_index("team_abbr")
        F("cha_model_pre", S, "CHA model title odds before the refit", pct(pre_m.loc["CHA", "model_pct"]),
          "MODELED", "QUOTABLE", PRE_MARKET_RUN, ".pre_refit_snapshot/market_devig_2026_27.csv")
        F("cha_gap_pre", S, "CHA model minus market before the refit, points", sgn(pre_m.loc["CHA", "diff_pp"], 2),
          "MODELED", "QUOTABLE", PRE_MARKET_RUN, ".pre_refit_snapshot/market_devig_2026_27.csv")
        F("cha_gap_now", S, "CHA model minus market now, points", sgn(mk.loc["CHA", "diff_pp"], 2),
          "MODELED", "QUOTABLE", rm, "market_devig_2026_27.csv")
        for key, sub, run_ in (("title_pre", "", PRE_SIM_RUN), ("title_aged_pre", "aged", PRE_SIM_RUN_AGED)):
            sim_pre = pd.read_csv(os.path.join(PRE, sub, "sim_all30_2026_27.csv"))
            F(key, S, "MIN title probability before the refit, mean of four views%s" % (", aged" if sub else ""),
              pct(100 * sim_pre[sim_pre.team_abbr == "MIN"].title_current.mean()), "MODELED", "QUOTABLE AS BAND",
              run_, ".pre_refit_snapshot/%ssim_all30_2026_27.csv" % (sub + "/" if sub else ""))
        cmp_ = pd.read_csv(os.path.join(REPO, "offseason", "data", "d89_rapm_before_after.csv"))
        rcmp = rid("d89_rapm_compare")
        F("cons_rapm_corr", S, "consensus-RAPM correlation across players, net, after the refit",
          "%.3f" % cmp_.consensus_net_after.corr(cmp_.net_rapm_after), "COMPOSED", "QUOTABLE", rcmp,
          "d89_rapm_before_after.csv")
        F("cons_rapm_corr_pre", S, "consensus-RAPM correlation across players, net, before the refit",
          "%.3f" % cmp_.consensus_net_before.corr(cmp_.net_rapm_before), "COMPOSED", "QUOTABLE", rcmp,
          "d89_rapm_before_after.csv")
        for who, nm in (("k", "Jonathan Kuminga"), ("ball", "LaMelo Ball")):
            row_ = cmp_[cmp_.player_name == nm].iloc[0]
            F(who + "_rapm_pre", S, "%s net RAPM before the refit" % nm, sgn(row_.net_rapm_before, 2), "MODELED",
              "QUOTABLE", rcmp, "d89_rapm_before_after.csv")
            F(who + "_rapm_post", S, "%s net RAPM after the refit" % nm, sgn(row_.net_rapm_after, 2), "MODELED",
              "QUOTABLE", rcmp, "d89_rapm_before_after.csv")
            F(who + "_cons_pre", S, "%s consensus net before the refit" % nm, sgn(row_.consensus_net_before, 2),
              "MODELED", "QUOTABLE", rcmp, "d89_rapm_before_after.csv")
            F(who + "_cons_post", S, "%s consensus net after the refit" % nm, sgn(row_.consensus_net_after, 2),
              "MODELED", "QUOTABLE", rcmp, "d89_rapm_before_after.csv")
        VAL = os.path.join(REPO, "postmortem", "outputs", "tables", "validation")
        # measured on the FROZEN stint caches, built before either fix: a fresh build can no
        # longer show the defect (D92)
        st_ = pd.read_csv(os.path.join(VAL, "stint_points_reconciliation_cache.csv"))
        F("misplaced_lineup", S, "share of points the old lineup pipeline credited to the wrong team",
          pct(100 * st_.err_possession.abs().sum() / st_.box_points.sum()), "OBSERVED", "QUOTABLE",
          rid("validate_stint_points"), "postmortem stint_points_reconciliation_cache.csv")
        po_ = pd.read_csv(os.path.join(VAL, "possession_points_reconciliation.csv"))
        F("misplaced_possession", S, "share of possession points the old attribution credited to the wrong team",
          pct(100 * po_.err_legacy.abs().sum() / po_.box_points.sum()), "OBSERVED", "QUOTABLE",
          rid("validate_possession_points"), "postmortem possession_points_reconciliation.csv")
        F("val_lineup_teamgames", S, "team-games in the lineup-grain check", len(st_), "FACT", "FACT",
          rid("validate_stint_points"), "postmortem stint_points_reconciliation_cache.csv")
        F("val_possession_teamgames", S, "team-games in the possession-grain check", len(po_), "FACT", "FACT",
          rid("validate_possession_points"), "postmortem possession_points_reconciliation.csv")

        F("off_delta_u", S, "offseason delta, un-aged", sgn(gate.loc["offseason delta", "unaged_mean"], 2), "MODELED", "NOT QUOTABLE", rw2, "w2_aging_gate.csv")
        F("off_delta_a", S, "offseason delta, aged", sgn(gate.loc["offseason delta", "aged_mean"], 2), "MODELED", "NOT QUOTABLE", rw2, "w2_aging_gate.csv")
        tail = csv("f4b_tail_players.csv")
        rf4 = rid("f4_per_view_disagreement")
        for i, x in tail.iterrows():
            base = "tail%02d" % i
            F(base + "_player", S, "tail player", "%s (%s)" % (x.player, x.team), "OBSERVED", "DESCRIPTIVE", rf4, "f4b_tail_players.csv")
            F(base + "_poss", S, "possessions", "{:,}".format(int(x.possessions)), "OBSERVED", "FACT", rf4, "f4b_tail_players.csv")
            for f in FORKS:
                F(base + "_" + f, S, f, "%+.2f" % x[f], "MODELED", "DESCRIPTIVE", rf4, "f4b_tail_players.csv")
        for i, tm in enumerate(f4a.sort_values("abs_mean_gap", ascending=False).index[:8].tolist() +
                               (["MIN"] if "MIN" not in f4a.sort_values("abs_mean_gap", ascending=False).index[:8] else [])):
            x = f4a.loc[tm]
            base = "pv_%s" % tm.lower()
            F(base + "_mkt", S, "%s market" % tm, pct(x.market_pct), "OBSERVED", "QUOTABLE", rf4, "f4a_per_view_disagreement.csv")
            for f in FORKS:
                F(base + "_" + f, S, "%s %s" % (tm, f), pct(x["pct_" + f]), "MODELED", "QUOTABLE AS BAND", rf4, "f4a_per_view_disagreement.csv")
            F(base + "_label", S, "%s label" % tm, x.label, "MODELED", "QUOTABLE", rf4, "f4a_per_view_disagreement.csv")

        # C5: the Bet series additions (C1 to C4) live on the same sheet
        import bet_numbers
        bet_numbers.add(F, rid, csv)

        df = pd.DataFrame(rows)
        missing = df[df.run_id.isna() | (df.run_id == "") | (df.run_id == "n/a")]
        if len(missing):
            raise RuntimeError("figures without a run id: %s" % list(missing.key))
        df.to_csv(OUT_CSV, index=False)
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write("# Final numbers, piece 2\n\n*Run `%s`. %d figures, every one with a run ID. "
                     "Anything not here does not go in the piece.*\n\n" % (r.run_id, len(df)))
            for sec, d in df.groupby("section", sort=False):
                fh.write("## %s\n\n| key | figure | value | label | verdict | run |\n|---|---|---|---|---|---|\n" % sec)
                for _, x in d.iterrows():
                    fh.write("| `%s` | %s | %s | %s | %s | `%s` |\n" % (x.key, x.figure, x.value, x.label, x.verdict, x.run_id))
                fh.write("\n")
        r.note("%d figures on the sheet across %d sections" % (len(df), df.section.nunique()))
        r.output(OUT_CSV, rows=len(df))
        r.output(OUT_MD)


if __name__ == "__main__":
    main()
