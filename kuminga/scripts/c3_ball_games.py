#!/usr/bin/env python3
"""C3: Ball's games. LaMelo Ball's games-played history by season with the cause of each
missed stretch, and the league base rate of games played for players with a comparable
injury history. Folds in the availability simulation (`c3_ball_availability.py`, both
bases) when its CSVs exist, so `docs/c3_ball_games.md` is the one C3 document.

HISTORY. Regular-season appearances from the warehouse box scores (a game counts when he
logged minutes), team games from the schedule, so the share is games played over games
the team played (72 in 2020-21). Missed stretches are runs of consecutive team games
without him. Causes come from `data/c3_ball_injury_causes.csv`, a hand-built table with
two source URLs and a quote per stretch (R8); a stretch with no row there is printed as
unsourced, never guessed.

BASE RATE. Every player-season t from 2001-02 to 2025-26 in which the player
  (a) was in the league five seasons earlier and last season (interior seasons with no
      box score count as zero games, so a whole season lost to injury counts),
  (b) had at least THREE of the five prior seasons at 60% or less of his team's games
      (Ball: 44%, 27% and 57% in 2022-23, 2023-24 and 2024-25),
  (c) was 23 to 27 years old in season t (Ball is 25 in 2026-27), and
  (d) played rotation minutes the season before, at least 24 minutes per appearance
      (Ball: 27.5 in 2025-26).
Variant B adds (e) a healthy season t-1, at least 80% of the team's games (Ball: 88%),
because the question is what follows a healthy year on top of a bad history, and that
selection matters. The outcome is the share of team games played in season t, reported
on an 82-game basis. Each player-season is one observation; the number of distinct
players is printed beside it. The unconditional rate for the same age and role band is
printed for comparison.

    python kuminga/scripts/c3_ball_games.py
"""
from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from kuminga.lib import runlog  # noqa: E402
from lib import db              # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
DOCS = os.path.join(REPO, "kuminga", "docs")
CAUSES = os.path.join(REPO, "kuminga", "data", "c3_ball_injury_causes.csv")
BALL = 1630163
CHA = 1610612766
AS_OF = "2026-09-22"
FORKS = ["consensus", "rapm", "box", "darko"]

AGE_LO, AGE_HI = 23, 27
HIST_SHARE, HIST_SEASONS = 0.60, 3
ROLE_MPA = 24.0
HEALTHY_PRIOR = 0.80
FIRST_T, LAST_T = 2001, 2025      # season start years


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def season_start(s):
    return int(str(s)[:4])


def history():
    rows = db.query("""
        with tg as (select season_year, game_id, game_date, matchup
                    from nba.nba_player_stats where team_id = %(cha)s and season_year >= '2020-21'
                    group by 1, 2, 3, 4),
             pg as (select game_id, minutes_played from nba.nba_player_stats where player_id = %(ball)s)
        select tg.season_year, tg.game_date, tg.matchup, g.season_type,
               (pg.game_id is not null and pg.minutes_played > 0) as played, pg.minutes_played
        from tg left join pg on pg.game_id = tg.game_id
        join nba.nba_games g on g.game_id = tg.game_id and g.team_id = %(cha)s
        order by tg.game_date""", {"cha": CHA, "ball": BALL})
    rs = rows[rows.season_type == "Regular Season"].copy()
    po = rows[rows.season_type == "Playoffs"]
    bio = db.query("select season_year, age from nba.nba_player_season_bio where player_id = %(b)s "
                   "and season_type = 'Regular Season'", {"b": BALL}).set_index("season_year").age
    hist = []
    for s, g in rs.groupby("season_year"):
        played = g[g.played]
        hist.append(dict(season=s, age=int(bio.get(s, np.nan)) if s in bio.index else np.nan,
                         games_played=int(g.played.sum()), team_games=len(g),
                         share=round(float(g.played.mean()), 4),
                         games_missed=int((~g.played).sum()),
                         mpg_per_appearance=round(float(played.minutes_played.mean()), 1) if len(played) else 0.0,
                         playoff_games=int(po[(po.season_year == s) & po.played].shape[0])))
    hist = pd.DataFrame(hist)
    rs["run"] = (rs.played != rs.played.shift()).cumsum()
    stretches = []
    for (s, _run, pl), g in rs.groupby(["season_year", "run", "played"]):
        if not pl:
            stretches.append(dict(season=s, first_missed=g.game_date.min().strftime("%Y-%m-%d"),
                                  last_missed=g.game_date.max().strftime("%Y-%m-%d"), games=len(g)))
    return hist, pd.DataFrame(stretches)


def panel():
    """One row per player-season: games played, team games (max over his teams), minutes per
    appearance, age."""
    ps = db.query("""
        with team_games as (select season_id, team_id, count(*) n from nba.nba_games
                            where season_type = 'Regular Season' group by 1, 2),
             app as (select s.player_id, s.season_year, s.team_id,
                            count(*) filter (where s.minutes_played > 0) gp,
                            avg(s.minutes_played) filter (where s.minutes_played > 0) mpa
                     from nba.nba_player_stats s
                     join nba.nba_games g on g.game_id = s.game_id and g.team_id = s.team_id
                     where g.season_type = 'Regular Season'
                     group by 1, 2, 3)
        select a.player_id, a.season_year, sum(a.gp) gp,
               max(t.n) team_games,
               sum(a.gp * coalesce(a.mpa, 0)) / nullif(sum(a.gp), 0) mpa
        from app a
        join team_games t on t.team_id = a.team_id
             and t.season_id = (20000 + cast(left(a.season_year, 4) as int))
        group by 1, 2""")
    bio = db.query("select player_id, season_year, max(age) age from nba.nba_player_season_bio "
                   "where season_type = 'Regular Season' group by 1, 2")
    ps = ps.merge(bio, on=["player_id", "season_year"], how="left")
    ps["t"] = ps.season_year.map(season_start)
    ps["share"] = ps.gp / ps.team_games
    return ps


def base_rate(ps):
    ps = ps.sort_values(["player_id", "t"])
    by_player = {pid: g.set_index("t") for pid, g in ps.groupby("player_id")}
    rows = []
    for pid, g in by_player.items():
        first = int(g.index.min())
        for t in g.index:
            if t < FIRST_T or t > LAST_T or first > t - 5:
                continue
            if (t - 1) not in g.index:
                continue
            prior = [float(g.share.get(k, 0.0)) if k in g.index else 0.0 for k in range(t - 5, t)]
            n_bad = sum(1 for x in prior if x <= HIST_SHARE)
            age = g.age.get(t)
            mpa1 = float(g.mpa.get(t - 1) or 0.0)
            rows.append(dict(player_id=pid, t=t, season=g.season_year.get(t), age=age,
                             share=float(g.share.get(t)), games_82=82.0 * float(g.share.get(t)),
                             prior_bad_seasons=n_bad, prior_share_min=min(prior),
                             share_prior=prior[-1], mpa_prior=mpa1,
                             in_age=(age >= AGE_LO) & (age <= AGE_HI) if pd.notna(age) else False,
                             in_role=mpa1 >= ROLE_MPA,
                             in_history=n_bad >= HIST_SEASONS,
                             healthy_prior=prior[-1] >= HEALTHY_PRIOR))
    c = pd.DataFrame(rows)
    c["cohort_A"] = c.in_age & c.in_role & c.in_history
    c["cohort_B"] = c.cohort_A & c.healthy_prior
    c["cohort_C"] = c.in_age & c.in_role & (c.prior_bad_seasons >= 2)
    c["cohort_D"] = c.age.between(22, 29) & c.in_role & c.in_history
    c["band_all"] = c.in_age & c.in_role
    return c


def summarize(c, mask, label):
    x = c[mask]
    g = x.games_82
    return dict(cohort=label, player_seasons=len(x), players=x.player_id.nunique(),
                mean_games=round(float(g.mean()), 1), median_games=round(float(g.median()), 1),
                p_ge_50=round(float((g >= 50).mean()), 3), p_ge_60=round(float((g >= 60).mean()), 3),
                p_ge_70=round(float((g >= 70).mean()), 3), p_all=round(float((x.share >= 0.99).mean()), 3),
                p_le_40=round(float((g <= 40).mean()), 3))


def write_doc(r, hist, stretches, summ, sim):
    L = ["# C3: Ball's games\n",
         "*As of %s. History from the warehouse box scores; causes from the sourced table in "
         "`data/c3_ball_injury_causes.csv`; base rate from every player-season since 2001-02 "
         "that matches the definition below; simulation on both aging bases. Run `%s`.*\n" % (AS_OF, r.run_id)]
    L.append("## His seasons\n")
    L.append("| season | age | games played | team games | share | missed | minutes per appearance | playoff games |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for _, x in hist.iterrows():
        L.append("| %s | %s | %d | %d | %.0f%% | %d | %.1f | %d |" % (
            x.season, "" if pd.isna(x.age) else int(x.age), x.games_played, x.team_games,
            100 * x.share, x.games_missed, x.mpg_per_appearance, x.playoff_games))
    L.append("")
    L.append("## Every missed stretch, with the cause on record\n")
    L.append("| season | first missed | last missed | games | cause | surgery | sources |")
    L.append("|---|---|---|---:|---|---|---|")
    for _, x in stretches.iterrows():
        cause = x.get("cause", "")
        if not isinstance(cause, str) or not cause.strip():
            cause, surg, src = "UNSOURCED (no row in the causes table)", "", ""
        else:
            surg = x.get("surgery", "")
            urls = [u for u in (x.get("source_url_1", ""), x.get("source_url_2", "")) if isinstance(u, str) and u.strip()]
            src = " ".join("[%d](%s)" % (i + 1, u) for i, u in enumerate(urls))
            if len(urls) < 2:
                src += " (single-sourced)"
        L.append("| %s | %s | %s | %d | %s | %s | %s |" % (x.season, x.first_missed, x.last_missed, x.games,
                                                        cause, surg if isinstance(surg, str) else "", src))
    L.append("")
    L.append("## The base rate: what a season after a history like his looks like\n")
    L.append("Definition: player-seasons from 2001-02 to 2025-26, age %d to %d, at least %.0f minutes per "
             "appearance the season before, and at least %d of the five prior seasons at %.0f%% or less of "
             "the team's games (a season with no box score in the middle of a career counts as zero). "
             "Variant B also requires a healthy prior season, at least %.0f%% of games, which is Ball's case "
             "(%.0f%% in 2025-26). C loosens the history to two of five prior seasons and D widens the age band "
             "to 22 to 29, both as sensitivity, because the strict cohort is small. Outcome: games played in the season that follows, on an 82-game basis. "
             "The band row is the same age and role band with no history condition.\n"
             % (AGE_LO, AGE_HI, ROLE_MPA, HIST_SEASONS, 100 * HIST_SHARE, 100 * HEALTHY_PRIOR,
                100 * float(hist.share.iloc[-1])))
    L.append("| cohort | player-seasons | players | mean games | median | P(50 or more) | P(60 or more) | P(70 or more) | P(all) | P(40 or fewer) |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, x in summ.iterrows():
        L.append("| %s | %d | %d | %.1f | %.1f | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f%% |" % (
            x.cohort, x.player_seasons, x.players, x.mean_games, x.median_games, 100 * x.p_ge_50,
            100 * x.p_ge_60, 100 * x.p_ge_70, 100 * x.p_all, 100 * x.p_le_40))
    L.append("")
    if sim is not None:
        L.append("## The simulation: title odds and P(top six) by Ball's regular-season games\n")
        L.append("Ball's regular-season availability set to games/82 with the pipeline's own allocator "
                 "redistributing his minutes, the regular-season net re-priced by the pipeline's formula, "
                 "the playoffs at full strength, common random numbers across the four states. Mean of the "
                 "four views with the band across views; the seed standard error is in the CSVs.\n")
        for basis, R in sim:
            L.append("**%s basis.**\n" % ("Primary" if basis == "unaged" else "Aged"))
            L.append("| Ball's games | title odds | band across views | drop from 82 | P(top six) | band | drop from 82 | mean West seed | net lost |")
            L.append("|---:|---:|---|---:|---:|---|---:|---:|---:|")
            for games, d in R.groupby("games", sort=False):
                L.append("| %d | %.2f%% | %.2f to %.2f | %.2fpp | %.1f%% | %.1f to %.1f | %.1fpp | %.2f | %.2f |" % (
                    games, d.title.mean(), d.title.min(), d.title.max(), d.title_drop_pp.mean(),
                    d.top6.mean(), d.top6.min(), d.top6.max(), d.top6_drop_pp.mean(),
                    d.mean_seed.mean(), (d.net_full - d.net_rs).mean()))
            L.append("")
    L.append("*Method.* Appearances: warehouse `nba_player_stats` joined to `nba_games`, Charlotte's schedule, "
             "a game counted when he logged minutes. Stretches: runs of consecutive team games without him. "
             "Base rate: `c3_base_rate_cohort.csv` holds every player-season with the flags; the summary is "
             "`c3_base_rate_summary.csv`. Simulation: `c3_ball_availability.py`, gates G1 to G5 in its "
             "docstring; detail in `outputs/c3_ball_availability.csv` and `_AGED.csv`, minutes in "
             "`c3_ball_minutes*.csv`.")
    path = os.path.join(DOCS, "c3_ball_games.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def main():
    with runlog.run("c3_ball_games", inputs={"causes": CAUSES, "age": [AGE_LO, AGE_HI],
                                             "hist_share": HIST_SHARE, "hist_seasons": HIST_SEASONS,
                                             "role_mpa": ROLE_MPA, "healthy_prior": HEALTHY_PRIOR,
                                             "seasons": [FIRST_T, LAST_T]}) as r:
        hist, stretches = history()
        r.note("Ball regular-season games by season: " + ", ".join(
            "%s %d/%d" % (x.season, x.games_played, x.team_games) for _, x in hist.iterrows()))
        if os.path.exists(CAUSES):
            causes = pd.read_csv(CAUSES, dtype=str)
            causes["games"] = causes.games.astype(int)
            stretches = stretches.merge(causes, on=["season", "first_missed", "last_missed", "games"], how="left")
            n_src = int(stretches.cause.notna().sum())
            r.note("causes table: %d of %d stretches sourced (sha256 %s)" % (n_src, len(stretches), sha(CAUSES)[:16]))
            two = int((stretches.source_url_1.notna() & stretches.source_url_2.notna()).sum())
            r.note("stretches with two source URLs: %d; single-sourced: %d" % (two, n_src - two))
        else:
            r.note("NO causes table at %s; every stretch printed as unsourced" % CAUSES)
        p_hist = os.path.join(OUT_DIR, "c3_ball_history.csv")
        p_str = os.path.join(OUT_DIR, "c3_ball_missed_stretches.csv")
        hist.to_csv(p_hist, index=False)
        stretches.to_csv(p_str, index=False)
        r.output(p_hist, rows=len(hist))
        r.output(p_str, rows=len(stretches))

        ps = panel()
        p_panel = os.path.join(OUT_DIR, "c3_player_seasons_panel.csv")
        ps.to_csv(p_panel, index=False)
        r.note("panel: %d player-seasons, %s to %s, sha256 %s" % (len(ps), ps.season_year.min(), ps.season_year.max(), sha(p_panel)[:16]))
        r.output(p_panel, rows=len(ps))
        # Ball's own row must reproduce from the panel
        b = ps[(ps.player_id == BALL)].set_index("season_year")
        for _, x in hist.iterrows():
            assert int(b.gp.get(x.season)) == x.games_played and int(b.team_games.get(x.season)) == x.team_games, \
                "panel disagrees with the history for %s" % x.season
        r.note("gate: the panel reproduces Ball's games and team games for all six seasons")
        c = base_rate(ps)
        summ = pd.DataFrame([summarize(c, c.cohort_A, "A: injury history"),
                             summarize(c, c.cohort_B, "B: injury history and a healthy prior season"),
                             summarize(c, c.cohort_C, "C: looser history, two of five prior seasons at 60% or less"),
                             summarize(c, c.cohort_D, "D: injury history, age 22 to 29"),
                             summarize(c, c.band_all, "band: same age and role, no history condition")])
        p_c = os.path.join(OUT_DIR, "c3_base_rate_cohort.csv")
        p_s = os.path.join(OUT_DIR, "c3_base_rate_summary.csv")
        c[c.band_all | c.cohort_D].to_csv(p_c, index=False)
        summ.to_csv(p_s, index=False)
        for _, x in summ.iterrows():
            r.note("%s: n=%d (%d players) mean %.1f, median %.1f, P(>=50) %.0f%%, P(>=60) %.0f%%, P(>=70) %.0f%%, P(all) %.0f%%"
                   % (x.cohort, x.player_seasons, x.players, x.mean_games, x.median_games, 100 * x.p_ge_50,
                      100 * x.p_ge_60, 100 * x.p_ge_70, 100 * x.p_all))
        r.output(p_c, rows=int((c.band_all | c.cohort_D).sum()))
        r.output(p_s, rows=len(summ))

        sim = []
        for basis, fn in (("unaged", "c3_ball_availability.csv"), ("aged", "c3_ball_availability_AGED.csv")):
            p = os.path.join(OUT_DIR, fn)
            if os.path.exists(p):
                sim.append((basis, pd.read_csv(p)))
        r.note("simulation CSVs folded in: %s" % ([b for b, _ in sim] or "none"))
        path = write_doc(r, hist, stretches, summ, sim or None)
        r.output(path)


if __name__ == "__main__":
    main()
