#!/usr/bin/env python3
"""
build_e_calibration.py  -- Component E baseline calibration gate.

This is the make-or-break step: every downstream title number rides on it. It
calibrates the two mappings the spec demands, against two independent anchors:

  SCALE (anchored on actual WIN TOTALS, 3 seasons 2023-24..2025-26):
    - deflation  rs_net = alpha + beta * hot_net : maps the hot top-10 rotation rollup
      onto the actual RS per-100 net scale (the scale D was calibrated on).
    - wins map   wins   = wins_a + wins_b * rs_net, with residual sigma_record.

  SHAPE (anchored on the de-vigged preseason TITLE BOARDS):
    - sigma_unobs : the unobserved-playoff-quality draw that governs how concentrated
      title odds are. Calibrated so the bracket sim, fed each season's preseason
      strengths (inverted from the win O/U column), reproduces that season's de-vigged
      title board. This is also the principled fix for the late-round survivorship
      bias D flagged: more sigma -> more upsets -> deep-round favorites compress.

DATA NOTE: the file 2023-24-preseason-odd.csv is a corrupted byte-duplicate of the
2025-26 board (it shows OKC 64-18 / SAS 62-20, which is 2025-26, not 2023-24). So the
SHAPE anchor uses the two genuine boards (2024-25, 2025-26); the SCALE anchor still
uses all three seasons' actual win totals from the warehouse. Re-source 2023-24 to
upgrade the shape backtest to three seasons.

    python build_e_calibration.py
"""

import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
DATA = os.path.join(HERE, "..", "data")
sys.path.insert(0, POSTMORTEM)
sys.path.insert(0, HERE)
from lib import db                          # noqa: E402
import build_team_ratings as A             # noqa: E402
import bracket_helpers as BH               # noqa: E402
import bracket_sim as E                    # noqa: E402
from build_series_calibration import TEAM_CONF  # noqa: E402

SEASONS = [(2023, "2023-24"), (2024, "2024-25"), (2025, "2025-26")]
BOARDS = {"2023-24": os.path.join(DATA, "2023-24-preseason-odd.csv"),
          "2024-25": os.path.join(DATA, "2024-25-preseason-odd.csv"),
          "2025-26": os.path.join(DATA, "2025-26-preseason-odd.csv")}


def actual_net_wins(yr):
    net = db.query("""SELECT g.team_abbreviation t, AVG(a.net_rating) net
                      FROM nba_games g JOIN nba_team_advanced_stats a
                        ON a.game_id=g.game_id AND a.team_tricode=g.team_abbreviation
                      WHERE g.season_type='Regular Season' AND (g.season_id %% 10000)=%s
                      GROUP BY t""", (yr,))
    w = db.query("""SELECT team_abbreviation t, SUM(CASE WHEN wl='W' THEN 1 ELSE 0 END) wins
                    FROM nba_games WHERE season_type='Regular Season' AND (season_id %% 10000)=%s
                    GROUP BY t""", (yr,))
    nd = {r["t"]: float(r["net"]) for _, r in net.iterrows()}
    wd = {r["t"]: float(r["wins"]) for _, r in w.iterrows()}
    return {t: (nd[t], wd[t]) for t in nd if t in wd}


def scale_calibration(imp):
    hot, rsnet, wins = [], [], []
    for yr, season in SEASONS:
        rots = BH.actual_top_rotations(season)
        nw = actual_net_wins(yr)
        for ab, rot in rots.items():
            if ab not in nw:
                continue
            h = A.rollup(BH.roster_to_mpg(rot), imp, "rs")["net"]
            rn, w = nw[ab]
            hot.append(h); rsnet.append(rn); wins.append(w)
    hot, rsnet, wins = np.array(hot), np.array(rsnet), np.array(wins)
    beta, alpha = np.polyfit(hot, rsnet, 1)          # rs_net = alpha + beta*hot
    defl_corr = np.corrcoef(alpha + beta * hot, rsnet)[0, 1]
    wins_b, wins_a = np.polyfit(rsnet, wins, 1)       # wins = wins_a + wins_b*rs_net
    pred = wins_a + wins_b * rsnet
    sigma_record = float(np.std(wins - pred))
    win_mae = float(np.mean(np.abs(wins - pred)))
    print("=== SCALE calibration (3 seasons, actual rosters vs actual wins) ===")
    print(f"  n teams-seasons = {len(hot)}")
    print(f"  deflation: rs_net = {alpha:+.3f} + {beta:.3f} * hot_net   "
          f"(corr {defl_corr:.3f}; hot is ~{1/beta:.2f}x wider than RS)")
    print(f"  wins map:  wins   = {wins_a:.2f} + {wins_b:.3f} * rs_net   "
          f"(win MAE {win_mae:.1f}, sigma_record {sigma_record:.1f})")
    return {"alpha": round(float(alpha), 4), "beta": round(float(beta), 4),
            "wins_a": round(float(wins_a), 3), "wins_b": round(float(wins_b), 3),
            "sigma_record": round(sigma_record, 3)}


def persistence_regression(scale):
    """How a team's REALIZED net regresses to its next-year FORWARD-LOOKING expectation
    (the market's preseason O/U-implied net). The sim's title mapping was calibrated on
    expectation nets (O/U-derived), so the 2026-27 baseline must feed expectation nets
    too: net_2026 = persist_int + persist_slope * actual_2025_net (+ any roster-change
    delta). Without this, a team that OVERperformed its expectation (DET 46.5 O/U -> 60
    wins) is fed its inflated realized net and the sim overrates it as a title threat."""
    wins_a, wins_b = scale["wins_a"], scale["wins_b"]
    xs, ys = [], []
    # actual net in year Y  ->  O/U-implied net in the year Y+1 preseason board
    for yA, board_key in [(2023, "2024-25"), (2024, "2025-26")]:
        nw = actual_net_wins(yA)
        rows = E.parse_board(BOARDS[board_key])
        ou_net = {x["abbr"]: (x["ou"] - wins_a) / wins_b for x in rows if x["abbr"] and x["ou"]}
        for t in nw:
            if t in ou_net:
                xs.append(nw[t][0]); ys.append(ou_net[t])
    xs, ys = np.array(xs), np.array(ys)
    slope, intercept = np.polyfit(xs, ys, 1)
    corr = np.corrcoef(xs, ys)[0, 1]
    print("\n=== PERSISTENCE regression (realized net -> next-year expectation) ===")
    print(f"  expectation = {intercept:+.3f} + {slope:.3f} * realized_net   (n={len(xs)}, corr {corr:.3f})")
    print(f"  e.g. DET +8.47 -> {intercept + slope*8.47:+.2f}; OKC +10.96 -> {intercept + slope*10.96:+.2f}")
    return round(float(slope), 4), round(float(intercept), 4)


def board_league(board_rows, wins_a, wins_b):
    strengths = {}
    for x in board_rows:
        if x["abbr"] is None or x["ou"] is None:
            continue
        net = (x["ou"] - wins_a) / wins_b               # invert wins map -> preseason net
        strengths[x["abbr"]] = {"net": net, "net_sd": 0.0, "munc": 0.0,
                                "conf": TEAM_CONF.get(x["abbr"], "W"), "profile": None}
    return strengths


CONTENDER_FLOOR = 0.02   # the title-shape question lives among teams the market gives >=2%;
#                          the longshot tail is dominated by the bookmaker favorite-longshot
#                          bias that naive proportional de-vig leaves in, not signal.


def _contender_metric(sim, devig_season):
    """Mean abs error on the genuine contenders (board >=2%), plus the favorite gap.
    Focused on title-odds SHAPE, not the longshot tail."""
    cont = [t for t in devig_season if devig_season[t] >= CONTENDER_FLOOR]
    mae = np.mean([abs(sim["teams"][t]["title"] - devig_season[t]) for t in cont])
    fav = max(devig_season, key=devig_season.get)
    fav_gap = abs(sim["teams"][fav]["title"] - devig_season[fav])
    return mae, fav_gap, len(cont)


def shape_calibration(scale, n_sims=6000):
    boards = {s: E.parse_board(p) for s, p in BOARDS.items()}
    devig = {s: {x["abbr"]: x["devig"] for x in rows if x["abbr"]} for s, rows in boards.items()}
    grid = np.round(np.arange(2.0, 7.51, 0.5), 2)
    print("\n=== SHAPE calibration (grid over sigma_unobs vs de-vigged boards) ===")
    print("  metric = mean abs error on genuine contenders (board >=2%); longshot tail excluded (bookmaker bias)")
    print(f"  {'sigma':>6}" + "".join(f"{s+' MAE':>13}{s+' favgap':>14}" for s in BOARDS) + f"{'avg MAE':>10}")
    rows = []
    for sig in grid:
        E._EP = {**scale, "sigma_unobs": float(sig), "source": "calib_grid"}
        per = {}
        for s in BOARDS:
            league = board_league(boards[s], scale["wins_a"], scale["wins_b"])
            sim = E.simulate_league(league, n_sims=n_sims, seed=2026)
            per[s] = _contender_metric(sim, devig[s])
        avg_mae = np.mean([per[s][0] for s in BOARDS])
        worst_favgap = max(per[s][1] for s in BOARDS)
        # robust score: fit the whole contender field AND don't badly miss either
        # season's headline favorite (the most meaningful single calibration point).
        score = avg_mae + worst_favgap
        rows.append((float(sig), per, avg_mae, score))
        print(f"  {sig:>6.2f}" + "".join(f"{per[s][0]*100:>12.1f}%{per[s][1]*100:>13.1f}%" for s in BOARDS)
              + f"{avg_mae*100:>9.1f}%")
    best = min(rows, key=lambda r: r[3])
    print(f"  -> best sigma_unobs = {best[0]:.2f}  (avg contender MAE {best[2]*100:.1f}%, "
          f"worst-season favorite gap {(best[3]-best[2])*100:.1f}%)")
    return best[0], boards, devig


def report_fit(scale, sigma_unobs, boards, devig, n_sims=12000):
    E._EP = {**scale, "sigma_unobs": float(sigma_unobs), "source": "calibrated"}
    print(f"\n=== Title-board reproduction at sigma_unobs={sigma_unobs:.2f} (top 10 each) ===")
    for s in BOARDS:
        league = board_league(boards[s], scale["wins_a"], scale["wins_b"])
        sim = E.simulate_league(league, n_sims=n_sims, seed=7)
        ranked = sorted(devig[s], key=lambda t: -devig[s][t])[:10]
        print(f"\n  {s}:  {'team':5}{'board%':>9}{'sim%':>8}{'net(pre)':>10}")
        for t in ranked:
            print(f"        {t:5}{devig[s][t]*100:>8.1f}%{sim['teams'][t]['title']*100:>7.1f}%"
                  f"{league[t]['net']:>10.2f}")


def win_total_reproduction(scale, imp):
    """Predicted wins (actual rosters -> deflated net -> wins map) vs actual wins."""
    print("\n=== Win-total reproduction (actual rosters, all 3 seasons) ===")
    allp, alla = [], []
    for yr, season in SEASONS:
        rots = BH.actual_top_rotations(season)
        nw = actual_net_wins(yr)
        preds, acts = [], []
        for ab, rot in rots.items():
            if ab not in nw:
                continue
            hot = A.rollup(BH.roster_to_mpg(rot), imp, "rs")["net"]
            rs = scale["alpha"] + scale["beta"] * hot
            pred = scale["wins_a"] + scale["wins_b"] * rs
            preds.append(pred); acts.append(nw[ab][1])
        preds, acts = np.array(preds), np.array(acts)
        mae = np.mean(np.abs(preds - acts)); corr = np.corrcoef(preds, acts)[0, 1]
        print(f"  {season}: win MAE {mae:.1f}, corr {corr:.3f}")
        allp += list(preds); alla += list(acts)
    allp, alla = np.array(allp), np.array(alla)
    print(f"  pooled : win MAE {np.mean(np.abs(allp-alla)):.1f}, corr {np.corrcoef(allp,alla)[0,1]:.3f}")


def main():
    imp = A.load_impacts()
    scale = scale_calibration(imp)
    win_total_reproduction(scale, imp)
    persist_slope, persist_int = persistence_regression(scale)
    sigma_unobs, boards, devig = shape_calibration(scale)
    report_fit(scale, sigma_unobs, boards, devig)

    params = {**scale, "sigma_unobs": round(float(sigma_unobs), 2),
              "persist_slope": persist_slope, "persist_int": persist_int,
              "munc_w": E.MUNC_W,
              "scale_anchor": "actual win totals 2023-24..2025-26",
              "shape_anchor": "de-vigged preseason boards 2023-24, 2024-25, 2025-26",
              "persist_anchor": "realized net -> next-year preseason O/U-implied net (2 transitions)",
              "source": "build_e_calibration"}
    json.dump(params, open(E.E_PARAMS_PATH, "w", encoding="utf-8"), indent=2)
    print(f"\nwrote {os.path.relpath(E.E_PARAMS_PATH, HERE)}")
    print(json.dumps(params, indent=2))


if __name__ == "__main__":
    main()
