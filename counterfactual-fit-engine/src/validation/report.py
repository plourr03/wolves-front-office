"""The auto-generated validation report (spec section 9: every gate lands
here; failures produce decision memos, never silent retunes).

Assembles current gate status from committed artifacts only:
  G1  from outputs/reconciliation_panel_full.parquet via reconcile.summarize
      (AM-3 denominator, AM-4 strata, invariant labels), plus the
      quarantine census with every reason bucketed.
  G2  from outputs/rapm/g2_rapm_report.md if F2 has run (linked, not
      duplicated); marked PENDING otherwise.
  G3-G5  marked PENDING until their layers exist.

Usage: python -m src.validation.report
Writes outputs/validation_report.md with a generation stamp.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.stints.reconcile import summarize  # noqa: E402

OUT = FITENGINE_ROOT / "outputs" / "validation_report.md"
PANEL = FITENGINE_ROOT / "outputs" / "reconciliation_panel_full.parquet"
G2_REPORT = FITENGINE_ROOT / "outputs" / "rapm" / "g2_rapm_report.md"

G1_RECON = 0.995
G1_QUAR = 0.005


def g1_section() -> list[str]:
    lines = ["## G1: data integrity (Layer 0)", ""]
    if not PANEL.exists():
        return lines + ["PENDING: no full-panel scorecard.", ""]
    sc = pd.read_parquet(PANEL)
    summ = summarize(sc)
    lines.append(f"Full panel: {len(sc):,} games "
                 f"({int(sc.quarantined.sum())} quarantined).")
    lines.append("")
    lines.append("| stratum | games | quarantine | recon TRUE 0.5 | "
                 "recon relaxed | team secs (INVARIANT) | poss parity % "
                 "(PARTITION) | verdict |")
    lines.append("|---|---|---|---|---|---|---|---|")
    all_green = True
    for _, r in summ.iterrows():
        green = (r.recon_rate_TRUE_0p5 >= G1_RECON
                 and r.recon_rate_relaxed >= G1_RECON
                 and r.quarantine_rate < G1_QUAR)
        all_green &= bool(green)
        lines.append(
            f"| {r.stratum} | {r.games:,} | {r.quarantine_rate:.4%} "
            f"| {r.recon_rate_TRUE_0p5:.4%} | {r.recon_rate_relaxed:.4%} "
            f"| {r.team_seconds_exact_INVARIANT:.4f} "
            f"| {r.poss_parity_pct_PARTITION:.4f} "
            f"| {'GREEN' if green else 'FAIL'} |")
    lines.append("")
    lines.append(f"Gate bars: recon >= {G1_RECON:.1%} on BOTH criteria "
                 f"(primary seconds-precise, secondary truncation-aware), "
                 f"quarantine < {G1_QUAR:.1%}, pooled AND per stratum. "
                 f"G1 {'GREEN' if all_green else 'NOT GREEN'} on this "
                 "scorecard.")
    q = sc[sc.quarantined]
    if len(q):
        lines += ["", "Quarantine reasons (all read, none laundered; "
                      "AM-3 counts their player-games as failures):", ""]
        for reason, grp in q.groupby(q.error.str.slice(0, 60)):
            lines.append(f"- {len(grp)} game(s): {reason}...")
    return lines + [""]


def stub_section(name: str, detail: str) -> list[str]:
    return [f"## {name}", "", f"PENDING: {detail}", ""]


def main() -> None:
    lines = [
        "# fitengine validation report",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')} from "
        "committed artifacts. Gate FAILURES produce decision memos for "
        "Bobby; thresholds never move to make a row green.",
        "",
    ]
    lines += g1_section()
    if G2_REPORT.exists():
        lines += ["## G2: Layer 1 (skills)", "",
                  f"RAPM rows: see `{G2_REPORT.relative_to(FITENGINE_ROOT)}` "
                  "(YoY band 0.50-0.75 and top-20 face lists). Factor rows "
                  "PENDING until F3.", ""]
    else:
        lines += stub_section("G2: Layer 1 (skills)",
                              "F2 RAPM not yet run on this machine.")
    lines += stub_section("G3: Layer 2 (synergy, dev seasons)",
                          "no Layer 2 fits exist (F4).")
    lines += stub_section("G4: trade backtest",
                          "harness plumbing only; dev iteration at F5. "
                          "Sealed window untouched and unenumerated.")
    lines += stub_section("G5: deployment sanity", "F6.")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
