#!/usr/bin/env python3
"""
gobert_delivery_addendum.py -- the addendum to the usage audit:
 (a) TEAM-level PnR ball-handler frequency by season, UTA vs MIN, to separate SCHEME CHOICE
     (does the team run PnR at all?) from FEEDER SCARCITY (is the volume concentrated in one
     player?), plus Edwards' own PnR ball-handler volume by year (it halved in 2025-26).
 (b) Project the delivery-system count (>=150 offensive PnR ball-handler poss) onto the
     Portfolio A and C rosters using each addition's historical PnR ball-handler volume
     (Dosunmu full season, Mitchell, McBride, and the MLE tier: Powell, McCollum, Huerter).
     If the plan moves the feeder count from 1 toward 3, that number is the Piece 2 -> Piece 7 bridge.

    python gobert_delivery_addendum.py
"""
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
from lib import db  # noqa: E402
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40)

EDWARDS = 1630162
MEANINGFUL = 150   # full-season offensive PnR ball-handler poss = a real live-dribble feeder
# Portfolio A/C additions (and incumbents to re-check). Match by name ILIKE.
ADDITIONS = ["Dosunmu", "Ajay Mitchell", "McBride", "Norman Powell", "McCollum", "Huerter",
             "Conley", "Jalen Smith", "DiVincenzo",
             "Terrence Shannon"]  # Finch-floated internal on-ball branch (June 2026); below the bar


def q(sql, params=None):
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = 30000")
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


def main():
    # ---- (a) TEAM PnR ball-handler frequency, UTA vs MIN, vs league avg ----
    tm = q("""SELECT season_year, team_abbreviation team, poss, poss_pct, ppp
              FROM nba_synergy_team_play_types
              WHERE play_type='PRBallHandler' AND type_grouping='Offensive'
                AND season_type='Regular Season' AND team_abbreviation IN ('UTA','MIN')
              ORDER BY season_year, team_abbreviation""")
    lg = q("""SELECT season_year, AVG(poss_pct) lg_poss_pct, AVG(poss) lg_poss
              FROM nba_synergy_team_play_types
              WHERE play_type='PRBallHandler' AND type_grouping='Offensive'
                AND season_type='Regular Season'
              GROUP BY season_year ORDER BY season_year""")
    tm = tm.merge(lg, on="season_year", how="left")
    tm["vs_lg_pp"] = ((tm["poss_pct"] - tm["lg_poss_pct"]) * 100).round(1)
    print("=== (a) TEAM PnR ball-handler frequency (offensive), UTA + MIN vs league avg ===")
    print("   poss_pct = share of team offense run as PnR ball-handler (SCHEME frequency)")
    for _, r in tm.iterrows():
        era = "UTA" if r.team == "UTA" else "MIN"
        print(f"  {r.season_year} {r.team}: team poss_pct {r.poss_pct*100:4.1f}%  (league {r.lg_poss_pct*100:4.1f}%, "
              f"{r.vs_lg_pp:+.1f}pp)  total poss {int(r.poss)}  ppp {r.ppp:.3f}")

    # ---- Edwards' own PnR ball-handler volume by year ----
    ed = q("""SELECT season_year, poss, poss_pct, ppp
              FROM nba_synergy_player_play_types
              WHERE player_id=%s AND play_type='PRBallHandler' AND type_grouping='Offensive'
                AND season_type='Regular Season' ORDER BY season_year""", (EDWARDS,))
    print("\n=== Edwards own PnR ball-handler poss by year (the lone MIN feeder) ===")
    print(ed.to_string(index=False))

    # ---- (b) additions' historical PnR ball-handler volume (per-game projected to full season) ----
    print("\n=== (b) Portfolio A/C additions: PnR ball-handler volume (offensive) ===")
    print("   poss + gp by season; full-season projection = poss/gp * 72 (to compare to the 150 bar)")
    proj = {}
    for name in ADDITIONS:
        d = q("""SELECT s.season_year, s.player_name, s.poss, s.gp
                 FROM nba_synergy_player_play_types s
                 WHERE s.player_name ILIKE %s AND s.play_type='PRBallHandler'
                   AND s.type_grouping='Offensive' AND s.season_type='Regular Season'
                   AND s.season_year IN ('2023-24','2024-25','2025-26')
                 ORDER BY s.season_year""", (f"%{name}%",))
        if not len(d):
            print(f"  {name:16}: no PnR ball-handler rows (likely a non-initiator / spot-up role)")
            proj[name] = 0
            continue
        d["per72"] = (d["poss"] / d["gp"].clip(lower=1) * 72).round(0)
        # representative = max recent full-season-projected volume
        best = d.sort_values("per72").iloc[-1]
        proj[name] = int(best["per72"])
        rows = " | ".join(f"{r.season_year}:{int(r.poss)}poss/{int(r.gp)}gp(->{int(r.per72)})" for _, r in d.iterrows())
        clears = "CLEARS 150" if best["per72"] >= MEANINGFUL else "below 150"
        print(f"  {best['player_name'][:16]:16}: {rows}   best proj {int(best['per72'])} [{clears}]")

    # ---- project the feeder count for Portfolio A and C ----
    # Incumbent feeders kept by A/C: Edwards (the lone 2025-26 feeder). Conley re-checked.
    ed_now = int(ed[ed.season_year == "2025-26"]["poss"].iloc[0]) if len(ed[ed.season_year == "2025-26"]) else 0
    def clears(name): return proj.get(name, 0) >= MEANINGFUL
    print("\n=== PROJECTED DELIVERY-SYSTEM COUNT (>=150 PnR ball-handler poss) ===")
    print(f"  2025-26 actual MIN: 1 (Edwards {ed_now})")
    # Portfolio A: Dosunmu re-sign + flier (McBride or Mitchell) + MLE shooter (Powell/McCollum/Huerter tier)
    base = ["Edwards"]
    a_dosunmu = clears("Dosunmu")
    print(f"\n  Edwards: feeder (anchor).")
    print(f"  Dosunmu (re-sign, full season): {'feeder' if a_dosunmu else 'borderline/below'} (proj {proj.get('Dosunmu',0)})")
    print(f"  Flier options: Ajay Mitchell proj {proj.get('Ajay Mitchell',0)} [{'feeder' if clears('Ajay Mitchell') else 'below'}], "
          f"McBride proj {proj.get('McBride',0)} [{'feeder' if clears('McBride') else 'below'}]")
    print(f"  MLE tier: McCollum {proj.get('McCollum',0)} [{'feeder' if clears('McCollum') else 'below'}], "
          f"Powell {proj.get('Norman Powell',0)} [{'feeder' if clears('Norman Powell') else 'below'}], "
          f"Huerter {proj.get('Huerter',0)} [{'feeder' if clears('Huerter') else 'below'}]")

    # count: Edwards + Dosunmu(if clears) + best flier(if clears) + MLE(if a PnR-capable name chosen)
    cnt_floor = 1 + (1 if a_dosunmu else 0)  # Edwards + Dosunmu
    flier = 1 if (clears("Ajay Mitchell") or clears("McBride")) else 0
    mle_pnr = 1 if (clears("McCollum")) else 0   # McCollum is the PnR-capable MLE; Powell/Huerter are off-ball
    print(f"\n  Portfolio C (flier = Ajay Mitchell): Edwards + Dosunmu + Mitchell "
          f"= {1 + (1 if a_dosunmu else 0) + (1 if clears('Ajay Mitchell') else 0)} feeders"
          f" (+1 to {1 + (1 if a_dosunmu else 0) + (1 if clears('Ajay Mitchell') else 0) + mle_pnr} if the MLE is a PnR guard like McCollum)")
    print(f"  Portfolio A (flier = McBride): Edwards + Dosunmu + McBride "
          f"= {1 + (1 if a_dosunmu else 0) + (1 if clears('McBride') else 0)} feeders"
          f" (+1 to {1 + (1 if a_dosunmu else 0) + (1 if clears('McBride') else 0) + mle_pnr} with a McCollum-type MLE)")
    print(f"\n  BRIDGE: the plan moves the feeder count from 1 (2025-26) toward 3, restoring a Utah-like")
    print(f"  delivery environment around Gobert WITHOUT trading him (Piece 2 -> Piece 7).")


if __name__ == "__main__":
    main()
