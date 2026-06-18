#!/usr/bin/env python3
"""
build_value_layer.py

Two partner-side primitives the acceptance model and the cap-relief channel need:

  player_surplus.csv  surplus = par_value(consensus_net) - salary_2026_27, league-wide.
     The par-value curve is the OPEN-MARKET price of impact, fit salary ~ consensus_net
     over market-priced veterans (reliable rotation players on >= $8M deals: not
     minimums, not rookie-scale). Positive surplus = a bargain a team KEEPS (the
     adverse-selection signal); negative surplus = an overpay a team wants to shed.
     This is the same surplus = net - par(salary) discipline run_pairs / the capstone
     already use, now computed for every player.

  team_posture.csv    each team classified rebuilder / mid / contender FROM DATA (no hand
     list): a continuous rebuild_score from projected net rating (-> wins) + roster youth +
     salary commitment, plus floor_seeking (apron salary below the $147M floor, room to
     absorb) and over_apron_cutter (first/second-apron, shedding pressure). This drives the
     cap-relief acceptance channel: only a genuine rebuilder/floor-seeker/over-apron team
     accepts a negative-on-court salary dump, and only for a priced sweetener.

    python build_value_layer.py
"""

import os
import sys
import csv

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
sys.path.insert(0, HERE)
import build_team_ratings as A          # noqa: E402  (load_impacts)
import bracket_sim as E                 # noqa: E402  (build_2026_27_league -> per-team net)
import age_curve as AC                  # noqa: E402  (ages_2026_27)
import evaluate_move as EM              # noqa: E402  (load_constants, load_team_state)

PRICED_MIN_SALARY = 8_000_000           # fit the market curve on clearly market-set deals
FLOOR = None                            # set from constants in main()


def contracts_path():
    """Prefer the verified warehouse source (nba_player_contracts via verified_contracts.py); fall
    back to the legacy Pass-1 scrape only if the verified file has not been generated."""
    verified = os.path.join(DATA, "nba_contracts_2026_27_verified.csv")
    return verified if os.path.exists(verified) else os.path.join(DATA, "nba_contracts_2026_27.csv")


def load_contracts():
    """nba_player_id(str) -> contract row (salary, multi-year flag, team, option_type)."""
    out = {}
    for r in csv.DictReader(open(contracts_path(), encoding="utf-8")):
        pid = (r.get("nba_player_id") or "").strip()
        if not pid:
            continue
        try:
            sal = int(float(r["salary_2026_27"] or 0))
        except ValueError:
            sal = 0
        years = sum(1 for k in ("salary_2026_27", "salary_2027_28", "salary_2028_29", "salary_2029_30")
                    if (r.get(k) or "").strip())
        out[str(int(float(pid)))] = {"name": r["player"], "team": r["team_abbr"], "salary": sal,
                                     "position": r.get("position", ""), "years_left": years,
                                     "option": (r.get("option_2026_27") or "").strip()}
    return out


def load_value():
    """nba_player_id(str) -> {consensus_net, reliable, name}."""
    out = {}
    for r in csv.DictReader(open(os.path.join(DATA, "player_value.csv"), encoding="utf-8")):
        try:
            net = float(r["consensus_net"]) if (r.get("consensus_net") or "").strip() else None
        except ValueError:
            net = None
        out[str(int(float(r["player_id"])))] = {"net": net, "reliable": r.get("reliable", ""),
                                                "name": r.get("player_name", "")}
    return out


def fit_par_curves(contracts, value):
    """Two curves over market-priced veterans (reliable rotation, >= $8M, salary > 0):
      dollar curve  salary  = a + b * net   (par DOLLARS for an impact level; sweetener context)
      net curve     net     = c + d * salary (par NET for a salary level; the surplus baseline)
    Returns (a, b, c, d, r2_net, n). The PRIMARY surplus is in net units (consensus_net minus
    the par net for that salary), which the series uses and which is bounded: a max contract has
    a high par net, so a star sits near par, not at a fake huge deficit."""
    xs_net, ys_dol = [], []
    for pid, ct in contracts.items():
        v = value.get(pid)
        if not v or v["net"] is None or ct["salary"] <= 0:
            continue
        if str(v["reliable"]).strip().lower() != "true" or ct["salary"] < PRICED_MIN_SALARY:
            continue
        xs_net.append(v["net"]); ys_dol.append(ct["salary"])
    xs_net, ys_dol = np.array(xs_net), np.array(ys_dol)
    b, a = np.polyfit(xs_net, ys_dol, 1)              # salary = a + b*net
    d, c = np.polyfit(ys_dol, xs_net, 1)              # net    = c + d*salary
    pred = c + d * ys_dol
    r2 = 1 - np.sum((xs_net - pred) ** 2) / np.sum((xs_net - xs_net.mean()) ** 2)
    return a, b, c, d, r2, len(xs_net)


def build_surplus(contracts, value, a, b, c, d):
    ages = AC.ages_2026_27([pid for pid in contracts])
    rows = []
    for pid, ct in contracts.items():
        v = value.get(pid)
        net = v["net"] if (v and v["net"] is not None) else None
        sal = ct["salary"]
        age = ages.get(pid)
        if net is None or sal <= 0:
            # FA / option / non-guaranteed: not a tradeable asset on the 2026-27 book; no surplus.
            exp_net = surplus_net = par_dollars = dollar_gap = None
        else:
            exp_net = c + d * sal                     # par NET for this salary
            surplus_net = net - exp_net               # series definition, impact units
            par_dollars = a + b * net                 # par DOLLARS for this impact (context)
            dollar_gap = par_dollars - sal            # +underpaid / -overpaid in $ (sweetener context)
        rows.append({"player_id": pid, "player_name": ct["name"], "team_abbr": ct["team"],
                     "position": ct["position"], "salary_2026_27": sal,
                     "years_left": ct["years_left"], "option_2026_27": ct.get("option", ""),
                     "age": round(age, 1) if age is not None else "",
                     "consensus_net": round(net, 2) if net is not None else "",
                     "exp_net": round(exp_net, 2) if exp_net is not None else "",
                     "surplus_net": round(surplus_net, 2) if surplus_net is not None else "",
                     "par_dollars": round(par_dollars) if par_dollars is not None else "",
                     "dollar_gap": round(dollar_gap) if dollar_gap is not None else "",
                     "keep_flag": ("KEEP" if (surplus_net is not None and surplus_net >= 1.0)
                                   else "shed" if (surplus_net is not None and surplus_net <= -1.0)
                                   else "neutral" if surplus_net is not None else "fa_unpriced")})
    return rows


def projected_net():
    """team -> projected 2026-27 net rating (deterministic, no Monte Carlo)."""
    imp = A.load_impacts()
    league = E.build_2026_27_league(imp)
    return {t: float(d["net"]) for t, d in league.items()}


def roster_youth(contracts):
    """team -> share of 2026-27 salary committed to players who'll be <= 23 at season start."""
    by_team = {}
    for pid, c in contracts.items():
        by_team.setdefault(c["team"], []).append((pid, c["salary"]))
    ages = AC.ages_2026_27([pid for pid in contracts])
    out = {}
    for team, plist in by_team.items():
        tot = sum(s for _, s in plist) or 1
        young = sum(s for pid, s in plist if (ages.get(pid) is not None and ages[pid] <= 23.0))
        out[team] = young / tot
    return out


def build_posture(contracts):
    const = EM.load_constants("2026-27")
    floor = const["min_team_salary"]
    nets = projected_net()
    youth = roster_youth(contracts)

    # net -> projected wins via the standard ~2.7 wins per net point about .500
    def proj_wins(net):
        return max(15.0, min(67.0, 41.0 + 2.7 * net))

    rows = []
    for team in sorted(nets):
        ts = EM.load_team_state(team, "2026-27", "base")
        apron = ts["apron_team_salary"]
        tier = ts["tier"]
        wins = proj_wins(nets[team])
        floor_seeking = apron < floor                       # room to / must absorb salary
        over_apron_cutter = tier in ("first_apron", "second_apron")
        # rebuild_score: low projected wins + roster youth + salary slack, each 0-1, averaged.
        w_score = max(0.0, min(1.0, (45.0 - wins) / 20.0))   # 1.0 at ~25 wins, 0 at >=45 wins
        youth_score = max(0.0, min(1.0, (youth[team] - 0.10) / 0.30))  # 1.0 at >=40% young salary
        slack_score = max(0.0, min(1.0, (floor - apron) / 40_000_000))  # 1.0 at $40M below floor
        rebuild = round((w_score + youth_score + slack_score) / 3.0, 3)
        posture = ("rebuilder" if rebuild >= 0.45 else
                   "retooler" if rebuild >= 0.25 else
                   "contender" if wins >= 52 else "mid")
        # a dump-absorber is a genuine rebuilder, OR a floor-seeker that is NOT a contender
        # (a cheap contender like a young DET will not eat bad money to help a rival).
        absorbs = rebuild >= 0.45 or (floor_seeking and posture in ("rebuilder", "retooler", "mid"))
        rows.append({"team_abbr": team, "proj_net": round(nets[team], 2), "proj_wins": round(wins, 1),
                     "apron_team_salary": round(apron), "tier": tier,
                     "youth_salary_share": round(youth[team], 3),
                     "floor_seeking": "TRUE" if floor_seeking else "FALSE",
                     "over_apron_cutter": "TRUE" if over_apron_cutter else "FALSE",
                     "rebuild_score": rebuild, "posture": posture,
                     "absorbs_dumps": "TRUE" if absorbs else "FALSE"})
    return rows


def main():
    contracts = load_contracts()
    value = load_value()

    a, b, c, d, r2, n = fit_par_curves(contracts, value)
    print(f"=== par curves over {n} market vets (reliable, >= $8M) ===")
    print(f"    dollar: salary ~= {a/1e6:.1f}M + {b/1e6:.2f}M * net   |   "
          f"net: exp_net ~= {c:+.2f} + {d*1e6:.3f} * (salary/$1M)   (R^2_net={r2:.2f})")
    for sal in (10, 20, 30, 45, 55):
        print(f"    salary ${sal}M -> par net {c + d*sal*1e6:+.2f}   (a +{sal}M player is 'par' at this net)")

    surplus = build_surplus(contracts, value, a, b, c, d)
    fields = ["player_id", "player_name", "team_abbr", "position", "salary_2026_27", "years_left",
              "option_2026_27", "age", "consensus_net", "exp_net", "surplus_net", "par_dollars",
              "dollar_gap", "keep_flag"]
    with open(os.path.join(DATA, "player_surplus.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(surplus)
    n_priced = sum(1 for r in surplus if r["surplus_net"] != "")
    print(f"\nplayer_surplus.csv: {len(surplus)} players ({n_priced} tradeable/priced, "
          f"{len(surplus)-n_priced} FA/option/non-guaranteed excluded)")

    ranked = sorted([r for r in surplus if r["surplus_net"] != ""], key=lambda r: -r["surplus_net"])
    print("\n  top 12 SURPLUS_NET (bargains -> KEEP, adverse selection):")
    for r in ranked[:12]:
        print(f"    {r['player_name']:24} {r['team_abbr']}  net {r['consensus_net']:+.2f}  "
              f"${r['salary_2026_27']/1e6:5.1f}M  surplus {r['surplus_net']:+.2f}  {r['keep_flag']}")
    print("  bottom 10 SURPLUS_NET (overpays -> shed):")
    for r in ranked[-10:]:
        print(f"    {r['player_name']:24} {r['team_abbr']}  net {r['consensus_net']:+.2f}  "
              f"${r['salary_2026_27']/1e6:5.1f}M  surplus {r['surplus_net']:+.2f}  {r['keep_flag']}")

    posture = build_posture(contracts)
    pf = ["team_abbr", "proj_net", "proj_wins", "apron_team_salary", "tier", "youth_salary_share",
          "floor_seeking", "over_apron_cutter", "rebuild_score", "posture", "absorbs_dumps"]
    with open(os.path.join(DATA, "team_posture.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=pf); w.writeheader(); w.writerows(posture)
    print(f"\nteam_posture.csv: {len(posture)} teams")
    print(f"  {'team':5}{'net':>7}{'wins':>6}{'rebuild':>9}{'posture':>11}  flags")
    for r in sorted(posture, key=lambda r: -r["rebuild_score"]):
        flags = []
        if r["floor_seeking"] == "TRUE": flags.append("floor-seek")
        if r["over_apron_cutter"] == "TRUE": flags.append("apron-cut")
        if r["absorbs_dumps"] == "TRUE": flags.append("ABSORBS-DUMPS")
        print(f"  {r['team_abbr']:5}{r['proj_net']:>+7.2f}{r['proj_wins']:>6.0f}"
              f"{r['rebuild_score']:>9.2f}{r['posture']:>11}  {', '.join(flags)}")


if __name__ == "__main__":
    main()
