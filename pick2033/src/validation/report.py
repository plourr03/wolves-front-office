"""Auto-generated validation report (spec Section 8 + Appendix A).
Collates every gate artifact in outputs/validation/ + sim manifests into
outputs/validation_report.md. Regenerate after any gate-relevant run."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VAL = PROJECT_ROOT / "outputs" / "validation"
SIMS = PROJECT_ROOT / "outputs" / "sims"
OUT = PROJECT_ROOT / "outputs" / "validation_report.md"

SECTIONS = [
    ("M0 cross-checks", ["m0_crosscheck.md"]),
    ("Gates 8.1 — Model A (trajectory)", ["model_a_backtests_v1_student_t.md",
                                          "model_a_backtests_v2_mixture.md",
                                          "model_a_gate_decision.md"]),
    ("Gates 8.2 — Model B (hazard) [PROVISIONAL]", ["model_b_hazard_PROVISIONAL.md",
                                                    "model_b_calibration_decision.md"]),
    ("Gates 8.3 — Model C (aging)", ["model_c_aging.md"]),
    ("Gates 8.4 — Engine D [PROVISIONAL]", ["early_84_rejudged.md",
                                            "engine_d_gates_PROVISIONAL.md",
                                            "engine_d_transient_decision.md"]),
    ("Model E1 — slot value", ["model_e1_slot_value.json"]),
]


def main():
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                            text=True, cwd=PROJECT_ROOT).stdout.strip()
    lines = [
        "# pick2033 validation report (auto-generated)",
        f"generated {datetime.now(timezone.utc).isoformat()} @ {commit}",
        "",
        "**Standing caveats:** Model B and all Engine D outputs are PROVISIONAL "
        "(borderline spells kept pending Bobby's final call; contract covariate "
        "omitted pending M2 backfill; July-6 exit updates pending). Swap PRICING "
        "is hard-gated on trade-terms verification (verified_post_july6: false). "
        "The 8.4 operationalization was chosen after a correlated preview, "
        "justified a priori; weaker than true pre-registration and disclosed.",
        "",
        "**Gate ruling log:** docs/decisions.md (8.1 accepted-with-red-gate; "
        "8.4 operationalization ratified with amendments; Model B calibration "
        "parked).",
        "",
        "**Counting convention:** season counts are INCLUSIVE (the panel is "
        "1980-2026 = 47 season-years, 1,314 franchise-season rows). Older "
        "memos saying '46 years' used span counting and stand under this "
        "note (declared 2026-07-02).",
        "",
    ]
    for title, files in SECTIONS:
        lines.append(f"\n---\n## {title}\n")
        for f in files:
            p = VAL / f
            if not p.exists():
                lines.append(f"*(missing artifact: {f})*")
                continue
            if f.endswith(".json"):
                d = json.loads(p.read_text())
                lines.append(f"```json\n{json.dumps(d, indent=1)[:1200]}\n```")
            else:
                lines.append(p.read_text(encoding="utf-8"))
    for mf in sorted(SIMS.glob("manifest_*.json")):
        m = json.loads(mf.read_text())
        lines.append(f"\n### Sim manifest: {m['variant']} ({m['tag']})\n"
                     f"gates: {m['gates']}  paths: {m['n_paths']}  seed: {m['seed']}")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"validation report -> {OUT} ({len(lines)} blocks)")


if __name__ == "__main__":
    main()
