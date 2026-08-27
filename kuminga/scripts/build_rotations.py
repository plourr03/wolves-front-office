#!/usr/bin/env python3
"""Item 8: the mechanical roster-delta projection for all 30 teams.

This replaces the engine's previous treatment, in which only MIA, MIN and BOS got a
modeled 2026-27 roster change (plus ORL and IND health cases) and the other 25 teams
were assumed to have stood pat at their measured 2025-26 net rating. The transaction
feed shows 309 legs and 16 trade groups across all 30 teams, so "stood pat" was false
for essentially everyone.

Per R2 the rule is MECHANICAL and IDENTICAL for all 30 teams. No hand-authored
rotations, no per-team judgment, no assumed_moves narratives.

THE HEURISTIC, stated once and applied everywhere
-------------------------------------------------
1. CANDIDATE POOL. Standard contracts and the R4 placeholder. Two-way contracts and
   dead-money rows are excluded from the rotation (two-ways cannot play more than a
   limited number of games and are not rotation pieces in a season projection).

2. AVAILABILITY (R7). A player's regular-season availability multiplies his minutes.
   rs_avail = 0 removes him from the rotation entirely and his minutes redistribute.

3. RANK SCORE. Each player is scored
       0.5 * pct_rank(prior_mpg) + 0.5 * pct_rank(consensus_net)
   where both percentile ranks are taken league-wide across all rostered players.
   Minutes alone would freeze every player in last season's role and would refuse to
   promote a player who changed teams into a bigger one; impact alone would hand a
   high-RAPM low-minute specialist a starter's load. The 50/50 split is a stated
   modelling choice, not a fitted one, and it is identical for all 30 teams.

4. MINUTES CURVE. The top ROTATION_SIZE available players by rank score receive
   minutes from an EMPIRICAL rank curve, fitted from the 2025-26 season itself: for
   each team, players are ranked by total minutes, and the league-average minutes per
   team game at each rank is the curve. So a team's third-best player gets what a
   third-best player actually played last season, not an invented number. The curve is
   rescaled so each team totals 240 minutes.

5. ROOKIES. 2026 draftees have no NBA minutes and no impact estimate. Both are
   supplied by draft-slot priors fitted from this project's own data:
     - impact: consensus_net regressed on draft slot across the 2025 draft class,
       whose rookie season IS the 2025-26 season the value spine is fitted on.
     - minutes: actual 2025-26 rookie minutes per game regressed on draft slot.
   Undrafted and unmatched players fall back to the replacement-level constant.

WHY THE DELTA IS THE PRODUCT, NOT THE LEVEL
-------------------------------------------
A talent rollup is not a calibrated net rating. Both the baseline (R6: the 2025-26
end-of-season roster) and the current roster are pushed through the SAME heuristic,
so the heuristic's level bias cancels in the difference. Each team's 2026-27 net is
then

    net = regress_to_expectation(measured 2025-26 net) + deflate(rollup_now - rollup_base)

which anchors on measured reality and moves it by the modelled roster change. This is
the same shape the engine already used for its three MOVED teams, applied to all 30.

    python kuminga/scripts/build_rotations.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import kfreeze, runlog  # noqa: E402

ROTATION_SIZE = 10
MPG_WEIGHT = 0.5                 # weight on prior minutes in the rank score
CURVE_WEIGHT = 0.5               # weight on the team-rank curve vs the player's own prior load
REPLACEMENT_NET = -2.0           # consensus_net for an unmatched / placeholder body
TEAM_MINUTES = 240.0

SNAP = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
INJ = os.path.join(REPO, "kuminga", "data", "injuries_2026_27.csv")
OUT_ROT = os.path.join(REPO, "kuminga", "outputs", "rotations_2026_27.csv")
OUT_CURVE = os.path.join(REPO, "kuminga", "outputs", "minutes_rank_curve.csv")
OUT_ROOK = os.path.join(REPO, "kuminga", "outputs", "rookie_priors.csv")

TF = {"PHO": "PHX", "BRK": "BKN", "CHO": "CHA"}


def nkey(name) -> str:
    import re
    import unicodedata
    s = str(name)
    try:
        s = s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    drop = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv"}
    s = " ".join(t for t in s.split() if t not in drop)
    return re.sub(r"[^a-z0-9]+", "", s)


# --------------------------------------------------------------------------- curve
def fit_minutes_curve(pg_adv: pd.DataFrame, tg: pd.DataFrame) -> pd.Series:
    """League-average minutes per team game by within-team minutes rank, 2025-26 RS."""
    rs = pg_adv[(pg_adv.season_type == "Regular Season") & (pg_adv.minutes_float > 0)]
    tot = rs.groupby(["team_id", "player_id"], as_index=False).minutes_float.sum()
    games = (tg[tg.season_type == "Regular Season"]
             .groupby("team_id").game_id.nunique().rename("g"))
    tot = tot.join(games, on="team_id")
    tot["mpg"] = tot.minutes_float / tot.g
    tot["rank"] = tot.groupby("team_id").mpg.rank(ascending=False, method="first")
    curve = tot[tot["rank"] <= ROTATION_SIZE].groupby("rank").mpg.mean()
    # normalise so the rotation sums to a full game
    curve = curve / curve.sum() * TEAM_MINUTES
    return curve


def fit_rookie_priors(bio: pd.DataFrame, pg_adv: pd.DataFrame, tg: pd.DataFrame,
                      value: pd.DataFrame):
    """Draft-slot priors for impact and minutes, fitted on the 2025 draft class."""
    rk = bio[bio.draft_year.astype(str) == "2025"].copy()
    rk["draft_number"] = pd.to_numeric(rk.draft_number, errors="coerce")
    rk = rk[rk.draft_number.notna()]

    rs = pg_adv[(pg_adv.season_type == "Regular Season") & (pg_adv.minutes_float > 0)]
    mins = rs.groupby("player_id").minutes_float.sum().rename("tot_min")
    gm = rs.groupby("player_id").game_id.nunique().rename("gp")
    rk = rk.join(mins, on="player_id").join(gm, on="player_id")
    rk["mpg"] = (rk.tot_min / 82.0).fillna(0.0)          # per team game, not per appearance

    v = value.set_index("player_id")
    rk["consensus_net"] = rk.player_id.map(v.consensus_net)

    # Linear fits on draft slot. Slot is a weak but real signal; the point is to avoid
    # giving the first pick and the 55th pick the same prior.
    fits = {}
    for col in ("consensus_net", "mpg"):
        sub = rk[rk[col].notna()]
        if len(sub) >= 10:
            b, a = np.polyfit(sub.draft_number, sub[col], 1)
            fits[col] = (a, b, len(sub))
        else:
            fits[col] = (REPLACEMENT_NET if col == "consensus_net" else 8.0, 0.0, len(sub))
    return fits, rk


def slot_prior(fits, col, slot):
    a, b, _ = fits[col]
    val = a + b * float(slot)
    if col == "mpg":
        return float(np.clip(val, 2.0, 30.0))
    return float(np.clip(val, -4.0, 2.0))


# --------------------------------------------------------------------------- main
def main():
    with runlog.run("build_rotations",
                    inputs={"snapshot": kfreeze.current_snapshot_id(),
                            "rotation_size": ROTATION_SIZE, "mpg_weight": MPG_WEIGHT}) as r:
        pg_adv, sid = kfreeze.load("player_games_adv")
        tg, _ = kfreeze.load("team_games", sid)
        bio, _ = kfreeze.load("player_bio", sid)
        rost25, _ = kfreeze.load("rosters_2025_26", sid)

        # Postgres NUMERIC columns arrive as decimal.Decimal, which will not divide by
        # a float. Coerce every numeric-ish column once, here, rather than discovering
        # it three joins downstream.
        for df, cols in ((pg_adv, ["minutes_float", "usage_percentage", "possessions"]),
                         (tg, ["pts", "plus_minus"]),
                         (bio, ["draft_number", "height_inches", "season_exp"])):
            for c in cols:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")

        value = pd.read_csv(VALUE)
        inj = pd.read_csv(INJ)
        snap = pd.read_csv(SNAP)

        # ---- empirical minutes curve --------------------------------------------
        curve = fit_minutes_curve(pg_adv, tg)
        curve.to_csv(OUT_CURVE)
        r.note("minutes curve (rank -> mpg): " +
               ", ".join(f"{int(k)}:{v:.1f}" for k, v in curve.items()))

        # ---- rookie priors -------------------------------------------------------
        fits, rk = fit_rookie_priors(bio, pg_adv, tg, value)
        r.note(f"rookie impact fit: consensus_net = {fits['consensus_net'][0]:.3f} "
               f"+ {fits['consensus_net'][1]:.5f} * slot  (n={fits['consensus_net'][2]})")
        r.note(f"rookie minutes fit: mpg = {fits['mpg'][0]:.2f} "
               f"+ {fits['mpg'][1]:.4f} * slot  (n={fits['mpg'][2]})")
        pd.DataFrame([{"pick": p,
                       "prior_consensus_net": slot_prior(fits, "consensus_net", p),
                       "prior_mpg": slot_prior(fits, "mpg", p)} for p in range(1, 61)]
                     ).to_csv(OUT_ROOK, index=False)

        # ---- prior minutes, league-wide -----------------------------------------
        # Minutes per APPEARANCE, not per team game. Dividing by 82 conflates role with
        # availability and would rate Edwards (61 games at ~35 mpg) as a 26-minute
        # player. Availability is applied separately and explicitly via rs_avail, so
        # folding it into the role signal as well would double-count it.
        rs = pg_adv[(pg_adv.season_type == "Regular Season") & (pg_adv.minutes_float > 0)]
        _tot = rs.groupby("player_id").minutes_float.sum()
        _app = rs.groupby("player_id").game_id.nunique()
        prior_mpg = (_tot / _app).rename("prior_mpg")

        # ---- impact table --------------------------------------------------------
        v = value.set_index("player_id")

        # ---- name -> id resolution for snapshot rows lacking an id ---------------
        bio_k = bio.copy()
        bio_k["k"] = bio_k.player_name.map(nkey)
        k2id = bio_k.drop_duplicates("k").set_index("k").player_id.to_dict()

        # ---- 2026 draft class, from the research pull ---------------------------
        raw = json.load(open(os.path.join(REPO, "kuminga", "data", "_research_raw.json"),
                             encoding="utf-8"))
        draft26 = {nkey(p["player"]): p for p in raw["draft"]["picks"]}
        r.note(f"2026 draft class available for slot priors: {len(draft26)} picks")

        inj_by_key = {nkey(x.player): x for _, x in inj.iterrows()}

        # ---- assemble both rosters ----------------------------------------------
        def build_pool(df, team_col, name_col, id_col, label):
            rows = []
            for _, x in df.iterrows():
                team = TF.get(x[team_col], x[team_col])
                name = x[name_col]
                k = nkey(name)
                pid = x[id_col] if id_col in df.columns and pd.notna(x.get(id_col)) else None
                if pid is None or (isinstance(pid, float) and np.isnan(pid)):
                    pid = k2id.get(k)
                pid = int(pid) if pid is not None and not pd.isna(pid) else None

                is_rookie = k in draft26
                slot = draft26[k]["pick"] if is_rookie else None

                cn = v.consensus_net.get(pid) if pid in v.index else None
                if cn is None or pd.isna(cn):
                    if is_rookie:
                        cn, src = slot_prior(fits, "consensus_net", slot), f"rookie_slot_{slot}"
                    else:
                        cn, src = REPLACEMENT_NET, "replacement"
                else:
                    src = "player_value"

                pm = prior_mpg.get(pid) if pid is not None else None
                if pm is None or pd.isna(pm):
                    pm = slot_prior(fits, "mpg", slot) if is_rookie else 6.0
                    pm_src = f"rookie_slot_{slot}" if is_rookie else "default_fringe"
                else:
                    pm, pm_src = float(pm), "measured_2025_26"

                ij = inj_by_key.get(k)
                avail = float(ij.rs_avail) if ij is not None else 1.0

                rows.append(dict(scenario=label, team_abbr=team, player_name=name,
                                 player_id=pid, is_rookie=is_rookie, draft_slot=slot,
                                 consensus_net=float(cn), impact_source=src,
                                 prior_mpg=float(pm), mpg_source=pm_src,
                                 rs_avail=avail))
            return pd.DataFrame(rows)

        cur = snap[snap.slot_type.isin(["standard", "placeholder"])]
        # R3: both Green branches (traded as a pure salary dump, or waived and
        # stretched) have him OFF the 2026-27 roster. The branches differ only in what
        # they do to the cap sheet, not to the team on the floor, so the strength and
        # attribution work runs once with Green removed and only the cap outputs fork.
        # He stays in the contract book and in team_state, which is where the fork lives.
        n_before = len(cur)
        cur = cur[cur.player_name.map(nkey) != nkey("Josh Green")]
        r.note(f"R3: removed Josh Green from the projected rotation pool "
               f"({n_before} -> {len(cur)} rostered players)")
        pool_now = build_pool(cur, "team_abbr", "player_name", "nba_player_id", "current")

        # R6 baseline: the 2025-26 end-of-season roster, NO injuries applied.
        base_src = rost25.rename(columns={"team_abbreviation": "team_abbr", "player": "player_name"})
        pool_base = build_pool(base_src, "team_abbr", "player_name", "player_id", "baseline")
        pool_base["rs_avail"] = 1.0          # R6: no injuries on the baseline

        pool = pd.concat([pool_now, pool_base], ignore_index=True)

        # ---- rank score (percentiles taken league-wide, within scenario) ---------
        pool["pct_mpg"] = pool.groupby("scenario").prior_mpg.rank(pct=True)
        pool["pct_net"] = pool.groupby("scenario").consensus_net.rank(pct=True)
        pool["rank_score"] = MPG_WEIGHT * pool.pct_mpg + (1 - MPG_WEIGHT) * pool.pct_net

        # ---- allocate minutes ----------------------------------------------------
        out = []
        for (scen, team), grp in pool.groupby(["scenario", "team_abbr"]):
            g = grp[grp.rs_avail > 0].sort_values("rank_score", ascending=False).copy()
            g = g.head(ROTATION_SIZE).reset_index(drop=True)
            g["rot_rank"] = g.index + 1
            g["curve_min"] = g.rot_rank.map(lambda i: curve.get(float(i), curve.iloc[-1]))
            # Blend the team-rank curve with the player's own prior load. The curve
            # alone lets a high-impact, moderate-minute player inherit a 36-minute
            # role he has never carried (Gobert, a 34-year-old centre who played 29);
            # prior minutes alone freeze everyone in last season's role and refuse to
            # promote a player who changed teams. Half and half is a stated modelling
            # choice, applied identically to all 30 teams.
            g["base_min"] = CURVE_WEIGHT * g.curve_min + (1 - CURVE_WEIGHT) * g.prior_mpg
            g["mpg"] = g.base_min * g.rs_avail
            tot = g.mpg.sum()
            if tot > 0:
                g["mpg"] = g.mpg / tot * TEAM_MINUTES      # always a full game of minutes
            out.append(g)
        rot = pd.concat(out, ignore_index=True)
        rot.to_csv(OUT_ROT, index=False)

        r.note(f"rotations built: {rot.scenario.nunique()} scenarios x "
               f"{rot.team_abbr.nunique()} teams, {len(rot)} player-rows")
        r.note(f"rookies placed in a rotation: {int(rot.is_rookie.sum())}")
        r.note(f"players on a replacement prior: {int((rot.impact_source=='replacement').sum())}")
        r.output(OUT_ROT, rows=len(rot))
        r.output(OUT_CURVE, rows=len(curve))
        r.output(OUT_ROOK, rows=60)

    print()
    mn = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN")]
    print("MINNESOTA projected rotation (current):")
    print(mn[["rot_rank", "player_name", "mpg", "consensus_net", "prior_mpg",
              "impact_source", "rs_avail"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
