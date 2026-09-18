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
from datetime import datetime, timedelta, timezone

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


IDS_DIR = os.path.join(REPO, "kuminga", "logs", "ids")


def _id_for(name: str, ts: datetime) -> str:
    return f"{name}_{ts.strftime('%Y%m%dT%H%M%SZ')}"


def logged_ids() -> set[str]:
    """Every run id already in the log."""
    out = set()
    if not os.path.exists(LOG_PATH):
        return out
    with open(LOG_PATH, encoding="utf-8") as fh:
        for line in fh:
            try:
                out.add(json.loads(line)["run_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return out


def duplicate_ids() -> dict[str, int]:
    """Ids appearing more than once in the log, with their counts."""
    counts: dict[str, int] = {}
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as fh:
            for line in fh:
                try:
                    counts[json.loads(line)["run_id"]] = \
                        counts.get(json.loads(line)["run_id"], 0) + 1
                except (json.JSONDecodeError, KeyError):
                    continue
    return {k: v for k, v in counts.items() if v > 1}


def _reserve(name: str, ts: datetime, taken: set[str]) -> tuple[str, datetime, int]:
    """A run id no other run holds.

    D86: the id is the script name and the start time to the second, so two runs that
    start in the same second collided silently. It happened to `noise_floor` (un-aged and
    aged back to back) and to `build_fcurve` (four forks in parallel), and a duplicate id
    makes provenance ambiguous for every figure that cites it. The id is now RESERVED:
    an O_EXCL marker file, which is atomic across processes, plus the ids already in the
    log. On a collision the timestamp walks forward a second at a time, so the id keeps
    its shape (`script_YYYYmmddTHHMMSSZ`) and `started_utc` stays the true start.
    """
    os.makedirs(IDS_DIR, exist_ok=True)
    bumped = 0
    while True:
        rid = _id_for(name, ts)
        if rid not in taken:
            try:
                fd = os.open(os.path.join(IDS_DIR, rid), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return rid, ts, bumped
            except FileExistsError:
                pass
        ts = ts + timedelta(seconds=1)
        bumped += 1


class _Run:
    def __init__(self, name: str, inputs: dict | None):
        ts = datetime.now(timezone.utc)
        self.started = ts.isoformat()
        self.run_id, _, self.id_bumped_seconds = _reserve(name, ts, logged_ids())
        self.name = name
        self.inputs = inputs or {}
        self.outputs: list[dict] = []
        self.notes: list[str] = []
        self.status = "running"
        self.error = None

    def output(self, path: str, **meta):
        self.outputs.append({"path": path, **meta})

    def note(self, msg: str):
        self.notes.append(msg)
        # The Windows console is cp1252 and raises on any name carrying a diacritic,
        # which killed a run mid-way through printing a roster. A log line must never
        # be able to fail the job it is logging.
        line = f"  [{self.run_id}] {msg}"
        try:
            print(line, flush=True)
        except UnicodeEncodeError:
            enc = getattr(sys.stdout, "encoding", None) or "ascii"
            print(line.encode(enc, "replace").decode(enc, "replace"), flush=True)


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
        # D86: never append an id the log already holds. It cannot normally happen now
        # that ids are reserved, but a log edited or merged by hand could reintroduce one,
        # and the record is bumped rather than lost.
        if r.run_id in logged_ids():
            old = r.run_id
            ts = datetime.strptime(r.run_id.rsplit("_", 1)[1], "%Y%m%dT%H%M%SZ").replace(
                tzinfo=timezone.utc)
            r.run_id, _, extra = _reserve(r.name, ts + timedelta(seconds=1), logged_ids())
            r.id_bumped_seconds += extra + 1
            r.notes.append(f"run id {old} was already in the log; this run is {r.run_id}")
        if r.id_bumped_seconds:
            r.notes.append(f"run id timestamp bumped {r.id_bumped_seconds}s to keep ids unique "
                           f"(started_utc is the true start)")
        rec = {
            "run_id": r.run_id, "script": r.name, "status": r.status,
            "started_utc": r.started, "id_bumped_seconds": r.id_bumped_seconds,
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "git_sha": _git_sha(), "python": sys.version.split()[0],
            "inputs": r.inputs, "outputs": r.outputs, "notes": r.notes,
            "error": r.error,
        }
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"[run] {r.run_id} -> {r.status}", flush=True)
