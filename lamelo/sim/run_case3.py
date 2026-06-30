"""
GATE 2 Case 3: star-acquisition win-total retrodiction (now that power is confirmed).

For each clean OFFSEASON star acquisition in the sealed era, predict the acquiring team's
net-rating and win change from adding the star (engine: box-BPM star impact -> team net ->
wins), and compare to the realized change (acq season vs prior season). Pre-registered
pass: (a) predicted SIGN correct vs realized for every case, (b) central prediction within
4 wins for >= 60% of cases, (c) realized inside the 80% predictive band for 70-90%.

CAVEATS (stated, not hidden):
- Clean-room RAPM is 2023-26 only, so star impacts use the BOX-BPM model (era-transport of
  the box->impact map). Documented.
- The prediction is the star's MARGINAL contribution; it does not subtract the specific
  outgoing players, so it is biased slightly positive for star-for-star deals (most here
  are star-for-picks/role-players, where it is a fair approximation).
- Primary realized metric is on-court net-rating change (less noisy than wins).

Run: python lamelo/sim/run_case3.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

REPO = Path(__file__).resolve().parents[2]
SNAP = REPO / "lamelo" / "data" / "snapshot_2026-06-25"
sys.path.insert(0, str(REPO / "postmortem" / "lib"))
import db  # noqa: E402

WINS_B = 2.413   # FIT-era net->wins slope (gate 1b); STARTER_MIN/48 = role weight
STARTER_MIN = 32.0
# clean offseason star acquisitions: (player, acquiring team, acq season_year str, prior str)
STARS = [
    ("Paul George", "OKC", "2017-18", "2016-17"), ("Jimmy Butler", "MIN", "2017-18", "2016-17"),
    ("Kyrie Irving", "BOS", "2017-18", "2016-17"), ("Chris Paul", "HOU", "2017-18", "2016-17"),
    ("Kawhi Leonard", "TOR", "2018-19", "2017-18"), ("Rudy Gobert", "MIN", "2022-23", "2021-22"),
    ("Donovan Mitchell", "CLE", "2022-23", "2021-22"), ("Dejounte Murray", "ATL", "2022-23", "2021-22"),
]
OFF = ["pts36", "ast36", "tov36", "oreb36", "ts", "usg", "ast_pct", "fg3a_rate"]
DEF = ["stl36", "blk36", "dreb36", "pf36", "dreb_pct"]


def box_features_for(season_years):
    """Per-36 box + minute-weighted advanced for given season-year strings (snapshot)."""
    ps = pd.read_parquet(SNAP / "nba_player_stats.parquet")
    ps = ps[ps.season_year.isin(season_years)]
    agg = {c: (c, "sum") for c in ["minutes_played", "pts", "ast", "tov", "oreb", "dreb",
                                   "stl", "blk", "pf", "fg3a", "fga"]}
    box = ps.groupby(["player_id", "season_year"]).agg(**agg).reset_index().rename(columns={"minutes_played": "min"})
    box = box[box["min"] > 0]
    adv = pd.read_parquet(SNAP / "nba_player_advanced_stats.parquet")
    adv = adv[adv.game_id.isin(set(ps.game_id.unique()))].copy()
    adv["minutes_float"] = pd.to_numeric(adv["minutes_float"], errors="coerce").fillna(0.0)
    ps_g = ps[["game_id", "player_id", "season_year"]].drop_duplicates()
    adv = adv.merge(ps_g, left_on=["game_id", "person_id"], right_on=["game_id", "player_id"], how="inner")
    out = {}
    for src, dst in [("true_shooting_percentage", "ts"), ("usage_percentage", "usg"),
                     ("assist_percentage", "ast_pct"), ("defensive_rebound_percentage", "dreb_pct")]:
        adv["_wv"] = pd.to_numeric(adv[src], errors="coerce") * adv["minutes_float"]
        g = adv.groupby(["player_id", "season_year"]).agg(num=("_wv", "sum"), den=("minutes_float", "sum"))
        out[dst] = (g["num"] / g["den"].replace(0, np.nan)).rename(dst)
    advg = pd.concat(out.values(), axis=1).reset_index()
    df = box.merge(advg, on=["player_id", "season_year"], how="left")
    m = df["min"].clip(lower=1)
    p36 = lambda c: df[c] / m * 36.0
    f = pd.DataFrame({"player_id": df["player_id"], "season_year": df["season_year"], "min": df["min"]})
    f["pts36"], f["ast36"], f["tov36"] = p36("pts"), p36("ast"), p36("tov")
    f["oreb36"], f["dreb36"] = p36("oreb"), p36("dreb")
    f["stl36"], f["blk36"], f["pf36"] = p36("stl"), p36("blk"), p36("pf")
    f["fg3a_rate"] = df["fg3a"] / df["fga"].clip(lower=1)
    for c in ["ts", "usg", "ast_pct", "dreb_pct"]:
        f[c] = df[c].fillna(df[c].median())
    return f.fillna(0.0)


def fit_box_net_model():
    """Box features (2023-26) -> net_rapm; the era-general box->impact map."""
    imp = pd.read_csv(REPO / "lamelo" / "data" / "impact" / "player_impact.csv")
    feat = box_features_for(["2023-24", "2024-25", "2025-26"])
    feat = feat.sort_values("min").drop_duplicates("player_id", keep="last").reset_index(drop=True)
    d = imp.merge(feat, on="player_id", how="inner")
    d = d[d.reliable == True] if d.reliable.dtype == bool else d[d.reliable.astype(str) == "True"]
    X, y = d[OFF + DEF].to_numpy(), d["net_rapm"].to_numpy()
    return Ridge(alpha=50.0).fit(X, y)


def realized_team(season_year, team):
    yr = int(season_year[:4])  # "2017-18" -> 2017; nba_games keys on (season_id %% 10000)
    net = db.scalar("""SELECT AVG(a.net_rating) FROM nba_games g JOIN nba_team_advanced_stats a
                       ON a.game_id=g.game_id AND a.team_tricode=g.team_abbreviation
                       WHERE g.season_type='Regular Season' AND g.team_abbreviation=%s
                       AND (g.season_id %% 10000)=%s""", (team, yr))
    w = db.scalar("""SELECT SUM(CASE WHEN wl='W' THEN 1 ELSE 0 END) FROM nba_games
                     WHERE season_type='Regular Season' AND team_abbreviation=%s AND (season_id %% 10000)=%s""",
                  (team, yr))
    return (float(net) if net is not None else None, float(w) if w is not None else None)


def main():
    model = fit_box_net_model()
    prior_feats = box_features_for(sorted({pr for *_, pr in STARS}))
    pf = {(r.player_id, r.season_year): r for _, r in prior_feats.iterrows()}
    # star name -> id (prefix match handles name drift, e.g. "Jimmy Butler III")
    bio = db.query("SELECT player_id, display_first_last FROM nba_player_bio")

    def find_id(name):
        ex = bio[bio.display_first_last == name]
        if len(ex):
            return ex.iloc[0].player_id
        pre = bio[bio.display_first_last.str.startswith(name)]
        return pre.iloc[0].player_id if len(pre) else None

    rows = []
    for name, team, acq, prior in STARS:
        pid = find_id(name)
        feat = pf.get((pid, prior))
        if feat is None:
            print(f"  (skip {name}: no prior-season box features)"); continue
        x = np.array([[feat[c] for c in OFF + DEF]])
        star_net = float(model.predict(x)[0])
        pred_dnet = star_net * (STARTER_MIN / 48.0)
        pred_dwins = WINS_B * pred_dnet
        net_acq, w_acq = realized_team(acq, team)
        net_pri, w_pri = realized_team(prior, team)
        real_dnet = (net_acq - net_pri) if (net_acq is not None and net_pri is not None) else None
        real_dwins = (w_acq - w_pri) if (w_acq is not None and w_pri is not None) else None
        rows.append({"star": name, "team": team, "star_net": star_net,
                     "pred_dnet": pred_dnet, "pred_dwins": pred_dwins,
                     "real_dnet": real_dnet, "real_dwins": real_dwins})

    print(f"\n{'star':18}{'tm':4}{'box-net':>8}{'pred_dnet':>10}{'real_dnet':>10}{'pred_dW':>9}{'real_dW':>9}{'|errW|':>8}")
    sign_ok = within4 = covered = total = 0
    for r in rows:
        if r["real_dwins"] is None:
            continue
        total += 1
        errw = abs(r["pred_dwins"] - r["real_dwins"])
        s_ok = np.sign(r["pred_dnet"]) == np.sign(r["real_dnet"]) if r["real_dnet"] is not None else False
        sign_ok += int(s_ok); within4 += int(errw <= 4)
        covered += int(errw <= 6.4)  # 80% band ~ +/-6.4 wins (star-impact sd ~5)
        print(f"{r['star']:18}{r['team']:4}{r['star_net']:>+8.2f}{r['pred_dnet']:>+9.2f}"
              f"{(r['real_dnet'] if r['real_dnet'] is not None else float('nan')):>+9.2f}"
              f"{r['pred_dwins']:>+8.1f}{r['real_dwins']:>+8.1f}{errw:>8.1f}")
    print(f"\n  n={total}")
    print(f"  (a) sign correct: {sign_ok}/{total}  (pass = all)")
    print(f"  (b) within 4 wins: {within4}/{total}  (pass >= 60%: {0.6*total:.1f})")
    print(f"  (c) inside 80% band (~+/-6.4W): {covered}/{total}  (pass 70-90%)")
    a = sign_ok == total
    b = within4 >= 0.6 * total
    c = 0.7 * total <= covered <= 0.9 * total
    print(f"  -> Case 3: (a){'PASS' if a else 'FAIL'} (b){'PASS' if b else 'FAIL'} (c){'PASS' if c else 'FAIL'}")
    print("  NOTE: box-BPM era-transport + star-marginal (no outgoing subtraction) + realized")
    print("  win change is confounded by load management, fit, and outgoing players. Directional only.")
    return rows


if __name__ == "__main__":
    main()
