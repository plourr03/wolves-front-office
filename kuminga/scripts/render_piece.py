#!/usr/bin/env python3
"""Render the piece skeleton and the morning report from their templates.

Every number in the rendered documents comes from `outputs/final_numbers.csv` by key.

  {{key}}          the figure's value
  {{key|t}}        the value followed by its label and script, e.g. `[modeled, run_sim]`
  {{TABLE:name}}   a table assembled from a family of sheet keys (tail, perview)

An unknown key is fatal. Alongside each rendered document a MASKED copy is written with
every rendered value replaced by a sentinel, which is what `reconcile_figures.py` scans for
digits that did not come from the sheet.

    python kuminga/scripts/render_piece.py
"""
from __future__ import annotations

import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

OUT = os.path.join(REPO, "kuminga", "outputs")
DOCS = os.path.join(REPO, "kuminga", "docs")
SHEET = os.path.join(OUT, "final_numbers.csv")
DOCS_TO_RENDER = [("piece_v2_skeleton.template.md", "piece_v2_skeleton.md"),
                  ("morning_report_v2.template.md", "morning_report_v2.md")]
SENT = "⟦⟧"
FORKS = ["consensus", "rapm", "box", "darko"]


def script_of(run_id):
    return re.sub(r"_\d{8}T\d{6}Z$", "", run_id)


def table(name, sheet):
    keys = sheet.index
    if name == "tail":
        bases = sorted({k[:6] for k in keys if re.match(r"tail\d\d_player$", k)})
        head = ["| player | possessions | consensus | RAPM | box | DARKO |", "|---|---:|---:|---:|---:|---:|"]
        rows = ["| {{%s_player}} | {{%s_poss}} | %s |" % (b, b, " | ".join("{{%s_%s}}" % (b, f) for f in FORKS))
                for b in bases]
        return "\n".join(head + rows)
    if name == "perview":
        teams = sorted({k.split("_")[1] for k in keys if re.match(r"pv_[a-z]+_mkt$", k)},
                       key=lambda t: t != "min")
        head = ["| team | market | consensus | RAPM | box | DARKO | views |", "|---|---:|---:|---:|---:|---:|---|"]
        rows = ["| %s | {{pv_%s_mkt}} | %s | {{pv_%s_label}} |" % (
            t.upper(), t, " | ".join("{{pv_%s_%s}}" % (t, f) for f in FORKS), t) for t in teams]
        return "\n".join(head + rows)
    if name == "allocators":
        items = [k[2:-6] for k in keys if k.startswith("v_") and k.endswith("_label")
                 and sheet.loc["v_%s_ships" % k[2:-6], "value"] == "yes"]
        head = ["| verdict | pooled, un-aged | pooled, aged | team-rank, un-aged | "
                "team-rank, aged | views clearing in each cell |",
                "|---|---:|---:|---:|---:|---|"]
        rows = ["| {{v_%s_label}} | {{v_%s_pooled_u}} | {{v_%s_pooled_a}} | {{v_%s_tr_u}} | "
                "{{v_%s_tr_a}} | {{v_%s_cells}} |" % ((i,) * 6) for i in items]
        return "\n".join(head + rows)
    if name in ("ship", "retired"):
        items = [k[2:-6] for k in keys if k.startswith("v_") and k.endswith("_label")]
        if name == "ship":
            items = [i for i in items if sheet.loc["v_%s_ships" % i, "value"] == "yes"]
        else:
            items = [i for i in items if sheet.loc["v_%s_preship" % i, "value"] == "yes"
                     and sheet.loc["v_%s_ships" % i, "value"] == "no"]
        head = ["| verdict | un-aged, mean points of title odds | aged | sign, un-aged / aged | views clearing, un-aged, aged |",
                "|---|---:|---:|---|---|"]
        rows = ["| {{v_%s_label}} | {{v_%s_u}} | {{v_%s_a}} | {{v_%s_signs}} | {{v_%s_clear}} |" % (i, i, i, i, i)
                for i in items]
        return "\n".join(head + rows)
    raise KeyError("unknown table %s" % name)


def render(text, sheet, used):
    text = re.sub(r"\{\{TABLE:([a-z]+)\}\}", lambda m: table(m.group(1), sheet), text)
    full, masked = [], []
    pos = 0
    for m in re.finditer(r"\{\{([A-Za-z0-9_]+)(\|t)?\}\}", text):
        key, tag = m.group(1), m.group(2)
        if key not in sheet.index:
            raise KeyError("template key not on the sheet: %s" % key)
        used.add(key)
        row = sheet.loc[key]
        val = str(row.value)
        extra = " `[%s, %s]`" % (row.label.split()[0].lower(), script_of(row.run_id)) if tag else ""
        full.append(text[pos:m.start()] + val + extra)
        masked.append(text[pos:m.start()] + SENT + (" `[tag]`" if tag else ""))
        pos = m.end()
    full.append(text[pos:])
    masked.append(text[pos:])
    return "".join(full), "".join(masked)


def main():
    with runlog.run("render_piece", inputs={"sheet": SHEET}) as r:
        sheet = pd.read_csv(SHEET, dtype=str).set_index("key")
        used = set()
        for src, dst in DOCS_TO_RENDER:
            tpl = open(os.path.join(DOCS, src), encoding="utf-8").read()
            full, masked = render(tpl, sheet, used)
            with open(os.path.join(DOCS, dst), "w", encoding="utf-8") as fh:
                fh.write(full)
            with open(os.path.join(OUT, dst.replace(".md", ".masked.md")), "w", encoding="utf-8") as fh:
                fh.write(masked)
            r.note("rendered %s -> %s" % (src, dst))
            r.output(os.path.join(DOCS, dst))
        pd.DataFrame(sorted(used), columns=["key"]).to_csv(os.path.join(OUT, "render_keys_used.csv"), index=False)
        r.note("%d distinct sheet keys used" % len(used))


if __name__ == "__main__":
    main()
