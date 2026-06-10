#!/usr/bin/env python3
"""
build_team_state.py

Builds team_state: the derived rollup the feasibility module queries. One row per
(team_abbr, season, scenario_id). It sits on top of the three raw files and the
league_year_constants, and recomputes totals from the contracts file rather than
storing a hand-maintained number, so every total is auditable and a scenario is
just a different roster fed through the same machinery.

Two salary bases, kept distinct because the CBA compares different lines to
different totals (this matters: conflating them mislabels a team's tier and kit):
- apron_team_salary  = actual salaries (+ likely bonuses, dead money, roster
  charges to 12). The TAX and APRON lines are compared to this.
- cap_team_salary    = actual salaries + cap holds + roster charges. The CAP line
  (under/over-cap, room exception) is compared to this. A team can be low on the
  apron basis but over the cap once its own free agents' holds are added.

Base assumptions (stored in the assumptions field so every row is auditable):
- Player options: counted at value (on the books until the player declines).
- Team options: counted only when likely exercised. Heuristic: exercised when the
  option is at or below that season's full MLE (rookie-scale and cheap deals teams
  keep), declined and excluded when larger (big veteran options teams routinely
  shed, e.g. a ~$24M option). The excluded amount is tracked.
- Own pending free agents carried at an (approximate) cap hold in the cap basis only.
- Repeater status projects the taxpayer flag forward in future seasons (taxpayer
  when projected apron salary clears the tax line) so the out-year cascade is not
  understated by a history-only lookback.

Run order: build_league_constants.py, build_tax_and_tpe.py, the scrapers +
enrich_player_ids.py, then this.
    python build_team_state.py
"""

import os
import re
import csv
import json
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
CONSTANTS = os.path.join(DATA, "league_year_constants.json")
CONTRACTS = os.path.join(DATA, "nba_contracts_2026_27.csv")
FREE_AGENTS = os.path.join(DATA, "nba_free_agents_2026.csv")
PICKS = os.path.join(DATA, "nba_draft_picks_future.csv")
TAX_HISTORY = os.path.join(DATA, "tax_history.csv")
TPES = os.path.join(DATA, "team_trade_exceptions.csv")
OUT_CSV = os.path.join(DATA, "team_state.csv")
OUT_JSON = os.path.join(DATA, "team_state.json")

SEASONS = ["2026-27", "2027-28", "2028-29", "2029-30"]
SEASON_COL = {s: "salary_" + s.replace("-", "_") for s in SEASONS}
ROSTER_TARGET = 12
TRADE_WINDOW = [str(y) for y in range(2026, 2034)]
TEAM_FIX = {"NO": "NOP", "NY": "NYK", "GS": "GSW", "SA": "SAS", "PHO": "PHX",
            "WSH": "WAS", "UTAH": "UTA", "NOR": "NOP"}

# Team-option intent is a player-value judgment, not derivable from the option
# amount (teams EXERCISE big team-friendly options on good players, e.g. OKC's
# Hartenstein $28.5M and Dort $17.2M, and DECLINE options a player has outplayed
# downward). So team options default to counted (exercised); only nba_player_ids
# in this curated set are treated as likely-declined and excluded. Analyst input,
# refine in Pass-2.
TEAM_OPTION_LIKELY_DECLINED = {
    "1630228",   # Jonathan Kuminga (ATL), $24.3M 2026-27 team option (per Bobby's note)
}


def _int(v):
    v = (v or "").strip()
    return int(v) if v.lstrip("-").isdigit() else 0


def season_start_year(season):
    return int(season[:4])


def prior_seasons(season, n):
    s = season_start_year(season)
    return [f"{y}-{str((y + 1) % 100).zfill(2)}" for y in range(s - n, s)]


def load_constants():
    with open(CONSTANTS, encoding="utf-8") as fh:
        return json.load(fh)["seasons"]


def load_csv(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ----------------------------------------------------------------------------- #
# Salary build-up
# ----------------------------------------------------------------------------- #
def team_salary(rows, team, season, const, removed_ids=frozenset()):
    """Salary roll-up for one team-season under base assumptions."""
    col = SEASON_COL[season]
    guaranteed = po = to_counted = to_declined = 0
    n_contract = n_guaranteed = 0
    for r in rows:
        if r["team_abbr"] != team or r["two_way_flag"] == "TRUE":
            continue
        if r["nba_player_id"] and r["nba_player_id"] in removed_ids:
            continue
        sal = _int(r[col])
        if sal <= 0:
            continue
        if r["player_option_flag"] == "TRUE" and r["player_option_year"] == season:
            po += sal
            n_contract += 1
        elif r["team_option_flag"] == "TRUE" and r["team_option_year"] == season:
            if r["nba_player_id"] in TEAM_OPTION_LIKELY_DECLINED:
                to_declined += sal              # curated likely-decline (analyst input)
            else:
                to_counted += sal               # default: team option exercised, on the books
                n_contract += 1
        else:
            guaranteed += sal
            n_guaranteed += 1
            n_contract += 1

    rookie_min = const["min_salary_by_yos"]["0"]
    apron_charges = max(0, ROSTER_TARGET - n_contract) * rookie_min
    apron_team_salary = guaranteed + po + to_counted + apron_charges
    return {
        "guaranteed_salary": guaranteed,
        "player_option_salary_counted": po,
        "team_option_salary_counted": to_counted,
        "team_option_declined_excluded": to_declined,
        "nonguaranteed_salary_counted": 0,
        "dead_money": 0,
        "incentives_likely": 0,
        "incentives_unlikely": 0,
        "incomplete_roster_charges": apron_charges,
        "apron_team_salary": apron_team_salary,
        "num_under_contract": n_contract,
        "num_guaranteed": n_guaranteed,
    }


def cap_holds_for(fa_rows, team):
    """Approximate cap holds for a team's own pending UFA/RFA (cap basis only).
    Proxy: prior AAV. Pass-2 should use the Bird-based percentage of prior salary.
    Returns (total, count)."""
    if not fa_rows:
        return 0, 0
    total = n = 0
    for r in fa_rows:
        pt = TEAM_FIX.get((r.get("previous_team") or "").upper(), (r.get("previous_team") or "").upper())
        if pt == team and r.get("fa_type") in ("UFA", "RFA"):
            total += _int(r.get("previous_aav"))
            n += 1
    return total, n


def tpe_available(tpe_rows, team, season):
    """Season-aware TPE summary. A TPE counts toward a season only if it has not
    expired before that league year starts (July 1 of the start year). Returns
    (sum_remaining, max_single) since TPEs cannot be combined in one trade."""
    if not tpe_rows:
        return None, None
    cutoff = f"{season_start_year(season)}-07-01"
    avail = []
    for r in tpe_rows:
        if r["team_abbr"] != team or r.get("is_active", "TRUE").upper() == "FALSE":
            continue
        if (r.get("expiry_date") or "") >= cutoff:
            avail.append(_int(r.get("remaining") or r.get("amount")))
    return (sum(avail), max(avail) if avail else 0)


# ----------------------------------------------------------------------------- #
# Tier, toolbox, permissions
# ----------------------------------------------------------------------------- #
def derive_tier(apron_sal, under_cap, const):
    """under/over-cap decided on the CAP basis (passed in); the tax/apron ladder on
    the apron basis."""
    if under_cap:
        return "under_cap"
    if apron_sal < const["luxury_tax"]:
        return "over_cap_under_tax"
    if apron_sal < const["first_apron"]:
        return "taxpayer"
    if apron_sal < const["second_apron"]:
        return "first_apron"
    return "second_apron"


def toolbox(tier):
    below_first = tier in ("over_cap_under_tax", "taxpayer")
    return {
        "full_mle_available": below_first,
        "taxpayer_mle_available": tier == "first_apron",
        "room_exception_available": tier == "under_cap",
        "bae_available": below_first,
        "min_exception_available": True,
        "matching_rule": ("tiered_125" if tier in ("under_cap", "over_cap_under_tax", "taxpayer")
                          else "pct_110" if tier == "first_apron" else "pct_100"),
        "can_aggregate": tier != "second_apron",
        "can_take_back_more_than_send": tier != "second_apron",
        "can_acquire_sign_and_trade": tier not in ("first_apron", "second_apron"),
        "can_use_prior_year_tpe": tier != "second_apron",
        "can_send_cash": tier != "second_apron",
        "can_sign_bought_out_above_mle": tier not in ("first_apron", "second_apron"),
    }


# ----------------------------------------------------------------------------- #
# Tradeable firsts (Stepien pass, v1)
# ----------------------------------------------------------------------------- #
def tradeable_firsts(pick_rows, team):
    """v1 Stepien pass. clean_count = own, outright (unconditional, unfrozen) firsts
    legally tradeable now (removing one leaves no two consecutive future years
    without a first). Full list tagged by type for human review. v1 tests picks
    independently and trusts the ledger's control rows."""
    firsts = [r for r in pick_rows
              if r["controlling_team"] == team and r["round"] == "1" and r["year"] in TRADE_WINDOW]
    held_years = {r["year"] for r in firsts}

    def two_consec_gap(years_with):
        return any(TRADE_WINDOW[i] not in years_with and TRADE_WINDOW[i + 1] not in years_with
                   for i in range(len(TRADE_WINDOW) - 1))

    listed, clean = [], 0
    for r in firsts:
        cond = (r["condition"] or "").lower()
        is_own = r["pick_origin"].strip()[:3].upper() == team
        is_swap, frozen = "swap" in cond, "frozen" in cond
        conditional = (is_swap or frozen or "favorable" in cond or "if " in cond
                       or "via" in cond or "protect" in cond or bool(re.search(r"\d", cond)))
        if frozen:
            typ, tradeable = "frozen_untradeable", False
        elif is_own and not conditional:
            tradeable = not two_consec_gap(held_years - {r["year"]})
            typ = "own_outright"
            clean += 1 if tradeable else 0
        elif is_own:
            typ, tradeable = "own_conditional_review", None
        else:
            typ, tradeable = ("incoming_swap" if is_swap else "incoming"), None
        listed.append({"year": r["year"], "origin": r["pick_origin"], "type": typ,
                       "tradeable": tradeable, "condition": r["condition"]})
    listed.sort(key=lambda d: (d["year"], d["type"]))
    return clean, listed


# ----------------------------------------------------------------------------- #
# Repeater (history + forward projection)
# ----------------------------------------------------------------------------- #
def repeater_status(team, season, const, taxpayer_flags):
    """Repeater = taxpayer in >= threshold of the prior lookback seasons. Uses
    historical flags where available and projected flags for modeled seasons."""
    lookback, threshold = const["repeater_lookback_years"], const["repeater_threshold_years"]
    window = {s: taxpayer_flags.get((team, s)) for s in prior_seasons(season, lookback)}
    known = {s: v for s, v in window.items() if v is not None}
    if not known:
        return None, None
    return (sum(1 for v in known.values() if v) >= threshold), window


# ----------------------------------------------------------------------------- #
# Assemble
# ----------------------------------------------------------------------------- #
BASE_ASSUMPTIONS = {
    "player_options": "counted at value (on books until declined)",
    "team_options": "counted at value (exercised) by default; only curated likely-declines (TEAM_OPTION_LIKELY_DECLINED, analyst input) excluded. Amount does not determine intent.",
    "nonguaranteed": "treated as guaranteed (guarantee dates are Pass-2)",
    "own_free_agents": "approx cap hold (prior AAV) in cap basis only; not in apron salary",
    "roster_charges": f"apron basis filled to {ROSTER_TARGET} at rookie min; cap basis counts holds toward the {ROSTER_TARGET}",
    "repeater": "taxpayer flag projected forward in future seasons (apron salary > tax line)",
}


def build_row(team, season, scenario_id, scenario_label, removed_ids,
              contracts, fa_rows, pick_rows, const, tpe_rows, taxpayer_flags):
    sb = team_salary(contracts, team, season, const, removed_ids)
    apron = sb["apron_team_salary"]
    cap = const["salary_cap"]

    holds, n_holds = (cap_holds_for(fa_rows, team) if season == "2026-27" else (0, 0))
    rookie_min = const["min_salary_by_yos"]["0"]
    cap_charges = max(0, ROSTER_TARGET - (sb["num_under_contract"] + n_holds)) * rookie_min
    salary_only = sb["guaranteed_salary"] + sb["player_option_salary_counted"] + sb["team_option_salary_counted"]
    cap_team_salary = salary_only + holds + cap_charges
    under_cap = cap_team_salary < cap

    tier = derive_tier(apron, under_cap, const)
    tb = toolbox(tier)
    tpe_sum, tpe_max = tpe_available(tpe_rows, team, season)
    rep, rep_window = repeater_status(team, season, const, taxpayer_flags)
    is_taxpayer = apron > const["luxury_tax"]
    tf_count, tf_list = tradeable_firsts(pick_rows, team)

    return {
        "team_abbr": team, "season": season,
        "scenario_id": scenario_id, "scenario_label": scenario_label,
        "assumptions": BASE_ASSUMPTIONS,
        **sb,
        "cap_holds": holds, "cap_team_salary": cap_team_salary, "cap_room": max(0, cap - cap_team_salary),
        "potential_cap_room_if_renounced": max(0, cap - (salary_only + sb["incomplete_roster_charges"])),
        "distance_to_cap": cap - cap_team_salary,              # cap basis (consistent with cap_room)
        "distance_to_tax": const["luxury_tax"] - apron,
        "distance_to_first_apron": const["first_apron"] - apron,
        "distance_to_second_apron": const["second_apron"] - apron,
        "tier": tier, "is_taxpayer": is_taxpayer,
        **tb,
        "tpe_total_available": tpe_sum, "tpe_max_single_available": tpe_max,
        "hard_capped": False, "hard_cap_level": "none",
        "hard_cap_line": None, "hard_cap_room": None, "hard_cap_trigger": "",
        "tradeable_firsts_count": tf_count, "tradeable_firsts": tf_list,
        "second_apron_pick_frozen": False,
        "taxpayer_this_season": is_taxpayer,
        "repeater_status": rep, "repeater_window": rep_window,
        "as_of_date": time.strftime("%Y-%m-%d"),
        "source": "computed from contracts + constants",
        "notes": "",
    }


def main():
    const_all = load_constants()
    contracts = load_csv(CONTRACTS)
    fa_rows = load_csv(FREE_AGENTS)
    pick_rows = load_csv(PICKS)
    tax_rows = load_csv(TAX_HISTORY)
    tpe_rows = load_csv(TPES)
    teams = sorted({r["team_abbr"] for r in contracts})

    # Combined taxpayer-flag map: historical (tax_history) + projected (apron > tax)
    # for the modeled seasons. Drives repeater across the out-year cascade.
    taxpayer_flags = {}
    if tax_rows:
        for r in tax_rows:
            taxpayer_flags[(r["team_abbr"], r["season"])] = r.get("paid_luxury_tax", "").upper() == "TRUE"
    for team in teams:
        for season in SEASONS:
            apron = team_salary(contracts, team, season, const_all[season])["apron_team_salary"]
            taxpayer_flags[(team, season)] = apron > const_all[season]["luxury_tax"]

    rows = []
    for team in teams:
        for season in SEASONS:
            rows.append(build_row(team, season, "base", "base case", frozenset(),
                                  contracts, fa_rows, pick_rows, const_all[season], tpe_rows, taxpayer_flags))

    GOBERT, RANDLE = "203497", "203944"
    for sid, label, removed in [
        ("s1_randle_out", "Randle traded out (subtraction-only baseline)", frozenset({RANDLE})),
        ("s2_gobert_out", "Gobert traded out (subtraction-only baseline)", frozenset({GOBERT})),
        ("s3_both_out", "Gobert and Randle traded out (subtraction-only baseline)", frozenset({GOBERT, RANDLE})),
    ]:
        for season in SEASONS:
            rows.append(build_row("MIN", season, sid, label, removed,
                                  contracts, fa_rows, pick_rows, const_all[season], tpe_rows, taxpayer_flags))

    flat_skip = {"assumptions", "tradeable_firsts", "repeater_window"}
    fieldnames = list(rows[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            flat = dict(r)
            for k in flat_skip:
                flat[k] = json.dumps(flat[k])
            w.writerow(flat)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump({"built": time.strftime("%Y-%m-%d"), "rows": rows}, fh, indent=2)

    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    print("\nMIN 2026-27:")
    for r in rows:
        if r["team_abbr"] == "MIN" and r["season"] == "2026-27":
            print(f"  [{r['scenario_id']:14}] apron=${r['apron_team_salary']:,} tier={r['tier']:18} "
                  f"tpe_sum=${r['tpe_total_available'] or 0:,} tpe_max=${r['tpe_max_single_available'] or 0:,}")


if __name__ == "__main__":
    main()
