#!/usr/bin/env python3
"""U1a: fit a net-impact aging curve from the warehouse, then apply it to all 30 rosters.

DESIGN. The only per-player-per-season impact figure in the warehouse is
`nba_player_season_bio.net_rating`, an on-court net rating. Levels of that number are
badly team-confounded, so the curve is fitted on YEAR-OVER-YEAR DELTAS, where each
player is his own control:

    delta(age) = net_rating(season t) - net_rating(season t-1),  age = age in season t

and the delta is credited to the age the player reached. Deltas are averaged by age and
then SHRUNK toward zero by n / (n + K), so ages with thin samples pull toward "no
change" rather than toward whatever three players did. The season-over-season curve is
the cumulative sum of those shrunken deltas, re-centred so the peak is zero, giving a
penalty in net-rating points to apply at any age.

WHAT THIS DOES NOT CONTROL FOR, stated because it is the main threat:
  - Team change. A player moving to a better team posts a large positive delta that has
    nothing to do with aging. Mitigated by requiring the SAME TEAM in both seasons.
  - Survivorship. Players who decline badly leave the league and stop contributing
    deltas, which biases the late-career curve UPWARD (too flat). This is the standard
    aging-curve bias and it is not fixed here; the late-30s penalty should be read as a
    floor on the real decline, not an estimate of it.
  - Minutes. A player whose role shrinks may hold his net rating while contributing
    less. Not modelled.

SCALE. Net rating is per-100-possessions team margin while on court, which is roughly
2x the scale of the per-player impact numbers the forks carry (a +8 net-rating swing is
not a +8 impact player). The fitted curve is therefore rescaled by IMPACT_SCALE before
being applied to player impacts, and that constant is a judgement call, logged as one.

    python kuminga/scripts/aging_curve.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from kuminga.lib import runlog   # noqa: E402
from lib import db               # noqa: E402

OUT = os.path.join(REPO, "kuminga", "outputs", "aging_curve.csv")
OUT_APPLIED = os.path.join(REPO, "kuminga", "outputs", "aging_applied.csv")

MIN_GP = 30          # both seasons, so a delta is not two 8-game samples
SHRINK_K = 40.0      # n / (n + K); at n = 40 a cell keeps half its measured delta
AGE_LO, AGE_HI = 20, 39
IMPACT_SCALE = 0.5   # net-rating points -> impact points. JUDGEMENT CALL, see D-log.
FIRST_SEASON = 2000  # start year; earlier data is thinner and the league differs
# C: drop-outs re-entered at this percentile of same-age observed deltas.
# 0.25 is a stated assumption: a player who loses his roster spot is assumed
# to have been on a bad-but-not-catastrophic trajectory, not the median one.
DROPOUT_PCTILE = 0.25


def main():
    with runlog.run("aging_curve", inputs={"min_gp": MIN_GP, "shrink_k": SHRINK_K,
                                           "dropout_pctile": DROPOUT_PCTILE,
                                           "impact_scale": IMPACT_SCALE,
                                           "same_team_only": True}) as r:
        q = f"""
            select player_id, player_name, season_year, age, gp, net_rating,
                   team_abbreviation
            from nba.nba_player_season_bio
            where season_type = 'Regular Season' and net_rating is not null
              and gp >= {MIN_GP}
              and cast(substring(season_year from 1 for 4) as integer) >= {FIRST_SEASON}
        """
        d = db.query(q)
        # Postgres NUMERIC arrives as decimal.Decimal, which silently poisons any later
        # arithmetic mixed with floats (pandas .std() raises; .mean() can coerce).
        for c in ("age", "gp", "net_rating"):
            d[c] = pd.to_numeric(d[c], errors="coerce").astype(float)
        d["yr"] = d.season_year.str.slice(0, 4).astype(int)
        # one row per player-season: the team he played most for is already the bio row,
        # but a traded player can appear twice. Keep the highest-gp row.
        d = d.sort_values("gp", ascending=False).drop_duplicates(["player_id", "yr"])
        r.note(f"player-seasons after filters: {len(d):,} "
               f"({d.player_id.nunique():,} players, {d.yr.min()}-{d.yr.max()})")

        prev = d.copy()
        prev["yr"] = prev.yr + 1
        m = d.merge(prev[["player_id", "yr", "net_rating", "team_abbreviation"]],
                    on=["player_id", "yr"], suffixes=("", "_prev"))
        r.note(f"consecutive-season pairs: {len(m):,}")
        same = m[m.team_abbreviation == m.team_abbreviation_prev].copy()
        r.note(f"  same team both seasons: {len(same):,} "
               f"({len(same) / len(m):.0%}); team-changers dropped to limit the "
               f"team-quality confound")
        same["delta"] = same.net_rating - same.net_rating_prev
        same["imputed"] = False

        # ---- C: SURVIVORSHIP CORRECTION ------------------------------------
        # Players who drop out of the following season contribute no delta, and they are
        # not a random sample: they are disproportionately the ones who declined. Leaving
        # them out biases the curve UPWARD, which is why the uncorrected fit shows every
        # age below 27 improving and most teams gaining. Each drop-out is re-entered with
        # an IMPUTED delta at a low percentile of the observed deltas at the age he would
        # have reached. The percentile is a stated assumption, not a fitted quantity.
        if DROPOUT_PCTILE is not None:
            last_yr = int(d.yr.max())
            nxt = set(zip(d.player_id, d.yr - 1))     # (player, season he came FROM)
            drop = d[(d.yr < last_yr)
                     & ~d.apply(lambda x: (x.player_id, x.yr) in nxt, axis=1)].copy()
            drop["age"] = drop.age + 1                # the age he would have reached
            obs_by_age = same.groupby("age").delta
            q = {a: float(g.quantile(DROPOUT_PCTILE)) for a, g in obs_by_age
                 if len(g) >= 10}
            drop["delta"] = drop.age.map(q)
            drop = drop.dropna(subset=["delta"])
            drop["imputed"] = True
            r.note(f"SURVIVORSHIP: {len(drop):,} drop-outs re-entered at the "
                   f"{DROPOUT_PCTILE:.0%} percentile of same-age observed deltas "
                   f"({len(drop) / (len(same) + len(drop)):.0%} of the corrected sample)")
            cols = ["player_id", "player_name", "age", "yr", "delta", "imputed"]
            same = pd.concat([same[cols], drop[cols]], ignore_index=True)

        rows = []
        for age in range(AGE_LO, AGE_HI + 1):
            g = same[same.age == age]
            n = len(g)
            raw = float(g.delta.mean()) if n else 0.0
            w = n / (n + SHRINK_K)
            rows.append(dict(age=age, n=n, raw_delta=raw, shrunk_delta=raw * w,
                             weight=w, sd=float(g.delta.std()) if n > 1 else np.nan))
        cur = pd.DataFrame(rows)
        cur["cum"] = cur.shrunk_delta.cumsum()
        peak_age = int(cur.loc[cur.cum.idxmax(), "age"])
        # The CUMULATIVE curve is descriptive only: distance from a player's own peak.
        cur["curve_net"] = cur.cum - cur.cum.max()          # <= 0 everywhere
        # THE ADJUSTMENT THAT IS ACTUALLY APPLIED is the ONE-YEAR expected change, not
        # the distance from peak. A player's measured 2025-26 impact already reflects how
        # old he was; what a 2026-27 projection needs is only what changes next season.
        # Applying the cumulative curve instead double-counts age and penalises the young
        # twice: it made 20-year-old Joan Beringer the most penalised player on Minnesota
        # at -2.864, when this same data says he should IMPROVE by +1.5 net points.
        cur["applied_impact"] = cur.shrunk_delta * IMPACT_SCALE
        cur.to_csv(OUT, index=False)

        r.note(f"PEAK at age {peak_age} (cumulative maximum)")
        for _, x in cur.iterrows():
            if x.age % 2 == 0 or x.age in (peak_age, AGE_HI):
                r.note(f"  age {int(x.age):2d}  n={int(x.n):5d}  raw {x.raw_delta:+.3f}  "
                       f"shrunk {x.shrunk_delta:+.3f} net -> APPLIED "
                       f"{x.applied_impact:+.3f} impact  (cumulative vs peak "
                       f"{x.curve_net:+.3f}, descriptive only)")

        # ---- apply to all 30 rosters, identically -----------------------------
        pool = pd.read_csv(os.path.join(REPO, "kuminga", "outputs",
                                        "player_pool_2026_27.csv"))
        bio = db.query("""
            select player_id, max(age) as age_2025_26
            from nba.nba_player_season_bio
            where season_type = 'Regular Season' and season_year = '2025-26'
            group by player_id
        """)
        bio["age_2025_26"] = pd.to_numeric(bio.age_2025_26, errors="coerce").astype(float)
        p = pool.merge(bio, on="player_id", how="left")
        # age in 2026-27 is last season's age + 1; rookies with no row get the
        # league-median rookie age rather than being silently skipped.
        p["age_2026_27"] = p.age_2025_26 + 1
        n_missing = int(p.age_2026_27.isna().sum())
        # 2026 draftees have no prior season. They are ~20 entering 2026-27, not 22, and
        # the curve is steep down there, so the default matters.
        is_rk = p.age_2026_27.isna() & p.get("is_rookie", False).fillna(False).astype(bool)
        p.loc[is_rk, "age_2026_27"] = 20.0
        p.loc[p.age_2026_27.isna(), "age_2026_27"] = 22.0
        r.note(f"age resolved for {len(p) - n_missing}/{len(p)} pool rows; "
               f"{int(is_rk.sum())} rookies defaulted to 20, "
               f"{n_missing - int(is_rk.sum())} others to 22")
        cmap = dict(zip(cur.age, cur.applied_impact))
        lo, hi = cur.age.min(), cur.age.max()
        p["age_adj"] = [cmap.get(int(np.clip(a, lo, hi)), 0.0) for a in p.age_2026_27]
        p[["scenario", "team_abbr", "player_name", "player_id", "age_2026_27",
           "age_adj"]].to_csv(OUT_APPLIED, index=False)

        cur_sc = p[p.scenario == "current"]
        team_eff = (cur_sc.assign(w=cur_sc.prior_mpg.fillna(0))
                    .groupby("team_abbr")
                    .apply(lambda g: np.average(g.age_adj, weights=g.w)
                           if g.w.sum() else 0.0, include_groups=False)
                    .sort_values())
        r.note("")
        r.note("MINUTES-WEIGHTED ONE-YEAR AGE ADJUSTMENT by team (impact points):")
        r.note(f"  most penalised (oldest): " + ", ".join(
            f"{t} {v:+.3f}" for t, v in team_eff.head(5).items()))
        r.note(f"  most helped (youngest): " + ", ".join(
            f"{t} {v:+.3f}" for t, v in team_eff.tail(5).items()))
        r.note(f"  MIN: {team_eff.get('MIN', float('nan')):+.3f} "
               f"(rank {list(team_eff.index).index('MIN') + 1} of {len(team_eff)}, "
               f"1 = most penalised)")
        mn = cur_sc[cur_sc.team_abbr == "MIN"].sort_values("age_adj")
        for _, x in mn.head(4).iterrows():
            r.note(f"    {x.player_name:22s} age {x.age_2026_27:.0f}  {x.age_adj:+.3f}")
        r.output(OUT, rows=len(cur))
        r.output(OUT_APPLIED, rows=len(p))

    print()
    print(cur[["age", "n", "raw_delta", "shrunk_delta", "applied_impact",
               "curve_net"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
