"""ON-2: PROVISIONAL spells import (overnight directive 2026-07-01).

Applies review decisions from outputs/star_spells_review.csv (Bobby's
annotated pass, carried onto the regenerated sheet) to the candidate
spell-season rows:

  KEEP / blank            spell retained
  PRUNE                   spell dropped (role-player BPM artifacts)
  SET exit_type=X         last-row event flags overridden
  BORDERLINE (your call)  PROVISIONALLY KEPT, tagged borderline_kept=True
                          (sensitivity fit excludes them; final call is
                          Bobby's at the M2 freeze)
  UPDATE July 6: ...      NOT applied (moratorium); tagged pending_july6

Output: data/staged/star_spells_provisional.parquet, tagged
provisional=True with a freeze hash printed and stored alongside
(star_spells_provisional.meta.json). NOT the final M2 freeze.

FINAL MODE (--final, the July-6 step-2 button): requires
trade_terms.yaml verified_post_july6=true; additionally applies
config/borderline_decisions.csv (Bobby's 21 accepted leans) and the three
pending_july6 exit updates (Giannis/Kawhi/LaMelo -> departure), writes
data/staged/star_spells_final.parquet with its own freeze hash, and
discloses which corrected spells sit in the sealed 8.2 holdout
(label correction, not peeking -- disclosed per the sequencing amendment).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGED = PROJECT_ROOT / "data" / "staged"
REVIEW = PROJECT_ROOT / "outputs" / "star_spells_review.csv"

SET_RE = re.compile(r"SET exit_type=(\w+)")


def holdout_disclosure(spell_ids: list[str]) -> str:
    """Which of the corrected spells fall in the sealed 8.2 holdout
    (deterministic from the fixed holdout seed and the provisional spell
    list -- computable in advance, disclosed on the record)."""
    import yaml
    params = yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())
    prov = pd.read_parquet(STAGED / "star_spells_provisional.parquet")
    rng = np.random.default_rng(params["model_b"]["holdout_seed"])
    spells = np.array(sorted(prov.spell_id.unique()))
    test = set(rng.choice(spells, int(0.2 * len(spells)), replace=False))
    touched = [s for s in spell_ids if s in test]
    return (f"sealed-holdout disclosure: {touched or 'none'} of the July-6 "
            f"corrected spells are holdout members")


def final_freeze():
    import yaml
    terms = yaml.safe_load((PROJECT_ROOT / "config" / "trade_terms.yaml").read_text())
    if not terms.get("verified_post_july6", False):
        raise RuntimeError("FINAL freeze requires verified_post_july6=true "
                           "(July-6 step 1 first)")
    sp = pd.read_parquet(STAGED / "star_spells_provisional.parquet")
    dec = pd.read_csv(PROJECT_ROOT / "config" / "borderline_decisions.csv")
    prune = set(dec[dec.decision == "PRUNE"].spell_id)
    out = sp[~sp.spell_id.isin(prune)].copy()
    july6 = sorted(out[out.pending_july6].spell_id.unique())
    for spell_id in july6:
        idx = out[out.spell_id == spell_id].sort_values("season").index
        out.loc[idx[-1], ["event_departure", "event_retire", "censored"]] = [True, False, False]
    out["provisional"] = False
    h = hashlib.sha256(pd.util.hash_pandas_object(out, index=False).values.tobytes()).hexdigest()[:16]
    out.to_parquet(STAGED / "star_spells_final.parquet", index=False)
    disclosure = holdout_disclosure(july6)
    meta = {"tag": "FINAL", "freeze_hash": h, "n_spells": int(out.spell_id.nunique()),
            "n_rows": len(out), "borderline_pruned": sorted(prune),
            "july6_departures_applied": july6, "holdout_disclosure": disclosure}
    (STAGED / "star_spells_final.meta.json").write_text(json.dumps(meta, indent=1))
    print(f"FINAL freeze {h}: {meta['n_spells']} spells / {len(out)} rows; "
          f"{len(prune)} borderlines pruned; July-6 departures: {july6}")
    print(disclosure)


def main():
    if "--final" in sys.argv:
        final_freeze()
        return
    sp = pd.read_parquet(STAGED / "star_spell_seasons_candidate.parquet")
    rev = pd.read_csv(REVIEW)
    sugg = rev.set_index("spell_id").claude_suggestion.fillna("")

    pruned, set_applied, borderline, pending = [], [], [], []
    sp["borderline_kept"] = False
    sp["pending_july6"] = False
    for spell_id, s in sugg.items():
        s = s.strip()
        if not s or s == "KEEP" or s.startswith("KEEP"):
            continue
        if s.startswith("PRUNE"):
            pruned.append(spell_id)
        elif s.startswith("BORDERLINE"):
            sp.loc[sp.spell_id == spell_id, "borderline_kept"] = True
            borderline.append(spell_id)
        elif s.startswith("UPDATE July 6"):
            sp.loc[sp.spell_id == spell_id, "pending_july6"] = True
            pending.append(spell_id)
        elif m := SET_RE.search(s):
            verdict = m.group(1).lower()
            idx = sp[sp.spell_id == spell_id].sort_values("season").index
            if len(idx) == 0:
                print(f"WARNING: SET for unknown spell {spell_id}")
                continue
            last = idx[-1]
            sp.loc[last, ["event_departure", "event_retire", "censored"]] = [
                verdict == "departure", verdict == "retire", verdict == "censored"]
            set_applied.append((spell_id, verdict))
        else:
            print(f"WARNING: unrecognized suggestion for {spell_id}: {s!r} (kept as-is)")

    out = sp[~sp.spell_id.isin(pruned)].reset_index(drop=True)
    out["provisional"] = True

    h = hashlib.sha256(pd.util.hash_pandas_object(out, index=False).values.tobytes()).hexdigest()[:16]
    out.to_parquet(STAGED / "star_spells_provisional.parquet", index=False)
    meta = {
        "tag": "PROVISIONAL", "freeze_hash": h,
        "n_spells": int(out.spell_id.nunique()), "n_rows": len(out),
        "pruned": pruned, "set_applied": set_applied,
        "borderline_kept": borderline, "pending_july6": pending,
        "note": ("BORDERLINE rows kept per overnight directive; final call is "
                 "Bobby's at the M2 freeze. July-6 exit updates NOT applied."),
    }
    (STAGED / "star_spells_provisional.meta.json").write_text(json.dumps(meta, indent=1))
    ev = out.groupby("spell_id").tail(1)
    print(f"PROVISIONAL freeze {h}: {meta['n_spells']} spells / {len(out)} rows "
          f"({len(pruned)} pruned, {len(set_applied)} SET applied, "
          f"{len(borderline)} borderline kept, {len(pending)} pending July 6)")
    print("exit mix:", {
        "departure": int(ev.event_departure.sum()),
        "retire": int(ev.event_retire.sum()),
        "censored": int(ev.censored.sum()),
        "uncoded": int((~ev.event_departure & ~ev.event_retire & ~ev.censored).sum()),
    })


if __name__ == "__main__":
    main()
