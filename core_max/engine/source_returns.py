#!/usr/bin/env python3
"""Phase 3 returns sourcing: surface REAL, capital-realistic, plausible-seller comps for the
two Fork B returns, with their impact distributions and real availability (games-missed) tails.

Conditions (user-set):
- capital realism: returns must be matchable by what we actually send (Gobert ~$36.5M; Randle
  ~$33.3M + filler), and we take back <= outgoing so the deal OPENS room and trips no hard cap
  (the Phase-0 gate property). No return needing capital we do not have.
- real injury tail: sized from the player's actual games-played history, not assumed clean.
- plausible SELLER, not just fit: surfaced with a seller-proxy (the holding team's projected
  2026-27 strength; weak teams are plausible sellers) so judgment about "would they move him"
  is data-anchored, not aspirational. Final seller call is stated per name in the writeup.

This SURFACES candidates and signals; it does not pick. The conservative/median/optimistic band
is named in the writeup with per-name seller rationale, for gut-check before any verdict runs.

    python core_max/engine/source_returns.py
"""
import os
import sys
import csv
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
import bracket_sim as BS          # for the seller-proxy team-net
import build_team_ratings as A
import build_rotation_model as RM  # DIMS, load_dims

PV = os.path.join(REPO, "offseason", "data", "player_value.csv")
CONTRACTS = os.path.join(REPO, "offseason", "data", "nba_contracts_2026_27_verified.csv")
SMB = os.path.join(REPO, "offseason", "data", "cache", "season_min_blk_2001_2026.csv")

GOBERT_OUT, RANDLE_OUT_PLUS = 36_500_000, 45_000_000   # Randle $33.3M + ~$12M filler (DiVincenzo)


def load():
    pv = pd.read_csv(PV)
    con = pd.read_csv(CONTRACTS)
    con["nba_player_id"] = con["nba_player_id"].astype(str)
    pv["player_id"] = pv["player_id"].astype(str)
    dims = RM.load_dims()
    smb = pd.read_csv(SMB)
    smb["yr"] = smb["season"].str[:4].astype(int)
    # availability: games-played rate over the last 3 seasons (82-game basis) -> missed-game tail
    recent = smb[smb["yr"].isin([2023, 2024, 2025])]
    gp = recent.groupby("PLAYER_ID").agg(gp=("GP", "sum"), age=("AGE", "max")).reset_index()
    gp["avail"] = (gp["gp"] / (3 * 82)).clip(upper=1.0)
    gp["PLAYER_ID"] = gp["PLAYER_ID"].astype(str)
    d = pv.merge(con[["nba_player_id", "team_abbr", "player", "position", "salary_2026_27",
                      "trade_kicker_pct", "no_trade_clause_flag"]],
                 left_on="player_id", right_on="nba_player_id", how="inner")
    d = d.merge(gp[["PLAYER_ID", "age", "avail"]], left_on="player_id", right_on="PLAYER_ID", how="left")
    for k, v in dims.items():
        for dim, val in v.items():
            d.loc[d["player_id"] == k, dim] = val
    d["salary_2026_27"] = pd.to_numeric(d["salary_2026_27"], errors="coerce")
    return d


def seller_proxy():
    """Holding team's projected 2026-27 net (low => non-contender => plausible seller)."""
    imp = A.load_impacts()
    s = BS.build_2026_27_league(imp)
    return {ab: s[ab]["net"] for ab in s}


def show(df, cols, label, n=12):
    print(f"\n=== {label} ===")
    hdr = f"{'player':22s}{'tm':>4s}{'pos':>5s}{'sal$M':>7s}{'net':>6s}{'sd':>5s}{'age':>4s}{'avail':>6s}{'sellerNet':>10s}  fit"
    print(hdr)
    for _, r in df.head(n).iterrows():
        nm = str(r["player"]).encode("ascii", "replace").decode()
        fit = " ".join(f"{d[:4]}{r.get(d, float('nan')):.2f}" for d in ["off_ball_shooting", "def_versatility_poa", "hc_creation", "secondary_playmaking"])
        print(f"{nm[:22]:22s}{r['team_abbr']:>4s}{str(r['position'])[:5]:>5s}{r['salary_2026_27']/1e6:>7.1f}"
              f"{r['consensus_net']:>+6.1f}{r['net_sd']:>5.1f}{(r['age'] if pd.notna(r['age']) else 0):>4.0f}"
              f"{(r['avail'] if pd.notna(r['avail']) else 0):>6.2f}{r['sellerNet']:>+10.1f}  {fit}")


def main():
    d = load()
    sp = seller_proxy()
    d["sellerNet"] = d["team_abbr"].map(sp).fillna(0.0)
    d = d[d["team_abbr"] != "MIN"]
    d = d[d["salary_2026_27"].notna() & (d["salary_2026_27"] >= 10e6)]
    for dim in RM.DIMS:
        d[dim] = pd.to_numeric(d.get(dim), errors="coerce")
    d = d.dropna(subset=["off_ball_shooting"])   # need a dimension profile to judge fit

    POS_C = d["position"].astype(str).str.fullmatch(r"C|C-F|F-C|Center.*")

    # Gobert-side: 3-and-D wing/guard (NOT a center), low-usage compatible, takes back <= Gobert
    g = d[(~POS_C) & (d["salary_2026_27"] <= GOBERT_OUT)
          & (d["off_ball_shooting"] >= 0.58) & (d["def_versatility_poa"] >= 0.55)
          & (d["hc_creation"] <= 0.65)].copy()
    g = g.sort_values("consensus_net", ascending=False)
    show(g, None, "GOBERT-SIDE candidates: 3-and-D wing/guard (<= $36.5M, low-usage, real D + shooting)")

    # Randle-side: secondary creator + shooting that scales next to Ant (NOT a ball-dominant alpha)
    r = d[(d["salary_2026_27"] <= RANDLE_OUT_PLUS)
          & (d["off_ball_shooting"] >= 0.52)
          & ((d["secondary_playmaking"] >= 0.58) | (d["hc_creation"].between(0.55, 0.78)))
          & (d["hc_creation"] <= 0.80)].copy()
    r = r.sort_values("consensus_net", ascending=False)
    show(r, None, "RANDLE-SIDE candidates: secondary creator + shooting, scales next to Ant (<= ~$45M w/ filler)")

    print("\nseller-proxy = holding team's projected 2026-27 net (lower => weaker team => more plausible seller).")
    print("avail = share of 246 possible games played 2023-26 (the real availability/injury-tail input).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
