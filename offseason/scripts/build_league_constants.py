#!/usr/bin/env python3
"""
build_league_constants.py

Writes league_year_constants.json: the CBA thresholds, exception amounts, trade-
matching brackets, and rule parameters as machine-readable data. This is the
bridge from the prose rules reference (../docs, and the cba-rules skill reference)
to code the feasibility module can read. Build this first; team_state joins to it.

Sources (verified June 2026):
- 2025-26 final figures: NBA PR (cap $154.647M, tax $187.895M, apron1 $195.945M,
  apron2 $207.824M, full MLE $14.104M, taxpayer MLE $5.685M, room $8.781M).
- 2026-27 projections: ~$165M cap (revised down on media-revenue dip); tax ~$201M,
  apron1 ~$209.1M, apron2 ~$222M; full MLE $15.048M, taxpayer MLE $6.065M,
  room $9.369M, BAE $5.478M (Hoops Rumors, off a $165M cap).
- Below-apron trade matching brackets (2023 CBA, permanent): 200% + $250K up to
  $7.5M outgoing; outgoing + $7.5M from $7.5M to $29M; 125% + $250K above $29M.
- Minimum salary scale: 2025-26 actual table by years of service.

Out-years (2027-28 .. 2029-30) are scaled forward at a documented growth rate.
Everything past 2025-26 is is_projection = TRUE and resets when the NBA sets each
cap in early July. Three figures the rules reference flags as CONFIRM (first-apron
matching %, exact tax bracket rates, frozen-pick counting window) are carried with
confirm flags rather than asserted.
"""

import os
import json
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "league_year_constants.json")

# Annual growth applied to 2026-27 to project out-years. Cap, tax, and both aprons
# rise at the same rate (cba-rules), and exceptions are cap-linked, so one factor
# scales the whole row. ~7% reflects recent NBA guidance (10% is the CBA ceiling).
GROWTH = 1.07

# Minimum salary scale, 2025-26 actual (years of service -> salary).
MIN_SCALE_2025_26 = {
    "0": 1272870, "1": 2048494, "2": 2296274, "3": 2378870, "4": 2461463,
    "5": 2667947, "6": 2874436, "7": 3080921, "8": 3287409, "9": 3303774,
    "10+": 3634153,
}

# Anchor rows. 2025-26 is final; 2026-27 is the researched projection.
ANCHORS = {
    "2025-26": {
        "salary_cap": 154_647_000, "luxury_tax": 187_895_000,
        "first_apron": 195_945_000, "second_apron": 207_824_000,
        "min_team_salary": 139_182_000,
        "full_mle": 14_104_000, "taxpayer_mle": 5_685_000,
        "room_exception": 8_781_000, "bae": 5_134_000,
        "match_t1": 7_500_000, "match_t2": 29_000_000,
        "min_scale": MIN_SCALE_2025_26, "is_projection": False,
    },
    "2026-27": {
        "salary_cap": 165_000_000, "luxury_tax": 201_000_000,
        "first_apron": 209_100_000, "second_apron": 222_000_000,
        "min_team_salary": 147_000_000,
        "full_mle": 15_048_000, "taxpayer_mle": 6_065_000,
        "room_exception": 9_369_000, "bae": 5_478_000,
        "match_t1": 8_000_000, "match_t2": 30_940_000,
        "min_scale": None, "is_projection": True,   # min_scale scaled below
    },
}

# Fields that simply scale by GROWTH for projected out-years.
SCALE_FIELDS = ["salary_cap", "luxury_tax", "first_apron", "second_apron",
                "min_team_salary", "full_mle", "taxpayer_mle", "room_exception",
                "bae", "match_t1", "match_t2"]

RULE_BLOCK = {
    # Trade matching. Below both aprons uses the bracketed formula; do not flatten
    # to 1.25. Thresholds (match_t1/match_t2) scale with the cap each year.
    "trade_matching": {
        "under_first_apron_brackets": [
            {"outgoing_max": "match_t1", "take_back": "2.00x + 250000"},
            {"outgoing_max": "match_t2", "take_back": "1.00x + match_t1"},
            {"outgoing_max": None, "take_back": "1.25x + 250000"},
        ],
        "first_apron_pct": 1.10, "first_apron_pct_confirm": True,
        "second_apron_pct": 1.00,
        "second_apron_no_aggregation": True,
    },
    "hard_cap_triggers": {
        "first_apron": ["full_mle", "bae", "sign_and_trade_acquire", "use_any_tpe_MIN"],
        "second_apron": ["taxpayer_mle"],
    },
    "repeater_lookback_years": 4,
    "repeater_threshold_years": 3,
    "frozen_pick": {
        "mechanism": "above 2nd apron freezes the first 7 drafts out; sustained "
                     "membership moves it to pick 30",
        "counting_window_candidates": ["2_of_4", "3_of_5"],
        "confirm": True,
    },
    # Approximate non-repeater luxury-tax bracket rates (per $1 over the line).
    # Shape is reliable; exact cents flagged CONFIRM against the CBA / Larry Coon.
    "tax_brackets_nonrepeater_approx": [
        {"over_by_max": 5_000_000, "rate": 1.50},
        {"over_by_max": 10_000_000, "rate": 1.75},
        {"over_by_max": 15_000_000, "rate": 2.50},
        {"over_by_max": 20_000_000, "rate": 4.75},
        {"over_by_max": None, "rate": 5.75},
    ],
    "tax_brackets_confirm": True,
    "stepien_rule": "cannot trade a future first that leaves the team without a "
                    "first in two consecutive future drafts; tradeable window is "
                    "7 drafts out",
}


def _round(x):
    return int(round(x / 1000.0) * 1000)   # round to nearest $1K, like the league


def scaled_min_scale(base_scale, factor):
    return {k: _round(v * factor) for k, v in base_scale.items()}


def build():
    rows = []
    today = time.strftime("%Y-%m-%d")

    base26 = ANCHORS["2026-27"]
    base26["min_scale"] = scaled_min_scale(MIN_SCALE_2025_26, base26["salary_cap"] / 154_647_000)

    for season in ("2025-26", "2026-27"):
        a = ANCHORS[season]
        row = {"season": season}
        for f in SCALE_FIELDS:
            row[f] = a[f]
        row["min_salary_by_yos"] = a["min_scale"]
        row.update(RULE_BLOCK)
        row["is_projection"] = a["is_projection"]
        row["source"] = "NBA PR (2025-26 final); Hoops Rumors / reporting (2026-27 proj)"
        row["as_of_date"] = today
        rows.append(row)

    # Project 2027-28 .. 2029-30 by scaling 2026-27.
    prev = {f: base26[f] for f in SCALE_FIELDS}
    prev_scale = base26["min_scale"]
    for season in ("2027-28", "2028-29", "2029-30"):
        cur = {f: _round(prev[f] * GROWTH) for f in SCALE_FIELDS}
        cur_scale = scaled_min_scale(prev_scale, GROWTH)
        row = {"season": season}
        row.update(cur)
        row["min_salary_by_yos"] = cur_scale
        row.update(RULE_BLOCK)
        row["is_projection"] = True
        row["source"] = f"projected from 2026-27 at {GROWTH:.2f}x/yr growth"
        row["as_of_date"] = today
        rows.append(row)
        prev, prev_scale = cur, cur_scale

    payload = {
        "built": today,
        "growth_assumption_outyears": GROWTH,
        "notes": "2025-26 final; 2026-27 researched projection; 2027-28+ scaled. "
                 "Confirm flags mark figures the rules reference says need a "
                 "primary-source check before publication.",
        "seasons": {r["season"]: r for r in rows},
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print(f"Wrote {len(rows)} seasons -> {OUT}")
    for r in rows:
        print(f"  {r['season']}: cap={r['salary_cap']:,} tax={r['luxury_tax']:,} "
              f"apron1={r['first_apron']:,} apron2={r['second_apron']:,} "
              f"{'(proj)' if r['is_projection'] else '(final)'}")


if __name__ == "__main__":
    build()
