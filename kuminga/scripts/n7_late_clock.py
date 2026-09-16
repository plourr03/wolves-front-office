#!/usr/bin/env python3
"""N7: late-clock and late-and-close. Who creates Minnesota's and the contenders' shots
when the possession or the game is running out?

TWO SITUATIONS, from play-by-play.
  CLUTCH       fourth quarter or overtime, five minutes or less on the game clock, score
               within five BEFORE the shot (the league's clutch definition).
  LATE CLOCK   under seven seconds on the shot clock, with the shot clock still on.
For each creator, in each situation and overall: attempts, effective field-goal
percentage, and the share of his made shots that were UNASSISTED (he made the shot
himself). A league reference row gives the same numbers for every player, so a creator's
late-clock drop can be read against the drop everyone takes.

THE SHOT CLOCK IS RECONSTRUCTED, because play-by-play does not carry it. Walking each
game in order:
  24  at a new possession: period start, the opponent's made field goal, the opponent's
      last made free throw, a defensive rebound, an opponent turnover, a jump ball won
      by the other side.
  14  if lower, after an offensive rebound, a non-shooting defensive foul, or a kicked
      ball (the reset rule).
  OFF when the game clock is at or below the shot clock; those shots are excluded from
      the late-clock split, as the league's own tables do.
The reconstruction is only trusted if it passes GATE G1: at every shot-clock violation
the play-by-play records, the reconstructed clock should read close to zero. The share
within two seconds is reported, and the script fails closed below MIN_G1.
GATE G2: play-by-play field-goal attempts reconcile to box-score attempts.

TWO FORMATS. The 2025-26 regular season is split between the live-data feed (`cdn`, 729
games: `2pt`/`3pt` shots, explicit offensive/defensive rebounds, a score on every row,
team rebounds with no team id) and the stats feed (`stats_api`, 501 games: `Made
Shot`/`Missed Shot`, rebounds typed "Unknown", scores only on scoring rows, team rows
carrying the team id as the person id). No game appears in both. Both are parsed; the
rebound type is decided the same way in both, by comparing the rebounder's team with
the team that missed.

WHO IS A CREATOR. Minnesota: the five from M5 (Ball, Edwards, Kuminga, Dosunmu, Hyland).
Each contender in the N4 field: the three highest 2025-26 usage rates among its
projected 2026-27 top eight by minutes (1,000+ minutes). A player's numbers are his,
whatever team he played for.

SAMPLE SIZE, stated as a threshold. A situation with fewer than THIN_FGA attempts, or an
unassisted share resting on fewer than THIN_FGM makes, is flagged THIN. Two windows:
2025-26 (regular season and playoffs) and 2023-24 to 2025-26 pooled.

    python kuminga/scripts/n7_late_clock.py
"""
from __future__ import annotations

import os
import re
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
ROT = os.path.join(OUT_DIR, "rotations_2026_27.csv")
OUT_SHOTS = os.path.join(OUT_DIR, "n7_shots.parquet")
OUT = os.path.join(OUT_DIR, "n7_late_clock_splits.csv")
OUT_G = os.path.join(OUT_DIR, "n7_gates.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "n7_late_clock.md")

PREFIXES = ["00223", "00224", "00225", "00423", "00424", "00425"]
SEASON = {"23": "2023-24", "24": "2024-25", "25": "2025-26"}
FIELD = ["BOS", "OKC", "SAS", "DET", "CHA", "HOU", "TOR", "DEN"]   # N4, D75
MIN_CREATORS = {1630163: "LaMelo Ball", 1630162: "Anthony Edwards",
                1630228: "Jonathan Kuminga", 1630245: "Ayo Dosunmu",
                1630538: "Nah'Shon Hyland"}
LATE = 7.0
CLUTCH_SECS = 300.0
CLUTCH_MARGIN = 5
THIN_FGA = 50
THIN_FGM = 25
MIN_G1 = 0.80
LAG_GRID = [0.0, 1.0, 2.0, 3.0, 4.0]   # inbound lag after a made basket, seconds
CALIBRATE = "00223"                   # lag chosen on 2023-24 only; G1 judged on the rest
AST_RE = re.compile(r"\([^()]* [0-9]+ AST\)")


def clock_secs(s):
    m = re.match(r"PT(\d+)M([\d.]+)S", str(s))
    return int(m.group(1)) * 60 + float(m.group(2)) if m else np.nan


def reconstruct(ev, team_of_id, lag):
    """Walk one season's events in order; return shots with a reconstructed shot clock,
    and the clock read at every shot-clock violation (gate G1).

    Two corrections found by diagnosing the first G1 failure (65.8% within two seconds):
      BLOCKS  a blocked shot usually does not touch the rim, so the offensive rebound
              that follows does NOT reset the clock to 14. A miss is treated as blocked
              when a block is logged at the same second.
      INBOUND after a made basket the game clock keeps running during the inbound (except
              in the last two minutes of the fourth quarter and overtime, when it stops),
              while the shot clock starts on the touch. The possession therefore starts
              `lag` seconds after the basket. The lag is calibrated on one season and the
              gate is judged on the others."""
    blocks = set(zip(ev.loc[ev.is_block, "game_id"], ev.loc[ev.is_block, "period"],
                     ev.loc[ev.is_block, "clk"]))
    shots, g1 = [], []
    stats = dict(games=0, skipped_games=0, forced=0)
    for gid, gdf in ev.groupby("game_id", sort=False):
        teams = [t for t in gdf.team.dropna().unique()]
        if len(teams) != 2:
            stats["skipped_games"] += 1
            continue
        stats["games"] += 1
        other = {teams[0]: teams[1], teams[1]: teams[0]}
        off, start, base, last_miss_team = None, None, 24.0, None
        last_miss_blocked = False
        pre_reset = (None, np.nan)   # (clock, shot clock) just before a 14-second reset
        score_h = score_a = 0
        for x in gdf.itertuples(index=False):
            t = x.clk
            if x.at == "period" and x.st == "start":
                off, start, base, last_miss_team = None, t, 24.0, None
                continue
            team = x.team
            margin_before = abs(score_h - score_a)
            if pd.notna(x.sh) and pd.notna(x.sa):
                score_h, score_a = int(x.sh), int(x.sa)

            def rem():
                return base - (start - t) if start is not None else np.nan

            def new_poss(tm, when):
                nonlocal off, start, base
                off, start, base = tm, when, 24.0

            if x.fg == 1:
                if team is None:
                    continue
                forced = False
                if off != team:
                    forced = off is not None
                    stats["forced"] += int(forced)
                    new_poss(team, start if off is None and start is not None else t)
                r_ = rem()
                shots.append((gid, x.pid, team, x.period, t, x.made, x.val, x.ast,
                              margin_before, r_, t <= r_ if pd.notna(r_) else False,
                              forced, x.source))
                if x.made:
                    clock_stops = x.period >= 4 and t <= 120.0
                    new_poss(other[team], t if clock_stops else max(t - lag, 0.0))
                    last_miss_team = None
                else:
                    last_miss_team = team
                    last_miss_blocked = (gid, x.period, t) in blocks
            elif x.at == "freethrow":
                if team is None:
                    continue
                if x.last_ft and x.made:
                    new_poss(other[team], t)
                    last_miss_team = None
                elif x.last_ft and not x.made:
                    last_miss_team = team
                    last_miss_blocked = False
            elif x.at == "rebound":
                rt = team
                if rt is None and last_miss_team is not None:
                    rt = last_miss_team if x.st == "offensive" else other[last_miss_team]
                if rt is None:
                    continue
                if last_miss_team is not None and rt == last_miss_team:
                    if off != rt:
                        new_poss(rt, t)
                    elif rem() < 14.0 and not last_miss_blocked:
                        pre_reset = (t, rem())
                        start, base = t, 14.0
                else:
                    new_poss(rt, t)
                last_miss_team = None
            elif x.at == "turnover":
                if team is None:
                    continue
                if x.shot_clock_to:
                    # a violation is often logged with a bookkeeping team rebound at the
                    # same second; read the clock as it stood before that reset
                    val = pre_reset[1] if pre_reset[0] == t else rem()
                    g1.append((gid, x.period, t, val if off == team else np.nan,
                               x.source))
                new_poss(other[team], t)
                last_miss_team = None
            elif x.at == "foul":
                if team is None or off is None:
                    continue
                if team != off and x.nonshooting_def:
                    if rem() < 14.0:
                        start, base = t, 14.0
            elif x.at == "violation" and x.kicked:
                if off is not None and rem() < 14.0:
                    start, base = t, 14.0
            elif x.at == "jumpball" and x.st == "recovered":
                # only the live feed names the RECOVERING team; the stats feed's team
                # is the first jumper, so its jump balls are left to the next event
                if team is not None and team != off:
                    new_poss(team, t)
    s = pd.DataFrame(shots, columns=["game_id", "pid", "team", "period", "clock", "made",
                                     "val", "ast", "margin_before", "shot_clock",
                                     "clock_off", "forced", "source"])
    return s, pd.DataFrame(g1, columns=["game_id", "period", "clock", "shot_clock",
                                        "source"]), stats


def load_events(prefix, r):
    q = db.query("""
        select game_id, action_number, period, clock, team_id, team_tricode, person_id,
               action_type, sub_type, shot_result, is_field_goal, shot_value,
               score_home, score_away, description, source
        from nba.nba_play_by_play where game_id like %(p)s
    """, {"p": prefix + "%"})
    q["period"] = pd.to_numeric(q.period)
    q["clk"] = q.clock.map(clock_secs)
    q["at"] = q.action_type.fillna("").str.lower()
    q["st"] = q.sub_type.fillna("").str.lower()
    q["desc"] = q.description.fillna("")
    # normalise the two formats
    q["fg"] = pd.to_numeric(q.is_field_goal, errors="coerce").fillna(0).astype(int)
    q.loc[q["at"] == "free throw", "at"] = "freethrow"
    q.loc[q["at"] == "jump ball", "at"] = "jumpball"
    q["made"] = q.shot_result.fillna("").str.lower().eq("made")
    ft = q["at"] == "freethrow"
    # stats feed: free throws have no shot_result; a miss is written "MISS"
    q.loc[ft & q.shot_result.isna(), "made"] = ~q.loc[ft & q.shot_result.isna(),
                                                      "desc"].str.startswith("MISS")
    nm = q.st.str.extract(r"(\d+) of (\d+)")
    q["last_ft"] = ft & nm[0].notna() & (nm[0] == nm[1])
    q["val"] = pd.to_numeric(q.shot_value, errors="coerce").fillna(
        pd.Series(np.where(q.desc.str.contains("3PT"), 3, 2), index=q.index))
    q["ast"] = q.desc.str.contains(AST_RE)
    q["shot_clock_to"] = (q["at"] == "turnover") & q.st.str.contains("shot clock")
    q["nonshooting_def"] = (q["at"] == "foul") & q.st.isin(
        ["personal", "loose ball", "personal take", "transition take", "away from play"])
    q["kicked"] = q.st.str.contains("kicked ball")
    q["is_block"] = q["at"].eq("block") | q.desc.str.contains(r"\bBLOCK\b")
    q["sh"] = pd.to_numeric(q.score_home, errors="coerce")
    q["sa"] = pd.to_numeric(q.score_away, errors="coerce")
    q["pid"] = pd.to_numeric(q.person_id, errors="coerce")
    # team: tricode, else team id, else a team row whose person id IS the team id
    ids = q.dropna(subset=["team_id", "team_tricode"]).drop_duplicates("team_id")
    id2t = dict(zip(ids.team_id.astype(float), ids.team_tricode))
    q["team"] = q.team_tricode
    miss = q.team.isna()
    q.loc[miss, "team"] = q.loc[miss, "team_id"].astype(float).map(id2t)
    miss = q.team.isna()
    q.loc[miss, "team"] = q.loc[miss, "pid"].astype(float).map(id2t)
    q["team"] = q.team.where(q.team.notna(), None)
    q = q.sort_values(["game_id", "period", "clk", "action_number"],
                      ascending=[True, True, False, True])
    r.note("  %s: %s rows, %d games, formats %s" % (prefix, "{:,}".format(len(q)),
                                                   q.game_id.nunique(),
                                                   q.source.value_counts().to_dict()))
    return q, id2t


def main():
    if "--doc-only" in sys.argv:
        with runlog.run("n7_late_clock_doc", inputs={"from": [OUT, OUT_G, OUT_SHOTS]}) as r:
            src = [x.split('"run_id": "')[1].split('"')[0]
                   for x in open(os.path.join(REPO, "kuminga", "logs", "runs.jsonl"),
                                 encoding="utf-8")
                   if '"n7_late_clock_2' in x and '"ok"' in x]
            write_doc(r, src[-1] if src else "unknown")
            r.output(OUT_MD)
        return
    with runlog.run("n7_late_clock",
                    inputs={"prefixes": PREFIXES, "late": LATE, "clutch_secs": CLUTCH_SECS,
                            "clutch_margin": CLUTCH_MARGIN, "thin_fga": THIN_FGA,
                            "thin_fgm": THIN_FGM, "min_g1": MIN_G1}) as r:
        shots, g1s = [], []
        ev_c, id_c = load_events(CALIBRATE, r)
        cal = []
        for lag in LAG_GRID:
            _, g1c, _ = reconstruct(ev_c, id_c, lag)
            gc = g1c.dropna(subset=["shot_clock"])
            cal.append((lag, float((gc.shot_clock.abs() <= 2.0).mean()),
                        float(gc.shot_clock.median())))
            r.note("  calibration on %s, inbound lag %.0f s: within 2 s %.1f%%, median "
                   "%+.1f" % (CALIBRATE, lag, 100 * cal[-1][1], cal[-1][2]))
        LAG = max(cal, key=lambda c: c[1])[0]
        r.note("  chosen inbound lag: %.0f s (calibrated on %s only)" % (LAG, CALIBRATE))
        del ev_c
        for p in PREFIXES:
            ev, id2t = load_events(p, r)
            s, g1, stt = reconstruct(ev, id2t, LAG)
            r.note("    games reconstructed %d, skipped %d, shots %s, possession forced at "
                   "the shot %d (%.2f%%)" % (stt["games"], stt["skipped_games"],
                                             "{:,}".format(len(s)), stt["forced"],
                                             100 * stt["forced"] / max(len(s), 1)))
            s["season"] = SEASON[p[3:5]]
            s["phase"] = "PO" if p.startswith("004") else "RS"
            g1["prefix"] = p
            shots.append(s)
            g1s.append(g1)
        S = pd.concat(shots, ignore_index=True)
        G1 = pd.concat(g1s, ignore_index=True)
        S.to_parquet(OUT_SHOTS, index=False)

        # ---- gate G1: the clock at recorded shot-clock violations ------------------
        g_all = G1.dropna(subset=["shot_clock"])
        g = g_all[g_all.prefix != CALIBRATE]       # the gate is judged OUT of sample
        within2 = float((g.shot_clock.abs() <= 2.0).mean())
        r.note("")
        r.note("G1, judged on the seasons NOT used to calibrate the lag. "
               "Shot-clock violations: %d recorded, %d with the offence tracked | "
               "reconstructed clock median %+.1f s, within 2 s of zero %.1f%%, within 4 s "
               "%.1f%%" % (len(G1), len(g), g.shot_clock.median(), 100 * within2,
                           100 * float((g.shot_clock.abs() <= 4.0).mean())))
        for (p, src), gg in g_all.groupby(["prefix", "source"]):
            r.note("    %s %-9s: n %4d, median %+.1f s, within 2 s %.1f%%"
                   % (p, src, len(gg), gg.shot_clock.median(),
                      100 * float((gg.shot_clock.abs() <= 2.0).mean())))
        late_ok = within2 >= MIN_G1
        if not late_ok:
            # the clutch split does not use the shot clock, so it still ships; the
            # late-clock split is WITHHELD rather than printed from an untrusted clock
            r.note("G1 FAILED (%.1f%% < %.0f%%): the late-clock split is withheld"
                   % (100 * within2, 100 * MIN_G1))

        # ---- gate G2: attempts reconcile to the box score ---------------------------
        box = db.query("""
            select substr(game_id, 4, 2) yy, left(game_id, 3) ph, player_id::bigint pid,
                   sum(fga) fga
            from nba.nba_player_stats
            where left(game_id, 5) in %(p)s group by 1, 2, 3
        """, {"p": tuple(PREFIXES)})
        box["fga"] = pd.to_numeric(box.fga)
        tot_box = float(box.fga.sum())
        tot_pbp = float(len(S))
        r.note("G2 field-goal attempts: play-by-play %s, box score %s, gap %.2f%%"
               % ("{:,}".format(int(tot_pbp)), "{:,}".format(int(tot_box)),
                  100 * (tot_pbp - tot_box) / tot_box))
        if abs(tot_pbp - tot_box) / tot_box > 0.01:
            raise RuntimeError("G2 failed: attempts do not reconcile")

        # ---- situations -------------------------------------------------------------------
        S["efg_pts"] = np.where(S.made, np.where(S.val == 3, 1.5, 1.0), 0.0)
        S["clutch"] = (S.period >= 4) & (S.clock <= CLUTCH_SECS) & (
            S.margin_before <= CLUTCH_MARGIN)
        S["late"] = (~S.clock_off) & (S.shot_clock < LATE) & S.shot_clock.notna() & late_ok
        on = S[~S.clock_off & S.shot_clock.notna()]
        dist = pd.cut(on.shot_clock, [-99, 4, 7, 15, 18, 22, 99],
                      labels=["0-4", "4-7", "7-15", "15-18", "18-22", "22-24"])
        r.note("reconstructed shot-clock distribution of attempts (clock on): %s | clock "
               "off %.1f%% | unreconstructed %.1f%%"
               % (", ".join("%s %.1f%%" % (k, 100 * v) for k, v in
                            dist.value_counts(normalize=True).sort_index().items()),
                  100 * S.clock_off.mean(), 100 * S.shot_clock.isna().mean()))
        pd.DataFrame([dict(inbound_lag=LAG, late_ok=late_ok, g1_n=len(g), g1_within2=within2,
                           g1_median=float(g.shot_clock.median()), g2_pbp=tot_pbp,
                           g2_box=tot_box)]).to_csv(OUT_G, index=False)

        # ---- creators ----------------------------------------------------------------------
        adv = db.query("""
            select person_id::bigint pid, sum(minutes_float) mins,
                   sum(usage_percentage * possessions) / nullif(sum(possessions), 0) usg
            from nba.nba_player_advanced_stats
            where game_id like '00225%%' and minutes_float > 0 group by 1
        """)
        adv["usg"] = pd.to_numeric(adv.usg)
        adv["mins"] = pd.to_numeric(adv.mins)
        adv = adv.set_index("pid")
        rot = pd.read_csv(ROT)
        cur = rot[(rot.scenario == "current") & rot.player_id.notna() & (rot.mpg > 0)]
        creators = [(p, n, "MIN") for p, n in MIN_CREATORS.items()]
        for t in FIELD:
            g8 = cur[cur.team_abbr == t].sort_values("mpg", ascending=False).head(8).copy()
            g8["pid"] = g8.player_id.astype(int)
            g8["usg"] = g8.pid.map(adv.usg)
            g8["mins"] = g8.pid.map(adv.mins)
            g8 = g8[g8.mins >= 1000].sort_values("usg", ascending=False).head(3)
            creators += [(int(x.pid), x.player_name, t) for _, x in g8.iterrows()]
        r.note("creators: %s" % "; ".join("%s %s" % (t, n) for _, n, t in creators))

        def split(d):
            fga = len(d)
            fgm = int(d.made.sum())
            return dict(fga=fga, efg=float(d.efg_pts.sum() / fga) if fga else np.nan,
                        fgm=fgm, unast=float(1 - d[d.made].ast.mean()) if fgm else np.nan)

        rows = []
        windows = [("2025-26", S[S.season == "2025-26"]), ("2023-26 pooled", S)]
        for wlab, W in windows:
            lg = {"all": split(W), "clutch": split(W[W.clutch]), "late": split(W[W.late])}
            rows.append(dict(window=wlab, team="LEAGUE", player="every player",
                             **{"%s_%s" % (k, m): v for k in lg for m, v in lg[k].items()}))
            for pid, name, t in creators:
                d = W[W.pid == pid]
                sp = {"all": split(d), "clutch": split(d[d.clutch]), "late": split(d[d.late])}
                row = dict(window=wlab, team=t, player=name, pid=pid)
                for k in sp:
                    for m, v in sp[k].items():
                        row["%s_%s" % (k, m)] = v
                    row["%s_thin" % k] = bool(sp[k]["fga"] < THIN_FGA
                                              or sp[k]["fgm"] < THIN_FGM)
                    row["%s_share_of_fga" % k] = (sp[k]["fga"] / sp["all"]["fga"]
                                                  if sp["all"]["fga"] else np.nan)
                rows.append(row)
        T = pd.DataFrame(rows)
        T.to_csv(OUT, index=False)
        r.note("")
        for wlab in ("2025-26", "2023-26 pooled"):
            r.note("%s  (fga / eFG / unassisted share; * = thin)" % wlab)
            for _, x in T[T.window == wlab].iterrows():
                def cell(k):
                    return "%4d %.3f %s%s" % (x["%s_fga" % k], x["%s_efg" % k],
                                              "%.2f" % x["%s_unast" % k]
                                              if pd.notna(x["%s_unast" % k]) else " n/a",
                                              "*" if x.get("%s_thin" % k) is True else " ")
                r.note("  %-6s %-24s all %s | clutch %s | late %s"
                       % (x.team, x.player, cell("all"), cell("clutch"), cell("late")))
        r.output(OUT, rows=len(T))
        r.output(OUT_G, rows=1)
        r.output(OUT_SHOTS, rows=len(S))
        write_doc(r, r.run_id)
        r.output(OUT_MD)


def write_doc(r, sim_run):
    NL = "\n"
    T = pd.read_csv(OUT)
    G = pd.read_csv(OUT_G).iloc[0]
    S = pd.read_parquet(OUT_SHOTS)
    S["efg_pts"] = np.where(S.made, np.where(S.val == 3, 1.5, 1.0), 0.0)
    S["clutch"] = (S.period >= 4) & (S.clock <= CLUTCH_SECS) & (
        S.margin_before <= CLUTCH_MARGIN)
    on = S[~S.clock_off & S.shot_clock.notna()]
    near = float(((on.shot_clock - LATE).abs() <= 2.0).mean())

    def se_rows(W, lg):
        """Clutch-minus-overall eFG for a player, net of the league's own drop, in
        standard errors from his own shot-level variance."""
        out = {}
        for pid, d in W.groupby("pid"):
            c, a_ = d[d.clutch].efg_pts, d.efg_pts
            if len(c) < 2:
                continue
            diff = (c.mean() - a_.mean()) - lg
            se = float(np.sqrt(c.var(ddof=1) / len(c)))
            out[pid] = (diff, diff / se if se else np.nan)
        return out

    L = ["# N7: late-and-close and late-clock creation" + NL,
         "*As of 2026-09-16. OBSERVED, play-by-play, regular seasons and playoffs 2023-24 "
         "to 2025-26. Run `%s`; doc run `%s`.*" % (sim_run, r.run_id) + NL]
    lgp = T[(T.window == "2023-26 pooled") & (T.team == "LEAGUE")].iloc[0]
    se_pooled = se_rows(S, lgp.clutch_efg - lgp.all_efg)
    ok_rows = T[(T.window == "2023-26 pooled") & (T.team != "LEAGUE") & T.clutch_thin.eq(False)]
    zs = {x.player: se_pooled.get(int(x.pid), (np.nan, np.nan)) for _, x in ok_rows.iterrows()}
    big = [(n, d, z) for n, (d, z) in zs.items() if pd.notna(z) and abs(z) >= 2]
    chance = 2 * 0.02275 * len(zs)
    sd_c = float(S[S.clutch].efg_pts.std())
    mnp = T[(T.window == "2023-26 pooled") & (T.team == "MIN")].set_index("player")
    ed = mnp.loc["Anthony Edwards"]
    ed_d, ed_z = se_pooled.get(int(ed.pid), (np.nan, np.nan))
    lb = mnp.loc["LaMelo Ball"]
    lb_d, lb_z = se_pooled.get(int(lb.pid), (np.nan, np.nan))
    # the prose below says both sit inside the noise; fail rather than print it untrue
    assert abs(ed_z) < 2 and abs(lb_z) < 2, "Minnesota creator sentence no longer true"
    L.append("**In plain terms.** In the last five minutes of a game within five points, "
             "every team's shooting gets worse and more of its baskets are made without an "
             "assist: across the league since 2023-24, effective shooting falls from %.3f "
             "to %.3f and the unassisted share of made shots rises from %.0f%% to %.0f%%. "
             "So the useful question about a creator is how much worse than that he gets, "
             "and it is answered below for Minnesota's five and each contender's top three. "
             "Of the %d creators with enough clutch shots to judge, %d differ from the "
             "league's drop by two standard errors or more (%s), against about %.1f that "
             "chance alone would produce across that many comparisons. Minnesota's two "
             "creators sit inside the noise: Anthony Edwards shot %.3f in the clutch on %d "
             "attempts, %+.3f beyond the league's drop (%+.1f SEs), with %.0f%% of his "
             "clutch baskets unassisted; LaMelo Ball shot %.3f on %d, %+.3f (%+.1f SEs), "
             "%.0f%% unassisted. **The late-clock half (under seven seconds on the shot clock) is "
             "withheld.** Play-by-play does not record the shot clock, the reconstruction "
             "was held to a bar set before it was built, and it missed: %.1f%% of recorded "
             "shot-clock violations read within two seconds of zero on the seasons it was "
             "not tuned on, against a bar of %.0f%%. With %.0f%% of all attempts sitting "
             "within two seconds of the seven-second line, a clock that is off by more than "
             "two seconds one time in five would move too many shots across the line to "
             "trust a creator's split." % (
                 lgp.all_efg, lgp.clutch_efg, 100 * lgp.all_unast, 100 * lgp.clutch_unast,
                 len(zs), len(big),
                 ", ".join("%s %+.1f" % (n, z) for n, d, z in big) if big else "none",
                 chance, ed.clutch_efg, ed.clutch_fga, ed_d, ed_z, 100 * ed.clutch_unast,
                 lb.clutch_efg, lb.clutch_fga, lb_d, lb_z, 100 * lb.clutch_unast,
                 100 * G.g1_within2, 100 * MIN_G1, 100 * near) + NL)

    for wlab, W in (("2023-26 pooled", S),
                    ("2025-26", S[S.game_id.astype(str).str[3:5] == "25"])):
        lgrow = T[(T.window == wlab) & (T.team == "LEAGUE")].iloc[0]
        lgdrop = lgrow.clutch_efg - lgrow.all_efg
        se = se_rows(W, lgdrop)
        L.append("## Clutch, %s" % wlab + NL)
        L.append("League: %s clutch attempts, eFG %.3f against %.3f overall (a drop of "
                 "%.3f), unassisted share %.2f against %.2f." % (
                     "{:,}".format(int(lgrow.clutch_fga)), lgrow.clutch_efg, lgrow.all_efg,
                     -lgdrop, lgrow.clutch_unast, lgrow.all_unast) + NL)
        L.append("| team | creator | clutch attempts | clutch eFG | overall eFG | clutch "
                 "change beyond the league's drop | in SEs | unassisted share, clutch / "
                 "overall | sample |")
        L.append("|---|---|---:|---:|---:|---:|---:|---|---|")
        for _, x in T[(T.window == wlab) & (T.team != "LEAGUE")].iterrows():
            d, z = se.get(int(x.pid), (np.nan, np.nan))
            L.append("| %s | %s | %d | %.3f | %.3f | %+.3f | %+.1f | %s / %.2f | %s |"
                     % (x.team, "**%s**" % x.player if x.team == "MIN" else x.player,
                        x.clutch_fga, x.clutch_efg, x.all_efg, d, z,
                        "%.2f" % x.clutch_unast if pd.notna(x.clutch_unast) else "n/a",
                        x.all_unast, "*thin*" if x.clutch_thin else "ok"))
        L.append("")

    L.append("## Late clock: withheld, and why" + NL)
    L.append("| reconstruction check | value |")
    L.append("|---|---|")
    L.append("| inbound lag after a made basket, chosen on the 2023-24 regular season "
             "only | %.0f seconds |"
             % G.inbound_lag)
    L.append("| recorded shot-clock violations used to judge it (every season and phase "
             "except the 2023-24 regular season, with the offence tracked) | %s |"
             % "{:,}".format(int(G.g1_n)))
    L.append("| reconstructed clock at those violations: median | %+.1f seconds |"
             % G.g1_median)
    L.append("| within two seconds of zero | **%.1f%%** (bar %.0f%%, set in advance) |"
             % (100 * G.g1_within2, 100 * MIN_G1))
    L.append("| field-goal attempts, play-by-play against box score | %s against %s |"
             % ("{:,}".format(int(G.g2_pbp)), "{:,}".format(int(G.g2_box))))
    L.append("| attempts within two seconds of the seven-second line | %.0f%% |"
             % (100 * near))
    L.append("")
    L.append("The first build read 65.8%% within two seconds across all seasons. Diagnosing the misses found "
             "two real errors: an offensive rebound after a blocked shot was resetting the "
             "clock to 14, though a blocked shot usually never touches the rim, and after a "
             "made basket the game clock runs during the inbound while the shot clock does "
             "not start until the touch. Fixing both, with the inbound lag chosen on one "
             "season and the check run on the others, brought it to %.1f%%. The bar was not "
             "moved to meet the result. The split can ship if a recorded shot clock becomes "
             "available (the league's tracking splits by shot-clock range are not in the "
             "warehouse), or if the bar is deliberately set lower as a decision, with this "
             "figure beside it. The reconstructed clock for every attempt is kept in "
             "`outputs/n7_shots.parquet` either way." % (100 * G.g1_within2) + NL)
    L.append("**What the clutch half does not show.** Who is on the floor, or who defends "
             "the shot. Free throws, which are a large part of late-game scoring and are not "
             "in eFG. Turnovers, which end possessions a creator never shot. And most "
             "individual clutch samples are small: a player needs %d attempts and %d makes "
             "in the situation before his row is marked ok, and even then a clutch eFG "
             "carries a standard error of about %.3f at %d attempts and %.3f at 300."
             % (THIN_FGA, THIN_FGM, sd_c / np.sqrt(THIN_FGA), THIN_FGA,
                sd_c / np.sqrt(300)) + NL)
    L.append("*Definitions.* Clutch: fourth quarter or overtime, 5:00 or less, score within "
             "five before the shot. eFG: (FGM + 0.5 x 3PM) / FGA. Unassisted: a made field "
             "goal with no assister named. Change beyond the league's drop: the creator's "
             "clutch eFG minus his overall eFG, minus the league's clutch minus overall, "
             "with a standard error from the variance of his own clutch shots. Creators: "
             "Minnesota's five from M5; each N4 contender's three highest 2025-26 usage rates "
             "among its projected top eight (1,000+ minutes). Detail: "
             "`outputs/n7_late_clock_splits.csv`, `n7_gates.csv`, `n7_shots.parquet`." + NL)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(NL.join(L))



if __name__ == "__main__":
    main()
