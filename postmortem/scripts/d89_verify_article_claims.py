#!/usr/bin/env python3
"""D89: re-test the two RAPM claims in the article draft on the refit.

D88 left both claims in `articles/02_how_they_got_here_first_draft.md` as UNVERIFIED,
because they are fitted on possession points and the possession grain still had the
and-one defect. The grain is fixed (D89) and postmortem's own RAPM is refit on it, so the
claims can be tested on their own sample rather than on a different one.

  CLAIM 1 (line 116) "Gobert's offensive impact, measured by RAPM, has gone from positive
                      in 2023-24 to clearly negative in 2025-26."
  CLAIM 2 (line 120) "By the 2025-26-only version of that RAPM metric, DiVincenzo had been
                      the highest-impact player in the entire league sample."

LABELS, decided before looking:
  VERIFIED     the claim holds on the refit, and the margin it needs is larger than the
               spread of the figures it is being compared against (see each test).
  REFUTED      the refit contradicts it.
  UNVERIFIABLE the refit neither supports nor contradicts it: the margin is inside the
               noise the metric itself carries, so the sentence cannot be made safe by
               recomputing, only by widening the sample.

Before values come from the frozen pre-D89 tables in
`outputs/tables/q2_localize/pre_d89/`, after values from the refit.

    python postmortem/scripts/d89_verify_article_claims.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from analyses.q2_localize import config  # noqa: E402

T = config.TABLE_DIR
PRE = T / "pre_d89"
OUT = os.path.join(ROOT, "outputs", "findings", "lineup_pipeline",
                   "04_d89_rapm_refit_and_article_claims.md")
GOBERT, DDV = config.GOBERT_ID, config.DIVINCENZO_ID


def load(name: str, pre: bool) -> pd.DataFrame:
    p = (PRE if pre else T) / name
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()


def val(df: pd.DataFrame, pid: int, col: str):
    if df.empty:
        return np.nan
    r = df[df.player_id == pid]
    return float(r.iloc[0][col]) if len(r) else np.nan


def main():
    rows = []
    seasons = {}
    for yr in (2023, 2024, 2025):
        seasons[yr] = dict(before=load("rapm_%d_only.csv" % yr, True),
                           after=load("rapm_%d_only.csv" % yr, False))

    print("=== CLAIM 1: Gobert's offensive RAPM, positive in 2023-24 to clearly negative in 2025-26")
    g = {}
    for yr in (2023, 2024, 2025):
        for basis in ("before", "after"):
            g[(yr, basis)] = val(seasons[yr][basis], GOBERT, "off_rapm")
        print("  %s  off RAPM before %+6.2f -> after %+6.2f"
              % (config.season_label(yr), g[(yr, "before")], g[(yr, "after")]))
    # the spread the claim has to beat: the SD of offensive RAPM across the fit
    sd25 = seasons[2025]["after"].off_rapm.std() if not seasons[2025]["after"].empty else np.nan
    start_pos = g[(2023, "after")] > 0
    end_neg = g[(2025, "after")] < 0
    # "clearly" negative: at least a quarter of the fit's own spread below zero
    clearly = end_neg and abs(g[(2025, "after")]) > 0.25 * sd25
    if start_pos and clearly:
        label1 = "VERIFIED"
    elif start_pos and end_neg:
        label1 = "UNVERIFIABLE"
    elif not end_neg:
        label1 = "REFUTED"
    else:
        label1 = "REFUTED"
    print("  2025-26 fit spread (SD of offensive RAPM) %.2f; a quarter of it is %.2f"
          % (sd25, 0.25 * sd25))
    print("  positive in 2023-24: %s | negative in 2025-26: %s | clearly: %s -> %s"
          % (start_pos, end_neg, clearly, label1))
    rows.append(("Claim 1: Gobert offence positive 2023-24 to clearly negative 2025-26", label1))

    print("\n=== CLAIM 2: DiVincenzo the highest-impact player in the 2025-26-only fit")
    for basis in ("before", "after"):
        df = seasons[2025][basis]
        if df.empty:
            print("  %s: table missing" % basis)
            continue
        d = df.sort_values("net_rapm", ascending=False).reset_index(drop=True)
        rank = int(d.index[d.player_id == DDV][0]) + 1 if (d.player_id == DDV).any() else -1
        top = d.iloc[0]
        ddv = d[d.player_id == DDV]
        ddv_net = float(ddv.iloc[0].net_rapm) if len(ddv) else np.nan
        print("  %-6s n=%d | DiVincenzo rank %d at %+.2f | leader %s at %+.2f"
              % (basis, len(d), rank, ddv_net, top.player_name[:22], top.net_rapm))
        if basis == "after":
            gap = float(top.net_rapm) - ddv_net
            # the margin to beat: how tightly the top of the fit is packed
            top10_spread = float(d.head(10).net_rapm.std())
            print("  gap to the leader %.2f; spread of the top ten %.2f" % (gap, top10_spread))
            if rank == 1:
                label2 = "VERIFIED" if gap == 0 else "VERIFIED"
            elif gap < top10_spread:
                label2 = "UNVERIFIABLE"
            else:
                label2 = "REFUTED"
            print("  -> %s" % label2)
            rows.append(("Claim 2: DiVincenzo highest net RAPM in the 2025-26-only fit", label2))

    print("\n=== Wolves rotation, 2025-26-only net RAPM, before and after")
    names = {config.ANT_ID: "Anthony Edwards", GOBERT: "Rudy Gobert", config.NAZ_ID: "Naz Reid",
             config.RANDLE_ID: "Julius Randle", config.MCDANIELS_ID: "Jaden McDaniels",
             config.CONLEY_ID: "Mike Conley", DDV: "Donte DiVincenzo",
             config.DOSUNMU_ID: "Ayo Dosunmu"}
    tab = []
    for pid, nm in names.items():
        b = val(seasons[2025]["before"], pid, "net_rapm")
        a = val(seasons[2025]["after"], pid, "net_rapm")
        bo = val(seasons[2025]["before"], pid, "off_rapm")
        ao = val(seasons[2025]["after"], pid, "off_rapm")
        tab.append(dict(player=nm, net_before=b, net_after=a, d_net=a - b,
                        off_before=bo, off_after=ao, d_off=ao - bo))
        print("  %-20s net %+6.2f -> %+6.2f (%+5.2f) | off %+6.2f -> %+6.2f (%+5.2f)"
              % (nm, b, a, a - b, bo, ao, ao - bo))

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("# D89. Postmortem RAPM refit, and the two article claims re-tested\n\n")
        fh.write("*Possession points are now credited to the team that scored them "
                 "(`lib/lineups.py`), so RAPM is refit on the corrected grain. Before values "
                 "are the frozen pre-D89 tables.*\n\n## The two claims\n\n")
        for claim, label in rows:
            fh.write("- **%s** -> **%s**\n" % (claim, label))
        fh.write("\n## Gobert's offensive RAPM by season-only fit\n\n")
        fh.write("| season | before | after |\n|---|---:|---:|\n")
        for yr in (2023, 2024, 2025):
            fh.write("| %s | %+.2f | %+.2f |\n"
                     % (config.season_label(yr), g[(yr, "before")], g[(yr, "after")]))
        fh.write("\n## Wolves rotation, 2025-26-only fit\n\n")
        fh.write(pd.DataFrame(tab).round(2).to_markdown(index=False) + "\n")
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
