#!/usr/bin/env python3
"""The full kuminga chain, as a committed script instead of a scratch shell file.

The D70 chain ran from a throwaway `chain_d70.sh` that is not in the repo, so the only
record of it was the run log. This is the same sequence, explicit and re-runnable.

  UN-AGED LEG   roster, rotations, strengths, sim, the four 200k f-curves in parallel,
                merge, both Shapley variants (team-rank and pooled), slot comparison,
                slot robustness, slot analysis, player option, seeds, counterfactuals,
                eval_signing, green_kept, lede_loophole, outputs, Williams sensitivity,
                W1c, N2, M4, noise floor, market, F4, champions.
  SNAPSHOT      the un-aged artifacts are copied to outputs/preaging BEFORE the steps
                that read that copy rather than the live one. `noise_floor`, `market_devig`
                and `f4_per_view_disagreement` all read outputs/preaging (it exists so an
                aged run cannot race them), so a snapshot taken at the end of the leg would
                feed them the PREVIOUS run's inputs. That ordering was wrong in the first
                version of this script and is the reason it is explicit here.
  AGED LEG      KUMINGA_AGING=1: strengths, sim, f-curves, merge, both Shapley variants,
                slot robustness, green_kept, seeds, aged noise floor. Scripts that take
                `--aged` write into outputs/aged themselves (D85/D86); the rest write to
                outputs and are copied into outputs/aged. `noise_floor --aged` reads
                outputs/aged, so that copy happens BEFORE it runs, not after the leg.
  RESTORE       the un-aged snapshot goes back over outputs.
  GATES         aging gate, D85 before/after record, D87 allocator agreement, backtest,
                then the sheet, both rendered documents and the reconcile gate.

The f-curve is the long pole: four forks, each about two and a half hours at 200,000
simulations, run concurrently. Budget five hours for the whole chain.

    python kuminga/scripts/chain.py --dry-run
    python kuminga/scripts/chain.py --nsims 200000
    python kuminga/scripts/chain.py --from shapley        # resume at a step
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "kuminga", "outputs")
PREAGING = os.path.join(OUT, "preaging")
AGED = os.path.join(OUT, "aged")
SNAP = os.path.join(OUT, ".chain_snapshot")
RESTORE_UNAGED = os.path.join(OUT, "_restore_unaged")
LOG = os.path.join(REPO, "kuminga", "logs", "chain_%s.log" % time.strftime("%Y%m%dT%H%M%SZ"))
FORKS = ["consensus", "rapm", "box", "darko"]

# the artifacts the aged leg regenerates, and therefore the ones to snapshot and to file
# under outputs/aged afterwards. Scripts with their own --aged flag are not in this list.
AGED_SET = ["team_strengths_2026_27.csv", "sim_all30_2026_27.csv", "fcurve_min.csv",
            "slot_robustness.csv", "green_kept.csv", "seed_distribution.csv",
            "slot_constrained.csv", "player_option.csv", "rotations_2026_27.csv",
            "aging_curve_nosurv.csv", "S1_shapley_slot_comparison.csv"]


def step(name, args=None, env=None, parallel=False):
    return dict(name=name, args=args or [], env=env or {}, parallel=parallel)


def plan(nsims: int):
    """Segments, in order. A snapshot falls between segments, never inside one."""
    def fcurves(env_extra=None, tag=""):
        out = []
        for f in FORKS:
            env = {"KUMINGA_FCURVE_FORK": f, "KUMINGA_FCURVE_NSIMS": str(nsims)}
            env.update(env_extra or {})
            s = step("build_fcurve", [], env, parallel=True)
            s["label"] = "build_fcurve[%s%s]" % (f, tag)
            out.append(s)
        return out

    # un-aged, everything that WRITES the un-aged basis
    unaged_write = [
        step("adapt_roster_v3"), step("build_rotations"), step("build_strengths"),
        step("run_sim"), *fcurves(), step("merge_fcurve_parts"),
        step("shapley"), step("shapley", ["--pooled"]),
        step("compare_slot_shapley"), step("slot_robustness"), step("slot_analysis"),
        step("player_option"), step("seed_distribution"), step("counterfactuals"),
        step("eval_signing"), step("green_kept"), step("lede_loophole"),
        step("build_outputs"), step("williams_minutes_sensitivity"), step("w1c_decompose"),
        step("n2_path"), step("m4_lineup_study"),
    ]
    # un-aged, everything that READS outputs/preaging and so must run after the snapshot
    unaged_read = [
        step("noise_floor"), step("market_devig"), step("f4_per_view_disagreement"),
        step("champions_table"), step("backtest_calibration"),
    ]
    aged_env = {"KUMINGA_AGING": "1"}
    # the aged basis is built in outputs/ (these scripts have no --aged flag and read the
    # top level), then filed under outputs/aged
    aged_write = [
        step("build_strengths", [], aged_env), step("run_sim", [], aged_env),
        *fcurves(aged_env, ",aged"), step("merge_fcurve_parts", [], aged_env),
    ]
    # `shapley --aged` READS outputs/aged for its f-curve and strengths (D85), so the file
    # step has to come first or it prices the aged game on the previous run's aged inputs.
    # That was wrong in the second version of this script; the r5 gate caught it.
    aged_write_b = [
        step("shapley", ["--aged"], aged_env), step("shapley", ["--pooled", "--aged"], aged_env),
        step("slot_robustness", [], aged_env), step("green_kept", [], aged_env),
        step("seed_distribution", [], aged_env),
    ]
    # also reads outputs/aged, and needs the aged slot_robustness filed there
    aged_read = [step("noise_floor", ["--aged"], aged_env)]
    gates = [
        step("w2_aging_gate"), step("r5_shapley_williams"), step("r5_honesty_rail_bases"),
        step("r2_departures"), step("r7_allocator_agreement"),
        step("build_final_numbers"), step("render_piece"), step("reconcile_figures"),
    ]
    return unaged_write, unaged_read, aged_write, aged_write_b, aged_read, gates


def run(steps, dry, log):
    """Run steps in order; consecutive parallel steps are launched together."""
    i = 0
    while i < len(steps):
        batch = [steps[i]]
        if steps[i]["parallel"]:
            while i + 1 < len(steps) and steps[i + 1]["parallel"]:
                i += 1
                batch.append(steps[i])
        procs = []
        for s in batch:
            label = s.get("label", s["name"])
            cmd = [sys.executable, os.path.join(HERE, s["name"] + ".py")] + s["args"]
            env = dict(os.environ)
            env.setdefault("KUMINGA_AGING", "0")
            env.update(s["env"])
            line = "%s  %s %s" % (label, " ".join(s["args"]),
                                  " ".join("%s=%s" % kv for kv in s["env"].items()))
            print("[chain] %s" % line, flush=True)
            log.write("[%s] START %s\n" % (time.strftime("%H:%M:%S"), line))
            log.flush()
            if dry:
                continue
            procs.append((label, s, subprocess.Popen(cmd, env=env, cwd=REPO,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.STDOUT, text=True)))
        for label, s, p in procs:
            out, _ = p.communicate()
            tail = "\n".join(out.strip().splitlines()[-4:])
            log.write("[%s] %s rc=%d\n%s\n" % (time.strftime("%H:%M:%S"), label, p.returncode, tail))
            log.flush()
            print("[chain] %s -> rc=%d" % (label, p.returncode), flush=True)
            if p.returncode != 0:
                print(out[-4000:], flush=True)
                raise SystemExit("chain failed at %s" % label)
        i += 1


def copy_set(src, dst, names, log):
    os.makedirs(dst, exist_ok=True)
    done = []
    for n in names:
        s = os.path.join(src, n)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(dst, n))
            done.append(n)
    log.write("copied %d files %s -> %s: %s\n"
              % (len(done), os.path.relpath(src, REPO), os.path.relpath(dst, REPO), done))
    log.flush()
    print("[chain] copied %d files to %s" % (len(done), os.path.relpath(dst, REPO)), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsims", type=int, default=200000)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--from", dest="from_step", default=None,
                    help="skip every step before this one (by name or label)")
    ap.add_argument("--skip-aged", action="store_true", help="un-aged leg and gates only")
    args = ap.parse_args()

    unaged_write, unaged_read, aged_write, aged_write_b, aged_read, gates = plan(args.nsims)
    segments = [("UN-AGED, WRITING", unaged_write), ("snapshot->preaging", None),
                ("UN-AGED, READING THE SNAPSHOT", unaged_read)]
    if not args.skip_aged:
        segments += [("AGED, WRITING", aged_write), ("file->aged", None),
                     ("AGED, ATTRIBUTION AND SLOTS", aged_write_b), ("file->aged", None),
                     ("AGED, READING", aged_read), ("restore un-aged", None)]
    segments += [("GATES AND OUTPUTS", gates)]

    if args.from_step:
        names = [s.get("label", s["name"]) for _, ss in segments if ss for s in ss] + \
                [s["name"] for _, ss in segments if ss for s in ss]
        if args.from_step not in names:
            raise SystemExit("--from %s is not a step in the chain" % args.from_step)
        seen = False
        cut = []
        for label, ss in segments:
            if ss is None:
                if seen:
                    cut.append((label, ss))
                continue
            keep = []
            for s in ss:
                if not seen and args.from_step in (s["name"], s.get("label")):
                    seen = True
                if seen:
                    keep.append(s)
            if keep:
                cut.append((label, keep))
        segments = cut

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as log:
        t0 = time.time()
        log.write("chain start %s, nsims=%d\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ"), args.nsims))
        print("[chain] log: %s" % os.path.relpath(LOG, REPO), flush=True)
        if not args.dry_run:
            copy_set(OUT, SNAP, sorted(f for f in os.listdir(OUT)
                                       if f.endswith((".csv", ".json", ".md"))), log)
        preaging_set = AGED_SET + ["shapley_min.csv", "shapley_min_POOLED.csv",
                                   "named_scenarios.csv", "named_scenarios_POOLED.csv",
                                   "shapley_order_spread.csv", "shapley_order_spread_POOLED.csv"]
        for label, steps in segments:
            print("[chain] === %s ===" % label, flush=True)
            if steps is not None:
                run(steps, args.dry_run, log)
                continue
            if args.dry_run:
                continue
            if label == "snapshot->preaging":
                copy_set(OUT, PREAGING, preaging_set, log)
                # `_restore_unaged` is the un-aged snapshot the OLD chain left behind, and
                # n4_versatility_index and n5_fragility read it (n5 gates on it matching
                # preaging). Refresh it here or those two keep scoring the previous chain.
                copy_set(OUT, RESTORE_UNAGED,
                         sorted(f for f in os.listdir(OUT) if f.endswith((".csv", ".json"))), log)
            elif label == "file->aged":
                copy_set(OUT, AGED, AGED_SET, log)
            elif label == "restore un-aged":
                copy_set(OUT, AGED, AGED_SET, log)       # catch anything the aged leg added
                copy_set(PREAGING, OUT, AGED_SET, log)   # put the un-aged basis back
        el = time.time() - t0
        log.write("chain done in %.0fs\n" % el)
        print("[chain] done in %.1f minutes" % (el / 60), flush=True)


if __name__ == "__main__":
    main()
