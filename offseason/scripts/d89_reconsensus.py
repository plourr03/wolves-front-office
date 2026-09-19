#!/usr/bin/env python3
"""D89: re-derive the consensus view from the refit RAPM, on FROZEN Basketball-Reference.

`build_external_triangulation.py` computes the consensus columns, but it fetches
Basketball-Reference live and that host 403s this project (the repo reaches it through a
proxy elsewhere). The BBR values it produced are already frozen in the pre-D89
`player_value.csv`, so consensus is re-derived from those, with the same formula and the
same weights: offence 60% RAPM / 40% BBR OBPM, defence 75% / 25%, z-blended and mapped
back onto the RAPM scale.

  G1  re-deriving consensus from the PRE-D89 RAPM and the same frozen BBR reproduces the
      pre-D89 consensus columns exactly. That is what proves the formula is replicated
      rather than re-invented. Only then is it applied to the refit RAPM.

    python offseason/scripts/d89_reconsensus.py
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
FROZEN = os.path.join(DATA, "player_value_ondisk_pre_d89.csv")   # pre-D89, carries bbr_*
BEFORE_FIT = os.path.join(DATA, "player_value_pre_d89.csv")      # refit on legacy points
PV = os.path.join(DATA, "player_value.csv")                      # refit on corrected points
OFF_RAPM_W, DEF_RAPM_W = 0.6, 0.75
BBR = ["bbr_bpm", "bbr_obpm", "bbr_dbpm", "bbr_mp"]
DERIVED = ["consensus_off", "consensus_def", "consensus_net", "impact_divergence",
           "def_divergence", "externally_corroborated"]


def norm(n):
    n = unicodedata.normalize("NFKD", str(n or ""))
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = n.lower().replace(".", "").replace("'", "").replace("-", " ")
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return re.sub(r"\s+", " ", n).strip()


def derive(m: pd.DataFrame) -> pd.DataFrame:
    """The formula from build_external_triangulation.main(), unchanged."""
    def zblend(rapm_col, bpm_col, rapm_w, sign=1):
        r = m[rapm_col] * sign
        b = m[bpm_col]
        rz = (r - r.mean()) / r.std()
        bz = (b - b.mean()) / b.std()
        cons_z = np.where(bz.notna(), rapm_w * rz + (1 - rapm_w) * bz, rz)
        return (cons_z * r.std() + r.mean()) * sign, rz, bz

    cons_off, rz_off, bz_off = zblend("off_rapm", "bbr_obpm", OFF_RAPM_W)
    cons_def, rz_def, bz_def = zblend("def_rapm", "bbr_dbpm", DEF_RAPM_W, sign=-1)
    m = m.copy()
    m["consensus_off"] = np.round(cons_off, 2)
    m["consensus_def"] = np.round(cons_def, 2)
    m["consensus_net"] = np.round(cons_off - cons_def, 2)
    rzn = (m["net_rapm"] - m["net_rapm"].mean()) / m["net_rapm"].std()
    bzn = (m["bbr_bpm"] - m["bbr_bpm"].mean()) / m["bbr_bpm"].std()
    m["impact_divergence"] = np.round(np.where(bzn.notna(), np.abs(rzn - bzn), np.nan), 2)
    m["def_divergence"] = np.round(np.where(bz_def.notna(), np.abs(rz_def - bz_def), np.nan), 2)
    m["externally_corroborated"] = np.where(
        m["bbr_bpm"].isna(), "no_external",
        np.where(m["impact_divergence"] <= 1.0, "TRUE", "FALSE"))
    return m


def attach_bbr(fit: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    """Join the frozen BBR columns on the same normalised-name key the original used."""
    f = frozen.copy()
    f["nkey"] = f.player_name.map(norm)
    f = f.drop_duplicates("nkey")[["nkey"] + BBR]
    out = fit.drop(columns=[c for c in BBR + DERIVED + ["nkey"] if c in fit.columns]).copy()
    out["nkey"] = out.player_name.map(norm)
    out = out.merge(f, on="nkey", how="left").drop(columns="nkey")
    return out


def main():
    frozen = pd.read_csv(FROZEN)
    print("frozen pre-D89 value layer: %d players, %d with BBR"
          % (len(frozen), int(frozen.bbr_bpm.notna().sum())))

    # ---- G1: reproduce the pre-D89 consensus from the pre-D89 RAPM ----------------
    check = derive(attach_bbr(frozen[[c for c in frozen.columns if c not in DERIVED]], frozen))
    ok = True
    for c in ("consensus_off", "consensus_def", "consensus_net"):
        d = (check[c] - frozen[c]).abs()
        worst = float(d.max())
        n_bad = int((d > 0.005).sum())
        print("G1 %s: worst |difference| %.4f, rows off by more than a rounding step: %d"
              % (c, worst, n_bad))
        ok = ok and n_bad == 0
    same_flag = int((check.externally_corroborated == frozen.externally_corroborated).sum())
    print("G1 externally_corroborated matches on %d of %d rows" % (same_flag, len(frozen)))
    if not ok or same_flag != len(frozen):
        raise RuntimeError("G1 failed: the consensus formula does not reproduce the frozen "
                           "columns, so it must not be applied to the refit")

    # ---- apply to both fits ------------------------------------------------------
    for path, label in ((BEFORE_FIT, "refit on legacy points"), (PV, "refit on corrected points")):
        if not os.path.exists(path):
            print("missing %s (%s), skipped" % (os.path.basename(path), label))
            continue
        fit = pd.read_csv(path)
        out = derive(attach_bbr(fit, frozen))
        out.to_csv(path, index=False)
        print("wrote consensus into %s (%s): %d players, %d with BBR"
              % (os.path.basename(path), label, len(out), int(out.bbr_bpm.notna().sum())))

    a = pd.read_csv(PV)
    b = pd.read_csv(BEFORE_FIT) if os.path.exists(BEFORE_FIT) else frozen
    k = ["player_id", "player_name", "consensus_off", "consensus_def", "consensus_net"]
    m = b[k].merge(a[k], on=["player_id", "player_name"], suffixes=("_b", "_a"))
    m["d_net"] = m.consensus_net_a - m.consensus_net_b
    print("\nconsensus net shift: mean %+.3f, mean abs %.3f, largest %.2f"
          % (m.d_net.mean(), m.d_net.abs().mean(), m.d_net.abs().max()))
    for nm in ("Rudy Gobert", "Anthony Edwards", "Jonathan Kuminga", "LaMelo Ball", "Naz Reid"):
        r = m[m.player_name == nm]
        if len(r):
            r = r.iloc[0]
            print("  %-20s consensus net %+6.2f -> %+6.2f" % (nm, r.consensus_net_b, r.consensus_net_a))


if __name__ == "__main__":
    main()
