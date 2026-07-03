"""F2 Layer 1a: per-season O/D ridge RAPM (plan D4, spec 8.2).

Per season s (end-year convention, 2014 = 2013-14):

  observations   directional matchup rows from the D6 stints table: the two
                 per-team rows of each physical stint pair on their shared
                 clock window, aggregated per (off five, def five). Target
                 is points per 100 possessions, possession-weighted.
                 Garbage-time stints are excluded (the F1 tagger flag, not
                 the seed script's margin approximation).
  design         one +1 column per qualifying offense player, one per
                 qualifying defense player; sub-threshold players pool into
                 a replacement column per side (prior 0). Sign convention
                 matches offseason/scripts/build_rapm.py: def_rapm is
                 points ALLOWED per 100 (lower is better), net = off - def.
  prior          two-stage, per spec 8.2: first-pass ridge -> learn a box
                 composite prior (in-house BPM, the seed script's method,
                 windowed to season s); blend with the player's season s-1
                 estimate aged one year via the pinned Model C curves
                 (config layer1a.prior_blend, currently 0.6 aged-prev /
                 0.4 box, dev-tunable pre-freeze). No s-1 estimate -> box
                 prior alone. Second stage shrinks toward the blend via the
                 offset trick (fit on y - X@prior, add back).
  alpha          ONE ridge alpha for all seasons and both stages, selected
                 by GCV (sklearn RidgeCV efficient LOO) on DEV SEASONS ONLY
                 (2016..2021 end-years) and frozen to
                 outputs/rapm/alpha_freeze.json. Reruns refuse to reselect
                 while the freeze file exists (house rule: no retunes).
  uncertainty    game-level block bootstrap, 200 resamples (config), refit
                 second stage per resample with the prior held fixed
                 (conditional-on-prior SEs; the prior's own uncertainty
                 enters Layer 1b through the covariance parquets and the
                 aging posterior, not here).
  A1 covariance  per-season parquet of bootstrap covariance for player
                 pairs sharing >= 500 possessions on the same side
                 (config layer1a.covariance_block_min_shared_poss).

G2 exports for the morning read (never fitted-to): YoY O/D correlations
per adjacent season pair with the 0.50-0.75 band marked, and top-20 net
RAPM tables per season.

Seasons fit chronologically so season s can consume s-1's estimates.

Usage: python -m src.models.rapm            # full 2014..2026 build
       python -m src.models.rapm 2016 2021  # subrange (dev iteration)
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import yaml
from scipy.sparse import csr_matrix, hstack

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.adapters.pinned_artifacts import load_pinned_path  # noqa: E402
from src.adapters.postmortem_lib import query  # noqa: E402

DB_PATH = FITENGINE_ROOT / "data" / "fitengine.duckdb"
OUT_DIR = FITENGINE_ROOT / "outputs" / "rapm"
ALPHA_FREEZE = OUT_DIR / "alpha_freeze.json"

CFG = yaml.safe_load((FITENGINE_ROOT / "config" / "model_params.yaml").read_text())
L1A = CFG["layer1a"]
SEED = int(CFG["seed"])
SEASONS_ALL = list(CFG["panel"]["seasons"])
DEV_SEASONS_GCV = [2016, 2017, 2018, 2019, 2020, 2021]  # 2015-16..2020-21
ALPHA_GRID = [250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0]
MIN_POSS_OWN = 500          # own column at >= this many season possessions
FACE_LIST_MIN_POSS = 2000   # rotation-level floor for the top-20 exports

# ---------------------------------------------------------------------------
# Model C aging (pinned posterior; basis reimplemented 1:1 from
# pick2033/src/models/aging.py and cross-checked by tests/test_rapm_units.py)

KNOTS = np.array([21.0, 24.0, 27.0, 30.0, 33.0, 36.0])


def natural_cubic_basis(age: np.ndarray, knots: np.ndarray = KNOTS) -> np.ndarray:
    K = len(knots)

    def d(k, x):
        num = np.maximum(x - knots[k], 0) ** 3 - np.maximum(x - knots[K - 1], 0) ** 3
        return num / (knots[K - 1] - knots[k])

    cols = [age - knots.mean()]
    for k in range(K - 2):
        cols.append(d(k, age) - d(K - 2, age))
    return np.column_stack(cols)


class AgingCurves:
    """Expected one-year impact delta by archetype and (next-season) age,
    posterior mean and variance over the 4,000 pinned draws."""

    def __init__(self) -> None:
        self.flat = pd.read_parquet(load_pinned_path("model_c_aging_posterior"))

    def delta(self, arch: str, age: float) -> tuple[float, float]:
        X = natural_cubic_basis(np.array([float(age)]))
        betas = np.column_stack(
            [self.flat[f"beta_{arch}_{b}"].values for b in range(X.shape[1])])
        draws = self.flat[f"intercept_{arch}"].values + (betas @ X.T).ravel()
        return float(draws.mean()), float(draws.var())


def archetype(position: str | None) -> str:
    """pick2033 aging.py convention: PG/SG guard, PF/C big, else wing."""
    p = (position or "").lower()
    if "center" in p:
        return "big"
    if p == "guard":
        return "guard"
    return "wing"


# ---------------------------------------------------------------------------
# Data assembly

def season_str(end_year: int) -> str:
    return f"{end_year - 1}-{str(end_year)[-4:][-2:]}"


def season_yy(end_year: int) -> str:
    return f"{end_year - 2001:02d}"


def load_matchups(con: duckdb.DuckDBPyConnection, end_year: int) -> pd.DataFrame:
    """Pair the two directional rows of each stint on their clock window and
    aggregate to (off five, def five) matchup rows for the season."""
    df = con.execute("""
        WITH season_stints AS (
            SELECT s.* FROM stints s
            JOIN games g USING (game_id)
            WHERE g.include_train AND g.season_yy = ? AND NOT s.in_garbage_time
        )
        SELECT a.game_id,
               a.lineup_id  AS off_lineup,
               b.lineup_id  AS def_lineup,
               SUM(a.possessions_off) AS poss,
               SUM(a.points_for)      AS pts
        FROM season_stints a
        JOIN season_stints b
          ON a.game_id = b.game_id
         AND a.period_start = b.period_start
         AND a.clock_start_sec = b.clock_start_sec
         AND a.period_end = b.period_end
         AND a.clock_end_sec = b.clock_end_sec
         AND a.team_id <> b.team_id
        WHERE a.possessions_off > 0
        GROUP BY 1, 2, 3
    """, [season_yy(end_year)]).fetchdf()
    # pairing sanity: every offensive row must have found exactly one mirror
    n_dir = con.execute("""
        SELECT count(*) FROM stints s JOIN games g USING (game_id)
        WHERE g.include_train AND g.season_yy = ? AND NOT s.in_garbage_time
          AND s.possessions_off > 0
    """, [season_yy(end_year)]).fetchone()[0]
    n_paired = con.execute("""
        WITH season_stints AS (
            SELECT s.* FROM stints s JOIN games g USING (game_id)
            WHERE g.include_train AND g.season_yy = ? AND NOT s.in_garbage_time
        )
        SELECT count(*) FROM season_stints a JOIN season_stints b
          ON a.game_id = b.game_id AND a.period_start = b.period_start
         AND a.clock_start_sec = b.clock_start_sec
         AND a.period_end = b.period_end AND a.clock_end_sec = b.clock_end_sec
         AND a.team_id <> b.team_id
        WHERE a.possessions_off > 0
    """, [season_yy(end_year)]).fetchone()[0]
    if n_dir != n_paired:
        raise RuntimeError(
            f"stint pairing mismatch season {end_year}: {n_dir} directional "
            f"rows, {n_paired} paired -- window join is not 1:1")
    return df


def build_design(df: pd.DataFrame):
    off_lists = [tuple(int(p) for p in s.split(",")) for s in df.off_lineup]
    def_lists = [tuple(int(p) for p in s.split(",")) for s in df.def_lineup]
    poss = df.poss.to_numpy(np.float64)

    cnt: dict[int, float] = {}
    for lst, w in zip(off_lists, poss):
        for p in lst:
            cnt[p] = cnt.get(p, 0.0) + w
    for lst, w in zip(def_lists, poss):
        for p in lst:
            cnt[p] = cnt.get(p, 0.0) + w
    players = sorted(p for p, c in cnt.items() if c >= MIN_POSS_OWN)
    col = {p: i for i, p in enumerate(players)}
    R = len(players)  # replacement column index per side

    n = len(df)
    ro, co = [], []
    rd, cd = [], []
    for i, lst in enumerate(off_lists):
        for p in lst:
            ro.append(i); co.append(col.get(p, R))
    for i, lst in enumerate(def_lists):
        for p in lst:
            rd.append(i); cd.append(col.get(p, R))
    X_off = csr_matrix((np.ones(len(ro), np.float64), (ro, co)), shape=(n, R + 1))
    X_def = csr_matrix((np.ones(len(rd), np.float64), (rd, cd)), shape=(n, R + 1))
    X = hstack([X_off, X_def]).tocsr()
    y = (df.pts.to_numpy(np.float64) / poss) * 100.0
    games = df.game_id.to_numpy()
    poss_by_player = {p: cnt[p] for p in players}
    return X, y, poss, games, players, R, poss_by_player


def ridge_solve(X, y, w, alpha: float, offset: np.ndarray | None = None):
    """Weighted ridge with intercept via centering; returns (coef, intercept)."""
    yy = y - (offset if offset is not None else 0.0)
    sw = w / w.sum()
    Xw = X.multiply(sw[:, None]).tocsr()
    x_mean = np.asarray(Xw.sum(axis=0)).ravel()
    y_mean = float(yy @ sw)
    G = (X.multiply(w[:, None]).T @ X).toarray()
    G -= w.sum() * np.outer(x_mean, x_mean)
    G[np.diag_indices_from(G)] += alpha
    b = np.asarray(X.multiply(w[:, None]).T @ yy).ravel() - w.sum() * x_mean * y_mean
    coef = np.linalg.solve(G, b)
    intercept = y_mean - float(x_mean @ coef)
    return coef, intercept


# ---------------------------------------------------------------------------
# Box composite prior (seed-script method, windowed to one season)

OFF_FEATS = ["pts36", "ast36", "tov36", "oreb36", "ts", "usg", "ast_pct", "fg3a_rate"]
DEF_FEATS = ["stl36", "blk36", "dreb36", "pf36", "dreb_pct"]


def box_features(end_year: int) -> pd.DataFrame:
    ss = season_str(end_year)
    box = query("""
        SELECT player_id, SUM(minutes_played) min, SUM(pts) pts, SUM(ast) ast,
               SUM(tov) tov, SUM(oreb) oreb, SUM(dreb) dreb, SUM(stl) stl,
               SUM(blk) blk, SUM(pf) pf, SUM(fg3a) fg3a, SUM(fga) fga
        FROM nba_player_stats
        WHERE season_year = %s
        GROUP BY player_id HAVING SUM(minutes_played) > 0""", (ss,))
    adv = query("""
        SELECT person_id AS player_id,
               SUM(true_shooting_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) ts,
               SUM(usage_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) usg,
               SUM(assist_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) ast_pct,
               SUM(defensive_rebound_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) dreb_pct
        FROM nba_player_advanced_stats
        WHERE game_id IN (SELECT DISTINCT game_id FROM nba_player_stats
                          WHERE season_year = %s)
        GROUP BY person_id""", (ss,))
    df = box.merge(adv, on="player_id", how="left")
    m = df["min"].clip(lower=1)
    feat = pd.DataFrame({"player_id": df["player_id"]})
    for c, src in [("pts36", "pts"), ("ast36", "ast"), ("tov36", "tov"),
                   ("oreb36", "oreb"), ("dreb36", "dreb"), ("stl36", "stl"),
                   ("blk36", "blk"), ("pf36", "pf")]:
        feat[c] = df[src] / m * 36.0
    feat["fg3a_rate"] = df["fg3a"] / df["fga"].clip(lower=1)
    for c in ["ts", "usg", "ast_pct", "dreb_pct"]:
        feat[c] = df[c].fillna(df[c].median())
    return feat.fillna(0.0)


def fit_box_prior(players, first_off, first_def, poss_w, feats):
    from sklearn.linear_model import Ridge
    fp = pd.DataFrame({"player_id": players, "off": first_off,
                       "def": first_def, "w": poss_w})
    d = fp.merge(feats, on="player_id", how="left")
    d[OFF_FEATS + DEF_FEATS] = d[OFF_FEATS + DEF_FEATS].fillna(
        feats[OFF_FEATS + DEF_FEATS].median(numeric_only=True))
    ro = Ridge(alpha=50.0).fit(d[OFF_FEATS], d["off"], sample_weight=d["w"])
    rd = Ridge(alpha=50.0).fit(d[DEF_FEATS], d["def"], sample_weight=d["w"])
    return ro.predict(d[OFF_FEATS]), rd.predict(d[DEF_FEATS])


# ---------------------------------------------------------------------------
# Alpha freeze (GCV on dev seasons only)

def select_alpha(con) -> float:
    if ALPHA_FREEZE.exists():
        frozen = json.loads(ALPHA_FREEZE.read_text())
        print(f"alpha already FROZEN at {frozen['alpha']} "
              f"({frozen['frozen_at']}); refusing to reselect")
        return float(frozen["alpha"])
    from sklearn.linear_model import RidgeCV
    per_season = {}
    total = None
    for s in DEV_SEASONS_GCV:
        df = load_matchups(con, s)
        X, y, w, games, players, R, _ = build_design(df)
        cv = RidgeCV(alphas=ALPHA_GRID, store_cv_results=True).fit(
            X.toarray(), y, sample_weight=w)
        errs = np.average(cv.cv_results_, axis=0, weights=w)
        per_season[s] = dict(zip(map(float, ALPHA_GRID), map(float, errs)))
        total = errs if total is None else total + errs
        print(f"  GCV {s}: best alpha {float(cv.alpha_)}")
    alpha = float(ALPHA_GRID[int(np.argmin(total))])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ALPHA_FREEZE.write_text(json.dumps({
        "alpha": alpha, "grid": ALPHA_GRID,
        "dev_seasons": DEV_SEASONS_GCV, "per_season_gcv": per_season,
        "frozen_at": pd.Timestamp.now().isoformat(), "seed": SEED,
    }, indent=1))
    print(f"alpha FROZEN at {alpha} (summed GCV over dev seasons)")
    return alpha


# ---------------------------------------------------------------------------
# Season fit

def fit_season(con, end_year: int, alpha: float, prev: pd.DataFrame | None,
               curves: AgingCurves, bio: pd.DataFrame,
               rng: np.random.Generator):
    df = load_matchups(con, end_year)
    X, y, w, games, players, R, poss_by_player = build_design(df)
    n_cols = X.shape[1]
    print(f"[{season_str(end_year)}] {len(df):,} matchup rows, "
          f"{len(players)} qualifying players")

    first_coef, _ = ridge_solve(X, y, w, alpha)
    first_off, first_def = first_coef[:R], first_coef[R + 1:2 * R + 1]

    feats = box_features(end_year)
    counts = np.array([poss_by_player[p] for p in players])
    box_off, box_def = fit_box_prior(players, first_off, first_def, counts, feats)

    b = bio[bio.end_year == end_year].set_index("player_id")
    w_prev = float(L1A["prior_blend"]["prev_season_aged"])
    w_box = float(L1A["prior_blend"]["box_composite"])
    prev_map = ({} if prev is None else
                prev.set_index("player_id")[["off_rapm", "def_rapm"]].to_dict("index"))

    prior_off = np.array(box_off, dtype=np.float64)
    prior_def = np.array(box_def, dtype=np.float64)
    n_blended = 0
    for i, p in enumerate(players):
        pr = prev_map.get(p)
        if pr is None:
            continue
        age = float(b.loc[p, "age"]) if p in b.index and pd.notna(b.loc[p, "age"]) else 27.0
        arch = archetype(b.loc[p, "position"] if p in b.index else None)
        d_mean, _ = curves.delta(arch, age)
        # Model C deltas are NET impact points; split evenly across O/D
        # (the curve was fit on net BPM change; no O/D split exists in it)
        aged_off = pr["off_rapm"] + d_mean / 2.0
        aged_def = pr["def_rapm"] - d_mean / 2.0
        prior_off[i] = w_prev * aged_off + w_box * box_off[i]
        prior_def[i] = w_prev * aged_def + w_box * box_def[i]
        n_blended += 1
    print(f"  prior: {n_blended} blended with aged s-1, "
          f"{len(players) - n_blended} box-only")

    prior_vec = np.concatenate([prior_off, [0.0], prior_def, [0.0]])
    offset = X @ prior_vec
    coef, intercept = ridge_solve(X, y, w, alpha, offset=offset)
    beta = prior_vec + coef
    off_rapm, def_rapm = beta[:R], beta[R + 1:2 * R + 1]

    # --- game-block bootstrap (prior held fixed; see module docstring) ---
    n_boot = int(L1A["bootstrap_resamples"])
    uniq_games = np.unique(games)
    game_idx = {g: i for i, g in enumerate(uniq_games)}
    row_game = np.array([game_idx[g] for g in games])
    draws = np.empty((n_boot, n_cols))
    for bidx in range(n_boot):
        mult = np.bincount(rng.integers(0, len(uniq_games), len(uniq_games)),
                           minlength=len(uniq_games)).astype(np.float64)
        wb = w * mult[row_game]
        if wb.sum() == 0:
            wb = w.copy()
        cb, _ = ridge_solve(X, y, wb, alpha, offset=offset)
        draws[bidx] = prior_vec + cb
    off_se = draws[:, :R].std(axis=0, ddof=1)
    def_se = draws[:, R + 1:2 * R + 1].std(axis=0, ddof=1)

    # --- A1 covariance blocks (>= threshold shared possessions) ---
    thresh = float(L1A["covariance_block_min_shared_poss"])
    shared: dict[tuple[int, int, str], float] = {}
    off_lists = [tuple(int(p) for p in s.split(",")) for s in df.off_lineup]
    def_lists = [tuple(int(p) for p in s.split(",")) for s in df.def_lineup]
    poss_arr = df.poss.to_numpy(np.float64)
    qual = set(players)
    for lists, side in ((off_lists, "off"), (def_lists, "def")):
        for lst, pw in zip(lists, poss_arr):
            q = sorted(p for p in lst if p in qual)
            for a_, b_ in combinations(q, 2):
                k = (a_, b_, side)
                shared[k] = shared.get(k, 0.0) + pw
    col_of = {p: i for i, p in enumerate(players)}
    cov_rows = []
    for (a_, b_, side), sp in shared.items():
        if sp < thresh:
            continue
        ia = col_of[a_] + (0 if side == "off" else R + 1)
        ib = col_of[b_] + (0 if side == "off" else R + 1)
        c = float(np.cov(draws[:, ia], draws[:, ib], ddof=1)[0, 1])
        cov_rows.append({"player_i": a_, "player_j": b_, "side": side,
                         "shared_poss": sp, "cov": c})

    names = query("""SELECT DISTINCT ON (player_id) player_id, player_name
                     FROM nba_player_stats WHERE player_id = ANY(%s)
                     ORDER BY player_id, game_date DESC""", (players,))
    name_map = dict(zip(names.player_id, names.player_name))
    out = pd.DataFrame({
        "player_id": players,
        "player_name": [name_map.get(p, str(p)) for p in players],
        "season": season_str(end_year), "end_year": end_year,
        "possessions": counts,
        "off_rapm": off_rapm, "off_se": off_se,
        "def_rapm": def_rapm, "def_se": def_se,
        "net_rapm": off_rapm - def_rapm,
        "net_se": np.hypot(off_se, def_se),
        "prior_off": prior_off, "prior_def": prior_def,
        "box_off": box_off, "box_def": box_def,
        "blended_prev": [p in prev_map for p in players],
        "intercept": intercept,
    })
    return out, pd.DataFrame(cov_rows)


# ---------------------------------------------------------------------------

def g2_report(all_seasons: dict[int, pd.DataFrame]) -> str:
    lines = ["# G2 RAPM rows (generated; face lists are narrative checks, "
             "never fitted-to)", ""]
    lines.append("## Year-over-year stability (own-column players in both "
                 "seasons; gate band 0.50-0.75)")
    lines.append("")
    lines.append("| pair | n | O-RAPM r | D-RAPM r | net r | in band |")
    lines.append("|---|---|---|---|---|---|")
    years = sorted(all_seasons)
    for a, b in zip(years, years[1:]):
        m = all_seasons[a].merge(all_seasons[b], on="player_id",
                                 suffixes=("_a", "_b"))
        if len(m) < 30:
            continue
        ro = float(np.corrcoef(m.off_rapm_a, m.off_rapm_b)[0, 1])
        rd = float(np.corrcoef(m.def_rapm_a, m.def_rapm_b)[0, 1])
        rn = float(np.corrcoef(m.net_rapm_a, m.net_rapm_b)[0, 1])
        ok = "YES" if (0.50 <= ro <= 0.75 and 0.50 <= rd <= 0.75) else "NO"
        lines.append(f"| {season_str(a)} -> {season_str(b)} | {len(m)} "
                     f"| {ro:.3f} | {rd:.3f} | {rn:.3f} | {ok} |")
    lines.append("")
    for yr in years:
        t = all_seasons[yr]
        top = (t[t.possessions >= FACE_LIST_MIN_POSS]
               .sort_values("net_rapm", ascending=False).head(20))
        lines.append(f"## Top 20 net RAPM, {season_str(yr)} "
                     f"(>= {FACE_LIST_MIN_POSS} poss)")
        lines.append("")
        lines.append("| player | net | off | def | poss |")
        lines.append("|---|---|---|---|---|")
        for _, r in top.iterrows():
            lines.append(f"| {r.player_name} | {r.net_rapm:+.2f} "
                         f"| {r.off_rapm:+.2f} | {r.def_rapm:+.2f} "
                         f"| {int(r.possessions):,} |")
        lines.append("")
    return "\n".join(lines)


def load_bio(seasons: list[int]) -> pd.DataFrame:
    rows = []
    for yr in seasons:
        b = query("""
            SELECT sb.player_id, sb.age, pb.position
            FROM nba_player_season_bio sb
            LEFT JOIN nba_player_bio pb USING (player_id)
            WHERE sb.season_year = %s AND sb.season_type = 'Regular Season'
        """, (season_str(yr),))
        b = b.drop_duplicates("player_id")
        b["end_year"] = yr
        rows.append(b)
    return pd.concat(rows, ignore_index=True)


def main() -> None:
    seasons = SEASONS_ALL
    if len(sys.argv) >= 3:
        lo, hi = int(sys.argv[1]), int(sys.argv[2])
        seasons = [s for s in SEASONS_ALL if lo <= s <= hi]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rng = np.random.default_rng(SEED)

    alpha = select_alpha(con)
    curves = AgingCurves()
    bio = load_bio(seasons)

    all_seasons: dict[int, pd.DataFrame] = {}
    prev: pd.DataFrame | None = None
    for yr in sorted(seasons):
        out, cov = fit_season(con, yr, alpha, prev, curves, bio, rng)
        out.to_parquet(OUT_DIR / f"rapm_{yr}.parquet", index=False)
        cov.to_parquet(OUT_DIR / f"cov_{yr}.parquet", index=False)
        all_seasons[yr] = out
        prev = out
        print(f"  wrote rapm_{yr}.parquet ({len(out)} players), "
              f"cov_{yr}.parquet ({len(cov)} pair blocks)")

    report = g2_report(all_seasons)
    (OUT_DIR / "g2_rapm_report.md").write_text(report, encoding="utf-8")
    print(f"\nG2 report -> {OUT_DIR / 'g2_rapm_report.md'}")
    con.close()


if __name__ == "__main__":
    main()
