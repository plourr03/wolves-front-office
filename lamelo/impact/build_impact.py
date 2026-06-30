"""
Phase 3 (impact layer), clean-room.

Reuses the RAPM METHOD from offseason/scripts/build_rapm.py (method reuse, not a
fitted-output import: no player_value.csv numbers are read), re-runs it fresh with
box features computed from the FROZEN snapshot (wh_65cf5da7f50c7f62), and
re-validates with the out-of-sample YoY metric-selection test that the plan requires.

Possession data: the derived stint cache offseason/data/cache/possessions_league
(2023-24..2025-26), a deterministic derivation from warehouse PBP, reused as a data
source. A full from-PBP rebuild against the freeze (older seasons need the legacy
format shim) is a deferred reproducibility hardening, not required for this window.

Outputs:
  lamelo/data/impact/player_impact.csv   canonical full-window clean-room RAPM
  lamelo/data/impact/yoy_calibration.json  OOS metric-selection numbers
  lamelo/data/impact/lamelo_raw.json     LaMelo's pre-transport anchor

HALT POINT: this is the layer the reviewer wants surfaced before transport. The 0.75
survival prior is applied to LaMelo's raw net RAPM here; eyes on the raw before the haircut.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SNAP = REPO / "lamelo" / "data" / "snapshot_2026-06-25"
OUTDIR = REPO / "lamelo" / "data" / "impact"
OUTDIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(REPO / "offseason" / "scripts"))
import build_rapm as br  # noqa: E402  METHOD reuse (fit_rapm, OFF_FEATS, DEF_FEATS)

LAMELO_ID = 1630163
SEASON_STRS = {2023: "2023-24", 2024: "2024-25", 2025: "2025-26"}


def snapshot_box_features(seasons) -> pd.DataFrame:
    """Replicate build_rapm.box_features on the FROZEN snapshot parquet for `seasons`
    (possession-year ints), so the fit pins the freeze instead of reading the warehouse live."""
    ss = [SEASON_STRS[y] for y in sorted(seasons)]
    ps = pd.read_parquet(SNAP / "nba_player_stats.parquet")
    ps = ps[ps.season_year.isin(ss)]
    agg = {c: (c, "sum") for c in
           ["minutes_played", "pts", "ast", "tov", "oreb", "dreb", "stl", "blk", "pf", "fg3a", "fga"]}
    box = ps.groupby("player_id").agg(**agg).reset_index().rename(columns={"minutes_played": "min"})
    box = box[box["min"] > 0]

    adv = pd.read_parquet(SNAP / "nba_player_advanced_stats.parquet")
    adv = adv[adv.game_id.isin(set(ps.game_id.unique()))].copy()
    adv["minutes_float"] = pd.to_numeric(adv["minutes_float"], errors="coerce").fillna(0.0)
    out = {}
    for src, dst in [("true_shooting_percentage", "ts"), ("usage_percentage", "usg"),
                     ("assist_percentage", "ast_pct"), ("defensive_rebound_percentage", "dreb_pct")]:
        adv["_wv"] = pd.to_numeric(adv[src], errors="coerce") * adv["minutes_float"]
        g = adv.groupby("person_id").agg(num=("_wv", "sum"), den=("minutes_float", "sum"))
        den = g["den"].replace(0, np.nan)  # NULLIF(SUM(minutes_float), 0)
        out[dst] = (g["num"] / den).rename(dst)
    advg = pd.concat(out.values(), axis=1).reset_index().rename(columns={"person_id": "player_id"})

    df = box.merge(advg, on="player_id", how="left")
    m = df["min"].clip(lower=1)
    p36 = lambda c: df[c] / m * 36.0
    feat = pd.DataFrame({"player_id": df["player_id"]})
    feat["pts36"], feat["ast36"], feat["tov36"] = p36("pts"), p36("ast"), p36("tov")
    feat["oreb36"], feat["dreb36"] = p36("oreb"), p36("dreb")
    feat["stl36"], feat["blk36"], feat["pf36"] = p36("stl"), p36("blk"), p36("pf")
    feat["fg3a_rate"] = df["fg3a"] / df["fga"].clip(lower=1)
    for c in ["ts", "usg", "ast_pct", "dreb_pct"]:
        feat[c] = df[c].fillna(df[c].median())
    return feat.fillna(0.0)


def run_fit(seasons, label):
    print(f"\n=== fit RAPM {label} (seasons {sorted(seasons)}) ===", flush=True)
    feats = snapshot_box_features(seasons)
    tbl = br.fit_rapm(seasons=tuple(sorted(seasons)), box_feats=feats)
    return tbl


def main():
    # 1) canonical full-window clean-room fit (the spine + LaMelo's raw anchor)
    full = run_fit((2023, 2024, 2025), "canonical full window 2023-24..2025-26")
    full = full.sort_values("net_rapm", ascending=False).reset_index(drop=True)
    full.to_csv(OUTDIR / "player_impact.csv", index=False)

    corr = float(np.corrcoef(full["net_rapm"], full["box_net_bpm"])[0, 1])
    print(f"\ncorr(net_rapm, box_net_bpm) = {corr:.3f}")
    print("Top 12 (validation: should be stars):")
    for _, r in full.head(12).iterrows():
        nm = str(r["player_name"]).encode("ascii", "replace").decode()
        print(f"  {nm:24} net={r['net_rapm']:+.2f} +/-{r['net_sd']:.2f} poss={r['possessions']:,}")

    # LaMelo raw anchor (full-window) + single-season 2025-26 context
    lm = full[full.player_id == LAMELO_ID]
    lm_row = lm.iloc[0].to_dict() if len(lm) else {}
    print("\n=== LaMelo raw RAPM (PRE-TRANSPORT anchor for the 0.75 survival prior) ===")
    if lm_row:
        print(f"  full-window net={lm_row['net_rapm']:+.2f} +/-{lm_row['net_sd']:.2f} "
              f"(off {lm_row['off_rapm']:+.2f}, def {lm_row['def_rapm']:+.2f}) "
              f"box_net_bpm={lm_row['box_net_bpm']:+.2f} poss={lm_row['possessions']:,} reliable={lm_row['reliable']}")

    # 2) YoY metric-selection: train 2023-24+2024-25, test held-out 2025-26 single-season RAPM
    train = run_fit((2023, 2024), "train 2023-24+2024-25")
    test = run_fit((2025,), "test held-out 2025-26 (single season)")
    tgt = test[["player_id", "net_rapm", "net_sd"]].rename(
        columns={"net_rapm": "target_net", "net_sd": "target_sd"})
    m = train.merge(tgt, on="player_id")
    m = m[(m["reliable"] == "TRUE") & (m["target_net"].notna())].copy()
    n = len(m)
    cal = {"n_players": int(n), "train": "2023-24+2024-25", "test": "2025-26 single-season RAPM",
           "note": "one transition only (cache is 3 seasons); low power, reported honestly",
           "candidates": {}}
    for pred in ["net_rapm", "box_net_bpm"]:
        err = m[pred] - m["target_net"]
        rmse = float(np.sqrt(np.mean(err ** 2)))
        corr_p = float(np.corrcoef(m[pred], m["target_net"])[0, 1])
        # noisy-target standardized error (coverage_calibration style): denom = quadrature of SDs
        denom = np.sqrt(m["net_sd"] ** 2 + m["target_sd"] ** 2) if pred == "net_rapm" else \
                np.sqrt(m["target_sd"] ** 2 + (m["net_sd"] ** 2))
        z = (err / denom)
        cal["candidates"][pred] = {
            "oos_corr_vs_next_season_rapm": round(corr_p, 3),
            "oos_rmse": round(rmse, 3),
            "std_resid_mean": round(float(z.mean()), 3),
            "std_resid_sd": round(float(z.std()), 3),
        }
    (OUTDIR / "yoy_calibration.json").write_text(json.dumps(cal, indent=2))
    (OUTDIR / "lamelo_raw.json").write_text(json.dumps(
        {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in lm_row.items()}, indent=2))

    print("\n=== YoY metric-selection (OOS, predict next-season RAPM) ===")
    print(f"  n={n} players reliable in train & present in test")
    for pred, d in cal["candidates"].items():
        print(f"  {pred:14} corr={d['oos_corr_vs_next_season_rapm']:+.3f} "
              f"rmse={d['oos_rmse']:.3f} std_resid_sd={d['std_resid_sd']:.2f}")
    winner = max(cal["candidates"], key=lambda k: cal["candidates"][k]["oos_corr_vs_next_season_rapm"])
    print(f"  -> higher OOS corr: {winner}")
    print(f"\nwrote {OUTDIR/'player_impact.csv'}, yoy_calibration.json, lamelo_raw.json")


if __name__ == "__main__":
    main()
