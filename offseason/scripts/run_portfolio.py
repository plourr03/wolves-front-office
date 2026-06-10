#!/usr/bin/env python3
"""
run_portfolio.py  -- THE CAPSTONE: full-offseason portfolios on the unified spine.

The cheap TPE fliers (Mitchell $3.0M, McBride $4.3M) fit inside MIN's TPEs ($10.8M/$7.6M/
$6.6M), so they STACK with a Randle conversion rather than competing. Each portfolio is a
SEQUENCE of moves (Randle conversion + TPE flier + MLE shooter where preserved + Dosunmu
re-sign + the No.28 pick), validated leg-by-leg through evaluate_move because BOTH a TPE use
and a full-MLE use trip the first-apron hard cap, so order and headroom matter. The complete
resulting roster then runs through F/G on the unified (aged, incumbent-default) spine, reported
like a target: four views (consensus/box/rapm/DARKO), risk-adjusted EV with band, gauntlet, and
the 2027 flexibility state each leaves behind.

    python run_portfolio.py
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

F.NS = 6000
M = {"Edwards": "1630162", "Dosunmu": "1630245", "McDaniels": "1630183", "Randle": "203944",
     "Gobert": "203497", "Naz": "1629675", "Conley": "201144", "Shannon": "1630545",
     "Beringer": "1642866", "Phillips": "1641763"}
SMITH = "1630188"; MCBRIDE = None; MITCHELL = None; MARK = "1628374"
PVN = {r["player_name"]: r["player_id"] for r in csv.DictReader(open(os.path.join(HERE, "..", "data", "player_value.csv"), encoding="utf-8"))}
MCBRIDE = PVN["Miles McBride"]; MITCHELL = PVN["Ajay Mitchell"]
# a modeled full-MLE 3-and-D wing shooter (durable, modest +): injected into the spine
MLE = "MLE_SHOOTER"
MINI = "MINI_MLE_SHOOTER"
PICK28 = "PICK28"


def _r(pid, role): return {"nba_player_id": pid, "role": role}


def inject_synthetics(imp, dims):
    imp[MLE] = {"off": 0.6, "def": -0.2, "off_sd": 1.3, "def_sd": 1.3, "def_div": 0.0, "read": ""}  # ~+0.8 net 3-and-D
    dims[MLE] = {d: (0.78 if d in ("off_ball_shooting", "transition") else 0.5) for d in B.DIMS}
    imp[MINI] = {"off": 0.4, "def": -0.1, "off_sd": 1.4, "def_sd": 1.4, "def_div": 0.0, "read": ""}  # ~+0.5 net taxpayer-MLE 3-and-D (Shamet/Kennard tier)
    dims[MINI] = {d: (0.74 if d in ("off_ball_shooting", "transition") else 0.48) for d in B.DIMS}
    imp[PICK28] = {"off": -0.8, "def": 0.6, "off_sd": 1.5, "def_sd": 1.5, "def_div": 0.0, "read": ""}  # rookie ~ -1.4
    dims[PICK28] = {d: 0.42 for d in B.DIMS}


# ---- portfolios: (name, move-sequence for the gate, resulting MIN rotation, 2027 note) ----
def portfolios():
    return [
        {"name": "A: Spacing+Depth, keep core (under apron)", "slug": "portA",
         "seq": [("trade", [{"label": "Randle", "salary": 33_333_334}], [{"label": "Smith", "salary": 9_428_571}], "none"),
                 ("resign Dosunmu (Bird)", [], [{"label": "Dosunmu", "salary": 16_500_000}], "bird"),
                 ("TPE: McBride", [], [{"label": "McBride", "salary": 4_300_000}], "tpe"),
                 ("full MLE: Powell/McCollum/Huerter tier", [], [{"label": "MLE shooter", "salary": 15_048_000}], "full_mle")],
         "rot": [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
                 _r(M["Naz"], "starter"), _r(M["Gobert"], "starter"), _r(SMITH, "sixth"),
                 _r(MCBRIDE, "rotation"), _r(MLE, "rotation"), _r(M["Conley"], "deep"), _r(PICK28, "deep")],
         "flex": "HIGH: Randle's $33M off the books, McBride/Smith expiring; only Dosunmu + MLE (short) added. 2027 war chest + picks intact."},
        {"name": "C: Mitchell upside + spacing (under apron)", "slug": "portC",
         "seq": [("trade", [{"label": "Randle", "salary": 33_333_334}], [{"label": "Smith", "salary": 9_428_571}], "none"),
                 ("resign Dosunmu (Bird)", [], [{"label": "Dosunmu", "salary": 16_500_000}], "bird"),
                 ("TPE: Mitchell", [], [{"label": "Mitchell", "salary": 3_000_000}], "tpe"),
                 ("full MLE: Powell/McCollum/Huerter tier", [], [{"label": "MLE shooter", "salary": 15_048_000}], "full_mle")],
         "rot": [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
                 _r(M["Naz"], "starter"), _r(M["Gobert"], "starter"), _r(SMITH, "sixth"),
                 _r(MITCHELL, "rotation"), _r(MLE, "rotation"), _r(M["Conley"], "deep"), _r(PICK28, "deep")],
         "flex": "HIGH: same as A; Mitchell is cheap multi-year (small hold), McBride-less. 2027 largely clean."},
        {"name": "B: Markkanen ceiling (lose Dosunmu, hard-capped)", "slug": "portB",
         "seq": [("trade Randle+filler->Markkanen", [{"label": "Randle", "salary": 33_333_334}, {"label": "filler", "salary": 3_600_000}],
                  [{"label": "Markkanen", "salary": 46_113_154}], "none"),
                 ("TPE: Mitchell", [], [{"label": "Mitchell", "salary": 3_000_000}], "tpe")],
         "rot": [_r(M["Edwards"], "starter"), _r(M["Conley"], "starter"), _r(M["McDaniels"], "starter"),
                 _r(MARK, "starter"), _r(M["Gobert"], "starter"), _r(M["Naz"], "sixth"),
                 _r(MITCHELL, "rotation"), _r(M["Shannon"], "rotation"), _r(PICK28, "deep")],
         "flex": "LOW: Markkanen's ~$46M multi-year clogs 2027; Dosunmu lost to the hard cap; no MLE room. Higher ceiling, less optionality."},
        {"name": "D: Patience fallback -- NO Randle trade (honest best: taxpayer MLE)", "slug": "portD",
         "seq": [("resign Dosunmu (Bird)", [], [{"label": "Dosunmu", "salary": 16_500_000}], "bird"),
                 ("taxpayer MLE: Shamet/Kennard tier shooter", [], [{"label": "mini-MLE shooter", "salary": 6_065_000}], "taxpayer_mle"),
                 ("ATTEMPT full MLE (should fail: over 1st apron)", [], [{"label": "full MLE", "salary": 15_048_000}], "full_mle")],
         "rot": [_r(M["Edwards"], "starter"), _r(M["Dosunmu"], "starter"), _r(M["McDaniels"], "starter"),
                 _r(M["Randle"], "starter"), _r(M["Gobert"], "starter"), _r(M["Naz"], "sixth"),
                 _r(MINI, "rotation"), _r(M["Conley"], "rotation"), _r(PICK28, "deep"), _r(M["Shannon"], "deep")],
         "flex": "MODERATE: keeps Randle ($33M; his 2027 player option clogs the sheet if exercised). The patience fallback if no counterparty materializes. CBA precision: re-signing Dosunmu lands ~$210.5M (over the FIRST apron), so the team is DOWN TO THE TAXPAYER MINI-MLE (~$6.1M, hard-caps at the SECOND apron $222M) + minimums -- not frozen, but no full MLE and no TPE absorptions."},
    ]


def sequence_gate(seq):
    c = EM.load_constants("2026-27"); ts = dict(EM.load_team_state("MIN", "2026-27", "base"))
    apron = ts["apron_team_salary"]; hard_line = None; hard_lbl = None; legs = []
    FIRST = {"tpe", "full_mle", "bae", "sign_and_trade"}; SECOND = {"taxpayer_mle"}
    for label, out, inc, exc in seq:
        ts["apron_team_salary"] = apron
        # MLE availability is tier-dependent: a team over the first apron loses the FULL MLE and
        # is down to the TAXPAYER MLE. Refresh the flags at the running apron before each leg.
        over_first = apron >= c["first_apron"]
        ts["full_mle_available"] = not over_first
        ts["taxpayer_mle_available"] = over_first
        r = EM.evaluate_move(ts, c, out, inc, exception_used=exc)
        out_base = sum(p["salary"] for p in out); inc_base = sum(p["salary"] for p in inc)
        tentative = apron - out_base + inc_base
        # bind the hard cap to the MOST RESTRICTIVE line this leg would trigger (first < second)
        line = c["first_apron"] if (exc in FIRST or r.get("hard_cap_set") not in (None, "none")) else \
            (c["second_apron"] if exc in SECOND else None)
        cand = min([x for x in (hard_line, line) if x is not None], default=None)
        over = (cand is not None and tentative > cand)
        ok = bool(r.get("legal")) and not over
        if ok:                       # only COMMIT legal legs to the running apron / hard cap
            apron = tentative
            if line is not None and (hard_line is None or line < hard_line):
                hard_line = line; hard_lbl = "first apron" if line == c["first_apron"] else "second apron"
        legs.append((label, ok, round(tentative), exc, over))
    return legs, round(apron), hard_line, hard_lbl


def main():
    base_imp = A.load_impacts(); dims = B.load_dims(); G.inject_replacement(base_imp, dims); inject_synthetics(base_imp, dims)
    ar = BH.actual_top_rotations("2025-26"); an = BH.actual_team_net(2025)
    aged = AC.aged_impacts(base_imp)

    def safe(s): return str(s).encode("ascii", "replace").decode()

    def dp(rot, imp, base, pre, replace=None):
        sc = {"name": "p", "slug": "p", "team_state_scenario": "base", "outgoing": [{"label": "Randle", "salary": 33_333_334}],
              "incoming": [{"label": "x", "salary": 1}], "override_ids": [], "post_rotations": {"MIN": rot}}
        if replace:
            sc = copy.deepcopy(sc)
            for p in sc["post_rotations"]["MIN"]:
                if p["nba_player_id"] in (replace if isinstance(replace, set) else {replace}):
                    p["nba_player_id"] = G.REPL_ID
        return (F._sim(F.apply_trade(sc, base, imp, dims, ar, an), 5.5)["teams"]["MIN"]["title"] - pre) * 100

    cap_tag = {"tpe": " [hard-cap: 1st apron]", "full_mle": " [hard-cap: 1st apron]", "bae": " [hard-cap: 1st apron]",
               "sign_and_trade": " [hard-cap: 1st apron]", "taxpayer_mle": " [hard-cap: 2nd apron $222M]"}
    for port in portfolios():
        legs, final_apron, hard_line, hard_lbl = sequence_gate(port["seq"])
        print(f"=== {safe(port['name'])} ===")
        print("  SEQUENCE (leg -> legal | running apron | hard-cap):")
        for label, ok, apr, exc, over in legs:
            print(f"    {safe(label):44} legal={ok} apron ${apr:,}{cap_tag.get(exc, '')}{' OVER CAP!' if over else ''}")
        binding = f"${hard_line:,} ({hard_lbl})" if hard_line else "none triggered"
        print(f"  -> final apron ${final_apron:,} vs binding hard cap {binding}  ({'UNDER, legal' if (hard_line is None or final_apron<=hard_line) else 'OVER -- INFEASIBLE'})")
        # four views + risk-adj on the unified spine
        rot = port["rot"]
        views = {}
        for vlbl, imp in [("consensus", aged), ("box", None), ("rapm", None), ("darko", None)]:
            if vlbl == "consensus":
                im = aged
            else:
                ov = [p["nba_player_id"] for p in rot if p["nba_player_id"] not in (G.REPL_ID, MLE, PICK28)]
                im = F.build_impacts_view(vlbl, ov, aged)
            base = E.build_2026_27_league(im); pre = F._sim(base, 5.5)["teams"]["MIN"]["title"]
            views[vlbl] = dp(rot, im, base, pre)
        # risk-adj (consensus): downside = the most fragile rotation piece out; pairs are deep so shallow
        base = E.build_2026_27_league(aged); pre = F._sim(base, 5.5)["teams"]["MIN"]["title"]
        central = views["consensus"]
        # band over the young/MLE projection (decline-only floor) + a shallow injury floor
        floor = dp(rot, AC.aged_impacts(base_imp, decline_only=True), E.build_2026_27_league(AC.aged_impacts(base_imp, decline_only=True)),
                   F._sim(E.build_2026_27_league(AC.aged_impacts(base_imp, decline_only=True)), 5.5)["teams"]["MIN"]["title"])
        cond = E.conditional_series("MIN", E.build_2026_27_league(aged), use_overlay=True)  # crude pre gauntlet ref
        post = F.apply_trade({"name": "p", "slug": "p", "team_state_scenario": "base", "outgoing": [{"label": "R", "salary": 1}],
                              "incoming": [{"label": "x", "salary": 1}], "override_ids": [], "post_rotations": {"MIN": rot}}, base, aged, dims, ar, an)
        condp = E.conditional_series("MIN", post, use_overlay=True)
        dvo = (condp["OKC"] - cond["OKC"]) * 100; dvs = (condp["SAS"] - cond["SAS"]) * 100
        flip = min(views.values()) < 0 < max(views.values())
        print(f"  FOUR VIEWS dP(title): consensus {views['consensus']:+.2f} | box {views['box']:+.2f} | rapm {views['rapm']:+.2f} | DARKO {views['darko']:+.2f}  ({'sign FLIPS' if flip else 'consistent'})")
        print(f"  RISK-ADJ EV (consensus central) {central:+.2f}pp | band [{min(floor,central):+.2f} .. {max(floor,central):+.2f}] (decline-only floor)")
        print(f"  GAUNTLET: vs OKC {dvo:+.1f}pp, vs SAS {dvs:+.1f}pp")
        print(f"  2027 FLEXIBILITY: {port['flex']}\n")


if __name__ == "__main__":
    main()
