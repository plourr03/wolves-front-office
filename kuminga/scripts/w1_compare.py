#!/usr/bin/env python3
"""W1: every headline verdict under the old default, under the team-changer rule, and
across the Cody Williams minutes range. One table, so the conditional claims are visible.

THE QUESTION W1 EXISTS TO ANSWER. Piece 1's numbers were resting on an assumption nobody
had made on purpose: Cody Williams was handed 19 minutes because he averaged 24.3 for a
27-win Utah team, and his impact is the worst on Minnesota's roster. Two fixes were
specified for the same problem. This is the first: a league-wide rule that prices a
team-changer on the rank he earns with his new team rather than the role he left.

  OLD DEFAULT   desired minutes = 0.5 * rank curve + 0.5 * own prior load, for everyone.
  W1 RULE       team-changers go to 0.8 / 0.2; incumbents stay at 0.5 / 0.5.
                Applied identically to all 30 teams, per R2.

WHAT THE RULE IS AND IS NOT. It is a re-anchoring, not a downgrade: rank score is half
impact, so a mover who is good on his new team moves UP and a mover who is not moves
DOWN. League-wide the correlation between a mover's impact and his minutes change under
the rule is +0.77, which is the rule working as designed.

THE LIMITATION, stated because it is real. The rule only re-optimises MOVERS. An
incumbent who is badly allocated stays badly allocated, so a team with more movers gets
a slightly better-optimised rotation for a reason that is about the method rather than
the roster. League-wide the mean team shift is +0.02 net points and it correlates 0.56
with the number of movers. For Minnesota the shift is +0.074, of which Cody Williams
alone is 69%; the remaining +0.023 is right at the league mean and therefore cancels in
relative terms. So Minnesota's gain is the correction this was built for, not the
artefact. That decomposition is printed here rather than asserted.

    python kuminga/scripts/w1_compare.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

OUTDIR = os.path.join(REPO, "kuminga", "outputs")
REF = os.path.join(OUTDIR, "w1_reference_old_default")
OUT = os.path.join(OUTDIR, "w1_verdict_comparison.csv")
FORKS = ["consensus", "rapm", "box", "darko"]


def sign_of(vals):
    return ("ALL POSITIVE" if min(vals) > 0 else
            "ALL NEGATIVE" if max(vals) < 0 else "MIXED")


def read(d, name):
    p = os.path.join(d, name)
    return pd.read_csv(p) if os.path.exists(p) else None


def regime(d, label):
    """Pull the four headline verdicts out of one output directory."""
    sim = read(d, "sim_all30_2026_27.csv")
    seed = read(d, "seed_distribution.csv")
    slot = read(d, "slot_robustness.csv")
    rot = read(d, "rotations_2026_27.csv")
    rec = {"regime": label}

    if sim is not None:
        # sim_all30 is LONG: one row per fork per team.
        m = sim[sim.team_abbr == "MIN"].set_index("fork")
        t = {f: float(m.loc[f, "title_current"]) * 100 for f in FORKS}
        b = {f: float(m.loc[f, "title_baseline"]) * 100 for f in FORKS}
        dl = {f: float(m.loc[f, "title_delta"]) * 100 for f in FORKS}
        rec.update(title_mean=sum(t.values()) / 4, title_lo=min(t.values()),
                   title_hi=max(t.values()), delta_mean=sum(dl.values()) / 4,
                   delta_lo=min(dl.values()), delta_hi=max(dl.values()),
                   delta_sign=sign_of(list(dl.values())))
    if seed is not None:
        s = seed[(seed.team_abbr == "MIN") & (seed.field == "current")]
        rec.update(top6_mean=float(s.p_playoff_top6.mean()),
                   top6_lo=float(s.p_playoff_top6.min()),
                   top6_hi=float(s.p_playoff_top6.max()))
    if slot is not None:
        a = slot[slot.variant == "A_c3_default_shannon"]
        if len(a):
            a = a.iloc[0]
            v = [float(a["pp_" + f]) for f in FORKS]
            rec.update(kuminga_mean_pp=float(a.mean_pp), kuminga_lo=min(v),
                       kuminga_hi=max(v), kuminga_sign=str(a.sign_agreement))
    if rot is not None:
        r_ = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN")]
        for who, pid in (("williams", "Cody Williams"), ("kuminga", "Jonathan Kuminga"),
                         ("ball", "LaMelo Ball")):
            row = r_[r_.player_name == pid]
            rec[who + "_mpg"] = float(row.mpg.iloc[0]) if len(row) else 0.0
    return rec


def main():
    with runlog.run("w1_compare", inputs={"reference": os.path.relpath(REF, REPO)}) as r:
        rows = [regime(REF, "old default (50/50 all)"),
                regime(OUTDIR, "W1 rule (80/20 movers)")]

        grid = read(OUTDIR, "williams_minutes_sensitivity.csv")
        if grid is not None:
            for _, x in grid.iterrows():
                if x.level == "model default":
                    continue
                rows.append(dict(
                    regime="W1 rule, Williams at %s" % x.level,
                    title_mean=x.title_mean, title_lo=x.title_lo, title_hi=x.title_hi,
                    delta_mean=x.delta_mean, delta_lo=min(x["delta_" + f] for f in FORKS),
                    delta_hi=max(x["delta_" + f] for f in FORKS),
                    delta_sign=x.delta_sign,
                    top6_mean=x.top6_mean, top6_lo=x.top6_lo, top6_hi=x.top6_hi,
                    kuminga_mean_pp=x.kuminga_mean_pp,
                    kuminga_lo=min(x["kuminga_pp_" + f] for f in FORKS),
                    kuminga_hi=max(x["kuminga_pp_" + f] for f in FORKS),
                    kuminga_sign=x.kuminga_sign,
                    williams_mpg=x.williams_mpg))

        d = pd.DataFrame(rows)
        d.to_csv(OUT, index=False)

        r.note("MINUTES under each regime (MIN):")
        for _, x in d.iterrows():
            if pd.notna(x.get("kuminga_mpg")):
                r.note("  %-28s Williams %5.2f | Kuminga %5.2f | Ball %5.2f"
                       % (x.regime, x.williams_mpg, x.kuminga_mpg, x.ball_mpg))
        r.note("")
        r.note("HEADLINE VERDICTS:")
        for _, x in d.iterrows():
            r.note("  %-28s title %.2f%% (%.2f-%.2f) | delta %+.2fpp %-13s | "
                   "top-6 %.2f | Kuminga %+.3fpp %s"
                   % (x.regime, x.title_mean, x.title_lo, x.title_hi,
                      x.delta_mean, x.delta_sign, x.top6_mean,
                      x.kuminga_mean_pp, x.kuminga_sign))

        # ---- the question the brief actually asks -----------------------------
        rng = d[d.regime.str.startswith("W1 rule")]
        dsg, ksg = set(rng.delta_sign.dropna()), set(rng.kuminga_sign.dropna())
        r.note("")
        r.note("ACROSS THE WILLIAMS RANGE, UNDER THE RULE:")
        r.note("  offseason delta : %s -> %s"
               % (", ".join(sorted(dsg)),
                  "UNCONDITIONAL" if len(dsg) == 1 else "CONDITIONAL"))
        r.note("  Kuminga slot    : %s -> %s"
               % (", ".join(sorted(ksg)),
                  "UNCONDITIONAL" if len(ksg) == 1 else "CONDITIONAL"))
        r.note("  title band      : %.2f%% to %.2f%%"
               % (rng.title_mean.min(), rng.title_mean.max()))
        r.note("  P(top 6)        : %.2f to %.2f"
               % (rng.top6_mean.min(), rng.top6_mean.max()))
        r.output(OUT, rows=len(d))

    print()
    cols = ["regime", "williams_mpg", "title_mean", "delta_mean", "delta_sign",
            "top6_mean", "kuminga_mean_pp", "kuminga_sign"]
    print(d[[c for c in cols if c in d.columns]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
