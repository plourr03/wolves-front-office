"""The Bet series additions on the final-numbers sheet (C1 to C4).

Called from `build_final_numbers.py` with its own `F`, `rid` and `csv` helpers, so every
figure the series prose quotes from the champions table, the Edwards clock, Ball's games
and the ledger is on the one sheet with a run ID, and the prose gate can find it there.
Keys are prefixed c1_ to c4_ by item.
"""
from __future__ import annotations

import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "outputs")
S = "C. The bet: additions for Parts 1, 3 and 4"
FORKS = ["consensus", "rapm", "box", "darko"]


def pct(v, n=2):
    return ("%." + str(n) + "f%%") % v


def money(v):
    return "$" + "{:,.0f}".format(v)


def millions(v):
    return "$%.1f million" % (v / 1e6)


def season_key(s):
    return str(s).replace("-", "_")


def add(F, rid, csv):
    # ---------------- C2: the Edwards clock --------------------------------------------
    r2 = rid("c2_edwards_clock")
    T = csv("c2_edwards_clock.csv")
    for scen, tag in (("win600", "600"), ("win450", "450")):
        x = T[T.scenario == scen].set_index("model_season")
        for yr in (2027, 2028, 2029, 2033):
            F("c2_haz_%d_%s" % (yr, tag), S, "Edwards departure hazard, %s season, team at .%s" % (x.loc[yr].season, tag),
              pct(100 * x.loc[yr].hazard, 1 if x.loc[yr].hazard < 0.095 else 0), "MODELED", "QUOTABLE AS BAND", r2, "c2_edwards_clock.csv")
            F("c2_haz_%d_%s_band" % (yr, tag), S, "80%% interval" , "%s to %s" % (
                pct(100 * x.loc[yr].hazard_lo80, 1 if x.loc[yr].hazard_lo80 < 0.095 else 0),
                pct(100 * x.loc[yr].hazard_hi80, 1 if x.loc[yr].hazard_hi80 < 0.095 else 0)), "MODELED", "QUOTABLE AS BAND", r2, "c2_edwards_clock.csv")
        for yr in (2029, 2033):
            F("c2_cum_%d_%s" % (yr, tag), S, "P(Edwards departed by %s), team at .%s" % (x.loc[yr].season, tag),
              pct(100 * x.loc[yr].cumulative, 0), "MODELED", "QUOTABLE AS BAND", r2, "c2_edwards_clock.csv")
            F("c2_cum_%d_%s_band" % (yr, tag), S, "80%% interval", "%s to %s" % (
                pct(100 * x.loc[yr].cumulative_lo80, 0), pct(100 * x.loc[yr].cumulative_hi80, 0)), "MODELED", "QUOTABLE AS BAND", r2, "c2_edwards_clock.csv")
    hi, lo = T[T.scenario == "win600"].team_win_pct_2yr.iloc[0], T[T.scenario == "win450"].team_win_pct_2yr.iloc[0]
    F("c2_scen_high", S, "central scenario, team two-year win percentage", ("%.3f" % hi).lstrip("0"), "MODELED", "DESCRIPTIVE", r2, "c2_edwards_clock.csv")
    F("c2_scen_low", S, "decline scenario, team two-year win percentage", ("%.3f" % lo).lstrip("0"), "MODELED", "DESCRIPTIVE", r2, "c2_edwards_clock.csv")
    F("c2_first_season", S, "first season in the star-spells data", 1990, "OBSERVED", "DESCRIPTIVE", r2, "c2_star_spell_seasons_with_contract.csv")
    F("c2_calib_window", S, "calibration slope window set in advance", "0.8 to 1.2", "MODELED", "DESCRIPTIVE", r2, "c2_model_b_hazard_M2_FINAL.md")
    F("c2_cba_year", S, "the collective bargaining agreement quoted", 2023, "OBSERVED", "DESCRIPTIVE", r2, "c2_cba_2023.pdf")
    Sg = csv("c2_stage_departures.csv")
    st3 = Sg[(Sg.stage == "two seasons left after this one") & (Sg.horizon == "within 3 seasons")].set_index("tier")
    wy = Sg[Sg.stage == "walk year"].set_index("tier")
    F("c2_raw_stage_n", S, "star-seasons with two seasons left, within-three window observed", int(st3.loc["all", "n"]), "OBSERVED", "QUOTABLE", r2, "c2_stage_departures.csv")
    F("c2_raw_within3", S, "of those, departed within three seasons", pct(100 * st3.loc["all", "rate"], 0), "OBSERVED", "QUOTABLE", r2, "c2_stage_departures.csv")
    F("c2_raw_walk_all", S, "walk-year departure rate, all star-seasons", pct(100 * wy.loc["all", "rate"], 0), "OBSERVED", "QUOTABLE", r2, "c2_stage_departures.csv")
    F("c2_raw_walk_all_n", S, "walk-year star-seasons", int(wy.loc["all", "n"]), "OBSERVED", "QUOTABLE", r2, "c2_stage_departures.csv")
    F("c2_raw_walk_600", S, "walk-year departure rate, team at .600 or better", pct(100 * wy.loc[".600 or better", "rate"], 0), "OBSERVED", "QUOTABLE", r2, "c2_stage_departures.csv")
    F("c2_raw_walk_600_n", S, "cases", int(wy.loc[".600 or better", "n"]), "OBSERVED", "QUOTABLE", r2, "c2_stage_departures.csv")
    F("c2_raw_walk_sub500", S, "walk-year departure rate, team under .500", pct(100 * wy.loc["under .500", "rate"], 0), "OBSERVED", "QUOTABLE", r2, "c2_stage_departures.csv")
    F("c2_raw_walk_sub500_n", S, "cases", int(wy.loc["under .500", "n"]), "OBSERVED", "QUOTABLE", r2, "c2_stage_departures.csv")
    fx = csv("c2_facts.csv").set_index("key").value
    F("c2_n_spells", S, "star spells in the Part 1 model", int(fx["n_spells"]), "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_n_rows", S, "player-seasons", "{:,}".format(int(fx["n_rows"])), "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_n_departures", S, "departures", int(fx["n_departures"]), "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_walk_multiple", S, "walk-year odds multiple against two seasons left (from the M2 coefficient)", "%.0f" % float(fx["walk_multiple"]), "MODELED", "QUOTABLE AS BAND", r2, "c2_facts.csv")
    F("c2_c_index", S, "Model B C-index on the sealed holdout", fx["c_index"], "MODELED", "DESCRIPTIVE", r2, "c2_facts.csv")
    F("c2_calibration", S, "Model B calibration slope (window 0.8 to 1.2, failed and printed)", fx["calibration_slope"], "MODELED", "DESCRIPTIVE", r2, "c2_facts.csv")
    for k in ("2026_27", "2027_28", "2028_29"):
        F("c2_salary_%s" % k, S, "Edwards salary %s" % k.replace("_", "-"), money(int(fx["salary_%s" % k])), "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
        F("c2_salary_%s_m" % k, S, "Edwards salary %s, rounded" % k.replace("_", "-"), millions(int(fx["salary_%s" % k])), "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_ext_signed", S, "rookie scale extension signed", fx["ext_signed"], "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_ext_window", S, "standard extension window opened (third anniversary)", "2026-07-08", "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_games_2025_26", S, "Edwards regular-season games 2025-26", int(fx["games_2025_26"]), "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_games_rule", S, "games required for All-NBA eligibility (Art. XXIX Sec. 6)", 65, "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_walk_year", S, "walk year", fx["walk_year"], "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_free_agency", S, "unrestricted free agency", fx["free_agency"], "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_dvpe_window", S, "designated veteran extension window (if All-NBA 2026-27)", "July 2027", "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_dvpe_last", S, "last extension window before free agency (needs All-NBA 2027-28)", "July 2028", "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_std_ext_reported", S, "standard extension available now, as reported", "two years, about $122 million", "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")
    F("c2_supermax_reported", S, "designated veteran extension as reported", "four years, about $300 million", "OBSERVED", "QUOTABLE", r2, "c2_facts.csv")

    # ---------------- C3: Ball's games --------------------------------------------------
    r3 = rid("c3_ball_games")
    H = csv("c3_ball_history.csv")
    for _, x in H.iterrows():
        k = season_key(x.season)
        F("c3_games_%s" % k, S, "Ball games played %s" % x.season, int(x.games_played), "OBSERVED", "QUOTABLE", r3, "c3_ball_history.csv")
        F("c3_team_games_%s" % k, S, "team games %s" % x.season, int(x.team_games), "OBSERVED", "QUOTABLE", r3, "c3_ball_history.csv")
        F("c3_share_%s" % k, S, "share of team games %s" % x.season, pct(100 * x.share, 0), "OBSERVED", "QUOTABLE", r3, "c3_ball_history.csv")
        F("c3_missed_%s" % k, S, "games missed %s" % x.season, int(x.games_missed), "OBSERVED", "QUOTABLE", r3, "c3_ball_history.csv")
    F("c3_mpa_2025_26", S, "Ball minutes per appearance 2025-26", "%.1f" % H[H.season == "2025-26"].mpg_per_appearance.iloc[0], "OBSERVED", "QUOTABLE", r3, "c3_ball_history.csv")
    F("c3_games_total", S, "Ball games played, six seasons", int(H.games_played.sum()), "OBSERVED", "QUOTABLE", r3, "c3_ball_history.csv")
    F("c3_team_games_total", S, "team games, six seasons", int(H.team_games.sum()), "OBSERVED", "QUOTABLE", r3, "c3_ball_history.csv")
    F("c3_missed_total", S, "games missed, six seasons", int(H.games_missed.sum()), "OBSERVED", "QUOTABLE", r3, "c3_ball_history.csv")
    F("c3_share_total", S, "share of team games, six seasons", pct(100 * H.games_played.sum() / H.team_games.sum(), 0), "OBSERVED", "QUOTABLE", r3, "c3_ball_history.csv")
    St = csv("c3_ball_missed_stretches.csv")
    F("c3_stretches", S, "missed stretches", len(St), "OBSERVED", "QUOTABLE", r3, "c3_ball_missed_stretches.csv")
    F("c3_stretches_sourced", S, "stretches with a sourced cause", int(St.cause.notna().sum()), "OBSERVED", "QUOTABLE", r3, "c3_ball_missed_stretches.csv")
    F("c3_surgeries", S, "stretches that ended in surgery", int(St.surgery.astype(str).str.startswith("yes").sum()), "OBSERVED", "QUOTABLE", r3, "c3_ball_missed_stretches.csv")
    B = csv("c3_base_rate_summary.csv")
    for _, x in B.iterrows():
        tag = x.cohort.split(":")[0].strip().lower()
        F("c3_%s_n" % tag, S, "base rate %s: player-seasons" % x.cohort, int(x.player_seasons), "OBSERVED", "QUOTABLE", r3, "c3_base_rate_summary.csv")
        F("c3_%s_players" % tag, S, "players", int(x.players), "OBSERVED", "QUOTABLE", r3, "c3_base_rate_summary.csv")
        F("c3_%s_mean" % tag, S, "mean games", "%.1f" % x.mean_games, "OBSERVED", "QUOTABLE", r3, "c3_base_rate_summary.csv")
        F("c3_%s_median" % tag, S, "median games", "%.1f" % x.median_games, "OBSERVED", "QUOTABLE", r3, "c3_base_rate_summary.csv")
        F("c3_%s_p50" % tag, S, "P(50 or more)", pct(100 * x.p_ge_50, 0), "OBSERVED", "QUOTABLE", r3, "c3_base_rate_summary.csv")
        F("c3_%s_p60" % tag, S, "P(60 or more)", pct(100 * x.p_ge_60, 0), "OBSERVED", "QUOTABLE", r3, "c3_base_rate_summary.csv")
        F("c3_%s_p70" % tag, S, "P(70 or more)", pct(100 * x.p_ge_70, 0), "OBSERVED", "QUOTABLE", r3, "c3_base_rate_summary.csv")
        F("c3_%s_pall" % tag, S, "P(all games)", pct(100 * x.p_all, 0), "OBSERVED", "QUOTABLE", r3, "c3_base_rate_summary.csv")
        F("c3_%s_p40" % tag, S, "P(40 or fewer)", pct(100 * x.p_le_40, 0), "OBSERVED", "QUOTABLE", r3, "c3_base_rate_summary.csv")
    F("c3_def_share", S, "base rate definition: a bad season is at most this share of team games", "60%", "OBSERVED", "DESCRIPTIVE", r3, "c3_base_rate_summary.csv")
    F("c3_def_seasons", S, "bad seasons required of the five prior", 3, "OBSERVED", "DESCRIPTIVE", r3, "c3_base_rate_summary.csv")
    F("c3_def_age", S, "age band", "23 to 27", "OBSERVED", "DESCRIPTIVE", r3, "c3_base_rate_summary.csv")
    F("c3_def_mpa", S, "minutes per appearance the season before, at least", 24, "OBSERVED", "DESCRIPTIVE", r3, "c3_base_rate_summary.csv")
    F("c3_def_healthy", S, "healthy prior season, at least this share", "80%", "OBSERVED", "DESCRIPTIVE", r3, "c3_base_rate_summary.csv")
    F("c3_def_first", S, "first season in the base rate", "2001-02", "OBSERVED", "DESCRIPTIVE", r3, "c3_base_rate_summary.csv")
    for basis, fn, tag in (("unaged", "c3_ball_availability.csv", "u"), ("aged", "c3_ball_availability_AGED.csv", "a")):
        rs = rid("c3_ball_availability", basis)
        A = csv(fn)
        M = csv(fn.replace("availability", "minutes"))
        for games, d in A.groupby("games"):
            F("c3_title_%d_%s" % (games, tag), S, "MIN title odds with Ball at %d games, mean of views (%s)" % (games, basis), pct(d.title.mean()), "MODELED", "QUOTABLE AS BAND", rs, fn)
            F("c3_title_%d_%s_band" % (games, tag), S, "band across views", "%s to %s" % (pct(d.title.min()), pct(d.title.max())), "MODELED", "QUOTABLE AS BAND", rs, fn)
            F("c3_title_drop_%d_%s" % (games, tag), S, "drop from 82 games, points", "%.2f" % d.title_drop_pp.mean(), "MODELED", "QUOTABLE AS BAND", rs, fn)
            F("c3_top6_%d_%s" % (games, tag), S, "P(top six) with Ball at %d games (%s)" % (games, basis), pct(d.top6.mean(), 1), "MODELED", "QUOTABLE AS BAND", rs, fn)
            F("c3_top6_%d_%s_band" % (games, tag), S, "band across views", "%s to %s" % (pct(d.top6.min(), 1), pct(d.top6.max(), 1)), "MODELED", "QUOTABLE AS BAND", rs, fn)
            F("c3_top6_drop_%d_%s" % (games, tag), S, "P(top six) drop from 82 games, points", "%.1f" % d.top6_drop_pp.mean(), "MODELED", "QUOTABLE AS BAND", rs, fn)
            F("c3_seed_%d_%s" % (games, tag), S, "mean West seed", "%.2f" % d.mean_seed.mean(), "MODELED", "QUOTABLE AS BAND", rs, fn)
            F("c3_net_drop_%d_%s" % (games, tag), S, "regular-season net lost, mean of views", "%.2f" % (d.net_full - d.net_rs).mean(), "MODELED", "QUOTABLE AS BAND", rs, fn)
            F("c3_ball_mpg_%d_%s" % (games, tag), S, "Ball minutes per game in the allocation", "%.1f" % M[M.games == games].ball_mpg.iloc[0], "MODELED", "DESCRIPTIVE", rs, fn.replace("availability", "minutes"))

    # ---------------- C1: champions -------------------------------------------------------
    r1 = rid("c1_champions")
    C = csv("c1_champions.csv")
    F("c1_n", S, "champions in the table", len(C), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_first", S, "first season", C.season.iloc[0], "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_last", S, "last season", C.season.iloc[-1], "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    for _, x in C.iterrows():
        k = season_key(x.season)
        seed = int(x.seed_bref) if pd.notna(x.seed_bref) else int(x.seed_warehouse)
        F("c1_%s_team" % k, S, "%s champion" % x.season, x.team, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_record" % k, S, "record", x.record, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_seed" % k, S, "seed", seed, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_net_rs" % k, S, "RS net rating", "%+.1f" % x.net_rs, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_net_rs_rank" % k, S, "RS net rating rank", int(x.net_rs_rank), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_net_post" % k, S, "post-All-Star net rating", "%+.1f" % x.net_post_asb, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_net_post_rank" % k, S, "post-All-Star net rating rank", int(x.net_post_asb_rank), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_net_po" % k, S, "playoff net rating", "%+.1f" % x.net_po, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_net_po_minus" % k, S, "playoff minus RS net rating", "%+.1f" % x.net_po_minus_rs, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_age" % k, S, "top-8 mean age", "%.1f" % x.top8_mean_age, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_oldest" % k, S, "top-8 oldest", "%.1f" % x.top8_oldest, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_drafted" % k, S, "top-8 drafted", int(x.top8_drafted), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_traded" % k, S, "top-8 traded for", int(x.top8_traded), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_signed" % k, S, "top-8 signed", int(x.top8_signed), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_returning" % k, S, "top-8 returning from the season before", int(x.top8_returning), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_returning_share" % k, S, "share of playoff minutes to returning players", pct(100 * x.returning_po_minutes_share, 0), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_returning_contract" % k, S, "top-8 with the franchise the season before, by contract", int(x.top8_returning_contract), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_returning_share_contract" % k, S, "share of playoff minutes to players returning by contract", pct(100 * x.returning_po_minutes_share_contract, 0), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_missed_rs" % k, S, "top-8 RS games missed", int(x.top8_rs_games_missed), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_missed_po" % k, S, "top-8 playoff games missed", int(x.top8_po_games_missed), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_po_games" % k, S, "playoff games", int(x.po_games), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_top5_rs" % k, S, "top-5 minutes share, RS", pct(100 * x.top5_share_rs, 0), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_top5_po" % k, S, "top-5 minutes share, playoffs", pct(100 * x.top5_share_po, 0), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_moves" % k, S, "in-season moves touching the top 8", x.in_season_moves, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_pre_pct" % k, S, "preseason title price, de-vigged", pct(float(x.preseason_implied_pct)), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_pre_rank" % k, S, "preseason title rank of 30", int(x.preseason_rank), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_pre_odds" % k, S, "preseason title odds, American", x.preseason_odds_american, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_pre_fav" % k, S, "preseason favourite", x.preseason_favorite, "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
        F("c1_%s_pre_fav_pct" % k, S, "preseason favourite's price, de-vigged", pct(float(x.preseason_favorite_pct)), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_mean_age", S, "top-8 mean age across champions", "%.1f" % C.top8_mean_age.mean(), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_mean_returning", S, "top-8 returning, mean across champions", "%.1f" % C.top8_returning.mean(), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_mean_returning_contract", S, "top-8 returning by contract, mean across champions", "%.1f" % C.top8_returning_contract.mean(), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_mean_returning_share", S, "share of playoff minutes to returning players, mean", pct(100 * C.returning_po_minutes_share.mean(), 0), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_mean_returning_share_contract", S, "share of playoff minutes to players returning by contract, mean", pct(100 * C.returning_po_minutes_share_contract.mean(), 0), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_seed_1_n", S, "champions that were the 1 seed", int((C.seed_bref.fillna(C.seed_warehouse) == 1).sum()), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_top3_net_n", S, "champions in the top three of RS net rating", int((C.net_rs_rank <= 3).sum()), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_top5_net_n", S, "champions in the top five of RS net rating", int((C.net_rs_rank <= 5).sum()), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_worst_rs_rank", S, "worst RS net rating rank of a champion", int(C.net_rs_rank.max()), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_worst_post_rank", S, "worst post-All-Star net rating rank of a champion", int(C.net_post_asb_rank.max()), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_moves_n", S, "champions with an in-season move touching the top 8", int((C.in_season_moves != "none").sum()), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_mean_top5_rs", S, "top-5 minutes share RS, mean", pct(100 * C.top5_share_rs.mean(), 0), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_mean_top5_po", S, "top-5 minutes share playoffs, mean", pct(100 * C.top5_share_po.mean(), 0), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_mean_missed_rs", S, "top-8 RS games missed, mean", "%.0f" % C.top8_rs_games_missed.mean(), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")
    F("c1_mean_missed_po", S, "top-8 playoff games missed, mean", "%.1f" % C.top8_po_games_missed.mean(), "OBSERVED", "QUOTABLE", r1, "c1_champions.csv")

    # ---------------- the Williams ordering check and the mover base rate (D110) ----------
    rb, rw = rid("mover_minutes_base_rate"), rid("williams_ordering_check")
    B = csv("mover_minutes_base_rate.csv").set_index("group")
    W = csv("williams_ordering_check.csv")
    T = csv("williams_projected_ten.csv").set_index("player")
    F("williams_prior_mpg", S, "Cody Williams, minutes per appearance for Utah 2025-26", "%.1f" % T.loc["Cody Williams", "prior_mpg"], "OBSERVED", "FACT", rw, "williams_projected_ten.csv")
    F("w_shannon_rank", S, "Shannon's rank on Minnesota's roster by the model's score", int(T.loc["Terrence Shannon Jr.", "order_rank"]), "MODELED", "FACT", rw, "williams_projected_ten.csv")
    F("w_pool_n", S, "available players in Minnesota's pool", len(T), "OBSERVED", "FACT", rw, "williams_projected_ten.csv")
    for key, lab, pre in (("primary", "the primary ordering (movers 0.2 / 0.8)", "primary"), ("flat", "the flat 0.5 / 0.5 ordering (sensitivity)", "sensitivity"),
                          ("impact_only", "impact-only ordering", "impact only")):
        x = W[W.ordering.str.startswith(pre)].iloc[0]
        F("w_rank_%s" % key, S, "Williams's rank under %s" % lab, int(x.williams_rank), "MODELED", "QUOTABLE", rw, "williams_ordering_check.csv")
        F("w_mpg_%s" % key, S, "Williams's minutes under %s" % lab, "%.1f" % x.williams_mpg, "MODELED", "QUOTABLE", rw, "williams_ordering_check.csv")
        F("w_delta_%s" % key, S, "offseason delta under %s, mean of four views" % lab, "%+.2f" % x.delta_mean, "MODELED", "QUOTABLE AS BAND", rw, "williams_ordering_check.csv")
        F("w_sign_%s" % key, S, "offseason verdict under %s" % lab, x.delta_sign, "MODELED", "QUOTABLE", rw, "williams_ordering_check.csv")
    F("w_ret_n", S, "mover cohort: players who changed teams", int(B.loc["all movers", "n"]), "OBSERVED", "FACT", rb, "mover_minutes_base_rate.csv")
    F("w_ret_median", S, "mover cohort: median share of prior minutes kept", "%.0f%%" % (100 * B.loc["all movers", "median"]), "OBSERVED", "QUOTABLE", rb, "mover_minutes_base_rate.csv")
    F("w_ret_q25", S, "mover cohort: lower quartile", "%.0f%%" % (100 * B.loc["all movers", "q25"]), "OBSERVED", "QUOTABLE", rb, "mover_minutes_base_rate.csv")
    F("w_ret_q75", S, "mover cohort: upper quartile", "%.0f%%" % (100 * B.loc["all movers", "q75"]), "OBSERVED", "QUOTABLE", rb, "mover_minutes_base_rate.csv")
    F("w_ret_top10_n", S, "movers who landed on a top-ten team by wins", int(B.loc["new team top ten by wins", "n"]), "OBSERVED", "FACT", rb, "mover_minutes_base_rate.csv")
    F("w_ret_top10_median", S, "their median share of prior minutes kept", "%.0f%%" % (100 * B.loc["new team top ten by wins", "median"]), "OBSERVED", "QUOTABLE", rb, "mover_minutes_base_rate.csv")
    F("w_ret_600_n", S, "movers who landed on a .600 team", int(B.loc["new team at or above .600", "n"]), "OBSERVED", "FACT", rb, "mover_minutes_base_rate.csv")
    F("w_ret_600_median", S, "their median share kept", "%.0f%%" % (100 * B.loc["new team at or above .600", "median"]), "OBSERVED", "QUOTABLE", rb, "mover_minutes_base_rate.csv")
    cal = W[W.ordering.str.startswith("calibrated: median, new team top ten")].iloc[0]
    F("w_cal_top10_mpg", S, "Williams at the top-ten-destination retention", "%.1f" % cal.williams_mpg, "MODELED", "QUOTABLE", rw, "williams_ordering_check.csv")
    F("w_cal_top10_delta", S, "offseason delta at that level, mean of four views", "%+.2f" % cal.delta_mean, "MODELED", "QUOTABLE AS BAND", rw, "williams_ordering_check.csv")
    F("w_cal_top10_sign", S, "offseason verdict at that level", cal.delta_sign, "MODELED", "QUOTABLE", rw, "williams_ordering_check.csv")
    med = W[W.ordering.str.startswith("calibrated: median retention, all movers")].iloc[0]
    F("w_cal_all_raw_mpg", S, "Williams at the all-movers median retention, before the default cap", "%.1f" % med.retention_x_prior, "MODELED", "QUOTABLE", rw, "williams_ordering_check.csv")

    # ---------------- C4: the ledger ------------------------------------------------------
    r4 = rid("c4_ledger")
    L = csv("c4_ledger.csv")
    ins = L[(L.direction == "in") & L.salary_2026_27.notna()]
    outs = L[(L.direction == "out") & L.salary_2026_27.notna()]
    F("c4_in_n", S, "players in with a 2026-27 salary", len(ins), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
    F("c4_in_total", S, "2026-27 salary in", money(ins.salary_2026_27.sum()), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
    F("c4_in_total_m", S, "2026-27 salary in, rounded", millions(ins.salary_2026_27.sum()), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
    F("c4_out_n", S, "players out with a 2026-27 salary", len(outs), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
    F("c4_out_total", S, "2026-27 salary out", money(outs.salary_2026_27.sum()), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
    F("c4_out_total_m", S, "2026-27 salary out, rounded", millions(outs.salary_2026_27.sum()), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
    F("c4_rows", S, "ledger rows", len(L), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
    F("c4_single_sourced", S, "ledger rows with one source", int((L.n_sources < 2).sum()), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
    seen = set()
    for _, x in L[L.salary_2026_27.notna() & L.bref.astype(str).str.startswith("/players")].iterrows():
        slug = x.bref.split("/")[-1].replace(".html", "")
        d = str(x.direction).split()[0]
        if (slug, d) in seen:
            continue
        seen.add((slug, d))
        F("c4_%s_%s_salary" % (slug, d), S, "%s 2026-27 salary (%s)" % (x.player, x.direction), money(x.salary_2026_27), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
        F("c4_%s_%s_salary_m" % (slug, d), S, "%s 2026-27 salary, rounded" % x.player, millions(x.salary_2026_27), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
        if pd.notna(x.contract_total):
            F("c4_%s_%s_total" % (slug, d), S, "%s remaining contract: years, total" % x.player, "%d years, %s" % (x.contract_years, money(x.contract_total)), "OBSERVED", "QUOTABLE", r4, "c4_ledger.csv")
    G = csv("../data/c4_offseason_grades.csv", dtype=str)
    read = G[G.status.str.startswith("read")]
    whole = read[read.scope.str.startswith("national") & read.what_was_graded.str.contains("whole offseason", na=False)]
    F("c4_grades_read", S, "graded pieces fetched and read", len(read), "OBSERVED", "QUOTABLE", r4, "c4_offseason_grades.csv")
    F("c4_grades_whole_n", S, "national whole-offseason grades", len(whole), "OBSERVED", "QUOTABLE", r4, "c4_offseason_grades.csv")
    F("c4_grades_whole", S, "national whole-offseason grades, outlet and grade", "; ".join("%s %s" % (x.outlet, x.grade_or_rank) for _, x in whole.iterrows()), "OBSERVED", "QUOTABLE", r4, "c4_offseason_grades.csv")
    F("c4_grades_trade_n", S, "national grades of the Ball trade alone", int(read.what_was_graded.str.startswith("LaMelo Ball trade only").sum()), "OBSERVED", "QUOTABLE", r4, "c4_offseason_grades.csv")
    F("c4_grades_not_read", S, "pieces found but not read", int((~G.status.str.startswith("read")).sum()), "OBSERVED", "QUOTABLE", r4, "c4_offseason_grades.csv")
