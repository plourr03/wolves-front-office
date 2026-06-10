#!/usr/bin/env python3
"""
build_series_calibration.py  -- calibrate + validate Component D (series_resolver).

Pulls every playoff game 1997-2025 with each team's regular-season per-100 net
rating, fits the per-game logistic P(home win) ~ b0 + b1*(net_home - net_away),
writes b0/b1 to data/series_resolver_params.json, persists the assembled series to
data/playoff_series_history.csv, then validates the COMPOSED best-of-7 resolver two
ways the spec demands:

  1. by rating gap  -- bin series on the RS net-rating gap, compare the resolver's
     predicted favorite-wins-series rate to the empirical rate. This directly tests
     the calibration.
  2. by seed        -- reconstruct 1-8 seeds within (season, conference) from RS
     record, report higher-seed series win rate by matchup (1v8 ... 4v5) and overall,
     against the resolver's prediction. Seeds are a record-based reconstruction
     (division-winner reseeding pre-2016 and the 2021+ play-in add minor noise, so we
     also report how often our higher-seed agrees with the actual home-court holder).

    python build_series_calibration.py
"""

import os
import sys
import csv
import json
import numpy as np
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
DATA = os.path.join(HERE, "..", "data")
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POSTMORTEM, ".env"))
except ImportError:
    pass
sys.path.insert(0, POSTMORTEM)
sys.path.insert(0, HERE)
from lib import db  # noqa: E402
import series_resolver as D  # noqa: E402

ROUND_NAME = {1: "R1", 2: "R2(semis)", 3: "ConfFinals", 4: "Finals"}

# Fixed conference map for seed reconstruction. Covers every franchise abbreviation
# appearing 1997-2025, including relocations (Charlotte 1997-2002 = East; that
# franchise became New Orleans/West in 2003; Bobcats/new Hornets are East).
CONF = {
    "E": {"ATL", "BOS", "BKN", "NJN", "CHA", "CHO", "CHH", "CHI", "CLE", "DET",
          "IND", "MIA", "MIL", "NYK", "ORL", "PHI", "TOR", "WAS", "WSB"},
    "W": {"DAL", "DEN", "GSW", "HOU", "LAC", "LAL", "MEM", "VAN", "MIN", "NOP",
          "NOH", "NOK", "OKC", "SEA", "PHX", "POR", "SAC", "SAS", "UTA"},
}
TEAM_CONF = {t: c for c, ts in CONF.items() for t in ts}


def pull():
    """RS net rating + RS wins per (season, team), and all playoff game rows."""
    rs = db.query("""
        SELECT (g.season_id % 10000) yr, g.team_abbreviation tm,
               AVG(a.net_rating) net,
               SUM(CASE WHEN g.wl='W' THEN 1 ELSE 0 END) wins, COUNT(*) gp
        FROM nba_games g
        JOIN nba_team_advanced_stats a
          ON a.game_id=g.game_id AND a.team_tricode=g.team_abbreviation
        WHERE g.season_type='Regular Season'
        GROUP BY yr, tm""")
    net = {(int(r["yr"]), r["tm"]): float(r["net"]) for _, r in rs.iterrows()}
    wins = {(int(r["yr"]), r["tm"]): float(r["wins"]) for _, r in rs.iterrows()}

    po = db.query("""
        SELECT game_id, (season_id % 10000) yr, game_date, team_abbreviation tm,
               CASE WHEN matchup LIKE '%vs.%' THEN 1 ELSE 0 END home, wl
        FROM nba_games WHERE season_type LIKE '%Playoff%'
        ORDER BY game_date, game_id""")
    return net, wins, po


def assemble_series(net, wins, po):
    """Group playoff game rows into series. Returns a list of series dicts."""
    games = {}     # game_id -> {yr, round, home_tm, away_tm, home_won, date}
    for _, r in po.iterrows():
        gid = r["game_id"]
        g = games.setdefault(gid, {"yr": int(r["yr"]), "round": int(gid[7]),
                                   "date": r["game_date"]})
        side = "home_tm" if r["home"] == 1 else "away_tm"
        g[side] = r["tm"]
        if r["home"] == 1:
            g["home_won"] = (r["wl"] == "W")

    series = {}    # (yr, frozenset(teams)) -> aggregate
    for gid, g in games.items():
        if "home_tm" not in g or "away_tm" not in g:
            continue
        key = (g["yr"], frozenset({g["home_tm"], g["away_tm"]}))
        s = series.setdefault(key, {"yr": g["yr"], "round": g["round"],
                                    "games": [], "wins": {}, "first": None})
        winner = g["home_tm"] if g["home_won"] else g["away_tm"]
        s["wins"][winner] = s["wins"].get(winner, 0) + 1
        s["games"].append((gid, g))
        if s["first"] is None or gid < s["first"][0]:
            s["first"] = (gid, g)

    out = []
    for (yr, teams), s in series.items():
        a, b = sorted(teams)
        if (yr, a) not in net or (yr, b) not in net:
            continue
        champ = max(s["wins"], key=s["wins"].get)
        loser = a if champ == b else b
        # home-court holder = home team of the chronologically-first game
        first_g = s["first"][1]
        hc_team = first_g["home_tm"]
        out.append({
            "yr": yr, "round": s["round"], "n_games": len(s["games"]),
            "champ": champ, "loser": loser, "hc_team": hc_team,
            "net_champ": net[(yr, champ)], "net_loser": net[(yr, loser)],
            "wins_champ": wins.get((yr, champ), 0), "wins_loser": wins.get((yr, loser), 0),
            "teamA": a, "teamB": b,
        })
    return out


def reconstruct_seeds(series_list, wins):
    """Rank playoff teams within (season, conference) by RS wins (tie: net rating)
    to recover 1-8 seeds. Returns {(yr, team): seed}."""
    by_conf = {}   # (yr, conf) -> set of teams that made the playoffs
    teamnet = {}
    for s in series_list:
        for tm, nt in ((s["champ"], s["net_champ"]), (s["loser"], s["net_loser"])):
            c = TEAM_CONF.get(tm)
            if c is None:
                continue
            by_conf.setdefault((s["yr"], c), set()).add(tm)
            teamnet[(s["yr"], tm)] = nt
    seeds = {}
    for (yr, c), teams in by_conf.items():
        ranked = sorted(teams, key=lambda t: (-wins.get((yr, t), 0), -teamnet[(yr, t)]))
        for i, t in enumerate(ranked, start=1):
            seeds[(yr, t)] = i
    return seeds


def fit_game_logistic(net, po):
    """One row per playoff game: outcome=home win, predictor=net_home-net_away."""
    games = {}
    for _, r in po.iterrows():
        gid = r["game_id"]
        g = games.setdefault(gid, {"yr": int(r["yr"])})
        if r["home"] == 1:
            g["home_tm"] = r["tm"]; g["home_won"] = (r["wl"] == "W")
        else:
            g["away_tm"] = r["tm"]
    diffs, ys = [], []
    for gid, g in games.items():
        if "home_tm" not in g or "away_tm" not in g:
            continue
        key_h = (g["yr"], g["home_tm"]); key_a = (g["yr"], g["away_tm"])
        if key_h not in net or key_a not in net:
            continue
        diffs.append(net[key_h] - net[key_a])
        ys.append(1 if g["home_won"] else 0)
    X = sm.add_constant(np.array(diffs))
    res = sm.Logit(np.array(ys), X).fit(disp=0)
    b0, b1 = float(res.params[0]), float(res.params[1])
    se0, se1 = float(res.bse[0]), float(res.bse[1])
    return b0, b1, se0, se1, len(ys)


def validate_by_gap(series_list):
    print("\n=== Validation 1: by RATING GAP (favorite = higher RS net) ===")
    print("net ratings on the per-100 RS scale; model uses each series' actual home-court holder")
    bins = [(0, 2), (2, 4), (4, 6), (6, 9), (9, 99)]
    rows = []
    for lo, hi in bins:
        emp, pred, n = [], [], 0
        for s in series_list:
            fav, dog = (s["champ"], s["loser"]) if s["net_champ"] >= s["net_loser"] else (s["loser"], s["champ"])
            net_f = max(s["net_champ"], s["net_loser"]); net_d = min(s["net_champ"], s["net_loser"])
            gap = net_f - net_d
            if not (lo <= gap < hi):
                continue
            fav_won = (s["champ"] == fav)
            fav_has_hc = (s["hc_team"] == fav)
            p = D.base_series_prob(net_f, net_d, fav_has_hc)
            emp.append(1 if fav_won else 0); pred.append(p); n += 1
        if n:
            rows.append((f"{lo}-{hi if hi < 99 else '+'}", n, np.mean(emp), np.mean(pred)))
    print(f"{'gap':>8}{'n':>5}{'emp fav win%':>14}{'model fav win%':>16}{'resid':>8}")
    for label, n, e, p in rows:
        print(f"{label:>8}{n:>5}{e*100:>13.0f}%{p*100:>15.0f}%{(e-p)*100:>+7.0f}")
    return rows


def validate_by_seed(series_list, seeds):
    print("\n=== Validation 2: by SEED (higher seed = lower seed number) ===")
    # agreement between reconstructed higher-seed and actual home-court holder
    agree = tot = 0
    for s in series_list:
        sc = seeds.get((s["yr"], s["champ"])); sl = seeds.get((s["yr"], s["loser"]))
        if sc is None or sl is None or sc == sl:
            continue
        hi_team = s["champ"] if sc < sl else s["loser"]
        tot += 1
        if hi_team == s["hc_team"]:
            agree += 1
    print(f"reconstructed higher-seed == actual home-court holder in {agree}/{tot} "
          f"= {agree/tot*100:.0f}% of series (sanity on the seed reconstruction)")

    # first-round matchups 1v8 ... 4v5
    print(f"\n  first round, higher-seed series win rate:")
    print(f"  {'matchup':>9}{'n':>5}{'emp hi-seed win%':>18}{'model':>9}")
    for hs, ls in [(1, 8), (2, 7), (3, 6), (4, 5)]:
        emp, pred, n = [], [], 0
        for s in series_list:
            if s["round"] != 1:
                continue
            sc = seeds.get((s["yr"], s["champ"])); sl = seeds.get((s["yr"], s["loser"]))
            if sc is None or sl is None:
                continue
            pair = {sc, sl}
            if pair != {hs, ls}:
                continue
            hi_is_champ = (sc < sl)
            net_hi = s["net_champ"] if hi_is_champ else s["net_loser"]
            net_lo = s["net_loser"] if hi_is_champ else s["net_champ"]
            hi_team = s["champ"] if hi_is_champ else s["loser"]
            p = D.base_series_prob(net_hi, net_lo, s["hc_team"] == hi_team)
            emp.append(1 if hi_is_champ else 0); pred.append(p); n += 1
        if n:
            print(f"  {f'{hs}v{ls}':>9}{n:>5}{np.mean(emp)*100:>17.0f}%{np.mean(pred)*100:>8.0f}%")

    # overall higher-seed win rate by round
    print(f"\n  higher-seed series win rate by round:")
    print(f"  {'round':>11}{'n':>5}{'emp hi-seed win%':>18}{'model':>9}")
    for rnd in (1, 2, 3, 4):
        emp, pred, n = [], [], 0
        for s in series_list:
            if s["round"] != rnd:
                continue
            sc = seeds.get((s["yr"], s["champ"])); sl = seeds.get((s["yr"], s["loser"]))
            if sc is None or sl is None or sc == sl:
                continue
            hi_is_champ = (sc < sl)
            net_hi = s["net_champ"] if hi_is_champ else s["net_loser"]
            net_lo = s["net_loser"] if hi_is_champ else s["net_champ"]
            hi_team = s["champ"] if hi_is_champ else s["loser"]
            p = D.base_series_prob(net_hi, net_lo, s["hc_team"] == hi_team)
            emp.append(1 if hi_is_champ else 0); pred.append(p); n += 1
        if n:
            print(f"  {ROUND_NAME[rnd]:>11}{n:>5}{np.mean(emp)*100:>17.0f}%{np.mean(pred)*100:>8.0f}%")


def write_history(series_list, seeds):
    path = os.path.join(DATA, "playoff_series_history.csv")
    cols = ["yr", "round", "n_games", "champ", "loser", "hc_team",
            "seed_champ", "seed_loser", "net_champ", "net_loser",
            "wins_champ", "wins_loser"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for s in sorted(series_list, key=lambda x: (x["yr"], x["round"])):
            row = {k: s.get(k) for k in cols}
            row["seed_champ"] = seeds.get((s["yr"], s["champ"]), "")
            row["seed_loser"] = seeds.get((s["yr"], s["loser"]), "")
            for k in ("net_champ", "net_loser"):
                row[k] = round(s[k], 2)
            w.writerow(row)
    return path


def main():
    net, wins, po = pull()
    series_list = assemble_series(net, wins, po)
    seeds = reconstruct_seeds(series_list, wins)

    b0, b1, se0, se1, n = fit_game_logistic(net, po)
    params = {"b0": round(b0, 4), "b1": round(b1, 4), "b0_se": round(se0, 4),
              "b1_se": round(se1, 4), "n_games": n, "seasons": "1997-2025",
              "model": "P(home win)=sigmoid(b0 + b1*(net_home-net_away)); net on RS per-100 scale",
              "source": "build_series_calibration"}
    json.dump(params, open(D.PARAMS_PATH, "w", encoding="utf-8"), indent=2)
    D._PARAMS = params  # use freshly-fit params for validation below

    print(f"=== Component D calibration (per-game logistic, {n} playoff games 1997-2025) ===")
    print(f"  HCA b0 = {b0:+.3f} (se {se0:.3f})  ->  even-matchup home win P = {D._sigmoid(b0):.3f}")
    print(f"  net slope b1 = {b1:+.4f} (se {se1:.4f})  ->  +1 net pt = {D._sigmoid(b1)-0.5:+.3f} game win prob")
    print(f"  wrote {os.path.relpath(D.PARAMS_PATH, HERE)}")

    print(f"\n  composed best-of-7 base odds (favorite, has home court):")
    print(f"  {'net gap':>8}{'P(series)':>11}")
    for gap in (0, 2, 4, 6, 8, 12):
        print(f"  {gap:>8}{D.base_series_prob(gap,0,True):>11.3f}")

    validate_by_gap(series_list)
    validate_by_seed(series_list, seeds)
    path = write_history(series_list, seeds)
    print(f"\nwrote {len(series_list)} series to {os.path.relpath(path, HERE)}")


if __name__ == "__main__":
    main()
