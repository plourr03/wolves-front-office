# Publish-day lock runbook

*Run this the day BEFORE publication, start to finish, in order. It is a refresh-and-verify procedure, not an analysis session. Written 2026-09-20 against the state left by D90.*

**The one rule that governs the day: no analysis changes on lock day.** Refresh inputs, re-run what the inputs force, verify the gates, freeze. If the day turns up something that wants a new estimate, a changed method, a new robustness check or a reworded claim beyond what a refreshed number forces, it does not happen today. Write it in `gaps_remaining.md` and publish without it, or move publication. Both are better than a method change nobody has checked.

**If a gate fails, stop and fix the cause.** Never pass a gate by widening it, by editing the rendered document by hand, or by adding a figure to the retracted list to silence it. The gates are the only thing standing between a refreshed input and a wrong sentence.

---

## 0. Before lock day: prep that must already exist

These are not lock-day work. If any of them is missing when lock day starts, do it the day before lock day, or accept the runbook's fallback and record it.

**0.1 A roster diff and classifier.** Step 1 needs a script that compares two `roster_snapshot_2026_27_v3.csv` files and classifies every membership and money change. It does not exist yet. Spec, so it can be built in an hour:

- Input: two snapshot paths (old, new). Join on `(team_abbr, player_name)` first, then on `spotrac_player_url` to survive a name spelling change.
- Classify each difference into exactly one of: **cut** (was `standard` or `non_guaranteed`, now absent or `dead_money`), **signing** (absent before, now `standard` or `non_guaranteed`), **two-way conversion** (`contract_type` changes into or out of two-way), **trade** (present in both snapshots under different `team_abbr`), **pending resolved** (was `pending`, now `standard`), **money only** (same membership, `cap_hit_2026_27` changed), **cap hold or dead money churn** (status changes among `cap_hold` and `dead_money`).
- Output `outputs/lock_roster_diff.csv` with one row per change, its class, both statuses, both salaries, the team, and the `source_url`.
- Fail closed on an unclassifiable difference rather than bucketing it as "other". An unexpected shape is the thing worth seeing on lock day.
- Gate: every row of the diff carries a class, and the row count equals the number of differing keys.

**0.2 Preseason-minutes plumbing.** Step 4 adds observed figures beside modelled ones. The sheet, the template and the gate all have to be ready for it, and none of that is lock-day work:

- A data file `kuminga/data/preseason_minutes_2026_27.csv` with columns `player_name, nba_player_id, games, minutes_total, mpg, as_of, source`. Empty until lock day.
- Sheet keys in `build_final_numbers.py`, tagged `OBSERVED` with the run ID of the script that writes the data file: `obs_williams_mpg`, `obs_clark_mpg`, `obs_beringer_mpg`, `obs_preseason_games`, `obs_preseason_asof`.
- Template sentences, already in place and rendering, so lock day only changes the numbers behind them. Section 3, after the Williams rotation sentence: `In preseason he played {{obs_williams_mpg}} minutes a night over {{obs_preseason_games}} games, and Jaylen Clark {{obs_clark_mpg}}` with an `[observed, preseason_minutes]` tag. Section 4, beside the Beringer slot verdict: `Beringer's preseason load was {{obs_beringer_mpg}} minutes a night` with the same tag.
- The observed figure never replaces the modelled one. Both appear, each with its own label, because the modelled minutes are what every verdict was priced on.

**0.3 A green light on the warehouse.** The daily refresh runs at 03:33. Confirm it ran and that preseason games are present before step 4 depends on them.

---

## 1. Rosters: re-pull all 30 from Spotrac, diff, classify

**1.1 Fetch.** Spotrac blocks direct requests, so fetch each team's 2026-27 cap page through the proxy the project already uses for Basketball-Reference (`r.jina.ai`), and save each as markdown into a dated directory:

```
mkdir -p kuminga/data/spotrac/2026-09-XX
# one file per team, 30 files, named <ABBR>.md
# https://r.jina.ai/https://www.spotrac.com/nba/<team-slug>/cap/_/year/2026
```

Save all 30 before parsing. A partial directory parses silently into a partial league and the gates below will not all catch it.

**1.2 Parse and gate.**

```
python kuminga/scripts/build_roster_v3.py kuminga/data/spotrac/2026-09-XX
python kuminga/scripts/roster_v3_gates.py
```

`build_roster_v3.py` writes `data/roster_snapshot_2026_27_v3.csv` and `data/spotrac_anchors_2026_27_v3.csv`. Before running it, copy the existing snapshot aside as the diff base: `cp kuminga/data/roster_snapshot_2026_27_v3.csv kuminga/data/roster_snapshot_2026_27_v3.PRE_LOCK.csv`.

Expect from the parse: 30 teams, about 620 rows, and Gate A reporting each team's standard count equal to Spotrac's own header count. Gate B is the dollar reconciliation against Spotrac's published apron figures. **Both gates fail closed. A failure means the parse is wrong or Spotrac changed its layout, and it is not a lock-day fix if the layout moved.** In that case publish on the existing snapshot and record that the roster was not re-pulled, with the reason.

**1.3 Diff and classify.** This step uses `lock_roster_diff.py`, which **does not exist yet**: build it from the spec in 0.1 before lock day, or do the diff by hand on the two snapshots and write the classification into `outputs/lock_roster_diff.csv` in the same shape, because step 3 reads that file.

```
python kuminga/scripts/lock_roster_diff.py \
    kuminga/data/roster_snapshot_2026_27_v3.PRE_LOCK.csv \
    kuminga/data/roster_snapshot_2026_27_v3.csv
```

Read every row of `outputs/lock_roster_diff.csv` yourself. The classifier decides the shape of the change; you decide whether it touches the piece.

**1.4 Pending moves.** Two lists have to be re-checked, because they are the ones that go stale by becoming true:

- `status == "pending"` rows in the new snapshot (Spotrac's own Pending Transactions section). There were 8 at the last build.
- `data/transaction_supplement.csv` rows where `status` is `reported_pending_official` or `official_announced` is false.

For each, check whether it is now official. A move becomes official in this project only with **two independent source URLs** (R8), recorded in `source_url_1` and `source_url_2`. A team release with no terms promotes the STATUS and not the DOLLARS: keep `terms_not_released_by_team` on any money it carries, exactly as `p0_lock_official.py` did for the Kuminga signing. If rows need promoting, `python kuminga/scripts/p0_lock_official.py` is the pattern to follow, and the two-source rule is the gate.

---

## 2. Injuries: re-check against the CBS board, add sourced long-term rows

The injury table is hand-curated by rule R7: a player is long-term out if a **sourced** report puts the expected absence at 20 or more games. The rows live in `kuminga/scripts/build_injuries.py` and the table is rebuilt from it.

**2.1** Open the CBS injury board and compare it against `data/injuries_2026_27.csv`. Look for three things: a new long-term injury that clears the 20-game bar, a return date that has moved, and a player on the table who is now cleared.

**2.2** For every change, edit the row in `build_injuries.py` with the source URL and the return language, then rebuild:

```
python kuminga/scripts/build_injuries.py
```

**2.3** Keep the two availability conventions straight, because they drive different things. `rs_avail` and `po_avail` are R7 as written and binary, and they are what the simulation uses. `rs_avail_frac` and `po_avail_frac` are derived from the sourced return language and exist so the conservatism of the binary rule stays measurable. **No source publishes an availability fraction. The injury, the date and the return language are sourced; the fraction is ours and is labelled as ours.**

**2.4** A new long-term injury to a rotation player is the single most likely thing to trigger the full re-run in step 3. Note which teams the changes touch before moving on.

---

## 3. The trigger decision, then one of two branches

**3.1 Build the trigger team set, fresh, on lock day.** It is the union of three lists:

- The named teams: **MIN, OKC, SAS, DEN, HOU, LAL**.
- The market's top eight by de-vigged price, ties included.
- The model's top eight by mean title odds across the four views.

```
python - <<'EOF'
import pandas as pd
m = pd.read_csv("kuminga/outputs/market_devig_2026_27.csv")
named = {"MIN", "OKC", "SAS", "DEN", "HOU", "LAL"}
mkt = set(m[m.market_rank <= 8].team_abbr)
mod = set(m.nlargest(8, "model_pct").team_abbr)
print("market top 8 (ties):", sorted(mkt))
print("model top 8:", sorted(mod))
print("TRIGGER SET:", sorted(named | mkt | mod))
EOF
```

On 2026-09-20 that rule gives 13 teams: BOS, CLE, DEN, DET, HOU, LAL, MIA, MIN, NYK, OKC, PHI, SAS, TOR. The market's rank-6 slot is a five-way tie at 3.16%, which is why the market list has 10 teams and not 8. **Recompute it on lock day and use that answer, not this one.**

**3.2 Decide what "touches a rotation player" means, and apply it mechanically.** A rotation player is one with allocated minutes above zero in `outputs/rotations_2026_27.csv` for the team in question, which is the ten-man rotation the model actually plays.

```
python - <<'EOF'
import pandas as pd
rot = pd.read_csv("kuminga/outputs/rotations_2026_27.csv")
rot = rot[(rot.scenario == "current") & (rot.mpg > 0)]
diff = pd.read_csv("kuminga/outputs/lock_roster_diff.csv")
TRIGGER = set("BOS CLE DEN DET HOU LAL MIA MIN NYK OKC PHI SAS TOR".split())  # recomputed above
hit = diff[diff.team_abbr.isin(TRIGGER) & diff.player_name.isin(set(rot.player_name))]
print("changes touching a rotation player on a trigger team:", len(hit))
print(hit[["team_abbr", "player_name", "class"]].to_string(index=False) if len(hit) else "none")
EOF
```

Injury changes from step 2 go through the same test: a new long-term row for a rotation player on a trigger team counts as a touch.

**If the count is zero, take Branch B. If it is anything else, take Branch A.** Do not judge the size of the change. A ten-minute bench player on Denver is inside the rule and the rule decides.

### Branch A: a trigger team's rotation moved. Re-run the full chain.

**Budget seven hours.** The D90 run took 6h49m: eight 200,000-simulation f-curve forks, four per aging basis, run concurrently. Start it in the morning, not the afternoon, and do not start it at all if publication is less than nine hours away. If the time is not there, publish on the current chain and record in `decisions.md` that a roster change landed after the last chain and was not priced.

```
python kuminga/scripts/chain.py --dry-run          # read the plan first
nohup python kuminga/scripts/chain.py --nsims 200000 > /tmp/lock_chain.log 2>&1 &
```

The chain runs rotations, strengths, the simulation, the four f-curves, both Shapley variants, the slot analysis and robustness, `eval_signing`, the backtest, the market comparison, then the aged leg, then the gates and the sheet. **The snapshot ordering inside it is load-bearing and was wrong twice before D90 got it right**: `noise_floor`, `market_devig` and `f4_per_view_disagreement` read `outputs/preaging`, and `shapley --aged` and `noise_floor --aged` read `outputs/aged`, so the chain files those directories before the steps that read them. Do not reorder it on lock day.

Watch for these, in the log:

- Every step `rc=0`. The chain stops at the first failure by design.
- `r5_shapley_williams`: the post-fix tables must reproduce to about 1e-15. The pre-D85 comparison is reported and not enforced, because those frozen tables were priced on the old impact spine.
- `r7_allocator_agreement`: **the seven verdicts, in all four cells.** Two aging bases by two minutes allocators. A verdict ships only if its sign is the same in all four and all four views clear their floor in each.
- `reconcile_figures`: C1 f-curve pricing within 0.15 points of the direct simulation, C2 no figure without a run ID and no stray digit, C3 no unmarked duplicate run ID.

Then re-test the verdicts explicitly and read the table rather than trusting the count:

```
python kuminga/scripts/d90_refit_before_after.py
```

It writes `docs/d90_refit_before_after.md` with Minnesota's number and rank per view on both bases, the seven verdicts in all four cells before and after, and each team's disagreement with the market. **If the shipping set changed, the piece changes with it, and that is a content decision, not a lock-day one.** A dropped verdict means either move publication or cut the sentence that rests on it. Cutting a sentence is allowed on lock day. Rewriting a claim to survive is not.

### Branch B: nothing touched a rotation player. Cap chain and market comparison only.

```
python kuminga/scripts/cap_reconciliation.py
python kuminga/scripts/cap_branches.py
python kuminga/scripts/green_resolution.py
python kuminga/scripts/dosunmu_final_states.py
python kuminga/scripts/apron_reconcile_all30.py
python kuminga/scripts/eval_signing.py
python kuminga/scripts/market_devig.py
python kuminga/scripts/f4_per_view_disagreement.py
python kuminga/scripts/r5_honesty_rail_bases.py
```

The cap chain closes to the dollar or it fails: `$217,621,829` minus Green, plus Williams and Konchar, minus the stretch and the one-dollar rounding, equals `$211,013,416`, and with Kuminga `$217,077,416`. Section 8 quotes that chain, so a cap input change that breaks it is a fail-closed condition, not a rounding note.

`market_devig.py` reads the frozen un-aged simulation from `outputs/preaging`, so Branch B does not disturb the aging bases. `r5_honesty_rail_bases.py` gives the rank correlation and the all-views counts on both bases, which section 1 quotes.

---

## 4. Preseason minutes, recorded as observed

Publication may fall before the preseason starts. Handle both cases and record which one happened.

**4.1 Check that preseason games exist and are ingested.** The 2026-27 preseason is `season_id = 12026` in the warehouse (2025-26 preseason was 12025, 142 games, 2 to 17 October).

```
python - <<'EOF'
import sys; sys.path.insert(0, "postmortem")
from lib import db
print(db.query("""
  select g.season_id, count(distinct g.game_id) games, max(g.game_date) last_game
  from nba.nba_games g where g.season_id = 12026 and g.team_id = 1610612750
  group by 1""").to_string(index=False))
EOF
```

**If there are no games, stop step 4 there.** Record in `decisions.md` that publication precedes the preseason, leave the modelled minutes standing alone, and do not invent an observed column. The sheet keys stay empty and the template sentences stay unrendered.

**4.2 If games exist, pull the three players.** Minutes come from `nba_player_stats`, and a null `minutes_float` is a DNP, not a zero, so DNPs are excluded from the per-game average and reported separately.

```
python - <<'EOF'
import sys; sys.path.insert(0, "postmortem")
from lib import db
q = """
select s.player_id, s.player_name,
       count(*) filter (where s.minutes_float is not null) games_played,
       count(*) filter (where s.minutes_float is null) dnps,
       round(sum(s.minutes_float)::numeric, 1) minutes_total,
       round((sum(s.minutes_float) / nullif(count(*) filter (where s.minutes_float is not null), 0))::numeric, 1) mpg
from nba.nba_player_stats s
join nba.nba_games g on g.game_id = s.game_id and g.team_id = s.team_id
where g.season_id = 12026 and s.player_id in (1642262, 1641740, 1642866)
group by 1, 2 order by mpg desc nulls last
"""
print(db.query(q).to_string(index=False))
EOF
```

Cody Williams is `1642262`, Jaylen Clark `1641740`, Joan Beringer `1642866`.

**4.3 Write the data file and rebuild.** Fill `kuminga/data/preseason_minutes_2026_27.csv` with the query output, an `as_of` stamp and the source (the warehouse table plus the snapshot id), then rebuild the sheet in step 5. The observed figures appear **beside** the modelled ones, never instead of them, each carrying its own label. Section 3 gives Williams' and Clark's; section 4 gives Beringer's.

**4.4 Do not let an observed number change a verdict.** The whole shipping list was priced on the modelled minutes. Williams at, say, six preseason minutes a night is a fact worth printing next to the model's 16.1, and it is also exactly the case the N8 watch list already covers: the threshold is 12.0 minutes a night through game 20, checked in November, not on lock day. Print the observation, leave the verdict, let the watch list do its job.

---

## 5. Sheet, render, gate, freeze

**5.1 Regenerate, in this order.** Each step reads the one before it.

```
python kuminga/scripts/build_final_numbers.py
python kuminga/scripts/render_piece.py
python kuminga/scripts/reconcile_figures.py
```

Expect, from the last two runs of D90: about 866 figures on the sheet, about 741 keys used by the two rendered documents, and the gate reporting zero keys without a run ID, zero stray digits, zero stale figures, C1 within 0.15 points and C3 with every duplicate id marked.

**5.2 Read the rendered documents.** The gate proves provenance, not prose. Read section 1 of `docs/piece_v2_skeleton.md` end to end, plus every sentence the day's refresh touched, and `docs/morning_report_v2.md` in full. A number that moved can leave a sentence around it true but misleading, and that is exactly what happened when the aged basis went from two views above the market to one.

**5.3 Log the day.** Append one entry to `decisions.md`: which branch ran and why, every roster and injury change with its class and sources, the trigger evaluation, whether the shipping set moved, the preseason minutes or the fact that there were none, and every figure that changed with its before and after. **A changed figure that is not logged with its before and after breaks the project's own rule.**

**5.4 Commit, then freeze.**

```
git add -A kuminga postmortem offseason
git commit -m "Publication lock: <date>"
```

Then build the publication snapshot: the two rendered documents, the sheet, the keys the piece uses, the gate result, the provenance table, and the inventory of every run ID the piece cites.

```
python - <<'EOF'
import hashlib, os, shutil
import pandas as pd
day = pd.Timestamp.utcnow().strftime("%Y%m%d")
dst = os.path.join("kuminga", "docs", "publication", day)
os.makedirs(dst, exist_ok=True)
files = ["kuminga/docs/piece_v2_skeleton.md", "kuminga/docs/morning_report_v2.md",
         "kuminga/outputs/final_numbers.csv", "kuminga/outputs/final_numbers.md",
         "kuminga/outputs/render_keys_used.csv", "kuminga/outputs/reconcile_skeleton.csv",
         "kuminga/outputs/canonical_figures.csv", "kuminga/outputs/PROVENANCE.csv"]
for f in files:
    shutil.copy2(f, os.path.join(dst, os.path.basename(f)))

# every run id the piece actually cites, with the figures that cite it
sheet = pd.read_csv("kuminga/outputs/final_numbers.csv", dtype=str)
used = set(pd.read_csv("kuminga/outputs/render_keys_used.csv").key)
cited = sheet[sheet.key.isin(used)]
inv = (cited.groupby(["run_id", "source"], dropna=False)
             .agg(figures=("key", "count"), keys=("key", lambda s: "; ".join(sorted(s)[:8])))
             .reset_index().sort_values("run_id"))
inv.to_csv(os.path.join(dst, "publication_run_ids.csv"), index=False)
print("distinct run ids cited:", cited.run_id.nunique(),
      "| inventory rows:", len(inv), "| figures:", int(inv.figures.sum()))
assert cited.run_id.notna().all() and (cited.run_id.str.strip() != "").all(), \
    "a cited figure has no run id"

with open(os.path.join(dst, "SHA256SUMS"), "w", encoding="utf-8") as fh:
    for n in sorted(os.listdir(dst)):
        if n == "SHA256SUMS":
            continue
        p = os.path.join(dst, n)
        fh.write("%s  %s\n" % (hashlib.sha256(open(p, "rb").read()).hexdigest(), n))
print("froze", dst)
EOF
git add kuminga/docs/publication && git commit -m "Publication snapshot: <date>" && git tag publish-<date>
```

The inventory is the answer to "where does this number come from" for every figure in the piece, and the assertion in it is the last gate of the day: a cited figure with no run ID fails the freeze.

---

## Abort conditions

Any one of these stops publication rather than being worked around:

- A roster gate fails and the cause is a Spotrac layout change (not a lock-day fix).
- The cap chain no longer closes to the dollar.
- `reconcile_figures` fails for a reason other than a figure legitimately returning to a value that sits on the retracted list. That exception happened once, when the D89 refit put the headline back on 1.68%, and it was resolved by removing the entry with the reason recorded, not by loosening the gate.
- The shipping set changes and there is no time to cut the sentences that rest on the dropped verdicts.
- Branch A is required and there are fewer than nine hours before publication.
- A figure moved and you cannot say why.

## Timing

Branch B is under an hour including the reading. Branch A is a full day: seven hours of chain plus an hour of gates, comparison and reading. Step 1 is thirty to sixty minutes of fetching. Decide the branch early, because it decides whether the day fits.

## Then stop

When the freeze is committed and tagged, the day is over. No further runs, no further edits, no "one more check" that turns into a method change at midnight. Anything found after the freeze goes in `gaps_remaining.md` for the piece that follows.
