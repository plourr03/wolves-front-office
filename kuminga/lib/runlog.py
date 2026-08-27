"""Run IDs and a run log for the Kuminga project.

Every script that produces an artifact opens a run, logs its inputs (snapshot ids,
source files) and outputs, and closes it. The run id is what the provenance appendix
maps published numbers back to.

    from kuminga.lib import runlog
    with runlog.run("build_roster_snapshot", inputs={"snapshot": sid}) as r:
        ...
        r.output("kuminga/data/roster_snapshot_2026_27.csv", rows=len(df))
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
LOG_PATH = os.path.join(REPO, "kuminga", "logs", "runs.jsonl")


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO, text=True,
            stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


class _Run:
    def __init__(self, name: str, inputs: dict | None):
        ts = datetime.now(timezone.utc)
        self.run_id = f"{name}_{ts.strftime('%Y%m%dT%H%M%SZ')}"
        self.name = name
        self.started = ts.isoformat()
        self.inputs = inputs or {}
        self.outputs: list[dict] = []
        self.notes: list[str] = []
        self.status = "running"
        self.error = None

    def output(self, path: str, **meta):
        self.outputs.append({"path": path, **meta})

    def note(self, msg: str):
        self.notes.append(msg)
        print(f"  [{self.run_id}] {msg}", flush=True)


@contextmanager
def run(name: str, inputs: dict | None = None):
    r = _Run(name, inputs)
    print(f"[run] {r.run_id}", flush=True)
    try:
        yield r
        r.status = "ok"
    except Exception:
        r.status = "failed"
        r.error = traceback.format_exc(limit=6)
        raise
    finally:
        rec = {
            "run_id": r.run_id, "script": r.name, "status": r.status,
            "started_utc": r.started,
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "git_sha": _git_sha(), "python": sys.version.split()[0],
            "inputs": r.inputs, "outputs": r.outputs, "notes": r.notes,
            "error": r.error,
        }
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"[run] {r.run_id} -> {r.status}", flush=True)
