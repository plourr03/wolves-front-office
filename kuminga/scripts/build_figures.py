#!/usr/bin/env python3
"""Item 18, figures: attribution waterfall, West ranking before/after, scenario fan.

These are ANALYSIS figures for the outputs directory, not article graphics. They are
built to be read by someone checking the work, so every one carries its fork spread
rather than a single line, and each has a method note printed on the figure itself.

    python kuminga/scripts/build_figures.py
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

OUTDIR = os.path.join(REPO, "kuminga", "outputs")
FIGDIR = os.path.join(OUTDIR, "figures")
FORKS = ["consensus", "rapm", "box", "darko"]

INK = "#1b1b1b"
GRID = "#d8d8d8"
POS = "#00843D"          # the Wolves-to-a-T brand green: good things
NEG = "#8a8a8a"          # danger stays neutral so green keeps meaning "good"
ACCENT = "#c8102e"

plt.rcParams.update({
    "figure.dpi": 200, "savefig.dpi": 200,
    "font.family": "DejaVu Sans",
    "axes.edgecolor": INK, "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
})


def note(ax, text):
    ax.text(0.0, -0.16, text, transform=ax.transAxes, fontsize=6.5,
            color="#555555", va="top", wrap=True)


def fig_waterfall(sh: pd.DataFrame):
    d = sh.copy()
    d = d.sort_values("mean_pp")
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    y = np.arange(len(d))
    for i, (mv, row) in enumerate(d.iterrows()):
        lo = min(row[f] for f in FORKS)
        hi = max(row[f] for f in FORKS)
        ax.plot([lo, hi], [i, i], color=GRID, lw=5, solid_capstyle="round", zorder=1)
        for f in FORKS:
            ax.scatter(row[f], i, s=18, color=NEG if row[f] < 0 else POS, zorder=3)
        ax.scatter(row.mean_pp, i, s=70, marker="|", color=INK, zorder=4, lw=1.6)
    ax.axvline(0, color=INK, lw=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels([m.replace("_", " ") for m in d.index], fontsize=8)
    ax.set_xlabel("Shapley contribution to Minnesota's 2026-27 title probability (pp)", fontsize=8)
    ax.set_title("Which move did what", fontsize=11, loc="left", weight="bold")
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    note(ax, "Each dot is one of four impact views (consensus, RAPM, box, DARKO); the bar is their "
             "range and the tick is the mean.\nExact Shapley over 256 coalitions, so contributions "
             "sum to the total offseason effect. A move whose dots straddle zero has no agreed sign.")
    fig.tight_layout()
    p = os.path.join(FIGDIR, "fig1_attribution_waterfall.png")
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_west(t2: pd.DataFrame):
    d = t2.sort_values("title_current_mean_pct", ascending=False).copy()
    d = d[d.title_current_mean_pct >= 0.05]
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    y = np.arange(len(d))
    ax.barh(y - 0.2, d.title_baseline_mean_pct, height=0.36, color="#bcbcbc",
            label="baseline: 2025-26 rosters, no injuries")
    ax.barh(y + 0.2, d.title_current_mean_pct, height=0.36, color=POS,
            label="after the 2026 offseason")
    for i, (_, row) in enumerate(d.iterrows()):
        if row.team_abbr == "MIN":
            ax.barh(i + 0.2, row.title_current_mean_pct, height=0.36, color=ACCENT)
            ax.barh(i - 0.2, row.title_baseline_mean_pct, height=0.36, color="#e8a0aa")
    ax.set_yticks(y)
    ax.set_yticklabels(d.team_abbr, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("title probability (%), mean of four impact views", fontsize=8)
    ax.set_title("The West, before and after", fontsize=11, loc="left", weight="bold")
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    note(ax, "Teams whose title probability rounds below 0.05% are omitted: their ordinal position "
             "is not meaningful.\nMinnesota in red. Baseline is every team's 2025-26 end-of-season "
             "roster run through the same pipeline.")
    fig.tight_layout()
    p = os.path.join(FIGDIR, "fig2_west_before_after.png")
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_fan(fan: pd.DataFrame):
    order = ["low_p10", "median", "high_p90", "playoff_slips"]
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    for i, fork in enumerate(FORKS):
        d = fan[fan.fork == fork].set_index("scenario").reindex(order)
        ax.plot(range(len(order)), d.title * 100, marker="o", ms=5, lw=1.6,
                label=fork, color=[INK, POS, "#7a7a7a", ACCENT][i])
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(["low (p10)", "median", "high (p90)", "playoff\ntranslation"], fontsize=8)
    ax.set_ylabel("Minnesota title probability (%)", fontsize=8)
    ax.set_title("What Kuminga's own uncertainty is worth", fontsize=11, loc="left", weight="bold")
    ax.legend(fontsize=7, frameon=False, title="impact view", title_fontsize=7)
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    note(ax, "Kuminga's impact swept across his own posterior (10th/50th/90th percentile) within each "
             "view, holding the rest of the league fixed.\n'Playoff translation' applies his measured "
             "regular-season-to-playoff decline. The spread BETWEEN views is wider than the spread "
             "within any one of them.")
    fig.tight_layout()
    p = os.path.join(FIGDIR, "fig3_scenario_fan.png")
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_seeds(sd: pd.DataFrame):
    """Minnesota's seed distribution, baseline vs current, per fork."""
    mn = sd[sd.team_abbr == "MIN"]
    seeds = [f"p_seed{k}" for k in range(1, 11)]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6), sharey=True)
    for ax, field, title in ((axes[0], "baseline", "Baseline: 2025-26 roster, healthy"),
                             (axes[1], "current", "After the 2026 offseason")):
        d = mn[mn.field == field]
        for i, fork in enumerate(FORKS):
            row = d[d.fork == fork]
            if row.empty:
                continue
            ax.plot(range(1, 11), row[seeds].to_numpy()[0], marker="o", ms=4, lw=1.5,
                    color=[INK, POS, "#7a7a7a", ACCENT][i], label=fork)
        ax.axvspan(6.5, 10.5, color="#f0f0f0", zorder=0)
        ax.text(8.5, ax.get_ylim()[1] * 0.92, "play-in", ha="center", fontsize=7,
                color="#777777")
        ax.set_xticks(range(1, 11))
        ax.set_xlabel("Western Conference seed", fontsize=8)
        ax.set_title(title, fontsize=9, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("probability", fontsize=8)
    axes[1].legend(fontsize=7, frameon=False, title="impact view", title_fontsize=7)
    fig.suptitle("Where Minnesota finishes", fontsize=11, x=0.02, ha="left", weight="bold")
    fig.tight_layout(rect=[0, 0.10, 1, 0.94])
    # Placed on the FIGURE, not an axis: an axis-relative note in a two-panel layout
    # lands on top of the left panel's x-axis label.
    fig.text(0.02, 0.015,
             "Seeds drawn from the engine's own seeding model (wins = 41 + 2.239*net + noise, ranked "
             "within conference). The shaded band is the play-in.\nUnder the consensus view the Wolves "
             "go from a 73% chance of avoiding the play-in to 39%; DARKO says 84%. That spread is the "
             "finding, not any one line.",
             fontsize=6.5, color="#555555", va="bottom")
    p = os.path.join(FIGDIR, "fig4_seed_distribution.png")
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    return p


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    with runlog.run("build_figures", inputs={"outdir": OUTDIR}) as r:
        made = []
        sh = os.path.join(OUTDIR, "shapley_min.csv")
        if os.path.exists(sh):
            made.append(fig_waterfall(pd.read_csv(sh, index_col=0)))
        else:
            r.note("shapley_min.csv missing, waterfall skipped")

        t2 = os.path.join(OUTDIR, "T2_west_ranking.csv")
        if os.path.exists(t2):
            made.append(fig_west(pd.read_csv(t2)))
        else:
            r.note("T2_west_ranking.csv missing, West figure skipped")

        sd = os.path.join(OUTDIR, "seed_distribution.csv")
        if os.path.exists(sd):
            made.append(fig_seeds(pd.read_csv(sd)))
        else:
            r.note("seed_distribution.csv missing, seed figure skipped")

        fan = os.path.join(OUTDIR, "scenario_fan.csv")
        if os.path.exists(fan):
            made.append(fig_fan(pd.read_csv(fan)))
        else:
            r.note("scenario_fan.csv missing, fan skipped")

        for p in made:
            r.note(f"wrote {os.path.relpath(p, REPO)}")
            r.output(p)
    print("\n".join(made))


if __name__ == "__main__":
    main()
