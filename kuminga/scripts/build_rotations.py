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

from kuminga.lib import kfreeze, rotation, runlog  # noqa: E402

# The heuristic itself now lives in kuminga/lib/rotation.py so build_rotations and
# shapley cannot drift apart again. These are re-exported for readability.
ROTATION_SIZE = rotation.ROTATION_SIZE
MPG_WEIGHT = rotation.MPG_WEIGHT
CURVE_WEIGHT = rotation.CURVE_WEIGHT
TEAM_MINUTES = rotation.TEAM_MINUTES
REPLACEMENT_NET = -2.0           # consensus_net for an unmatched / placeholder body
USE_CEILING = os.environ.get("KUMINGA_NO_CEILING", "") != "1"

# v1 failed both G4 gates. The sim now reads the gate-passing v3 book, mapped
# into this schema by adapt_roster_v3.py.
SNAP = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_SIM.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
INJ = os.path.join(REPO, "kuminga", "data", "injuries_2026_27.csv")
OUT_ROT = os.path.join(REPO, "kuminga", "outputs", "rotations_2026_27.csv")
OUT_CURVE = os.path.join(REPO, "kuminga", "outputs", "minutes_rank_curve.csv")
OUT_ROOK = os.path.join(REPO, "kuminga", "outputs", "rookie_priors.csv")
OUT_POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
OUT_POOLSHARE = os.path.join(REPO, "kuminga", "outputs", "team_pool_shares.csv")

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
                # 2026 rookies exist in no id namespace yet: nba_player_bio stops at the
                # 2025 class. Without an id their minutes were allocated and then DROPPED
                # by every consumer (which filters on notna(player_id)), so a team with a
                # rookie in its rotation was silently valued on fewer than 240 minutes.
                # Washington lost 19 of Dybantsa's minutes that way. Synthetic negative
                # ids keep them in the arithmetic and make them obvious in any join.
                if (pid is None or pd.isna(pid)) and is_rookie:
                    pid = -(1000 + int(slot))

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
        # WAS: an unconditional by-name removal of Josh Green, because both cap
        # branches had him leaving Minnesota and neither had him anywhere else. On
        # 2026-08-29 he was TRADED TO UTAH, so that line would now delete a real Jazz
        # rotation player from the league and understate Utah by 14.7M of salary and
        # roughly 25 minutes a night. The roster book already reflects the trade, so
        # the special case is gone and replaced by an assertion that it stays gone.
        _g = cur[cur.player_name.map(nkey) == nkey("Josh Green")]
        assert len(_g) <= 1, "Josh Green on more than one roster"
        r.note("Josh Green: on %s in the roster book (traded 2026-08-29); no by-name "
               "removal is applied any more" % (list(_g.team_abbr)[0] if len(_g)
                                                else "NO TEAM"))
        assert "MIN" not in set(_g.team_abbr), "Green still on Minnesota"
        pool_now = build_pool(cur, "team_abbr", "player_name", "nba_player_id", "current")

        # R6 baseline: the 2025-26 end-of-season roster, NO injuries applied.
        base_src = rost25.rename(columns={"team_abbreviation": "team_abbr", "player": "player_name"})
        pool_base = build_pool(base_src, "team_abbr", "player_name", "player_id", "baseline")
        pool_base["rs_avail"] = 1.0          # R6: no injuries on the baseline

        pool = pd.concat([pool_now, pool_base], ignore_index=True)

        # ---- position pool (S1) --------------------------------------------------
        # Primary listing decides the pool: Guard-Forward is a guard, Forward-Centre a
        # forward. Rookies have no bio row, so their draft-board position is used.
        pos_by_id = bio.set_index("player_id").position.to_dict()
        draft_pos = {nkey(p["player"]): p.get("position", "") for p in raw["draft"]["picks"]}
        def resolve_pos(row):
            if pd.notna(row.player_id) and row.player_id in pos_by_id:
                v = pos_by_id[row.player_id]
                if isinstance(v, str) and v:
                    return v
            dp = draft_pos.get(nkey(row.player_name), "")
            return {"G": "Guard", "F": "Forward", "C": "Center", "G-F": "Guard-Forward",
                    "F-C": "Forward-Center", "F-G": "Forward-Guard",
                    "C-F": "Center-Forward"}.get(dp, dp or "Forward")
        pool["position"] = pool.apply(resolve_pos, axis=1)
        pool["pool"] = pool.position.map(rotation.pool_of)
        r.note("position pools: " + str(pool.pool.value_counts().to_dict()))

        # Each team's OWN 2025-26 share of minutes by pool, which is the budget the
        # slot-aware allocator uses. Saved so downstream scripts use the same numbers.
        rsx = pg_adv[(pg_adv.season_type == "Regular Season") & (pg_adv.minutes_float > 0)].copy()
        rsx["pool"] = rsx.player_id.map(pos_by_id).map(rotation.pool_of)
        tri = tg[["team_id", "team_abbreviation"]].drop_duplicates().set_index("team_id").team_abbreviation
        tot = rsx.groupby(["team_id", "pool"]).minutes_float.sum().unstack(fill_value=0)
        shares = tot.div(tot.sum(axis=1), axis=0)
        shares.index = shares.index.map(tri)
        shares = shares.reindex(columns=["guard", "forward", "big"]).fillna(0.0)
        shares.to_csv(OUT_POOLSHARE)
        r.note("team pool shares saved; MIN big share "
               f"{shares.loc['MIN','big']*240:.1f} min vs league mean "
               f"{shares.big.mean()*240:.1f}")

        # ---- rank score (percentiles taken league-wide, within scenario) ---------
        pool["pct_mpg"] = pool.groupby("scenario").prior_mpg.rank(pct=True)
        pool["pct_net"] = pool.groupby("scenario").consensus_net.rank(pct=True)
        pool["rank_score"] = MPG_WEIGHT * pool.pct_mpg + (1 - MPG_WEIGHT) * pool.pct_net

        # ---- W1: the team-changer minutes rule -------------------------------
        # Prior minutes per appearance is a ROLE signal, and a role earned on one team
        # does not transfer to another. A player who moved is blended toward the rank
        # curve and away from his own prior load; incumbents keep the 50/50 blend. The
        # rule is mechanical and identical for all 30 teams, per R2.
        #
        # The BASELINE scenario is the 2025-26 end-of-season rosters, where by
        # construction nobody has moved, so no baseline player is reweighted. That
        # asymmetry is deliberate and is the point: the delta is supposed to price the
        # offseason, and the offseason is exactly who moved.
        _base_team = (pool[pool.scenario == "baseline"]
                      .dropna(subset=["player_id"])
                      .drop_duplicates("player_id")
                      .set_index("player_id").team_abbr)
        pool["team_2025_26"] = pool.player_id.map(_base_team)
        pool["moved_teams"] = ((pool.scenario == "current")
                               & pool.team_2025_26.notna()
                               & (pool.team_abbr != pool.team_2025_26))
        pool["curve_weight"] = np.where(pool.moved_teams,
                                        rotation.MOVER_CURVE_WEIGHT,
                                        rotation.CURVE_WEIGHT)
        n_moved = int(pool.moved_teams.sum())
        n_new = int(((pool.scenario == "current") & pool.team_2025_26.isna()).sum())
        r.note(f"W1 team-changer rule: curve weight {rotation.CURVE_WEIGHT} for "
               f"incumbents, {rotation.MOVER_CURVE_WEIGHT} for movers")
        r.note(f"  {n_moved} players changed teams; {n_new} current-scenario players "
               f"have no 2025-26 row (2026 draftees and unmatched) and keep the "
               f"incumbent blend, because there is no prior role to discount")

        # ---- allocate minutes ----------------------------------------------------
        out = []
        r.note(f"minutes ceiling ENABLED: {USE_CEILING} "
               f"(min(prior load + {rotation.CEILING_BONUS:.0f}, "
               f"{rotation.CEILING_HARD_MAX:.0f}), overflow cascades down the rank order)")
        for (scen, team), grp in pool.groupby(["scenario", "team_abbr"]):
            g = rotation.allocation_frame(grp, curve, use_ceiling=USE_CEILING)
            g["scenario"] = scen
            g["team_abbr"] = team
            out.append(g)
        rot = pd.concat(out, ignore_index=True)
        rot.to_csv(OUT_ROT, index=False)
        # The full pre-truncation pool, with every player's attributes. Item 11 needs
        # it to re-allocate minutes for each Shapley coalition, which changes who is
        # in the top ROTATION_SIZE.
        pool.to_csv(OUT_POOL, index=False)

        r.note(f"rotations built: {rot.scenario.nunique()} scenarios x "
               f"{rot.team_abbr.nunique()} teams, {len(rot)} player-rows")
        r.note(f"rookies placed in a rotation: {int(rot.is_rookie.sum())}")
        r.note(f"players on a replacement prior: {int((rot.impact_source=='replacement').sum())}")
        r.output(OUT_ROT, rows=len(rot))
        r.output(OUT_CURVE, rows=len(curve))
        r.output(OUT_ROOK, rows=60)
        r.output(OUT_POOL, rows=len(pool))
        r.output(OUT_POOLSHARE, rows=30)

    print()
    mn = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN")]
    print("MINNESOTA projected rotation (current):")
    print(mn[["rot_rank", "player_name", "mpg", "consensus_net", "prior_mpg",
              "impact_source", "rs_avail"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
