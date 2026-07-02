"""Carry annotations from outputs/star_spells_review_annotated.csv onto the
regenerated review CSV (post arrival-year bugfix).

Mapping key: (player_id, franchise_id) + season-span overlap. Where multiple
annotated rows map to one regenerated spell (the merged pairs), AGENT_FIX
directives are marked resolved_by_builder; any other annotations concatenate.
The annotated source file is never modified.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "outputs"
ANNOTATED = OUT / "star_spells_review_annotated.csv"
REVIEW = OUT / "star_spells_review.csv"


def pid_of(spell_id: str) -> str:
    return spell_id.rsplit("_", 1)[0]


def main():
    ann = pd.read_csv(ANNOTATED)
    new = pd.read_csv(REVIEW)
    ann["player_id"] = ann.spell_id.map(pid_of)
    new["player_id"] = new.spell_id.map(pid_of)

    carried, resolved, unmapped = 0, 0, []
    new["claude_suggestion"] = ""
    new["claude_reason"] = ""
    new["auto_fixed_note"] = ""

    for _, a in ann.iterrows():
        has_sugg = isinstance(a.claude_suggestion, str) and a.claude_suggestion.strip()
        has_bobby = (isinstance(a.get("bobby_correction"), str) and str(a.bobby_correction).strip()) or \
                    (isinstance(a.get("bobby_notes"), str) and str(a.bobby_notes).strip())
        if not has_sugg and not has_bobby:
            continue
        cand = new[(new.player_id == a.player_id) & (new.franchise_id == a.franchise_id)
                   & (new.entry_season <= a.exit_season) & (new.exit_season >= a.entry_season)]
        if cand.empty:
            unmapped.append(a.spell_id)
            continue
        idx = cand.index[0]
        if has_sugg and a.claude_suggestion.strip().startswith("AGENT_FIX"):
            note = f"[{a.spell_id}: {a.claude_suggestion.strip()} -> resolved by builder fix]"
            new.at[idx, "auto_fixed_note"] = (new.at[idx, "auto_fixed_note"] + " " + note).strip()
            resolved += 1
            continue
        if has_sugg:
            sep = " | " if new.at[idx, "claude_suggestion"] else ""
            new.at[idx, "claude_suggestion"] += sep + a.claude_suggestion.strip()
            reason = a.claude_reason if isinstance(a.claude_reason, str) else ""
            new.at[idx, "claude_reason"] += (sep + reason.strip()) if reason.strip() else ""
            carried += 1
        if has_bobby:
            for col in ("bobby_correction", "bobby_notes"):
                val = a.get(col)
                if isinstance(val, str) and val.strip():
                    new.at[idx, col] = val.strip()

    new = new.drop(columns=["player_id"])
    new.to_csv(REVIEW, index=False)
    print(f"carried {carried} annotations; {resolved} AGENT_FIX rows resolved by the "
          f"builder fix; {len(unmapped)} unmapped: {unmapped}")


if __name__ == "__main__":
    main()
