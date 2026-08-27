#!/usr/bin/env python3
"""L3: the final numbers sheet.

Every figure the piece is allowed to quote, with the run that produced it, its band
across the four impact views, and a verdict label saying what kind of claim it can
support. Anything not on this sheet does not go in the piece.

Verdict labels:
  QUOTABLE          a sign or a magnitude that survives all four views
  QUOTABLE AS BAND  quote the range, never the midpoint
  DIRECTIONAL       the sign is agreed but the magnitude is not
  NOT QUOTABLE      the views disagree on sign, or the estimate is too uncertain
  FACT              not a model output; a sourced or arithmetic fact

    python kuminga/scripts/build_final_numbers.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import kfreeze, runlog  # noqa: E402

OUTDIR = os.path.join(REPO, "kuminga", "outputs")
LOG = os.path.join(REPO, "kuminga", "logs", "runs.jsonl")
FORKS = ["consensus", "rapm", "box", "darko"]
OUT = os.path.join(OUTDIR, "final_numbers.md")
OUT_CSV = os.path.join(OUTDIR, "final_numbers.csv")


def last_run(script):
    best = None
    with open(LOG, encoding="utf-8") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("script") == script and d.get("status") == "ok":
                best = d["run_id"]
    return best or "n/a"


def load(name, **kw):
    p = os.path.join(OUTDIR, name)
    return pd.read_csv(p, **kw) if os.path.exists(p) else None


def main():
    with runlog.run("build_final_numbers", inputs={"outdir": OUTDIR}) as r:
        rows = []

        def add(section, label, value, band, verdict, run, note=""):
            rows.append(dict(section=section, figure=label, value=value, band=band,
                             verdict=verdict, run_id=run, note=note))

        # ---- the cap ---------------------------------------------------------
        rec = load("cap_reconciliation.csv")
        br = load("cap_branches_canonical.csv")
        gate = json.load(open(os.path.join(OUTDIR, "kuminga_cap_gate.json"), encoding="utf-8"))
        rid_cap = last_run("cap_reconciliation")
        rid_sign = last_run("eval_signing")
        add("The deal that cannot happen yet", "MIN 2026-27 apron salary, pre-Kuminga",
            "$215,871,829", "13 contracted players", "FACT", rid_cap,
            "contracted salary only; excludes cap holds and the roster placeholder")
        add("The deal that cannot happen yet", "with Kuminga at the taxpayer MLE",
            "$221,935,829", "14 contracted players", "FACT", rid_cap)
        add("The deal that cannot happen yet", "amount over the second apron",
            f"${-gate['green_on_books']['room_after_signing']:,.0f}",
            "second apron $221,686,000", "FACT", rid_sign,
            "less than a rookie-minimum contract")
        if br is not None:
            t14 = br[(br.branch == "trade") & (br.n_players == 14)].iloc[0]
            s14 = br[(br.branch == "stretch") & (br.n_players == 14)].iloc[0]
            add("The deal that cannot happen yet", "trade branch at a legal 14-man roster",
                f"${t14.apron_team_salary:,.0f}",
                f"${t14.vs_first_apron:,.0f} under the first apron", "FACT", rid_cap)
            add("The deal that cannot happen yet", "stretch branch at 14",
                f"${s14.apron_team_salary:,.0f}",
                f"${-s14.vs_first_apron:,.0f} OVER the first apron", "FACT", rid_cap)
            t15 = br[(br.branch == "trade") & (br.n_players == 15)].iloc[0]
            add("The deal that cannot happen yet", "a 15th man in the trade branch",
                f"${-t15.vs_first_apron:,.0f} over the first apron", "", "FACT", rid_cap,
                "so any salary returning in a Green trade crosses it")
        # ---- S3: the loophole, so the lede survives a reader with a calculator
        lp = load("lede_loophole.csv")
        rid_lp = last_run("lede_loophole")
        if lp is not None:
            # NB: x.item is Series.item, the METHOD. Must index by name.
            g = dict(zip(lp["item"], lp["amount"].astype(float)))
            add("The deal that cannot happen yet", "room under the second apron",
                f"${g['ROOM under the second apron']:,.0f}", "", "FACT", rid_lp,
                "an exception may be used PARTIALLY, so this much of it fits")
            add("The deal that cannot happen yet",
                "max first-year salary at a 14-man roster",
                f"${g['max first-year salary, 14-man roster']:,.0f}",
                "95.9% of the taxpayer MLE", "FACT", rid_lp,
                "lands team salary on the apron to the dollar, which is legal because "
                "the hard cap prohibits EXCEEDING it; so the accurate lede is 'could "
                "not sign him to the FULL exception'")
            add("The deal that cannot happen yet",
                "max first-year salary at a 15-man roster",
                f"${g['max first-year salary, 15-man roster']:,.0f}",
                "73.5% of the taxpayer MLE", "FACT", rid_lp,
                "after a rookie-minimum 15th man")
            add("The deal that cannot happen yet", "what the loophole costs Kuminga",
                f"${g['what the loophole costs KUMINGA']:,.0f}", "over two years",
                "FACT", rid_lp, "at the 5% maximum raise; the reason it is a loophole "
                "and not a plan")
            add("The deal that cannot happen yet", "regular-season roster minimum",
                "14 or 15 players", "12 or 13 allowed for 2 consecutive weeks and 28 "
                "days total", "FACT", "CBA Article XXIX Sec 2(a), 2(b)(i)",
                "verified 2026-08-27 against CBA text and cbaguide.com")

        # ---- price and market -------------------------------------------------
        mk = load("market_comparison.csv")
        sp = load("kuminga_surplus_by_fork.csv")
        if mk is not None:
            lo, hi = mk.market_all_ages.min(), mk.market_all_ages.max()
            add("The price and the market", "Kuminga market value, four views",
                f"${lo/1e6:.1f}M to ${hi/1e6:.1f}M", "all-ages percentile map",
                "QUOTABLE AS BAND", rid_sign)
            add("The price and the market", "best real bid (Lakers, rejected)",
                "$12.0M/yr over 3 years", "~$36M total, sign-and-trade", "FACT", rid_sign,
                "Anthony Slater, ESPN")
            n_ag = int(mk.agrees_with_best_bid.sum())
            add("The price and the market", "views agreeing with the real bid within 25%",
                f"{n_ag} of 4", "consensus $11.5M, RAPM $11.7M vs a $12.0M bid",
                "QUOTABLE", rid_sign,
                "the two possession-based views land within 4%; box and DARKO do not")
            add("The price and the market", "age-restricted market value (22-25)",
                f"${mk.market_age_restricted.min()/1e6:.1f}M to "
                f"${mk.market_age_restricted.max()/1e6:.1f}M",
                "n=38, bimodal", "NOT QUOTABLE", rid_sign,
                "measures the age structure of NBA pay, not his value")
        if sp is not None:
            t = sp[sp.price_label == "taxpayer_mle_2026_27"]
            add("The price and the market", "surplus in impact units at the MLE",
                f"{t.surplus_net.min():+.2f} to {t.surplus_net.max():+.2f}",
                "2 of 4 positive", "NOT QUOTABLE", rid_sign, "views disagree on sign")
            a = sp[sp.price_label == "atl_option_declined"]
            add("The price and the market", "surplus at Atlanta's declined $24.3M option",
                f"{a.surplus_net.min():+.2f} to {a.surplus_net.max():+.2f}",
                "all four negative", "QUOTABLE", rid_sign,
                "all four views agree Atlanta was right to decline")

        # ---- the slot ---------------------------------------------------------
        sc = load("slot_constrained.csv")
        rid_slot = last_run("slot_analysis")
        if sc is not None:
            v = ("ALL POSITIVE" if (sc.marginal_pp > 0).all() else
                 "ALL NEGATIVE" if (sc.marginal_pp < 0).all() else "MIXED")
            add("The slot he inherits", "Kuminga marginal contribution, slot-constrained",
                f"{sc.marginal_pp.min():+.3f} to {sc.marginal_pp.max():+.3f}pp",
                v, "QUOTABLE AS BAND" if v != "MIXED" else "NOT QUOTABLE", rid_slot,
                f"his minutes can only go to {sc.filler.iloc[0]}")
        sr = load("slot_robustness.csv")
        rid_sr = last_run("slot_robustness")
        if sr is not None:
            ok = sr[sr.sign_agreement == "ALL POSITIVE"].variant.tolist()
            bad = sr[sr.sign_agreement != "ALL POSITIVE"].variant.tolist()
            add("The slot he inherits", "fills where all-positive HOLDS",
                f"{len(ok)} of {len(sr)}", "; ".join(ok), "FACT", rid_sr,
                "so the claim is 'against the MOST LIKELY internal alternative', "
                "never 'against any internal alternative'")
            add("The slot he inherits", "fills where all-positive FAILS",
                f"{len(bad)} of {len(sr)}", "; ".join(bad), "FACT", rid_sr,
                "name these in the piece rather than hedging")
            for _, x in sr.iterrows():
                add("The slot he inherits", f"fill variant {x.variant}",
                    f"{x.mean_pp:+.2f}pp mean", f"{x.lo_pp:+.2f} to {x.hi_pp:+.2f}pp",
                    "QUOTABLE AS BAND" if x.sign_agreement != "MIXED" else "NOT QUOTABLE",
                    rid_sr, f"{x.sign_agreement}"
                    + (f"; {x.unplaced_minutes:.1f} min unplaced"
                       if x.unplaced_minutes > 0.01 else ""))
        le = load("lineup_evidence.csv")
        rid_le = last_run("lineup_evidence")
        if le is not None:
            for lab in ("Randle+Gobert", "Reid+Gobert"):
                x = le[le.label == lab]
                if len(x):
                    add("The slot he inherits", f"{lab} net rating",
                        f"{x.net_rating.iloc[0]:+.2f}",
                        f"{x.poss_off.iloc[0]:,.0f} possessions", "FACT", rid_le,
                        "descriptive on/off, not an effect")
            for tm in ("GSW", "ATL"):
                x = le[(le.label == "ON minus OFF") & (le.team == tm)]
                if len(x):
                    add("The slot he inherits", f"Kuminga on/off at {tm}",
                        f"{x.net_rating.iloc[0]:+.2f}",
                        f"{x.poss_off.iloc[0]:,.0f} possessions", "FACT", rid_le,
                        "small sample; the sign reversal between teams is the point")

        # ---- what moved the offseason ----------------------------------------
        # PRIMARY is the slot-aware run (D31): a departing player's minutes go to his
        # own position group. The unpooled run is kept only to test which verdicts
        # survive the change, and a verdict that does not survive is not quotable.
        sh = load("shapley_min_POOLED.csv", index_col=0)
        cmp_ = load("S1_shapley_slot_comparison.csv")
        rid_sh = last_run("shapley")
        rid_cmp = last_run("compare_slot_shapley")
        flipped = set(cmp_[cmp_.flipped].move) if cmp_ is not None else set()
        if sh is not None:
            for mv, x in sh.iterrows():
                agreed = x.sign_agreement != "MIXED"
                verdict = ("NOT QUOTABLE" if (mv in flipped or not agreed)
                           else "QUOTABLE AS BAND")
                note = x.sign_agreement
                if mv in flipped:
                    note += "; FLIPPED under the unpooled minutes rule, so no sign"
                add("What moved the offseason", f"Shapley: {mv}",
                    f"{x.mean_pp:+.2f}pp mean",
                    f"{min(x[f] for f in FORKS):+.2f} to {max(x[f] for f in FORKS):+.2f}pp",
                    verdict, rid_sh, note)
            exi = sh.drop(index="ddv_injury", errors="ignore")[FORKS].sum()
            sign = ("ALL POSITIVE" if (exi > 0).all() else
                    "ALL NEGATIVE" if (exi < 0).all() else "MIXED")
            add("What moved the offseason", "transactions excluding the injury",
                f"{exi.mean():+.2f}pp mean",
                f"{exi.min():+.2f} to {exi.max():+.2f}pp", "NOT QUOTABLE", rid_sh,
                f"{sign} here but MIXED under the unpooled rule, so it flips and "
                f"cannot carry a sign")
        # P1: the Dosunmu finding is TWO claims and the sheet must label them apart.
        dc = load("dosunmu_cap.csv")
        rid_dc = last_run("dosunmu_cap")
        if sh is not None and "dosunmu_retained" in sh.index:
            x = sh.loc["dosunmu_retained"]
            add("Dosunmu (a) on-court", "his minutes vs the guards on the roster",
                f"{x.mean_pp:+.2f}pp mean",
                f"{min(x[f] for f in FORKS):+.2f} to {max(x[f] for f in FORKS):+.2f}pp",
                "QUOTABLE AS BAND", rid_sh,
                "counterfactual is LOSE HIM FOR NOTHING, not spend the money elsewhere: "
                "Minnesota was over the cap, so the salary was never convertible into a "
                "replacement at that price")
        if dc is not None:
            g = {r_["scenario"]: r_ for _, r_ in dc.iterrows()}
            on = g["13 players, Dosunmu on the book"]
            off = g["12 players, Dosunmu gone"]
            off14 = g["14 players, Dosunmu gone + 2 minimums"]
            add("Dosunmu (b) cap", "2026-27 salary", "$19,310,345",
                "5 years; $86,510,348 across the 4 years in the contract book",
                "FACT", rid_dc,
                "the reported $112M total includes a 5th year not carried in the book")
            add("Dosunmu (b) cap", "MIN vs the tax line, with him",
                f"${on.vs_tax_line:,.0f} over", f"est tax bill ${on.est_tax_bill:,.0f}",
                "FACT", rid_dc, "tax rates flagged CONFIRM in the constants; label est")
            add("Dosunmu (b) cap", "MIN vs the tax line, without him",
                f"${-off.vs_tax_line:,.0f} under", "no tax bill", "FACT", rid_dc,
                f"still under after filling to 14 men: "
                f"${-off14.vs_tax_line:,.0f} under, no bill. His is the contract that "
                f"makes them a taxpayer.")
            add("Dosunmu (b) cap", "exception tier without him",
                f"${off.vs_first_apron:,.0f} under the first apron",
                "non-taxpayer mid-level available", "FACT", rid_dc,
                "so the tool to chase a forward would have been up to $12,453,516 "
                "rather than the $6,064,000 taxpayer exception")
            add("Dosunmu (b) cap", "second-apron distance without him",
                f"${g['13 players, Kuminga signed, Dosunmu gone'].vs_second_apron:,.0f} under",
                "same roster, Kuminga signed", "FACT", rid_dc,
                "against $249,829 OVER with him")
        # P2: does the injury claim hold per view, or only on the mean?
        if sh is not None and "ddv_injury" in sh.index:
            wins = [f for f in FORKS if sh[f].idxmin() == "ddv_injury"]
            rank_mean = int(sh["mean_pp"].rank().loc["ddv_injury"])
            add("What moved the offseason", "is the injury the largest single negative?",
                f"under {len(wins)} of 4 views", f"only: {', '.join(wins) or 'none'}",
                "NOT QUOTABLE", rid_sh,
                f"rank {rank_mean} of {len(sh)} on the mean, behind dosunmu_retained and "
                f"depth; under rapm it is the SMALLEST negative. Say 'negative under all "
                f"four and the only item nobody chose', never 'the largest'.")
        if cmp_ is not None:
            add("What moved the offseason", "player verdicts that survive the slot rule",
                f"{int(cmp_[cmp_.quotable].shape[0])} of "
                f"{int(cmp_.player_specific.sum())}",
                "; ".join(cmp_[cmp_.quotable].move), "FACT", rid_cmp,
                "flipped and dropped: "
                + (", ".join(cmp_[cmp_.player_specific & cmp_.flipped].move) or "none"))

        # ---- the structural risk ---------------------------------------------
        po = load("player_option.csv")
        rid_po = last_run("player_option")
        if po is not None:
            b = po[po.aging == "flat"]
            add("The structural risk", "P(Kuminga opts out after year one)",
                f"{b.p_opt_out.min():.2f} to {b.p_opt_out.max():.2f}", "flat aging",
                "QUOTABLE AS BAND", rid_po, "first-pass model, not calibrated")
            add("The structural risk", "P(Minnesota can retain him)",
                f"{b.p_minnesota_retains.min():.2f} to {b.p_minnesota_retains.max():.2f}",
                "flat aging", "QUOTABLE AS BAND", rid_po,
                "Non-Bird caps a re-sign start at $7,640,640")
        add("The structural risk", "Non-Bird re-sign ceiling in 2027", "$7,640,640",
            "120% of the year-two salary", "FACT", "league_year_constants",
            "confirmed from CBA text: a declined option year is never covered")

        # ---- the West ---------------------------------------------------------
        sd = load("seed_distribution.csv")
        rid_sd = last_run("seed_distribution")
        if sd is not None:
            mn = sd[(sd.team_abbr == "MIN")]
            base = mn[mn.field == "baseline"].p_playoff_top6
            cur = mn[mn.field == "current"].p_playoff_top6
            add("The West", "P(MIN avoids the play-in), baseline",
                f"{base.mean():.2f}", f"{base.min():.2f} to {base.max():.2f}",
                "QUOTABLE AS BAND", rid_sd)
            add("The West", "P(MIN avoids the play-in), after the offseason",
                f"{cur.mean():.2f}", f"{cur.min():.2f} to {cur.max():.2f}",
                "QUOTABLE AS BAND", rid_sd, "the widest and most legible result")
        t2 = load("T2_west_ranking.csv")
        rid_out = last_run("build_outputs")
        if t2 is not None:
            m = t2[t2.team_abbr == "MIN"].iloc[0]
            add("The West", "MIN West rank, before and after",
                f"#{int(m.west_rank_baseline)} to #{int(m.west_rank_current)}",
                "mean of four views", "DIRECTIONAL", rid_out)
        sim = load("sim_all30_2026_27.csv")
        rid_sim = last_run("run_sim")
        if sim is not None:
            m = sim[sim.team_abbr == "MIN"]
            add("The West", "MIN title probability, after",
                f"{m.title_current.mean()*100:.2f}%",
                f"{m.title_current.min()*100:.2f}% to {m.title_current.max()*100:.2f}%",
                "QUOTABLE AS BAND", rid_sim, "never quote the midpoint alone")
            add("The West", "MIN offseason title-odds change",
                f"{m.title_delta.mean()*100:+.2f}pp",
                f"{m.title_delta.min()*100:+.2f} to {m.title_delta.max()*100:+.2f}pp",
                "NOT QUOTABLE", rid_sim, "the four views disagree on sign")

        # ---- the honesty rail --------------------------------------------------
        bt = load("backtest_calibration_summary.csv")
        rid_bt = last_run("backtest_calibration")
        if bt is not None:
            add("Calibration", "title-odds error vs the market, 3-season backtest",
                f"{bt.title_mae_pp.min():.2f} to {bt.title_mae_pp.max():.2f}pp",
                "mean absolute error", "FACT", rid_bt,
                "the same size as Minnesota's entire fork spread")
            add("Calibration", "win-total error vs the market",
                f"{bt.model_wins_mae.mean():.2f} vs {bt.market_wins_mae.mean():.2f}",
                "model vs market MAE", "FACT", rid_bt, "model bias +0.27 wins")

        df = pd.DataFrame(rows)
        df.to_csv(OUT_CSV, index=False)

        man = kfreeze.manifest()
        with open(OUT, "w", encoding="utf-8") as fh:
            fh.write("# Final numbers\n\n")
            fh.write("Every figure the piece may quote, with the run that produced it. "
                     "Anything not on this sheet does not go in.\n\n")
            fh.write(f"Frozen warehouse snapshot: `{man['snapshot_id']}`.\n\n")
            fh.write("**Verdict labels.** QUOTABLE: survives all four views. "
                     "QUOTABLE AS BAND: quote the range, never the midpoint. "
                     "DIRECTIONAL: sign agreed, magnitude not. "
                     "NOT QUOTABLE: views disagree on sign, or too uncertain. "
                     "FACT: sourced or arithmetic, not a model output.\n\n")
            for sec in df.section.unique():
                fh.write(f"## {sec}\n\n")
                fh.write(df[df.section == sec][["figure", "value", "band", "verdict",
                                                "run_id", "note"]]
                         .to_markdown(index=False))
                fh.write("\n\n")
        counts = df.verdict.value_counts().to_dict()
        r.note(f"{len(df)} figures across {df.section.nunique()} sections: {counts}")
        r.output(OUT)
        r.output(OUT_CSV, rows=len(df))

    print(df[["section", "figure", "value", "verdict"]].to_string(index=False))


if __name__ == "__main__":
    main()
