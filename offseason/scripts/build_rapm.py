#!/usr/bin/env python3
"""
build_rapm.py

The on-court value spine: a multi-year, league-wide, box-score-informed RAPM
fit from the possession data built by build_possessions_league.py.

Method (the four checkpoint decisions):
1. FULL league-wide, 3 seasons (2023-24..2025-26, RS+PO), recency-weighted
   (more recent seasons count more).
2. BOX-SCORE-INFORMED 2-stage prior: fit a first-pass plain ridge RAPM, regress
   those estimates on per-player box-score features to LEARN a box model (the
   in-house "BPM"), then fit a second ridge that shrinks toward that prior mean.
   So low-minute players are pulled toward a sensible box estimate, not to zero.
3. Offense and defense are separate coefficients throughout.
4. Intervals: analytical ridge posterior SD (Bayesian-ridge interpretation),
   reported as a band. Bootstrap is a Pass-2 refinement.

Garbage time: approximated (no clock in the possession data) by dropping 4th-period
possessions in a >25-point blowout. Documented as an approximation.

Output: offseason/data/player_value.csv (joined to the crosswalk + playoff read).

    python build_rapm.py
"""

import os
import sys
import argparse
import glob
import csv
import numpy as np
import pandas as pd
from collections import Counter
from scipy.sparse import csr_matrix, hstack
from sklearn.linear_model import Ridge, RidgeCV

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
CACHE = os.path.join(HERE, "..", "data", "cache", "possessions_league")
# D89: the possession points column and the cache directory are overridable, so the fit
# can be run on the corrected points and on the pre-fix ones and the two compared.
POINTS_COL = "points_scored"
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(DATA, "player_value.csv")

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POSTMORTEM, ".env"))
except ImportError:
    pass
sys.path.insert(0, POSTMORTEM)
from lib import db  # noqa: E402

MIN_POSS = 1000                    # own column if total (off+def) possessions >= this
RELIABLE_POSS = 3000               # flag estimates below ~a season of rotation minutes
RECENCY = {2023: 0.69, 2024: 0.83, 2025: 1.0}   # ~0.83^k recency weight
ALPHAS = [500, 1000, 2000, 4000, 8000]
GARBAGE_MARGIN = 25                # 4th-period possessions beyond this margin dropped


def load_possessions(seasons=None):
    files = sorted(glob.glob(os.path.join(CACHE, "*.parquet")))
    print(f"loading {len(files)} game files ...", flush=True)
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    if seasons is not None:
        df = df[df["season_year"].isin(list(seasons))].reset_index(drop=True)
        print(f"  filtered to seasons {sorted(seasons)}: {len(df):,} possessions", flush=True)
    df = df.sort_values(["game_id", "possession_number"]).reset_index(drop=True)

    # approximate garbage-time filter: running absolute margin, drop 4th-period blowout
    pts = df[POINTS_COL].to_numpy()
    off = df["offensive_team_id"].to_numpy()
    gid = df["game_id"].to_numpy()
    absm = np.zeros(len(df), dtype=np.int32)
    cur, sA, sB, teamA = None, 0, 0, None
    for i in range(len(df)):
        if gid[i] != cur:
            cur, sA, sB, teamA = gid[i], 0, 0, off[i]
        absm[i] = abs(sA - sB)
        if off[i] == teamA:
            sA += pts[i]
        else:
            sB += pts[i]
    df["abs_margin"] = absm
    keep = ~((df["period"] >= 4) & (df["abs_margin"] > GARBAGE_MARGIN))
    print(f"  {len(df):,} possessions; garbage-time dropped {(~keep).sum():,}", flush=True)
    return df[keep].reset_index(drop=True)


def build_matrix(df):
    off_lists = df["off_players_str"].str.split(",").tolist()
    def_lists = df["def_players_str"].str.split(",").tolist()
    cnt = Counter()
    for lst in off_lists:
        cnt.update(int(p) for p in lst if p)
    for lst in def_lists:
        cnt.update(int(p) for p in lst if p)
    qualifying = sorted(p for p, c in cnt.items() if c >= MIN_POSS)
    col = {p: i for i, p in enumerate(qualifying)}
    R = len(qualifying)                                  # replacement column index = R
    print(f"  qualifying players (>= {MIN_POSS} poss): {R}; pooled: {len(cnt) - R}", flush=True)

    n = len(df)
    ro, co, rd, cd = [], [], [], []
    for i, lst in enumerate(off_lists):
        for p in lst:
            if p:
                ro.append(i); co.append(col.get(int(p), R))
    for i, lst in enumerate(def_lists):
        for p in lst:
            if p:
                rd.append(i); cd.append(col.get(int(p), R))
    X_off = csr_matrix((np.ones(len(ro), np.float32), (ro, co)), shape=(n, R + 1))
    X_def = csr_matrix((np.ones(len(rd), np.float32), (rd, cd)), shape=(n, R + 1))
    X = hstack([X_off, X_def]).tocsr()
    y = df[POINTS_COL].to_numpy(np.float32) * 100.0
    w = df["season_year"].map(RECENCY).to_numpy(np.float32)
    return X, y, w, qualifying, R


SEASON_STRS = {2023: "2023-24", 2024: "2024-25", 2025: "2025-26"}


def _season_strs(seasons):
    """Map possession season-year ints (e.g. 2023) to box-table strings ('2023-24').
    seasons=None -> the full canonical 3-season window (behavior-preserving)."""
    yrs = sorted(SEASON_STRS) if seasons is None else sorted(seasons)
    return tuple(SEASON_STRS[y] for y in yrs)


def box_features(seasons=None):
    """Per-player season aggregates -> per-100 rates + minute-weighted advanced rates.
    Feeds the learned box prior (the in-house BPM). seasons=None is the full canonical
    window; a subset restricts the box features to the same window as the fit."""
    ss = _season_strs(seasons)
    box = db.query("""
        SELECT player_id, SUM(minutes_played) min, SUM(pts) pts, SUM(ast) ast,
               SUM(tov) tov, SUM(oreb) oreb, SUM(dreb) dreb, SUM(stl) stl,
               SUM(blk) blk, SUM(pf) pf, SUM(fg3a) fg3a, SUM(fga) fga
        FROM nba_player_stats
        WHERE season_year IN %s
        GROUP BY player_id HAVING SUM(minutes_played) > 0""", (ss,))
    adv = db.query("""
        SELECT person_id AS player_id,
               SUM(true_shooting_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) ts,
               SUM(usage_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) usg,
               SUM(assist_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) ast_pct,
               SUM(defensive_rebound_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) dreb_pct
        FROM nba_player_advanced_stats
        WHERE game_id IN (SELECT DISTINCT game_id FROM nba_player_stats
                          WHERE season_year IN %s)
        GROUP BY person_id""", (ss,))
    df = box.merge(adv, on="player_id", how="left")
    m = df["min"].clip(lower=1)
    per36 = lambda c: df[c] / m * 36.0
    feat = pd.DataFrame({"player_id": df["player_id"]})
    feat["pts36"], feat["ast36"], feat["tov36"] = per36("pts"), per36("ast"), per36("tov")
    feat["oreb36"], feat["dreb36"] = per36("oreb"), per36("dreb")
    feat["stl36"], feat["blk36"], feat["pf36"] = per36("stl"), per36("blk"), per36("pf")
    feat["fg3a_rate"] = df["fg3a"] / df["fga"].clip(lower=1)
    feat["ts"] = df["ts"].fillna(df["ts"].median())
    feat["usg"] = df["usg"].fillna(df["usg"].median())
    feat["ast_pct"] = df["ast_pct"].fillna(df["ast_pct"].median())
    feat["dreb_pct"] = df["dreb_pct"].fillna(df["dreb_pct"].median())
    return feat.fillna(0.0)


OFF_FEATS = ["pts36", "ast36", "tov36", "oreb36", "ts", "usg", "ast_pct", "fg3a_rate"]
DEF_FEATS = ["stl36", "blk36", "dreb36", "pf36", "dreb_pct"]


def fit_box_prior(player_ids, first_off, first_def, poss_weight, feats):
    """Regress first-pass RAPM on box features (weighted by possessions) to learn
    the prior mean for each player. Predicted = the in-house box BPM."""
    fp = pd.DataFrame({"player_id": player_ids, "off": first_off, "def": first_def, "w": poss_weight})
    d = fp.merge(feats, on="player_id", how="left").fillna(feats.median(numeric_only=True))
    Xo, Xd = d[OFF_FEATS].to_numpy(), d[DEF_FEATS].to_numpy()
    ro = Ridge(alpha=50.0).fit(Xo, d["off"], sample_weight=d["w"])
    rd = Ridge(alpha=50.0).fit(Xd, d["def"], sample_weight=d["w"])
    prior_off = ro.predict(Xo)
    prior_def = rd.predict(Xd)
    return prior_off, prior_def


def fit_rapm(seasons=None, box_feats=None):
    """Core box-informed RAPM fit, returning the per-player table (off/def/net RAPM,
    analytic SDs, learned box prior, possessions). seasons=None is the canonical full
    window (2023-24..2025-26): fit_rapm(None) is the SAME computation that produced
    player_value.csv's RAPM columns (behavior-preserving, verified by the refactor diff
    gate). A subset such as (2023, 2024) fits a windowed RAPM for held-out validation,
    using the same estimator with per-season recency weights subset to the window.
    box_feats optionally injects a FROZEN box-feature table (the output of box_features
    for the same window) so a multi-step build pins ONE warehouse snapshot and a later
    warehouse update cannot open a seam mid-build; box_feats=None reads the warehouse
    live (behavior-preserving). The table is RETURNED only; nothing is written (main()
    owns the canonical write, and the coverage validation must never overwrite the
    enriched player_value.csv)."""
    df = load_possessions(seasons)
    X, y, w, players, R = build_matrix(df)
    print("fitting first-pass ridge (CV alpha) ...", flush=True)
    cv = RidgeCV(alphas=ALPHAS).fit(X, y, sample_weight=w)
    alpha = float(cv.alpha_)
    print(f"  selected alpha={alpha}", flush=True)
    first = cv.coef_
    first_off, first_def = first[:R + 1], first[R + 1:]

    # possession counts per qualifying player (for prior weighting)
    counts = np.asarray((X[:, :R] > 0).sum(axis=0)).ravel() + np.asarray((X[:, R + 1:2 * R + 1] > 0).sum(axis=0)).ravel()
    feats = box_features(seasons) if box_feats is None else box_feats.copy()
    print("learning box-score prior ...", flush=True)
    prior_off_p, prior_def_p = fit_box_prior(players, first_off[:R], first_def[:R], counts, feats)

    # prior vector aligned to all columns (replacement prior = 0)
    prior_vec = np.concatenate([prior_off_p, [0.0], prior_def_p, [0.0]]).astype(np.float64)
    offset = X @ prior_vec
    print("fitting 2-stage ridge (shrink toward prior) ...", flush=True)
    r2 = Ridge(alpha=alpha, fit_intercept=True).fit(X, y - offset, sample_weight=w)
    beta = prior_vec + r2.coef_
    off_rapm, def_rapm = beta[:R + 1], beta[R + 1:]

    # analytical ridge posterior SD: sigma^2 * diag((X'X + alpha I)^-1)
    print("computing analytical intervals ...", flush=True)
    XtX = (X.T @ X).toarray().astype(np.float64)
    G = XtX + alpha * np.eye(XtX.shape[0])
    invG = np.linalg.inv(G)
    resid = (y - offset) - r2.predict(X)
    dof = max(1, len(y) - np.linalg.matrix_rank(np.eye(1)))  # large-n: ~ n
    sigma2 = float(np.average(resid ** 2, weights=w)) * len(y) / (len(y) - X.shape[1])
    sd = np.sqrt(sigma2 * np.clip(np.diag(invG), 0, None))
    off_sd, def_sd = sd[:R + 1], sd[R + 1:]

    # names + playoff read
    names = db.query("""SELECT DISTINCT ON (player_id) player_id, player_name
                        FROM nba_player_stats WHERE player_id = ANY(%s)
                        ORDER BY player_id, game_date DESC""", (players,))
    name_map = dict(zip(names["player_id"], names["player_name"]))
    pri = {p: (po, pd_) for p, po, pd_ in zip(players, prior_off_p, prior_def_p)}

    rows = []
    for i, p in enumerate(players):
        bo, bd = pri[p]
        rows.append({
            "player_id": p, "player_name": name_map.get(p, str(p)),
            "possessions": int(counts[i]),
            "off_rapm": round(float(off_rapm[i]), 2), "off_sd": round(float(off_sd[i]), 2),
            "def_rapm": round(float(def_rapm[i]), 2), "def_sd": round(float(def_sd[i]), 2),
            "net_rapm": round(float(off_rapm[i] - def_rapm[i]), 2),
            "net_sd": round(float(np.hypot(off_sd[i], def_sd[i])), 2),
            "box_off_prior": round(float(bo), 2), "box_def_prior": round(float(bd), 2),
            "box_net_bpm": round(float(bo - bd), 2),
            "reliable": "TRUE" if int(counts[i]) >= RELIABLE_POSS else "FALSE",
        })
    return pd.DataFrame(rows)


def main():
    global CACHE, POINTS_COL, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=None, help="possession cache directory to fit on")
    ap.add_argument("--points-col", default="points_scored",
                    help="points_scored (corrected) or points_scored_legacy (pre-D89)")
    ap.add_argument("--out", default=None, help="output csv path")
    args = ap.parse_args()
    if args.cache:
        CACHE = (args.cache if os.path.isabs(args.cache)
                 else os.path.join(HERE, "..", "data", "cache", args.cache))
    POINTS_COL = args.points_col
    if args.out:
        OUT = args.out if os.path.isabs(args.out) else os.path.join(DATA, args.out)
    print("cache=%s" % CACHE, flush=True)
    print("points column=%s" % POINTS_COL, flush=True)
    print("out=%s" % OUT, flush=True)

    val = fit_rapm()

    # merge playoff translation (canonical full-window output only)
    pt_path = os.path.join(DATA, "playoff_translation.csv")
    if os.path.exists(pt_path):
        pt = pd.read_csv(pt_path)[["player_id", "translation_read", "rs_to_po_delta", "hc_poss_po"]]
        val = val.merge(pt, on="player_id", how="left")

    val = val.sort_values("net_rapm", ascending=False).reset_index(drop=True)
    val.to_csv(OUT, index=False)

    def safe(s): return str(s).encode("ascii", "replace").decode()
    print(f"\nWrote {len(val)} players -> {OUT}")
    corr = np.corrcoef(val["net_rapm"], val["box_net_bpm"])[0, 1]
    print(f"corr(net_rapm, box_net_bpm) = {corr:.3f}  (triangulation sanity)")
    print("\nTop 15 net RAPM (validation: should be stars):")
    for _, r in val.head(15).iterrows():
        print(f"  {safe(r['player_name']):24} net={r['net_rapm']:+.2f} +/-{r['net_sd']:.2f} "
              f"(off {r['off_rapm']:+.2f}, def {r['def_rapm']:+.2f}) poss={r['possessions']:,}")
    print("\nBottom 5 net RAPM:")
    for _, r in val.tail(5).iterrows():
        print(f"  {safe(r['player_name']):24} net={r['net_rapm']:+.2f}")


if __name__ == "__main__":
    main()
