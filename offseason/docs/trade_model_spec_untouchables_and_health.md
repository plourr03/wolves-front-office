# Trade Model Fix Spec: Partner Untouchables Override + Returning-Star Health Correction

Author note for the agent: do not use em dashes or en dashes anywhere in code comments or docs. Use commas, periods, or parentheses.

## Why this exists

The board surfaced Indiana sending Andrew Nembhard and Obi Toppin for Julius Randle, Terrence Shannon Jr., and a first. That deal should never generate. There are two independent root causes, and this spec fixes both.

1. The untouchable gate (`trade_search.py:225`) is superstar-calibrated. It excludes only: surplus >= 3.0, a young $30M+ cornerstone (age <= 29), or a $35M+ older star unless his team is a rebuilder/retooler. Nembhard is about $19.5M and Toppin about $15M, and neither is a 3.0-surplus player, so both clear all three thresholds. Reported-core role players on mid salaries are invisible to the data gate.

2. Indiana's posture (`build_value_layer.py:168`) and baseline net (`bracket_sim.py:280`) are computed off a 15-40 season that only happened because Haliburton missed all of it. The wins-shortfall sub-score inflates the rebuild_score and drags posture toward retooler. Once Indiana reads as a retooler: the acceptance Value channel (`partner_acceptance.py:233`) starts counting picks toward a yes, so a Randle-plus-pick lowball clears, and the "$35M+ older star unless rebuilder/retooler" rule opens Pascal Siakam up as available. Separately, the depressed baseline net means every Indiana deal mis-scores its dP. The same trap sits on Boston, whose 2025-26 is a deliberate Tatum-Achilles gap year.

Fix 1 (override) closes cause 1. Fix 2 (health correction) closes cause 2. Both are config-driven so they stay auditable and Bobby owns the source tables.

---

## Fix 1: Partner untouchables override

### 1.1 New config

Place this next to Minnesota's `OFF_LIMITS` (`trade_search.py:43`). It is the partner-side mirror of that list for the other 29 teams. A CSV (`data/partner_untouchables.csv`, columns team, player_id, tier, confidence) is acceptable if it fits the data-layer pattern better, but the dict is fine to start.

```python
# Partner-side untouchables override. Unioned with the data gate in screen_partner (~line 272).
# "hard"  = never offered.
# "speculative" = only if the team's posture flips. Route to the path that already gates AD and Kyrie.
# Conf in comments: R = reported/consensus, J = analyst read. This patches only the sub-superstar gate hole.
PARTNER_UNTOUCHABLES = {
    # East
    "ATL": {"hard": ["Jalen Johnson"]},                                   # R; Trae Young = gray
    "BOS": {"hard": ["Jayson Tatum"]},                                    # R only; rest movable in the gap year
    "BKN": {"hard": []},                                                  # no centerpiece
    "CHA": {"hard": ["LaMelo Ball", "Brandon Miller", "Kon Knueppel"]},   # R
    "CHI": {"hard": ["Matas Buzelis"]},                                   # J
    "CLE": {"hard": ["Donovan Mitchell", "Evan Mobley"]},                 # R
    "DET": {"hard": ["Cade Cunningham", "Ausar Thompson"]},               # Cunningham R, Thompson J; Duren is RFA
    "IND": {"hard": ["Tyrese Haliburton", "Pascal Siakam",
                     "Andrew Nembhard", "Obi Toppin"]},                   # R, core-seven group
    "MIA": {"hard": ["Bam Adebayo"]},                                     # R; Herro openly available
    "MIL": {"hard": []},                                                  # Giannis = extend-or-trade
    "NYK": {"hard": ["Jalen Brunson", "Karl-Anthony Towns"]},            # R
    "ORL": {"hard": ["Paolo Banchero", "Franz Wagner"]},                  # R; Suggs core (J)
    "PHI": {"hard": ["Tyrese Maxey", "Joel Embiid", "VJ Edgecombe"]},     # Maxey R, others J
    "TOR": {"hard": ["Scottie Barnes"]},                                  # R
    "WAS": {"hard": ["Tre Johnson"]},                                     # R; Anthony Davis is available
    # West
    "DAL": {"hard": ["Cooper Flagg"], "speculative": ["Kyrie Irving"]},   # Flagg R; Kyrie soft keep
    "DEN": {"hard": ["Nikola Jokic"]},                                    # R only
    "GSW": {"hard": ["Stephen Curry"]},                                   # R
    "HOU": {"hard": ["Amen Thompson", "Alperen Sengun"]},                # Thompson R, Sengun J
    "LAC": {"hard": []},                                                  # retooling
    "LAL": {"hard": ["Luka Doncic"]},                                     # R; LeBron/Reaves are FAs
    "MEM": {"hard": []},                                                  # selling; Morant available
    "MIN": {"hard": ["Anthony Edwards", "Jaden McDaniels", "Joan Beringer"]},  # matches OFF_LIMITS
    "NOP": {"hard": ["Trey Murphy III", "Derik Queen"]},                  # J
    "OKC": {"hard": ["Shai Gilgeous-Alexander", "Chet Holmgren", "Jalen Williams"]},  # R
    "PHX": {"hard": ["Devin Booker"]},                                    # J; verify rest of roster
    "POR": {"hard": ["Shaedon Sharpe", "Donovan Clingan"]},               # J, low conf
    "SAC": {"hard": []},                                                  # no franchise piece
    "SAS": {"hard": ["Victor Wembanyama", "Stephon Castle", "Dylan Harper", "De'Aaron Fox"]},  # R
    "UTA": {"hard": []},                                                  # rebuilding; Kessler is RFA
}
```

### 1.2 Wiring

In `trade_search.py`, inside `screen_partner` where `partner_players` is built (the "not screened out as untouchable" step, around line 272):

1. Run the existing line-225 data gate unchanged.
2. Then drop any player whose (team, player) is in `PARTNER_UNTOUCHABLES[team]["hard"]`.
3. For players in `["speculative"]`, do not drop them. Tag them `speculative=True` and route them through the exact mechanism that currently makes AD and Kyrie conditional on Washington/Dallas pivoting. Do not invent a second speculative path.

### 1.3 Required details

- Match on the stable `player_id` used in `player_value.csv`, not the display string. If the pipeline currently keys on names, normalize on both sides (case-fold, strip punctuation and Jr./III suffixes) so "De'Aaron Fox" and similar do not silently miss.
- Union semantics: a player is unavailable if the data gate OR the override fires. The override only adds exclusions. It must never make a data-gated player available.
- Reason tag: when the override removes a player, set `reason = "manual_untouchable_reported_core"` so `emit_board` and `build_board_doc.py` can show it in the no-deal verdict, consistent with how the board already explains itself.
- Carry the R/J confidence through to the row so it is auditable. Optional: a config flag `TREAT_J_AS_SOFT` that demotes J-tagged entries to speculative, for A/B testing.

### 1.4 Acceptance tests

1. The Nembhard-and-Toppin-for-Randle deal no longer generates. Indiana offers neither player.
2. Edwards, McDaniels, and Beringer behavior is unchanged.
3. AD and Kyrie still appear only as Speculative.
4. A team with `"hard": []` (for example BKN) behaves exactly as before the change.
5. When the override fires, the board's no-deal reason string shows it.

---

## Fix 2: Returning-star health correction

This is the disease. Without it, the override stops the one deal but the model will still offer Siakam in a lowball and will still treat Boston as a fire sale.

### 2.1 New config

```python
# Stars who missed all or most of 2025-26 and are expected back. Sourced, with confidence.
# projected_avail: expected suit-up rate next season (cap it, do not assume 82).
# net_basis: which view/level to inject (use pre-injury consensus_net, haircut for injury type and age).
RETURNING_STARS = {
    "IND": [{"player": "Tyrese Haliburton", "projected_avail": 0.85,
             "injury": "achilles", "conf": "R"}],
    "BOS": [{"player": "Jayson Tatum", "projected_avail": 0.80,
             "injury": "achilles", "conf": "R"}],
    # add a row whenever a future team loses a star to a multi-month injury
}
```

### 2.2 Two integration options

Option A (preferred, the real fix). Before computing `rebuild_score` and the baseline net anchor, inject the returning star into the team's current roster at projected level using the existing roster-rollup and `apply_trade` machinery, then recompute:
- the projected-wins term feeding `rebuild_score` (`build_value_layer.py:168`), so the wins-shortfall sub-score reflects the healthy roster, and
- the regressed measured-net anchor (`bracket_sim.py:280`), by blending the injury-year measured net toward the healthy-roster projection, weighted by `projected_avail` and the star's projected minutes.

This generalizes: any future injured-star team is handled by adding one row.

Option B (stopgap). A manual posture override that forces IND and BOS to contender/mid, plus a manual baseline-net bump. Faster, less principled, and it does not clean the dP scoring as well as fixing the inputs. Use only if you do not want to touch the rollup yet.

### 2.3 Guardrails

- Cap `projected_avail`. Do not assume a full season off an Achilles.
- Haircut the injected net for the injury and age. You already worry that Tatum's rating overstates post-Achilles health, so reuse that haircut here rather than injecting his pre-injury number flat.
- Make the correction visible in outputs: flag `health_adjusted_baseline = True` for affected teams so it is auditable, not silent.
- Fix the known Zubac-on-Indiana contract row while you are in Indiana's data, since the bad salary also corrupts Indiana matching.

### 2.4 Acceptance tests

1. Indiana posture moves off retooler toward contender/mid.
2. Indiana no longer rubber-stamps a Randle-led lowball through the picks-count Value channel.
3. The model no longer offers Pascal Siakam in a lowball.
4. Boston stops reading as a fire sale.
5. Baseline title odds for IND and BOS move up to roughly track betting markets and public models, per the existing baseline sanity check.
6. The post-Achilles haircut is applied so Boston is not overrated either.

---

## Run order

1. Verify and correct the current-salary data (at minimum the flagged Zubac-on-Indiana row). Matching and acceptance are exact-number sensitive.
2. Land Fix 1 (override) and Fix 2 (health correction).
3. Re-run with `--tier2` so the board numbers are the real risk-adjusted ones.
4. Re-check the baseline sanity checks: known-team baseline title odds track markets, marginal additions move the needle marginally, the series resolver still reproduces history.
