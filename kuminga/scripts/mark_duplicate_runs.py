#!/usr/bin/env python3
"""D86: mark the run-log entries that share a run id, once.

`runlog` now reserves ids, so a collision cannot happen again (see `lib/runlog.py`). The
ids already in the log still collide, and a figure citing one of them is ambiguous about
which run produced it. This marks every record in a colliding group, so the gate in
`reconcile_figures.py` can fail on any duplicate that is NOT marked.

  noise_floor    two runs (un-aged, then aged) started in the same second. Both are
                 SUPERSEDED by later runs with distinct ids, and the marking says by which.
  build_fcurve   four forks run in parallel, one id between them. Not superseded: each
                 record is real work, and they are legacy duplicates.

  G1  no figure on `final_numbers.csv` cites a duplicated id. If one did, this script
      refuses to run and the figure has to be rebuilt first.
  G2  the rewritten log has the same number of records, and every record keeps its
      fields; only the marking fields are added.

    python kuminga/scripts/mark_duplicate_runs.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

LOG = os.path.join(REPO, "kuminga", "logs", "runs.jsonl")
BACKUP = os.path.join(REPO, "kuminga", "logs", "backup", "runs_pre_d86.jsonl")
SHEET = os.path.join(REPO, "kuminga", "outputs", "final_numbers.csv")

LEGACY_REASON = {
    "build_fcurve": "four forks ran in parallel and shared one start second; each record "
                    "is a separate fork, all four are real",
    "noise_floor": "the un-aged and aged runs started in the same second",
}


def main():
    before = open(LOG, "rb").read()
    with runlog.run("mark_duplicate_runs",
                    inputs={"log": LOG, "sha256_before": hashlib.sha256(before).hexdigest()}) as r:
        records = [json.loads(line) for line in before.decode("utf-8").splitlines() if line.strip()]
        counts: dict[str, int] = {}
        for d in records:
            counts[d["run_id"]] = counts.get(d["run_id"], 0) + 1
        dups = {k: v for k, v in counts.items() if v > 1}
        r.note("%d records, %d distinct ids, %d ids duplicated (%d extra records)"
               % (len(records), len(counts), len(dups), sum(dups.values()) - len(dups)))

        # G1: nothing published may cite an ambiguous id
        sheet = pd.read_csv(SHEET, dtype=str)
        cited = [k for k in dups if (sheet.run_id == k).any()]
        r.note("G1: figures on the sheet citing a duplicated id: %s" % (cited or "none"))
        if cited:
            raise RuntimeError("G1 failed: the sheet cites duplicated run ids %s" % cited)

        # the superseding run for each duplicated noise_floor record, by basis
        latest = {}
        for d in records:
            if d["script"] == "noise_floor" and counts[d["run_id"]] == 1 and d["status"] == "ok":
                latest[(d.get("inputs") or {}).get("basis")] = d["run_id"]
        r.note("latest distinct noise_floor run by basis: %s" % latest)

        marked = 0
        for d in records:
            if counts[d["run_id"]] == 1:
                continue
            d["duplicate_id_legacy"] = True
            d["duplicate_id_count"] = counts[d["run_id"]]
            d["duplicate_id_reason"] = LEGACY_REASON.get(d["script"], "shared a start second")
            if d["script"] == "noise_floor":
                basis = (d.get("inputs") or {}).get("basis")
                d["superseded_by"] = latest.get(basis)
                d["superseded_reason"] = ("re-run after D85 with a distinct id; the D85 figures "
                                          "come from the superseding run")
            marked += 1
        r.note("marked %d records across %d ids" % (marked, len(dups)))
        for k, v in sorted(dups.items()):
            sup = [d.get("superseded_by") for d in records if d["run_id"] == k]
            r.note("  %s x%d%s" % (k, v, " -> superseded by %s" % sup[0] if sup[0] else ""))

        os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
        shutil.copy2(LOG, BACKUP)
        body = "".join(json.dumps(d) + "\n" for d in records)
        with open(LOG, "w", encoding="utf-8") as fh:
            fh.write(body)

        # G2: same records, nothing lost
        after = [json.loads(line) for line in open(LOG, encoding="utf-8") if line.strip()]
        keys_before = [(d["run_id"], d["script"], d["started_utc"]) for d in records]
        keys_after = [(d["run_id"], d["script"], d["started_utc"]) for d in after]
        r.note("G2: %d records before, %d after, identical keys: %s"
               % (len(records), len(after), keys_before == keys_after))
        if keys_before != keys_after:
            raise RuntimeError("G2 failed: the rewritten log does not match record for record")
        r.note("backup of the pre-D86 log: %s (sha256 %s)"
               % (os.path.relpath(BACKUP, REPO), hashlib.sha256(before).hexdigest()[:16]))
        r.output(LOG, rows=len(after))
        r.output(BACKUP, rows=len(records))


if __name__ == "__main__":
    main()
