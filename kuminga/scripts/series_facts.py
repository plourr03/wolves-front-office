#!/usr/bin/env python3
"""The narrative facts the series prose asserts that are not model figures: records, series
results, draft slots, injury dates. Each is recomputed from the warehouse (or from a frozen
source table) so the articles' non-model numbers are checkable too, not taken on trust.

Writes `outputs/series_facts.csv` (key, value, basis) with a run ID. `audit_series.py` binds
the prose to these keys the same way it binds model figures to the sheet.

    python kuminga/scripts/series_facts.py
"""
from __future__ import annotations

import collections
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from kuminga.lib import runlog  # noqa: E402
from lib import db              # noqa: E402

OUT = os.path.join(REPO, "kuminga", "outputs", "series_facts.csv")
MIN_ID = 1610612750
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}


def main():
    with runlog.run("series_facts", inputs={"team": MIN_ID}) as r:
        rows = []

        def F(key, value, basis):
            rows.append(dict(key=key, value=str(value), basis=basis))

        # ---- Minnesota's 2025-26 season and playoff path -----------------------------
        rec = db.query("select sum(case when wl='W' then 1 else 0 end) w, sum(case when wl='L' then 1 else 0 end) l "
                       "from nba.nba_games where team_id=%(t)s and season_id=22025", {"t": MIN_ID}).iloc[0]
        F("min_wins_2025_26", int(rec.w), "nba_games, regular season 2025-26")
        F("min_losses_2025_26", int(rec.l), "nba_games, regular season 2025-26")
        po = db.query("select game_date, matchup, wl from nba.nba_games where team_id=%(t)s and season_id=42025 "
                      "order by game_date", {"t": MIN_ID})
        po["game_date"] = pd.to_datetime(po.game_date)
        po["opp"] = po.matchup.str.extract(r"(\w{3})$")
        for opp, g in po.groupby("opp", sort=False):
            w, l = int((g.wl == "W").sum()), int((g.wl == "L").sum())
            F("min_2026_%s_games" % opp.lower(), len(g), "nba_games, 2026 playoffs")
            F("min_2026_%s_games_word" % opp.lower(), WORDS[len(g)], "nba_games, 2026 playoffs")
            F("min_2026_%s_record" % opp.lower(), "%d-%d" % (w, l), "nba_games, 2026 playoffs")
            r.note("MIN vs %s, 2026 playoffs: %d-%d in %d games, %s to %s" % (
                opp, w, l, len(g), g.game_date.min().strftime("%b %d"), g.game_date.max().strftime("%b %d")))
        F("season_end_2026", po.game_date.max().strftime("%Y-%m-%d"), "not used; see finals_end")
        # DiVincenzo's Achilles: which game of the Denver series
        inj = pd.read_csv(os.path.join(REPO, "kuminga", "data", "injuries_2026_27.csv"))
        d_inj = pd.Timestamp(inj[inj.player == "Donte DiVincenzo"].injury_date.iloc[0])
        den = po[po.opp == "DEN"].reset_index(drop=True)
        gm = den.index[den.game_date == d_inj]
        assert len(gm) == 1, "the injury date is not a Denver series game date"
        F("ddv_injury_game", int(gm[0]) + 1, "injuries_2026_27.csv date against the 2026 Denver series schedule")
        F("ddv_injury_game_word", WORDS[int(gm[0]) + 1], "same")
        F("ddv_injury_series_result", "%d-%d" % (int((den.wl == "W").sum()), int((den.wl == "L").sum())),
          "nba_games, 2026 first round")
        r.note("DiVincenzo's Achilles (%s) was game %d of the Denver series, which MIN won %s"
               % (d_inj.date(), int(gm[0]) + 1, rows[-1]["value"]))

        # ---- every Finals, 2015-16 through 2025-26 ------------------------------------
        d = db.query("select season_id, game_id, game_date, team_abbreviation t, wl from nba.nba_games "
                     "where season_type='Playoffs' and season_id>=42015 order by season_id, game_date")
        d["game_date"] = pd.to_datetime(d.game_date)
        for sid, g in d.groupby("season_id"):
            season = "%d-%s" % (sid - 40000, str(sid - 40000 + 1)[2:])
            last = g[g.game_date == g.game_date.max()]
            a, b = sorted(set(last.t))
            pair = g[g.t.isin([a, b])]
            ids = pair.groupby("game_id").t.nunique()
            fin = pair[pair.game_id.isin(ids[ids == 2].index)]
            tal = collections.Counter(fin[fin.wl == "W"].t)
            champ, runner = (a, b) if tal[a] > tal[b] else (b, a)
            n = fin.game_id.nunique()
            F("finals_%s_champion" % season, champ, "nba_games, last series of the playoffs")
            F("finals_%s_runner_up" % season, runner, "same")
            F("finals_%s_games" % season, n, "same")
            F("finals_%s_games_word" % season, WORDS[n], "same")
            F("finals_%s_record" % season, "%d-%d" % (tal[champ], tal[runner]), "same")
            F("finals_%s_end" % season, fin.game_date.max().strftime("%Y-%m-%d"), "same")
            # the champion's own full playoff record that spring
            own = g[g.t == champ]
            F("po_record_%s_%s" % (season, champ), "%d-%d" % (int((own.wl == "W").sum()), int((own.wl == "L").sum())),
              "nba_games, all playoff games")
            F("po_losses_%s_%s" % (season, champ), int((own.wl == "L").sum()), "same")
            F("po_losses_word_%s_%s" % (season, champ), WORDS.get(int((own.wl == "L").sum()), str(int((own.wl == "L").sum()))), "same")
            # was the champion ever three games to one down in the Finals?
            seq = fin[fin.t == champ].sort_values("game_date").wl.tolist()
            trailed31 = any(seq[:i].count("L") == 3 and seq[:i].count("W") == 1 for i in range(4, len(seq) + 1))
            F("finals_%s_champ_trailed_3_1" % season, "yes" if trailed31 else "no", "same")
            F("finals_%s_champ_lost_first_two" % season, "yes" if seq[:2] == ["L", "L"] else "no", "same")
        r.note("finals: " + "; ".join("%s %s beat %s %s" % (k.split("_")[1], v, "", "") for k, v in
                                      [(x["key"], x["value"]) for x in rows if x["key"].endswith("_champion")]))

        # ---- draft slots the prose names ---------------------------------------------
        for name, pid in (("cody_williams", 1642262), ("isaiah_evans", 1642912), ("joshua_jefferson", None),
                          ("trey_kaufman_renn", None)):
            if pid is None:
                continue
            b = db.query("select draft_year, draft_round, draft_number from nba.nba_player_bio where player_id=%(p)s",
                         {"p": pid})
            if len(b) and str(b.draft_number.iloc[0]).isdigit():
                F("draft_%s_pick" % name, int(b.draft_number.iloc[0]), "nba_player_bio")
                F("draft_%s_year" % name, str(b.draft_year.iloc[0]), "nba_player_bio")
        # the 2026 picks from the cached Basketball-Reference draft page
        from bs4 import BeautifulSoup
        from kuminga.lib import bref
        soup = BeautifulSoup(bref.strip_comments(bref.fetch("/draft/NBA_2026.html")), "lxml")
        for tr in soup.find("table", id="stats").tbody.find_all("tr"):
            pl = tr.find("td", {"data-stat": "player"})
            if pl is None or not pl.find("a"):
                continue
            nm = pl.get_text(strip=True)
            if nm in ("Joshua Jefferson", "Trey Kaufman-Renn", "Isaiah Evans"):
                key = nm.lower().replace(" ", "_").replace("-", "_")
                F("draft_%s_pick" % key, int(tr.find("td", {"data-stat": "pick_overall"}).get_text(strip=True)),
                  "Basketball-Reference 2026 draft page (cached)")
                F("draft_%s_team" % key, tr.find("td", {"data-stat": "team_id"}).get_text(strip=True), "same")

        # ---- Minnesota's roster count on the current book -----------------------------
        v3 = pd.read_csv(os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_v3.csv"))
        v3 = v3[(v3.team_abbr == "MIN") & v3.status.isin(["standard", "pending", "non_guaranteed"])]
        F("min_roster_count", len(v3), "roster_snapshot_2026_27_v3.csv, standard plus pending")
        F("min_roster_count_word", {14: "fourteen", 15: "fifteen"}.get(len(v3), str(len(v3))), "same")

        # ---- Ball's games in the seasons before the trade -----------------------------
        h = pd.read_csv(os.path.join(REPO, "kuminga", "outputs", "c3_ball_history.csv"))
        prior3 = int(h[h.season.isin(["2022-23", "2023-24", "2024-25"])].games_played.sum())
        prior4 = int(h[h.season.isin(["2021-22", "2022-23", "2023-24", "2024-25"])].games_played.sum())
        F("ball_games_prior_three", prior3, "c3_ball_history.csv, 2022-23 to 2024-25")
        F("ball_games_prior_four", prior4, "c3_ball_history.csv, 2021-22 to 2024-25")
        F("ball_games_prior_four_mean", round(prior4 / 4.0, 1), "same")
        F("ball_games_career_mean", round(float(h.games_played.sum()) / len(h), 1), "c3_ball_history.csv, six seasons")
        r.note("Ball: %d games in the three seasons before 2025-26, %d in the four (mean %.1f), career mean %.1f"
               % (prior3, prior4, prior4 / 4.0, float(h.games_played.sum()) / len(h)))

        # ---- the Edwards games gap the supermax turns on ------------------------------
        sheet = pd.read_csv(os.path.join(REPO, "kuminga", "outputs", "final_numbers.csv"), dtype=str).set_index("key")
        gap = int(sheet.loc["c2_games_rule", "value"]) - int(sheet.loc["c2_games_2025_26", "value"])
        F("edwards_games_short", gap, "c2_games_rule minus c2_games_2025_26")
        F("edwards_games_short_word", WORDS[gap], "same")

        # ---- what shaving Kuminga's first year to fit under the hard cap would cost ----
        # He signed the taxpayer MLE exactly: year one, then a 5% raise. To fit under the
        # wall without the Green trade he would have had to give back the whole overage in
        # year one, which also shrinks the raise.
        y1 = int(sheet.loc["k_y1", "value"].replace("$", "").replace(",", ""))
        y2 = int(sheet.loc["k_y2", "value"].replace("$", "").replace(",", ""))
        over = int(sheet.loc["dos_stuck_over", "value"].replace("$", "").replace(",", ""))
        raise_pct = y2 / y1
        cost = over * (1 + raise_pct)
        F("kuminga_shave_cost", "$%s" % "{:,.0f}".format(cost), "dos_stuck_over x (1 + k_y2/k_y1)")
        F("kuminga_shave_cost_m", "$%.1f million" % (cost / 1e6), "same")
        r.note("Kuminga shaving the overage would have cost him $%s over the two years (raise %.3f)"
               % ("{:,.0f}".format(cost), raise_pct))

        df = pd.DataFrame(rows)
        assert df.key.is_unique, "duplicate fact key"
        df.to_csv(OUT, index=False)
        r.note("%d narrative facts written" % len(df))
        r.output(OUT, rows=len(df))


if __name__ == "__main__":
    main()
