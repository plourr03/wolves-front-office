#!/usr/bin/env python3
"""
risk_overlay.py  -- Championship layer, Component G (risk + intangibles overlay).

Prices the soft factors honestly, MEASURED and JUDGED kept separate, across the FULL
slate (the overlay punishes fragility, so its natural consequence is that durable
mid-tier risers can out-rank fragile stars).

EV MODEL: availability is the probability weight between two EXPLICIT rosters, not a
scalar on the upside:
  - WITH (healthy): post-trade roster, star playing -> dP_with (playoff- and usage-adjusted).
  - WITHOUT (the games he misses): the SAME trade happened (the pieces are gone) but the
    star's minutes are replacement-level -> dP_without, which is BELOW baseline (negative).
  adj_center = avail * dP_with + (1 - avail) * dP_without.

BREAK-EVEN availability a* = |without| / (with + |without|): the availability at which the
risk-adjusted EV crosses zero. If with <= 0 the move is negative even at 100% health.

availability = P(suits up for a given RS game), recency-weighted 0.2/0.3/0.5 over
2023-24..2025-26, cap 82, missed season = 0. This is the BASE number. For DISCRETE-REHAB
cases (a single surgery + rehab season, e.g. an ACL with a Year-2 return by opening night),
the backward average is biased LOW; we keep the base but show a medical-judgment sensitivity
and never silently replace it.

TWO DOCUMENTED CAVEATS (both make this conservative):
  1. The healthy/absent two-branch model has NO middle "plays diminished" branch, so true
     EV sits somewhat ABOVE the absent-weighted center. The model is conservative.
  2. RS suit-up rate is a PROXY. The truer driver of title equity is PLAYOFF availability
     (does he suit up, and at what level, in May). A load-managing star is more available in
     the playoffs than his RS rate implies; one who breaks down in May is less. Read the
     numbers as RS-availability proxies for the playoff question, not the playoff answer.

JUDGMENT flags green/yellow/red + reason; a RED flag caps the tier. Acquisition probability
is a STATED ASSUMPTION outside the number. Deep-round odds remain a slight upper bound.

    python risk_overlay.py
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
import run_f_slate as S                 # noqa: E402
from lib import db                      # noqa: E402

F.NS = 7000
PO_MULT = {"holds_up": 1.03, "neutral": 1.0, "slips": 0.92, "insufficient_po_sample": 0.97, "": 0.98}
REPL_ID = "REPLACEMENT"


def availability(pid):
    r = db.query("""SELECT (g.season_id %% 10000) yr, COUNT(DISTINCT g.game_id) gp
                    FROM nba_games g JOIN nba_player_stats p ON p.game_id=g.game_id AND p.player_id=%s
                    WHERE g.season_type='Regular Season' AND (g.season_id %% 10000) IN (2023,2024,2025)
                    GROUP BY yr""", (int(pid),))
    gp = {int(x["yr"]): int(x["gp"]) for _, x in r.iterrows()}
    w = {2023: 0.2, 2024: 0.3, 2025: 0.5}
    return sum(w[y] * min(82, gp.get(y, 0)) / 82 for y in w), gp


def usage_mult(pid, dims, edwards_id="1630162"):
    def onball(p):
        d = dims.get(p, {})
        return 0.5 * (d.get("hc_creation", 0.5) + d.get("secondary_playmaking", 0.5))
    pen = 1.2 * max(0.0, onball(pid) - 0.5) * max(0.0, onball(edwards_id) - 0.5)
    return max(0.80, 1.0 - pen)


JUDGMENT = {
    "Giannis": {"availability": ("yellow", "Historically durable; a 36-game 2025-26 dip to monitor."),
                "culture": ("green", "Champion, franchise cornerstone."), "playoff": ("green", "holds_up, Finals-MVP pedigree.")},
    "Kyrie": {"availability": ("red", "ACL, missed ALL of 2025-26, age 34; discrete-rehab (see sensitivity)."),
              "culture": ("green", "Model pro late-career."), "usage_fit": ("yellow", "Ball-dominant, overlaps Edwards.")},
    "AD": {"availability": ("red", "49% recency-wtd, age 33, chronic soft-tissue; the durability IS the knock."),
           "playoff": ("green", "holds_up."), "usage_fit": ("green", "Off-ball big, fills the rim himself.")},
    "Morant": {"availability": ("red", "33%, chronic + suspension-shortened."),
               "off_court": ("red", "Conduct/suspension history."), "usage_fit": ("yellow", "Ball-dominant; synergy is the upside.")},
    "Trae": {"availability": ("yellow", "50%, 15-game 2025-26."), "defense": ("red", "Negative-impact defender; a title-defense liability."),
             "usage_fit": ("yellow", "Ball-dominant, overlaps Edwards.")},
    "Markkanen": {"availability": ("yellow", "56%; some missed time but no chronic red."),
                  "culture": ("green", "Clean profile."), "usage_fit": ("green", "Off-ball stretch four, low overlap.")},
    "Giddey": {"availability": ("green", "78%, durable."), "usage_fit": ("yellow", "Playmaking guard, partial overlap; a lesser orchestrator."),
               "culture": ("green", "Clean.")},
    "Quickley": {"availability": ("green", "71%."), "usage_fit": ("yellow", "Combo guard, some overlap."), "culture": ("green", "Clean.")},
}
ACQUISITION = {
    "Giannis": "LONG SHOT (Miami frontrunner; would need to outbid the field).",
    "Kyrie": "MODERATE (Dallas-reset dependent).", "AD": "HIGHEST of the stars (Washington, salary matches).",
    "Morant": "MODERATE (Memphis-pivot dependent).", "Trae": "MODERATE (Washington).",
    "Markkanen": "HIGH (Utah is a willing seller; a gettable stretch four).",
    "Giddey": "HIGH (cheap, Chicago).", "Quickley": "MODERATE (Toronto).",
}
DISCRETE_REHAB = {"Kyrie": "Year-2 ACL return by 2026-27 opening night; the 32% base includes the lost rehab season and is biased LOW."}


def inject_replacement(imp, dims):
    imp[REPL_ID] = {"off": -1.0, "def": 1.0, "off_sd": 1.2, "def_sd": 1.2, "def_div": 0.0, "read": ""}
    dims[REPL_ID] = {d: 0.40 for d in B.DIMS}


def main():
    import csv
    imp = A.load_impacts(); dims = B.load_dims(); inject_replacement(imp, dims)
    actual_rot = BH.actual_top_rotations("2025-26"); actual_net = BH.actual_team_net(2025)
    pv = {r["player_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "..", "data", "player_value.csv"), encoding="utf-8"))}

    def safe(s): return str(s).encode("ascii", "replace").decode()

    base_c = E.build_2026_27_league(imp)
    pre = F._sim(base_c, 5.5)["teams"]["MIN"]["title"]

    def dp(sc, replace_pid=None, synergy=0.0):
        s = sc
        if replace_pid:
            s = copy.deepcopy(sc)
            for p in s["post_rotations"]["MIN"]:
                if p["nba_player_id"] == replace_pid:
                    p["nba_player_id"] = REPL_ID
        post = F.apply_trade(s, base_c, imp, dims, actual_rot, actual_net, synergy_uplift=synergy)
        return (F._sim(post, 5.5)["teams"]["MIN"]["title"] - pre) * 100

    ad = {s["slug"]: s for s in F.ad_scenarios(actual_rot)}
    # name, star_pid, scenario, synergy, metric_flips
    cases = [
        ("Giannis", "203507", S.make_scenario("Giannis", "203507", 58_456_566, "MIL", "F", "both"), 0.0, True),
        ("Markkanen", "1628374", S.make_scenario("Markkanen", "1628374", 46_113_154, "UTA", "F", "randle"), 0.0, True),
        ("Kyrie", "202681", S.make_scenario("Kyrie", "202681", 39_491_282, "DAL", "G", "randle"), 0.0, False),
        ("Giddey", "1630581", S.make_scenario("Giddey", "1630581", 25_000_000, "CHI", "G", "randle"), S.SYNERGY_UPLIFT, False),
        ("Quickley", "1630193", S.make_scenario("Quickley", "1630193", 32_500_000, "TOR", "G", "randle"), 0.0, False),
        ("AD+Kessler", "203076", ad["ad_kessler"], 0.0, True),
        ("AD straight", "203076", ad["ad_straight"], 0.0, True),
        ("Morant", "1629630", S.make_scenario("Morant", "1629630", 42_166_510, "MEM", "G", "randle"), S.SYNERGY_UPLIFT, True),
        ("Trae", "1629027", S.make_scenario("Trae", "1629027", 48_967_380, "WAS", "G", "randle"), S.SYNERGY_UPLIFT, True),
    ]
    print("=== Component G: FULL-SLATE risk overlay (risk-adjusted EV + break-even availability) ===")
    print(f"MIN baseline title {pre*100:.2f}%. availability = recency-wtd RS suit-up rate (base; see caveats + sensitivity).\n")
    board = []
    for name, pid, sc, syn, flips in cases:
        avail, gp = availability(pid)
        jname = name.split("+")[0].split()[0]   # AD+Kessler / AD straight -> AD
        read = pv.get(pid, {}).get("translation_read", "")
        pomul = PO_MULT.get(read, 0.98); umul = usage_mult(pid, dims)
        with_real = dp(sc) * pomul * umul
        without = dp(sc, replace_pid=pid)
        adj = avail * with_real + (1 - avail) * without
        syn_adj = None
        if syn:
            with_s = dp(sc, synergy=syn) * pomul * umul
            syn_adj = avail * with_s + (1 - avail) * without
        be = (abs(without) / (with_real + abs(without))) if with_real > 0 else None
        flags = JUDGMENT.get(jname, {})
        reds = [k for k, v in flags.items() if v[0] == "red"]
        tier = (f"CAPPED (RED: {','.join(reds)})" if reds else
                "raises ceiling materially" if adj > 1.0 else "modest riser" if adj > 0.3 else
                "marginal" if adj > -0.3 else "downgrade")
        board.append({"name": name, "jname": jname, "avail": avail, "gp": gp, "with": with_real, "without": without,
                      "adj": adj, "syn": syn_adj, "be": be, "tier": tier, "reds": reds, "flips": flips,
                      "read": read, "pomul": pomul, "umul": umul})

    board.sort(key=lambda r: -r["adj"])
    print(f"{'target':12}{'risk-adj EV':>12}{'break-even':>12}{'avail':>8}{'with/without':>16}{'+syn':>7}{'raw-ish':>9}  tier")
    for r in board:
        be = f"{r['be']*100:.0f}%" if r["be"] is not None else "neg@100%"
        syn = f"{r['syn']:+.2f}" if r["syn"] is not None else "  -"
        print(f"{safe(r['name']):12}{r['adj']:>+11.2f}{be:>12}{r['avail']*100:>6.0f}% "
              f"{(str(round(r['with'],2))+'/'+str(round(r['without'],2))):>15}{syn:>7}{r['with']:>+9.2f}  "
              + ("RED-capped " if r["reds"] else "") + r["tier"])

    # Kyrie discrete-rehab medical-judgment sensitivity
    print("\n=== Kyrie ACL sensitivity (discrete-rehab; base 32% is biased low, kept as base) ===")
    kr = next(r for r in board if r["name"] == "Kyrie")
    print(f"  {DISCRETE_REHAB['Kyrie']}")
    print(f"  break-even availability = {kr['be']*100:.0f}%. Risk-adjusted EV at assumed 2026-27 health:")
    for a in (0.32, 0.45, 0.55, 0.65):
        adj = a * kr["with"] + (1 - a) * kr["without"]
        print(f"    avail {a*100:.0f}%: risk-adj EV {adj:+.2f}pp  ({'positive' if adj > 0 else 'negative'})")
    print("  -> Kyrie's verdict is CONDITIONAL on the medical read: at a credible Year-2-ACL 55-65% he flips positive.")

    print("\nCAVEATS: (1) two-branch healthy/absent model has no 'plays diminished' middle -> conservative (true EV a bit higher).")
    print("         (2) RS suit-up is a PROXY; PLAYOFF availability is the truer title-equity driver. Read accordingly.")


if __name__ == "__main__":
    main()
