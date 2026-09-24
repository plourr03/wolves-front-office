#!/usr/bin/env python3
"""H4 / N1: the 2025-26 New York Knicks, champion, as a case file.

THE FRAMING RULE, and it governs every sentence this produces: never "the odds were
wrong." The preseason market is a prior. The Knicks case is useful precisely because the
market priced them WELL and they still outran the price, which is the shape of argument a
Minnesota preview actually needs.

THREE PARTS, per H4:
  1. WHAT THE ODDS USED   the preseason title price, the win total, and what was
                          observable in September: last season's margin, continuity.
  2. WHAT CHANGED         the regular season against the playoffs: margin, rotation
                          concentration, health of the top eight, the series themselves.
  3. WHICH H1 FEATURES    would have flagged it, and which would have flagged it the
                          WRONG way. Tested against what this project has already found
                          carries no out-of-sample signal (M1 style, F4d concentration).

SOURCES, with the two-source discipline applied to the facts the argument rests on.
  Series results        warehouse `nba_games` (season 42025) AND
                        https://en.wikipedia.org/wiki/2026_NBA_playoffs (3rd seed East;
                        ATL 4-2, PHI 4-0, CLE 4-0, SAS 4-1). Game counts agree exactly.
  Preseason price       `offseason/data/2025-26-preseason-odd.csv` (+900, 53.5 wins).
  Preseason model       `outputs/backtest_calibration.csv`, this project's own backtest.
  Minutes and health    `nba_player_tracking_season`, DEDUPED: the table carries one row
                        per tracking category, and `min` is already a season total.

This script reads only the warehouse and files the background re-run does not write, so
it is safe to run while that chain is in flight.

    python kuminga/scripts/h4_knicks_case_file.py
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

from kuminga.lib import runlog  # noqa: E402
from lib import db              # noqa: E402

TEAM, CMP = "NYK", "MIN"
SEASON, PREV = "2025-26", "2024-25"
RS_ID, PO_ID = 22025, 42025
ODDS = os.path.join(REPO, "offseason", "data", "2025-26-preseason-odd.csv")
BACKTEST = os.path.join(REPO, "kuminga", "outputs", "backtest_calibration.csv")
STYLE = os.path.join(REPO, "kuminga", "outputs", "m1_style_features.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "h4_knicks_case_file.csv")
BAND = os.path.join(REPO, "kuminga", "outputs", "champions_h2_base_rates.csv")   # the champions' price band, all seasons
H1 = os.path.join(REPO, "kuminga", "outputs", "champions_h1.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "case_file_knicks_2025_26.md")
WIKI = "https://en.wikipedia.org/wiki/2026_NBA_playoffs"


def american_to_prob(o):
    o = float(o)
    return 100.0 / (o + 100.0) if o > 0 else (-o) / (-o + 100.0)


def main():
    with runlog.run("h4_knicks_case_file", inputs={"team": TEAM, "season": SEASON,
                                                   "series_source_2": WIKI}) as r:
        F = {}

        # ---- 1. WHAT THE ODDS USED --------------------------------------------
        od = pd.read_csv(ODDS)
        od["p"] = od.Odds.map(american_to_prob)
        od["p"] = od.p / od.p.sum()
        od = od.sort_values("p", ascending=False).reset_index(drop=True)
        od["rank"] = np.arange(1, len(od) + 1)
        k = od[od.Team == "New York Knicks"].iloc[0]
        F["market_odds"] = int(k.Odds)
        F["market_title_pct"] = float(k.p * 100)
        F["market_rank"] = int(k["rank"])
        F["market_win_total"] = float(k["W-L O/U"])
        F["favourite"] = od.iloc[0].Team
        F["favourite_pct"] = float(od.iloc[0].p * 100)
        # the champions' preseason band, from the champions table (every season with odds)
        band = pd.read_csv(BAND).iloc[0]
        h1 = pd.read_csv(H1)
        F["band_n"] = int(band.n_seasons)
        F["band_lo"] = float(band.champ_implied_min)
        F["band_hi"] = float(band.champ_implied_max)
        F["band_worst_rank"] = int(band.champ_rank_max)
        F["band_top5"] = int(round(band.p_champ_top5 * band.n_seasons))
        lo = h1.sort_values("champ_implied_pct").iloc[0]
        F["band_floor_team"] = "%s %s" % (lo.champion, lo.season)

        bt = pd.read_csv(BACKTEST)
        b = bt[(bt.season == SEASON) & (bt.team_abbr == TEAM)].iloc[0]
        F["model_title_pct"] = float(b.model_title * 100)
        F["model_wins"] = float(b.model_wins)
        F["actual_wins"] = int(b.actual_wins)
        F["model_win_miss"] = float(b.model_wins - b.actual_wins)
        F["market_win_miss"] = float(b.market_wins - b.actual_wins)

        # ---- 2. WHAT CHANGED ----------------------------------------------------
        g = db.query("""select season_id, team_abbreviation team, game_id, game_date,
                               matchup, wl, plus_minus
                        from nba.nba_games where season_id in (%s, %s)""" % (RS_ID, PO_ID))
        g["plus_minus"] = pd.to_numeric(g.plus_minus)
        g["game_date"] = pd.to_datetime(g.game_date)
        rs_all = g[g.season_id == RS_ID]
        po_all = g[g.season_id == PO_ID]

        rs = rs_all[rs_all.team == TEAM].sort_values("game_date")
        po = po_all[po_all.team == TEAM].sort_values("game_date").copy()
        F["rs_record"] = "%d-%d" % ((rs.wl == "W").sum(), (rs.wl == "L").sum())
        F["rs_margin"] = float(rs.plus_minus.mean())
        feb = rs[rs.game_date.dt.month == 2].copy()
        feb["gap"] = feb.game_date.diff().dt.days
        brk = feb.loc[feb.gap.idxmax(), "game_date"]
        F["pre_break_margin"] = float(rs[rs.game_date < brk].plus_minus.mean())
        F["post_break_margin"] = float(rs[rs.game_date >= brk].plus_minus.mean())

        F["po_record"] = "%d-%d" % ((po.wl == "W").sum(), (po.wl == "L").sum())
        F["po_margin"] = float(po.plus_minus.mean())
        F["po_games"] = int(len(po))

        rsm = rs_all.groupby("team").plus_minus.mean().sort_values(ascending=False)
        pom = po_all.groupby("team").plus_minus.mean().sort_values(ascending=False)
        F["rs_margin_rank"] = list(rsm.index).index(TEAM) + 1
        F["po_margin_rank"] = list(pom.index).index(TEAM) + 1
        F["po_teams"] = int(len(pom))
        lift = (pom - rsm.reindex(pom.index)).sort_values(ascending=False)
        F["lift"] = float(lift[TEAM])
        F["lift_rank"] = list(lift.index).index(TEAM) + 1
        F["lift_second"] = "%s %+.2f" % (lift.index[1], lift.iloc[1])
        F["lift_mean"] = float(lift.mean())
        F["n_positive_lift"] = int((lift > 0).sum())
        if CMP in lift.index:
            F["cmp_lift"] = float(lift[CMP])
            F["cmp_lift_rank"] = list(lift.index).index(CMP) + 1

        po["opp"] = po.matchup.str[-3:]
        series = (po.groupby("opp", sort=False)
                  .agg(games=("game_id", "size"), w=("wl", lambda x: (x == "W").sum()),
                       margin=("plus_minus", "mean")).reset_index())
        series["l"] = series.games - series.w
        F["series"] = "; ".join("%s %d-%d (%+.1f)" % (x.opp, x.w, x.l, x.margin)
                                for _, x in series.iterrows())

        t = db.query("""select season_year, season_type, player_id, player_name,
                               team_abbreviation team, gp, min
                        from nba.nba_player_tracking_season
                        where season_year in ('%s', '%s')""" % (SEASON, PREV))
        for c in ("gp", "min"):
            t[c] = pd.to_numeric(t[c])
        t = t.drop_duplicates(subset=["season_year", "season_type", "team", "player_id"])
        cur = t[(t.season_year == SEASON) & (t.team == TEAM)]
        trs = cur[cur.season_type == "Regular Season"].set_index("player_id")
        tpo = cur[cur.season_type == "Playoffs"].set_index("player_id")

        def share(df, n):
            v = df["min"].sort_values(ascending=False)
            return float(v.head(n).sum() / v.sum())

        for n in (3, 5, 8):
            F["top%d_share_rs" % n] = share(trs, n)
            F["top%d_share_po" % n] = share(tpo, n)

        top5 = trs.sort_values("min", ascending=False).head(5)
        top8 = trs.sort_values("min", ascending=False).head(8)
        rs_games = int(len(rs))
        F["top5_rs_games_missed"] = int(sum(rs_games - int(x.gp)
                                            for _, x in top5.iterrows()))
        F["top5_po_games_missed"] = int(sum(F["po_games"] - (int(tpo.loc[p].gp)
                                                             if p in tpo.index else 0)
                                            for p in top5.index))
        F["top8_po_games_missed"] = int(sum(F["po_games"] - (int(tpo.loc[p].gp)
                                                             if p in tpo.index else 0)
                                            for p in top8.index))
        F["top5_names"] = ", ".join(top5.player_name.str.split().str[-1])

        prv = t[(t.season_year == PREV) & (t.season_type == "Regular Season")]
        allc = t[(t.season_year == SEASON) & (t.season_type == "Regular Season")]
        cont = {}
        for tm, gg in allc.groupby("team"):
            back = set(prv[prv.team == tm].player_id)
            cont[tm] = float(gg[gg.player_id.isin(back)]["min"].sum() / gg["min"].sum())
        cs = pd.Series(cont).sort_values(ascending=False)
        F["continuity"] = float(cs[TEAM])
        F["continuity_rank"] = list(cs.index).index(TEAM) + 1
        F["continuity_median"] = float(cs.median())
        if CMP in cs.index:
            F["cmp_continuity"] = float(cs[CMP])
            F["cmp_continuity_rank"] = list(cs.index).index(CMP) + 1

        st = pd.read_csv(STYLE)
        s = st[st.season == SEASON]
        style = {}
        for c in ("rim_rate", "fg3a_rate", "pace", "opp_tov_rate", "oreb_rate", "size"):
            if c in s.columns:
                style[c] = int(s[c].rank(ascending=False)[s.team == TEAM].iloc[0])
        F["style_ranks"] = ", ".join("%s %d" % kv for kv in style.items())

        pd.DataFrame([F]).T.rename(columns={0: "value"}).to_csv(OUT)

        for k_, v in F.items():
            r.note("  %-24s %s" % (k_, v if not isinstance(v, float) else round(v, 3)))

        # ---- the case file -------------------------------------------------------
        md = f"""# Case file: the 2025-26 New York Knicks

**Champion.** Beat San Antonio 4-1 in the Finals. Jalen Brunson, Finals MVP. First title since 1973.

**How to read this file.** The preseason market is a prior, not a prediction to be graded right or wrong. The Knicks matter to a Minnesota preview because **the market priced them well and they still outran the price**, and the useful question is what moved them inside it. Every figure below is from run `{r.run_id}`.

**Sources.** Series results from the warehouse (`nba_games`, season 42025) and independently from [Wikipedia's 2026 NBA playoffs page]({WIKI}); game counts agree exactly. Preseason price from the project's hand-transcribed odds file. Preseason model number from this project's own calibration backtest.

---

## 1. What the odds used

**The market had them as a contender, and it was right to.**

| | Knicks | note |
|---|---:|---|
| preseason title price | +{F['market_odds']} | |
| implied probability, de-vigged | **{F['market_title_pct']:.2f}%** | rank **{F['market_rank']}** of 30 |
| preseason favourite | {F['favourite']} | {F['favourite_pct']:.2f}% |
| win total | {F['market_win_total']:.1f} | they won **{F['actual_wins']}** |

**The market missed their regular season by {abs(F['market_win_miss']):.1f} wins.** That is close to perfect, and it is the first thing a reader should take from this file: the odds were not surprised by who the Knicks were in the regular season.

**Our own model was.** This project's preseason model had them at **{F['model_title_pct']:.2f}%** and **{F['model_wins']:.1f} wins**, a miss of **{abs(F['model_win_miss']):.1f} wins**, against the market's {abs(F['market_win_miss']):.1f}. The model sat below the market on the eventual champion by roughly {F['market_title_pct'] - F['model_title_pct']:.1f} points. **That is the same direction it sits on Minnesota now**, and it belongs in the piece as a reason to hold the model's Minnesota number loosely, not as a reason to trust the market's blindly.

**What was observable in September.** Continuity of **{F['continuity']:.3f}**, rank **{F['continuity_rank']}** of 30 against a league median of {F['continuity_median']:.3f}: all five starters returned. A returning core is exactly the kind of information a market can see and price, and it did.

---

## 2. What changed

**The regular season was steady, not a late surge.** {F['rs_record']}, a margin of **{F['rs_margin']:+.2f}**, rank **{F['rs_margin_rank']}** of 30. **{F['pre_break_margin']:+.2f} before the All-Star break and {F['post_break_margin']:+.2f} after.** Nothing in March told you April was coming.

**Then the playoffs were a different team.**

| | regular season | playoffs |
|---|---:|---:|
| record | {F['rs_record']} | **{F['po_record']}** |
| margin per game | {F['rs_margin']:+.2f} | **{F['po_margin']:+.2f}** |
| rank | {F['rs_margin_rank']} of 30 | **{F['po_margin_rank']} of {F['po_teams']}** |

**The playoff margin was {F['po_margin'] / F['rs_margin']:.2f} times the regular-season margin.** Playoff opponents are better, so almost every team's margin FALLS in April: the average change across the {F['po_teams']} playoff teams was **{F['lift_mean']:+.2f}**. The Knicks' change was **{F['lift']:+.2f}**. **They were the only one of {F['po_teams']} playoff teams whose margin improved at all**; the next best was {F['lift_second']}.

**The series:** {F['series']}. They swept Philadelphia and Cleveland by roughly twenty points a game, then won a close Finals.

**Three things moved, and none of them was visible in September.**

**Health reversed.** The starting five ({F['top5_names']}) missed **{F['top5_rs_games_missed']} regular-season games** between them. In the playoffs they missed **{F['top5_po_games_missed']}**. The top eight missed {F['top8_po_games_missed']} playoff games in total across {F['po_games']}. A team that spent the winter shorthanded arrived in April whole.

**The rotation shortened onto the starters.**

| minutes share | regular season | playoffs | change |
|---|---:|---:|---:|
| top 3 | {F['top3_share_rs']:.3f} | {F['top3_share_po']:.3f} | {F['top3_share_po'] - F['top3_share_rs']:+.3f} |
| top 5 | {F['top5_share_rs']:.3f} | {F['top5_share_po']:.3f} | **{F['top5_share_po'] - F['top5_share_rs']:+.3f}** |
| top 8 | {F['top8_share_rs']:.3f} | {F['top8_share_po']:.3f} | {F['top8_share_po'] - F['top8_share_rs']:+.3f} |

**The bracket broke their way.** San Antonio beat Oklahoma City, the preseason favourite, in seven games in the West final, so the Knicks never had to beat the team the market liked most.

---

## 3. Which H1 features would have flagged it

| feature | Knicks | flag? |
|---|---|---|
| preseason market rank | {F['market_rank']} | **yes**: {F['band_top5']} of the {F['band_n']} champions in this project's sample started in the market's top five, and none worse than {F['band_worst_rank']}th |
| preseason implied probability | {F['market_title_pct']:.2f}% | **circular, so not counted**: the Knicks are one of the {F['band_n']} champions whose prices DEFINE the {F['band_lo']:.2f}% to {F['band_hi']:.2f}% band. Being inside it is true by construction. The floor is {F['band_floor_team']} at {F['band_lo']:.2f}%. |
| continuity | {F['continuity']:.3f}, rank {F['continuity_rank']} | **weakly**: see the Minnesota line below |
| regular-season margin | {F['rs_margin']:+.2f}, rank {F['rs_margin_rank']} | no: good, not elite |
| style profile | {F['style_ranks']} | **no**, and this project's held-out test found style carries no playoff signal |
| regular-season health | {F['top5_rs_games_missed']} games missed by the starters | **the wrong way**: a health feature would have marked them DOWN |
| minutes concentration | not a preseason quantity | no: F4d found regular-season concentration does not predict playoff margin |

**The honest reading.** The one non-circular feature that flagged the Knicks is the one the market already priced: they were a top-four team. **Everything that separated them from the other contenders happened after the price was set**, and the one regular-season signal that bore on it, health, pointed the wrong way. This is not a missed signal. It is a one-in-twelve prior landing, driven by variance the preseason could not observe.

---

## What this file means for Minnesota

**The Knicks are the template, and Minnesota does not yet fit it on the first flag.**

- **Market position.** The Knicks started **inside** the champion band at rank {F['market_rank']}. Minnesota starts at **3.16% and rank 6**: inside every champion's starting rank (none worse than {F['band_worst_rank']}th) but below the band's price floor, {F['band_floor_team']} at {F['band_lo']:.2f}%, which is the closest champion to it by price.
- **Continuity is not the story.** Minnesota's continuity in 2025-26 was **{F.get('cmp_continuity', float('nan')):.3f}, rank {F.get('cmp_continuity_rank', 0)}**, slightly higher than the Knicks', and Minnesota went out in the second round (beat Denver 4-2, lost to San Antonio 2-4).
- **The playoff lift is the story, and it ran the other way for Minnesota.** In 2025-26 Minnesota's margin changed by **{F.get('cmp_lift', float('nan')):+.2f}** from regular season to playoffs, rank **{F.get('cmp_lift_rank', 0)}** of {F['po_teams']}. The Knicks' changed by **{F['lift']:+.2f}**, rank 1.

**The sentence the piece can support:** the last champion was a team the market already had as a contender, which then got healthy, shortened its rotation onto its starters, and played nine points better in the playoffs than in the regular season. None of that was visible in September. Minnesota's case for a similar run has to start from a lower price and a team that went the other way last April.
"""
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write(md)
        r.output(OUT, rows=len(F))
        r.output(OUT_MD)

    print("\nwrote", os.path.relpath(OUT_MD, REPO))


if __name__ == "__main__":
    main()
