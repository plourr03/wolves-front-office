#!/usr/bin/env python3
"""D90: what the RAPM refit did to the piece, before and after, figure by figure.

BEFORE is `outputs/.chain_snapshot`, the copy `chain.py` takes of every top-level output
before it runs. AFTER is the outputs the chain leaves behind. The aged simulation's before
state is not in that snapshot (the snapshot is top-level only), so it is read from git.

Reports, in the order the piece needs them:
  1. Minnesota's title number and its rank in each view, on both aging bases.
  2. The seven shipping verdicts in all four cells (two bases x two allocators).
  3. Charlotte and Boston: their disagreement with the market, on both bases.
  4. Whether the shipping set itself changed.

    python kuminga/scripts/d90_refit_before_after.py
"""
from __future__ import annotations

import os
import subprocess
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "kuminga", "outputs")
# the pre-refit state, preserved before the chain re-ran (the chain overwrites its own
# .chain_snapshot on every run, so the before baseline is kept separately)
SNAP = os.path.join(OUT, ".pre_refit_snapshot")
AGED = os.path.join(OUT, "aged")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "d90_refit_before_after.md")
FORKS = ["consensus", "rapm", "box", "darko"]
SHIPPED = ["ball_in", "reid_out", "ddv_injury", "A_c3_default_shannon", "C_mcdaniels_slides",
           "D_beringer_fills", "E_tight_rule_F_or_FC"]


def git_show(relpath: str) -> pd.DataFrame | None:
    """A tracked file as of HEAD, for the aged before-state."""
    try:
        txt = subprocess.check_output(["git", "show", "HEAD:" + relpath], cwd=REPO, text=True,
                                      stderr=subprocess.DEVNULL)
        from io import StringIO
        return pd.read_csv(StringIO(txt))
    except Exception:
        return None


def title_table(sim: pd.DataFrame) -> dict:
    """MIN title odds and rank per view, from a sim_all30 frame."""
    out = {}
    for f in FORKS:
        s = sim[sim.fork == f].sort_values("title_current", ascending=False).reset_index(drop=True)
        row = s[s.team_abbr == "MIN"]
        if row.empty:
            continue
        out[f] = dict(title=100 * float(row.iloc[0].title_current),
                      rank=int(row.index[row.team_abbr == "MIN"][0]) + 1)
    if out:
        out["mean"] = sum(v["title"] for v in out.values() if isinstance(v, dict)) / len(FORKS)
    return out


def main():
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    # ---- 1. Minnesota ------------------------------------------------------------
    pairs = [("un-aged", os.path.join(SNAP, "sim_all30_2026_27.csv"),
              os.path.join(OUT, "sim_all30_2026_27.csv"), None),
             ("aged", None, os.path.join(AGED, "sim_all30_2026_27.csv"),
              "kuminga/outputs/aged/sim_all30_2026_27.csv")]
    say("## 1. Minnesota's title number and rank per view")
    say()
    say("| basis | view | before | rank | after | rank |")
    say("|---|---|---:|---:|---:|---:|")
    for basis, bpath, apath, git_rel in pairs:
        before = pd.read_csv(bpath) if bpath and os.path.exists(bpath) else git_show(git_rel)
        after = pd.read_csv(apath) if os.path.exists(apath) else None
        if before is None or after is None:
            say("| %s | (missing) | | | | |" % basis)
            continue
        tb, ta = title_table(before), title_table(after)
        for f in FORKS:
            if f in tb and f in ta:
                say("| %s | %s | %.2f%% | %d | **%.2f%%** | **%d** |"
                    % (basis, f, tb[f]["title"], tb[f]["rank"], ta[f]["title"], ta[f]["rank"]))
        if "mean" in tb and "mean" in ta:
            say("| %s | **mean of four** | %.2f%% | | **%.2f%%** | |"
                % (basis, tb["mean"], ta["mean"]))
    say()

    # ---- 2. the seven verdicts in four cells ------------------------------------
    say("## 2. The shipping verdicts, all four cells")
    say()
    b = pd.read_csv(os.path.join(SNAP, "r7_allocator_verdicts.csv")).set_index("item")
    a_path = os.path.join(OUT, "r7_allocator_verdicts.csv")
    if os.path.exists(a_path):
        a = pd.read_csv(a_path).set_index("item")
        say("| verdict | pooled un-aged | pooled aged | team-rank un-aged | team-rank aged | ships |")
        say("|---|---|---|---|---|---|")
        cols = ["pooled_unaged_mean", "pooled_aged_mean", "teamrank_unaged_mean", "teamrank_aged_mean"]
        for item in b.index:
            if item not in a.index:
                continue
            cells = " | ".join("%+.2f to **%+.2f**" % (b.loc[item, c], a.loc[item, c]) for c in cols)
            ships = "%s to **%s**" % ("yes" if b.loc[item, "ships_all_four"] else "no",
                                      "yes" if a.loc[item, "ships_all_four"] else "no")
            say("| %s | %s | %s |" % (item, cells, ships))
        before_set = set(b[b.ships_all_four].index)
        after_set = set(a[a.ships_all_four].index)
        say()
        say("Shipping before: %d. After: %d." % (len(before_set), len(after_set)))
        say("Dropped: %s" % (sorted(before_set - after_set) or "none"))
        say("Added: %s" % (sorted(after_set - before_set) or "none"))
        say("The seven that shipped before, still shipping: %s"
            % sorted(s for s in SHIPPED if s in after_set))
    else:
        say("r7_allocator_verdicts.csv not rebuilt yet")
    say()

    # ---- 3. Charlotte and Boston -------------------------------------------------
    say("## 3. Charlotte and Boston against the market")
    say()
    bd = pd.read_csv(os.path.join(SNAP, "r5_disagreements_bases.csv"))
    ad_path = os.path.join(OUT, "r5_disagreements_bases.csv")
    if os.path.exists(ad_path):
        ad = pd.read_csv(ad_path)
        say("| team | basis | market | model before | model after | label before | label after | "
            "views above market, before to after |")
        say("|---|---|---:|---:|---:|---|---|---|")
        for team in ("CHA", "BOS", "MIN"):
            for basis in ("unaged", "aged"):
                rb = bd[(bd.team == team) & (bd.basis == basis)]
                ra = ad[(ad.team == team) & (ad.basis == basis)]
                if rb.empty or ra.empty:
                    continue
                rb, ra = rb.iloc[0], ra.iloc[0]
                say("| %s | %s | %.2f%% | %.2f%% | **%.2f%%** | %s | **%s** | %d to %d |"
                    % (team, basis, rb.market_pct, rb.mean_pct, ra.mean_pct, rb.label, ra.label,
                       rb.views_above_market, ra.views_above_market))
        say()
        for team in ("CHA", "BOS"):
            ch = []
            for basis in ("unaged", "aged"):
                rb = bd[(bd.team == team) & (bd.basis == basis)].iloc[0]
                ra = ad[(ad.team == team) & (ad.basis == basis)].iloc[0]
                if rb.label != ra.label:
                    ch.append("%s: %s to %s" % (basis, rb.label, ra.label))
                if bool(rb.disagreement) != bool(ra.disagreement):
                    ch.append("%s: %s a disagreement" % (basis, "was" if rb.disagreement else "now"))
            say("**%s**: %s" % (team, "; ".join(ch) if ch else "label unchanged on both bases"))
    else:
        say("r5_disagreements_bases.csv not rebuilt yet")
    say()

    # ---- 4. the honesty rail -----------------------------------------------------
    rb_path, ra_path = os.path.join(SNAP, "r5_honesty_rail_bases.csv"), os.path.join(OUT, "r5_honesty_rail_bases.csv")
    if os.path.exists(rb_path) and os.path.exists(ra_path):
        say("## 4. The honesty rail")
        say()
        rb = pd.read_csv(rb_path).set_index("basis")
        ra = pd.read_csv(ra_path).set_index("basis")
        say("| basis | rank correlation before | after | disagreements before | after | all-views before | after |")
        say("|---|---|---|---:|---:|---:|---:|")
        for basis in ("unaged", "aged"):
            if basis in rb.index and basis in ra.index:
                say("| %s | %.2f to %.2f | **%.2f to %.2f** | %d | **%d** | %d | **%d** |"
                    % (basis, rb.loc[basis, "rankcorr_lo"], rb.loc[basis, "rankcorr_hi"],
                       ra.loc[basis, "rankcorr_lo"], ra.loc[basis, "rankcorr_hi"],
                       rb.loc[basis, "n_disagree"], ra.loc[basis, "n_disagree"],
                       rb.loc[basis, "n_allviews"], ra.loc[basis, "n_allviews"]))

    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("# D90. The chain re-run on refit impacts, before and after\n\n")
        fh.write("*Before is `outputs/.chain_snapshot`, taken by `chain.py` before the run; the "
                 "aged simulation's before state comes from git. After is the chain's output.*\n\n")
        fh.write("\n".join(lines) + "\n")
    print("\nwrote %s" % os.path.relpath(OUT_MD, REPO))


if __name__ == "__main__":
    main()
