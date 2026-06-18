#!/usr/bin/env python3
"""
build_urgency_layer.py  -- Phase 2, Component A: the computed urgency and leverage layer.

Everything here comes ONLY from data (apron distance, health-adjusted projected wins, roster age,
contract years, surplus, the 6-dim need vectors). News-driven motivation lives elsewhere, in the
sourced motivation_overrides table; this layer never synthesizes a news signal from box scores.

Writes two files beside the existing data foundation:
  team_urgency.csv          one row per team: shed_pressure, win_now_pressure, asset_hunger,
                            expiring_risk (each normalized to [0,1] across the league), plus the
                            raw inputs for audit and the back-compat posture/flags carried through.
  player_market_heat.csv    one row per available player: need_fit summed over suitor teams,
                            market_heat (surplus x demand), and n_suitors. High heat = scarce and
                            coveted, a price premium; low/zero heat with high shed_pressure = a
                            forced sale, a discount.

Reads the Phase 1 health-adjusted projected wins via team_posture.csv (regenerated after the
returning-star correction), so IND reads as a 32-win mid, not a 26-win retooler.

    python build_urgency_layer.py
"""

import os
import sys
import csv
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# 2026-27 lines (millions), same source as evaluate_move.py
TAX, FIRST_APRON, SECOND_APRON = 201.0, 209.1, 222.0
SHED_W = (1.0, 2.0, 4.0)            # over-tax, over-first-apron, over-second-apron; steeper each band
WIN_NOW_WINS_W, WIN_NOW_AGE_W = 0.6, 0.4
DIMS = ["hc_creation", "secondary_playmaking", "off_ball_shooting",
        "def_versatility_poa", "rim_protect_reb", "transition"]
SUITOR_FIT_MIN = 0.04              # need_fit above which a team counts as a suitor
VALUE_FLOOR = 0.3                  # only players with consensus_net above this carry expiring_risk / heat


def _f(x, d=0.0):
    try:
        return float(x)
    except (ValueError, TypeError):
        return d


def minmax(d):
    """dict team/key -> raw value, returned normalized to [0,1] across the league (flat -> 0.0)."""
    vals = list(d.values())
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-12:
        return {k: 0.0 for k in d}
    return {k: (v - lo) / (hi - lo) for k, v in d.items()}


def load_posture():
    with open(os.path.join(DATA, "team_posture.csv"), encoding="utf-8") as fh:
        return {r["team_abbr"]: r for r in csv.DictReader(fh)}


def load_players():
    with open(os.path.join(DATA, "player_surplus.csv"), encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)]


def load_dims():
    out = {}
    with open(os.path.join(DATA, "player_dimensions.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[str(r["player_id"]).strip()] = {d: _f(r.get(d), 0.5) for d in DIMS}
    return out


def load_need_vectors():
    nv = collections.defaultdict(dict)
    with open(os.path.join(DATA, "team_needs.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            nv[r["team_abbr"]][r["dimension"]] = _f(r.get("need"), 0.0)
    return nv


# ------------------------------------- team signals ----------------------------------------- #
def resign_prob(player, posture):
    """PROXY (flagged): probability the player's own team re-signs him rather than lose him for
    nothing. From contract control, team cap posture, and age. No Bird-rights data in the book, so
    this is a documented heuristic, not a computed CBA value."""
    age = _f(player.get("age"), 28.0)
    tier = posture.get("tier", "")
    ppost = posture.get("posture", "mid")
    p = 0.55
    if tier != "under_cap":                 # an over-cap team can re-sign its own FA over the cap
        p += 0.15
    if ppost in ("rebuilder", "retooler"):  # a teardown is likelier to let a vet walk / cash out
        p -= 0.20
    if 25.0 <= age <= 30.0:
        p += 0.10
    elif age >= 33.0:
        p -= 0.15
    return max(0.10, min(0.95, p))


def build_team_urgency(posture, players):
    by_team = collections.defaultdict(list)
    for r in players:
        by_team[r["team_abbr"]].append(r)

    shed_raw, winnow_raw, hunger, exp_raw = {}, {}, {}, {}
    roster_age, exp_driver = {}, {}
    for team, pr in posture.items():
        sal_m = _f(pr.get("apron_team_salary")) / 1e6
        shed_raw[team] = (SHED_W[0] * max(0.0, sal_m - TAX)
                          + SHED_W[1] * max(0.0, sal_m - FIRST_APRON)
                          + SHED_W[2] * max(0.0, sal_m - SECOND_APRON))
        hunger[team] = _f(pr.get("rebuild_score"))         # already a clean 0..1 continuous

        roster = by_team.get(team, [])
        wsum = sum(_f(p.get("salary_2026_27")) for p in roster) or 1.0
        roster_age[team] = sum(_f(p.get("salary_2026_27")) * _f(p.get("age"), 28.0) for p in roster) / wsum

        # expiring_risk: max over valuable expiring players of net * (1 - resign_prob)
        best, who = 0.0, ""
        for p in roster:
            net = _f(p.get("consensus_net"))
            yrs = _f(p.get("years_left"), 1.0)
            if net < VALUE_FLOOR or yrs > 1:
                continue
            risk = net * (1.0 - resign_prob(p, pr))
            if risk > best:
                best, who = risk, p.get("player_name", "")
        exp_raw[team] = best
        exp_driver[team] = who

    wins = {t: _f(posture[t].get("proj_wins")) for t in posture}
    wins_n, age_n = minmax(wins), minmax(roster_age)
    winnow_raw = {t: WIN_NOW_WINS_W * wins_n[t] + WIN_NOW_AGE_W * age_n[t] for t in posture}

    shed_n = minmax(shed_raw)
    winnow_n = minmax(winnow_raw)
    hunger_n = minmax(hunger)
    exp_n = minmax(exp_raw)

    rows = []
    for team in sorted(posture):
        pr = posture[team]
        rows.append({
            "team_abbr": team,
            "shed_pressure": round(shed_n[team], 3),
            "win_now_pressure": round(winnow_n[team], 3),
            "asset_hunger": round(hunger_n[team], 3),
            "expiring_risk": round(exp_n[team], 3),
            "expiring_driver": exp_driver[team],
            "proj_wins": pr.get("proj_wins", ""),
            "roster_age": round(roster_age[team], 1),
            "apron_team_salary": pr.get("apron_team_salary", ""),
            "rebuild_score": pr.get("rebuild_score", ""),
            "posture": pr.get("posture", ""),
            "floor_seeking": pr.get("floor_seeking", ""),
            "over_apron_cutter": pr.get("over_apron_cutter", ""),
            "absorbs_dumps": pr.get("absorbs_dumps", ""),
        })
    return rows, winnow_n


# ------------------------------------- player market heat ----------------------------------- #
def acquire_weight(team, posture, winnow_n):
    """How hard a team would push to ACQUIRE: win-now pressure plus cap capacity to take salary on.
    Cap capacity = room below the second apron (a team far under can absorb; an over-apron team
    cannot easily add)."""
    sal_m = _f(posture[team].get("apron_team_salary")) / 1e6
    cap_capacity = max(0.0, min(1.0, (SECOND_APRON - sal_m) / 60.0))   # 1.0 at >= $60M under the 2nd apron
    return 0.6 * winnow_n.get(team, 0.0) + 0.4 * cap_capacity


def build_market_heat(posture, players, dims, need_vectors, winnow_n):
    aw = {t: acquire_weight(t, posture, winnow_n) for t in posture}
    rows = []
    for p in players:
        pid = str(p["player_id"]).strip()
        net = _f(p.get("consensus_net"))
        surplus = _f(p.get("surplus_net"))
        if p.get("consensus_net", "") == "" or net < VALUE_FLOOR or pid not in dims:
            continue
        av = dims[pid]
        own = p["team_abbr"]
        demand, suitors = 0.0, 0
        for team in posture:
            if team == own:
                continue
            nv = need_vectors.get(team, {})
            fit = sum(av[d] * nv.get(d, 0.0) for d in DIMS)
            if fit > SUITOR_FIT_MIN:
                demand += fit * aw[team]
                suitors += 1
        rows.append({
            "player_id": pid, "player_name": p.get("player_name", ""), "team_abbr": own,
            "consensus_net": round(net, 2), "surplus_net": round(surplus, 2),
            "sum_demand": round(demand, 3), "n_suitors": suitors,
            "market_heat_raw": round(surplus * demand, 3),
        })
    # normalize heat to [0,1] across priced players (clamped at 0 so forced sales sit at the floor)
    heats = {r["player_id"]: max(0.0, r["market_heat_raw"]) for r in rows}
    hn = minmax(heats)
    for r in rows:
        r["market_heat"] = round(hn[r["player_id"]], 3)
    rows.sort(key=lambda r: -r["market_heat"])
    return rows


def main():
    posture = load_posture()
    players = load_players()
    dims = load_dims()
    need_vectors = load_need_vectors()

    team_rows, winnow_n = build_team_urgency(posture, players)
    tf = ["team_abbr", "shed_pressure", "win_now_pressure", "asset_hunger", "expiring_risk",
          "expiring_driver", "proj_wins", "roster_age", "apron_team_salary", "rebuild_score",
          "posture", "floor_seeking", "over_apron_cutter", "absorbs_dumps"]
    with open(os.path.join(DATA, "team_urgency.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=tf); w.writeheader(); w.writerows(team_rows)

    heat_rows = build_market_heat(posture, players, dims, need_vectors, winnow_n)
    hf = ["player_id", "player_name", "team_abbr", "consensus_net", "surplus_net",
          "sum_demand", "n_suitors", "market_heat_raw", "market_heat"]
    with open(os.path.join(DATA, "player_market_heat.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=hf); w.writeheader(); w.writerows(heat_rows)

    print(f"team_urgency.csv: {len(team_rows)} teams   |   player_market_heat.csv: {len(heat_rows)} players")
    print("  (resign_prob inside expiring_risk is a documented PROXY: no Bird-rights data in the book)")
    print("\n  top 6 shed_pressure (eager to dump salary):")
    for r in sorted(team_rows, key=lambda r: -r["shed_pressure"])[:6]:
        print(f"    {r['team_abbr']:4} shed {r['shed_pressure']:.2f}  apron ${_f(r['apron_team_salary'])/1e6:.0f}M  {r['posture']}")
    print("  top 6 win_now_pressure (eager to upgrade, will overpay):")
    for r in sorted(team_rows, key=lambda r: -r["win_now_pressure"])[:6]:
        print(f"    {r['team_abbr']:4} win-now {r['win_now_pressure']:.2f}  {r['proj_wins']}w  age {r['roster_age']}")
    print("  top 6 asset_hunger (wants youth/picks):")
    for r in sorted(team_rows, key=lambda r: -r["asset_hunger"])[:6]:
        print(f"    {r['team_abbr']:4} hunger {r['asset_hunger']:.2f}  rebuild {r['rebuild_score']}  {r['posture']}")
    print("  top 8 market_heat (scarce + coveted -> premium):")
    for r in heat_rows[:8]:
        print(f"    {r['player_name']:24} {r['team_abbr']:4} heat {r['market_heat']:.2f}  "
              f"suitors {r['n_suitors']:2}  surplus {r['surplus_net']:+.2f}")


if __name__ == "__main__":
    main()
