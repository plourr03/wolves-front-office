"""Historical replays (spec 8.5). ON-7 scope: DATA CUTS ONLY -- the replay
fits run after the final spells freeze (overnight directive constraint).

As-of discipline: every input is filtered to information available at the
as-of date. This module centralizes those cuts so the replay runner cannot
accidentally leak the future:
  - franchise panel: seasons <= as_of season (trajectory fit via
    fit(through=...) which keys its own cache)
  - draft outcomes for E1: draft_year <= as_of - 4 (full 4-yr value window
    observable at the time)
  - star spells: spell-season rows with season <= as_of, censoring flags
    recomputed at the boundary (a spell alive in as_of is censored there,
    whatever happened later)
  - lottery era: pre_2019_weighted (k=3)
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
STAGED = PROJECT_ROOT / "data" / "staged"


def panel_cut(as_of_season: int) -> pd.DataFrame:
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    df = con.execute("SELECT * FROM franchise_seasons WHERE season <= ?",
                     [as_of_season]).fetchdf()
    con.close()
    return df


def draft_cut(as_of_season: int) -> pd.DataFrame:
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    df = con.execute("SELECT * FROM draft_outcomes WHERE draft_year <= ?",
                     [as_of_season - 4]).fetchdf()
    con.close()
    return df


def spells_cut(as_of_season: int, source: str = "star_spells_provisional.parquet") -> pd.DataFrame:
    """Spell rows visible at as_of, with boundary censoring recomputed:
    any spell whose last visible row is as_of becomes censored there."""
    sp = pd.read_parquet(STAGED / source)
    cut = sp[sp.season <= as_of_season].copy()
    last_idx = cut.sort_values("season").groupby("spell_id").tail(1).index
    at_edge = cut.loc[last_idx, "season"] == as_of_season
    edge_idx = last_idx[at_edge]
    cut.loc[edge_idx, ["event_departure", "event_retire", "censored"]] = [False, False, True]
    return cut


def run_nets_replay(n_paths: int = 20_000):
    """The 2013 Celtics-Nets replay (spec 8.5 primary). BUILT 2026-07-02;
    EXECUTION deferred to post-final-spells per the overnight directive.

    v1 replay chain: as-of-2013 trajectory fit (fit(through=2013), own cache)
    -> pure-Model-A league sim 2014-2018 -> pre-2019 lottery (k=3, weighted
    table) with top-8-per-conference playoffs (no play-in that era) -> BKN
    slot distributions for 2014/2016/2018 + the 2017 swap vs BOS -> score
    realized outcomes (config/replay_nets_2013.yaml) against 90% intervals.
    Two-tier roster detail for 2013 BKN/BOS is an execution-time decision
    for Bobby (needs 2013 rosters; pure-A is the declared default)."""
    import numpy as np
    import yaml
    from src.models.trajectory import fit, forecast_paths, load_panel, load_params
    from src.sim.league_sim import TEAM_CONF
    from src.sim.lottery import legacy_lottery
    from src.sim.strength_blend import load_srs_to_wins

    cfg = yaml.safe_load((PROJECT_ROOT / "config" / "replay_nets_2013.yaml").read_text())
    params = load_params()
    post, fr_ids, _ = fit(through=2013, quiet=True)
    panel = panel_cut(2013)
    start = panel[panel.season == 2013].set_index("franchise_id").srs.to_dict()
    p = load_srs_to_wins()
    rng = np.random.default_rng(params["seed"] + 2013)
    horizons = 5   # 2014..2018
    srs = forecast_paths(post, fr_ids, start, horizons, n_paths, params["seed"] + 2013)
    present = [f for f in fr_ids if f in start]
    conf = np.array([0 if TEAM_CONF.get(f, "E") == "E" else 1 for f in present])
    results = {}
    for h, season in enumerate(range(2014, 2019)):
        wp = np.clip(0.5 + p["c"] * srs[:, h, :]
                     + rng.normal(0, p["resid_sd_win_pct"], (n_paths, len(present))),
                     0.02, 0.98)
        wp *= 0.5 / wp.mean(axis=1, keepdims=True)
        slots = np.zeros((n_paths, len(present)), dtype=np.int8)
        for path in range(n_paths):
            w = wp[path]
            playoff = []
            for c in (0, 1):
                idx = np.where(conf == c)[0]
                playoff.extend(idx[np.argsort(-w[idx])][:8])
            lott = np.array([i for i in np.argsort(w) if i not in set(playoff)])
            order = lott[np.argsort(w[lott])][:14]
            picks = legacy_lottery(order[None, :], "pre_2019_weighted", rng)[0]
            for j, t in enumerate(picks):
                slots[path, t] = j + 1
            rest = sorted(playoff, key=lambda i: w[i])
            for j, t in enumerate(rest):
                slots[path, t] = 15 + j
        results[season] = slots
    return results, present, cfg


def main():
    for s in (2013, 2019):
        p, d, sp = panel_cut(s), draft_cut(s), spells_cut(s)
        print(f"as-of {s}: panel {len(p)} rows (max {p.season.max()}), "
              f"drafts {d.draft_year.min()}-{d.draft_year.max()} ({len(d)}), "
              f"spells {sp.spell_id.nunique()} "
              f"({int(sp.groupby('spell_id').tail(1).censored.sum())} censored at edge)")
        assert p.season.max() == s and d.draft_year.max() == s - 4


if __name__ == "__main__":
    main()
