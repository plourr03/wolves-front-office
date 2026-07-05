"""
alebron Phase 2: MIN's 2026-27 cap state AFTER the completed LaMelo trade, then the
feasibility of adding LeBron James as a free agent. Reproduces the post-LaMelo sheet from
the frozen snapshot (as the LaMelo project did) and extends it with the VERIFIED 2026-27
thresholds and the confirmed Clark/Bones re-signings, then tests LeBron at (a) the veteran
minimum and (b) the taxpayer MLE against the second-apron HARD CAP.

The headline Q0 finding lives here: the LaMelo trade hard-capped MIN so tightly that a
14-man roster already sits within a whisker of the $221.686M second apron, so LeBron can
be added only at the MINIMUM and only by SUBTRACTING an existing minimum body (he is a
swap, not an addition), and the taxpayer MLE is off the table.

Thresholds and minimum figures are the VERIFIED official 2026-27 numbers
(alebron/data/field_2026_offseason.json), not the LaMelo project's slightly rounded set.

Run: python alebron/data_pull/min_cap_state.py  ->  alebron/data/cap_state.json
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SNAP = REPO / "alebron" / "data" / "snapshot_2026-06-25"
OUT = REPO / "alebron" / "data" / "cap_state.json"

# VERIFIED official 2026-27 thresholds (field_2026_offseason.json / NBA.com / Hoops Rumors)
TH = {
    "salary_cap": 164_961_000,
    "luxury_tax": 200_428_000,
    "first_apron": 209_015_000,
    "second_apron": 221_686_000,
    "taxpayer_mle": 6_064_000,
    "vet_min_10yr_full": 3_876_529,
    "vet_min_10yr_caphit": 2_449_421,   # 1-yr min for a 3+ yr vet; league reimburses the rest
    "vet_min_generic_caphit": 2_100_000,  # approx cap hit of the min roster body LeBron would displace
}

OUT_PLAYERS = ["Julius Randle", "Naz Reid"]
LAMELO = 41_250_000   # base 40,770,520 + trade bonus to the max (per reporting)
GREEN = 14_679_012
GUEYE = 2_406_205
AYO_TOTAL, AYO_YEARS, AYO_RAISE = 112_000_000, 5, 0.08   # Bird re-sign, y1 at 8% raises
# Confirmed 2026 re-signings not in the pre-trade snapshot:
CLARK_Y1 = 3_200_000   # 3yr/~$10M RFA re-sign (approx y1)
BONES = 2_900_000      # 1yr/~$2.9M
ONE_MORE_MIN = 2_100_000  # a 14th/15th minimum body to reach a legal roster


def ayo_year1(total, years, raise_pct):
    divisor = sum(1 + raise_pct * i for i in range(years))
    return round(total / divisor)


def main():
    con = pd.read_parquet(SNAP / "nba_player_contracts.parquet")
    min27 = con[(con.team_abbr == "MIN") & (con.season == "2026-27")][["player_name", "salary"]].copy()
    kept = min27[~min27.player_name.isin(OUT_PLAYERS)].copy()
    kept_sum = int(kept.salary.sum())
    ayo_y1 = ayo_year1(AYO_TOTAL, AYO_YEARS, AYO_RAISE)
    incoming = {"LaMelo Ball": LAMELO, "Josh Green": GREEN, "Mouhamed Gueye": GUEYE,
                "Ayo Dosunmu (re-sign y1)": ayo_y1}
    post_lamelo = kept_sum + sum(incoming.values())
    n_post_lamelo = len(kept) + len(incoming)

    # Fill the roster with the CONFIRMED re-signings + one more minimum to a legal 14.
    fills = {"Jaylen Clark (re-sign y1)": CLARK_Y1, "Bones Hyland": BONES, "one more minimum": ONE_MORE_MIN}
    filled = post_lamelo + sum(fills.values())
    n_filled = n_post_lamelo + len(fills)
    room_after_fill = TH["second_apron"] - filled

    hardcap = TH["second_apron"]
    lebron = {}
    # (a) minimum, ADDED as an extra body (roster grows by 1)
    add_min = filled + TH["vet_min_10yr_caphit"]
    lebron["min_added_as_extra_body"] = {
        "lebron_cap_hit": TH["vet_min_10yr_caphit"], "team_salary": add_min,
        "over_hardcap_by": add_min - hardcap, "legal": add_min <= hardcap,
        "note": "LeBron as a 15th man ON TOP of a filled 14. The naive 'just add him' case."}
    # (b) minimum, SWAPPED for the last minimum body (roster size unchanged)
    swap_min = filled - ONE_MORE_MIN + TH["vet_min_10yr_caphit"]
    lebron["min_swapped_for_a_minimum_body"] = {
        "lebron_cap_hit": TH["vet_min_10yr_caphit"], "displaced_body_caphit": ONE_MORE_MIN,
        "team_salary": swap_min, "over_hardcap_by": swap_min - hardcap, "legal": swap_min <= hardcap,
        "note": "LeBron REPLACES the 14th/15th minimum body. The realistic path if legal."}
    # (c) taxpayer MLE, added
    mle = filled + TH["taxpayer_mle"]
    lebron["taxpayer_mle_added"] = {
        "lebron_cap_hit": TH["taxpayer_mle"], "team_salary": mle,
        "over_hardcap_by": mle - hardcap, "legal": mle <= hardcap,
        "note": "The MLE MIN nominally keeps, but only if it fits under the hard cap."}
    # (d) taxpayer MLE, swapped for a minimum body
    mle_swap = filled - ONE_MORE_MIN + TH["taxpayer_mle"]
    lebron["taxpayer_mle_swapped_for_a_minimum_body"] = {
        "lebron_cap_hit": TH["taxpayer_mle"], "displaced_body_caphit": ONE_MORE_MIN,
        "team_salary": mle_swap, "over_hardcap_by": mle_swap - hardcap, "legal": mle_swap <= hardcap}

    verdict = {
        "post_lamelo_salary": post_lamelo, "n_post_lamelo_committed": n_post_lamelo,
        "filled_14man_salary": filled, "n_filled": n_filled,
        "room_under_second_apron_after_fill": room_after_fill,
        "hard_capped_at": "second_apron ($221.686M)",
        "hard_cap_trigger": "salary aggregation in the LaMelo four-team trade",
        "feasibility_conclusion": (
            "LeBron fits ONLY at the veteran minimum and ONLY as a SWAP for an existing minimum "
            "body (not as an addition). The taxpayer MLE is INFEASIBLE (it blows the hard cap). So "
            "the four-time MVP can be added, if at all, only as a minimum-for-minimum swap that keeps "
            "the roster the same size. He is not additive; he is a substitution, and the hard cap is "
            "the reason. Availability is then the whole game: a 41-turning-42 body in a spot that "
            "otherwise holds a healthier 65-75 game minimum player."),
    }

    out = {
        "as_of": "2026-07-03", "snapshot": "wh_65cf5da7f50c7f62",
        "model_basis": "Completed post-LaMelo trade + confirmed Clark/Bones re-signings; VERIFIED 2026-27 thresholds.",
        "thresholds_2026_27": TH, "players_out_in_lamelo_trade": OUT_PLAYERS,
        "kept_sum": kept_sum, "incoming_lamelo": incoming, "roster_fills": fills,
        "assumptions": {
            "ayo_resign": f"{AYO_YEARS}yr/${AYO_TOTAL:,} at {int(AYO_RAISE*100)}% -> y1 ${ayo_y1:,}",
            "clark_resign": "3yr/~$10M -> y1 ~$3.2M (approx)", "bones": "1yr/~$2.9M",
            "lebron_min_caphit": "10+yr vet, 1-yr min: full $3,876,529, cap/apron hit $2,449,421",
        },
        "lebron_scenarios": lebron, "verdict": verdict,
    }
    OUT.write_text(json.dumps(out, indent=2))

    print(f"post-LaMelo committed:      ${post_lamelo:,} ({n_post_lamelo} players)")
    print(f"filled to 14 (+Clark/Bones/min): ${filled:,} ({n_filled} players)")
    print(f"room under 2nd apron ($221.686M) after fill: ${room_after_fill:,}")
    print("\nLeBron feasibility vs the $221.686M hard cap:")
    for k, v in lebron.items():
        flag = "LEGAL" if v["legal"] else f"OVER by ${v['over_hardcap_by']:,}"
        print(f"  {k:42} team ${v['team_salary']:,}  -> {flag}")
    print(f"\n{verdict['feasibility_conclusion']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
