#!/usr/bin/env python3
"""
analyze_gobert_usage.py -- assemble the final Gobert usage table and the Utah-vs-Minnesota
era comparison for "It's Not All Gobert's Fault".

Reads gobert_usage.csv (pull_gobert_usage.py), adds SCREEN ASSISTS from the warehouse hustle
table (2016-17+), FLAGS the corrupt 2021-22 tracking row (touches/passing halved; excluded from
touch/pass era means but kept for synergy/dunk/delivery), and prints era summaries.

    python analyze_gobert_usage.py
"""
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
from lib import db  # noqa: E402
CACHE = os.path.join(HERE, "..", "data", "cache", "gobert_usage.csv")
OUT = os.path.join(HERE, "..", "data", "cache", "gobert_usage_final.csv")
GOBERT = 203497
pd.set_option("display.width", 280); pd.set_option("display.max_columns", 50)

# 2021-22 tracking (Possessions + Passing) is a partial/corrupt ingest: touches and passes are
# ~halved vs full surrounding seasons despite full gp/minutes. Exclude from touch/pass means.
BAD_TRACK = {"2021-22"}


def q(sql, params=None):
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = 30000")
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


def main():
    df = pd.read_csv(CACHE)

    # ---- screen assists (hustle), per game ----
    sa = q("""SELECT season_year, g sa_gp, screen_assists, screen_ast_pts
              FROM nba_player_hustle_stats_season
              WHERE player_id=%s AND season_type='Regular Season'
              ORDER BY season_year""", (GOBERT,))
    sa["screen_ast_pg"] = (pd.to_numeric(sa["screen_assists"]) / sa["sa_gp"].clip(lower=1)).round(2)
    df = df.merge(sa[["season_year", "screen_assists", "screen_ast_pg"]], on="season_year", how="left")

    # mark the corrupt tracking row, blank its touch/pass-derived fields for the means
    df["track_ok"] = ~df["season_year"].isin(BAD_TRACK)

    cols = ["season_year", "era", "gp", "mpg",
            "roll_poss_pg", "roll_ppp", "roll_poss_pct",
            "screen_ast_pg", "touches_pg", "frontct_touches_pg", "dunk_fga_pg", "dunk_fg",
            "deliv_meaningful", "deliv_primary", "top_bh", "top_bh_poss", "track_ok"]
    df = df[cols]
    df.to_csv(OUT, index=False)
    print("=== GOBERT USAGE, FINAL (warehouse; 2021-22 touches/screen flagged corrupt) ===")
    print(df.to_string(index=False))

    # ---- era summaries ----
    # Utah "prime starter" window = 2016-17..2021-22 (he became a full-time starter ~2016-17).
    # Minnesota = 2022-23..2025-26. Touch/pass means exclude corrupt 2021-22 and missing 2020-21.
    uta_prime = df[(df.era == "Utah") & (df.season_year >= "2016-17")]
    minn = df[df.era == "Minnesota"]

    def summ(d, label):
        dt = d[d.track_ok]  # touch fields only from clean tracking rows
        print(f"\n  [{label}]  (n={len(d)} seasons; touch-means n={len(dt)})")
        print(f"    roll-man poss/game   : {d.roll_poss_pg.mean():.2f}")
        print(f"    roll-man PPP         : {d.roll_ppp.mean():.3f}")
        print(f"    roll-man % of offense: {d.roll_poss_pct.mean()*100:.1f}%")
        print(f"    screen assists/game  : {d.screen_ast_pg.mean():.2f}")
        print(f"    touches/game         : {dt.touches_pg.mean():.1f}")
        print(f"    frontcourt touch/game: {dt.frontct_touches_pg.mean():.1f}")
        print(f"    dunk att/game        : {d.dunk_fga_pg.mean():.2f}  (FG {d.dunk_fg.mean()*100:.1f}%)")
        print(f"    meaningful PnR BHs    : {d.deliv_meaningful.mean():.1f}  (primary {d.deliv_primary.mean():.1f})")

    print("\n=== ERA COMPARISON ===")
    summ(uta_prime, "UTAH prime starter 2016-17..2021-22")
    summ(minn, "MINNESOTA 2022-23..2025-26")

    # deltas on the headline metrics
    print("\n=== HEADLINE DELTAS (Utah prime -> Minnesota) ===")
    for k, lbl, pct in [("roll_poss_pg", "roll-man poss/game", True),
                        ("roll_ppp", "roll-man PPP", False),
                        ("touches_pg", "touches/game (clean)", True),
                        ("screen_ast_pg", "screen assists/game", True),
                        ("dunk_fga_pg", "dunk att/game", True),
                        ("deliv_meaningful", "meaningful PnR ball-handlers", True)]:
        if k == "touches_pg":
            u, m = uta_prime[uta_prime.track_ok][k].mean(), minn[minn.track_ok][k].mean()
        else:
            u, m = uta_prime[k].mean(), minn[k].mean()
        d = m - u
        pc = f" ({d/u*100:+.0f}%)" if pct and u else ""
        print(f"  {lbl:<32}: {u:.2f} -> {m:.2f}   delta {d:+.2f}{pc}")


if __name__ == "__main__":
    main()
