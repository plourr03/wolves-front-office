#!/usr/bin/env python3
"""
build_external_triangulation.py

External validation of the RAPM impact spine, the step the review said gates
everything. Pulls an INDEPENDENT public impact metric (Basketball-Reference
BPM/OBPM/DBPM, league-wide, box-based with its own coefficients, computed outside
our pipeline) and triangulates it against our possession-based RAPM.

Why BPM and not DARKO/EPM/LEBRON: those are app- or subscription-gated with no
clean programmatic pull (flagged for Pass-2). BPM is freely scriptable and, being
box-based while our RAPM is possession-based, is a genuine independent check, not
the circular correlation against our own box prior.

What it does:
1. Fetch BBR advanced for 2023-24, 2024-25, 2025-26; take the combined row per
   traded player; aggregate minute x recency weighted to match the RAPM window.
2. Match to player_value by normalized name; report coverage.
3. Report corr(net_rapm, BPM), corr(off_rapm, OBPM), corr(-def_rapm, DBPM).
4. Form a CONSENSUS impact (z-blend, 0.6 RAPM / 0.4 BPM, mapped back to the RAPM
   scale) for net/off/def, and a per-player DIVERGENCE (|z_rapm - z_bpm|). High
   divergence = the two methods disagree = the verdict stays provisional; low
   divergence = externally corroborated = firm.
5. Write the new columns back into player_value.csv (post-step, like enrich).

Run AFTER build_rapm.py:
    python build_external_triangulation.py
"""

import os
import re
import time
import unicodedata
import io
import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PV = os.path.join(DATA, "player_value.csv")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research"}
SEASONS = {2024: 0.69, 2025: 0.83, 2026: 1.0}    # BBR end-year -> recency weight (matches RAPM)
# Consensus weights. Defense leans harder on RAPM because box BPM underrates rim
# deterrence (Gobert RAPM +5.76 vs box +1.52; def corr 0.66 vs off 0.77). BBR is a
# stopgap independent check, NOT the final word; EPM/LEBRON stay a live Pass-2.
OFF_RAPM_W, DEF_RAPM_W = 0.6, 0.75


def norm(n):
    n = unicodedata.normalize("NFKD", str(n or ""))
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = n.lower().replace(".", "").replace("'", "").replace("-", " ")
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"\s+", " ", n).strip()


def fetch_bbr(year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_advanced.html"
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    tabs = pd.read_html(io.StringIO(r.text))
    df = next(t for t in tabs if any("BPM" in str(c) for c in t.columns))
    df = df[df["Player"].notna() & (df["Player"] != "Player")].copy()
    for c in ("MP", "BPM", "OBPM", "DBPM"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # traded players appear once per team plus a combined row; keep max-MP (the combined)
    df = df.sort_values("MP", ascending=False).drop_duplicates("Player", keep="first")
    df["year"] = year
    return df[["Player", "MP", "BPM", "OBPM", "DBPM", "year"]].dropna(subset=["MP"])


def main():
    parts = []
    for y in SEASONS:
        parts.append(fetch_bbr(y))
        print(f"  BBR {y}: {len(parts[-1])} players")
        time.sleep(3)                                 # be polite to BBR
    bbr = pd.concat(parts, ignore_index=True)
    bbr["w"] = bbr["MP"] * bbr["year"].map(SEASONS)
    agg = bbr.groupby("Player").apply(lambda g: pd.Series({
        "bbr_bpm": np.average(g["BPM"], weights=g["w"]),
        "bbr_obpm": np.average(g["OBPM"], weights=g["w"]),
        "bbr_dbpm": np.average(g["DBPM"], weights=g["w"]),
        "bbr_mp": g["MP"].sum(),
    }), include_groups=False).reset_index()
    agg["nkey"] = agg["Player"].map(norm)

    pv = pd.read_csv(PV)
    # idempotent: drop any external columns from a prior run before re-merging
    added = ["bbr_bpm", "bbr_obpm", "bbr_dbpm", "bbr_mp", "consensus_off", "consensus_def",
             "consensus_net", "impact_divergence", "def_divergence", "externally_corroborated", "nkey"]
    pv = pv.drop(columns=[c for c in added if c in pv.columns])
    pv["nkey"] = pv["player_name"].map(norm)
    m = pv.merge(agg.drop(columns="Player"), on="nkey", how="left")
    cov = m["bbr_bpm"].notna().sum()
    print(f"\nmatched {cov}/{len(pv)} player_value rows to BBR")

    # correlations (the actual independent check)
    sub = m.dropna(subset=["bbr_bpm"])
    print("\nIndependent triangulation (RAPM vs BBR BPM):")
    print(f"  corr(net_rapm, bbr_bpm)   = {np.corrcoef(sub['net_rapm'], sub['bbr_bpm'])[0,1]:.3f}")
    print(f"  corr(off_rapm, bbr_obpm)  = {np.corrcoef(sub['off_rapm'], sub['bbr_obpm'])[0,1]:.3f}")
    print(f"  corr(-def_rapm, bbr_dbpm) = {np.corrcoef(-sub['def_rapm'], sub['bbr_dbpm'])[0,1]:.3f}")

    # consensus on the RAPM scale, plus divergence. Defense weighted harder to RAPM.
    def zblend(rapm_col, bpm_col, rapm_w, sign=1):
        r = m[rapm_col] * sign
        b = m[bpm_col]
        rz = (r - r.mean()) / r.std()
        bz = (b - b.mean()) / b.std()
        cons_z = np.where(bz.notna(), rapm_w * rz + (1 - rapm_w) * bz, rz)   # fall back to RAPM if no BBR
        return (cons_z * r.std() + r.mean()) * sign, rz, bz   # map back to the rapm_col scale

    cons_off, rz_off, bz_off = zblend("off_rapm", "bbr_obpm", OFF_RAPM_W)
    cons_def, rz_def, bz_def = zblend("def_rapm", "bbr_dbpm", DEF_RAPM_W, sign=-1)   # def negative=good
    m["consensus_off"] = np.round(cons_off, 2)
    m["consensus_def"] = np.round(cons_def, 2)
    m["consensus_net"] = np.round(cons_off - cons_def, 2)    # net from components, so def's RAPM weighting flows through

    # overall method divergence (net) -> the player firm/provisional flag
    rzn = (m["net_rapm"] - m["net_rapm"].mean()) / m["net_rapm"].std()
    bzn = (m["bbr_bpm"] - m["bbr_bpm"].mean()) / m["bbr_bpm"].std()
    m["impact_divergence"] = np.round(np.where(bzn.notna(), np.abs(rzn - bzn), np.nan), 2)
    # DEFENSIVE divergence (RAPM vs box on D) -> carried into team-rating uncertainty
    m["def_divergence"] = np.round(np.where(bz_def.notna(), np.abs(rz_def - bz_def), np.nan), 2)
    m["externally_corroborated"] = np.where(
        m["bbr_bpm"].isna(), "no_external",
        np.where(m["impact_divergence"] <= 1.0, "TRUE", "FALSE"))

    m.drop(columns="nkey").to_csv(PV, index=False)
    print(f"wrote consensus + divergence into {PV}")

    def safe(s): return str(s).encode("ascii", "replace").decode()
    print("\nDoes AD move? board players: RAPM vs BBR vs consensus")
    for n in ["Anthony Davis", "Kawhi Leonard", "Giannis", "Ja Morant", "Zion",
              "Trae Young", "Lauri Markkanen", "Julius Randle", "Rudy Gobert", "Anthony Edwards"]:
        row = m[m["player_name"].str.contains(n, case=False, na=False)]
        if len(row):
            x = row.iloc[0]
            print(f"  {safe(x['player_name']):22} RAPM {x['net_rapm']:+5.2f} | BBR {x['bbr_bpm']:+5.2f} | "
                  f"consensus {x['consensus_net']:+5.2f} | div {x['impact_divergence']} | "
                  f"corrob {x['externally_corroborated']}")


if __name__ == "__main__":
    main()
