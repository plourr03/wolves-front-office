#!/usr/bin/env python3
"""
build_opponent_profiles.py  -- Championship layer, Component C.

Consumes the projected contender rosters (offseason/data/opponent_rosters.json,
produced by the opponent-profiles workflow) and turns each into a quantified
structural profile via the validated Components A and B:
  - team offensive / defensive / net rating in RS and playoff modes, with interval
    and method_uncertainty (the RAPM-vs-box defensive disagreement),
  - the six-dimension team identity profile (same space as the need-fit layer),
  - the scouted qualitative identity (offense, defense, rim, switch, where-they-crack)
    and the assumed moves carried through for eyeballing.

Explicit Wembanyama check: the Spurs are the team we most want to beat and Wemby is a
method-divergent rim protector like Gobert, so we verify the defensive reweighting
preserved his rim deterrence rather than letting the box view wash it out. We report
SAS's team defense under the reweighted consensus vs a box-only defensive view, and
the gap is the deterrence the reweighting saves.

    python build_opponent_profiles.py
"""

import os
import sys
import csv
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUTDIR = os.path.join(HERE, "..", "outputs")
sys.path.insert(0, HERE)
import build_team_ratings as A
import build_rotation_model as B

ROLE_MPG = {"starter": 34, "sixth": 26, "rotation": 18, "deep": 9}
ROSTERS = os.path.join(DATA, "opponent_rosters.json")


def roster_to_mpg(rotation):
    """Role tiers -> per-game minutes, rescaled so the rotation sums to 240."""
    raw = {p["nba_player_id"]: ROLE_MPG.get(p["role"], 12) for p in rotation}
    tot = sum(raw.values()) or 1
    return {pid: m / tot * 240.0 for pid, m in raw.items()}


def box_only_def(roster_mpg, box_def):
    """Team defensive rating if we had used the box-only defensive view (bbr_dbpm),
    for the Wembanyama contrast. Higher bbr_dbpm = better, so team box-def (lower=better)
    = -sum(w * dbpm)."""
    s = 0.0
    for pid, mpg in roster_mpg.items():
        if pid in box_def:
            s += (mpg / 48.0) * box_def[pid]
    return -s


def write_markdown(profiles, wemby_line):
    os.makedirs(OUTDIR, exist_ok=True)
    L = ["# Contender profiles, 2026-27 (Championship layer, Component C)\n",
         "_Projected post-offseason rosters (workflow) rolled up through the validated team-rating "
         "(A) and rotation/redundancy (B) layers. Net is per-100 vs an average team; method_uncertainty "
         "is the RAPM-vs-box defensive disagreement (higher = our defensive read is less certain). "
         "Assumed moves are the documented snapshot and drive everything downstream; eyeball them._\n",
         f"**Wembanyama / rim-deterrence check.** {wemby_line}\n",
         "## Strength table (RS net, descending)\n",
         "| Team | RS net (off/def) | PO net | +/- | method_unc | data |",
         "|---|---|---|---|---|---|"]
    for p in profiles:
        L.append(f"| {p['team']} | {p['rs_net']:+.2f} ({p['rs_off']:+.1f}/{p['rs_def']:+.1f}) | "
                 f"{p['po_net']:+.2f} | {p['net_sd']:.1f} | {p['method_uncertainty']:.2f} | {p['players_with_data']} |")
    for p in profiles:
        L.append(f"\n### {p['team']}  (RS net {p['rs_net']:+.2f}, PO net {p['po_net']:+.2f})\n")
        L.append(f"- **Assumed moves:** {'; '.join(p['assumed_moves'])}. _Key assumption:_ {p['key_assumption']} "
                 f"(confidence: {p['confidence']}).")
        rot = ", ".join(f"{r['name']} ({r['role']})" for r in p['rotation'])
        L.append(f"- **Projected rotation:** {rot}.")
        idn = p["identity"]
        L.append(f"- **Offense:** {idn['offense']}")
        L.append(f"- **Defense takes away:** {idn['defense']}")
        L.append(f"- **Rim protection:** {idn['rim_protection']}  |  **Switchability:** {idn['switchability']}")
        L.append(f"- **Where they crack:** {idn['where_they_crack']}")
        dd = p["dimensions"]
        L.append(f"- **Dimensions (pctile):** creation {dd['hc_creation']}, playmaking "
                 f"{dd['secondary_playmaking']}, shooting {dd['off_ball_shooting']}, def-versatility "
                 f"{dd['def_versatility_poa']}, rim/reb {dd['rim_protect_reb']}, transition {dd['transition']}")
    path = os.path.join(OUTDIR, "opponent_profiles.md")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    if not os.path.exists(ROSTERS):
        sys.exit(f"missing {ROSTERS}; run the opponent-profiles workflow and persist its rosters first")
    rosters = json.load(open(ROSTERS, encoding="utf-8"))
    imp = A.load_impacts()
    dims = B.load_dims()
    # box-only defensive view (bbr_dbpm) for the Wemby contrast
    box_def = {}
    for r in csv.DictReader(open(os.path.join(DATA, "player_value.csv"), encoding="utf-8")):
        v = (r.get("bbr_dbpm") or "").strip()
        if v:
            try:
                box_def[r["player_id"]] = float(v)
            except ValueError:
                pass

    profiles = []
    for tm in rosters:
        mpg = roster_to_mpg(tm["rotation"])
        rs = A.rollup(mpg, imp, "rs")
        po = A.rollup(B.project_rotation(mpg, "playoff"), imp, "playoff")
        prof = B.team_profile(mpg, dims)
        covered = sum(1 for p in tm["rotation"] if p["nba_player_id"] in imp)
        profiles.append({
            "team": tm["team_abbr"], "assumed_moves": tm["assumed_moves"],
            "key_assumption": tm["key_assumption"], "confidence": tm["confidence"],
            "rotation": tm["rotation"], "identity": tm["identity"],
            "rs_net": round(rs["net"], 2), "rs_off": round(rs["off"], 2), "rs_def": round(rs["def"], 2),
            "po_net": round(po["net"], 2), "po_off": round(po["off"], 2), "po_def": round(po["def"], 2),
            "net_sd": round(rs["net_sd"], 2), "method_uncertainty": rs["method_uncertainty"],
            "dimensions": {d: round(prof[d], 2) for d in B.DIMS},
            "players_with_data": f"{covered}/{len(tm['rotation'])}",
        })

    # center net ratings to the contender-field mean (relative strength)
    mean_net = np.mean([p["rs_net"] for p in profiles])
    for p in profiles:
        p["rs_net_centered"] = round(p["rs_net"] - mean_net, 2)
    profiles.sort(key=lambda p: -p["rs_net"])

    json.dump(profiles, open(os.path.join(DATA, "opponent_profiles.json"), "w", encoding="utf-8"), indent=2)

    # ---- Wembanyama rim-deterrence check (SAS) ----
    sas = next((p for p in profiles if p["team"] == "SAS"), None)
    wemby_line = ""
    if sas:
        mpg = roster_to_mpg(sas["rotation"])
        consensus_def = sas["rs_def"]                 # reweighted (lower=better)
        box_def_team = box_only_def(mpg, box_def)     # box-only view
        wv = next((r for r in csv.DictReader(open(os.path.join(DATA, "player_value.csv"), encoding="utf-8"))
                   if r["player_name"] == "Victor Wembanyama"), None)
        wemby_line = (f"SAS team defense: consensus (reweighted) {consensus_def:+.2f} vs box-only "
                      f"{box_def_team:+.2f} -> the reweighting preserves {box_def_team - consensus_def:+.2f} "
                      f"of rim deterrence (negative = better D kept). "
                      f"Wemby: def_rapm {wv['def_rapm']}, consensus_def {wv['consensus_def']}, "
                      f"box dbpm-based weaker; method_uncertainty carried.")

    write_markdown(profiles, wemby_line)

    def safe(s): return str(s).encode("ascii", "replace").decode()
    print(f"=== Component C: {len(profiles)} contender profiles (RS net desc) ===\n")
    for p in profiles:
        print(f"{safe(p['team']):4} RS net {p['rs_net']:+6.2f} (off {p['rs_off']:+.2f}/def {p['rs_def']:+.2f}) | "
              f"PO net {p['po_net']:+6.2f} | +/-{p['net_sd']:.2f} | method_unc {p['method_uncertainty']:.2f} | "
              f"data {p['players_with_data']}")
    print("\nWemby check:", safe(wemby_line))
    print(f"\nwrote opponent_profiles.json ({len(profiles)} teams)")


if __name__ == "__main__":
    main()
