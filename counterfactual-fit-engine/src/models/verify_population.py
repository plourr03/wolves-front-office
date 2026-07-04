"""Population verification (ruling 2026-07-03), BLOCKING the skill_vectors
freeze. Asserts that no query target and no backtest-scored incoming player
falls in the archetype-prior group (i.e., every one of them has a FITTED
skill vector, never an archetype fallback).

The fitted population = player-seasons with an own-column Layer-1a RAPM
estimate (rotation players; the factor model's domain). A backtest case's
incoming player is scored AS-OF their PRECEDING season, so the invariant is:
every backtest incoming player has a fitted vector for their preceding
season. Because the G4 inclusion filter already requires a top-100-minutes
incoming player (who by construction has RAPM), the two filters SHOULD be
consistent; this makes that a checked invariant.

SEALED DISCIPLINE: sealed-window (2021-22+) incoming players are checked BY
ID only. This prints COUNTS and the pass/fail invariant, never the case
list, team, or player names -- no sealed case is enumerated or scored.

Prints the check (not a summary). Exit code 1 if the invariant fails.
Usage: python -m src.models.verify_population
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.adapters.postmortem_lib import query  # noqa: E402
from src.etl.transaction_universe import (  # noqa: E402
    appearances, detect_team_changes, minutes_rank_by_season,
    FIRST_END_YEAR, TOP_MINUTES_RANK)

FEAT_PATH = FITENGINE_ROOT / "outputs" / "features" / "player_features.parquet"
DEV_MAX_END_YEAR = 2021
NAMED_QUERY_TARGETS = ["Anthony Edwards", "LaMelo Ball"]


def fitted_population() -> set:
    """(player_id, end_year) pairs that WILL receive a fitted vector:
    player-seasons with an own-column RAPM estimate."""
    f = pd.read_parquet(FEAT_PATH)
    f = f[f.off_rapm.notna()]
    return set(zip(f.player_id.astype(int), f.end_year.astype(int)))


def backtest_incoming(top_filter: bool = True) -> pd.DataFrame:
    """All team-change incoming players (every season), with the preceding
    end_year whose vector would be used. Optionally restrict to the G4
    top-100-preceding-minutes filter (the actual inclusion rule)."""
    app = appearances()
    changes = detect_team_changes(app)
    changes = changes[changes.end_year >= FIRST_END_YEAR].copy()
    if top_filter:
        ranks = minutes_rank_by_season().rename(
            columns={"end_year": "preceding_end_year"})
        changes = changes.merge(ranks, on=["player_id", "preceding_end_year"],
                                how="left")
        changes = changes[changes.min_rank <= TOP_MINUTES_RANK]
    return changes[["player_id", "end_year", "preceding_end_year"]].drop_duplicates()


def main() -> None:
    pop = fitted_population()
    pop_pids = {pid for pid, _ in pop}
    print(f"fitted population: {len(pop)} player-seasons "
          f"({len(pop_pids)} distinct players with own-column RAPM)")

    inc = backtest_incoming(top_filter=True)
    inc["has_vector"] = [
        (int(r.player_id), int(r.preceding_end_year)) in pop
        for r in inc.itertuples()]

    dev = inc[inc.end_year <= DEV_MAX_END_YEAR]
    sealed = inc[inc.end_year > DEV_MAX_END_YEAR]

    dev_ok = bool(dev.has_vector.all())
    sealed_ok = bool(sealed.has_vector.all())
    print("\n--- backtest incoming players (top-100-min filter), "
          "preceding-season vector coverage ---")
    print(f"DEV window (2015-16..2020-21): {len(dev)} incoming players, "
          f"all have a fitted prior-season vector: {dev_ok}")
    if not dev_ok:
        miss = dev[~dev.has_vector]
        print("  DEV MISSING (would take an archetype prior -- VIOLATION):")
        print(miss.to_string(index=False))
    # SEALED: counts + invariant ONLY, no case enumeration
    print(f"SEALED window (2021-22+, by id, NOT enumerated): {len(sealed)} "
          f"incoming players, all have a fitted prior-season vector: {sealed_ok}")
    if not sealed_ok:
        print(f"  SEALED VIOLATION: {int((~sealed.has_vector).sum())} incoming "
              "player(s) lack a fitted prior-season vector -> memo + Bobby "
              "ruling at F5 (NOT a silent archetype fallback). IDs withheld "
              "here to preserve the seal; surface under sealed ceremony.")

    # named query targets: explicit callout
    print("\n--- named query targets (explicit callout) ---")
    names = query("""SELECT DISTINCT player_id, player_name
                     FROM nba_player_stats WHERE player_name = ANY(%s)""",
                  (NAMED_QUERY_TARGETS,))
    for _, r in names.iterrows():
        seasons = sorted(ey for pid, ey in pop if pid == int(r.player_id))
        print(f"  {r.player_name} (id {r.player_id}): fitted vector seasons "
              f"{seasons}  -> in population: {len(seasons) > 0}")

    ok = dev_ok and sealed_ok and all(
        any(pid == int(r.player_id) for pid, _ in pop)
        for _, r in names.iterrows())
    print(f"\nPOPULATION VERIFICATION: {'PASS' if ok else 'FAIL'}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
