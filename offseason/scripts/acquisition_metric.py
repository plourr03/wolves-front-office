#!/usr/bin/env python3
"""
acquisition_metric.py

Assembles the four components into the acquisition-metric output for a target,
across the Wolves' exit scenarios: a one-page profile, a conditional verdict
matrix (target x scenario), and a tier by a written rule. Gates before it scores.

Components (all traced to the built data layer):
  1. Feasibility (gate)  evaluate_move salary matching + the apron/Dosunmu reality,
                         plus a comp-anchored asset-cost read vs the Wolves chest.
  2. Contract/timeline   from the contracts file (salary, expiry, options, age).
  3. Need-fit            target's player_dimensions profile dotted with the
                         scenario need vector, with a role adjustment (a wing does
                         not fill a center-sized rim-protection hole).
  4. Impact              net RAPM with its band, the playoff-translation read, and
                         an age-decline note.

No fake precision: trade cost is a comp-anchored range, impact carries its interval,
feasibility is a category with the binding constraint named. Availability is an
explicit assumption (we analyze the decision space, not report a deal as done).

    python acquisition_metric.py "Kawhi Leonard"
"""

import os
import sys
import csv
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUTDIR = os.path.join(HERE, "..", "outputs", "acquisition_profiles")
sys.path.insert(0, HERE)
from evaluate_move import evaluate_move, load_team_state, load_constants, matching_limit  # noqa

DIMS = ["hc_creation", "secondary_playmaking", "off_ball_shooting",
        "def_versatility_poa", "rim_protect_reb", "transition"]

# Wolves-specific config (the exit scenarios as outgoing packages from base).
# (name, 2026-27 salary, outbound trade-kicker pct). Gobert carries a 7.5% kicker.
REMOVED = {
    "status_quo": [],
    "randle_out": [("Julius Randle", 33_333_334, 0.0)],
    "gobert_out": [("Rudy Gobert", 36_500_000, 0.075)],
    "both_out": [("Julius Randle", 33_333_334, 0.0), ("Rudy Gobert", 36_500_000, 0.075)],
}
DOSUNMU_OUT_RULE = 58_500_000   # must send >= this to re-sign Dosunmu under the 2nd-apron hard cap
# Wolves chest (from team_state tradeable_firsts + young players).
CHEST = "two tradeable firsts (2028, 2033 own outright) plus young players (Shannon, Clark) and filler/seconds"
BIG_POSITIONS = ("C", "C-F", "F-C")


def _csv_lookup(path, key, needle):
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if needle.lower() in (r.get(key, "") or "").lower():
            return r
    return None


def load_target(name):
    con = _csv_lookup(os.path.join(DATA, "nba_contracts_2026_27.csv"), "player", name)
    val = _csv_lookup(os.path.join(DATA, "player_value.csv"), "player_name", name)
    if not con or not val:
        raise ValueError(f"target '{name}' not found in contracts/value tables")
    pid = val["player_id"]
    dim = next((r for r in csv.DictReader(open(os.path.join(DATA, "player_dimensions.csv"), encoding="utf-8"))
                if r["player_id"] == pid), None)
    def _f(key, default=None):
        v = (val.get(key) or "").strip()
        try:
            return float(v)
        except ValueError:
            return default

    net_rapm = _f("net_rapm", 0.0)
    return {
        "name": con["player"], "pid": pid, "team": con["team_abbr"],
        "position": con["position"], "salary": int(con["salary_2026_27"] or 0),
        "expiring": not (con.get("salary_2027_28") or "").strip(),
        "player_option_year": con.get("player_option_year", ""),
        "net_rapm": net_rapm, "net_sd": _f("net_sd", 1.6),
        "off_rapm": _f("off_rapm", 0.0), "def_rapm": _f("def_rapm", 0.0),
        "box_net_bpm": _f("box_net_bpm", 0.0), "reliable": val["reliable"],
        # consensus (RAPM + external BBR) is the impact point used for scoring; falls
        # back to RAPM where no external metric matched.
        "bbr_bpm": _f("bbr_bpm"), "consensus_net": _f("consensus_net", net_rapm),
        "divergence": _f("impact_divergence"), "corroborated": val.get("externally_corroborated", ""),
        "playoff_read": val.get("translation_read", ""), "po_delta": val.get("rs_to_po_delta", ""),
        "dims": {d: float(dim[d]) for d in DIMS} if dim else {d: 0.0 for d in DIMS},
    }


def load_needs():
    needs = {}
    for r in csv.DictReader(open(os.path.join(DATA, "need_vectors.csv"), encoding="utf-8")):
        needs.setdefault(r["scenario"], {})[r["dimension"]] = float(r["need"])
    return needs


# --- Component 1: feasibility ------------------------------------------------ #
def feasibility(scenario, tgt, base_ts, const):
    removed = REMOVED[scenario]
    incoming = [{"label": tgt["name"], "salary": tgt["salary"]}]

    if not removed:
        return {"category": "infeasible", "constraint":
                "over the cap with nothing large enough to match; cannot absorb a "
                f"${tgt['salary']:,} salary without sending salary out", "package": None}

    outgoing = [{"label": n, "salary": s, "trade_kicker_pct": k} for (n, s, k) in removed]
    # kicker-inflated outgoing raises the take-back limit; add filler only if still short
    out_match = sum(p["salary"] * (1 + p["trade_kicker_pct"]) for p in outgoing)
    filler = max(0, tgt["salary"] - matching_limit(out_match, base_ts["tier"], const))
    if filler > 0:
        outgoing.append({"label": "salary filler", "salary": round(filler + 500_000)})
    r = evaluate_move(base_ts, const, outgoing, incoming)

    out_base = sum(p["salary"] for p in outgoing)            # base shed, for Dosunmu rule + apron
    keeps_dosunmu = out_base >= DOSUNMU_OUT_RULE
    new_apron = base_ts["apron_team_salary"] - out_base + tgt["salary"]
    if not r["legal"]:
        return {"category": "infeasible", "constraint": r["failing_constraint"],
                "package": outgoing, "new_apron": new_apron}
    if keeps_dosunmu and new_apron < const["second_apron"]:
        cat, constraint = "feasible", (f"send ${out_base:,}, take ${tgt['salary']:,}; "
                                       f"sheds enough to re-sign Dosunmu and stay under the second apron")
    else:
        cat = "stretch"
        constraint = (f"salary-legal, but sending only ${out_base:,} while taking back "
                      f"${tgt['salary']:,} balloons the apron; keeping Dosunmu needs "
                      f">= ${DOSUNMU_OUT_RULE:,} out, so this works only by NOT re-signing "
                      f"Dosunmu or sending additional salary")
    return {"category": cat, "constraint": constraint, "package": outgoing,
            "new_apron": round(new_apron)}


# --- Component 3: need-fit (with role adjustment) ---------------------------- #
def need_fit(tgt, need_vec):
    is_big = tgt["position"] in BIG_POSITIONS
    num = den = 0.0
    filled, unfilled = [], []
    for d in DIMS:
        need = max(0.0, need_vec.get(d, 0.0))
        if need <= 0.05:
            continue
        contrib = tgt["dims"][d]
        # role adjustment: a non-big without elite rim numbers cannot fill a center-
        # sized rim-protection hole. Elite rim forwards (Giannis-type, >=0.85) keep credit.
        if d == "rim_protect_reb" and not is_big and contrib < 0.85:
            contrib = min(contrib, 0.40)
        num += need * contrib
        den += need
        (filled if contrib >= 0.60 else unfilled).append((d, round(need, 2), round(tgt["dims"][d], 2)))
    score = (num / den) if den else 0.0
    return {"score": round(score, 3), "filled": filled, "unfilled": unfilled, "is_big": is_big}


# --- Component 4: impact ----------------------------------------------------- #
PLAYOFF_MULT = {"holds_up": 1.05, "neutral": 1.0, "slips": 0.88, "insufficient_po_sample": 0.97}


def impact_score(tgt, age):
    """Impact composite at the posterior MEAN and at the downside (lower band), so a
    wide-interval bet is treated differently from a steady one. The impact spine is
    sanity-checked against box BPM (r=0.77) but NOT externally validated (EPM/DARKO/
    LEBRON are Pass-2), and box BPM shares the RAPM prior, so any impact-decided
    verdict is provisional."""
    pmult = PLAYOFF_MULT.get(tgt["playoff_read"], 1.0)
    amult = 0.90 if (age and age >= 34) else 1.0
    point = tgt["consensus_net"]                       # consensus (RAPM + external BBR)

    def comp(net):
        return max(0.0, min(1.0, net / 8.0)) * pmult * amult

    lo = point - 1.96 * tgt["net_sd"]
    hi = point + 1.96 * tgt["net_sd"]
    # provisional if internal uncertainty is high OR the external metric disagrees
    wide = (tgt["net_sd"] >= 1.6 or tgt["reliable"] != "TRUE"
            or tgt["playoff_read"] in ("slips", "insufficient_po_sample")
            or tgt.get("corroborated") == "FALSE")
    return {"composite": round(comp(point), 3),
            "composite_downside": round(comp(lo), 3),
            "playoff_mult": pmult, "age_mult": amult, "point": round(point, 2),
            "band": (round(lo, 1), round(hi, 1)), "wide_band": wide}


def tier_for(score):
    if score >= 0.50:
        return "priority target"
    if score >= 0.38:
        return "worth pursuing"
    if score >= 0.25:
        return "situational"
    return "pass"


def top_need_dim(need_vec):
    d = max(need_vec, key=lambda k: need_vec[k])
    return d, need_vec[d]


def run(target_name, age=None, availability_note=""):
    const = load_constants("2026-27")
    base_ts = load_team_state("MIN", "2026-27", "base")
    tgt = load_target(target_name)
    needs = load_needs()

    matrix = []
    for scen in ["status_quo", "randle_out", "gobert_out", "both_out"]:
        feas = feasibility(scen, tgt, base_ts, const)
        nf = need_fit(tgt, needs[scen])
        imp = impact_score(tgt, age)
        gate_ok = feas["category"] in ("feasible", "stretch")
        score = round(nf["score"] * imp["composite"], 3) if gate_ok else 0.0
        score_dn = round(nf["score"] * imp["composite_downside"], 3) if gate_ok else 0.0
        # contingent companion move: is the scenario's TOP need left unfilled?
        tnd, tneed = top_need_dim(needs[scen])
        contingent = (tnd if (gate_ok and tneed > 0.05 and tnd in [d for d, _, _ in nf["unfilled"]])
                      else None)
        if feas["category"] == "infeasible":
            tier = "infeasible"
        else:
            tier = tier_for(score)
            if feas["category"] == "stretch":
                tier += " (feasibility-gated)"
            if imp["wide_band"] and tier_for(score_dn) != tier_for(score):
                tier += f" / {tier_for(score_dn)} on the downside band"
        matrix.append({"scenario": scen, "feasibility": feas, "need_fit": nf, "impact": imp,
                       "score": score, "score_downside": score_dn,
                       "contingent_on": contingent, "tier": tier})

    feasible_rows = [m for m in matrix if m["feasibility"]["category"] == "feasible"]
    if feasible_rows:
        best, gate = max(feasible_rows, key=lambda m: m["score"]), "feasible"
    elif any(m["feasibility"]["category"] == "stretch" for m in matrix):
        best = max([m for m in matrix if m["feasibility"]["category"] == "stretch"], key=lambda m: m["score"])
        gate = "stretch"
    else:
        best, gate = matrix[0], "infeasible"

    overall = build_overall(best, gate)
    overall_scen = best["scenario"] if gate != "infeasible" else None
    write_profile(tgt, matrix, overall, overall_scen, age, availability_note)
    return tgt, matrix, overall, overall_scen


def build_overall(best, gate):
    if gate == "infeasible":
        return "INFEASIBLE (no exit scenario yields a legal, apron-viable deal)"
    parts = [tier_for(best["score"])]
    if gate == "stretch":
        parts[0] += " (only via a stretch scenario)"
    parts.append(f"via {best['scenario']}")
    if best["contingent_on"]:
        parts.append(f"CONTINGENT on a companion {best['contingent_on']} move")
    if best["impact"]["wide_band"]:
        parts.append("PROVISIONAL: wide impact band, not yet externally validated")
    return "; ".join(parts)


def write_profile(tgt, matrix, overall, overall_scen, age, availability_note):
    os.makedirs(OUTDIR, exist_ok=True)
    slug = tgt["name"].lower().replace(" ", "_").replace(".", "")
    path = os.path.join(OUTDIR, f"{slug}.md")
    L = []
    L.append(f"# Acquisition profile: {tgt['name']}")
    L.append(f"\n_Target of the Minnesota Timberwolves, 2026-27. Generated by acquisition_metric.py. "
             f"Availability is an assumption: {availability_note or 'flagged, not confirmed'}._\n")
    lo, hi = matrix[0]["impact"]["band"]
    bbr = f"{tgt['bbr_bpm']:+.2f}" if tgt["bbr_bpm"] is not None else "n/a"
    L.append(f"**Snapshot.** {tgt['position']}, {tgt['team']}, ${tgt['salary']:,} in 2026-27"
             f"{' (expiring; rental)' if tgt['expiring'] else ''}"
             f"{f', age ~{age}' if age else ''}. "
             f"Consensus impact {tgt['consensus_net']:+.2f} (95% band {lo:+.1f} to {hi:+.1f}), "
             f"blending RAPM {tgt['net_rapm']:+.2f} and external BBR BPM {bbr} "
             f"(divergence {tgt['divergence']}, externally corroborated: {tgt['corroborated']}). "
             f"Playoff half-court read: **{tgt['playoff_read']}**.")
    L.append(f"\n**Overall verdict: {overall}.**\n")
    L.append("_Impact is the CONSENSUS of our possession-based RAPM and an independent external "
             "metric (Basketball-Reference BPM; league-wide corr 0.74). Where the two agree the "
             "verdict is firm; where they diverge (externally corroborated = FALSE) it stays "
             "provisional. DARKO/EPM/LEBRON remain a Pass-2 add. Read the downside column, not just "
             "the mean._\n")

    L.append("## Conditional verdict matrix\n")
    L.append("| Scenario | Feasibility | Need-fit | Impact (mean / downside) | Score (mean / downside) | Tier |")
    L.append("|---|---|---|---|---|---|")
    for m in matrix:
        cflag = f" (needs companion {m['contingent_on']})" if m["contingent_on"] else ""
        L.append(f"| {m['scenario']} | {m['feasibility']['category']} | "
                 f"{m['need_fit']['score']:.2f} | {m['impact']['composite']:.2f} / {m['impact']['composite_downside']:.2f} | "
                 f"{m['score']:.2f} / {m['score_downside']:.2f} | {m['tier']}{cflag} |")

    L.append("\n## Feasibility detail (the gate)\n")
    for m in matrix:
        f = m["feasibility"]
        pkg = (", ".join(f"{p['label']} ${p['salary']:,}" for p in f["package"])
               if f.get("package") else "no viable outgoing")
        L.append(f"- **{m['scenario']}** ({f['category']}): {f['constraint']}. Outgoing: {pkg}.")
    L.append(f"\nAsset cost: comp-anchored. As an aging, expiring, injury-risk star, "
             f"{tgt['name']} prices below a prime star. Comps (nba_trade_comps): Jimmy Butler "
             f"(one protected first plus a starter), Brandon Ingram on an expiring (one first plus "
             f"expirings), Kevin Durant at 36 (a young scorer, a veteran, a pick, seconds). Range: "
             f"roughly one first plus a young rotation player and/or expiring salary, with seconds. "
             f"The Wolves chest ({CHEST}) covers that, so asset cost is feasible, not the binding "
             f"constraint. The binding constraint is the apron, above.")
    L.append(f"\nFiller note: in the single-big scenarios the match is only legal with salary filler "
             f"sent ON TOP of the headline big (a ${tgt['salary']:,} incoming cannot be absorbed by one "
             f"sub-$37M outgoing under the brackets). That filler is modeled as replacement-level outgoing; "
             f"its real identity, a rotation piece versus a throwaway, changes both the apron math and the "
             f"returning roster and must be set when a concrete deal is built. Outbound trade kickers (e.g. "
             f"Gobert's) further inflate the outgoing number and are a Pass-2 contract fill.")

    L.append("\n## Need-fit detail\n")
    for m in matrix:
        nf = m["need_fit"]
        fil = ", ".join(f"{d} (need {n}, fills {v})" for d, n, v in nf["filled"]) or "none"
        unf = ", ".join(f"{d} (need {n}, only {v})" for d, n, v in nf["unfilled"]) or "none"
        L.append(f"- **{m['scenario']}** (fit {nf['score']:.2f}): fills {fil}. Gaps left: {unf}.")
    if tgt["position"] in BIG_POSITIONS or tgt["dims"]["rim_protect_reb"] >= 0.85:
        L.append(f"\nRole note: {tgt['name']} ({tgt['position']}, rim-protect pctile "
                 f"{tgt['dims']['rim_protect_reb']:.2f}) fills a center-sized rim-protection need DIRECTLY. "
                 f"No role cap applied: this is exactly why a rim presence clears the both-out hole a wing cannot.")
    else:
        L.append(f"\nRole adjustment applied: {tgt['name']} ({tgt['position']}, rim-protect pctile "
                 f"{tgt['dims']['rim_protect_reb']:.2f}) cannot fill a center-sized rim-protection need; his "
                 f"contribution there is capped (a wing does not replace a rim protector).")

    L.append("\n## Impact and playoff translation\n")
    im = matrix[0]["impact"]
    bbr = f"{tgt['bbr_bpm']:+.2f}" if tgt["bbr_bpm"] is not None else "n/a"
    agree = ("methods agree, impact FIRM" if tgt["corroborated"] == "TRUE"
             else "methods DISAGREE, impact provisional" if tgt["corroborated"] == "FALSE"
             else "no external match")
    L.append(f"- Consensus impact {im['point']:+.2f} = blend of RAPM {tgt['net_rapm']:+.2f} and external "
             f"BBR BPM {bbr}; 95% band {im['band'][0]:+.1f} to {im['band'][1]:+.1f}, reliable={tgt['reliable']}. "
             f"Divergence {tgt['divergence']} ({agree}). Composite {im['composite']:.2f} at the mean, "
             f"{im['composite_downside']:.2f} on the downside band"
             f"{' (WIDE band: read as a bet)' if im['wide_band'] else ''}.")
    L.append(f"- Playoff half-court read **{tgt['playoff_read']}** (RS-to-PO delta {tgt['po_delta']}); "
             f"applied as a {im['playoff_mult']}x multiplier. Age multiplier {im['age_mult']}x.")

    L.append("\n## What would change this verdict\n")
    L.append("- If the Wolves solve rim protection separately (keep a center, or pair this move with a "
             "cheap rim protector), the both-out fit rises materially.")
    L.append("- If they will not re-sign Dosunmu, the single-big scenarios open up (the apron constraint "
             "relaxes), changing the feasible set.")
    L.append("- The playoff read sits on a small recent sample; a healthy deep run would lift the "
             "translation multiplier. Health and availability are the dominant swing factors.")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"profile -> {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default="Kawhi Leonard")
    ap.add_argument("--age", type=int, default=None)
    ap.add_argument("--availability", default="")
    args = ap.parse_args()

    def safe(s):
        return str(s).encode("ascii", "replace").decode()

    tgt, matrix, overall, scen = run(args.target, age=args.age, availability_note=args.availability)
    print(f"\n=== {safe(tgt['name'])} ({tgt['position']}, ${tgt['salary']:,}"
          f"{', expiring' if tgt['expiring'] else ''}) ===")
    print(f"net RAPM {tgt['net_rapm']:+.2f}+/-{tgt['net_sd']:.2f} | playoff {tgt['playoff_read']}")
    print(f"\n{'scenario':12} {'feasibility':12} {'need_fit':>8} {'impact':>7} {'score':>6}  tier")
    for m in matrix:
        print(f"{m['scenario']:12} {m['feasibility']['category']:12} "
              f"{m['need_fit']['score']:>8.2f} {m['impact']['composite']:>7.2f} "
              f"{m['score']:>6.2f}  {m['tier']}")
    print(f"\nOVERALL TIER: {overall.upper()}" + (f"  (best via {scen})" if scen else ""))
