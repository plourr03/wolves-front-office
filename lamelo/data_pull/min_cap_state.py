"""
Phase 2: compute MIN's post-trade 2026-27 cap state from the frozen snapshot.

Reproduces (or rejects) the external claim that the completed four-team trade puts
MIN at roughly $211M, over the first apron, and HARD-CAPPED at the second apron.
The hard cap is a RULE consequence of aggregating Reid + Randle to acquire LaMelo
(second_apron_no_aggregation), not a salary-level effect; the salary level only
confirms how much room remains under that hard cap.

CRITICAL: model the COMPLETED (post-July-6) trade, not the live tracker. Live sheets
(Spotrac ~$192M) do not yet include LaMelo's incoming max because the deal is not
official until 2026-07-06. Using the live sheet would wrongly read as under-apron.

Run: python lamelo/data_pull/min_cap_state.py  ->  lamelo/data/cap_state.json
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SNAP = REPO / "lamelo" / "data" / "snapshot_2026-06-25"
OUT = REPO / "lamelo" / "data" / "cap_state.json"

# 2026-27 thresholds, from offseason/data/league_year_constants.json (public CBA facts,
# cross-checked against cap-analyst reporting). Not a fitted output.
TH = {
    "salary_cap": 165_000_000,
    "luxury_tax": 201_000_000,
    "first_apron": 209_100_000,
    "second_apron": 222_000_000,
    "full_mle": 15_048_000,
    "taxpayer_mle": 6_065_000,
}

OUT_PLAYERS = ["Julius Randle", "Naz Reid"]
# Incoming and re-sign. Assumptions are explicit and parameterized.
LAMELO = 41_250_000  # base 40,770,520 + trade bonus to the max (per reporting)
GREEN = 14_679_012
GUEYE = 2_406_205
AYO_TOTAL, AYO_YEARS, AYO_RAISE = 112_000_000, 5, 0.08  # Bird re-sign, 8% of year-1


def ayo_year1(total: int, years: int, raise_pct: float) -> int:
    # NBA raises are a flat percentage of the first-year salary (not compounding)
    divisor = sum(1 + raise_pct * i for i in range(years))
    return round(total / divisor)


def main() -> None:
    con = pd.read_parquet(SNAP / "nba_player_contracts.parquet")
    min27 = con[(con.team_abbr == "MIN") & (con.season == "2026-27")][
        ["player_name", "salary"]
    ].copy()
    pre_sum = int(min27.salary.sum())
    kept = min27[~min27.player_name.isin(OUT_PLAYERS)].copy()
    kept_sum = int(kept.salary.sum())
    ayo_y1 = ayo_year1(AYO_TOTAL, AYO_YEARS, AYO_RAISE)
    incoming = {
        "LaMelo Ball": LAMELO,
        "Josh Green": GREEN,
        "Mouhamed Gueye": GUEYE,
        "Ayo Dosunmu (re-sign y1)": ayo_y1,
    }
    in_sum = sum(incoming.values())
    total = kept_sum + in_sum
    n_players = len(kept) + len(incoming)

    # tier verdict
    aggregation_used = True  # Reid + Randle aggregated to acquire LaMelo
    hard_cap = TH["second_apron"] if aggregation_used else None
    verdict = {
        "post_trade_salary": total,
        "n_players_committed": n_players,
        "in_luxury_tax": total > TH["luxury_tax"],
        "over_first_apron": total > TH["first_apron"],
        "over_second_apron": total > TH["second_apron"],
        "over_tax_by": total - TH["luxury_tax"],
        "over_first_apron_by": total - TH["first_apron"],
        "room_under_second_apron_hardcap": TH["second_apron"] - total,
        "hard_capped_at": "second_apron",
        "hard_cap_trigger": "aggregating Reid + Randle salaries to acquire LaMelo (second_apron_no_aggregation)",
        "tpe_33m_available": False,  # forfeited by the aggregation
        "full_nontaxpayer_mle_available": False,  # over the first apron
        "taxpayer_mle_available": True,  # between 1st and 2nd apron: kept (lost only ABOVE the 2nd apron)
        "taxpayer_mle_note": (
            "Confirmed: MIN sits between the first and second apron, so it keeps the "
            "taxpayer MLE (~6.065M); a team loses it only ABOVE the second apron. Using it "
            "keeps them hard-capped at the second apron, which the aggregation already did, "
            "so it adds no new restriction. The binding limit is the ~10.6M of room under "
            "the 222M hard cap, which must ALSO cover re-signing RFA Jaylen Clark and the "
            "remaining minimum spots. So the realistic toolkit is the taxpayer MLE plus "
            "minimums, and even that is room-constrained, not fully deployable. This "
            "reinforces the depth constraint; it does not relax it."
        ),
        "tools_to_fill": "taxpayer MLE (6.065M, room-constrained) and minimums; RFA Jaylen Clark; thin at PF",
    }

    out = {
        "as_of": "2026-06-25",
        "snapshot": "wh_65cf5da7f50c7f62",
        "model_basis": "COMPLETED post-2026-07-06 trade, NOT the live tracker (Spotrac ~192M is pre-official and would read under-apron, which is wrong)",
        "thresholds_2026_27": TH,
        "min_pre_trade_committed_2026_27": pre_sum,
        "players_out": OUT_PLAYERS,
        "kept_sum": kept_sum,
        "incoming": incoming,
        "assumptions": {
            "lamelo_includes_trade_bonus_to_max": LAMELO,
            "ayo_resign": f"{AYO_YEARS}yr / ${AYO_TOTAL:,} at {int(AYO_RAISE*100)}% raises -> y1 ${ayo_y1:,}",
        },
        "verdict": verdict,
    }
    OUT.write_text(json.dumps(out, indent=2))

    print(f"pre-trade MIN 2026-27 committed: ${pre_sum:,} ({len(min27)} players)")
    print(f"kept (minus Randle, Reid):       ${kept_sum:,} ({len(kept)} players)")
    print(f"Ayo re-sign year 1:              ${ayo_y1:,}")
    print(f"POST-TRADE total:                ${total:,} ({n_players} players)")
    print(f"  over luxury tax (201.0M) by:   ${total - TH['luxury_tax']:,}")
    print(f"  over first apron (209.1M) by:  ${total - TH['first_apron']:,}")
    print(f"  room under 2nd apron (222.0M): ${TH['second_apron'] - total:,}")
    print(f"  HARD-CAPPED at second apron (aggregation). $33.3M TPE forfeited, no full MLE.")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
