#!/usr/bin/env python3
"""Item 18: assemble the deliverable tables and the provenance appendix.

Reads every artifact the pipeline produced and writes the publication tables, plus an
appendix that maps each one back to the script, the run id, and the frozen snapshot
that produced it. Nothing is computed here that was not computed upstream; this is
assembly, so that a number in the piece can always be walked back to a run.

    python kuminga/scripts/build_outputs.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import kfreeze, runlog  # noqa: E402

OUTDIR = os.path.join(REPO, "kuminga", "outputs")
LOG = os.path.join(REPO, "kuminga", "logs", "runs.jsonl")
FORKS = ["consensus", "rapm", "box", "darko"]


def load(name, **kw):
    p = os.path.join(OUTDIR, name)
    return pd.read_csv(p, **kw) if os.path.exists(p) else None


def band(row, cols):
    v = [row[c] for c in cols if pd.notna(row.get(c))]
    return (min(v), max(v)) if v else (np.nan, np.nan)


def main():
    with runlog.run("build_outputs", inputs={"outdir": OUTDIR}) as r:
        sim = load("sim_all30_2026_27.csv")
        assert sim is not None, "run kuminga/scripts/run_sim.py first"

        # ---- T1: all-30 before/after -----------------------------------------
        t1 = sim.pivot_table(index=["team_abbr", "conf"],
                             columns="fork",
                             values=["title_baseline", "title_current", "title_delta",
                                     "wins_current", "net_current"]).reset_index()
        t1.columns = ["_".join(c).strip("_") for c in t1.columns]
        dcols = [f"title_delta_{f}" for f in FORKS if f"title_delta_{f}" in t1.columns]
        t1["title_delta_mean_pp"] = t1[dcols].mean(axis=1) * 100
        t1["title_delta_min_pp"] = t1[dcols].min(axis=1) * 100
        t1["title_delta_max_pp"] = t1[dcols].max(axis=1) * 100
        t1["sign_agreement"] = np.where(
            (t1[dcols] > 0).all(axis=1), "ALL POSITIVE",
            np.where((t1[dcols] < 0).all(axis=1), "ALL NEGATIVE", "MIXED"))
        ccols = [f"title_current_{f}" for f in FORKS if f"title_current_{f}" in t1.columns]
        t1["title_current_mean_pct"] = t1[ccols].mean(axis=1) * 100
        t1 = t1.sort_values("title_current_mean_pct", ascending=False)
        t1["rank_current"] = range(1, len(t1) + 1)
        bcols = [f"title_baseline_{f}" for f in FORKS if f"title_baseline_{f}" in t1.columns]
        t1["title_baseline_mean_pct"] = t1[bcols].mean(axis=1) * 100
        t1["rank_baseline"] = t1.title_baseline_mean_pct.rank(ascending=False).astype(int)
        t1["rank_change"] = t1.rank_baseline - t1.rank_current
        t1.to_csv(os.path.join(OUTDIR, "T1_all30_before_after.csv"), index=False)
        r.note(f"T1: {len(t1)} teams | sign agreement: "
               f"{t1.sign_agreement.value_counts().to_dict()}")

        # ---- T2: the West ordinal ranking ------------------------------------
        west = t1[t1.conf == "W"].copy().sort_values("title_current_mean_pct", ascending=False)
        west["west_rank_current"] = range(1, len(west) + 1)
        west["west_rank_baseline"] = west.title_baseline_mean_pct.rank(ascending=False).astype(int)
        west["west_rank_change"] = west.west_rank_baseline - west.west_rank_current
        west.to_csv(os.path.join(OUTDIR, "T2_west_ranking.csv"), index=False)
        mn = west[west.team_abbr == "MIN"].iloc[0]
        r.note(f"T2: Minnesota is West #{int(mn.west_rank_current)} now, "
               f"#{int(mn.west_rank_baseline)} on the baseline "
               f"({int(mn.west_rank_change):+d})")

        # ---- T3-T7: pass-throughs with a band column --------------------------
        for src, dest, key in (("shapley_min.csv", "T3_shapley.csv", "move"),
                               ("scenario_fan.csv", "T4_scenario_fan.csv", None),
                               ("kuminga_surplus_by_fork.csv", "T5_surplus.csv", None),
                               ("counterfactual_fives.csv", "T6_counterfactual_fives.csv", None),
                               ("cap_branches.csv", "T7_cap_branches.csv", None),
                               ("player_option.csv", "T8_player_option.csv", None),
                               ("lineup_evidence.csv", "T9_lineup_evidence.csv", None)):
            df = load(src, index_col=0) if key else load(src)
            if df is None:
                r.note(f"  {src}: MISSING, skipped")
                continue
            df.to_csv(os.path.join(OUTDIR, dest))
            r.note(f"  {dest}: {len(df)} rows")

        # ---- provenance appendix ---------------------------------------------
        runs = []
        with open(LOG, encoding="utf-8") as fh:
            for line in fh:
                try:
                    runs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        prov = []
        for run in runs:
            for o in run.get("outputs", []):
                prov.append(dict(
                    artifact=os.path.relpath(o["path"], REPO) if os.path.isabs(o["path"]) else o["path"],
                    rows=o.get("rows", ""),
                    run_id=run["run_id"], script=run["script"], status=run["status"],
                    finished_utc=run["finished_utc"], git_sha=run["git_sha"],
                    snapshot=run.get("inputs", {}).get("snapshot", ""),
                ))
        pv = pd.DataFrame(prov).drop_duplicates(subset=["artifact"], keep="last")
        pv.to_csv(os.path.join(OUTDIR, "PROVENANCE.csv"), index=False)
        r.note(f"provenance: {len(pv)} artifacts across {len(runs)} runs")

        man = kfreeze.manifest()
        with open(os.path.join(OUTDIR, "PROVENANCE.md"), "w", encoding="utf-8") as fh:
            fh.write("# Provenance appendix\n\n")
            fh.write(f"Assembled {datetime.now(timezone.utc).isoformat()}\n\n")
            fh.write("## Frozen warehouse snapshot\n\n")
            fh.write(f"- **Snapshot id:** `{man['snapshot_id']}`\n")
            fh.write(f"- **Frozen at:** {man['frozen_at_utc']}\n")
            fh.write(f"- **Source:** {man['source']}\n\n")
            fh.write("| Table | Rows | sha256 (first 16) |\n|---|---|---|\n")
            for t, meta in man["tables"].items():
                fh.write(f"| `{t}` | {meta['rows']:,} | `{meta['sha256'][:16]}` |\n")
            fh.write("\n## Artifacts and the runs that produced them\n\n")
            fh.write(pv[["artifact", "rows", "script", "run_id", "status"]]
                     .to_markdown(index=False))
            fh.write("\n\n## External sources\n\n")
            fh.write("Every externally sourced fact carries its URL in the file that "
                     "uses it:\n\n")
            fh.write("- Cap thresholds: `offseason/data/league_year_constants.json`, "
                     "`source` field per season.\n")
            fh.write("- Kuminga terms and the Hawks option: "
                     "`kuminga/data/transaction_supplement.csv`, "
                     "`source_url_1` / `source_url_2`.\n")
            fh.write("- Dead-money resolution: "
                     "`kuminga/data/dup_resolution_verified.json`, `sources` per player.\n")
            fh.write("- Injuries: `kuminga/data/injuries_2026_27.csv`, `source_url`.\n")
            fh.write("- Traded picks: "
                     "`kuminga/data/traded_picks_2026_offseason.csv`, `source_url`.\n")

        r.output(os.path.join(OUTDIR, "T1_all30_before_after.csv"), rows=len(t1))
        r.output(os.path.join(OUTDIR, "T2_west_ranking.csv"), rows=len(west))
        r.output(os.path.join(OUTDIR, "PROVENANCE.csv"), rows=len(pv))

    print()
    cols = ["team_abbr", "conf", "rank_baseline", "rank_current", "rank_change",
            "title_baseline_mean_pct", "title_current_mean_pct",
            "title_delta_min_pp", "title_delta_max_pp", "sign_agreement"]
    print(t1[cols].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
