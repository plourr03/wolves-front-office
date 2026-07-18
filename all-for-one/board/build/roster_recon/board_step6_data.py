"""Warehouse pulls for board step six (season-boundary evolution, market tightness).

Computes, from real warehouse + offseason data, the calibration inputs the board's
evolution/market/tax mechanisms consume. Writes board_step6_data.json. Everything
here is FACTS and CALIBRATIONS ("model that teams change, never how"): no predicted
trades, no per-team trajectories asserted.

  age_curve      : same-player year-over-year net_rating change by age (the shape of
                   development up / decline down); used to drift player impacts.
  impact_ages    : current age per impact-table player_id (to apply the curve).
  churn_sigma    : SD of year-over-year team net swings (far-field churn variance).
  regress_beta   : year-over-year mean-reversion slope of team net (far-field drift).
  deadline_market: trade activity in the Jan15-Feb15 window per season (tightness proxy).
  contract_cont  : per-team returning vs expiring salary 2027-28 (near-field continuity).
  tax            : CBA tax schedule + MIN repeater clock + ownership posture (ARM-D).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query   # noqa: E402

HERE = Path(__file__).parent
OFF = REPO / "offseason" / "data"


def age_curve_and_ages():
    """Same-player YoY net_rating change by age (min 40 gp both seasons). Shape only;
    the board scales it to an impact-drift magnitude (TUNE)."""
    d = query("""
        select player_id, season_year, age, gp, net_rating
        from nba.nba_player_season_bio
        where season_type = 'Regular Season' and gp >= 40 and net_rating is not null
    """)
    d["yy"] = d.season_year.str[:4].astype(int)
    d = d.sort_values(["player_id", "yy"])
    d["net_next"] = d.groupby("player_id").net_rating.shift(-1)
    d["yy_next"] = d.groupby("player_id").yy.shift(-1)
    consec = d[(d.yy_next == d.yy + 1)].copy()
    consec["dnet"] = consec.net_next - consec.net_rating
    # mean YoY net change by age bucket
    curve = consec.groupby(consec.age.clip(19, 36)).dnet.mean().round(3).to_dict()
    curve = {int(k): float(v) for k, v in curve.items()}
    # current age for impact players
    imp = pd.read_csv(REPO / "lamelo" / "data" / "impact" / "player_impact.csv")
    latest = (query("""
        select player_id, max(season_year) as sy from nba.nba_player_season_bio group by player_id
    """))
    ages = query("""
        select player_id, season_year, age from nba.nba_player_season_bio
    """)
    ages["yy"] = ages.season_year.str[:4].astype(int)
    cur = ages.sort_values("yy").groupby("player_id").age.last()
    # +1 year to bring the last observed season to 2026-27 age (approx)
    impact_ages = {}
    for pid in imp.player_id.astype(int):
        if pid in cur.index:
            impact_ages[str(pid)] = int(cur.loc[pid]) + 1
    return curve, impact_ages, len(consec)


def churn_and_regress():
    """Team-season net (reg season, game_id like 002%) -> YoY swing SD + mean-reversion
    slope. season encoded in game_id chars 4-5."""
    t = query("""
        select team_id, substring(game_id from 4 for 2) as yy, avg(net_rating) as net, count(*) as g
        from nba.nba_team_advanced_stats
        where game_id like '002%' and net_rating is not null
        group by team_id, substring(game_id from 4 for 2)
        having count(*) >= 50
    """)
    t["yy"] = t.yy.astype(int)
    t = t.sort_values(["team_id", "yy"])
    t["net_next"] = t.groupby("team_id").net.shift(-1)
    t["yy_next"] = t.groupby("team_id").yy.shift(-1)
    c = t[t.yy_next == t.yy + 1].copy()
    c["dnet"] = (c.net_next - c.net).astype(float)
    churn_sigma = float(c.dnet.std())
    # regression: net_next = a + b*net -> b<1 is mean reversion; drift = (b-1)*net
    b, a = np.polyfit(c.net.astype(float), c.net_next.astype(float), 1)
    return dict(churn_sigma=round(churn_sigma, 3), regress_slope=round(float(b), 3),
                regress_intercept=round(float(a), 3), n_pairs=int(len(c)))


def deadline_market():
    """Trade-window (Jan 15 - Feb 15) activity per season as a tightness proxy. More
    buyers chasing at the deadline -> higher sweetener prices (TUNE mapping in board)."""
    tr = query("""
        select extract(year from transaction_date)::int as yr,
               count(*) filter (where transaction_type = 'Trade') as trades,
               count(distinct team_id) filter (where transaction_type = 'Trade') as teams_in
        from nba.nba_transactions
        where (extract(month from transaction_date) = 2 and extract(day from transaction_date) <= 15)
           or (extract(month from transaction_date) = 1 and extract(day from transaction_date) >= 15)
        group by 1 order by 1
    """)
    tr = tr[tr.trades > 0]
    trades = tr.trades.astype(float)
    return dict(by_year={int(r.yr): dict(trades=int(r.trades), teams_in=int(r.teams_in)) for _, r in tr.iterrows()},
                mean_trades=round(float(trades.mean()), 1), sd_trades=round(float(trades.std()), 1),
                min_trades=int(trades.min()), max_trades=int(trades.max()))


def contract_continuity():
    """Per-team returning (2027-28) vs current (2026-27) salary + option count, from
    nba_player_contracts. Facts only: how much of each team is locked vs expiring."""
    c = pd.read_csv(OFF / "nba_contracts_2026_27_verified.csv") if (OFF / "nba_contracts_2026_27_verified.csv").exists() else None
    try:
        d = query("""
            select team_abbr, season, sum(salary) as sal,
                   count(*) filter (where option_type is not null and option_type <> '') as options
            from nba.nba_player_contracts
            where season in ('2026-27','2027-28')
            group by team_abbr, season
        """)
        piv = d.pivot_table(index="team_abbr", columns="season", values="sal", aggfunc="sum").fillna(0)
        opt = d.groupby("team_abbr").options.sum()
        out = {}
        for tm in piv.index:
            s2627 = float(piv.loc[tm].get("2026-27", 0.0))
            s2728 = float(piv.loc[tm].get("2027-28", 0.0))
            cont = s2728 / s2627 if s2627 > 0 else 0.0
            out[tm] = dict(sal_2627=round(s2627 / 1e6, 1), returning_2728=round(s2728 / 1e6, 1),
                           continuity=round(cont, 3), options=int(opt.get(tm, 0)))
        league_cont = float(np.mean([v["continuity"] for v in out.values() if v["continuity"] > 0]))
        return dict(by_team=out, league_mean_continuity=round(league_cont, 3))
    except Exception as e:
        return dict(error=str(e))


def tax_and_ownership():
    """CBA tax schedule (standard brackets) + MIN repeater clock (tax_history) + cap
    constants (league_year_constants) for the ARM-D value channel."""
    lyc = json.loads((OFF / "league_year_constants.json").read_text())
    th = pd.read_csv(OFF / "tax_history.csv")
    minh = th[th.team_abbr == "MIN"].sort_values("season")
    taxed_recent = minh.tail(4).paid_luxury_tax.astype(str).str.upper().eq("TRUE").sum() if len(minh) else 0
    # standard non-repeater luxury-tax brackets ($ over line -> incremental rate), CBA public schedule
    nonrep = [(0, 1.50), (5e6, 1.75), (10e6, 2.50), (15e6, 3.25), (20e6, 3.75)]  # +0.5/5M above
    repeater_premium = 1.00   # repeater adds ~+1.00 to each bracket (approx, TUNE)
    return dict(seasons_taxed_last4=int(taxed_recent),
                is_repeater_2627=bool(taxed_recent >= 3),
                nonrep_brackets=nonrep, repeater_premium=repeater_premium,
                luxury_tax_2627=lyc["seasons"].get("2026-27", {}).get("luxury_tax"),
                first_apron_2627=lyc["seasons"].get("2026-27", {}).get("first_apron"),
                min_tax_history=[{"season": r.season, "taxed": str(r.paid_luxury_tax)} for _, r in minh.iterrows()])


def main():
    print("Pulling board step-six calibration data (facts + calibrations only)...")
    curve, impact_ages, n_consec = age_curve_and_ages()
    print(f"  age curve: {len(curve)} age buckets from {n_consec} consecutive-season pairs")
    ch = churn_and_regress()
    print(f"  churn: sigma {ch['churn_sigma']}, regress slope {ch['regress_slope']} (n={ch['n_pairs']})")
    dm = deadline_market()
    print(f"  deadline market: mean {dm['mean_trades']} trades (range {dm['min_trades']}-{dm['max_trades']})")
    cc = contract_continuity()
    print(f"  contract continuity: league mean {cc.get('league_mean_continuity')}")
    tx = tax_and_ownership()
    print(f"  tax: MIN taxed {tx['seasons_taxed_last4']}/last4, repeater={tx['is_repeater_2627']}")

    out = {"age_curve": curve, "impact_ages": impact_ages, "n_consec_pairs": n_consec,
           "churn": ch, "deadline_market": dm, "contract_continuity": cc, "tax": tx,
           "note": "facts + calibrations; no predicted trades; age curve is SHAPE (board scales it, TUNE)"}
    (HERE / "board_step6_data.json").write_text(json.dumps(out, indent=1))
    print(f"wrote {HERE/'board_step6_data.json'}")
    # quick age-curve sanity: young should be positive, old negative
    print("  age-curve sample:", {a: curve.get(a) for a in (21, 24, 27, 30, 33, 36) if a in curve})


if __name__ == "__main__":
    main()
