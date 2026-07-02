"""Engine D: two-tier league simulation, 2027-2033 (spec 7.5, amended by the
2026 lottery reform and the ratified 8.4 operationalization).

Tier 1 (MIN, CHA): roster-informed strength -- minutes-weighted BPM rollup
calibrated to SRS, aging via Model C posterior curves, star departures via
Model B (PROVISIONAL) hazard draws, blended with the Model A franchise prior
per the w(t) schedule. Tier 2 (other 28): pure Model A dynamics.

Season loop per simulated year:
  strengths -> expected wins (+ season noise, renormalized to 1230)
  -> conference standings -> play-in (seeds 7-10; single-game probit on SRS
  gap + 2.6 home edge for the higher seed, sd 13.4 -- documented approx)
  -> 3-2-1 lottery (16 teams, ball counts by play-in role, worst-3 relegated
  + top-12 floor, no-repeat-#1, no-top-5-three-straight tracked ACROSS
  years per path) -> full pick order 1-30 (17-30 = ball-less playoff teams,
  inverse record).

Star handling (v1, documented): hazard applies to listed star players on
the two detail teams (Edwards; LaMelo entering a MIN spell). Charlotte
post-trade carries no active star spell -- its trajectory is prior-driven.
Departure shock: remove the player's minutes-weighted BPM contribution from
the roster AND shift the franchise-prior state by the historical mean
post-star-exit SRS innovation (estimated from star_spells x franchise_seasons
at build time, reported in the run manifest).

All outputs tagged PROVISIONAL while Model B is provisional and trade terms
await July-6 verification.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(REPO_ROOT / "offseason" / "scripts"))

from src.models.aging import archetype_of, curve_from_posterior  # noqa: E402
from src.models.hazard import COVARS, predict_hazard  # noqa: E402
from src.models.trajectory import fit as fit_trajectory  # noqa: E402
from src.models.trajectory import load_panel  # noqa: E402
from src.sim.lottery import (  # noqa: E402
    BALLS_78_LOSER, BALLS_LOTTERY, BALLS_NINE_TEN, BALLS_RELEGATED,
    reformed_lottery,
)
from src.sim.strength_blend import load_srs_to_wins  # noqa: E402

# static current conference map (matches offseason build_series_calibration
# TEAM_CONF; defined locally to avoid importing its statsmodels dependency).
# No realignment modeled through 2033 (documented assumption).
TEAM_CONF = {t: "E" for t in ("ATL BOS BKN CHA CHI CLE DET IND MIA MIL "
                              "NYK ORL PHI TOR WAS").split()}
TEAM_CONF.update({t: "W" for t in ("DAL DEN GSW HOU LAC LAL MEM MIN NOP OKC "
                                   "PHX POR SAC SAS UTA").split()})

DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"
STAGED = PROJECT_ROOT / "data" / "staged"
POSTERIORS = PROJECT_ROOT / "outputs" / "posteriors"
SIMS = PROJECT_ROOT / "outputs" / "sims"

SEASONS = list(range(2027, 2034))
GAME_SD, HOME_EDGE = 13.4, 2.6
ROTATION_MIN = np.array([34, 32, 30, 28, 26, 20, 16, 12, 8, 6], dtype=float)
REPLACEMENT_BPM = -2.0

# star players subject to Model B hazard on the detail teams (v1 list).
# contract_path: season -> years remaining on the deal being played under.
# Edwards is verified 2/1/0 with the 2029 walk year. LaMelo has the SAME
# 2029 walk year on his current deal, and is extension-eligible July 6
# (2yr/$119.2M): 'unsigned' keeps 2/1/0, 'extended' runs 4/3/2/1/0 through
# 2031. July-6 directive: set per the news that morning; if unresolved,
# run BOTH (pre-declared sensitivity), never pick silently.
# post_walk_reset: if a star survives his walk year (no departure drawn),
# he re-signs and the clock resets to this value, decrementing thereafter
# (documented assumption, tornado-tested via the hazard-scale arm).
STARS = {
    "MIN": [
        {"player": "Anthony Edwards", "age_2026": 24, "tenure_2026": 6,
         "all_nba_count": 2, "spell_market_tier": 2,
         "contract_path": {2027: 2, 2028: 1, 2029: 0}, "post_walk_reset": 4},
        {"player": "LaMelo Ball", "age_2026": 24, "tenure_2026": 0,
         "all_nba_count": 0, "spell_market_tier": 2,
         "contract_path": {2027: 2, 2028: 1, 2029: 0}, "post_walk_reset": 4,
         "contract_path_extended": {2027: 4, 2028: 3, 2029: 2, 2030: 1, 2031: 0}},
    ],
    "CHA": [],
}


def contract_years_for(star: dict, season: int, scenario: str = "unsigned") -> int:
    path = (star.get("contract_path_extended")
            if scenario == "extended" and "contract_path_extended" in star
            else star["contract_path"])
    if season in path:
        return path[season]
    walk = max(path)
    k = season - walk - 1
    return max(star["post_walk_reset"] - k, 0)


def load_config():
    return yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())


def load_rosters() -> dict[str, pd.DataFrame]:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("""
        SELECT team, player, position, age, bbr_bpm, bbr_mp, consensus_net, net_rapm
        FROM rosters_current WHERE roster_state = 'post_trade'
    """).fetchdf()
    con.close()
    out = {}
    for team in ("MIN", "CHA"):
        t = df[df.team == team].copy()
        raw = t.bbr_bpm.fillna(t.consensus_net).fillna(t.net_rapm).fillna(REPLACEMENT_BPM)
        # reliability shrinkage toward a bench prior: selecting a rotation by
        # MEASURED value loads on noise (a 6.3 low-minutes artifact once made
        # Diabate CHA's best player); w = mp/(mp+1500)
        mp = t.bbr_mp.fillna(0.0)
        w = mp / (mp + 1500.0)
        t["bpm"] = w * raw + (1 - w) * (-1.0)
        t["archetype"] = t.position.map(archetype_of)
        t = t.sort_values("bpm", ascending=False).head(10).reset_index(drop=True)
        t["minutes"] = ROTATION_MIN[: len(t)]
        out[team] = t[["player", "age", "bpm", "archetype", "minutes"]]
    return out


def rotation_aggregate(bpm_ranked: np.ndarray) -> np.ndarray:
    """The SINGLE aggregate construction used on BOTH the historical
    calibration side and the sim side (a construction mismatch here once
    inflated MIN/CHA 2027 strengths to 57-77% sixty-win rates): top-10
    players in rank order at ROTATION_MIN weights, remaining minutes of the
    240 filled at replacement level.

    bpm_ranked: (..., 10) BPM values in rotation-rank order."""
    bench_min = 240.0 - ROTATION_MIN.sum()
    num = (bpm_ranked * ROTATION_MIN).sum(-1) + bench_min * REPLACEMENT_BPM
    return 5 * num / 240.0


def fit_roster_to_srs() -> dict:
    """Calibrate the rotation_aggregate -> SRS on 1985+ history, with the
    historical top-10 chosen BY MINUTES (the realized rotation order; the
    sim ranks its projected roster by BPM as the rotation proxy)."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    ps = con.execute("""
        SELECT franchise_id, season, mp, bpm FROM player_impact_seasons
        WHERE NOT is_combined AND franchise_id IS NOT NULL AND season >= 1985
          AND mp IS NOT NULL AND bpm IS NOT NULL
    """).fetchdf()
    fs = con.execute("SELECT franchise_id, season, srs FROM franchise_seasons "
                     "WHERE season >= 1985").fetchdf()
    con.close()
    rows = []
    for (f, s), g in ps.groupby(["franchise_id", "season"]):
        top = g.nlargest(10, "mp")
        if len(top) < 10:
            continue
        rows.append({"franchise_id": f, "season": s,
                     "rot_agg": float(rotation_aggregate(top.bpm.values))})
    m = pd.DataFrame(rows).merge(fs, on=["franchise_id", "season"])
    x, y = m.rot_agg.values, m.srs.values
    b, a = np.polyfit(x, y, 1)
    resid_sd = float((y - (a + b * x)).std(ddof=2))
    return {"a": float(a), "b": float(b), "resid_sd": resid_sd,
            "r": float(np.corrcoef(x, y)[0, 1]), "n": len(m)}


def star_exit_prior_shift() -> float:
    """Historical mean next-season SRS innovation surprise after a star
    departure, relative to the AR(1) expectation (phi from Model A v2)."""
    sp = pd.read_parquet(STAGED / "star_spells_provisional.parquet")
    exits = sp[sp.event_departure].groupby("spell_id").tail(1)
    panel = load_panel().set_index(["franchise_id", "season"]).srs
    post, _, _ = fit_trajectory(quiet=True)
    phi, mu_cols = float(post.phi.mean()), {c: float(post[c].mean())
                                            for c in post.columns if c.startswith("mu_")}
    surprises = []
    for _, r in exits.iterrows():
        k0, k1 = (r.franchise_id, int(r.season)), (r.franchise_id, int(r.season) + 1)
        if k0 in panel.index and k1 in panel.index:
            mu = mu_cols.get(f"mu_{r.franchise_id}", 0.0)
            expected = mu + phi * (panel.loc[k0] - mu)
            surprises.append(float(panel.loc[k1] - expected))
    return float(np.mean(surprises))


class EngineD:
    def __init__(self, n_paths: int, seed: int, use_roster_tier: bool = True):
        cfg = load_config()
        self.n_paths, self.seed = n_paths, seed
        self.use_roster_tier = use_roster_tier
        self.blend_w = cfg["simulation"]["blend_w"]
        self.rng = np.random.default_rng(seed)

        self.post_a, fr_ids, _ = fit_trajectory(quiet=True)
        self.fr_ids = fr_ids
        self.fr_index = {f: i for i, f in enumerate(fr_ids)}
        panel = load_panel()
        self.start_srs = panel[panel.season == 2026].set_index("franchise_id").srs.to_dict()
        self.wins_p = load_srs_to_wins()
        self.conf = np.array([0 if TEAM_CONF.get(f, "E") == "E" else 1 for f in fr_ids])

        draw_idx = self.rng.integers(0, len(self.post_a), n_paths)
        self.phi = self.post_a.phi.values[draw_idx]
        self.sigma = self.post_a.sigma.values[draw_idx]
        self.w_routine = self.post_a.w_routine.values[draw_idx]
        self.sigma_shock = self.post_a.sigma_shock.values[draw_idx]
        self.mu = np.stack([self.post_a[f"mu_{f}"].values[draw_idx] for f in fr_ids], axis=1)

        if use_roster_tier:
            self._init_roster_tier(cfg, draw_idx)

    def _init_roster_tier(self, cfg, draw_idx):
        self.rosters = load_rosters()
        self.roster_cal = fit_roster_to_srs()
        self.exit_shift = star_exit_prior_shift()
        aging_files = sorted(POSTERIORS.glob("aging_with_imputation_*.parquet"))
        self.aging_post = pd.read_parquet(aging_files[-1])
        # prefer the M2 FINAL hazard posterior when it exists (July-6+);
        # its contract covariates are detected by column presence below
        m2_files = sorted(POSTERIORS.glob("hazard_m2_full_*.parquet"))
        hazard_files = m2_files or sorted(POSTERIORS.glob("hazard_full_*.parquet"))
        self.hazard_post = pd.read_parquet(hazard_files[-1])
        self.hazard_is_m2 = "b_contract_z" in self.hazard_post.columns
        stats_file = POSTERIORS / "hazard_m2_stats.json"
        self.m2_stats = (json.loads(stats_file.read_text())
                         if self.hazard_is_m2 and stats_file.exists() else None)
        self.lamelo_scenario = cfg["simulation"].get("lamelo_contract", "unsigned")
        # precompute aging curve means per archetype x age grid (draws paired later)
        self.age_grid = np.arange(19, 45)
        self.aging_curves = {
            a: curve_from_posterior(self.aging_post, a, self.age_grid.astype(float))
            for a in ("guard", "wing", "big")}
        # hazard covariate normalization stats from the provisional fit input
        d = pd.read_parquet(STAGED / "star_spells_provisional.parquet")
        self.hz_stats = {
            "age_mean": d.age.mean(), "age_sd": d.age.std(),
            "yrs_mean": d.years_with_franchise.mean(), "yrs_sd": d.years_with_franchise.std(),
            "win_mean": d.team_win_pct_2yr.mean(), "win_sd": d.team_win_pct_2yr.std(),
            "an_mean": d.all_nba_count_career.mean(), "an_sd": d.all_nba_count_career.std(),
        }

    # ---- roster tier helpers -------------------------------------------
    def roster_srs(self, bpm: np.ndarray, minutes: np.ndarray) -> np.ndarray:
        ranked = np.sort(bpm, axis=-1)[..., ::-1]   # re-rank each season/path
        agg = rotation_aggregate(ranked)
        return self.roster_cal["a"] + self.roster_cal["b"] * agg

    def hazard_for(self, star, season_i, team_win2, departed_mask):
        s, st = star, self.hz_stats
        season = SEASONS[season_i]
        age = s["age_2026"] + season - 2026
        yrs = s["tenure_2026"] + season - 2026
        age_z = (age - st["age_mean"]) / st["age_sd"]
        cols = [
            np.full_like(team_win2, age_z),
            np.full_like(team_win2, age_z ** 2),
            np.full_like(team_win2, (yrs - st["yrs_mean"]) / st["yrs_sd"]),
            (team_win2 - st["win_mean"]) / st["win_sd"],
            np.zeros_like(team_win2),                       # deep_run_recent: sim-lite v1
            np.full_like(team_win2, s["spell_market_tier"] - 2.0),
            np.full_like(team_win2, 1.0 if yrs >= 7 else 0.0),
            np.full_like(team_win2, (s["all_nba_count"] - st["an_mean"]) / st["an_sd"]),
        ]
        covars = list(COVARS)
        if self.hazard_is_m2:
            cyr = contract_years_for(s, season, self.lamelo_scenario)
            m2 = self.m2_stats
            cols.append(np.full_like(team_win2,
                                     (cyr - m2["cyr_mean"]) / m2["cyr_sd"]))
            cols.append(np.ones_like(team_win2))            # contract_known
            covars += ["contract_z", "contract_known"]
        X = np.column_stack(cols)
        b = self.hazard_post[[f"b_{c}" for c in covars]].values
        hz_draw = self.rng.integers(0, len(self.hazard_post), len(team_win2))
        logits = (self.hazard_post.b0.values[hz_draw]
                  + (X * b[hz_draw]).sum(1)
                  + self.hazard_post["u_era_3"].values[hz_draw])
        h = 1 / (1 + np.exp(-logits))
        return np.where(departed_mask, 0.0, h)

    # ---- season mechanics ----------------------------------------------
    def wins_from_theta(self, theta):
        wp = 0.5 + self.wins_p["c"] * theta
        wp = wp + self.rng.normal(0, self.wins_p["resid_sd_win_pct"], wp.shape)
        wp = np.clip(wp, 0.02, 0.98)
        wins = wp * 82
        wins *= 1230.0 / wins.sum(axis=1, keepdims=True)
        return wins

    def playin_and_lottery_inputs(self, wins):
        """Per path: conference seeding, play-in resolution, lottery roles.
        Returns (lottery_teams, balls, relegated, playoff_no_ball_order)."""
        n = wins.shape[0]
        lottery_teams = np.empty((n, 16), dtype=int)
        balls = np.empty((n, 16))
        relegated = np.zeros((n, 16), dtype=bool)
        rest_order = np.empty((n, 14), dtype=int)
        srs_now = self._theta_now  # set by run loop before call
        for p in range(n):
            w = wins[p]
            entries = []          # (team_idx, balls): exactly 8 per conference
            playoff_no_ball = []  # exactly 7 per conference
            for c in (0, 1):
                idx = np.where(self.conf == c)[0]
                order = idx[np.argsort(-w[idx] + self.rng.uniform(0, 1e-6, len(idx)))]
                s7, s8, s9, s10 = order[6], order[7], order[8], order[9]

                def game(a, b_):
                    diff = srs_now[p, a] - srs_now[p, b_] + HOME_EDGE
                    return (a, b_) if self.rng.random() < _phi(diff / GAME_SD) else (b_, a)

                w78, l78 = game(s7, s8)
                w910, _ = game(s9, s10)
                game(l78, w910)  # second-chance winner is ALWAYS a ball-holder,
                # so the 8-seed identity never changes the ball table (A1:
                # roles fixed at seeding; a second-chance winner keeps balls)
                playoff_no_ball.extend(list(order[:6]) + [w78])
                entries.append((l78, BALLS_78_LOSER))
                entries.append((s9, BALLS_NINE_TEN))
                entries.append((s10, BALLS_NINE_TEN))
                entries.extend((t, BALLS_LOTTERY) for t in order[10:])
            teams = np.array([t for t, _ in entries])
            tballs = np.array([b_ for _, b_ in entries], dtype=float)
            # worst three records league-wide among lottery teams -> relegated
            worst3 = teams[np.argsort(w[teams])[:3]]
            for t in worst3:
                tballs[np.where(teams == t)[0][0]] = BALLS_RELEGATED
            order16 = np.argsort(w[teams])          # worst first
            lottery_teams[p] = teams[order16]
            balls[p] = tballs[order16]
            relegated[p] = np.isin(lottery_teams[p], worst3)
            pnb = set(playoff_no_ball)
            rest_order[p] = np.array([t for t in np.argsort(w) if t in pnb])
        return lottery_teams, balls, relegated, rest_order

    def run(self):
        n = self.n_paths
        theta = np.tile(np.array([self.start_srs[f] for f in self.fr_ids]), (n, 1))
        slots = np.zeros((n, len(SEASONS), len(self.fr_ids)), dtype=np.int8)
        win_paths = np.zeros((n, len(SEASONS), len(self.fr_ids)), dtype=np.float32)
        won_no1_last = np.zeros((n, len(self.fr_ids)), dtype=bool)
        top5_streak = np.zeros((n, len(self.fr_ids)), dtype=np.int8)
        departures = {s["player"]: np.zeros(n, dtype=bool)
                      for t in STARS for s in STARS[t]} if self.use_roster_tier else {}

        if self.use_roster_tier:
            rosters = {t: {
                "bpm": np.tile(self.rosters[t].bpm.values, (n, 1)),
                "age": self.rosters[t].age.values.astype(float).copy(),
                "arch": self.rosters[t].archetype.values,
                "minutes": self.rosters[t].minutes.values,
                "players": self.rosters[t].player.values,
            } for t in ("MIN", "CHA")}
            win2 = {t: np.full(n, 0.60 if t == "MIN" else 0.35) for t in ("MIN", "CHA")}
            # Model C parameter uncertainty pairs with paths (spec: posterior
            # draws per path). Posterior-MEAN deltas gave every path the same
            # deterministic young-core crest -- no stall-out worlds
            # (2026-07-02 escalation finding).
            aging_draw = self.rng.integers(0, len(self.aging_post), n)

        # the franchise-prior chain evolves from ITS OWN state (spec 7.4:
        # departure shocks "shift the franchise prior state" -- a separate
        # chain). Evolving the prior from the blended state let roster
        # optimism compound recursively (first 50k run: CHA median 51 wins
        # in 2033, prior-leak artifact).
        theta_prior_state = theta.copy()

        for si, season in enumerate(SEASONS):
            shock = self.rng.random(theta.shape) > self.w_routine[:, None]
            scale = np.where(shock, self.sigma_shock[:, None], self.sigma[:, None])
            innov = self.rng.normal(0, 1, theta.shape) * scale
            theta_prior = (self.mu + self.phi[:, None] * (theta_prior_state - self.mu)
                           + innov)

            theta_next = theta_prior.copy()
            if self.use_roster_tier:
                w_t = self.blend_w[season]
                for team in ("MIN", "CHA"):
                    ti = self.fr_index[team]
                    r = rosters[team]
                    # aging: per-path posterior curve draw (player-level eps
                    # deliberately NOT added: team-level dispersion is already
                    # carried by roster-cal resid_sd; documented)
                    for j in range(len(r["age"])):
                        a = int(np.clip(r["age"][j], 19, 44)) - 19
                        r["bpm"][:, j] += self.aging_curves[r["arch"][j]][aging_draw, a]
                        r["age"][j] += 1
                    # star departures
                    for s in STARS[team]:
                        pj = np.where(r["players"] == s["player"])[0]
                        if len(pj) == 0:
                            continue
                        h = self.hazard_for(s, si, win2[team], departures[s["player"]])
                        leave = (self.rng.random(n) < h) & ~departures[s["player"]]
                        if leave.any():
                            departures[s["player"]] |= leave
                            r["bpm"][leave, pj[0]] = REPLACEMENT_BPM
                            theta_prior[leave, ti] += self.exit_shift
                    th_roster = self.roster_srs(r["bpm"], r["minutes"][None, :])
                    theta_next[:, ti] = w_t * th_roster + (1 - w_t) * theta_prior[:, ti]

            theta_prior_state = theta_prior   # prior chain advances independently
            theta = theta_next
            self._theta_now = theta
            wins = self.wins_from_theta(theta)
            win_paths[:, si, :] = wins
            if self.use_roster_tier:
                for team in ("MIN", "CHA"):
                    ti = self.fr_index[team]
                    win2[team] = 0.5 * (win2[team] + wins[:, ti] / 82)

            lot_teams, balls, releg, rest = self.playin_and_lottery_inputs(wins)
            b1 = won_no1_last[np.arange(n)[:, None], lot_teams]
            b5 = (top5_streak >= 2)[np.arange(n)[:, None], lot_teams]
            picks16 = reformed_lottery(lot_teams, balls, releg, b1, b5, self.rng)

            season_slots = np.zeros((n, len(self.fr_ids)), dtype=np.int8)
            np.put_along_axis(season_slots, picks16, np.arange(1, 17, dtype=np.int8)[None, :]
                              .repeat(n, 0), axis=1)
            np.put_along_axis(season_slots, rest, np.arange(17, 31, dtype=np.int8)[None, :]
                              .repeat(n, 0), axis=1)
            slots[:, si, :] = season_slots

            won_no1_last[:] = season_slots == 1
            top5_streak = np.where(season_slots <= 5, top5_streak + 1, 0).astype(np.int8)

        return {"slots": slots, "win_paths": win_paths, "departures": departures,
                "fr_ids": self.fr_ids, "seasons": SEASONS}


def _phi(z):
    from math import erf, sqrt
    return 0.5 * (1 + erf(z / sqrt(2)))
