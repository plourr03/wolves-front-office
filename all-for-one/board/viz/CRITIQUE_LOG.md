# THE CORRIDOR — internal critique log

Per the v3 process directive: render, screenshot, score against the checklist, iterate a
minimum of three times, log the scores. This is that log.

**Blocker on the frame-scored half.** The directive names `board/viz/reference/afo_frame.jpg`
as the mandatory visual target and says to score against it. That file is not in the repo
yet (Bobby said he is committing it; the drop-point `board/viz/reference/` is created and
waiting). So the three iterations below are scored against the WRITTEN checklist Bobby gave,
which I can evaluate by viewing my own renders. The two frame-dependent axes (weave density
and channel-glow FEEL, matched to afo_frame.jpg) are marked PENDING and are not yet tuned to
the reference. Once the frame lands I will run a fourth-plus pass scored directly against it.

Checklist (Bobby's): field darkness · channel glow · weave density · around-not-through ·
thin gold · bends only at columns. Scores are my own read, 0-10.

## Iteration 1 — grammar first pass

| axis | score | note |
|---|---|---|
| field darkness | 8 | dark ground, corridors glow on black |
| channel glow | 6 | glows, but flat; PENDING vs frame |
| weave density | 5 | reads as a uniform lane grid, not thick corridors |
| around-not-through | 6 | ring '27 has a gold entry, weave passes above; parting weak |
| thin gold | 8 | thin gold chevron entering ring '27, honest 4.5% |
| bends only at columns | 9 | all orthogonal + 45-degree jogs land on columns |

Verdict: the grammar is right (timeline L-R, rings in-line, bands, circuit bends) but the
weave is an even grid. The spec says bundles must SHARE lanes so corridors glow by
accumulation. Fix next.

## Iteration 2 — bundle into corridors (accumulation)

Change: lanes quantized into a few corridor lanes that grow in count over time, so many
traces share a lane (glow by accumulation) and the braid unwinds from the NOW trunk.

| axis | score | note |
|---|---|---|
| field darkness | 9 | |
| channel glow | 8 | corridors now read as luminous channels |
| weave density | 8 | a single trunk at NOW unwinds into a hex weave; real circuit feel |
| around-not-through | 6 | unchanged; exits still sprawl |
| thin gold | 8 | |
| bends only at columns | 9 | |

Verdict: big lift. But the failing futures (convert/requested) sprawl as diagonal bundles to
the bottom-right instead of leaving through the bottom edge at their column.

## Iteration 3 — the failure shelf and the exits

Change: convert/requested ride the UP band (alive) until their event column, then the route
ends and the tail drops them into the failure shelf — convert freezes as a red ring, requested
bends 45 degrees down and leaves through the bottom edge.

| axis | score | note |
|---|---|---|
| field darkness | 9 | |
| channel glow | 8 | PENDING final match vs frame |
| weave density | 8 | PENDING final match vs frame |
| around-not-through | 7 | ring '27 entered by rings only, alive weave routes around; ring '28 crowded |
| thin gold | 8 | |
| bends only at columns | 9 | teal all snapped; rose exits are continuous diagonals (they are leaving) |

Verdict: the exits now drain cleanly off the bottom (the 51% Ant-departs as a rose fall), the
red resets sit in the shelf at the node-9 column, and the alive weave carries the road to the
gate. Composition reads as intended for THE CORRIDOR.

---

# ONE RIVER (v4) — supersedes the corridor composition

Bobby's v4 review APPROVED the hex-weave braid ("keep exactly that braid feel"), so the
approved weave is now the confirmed reference for the weave axis (the frame `afo_frame.jpg`
is still not in the repo). Everything else simplified to one river that narrows as light
exits. Three iterations, viewed and scored against the checklist plus the approved weave.

## River iteration 1 — one river, first pass

| axis | score | note |
|---|---|---|
| field darkness | 9 | |
| approved weave feel | 8 | the hex braid reproduced, beautiful on the left |
| narrowing / conservation of light | 8 | river wide at NOW, cinches after July 27 |
| rings in the river | 7 | ring '27 parts the weave, gold entry thread; ring '28 at the gate |
| death = leaving the page | 6 | departures peel to the edges, but streak to the corners (too long) |
| one color story | 9 | teal + gold + rose whisper |

Verdict: strong, but VIOLATES law 5 — the right half decays into straight parallel wires
(the narrowing compressed the strands until the crossings vanished). Fix next.

## River iteration 2 — weave survives full width

Change: fewer, wider-spaced strands (K 11 -> 7) and a floored river height (never below 0.42
of full), so the braid keeps crossing to the gate while still narrowing.

| axis | score | note |
|---|---|---|
| approved weave feel | 9 | cleaner, more open hex; crossings now continue past July 27 |
| narrowing | 8 | still visibly thinner right, but no longer straight parallel |
| death = leaving | 6 | peels still a touch long/bright |
| bends only at columns | 9 | |

Verdict: law 5 satisfied (weave persists, thinner). Clean up the death peels.

## River iteration 3 — death as a short fade, legend off the field

Change: deaths peel at 45 degrees toward the nearest edge and fade to nothing within ~1.5
columns (dimmer, no reach to the corner); legend moved under the lede, away from the labels.

| axis | score | note |
|---|---|---|
| field darkness | 9 | |
| approved weave feel | 8 | hex braid full width, narrower right |
| narrowing / conservation | 8 | visible thinning NOW -> gate |
| rings in the river | 8 | parts around ring '27, thin gold entry, ring '28 crowded at the gate |
| death = leaving the page | 8 | clean 45-degree fades, gone within 1.5 columns, rose whisper |
| bends only at columns | 9 | |
| one color story | 9 | |
| human labels | 9 | Now / reads / deadline / playoffs / draft / July 27 / the gate |

Verdict: honors the v4 spec. Delivered as one straight still + its 50% zoom.

Note: `afo_frame.jpg` is STILL not in the repo, so the density/glow is matched to the APPROVED
weave (Bobby's v4 review), not to the frame. If the frame lands and differs, a further pass runs.

## Still to do once afo_frame.jpg lands

- match weave DENSITY to the frame (lane count 36-48, stroke restraint from the reference prototype)
- match channel GLOW feel (three-pass alphas, tone-map exposure) to the frame's luminous channels
- verify around-the-ring behavior against the frame's parting
- then re-score directly against the frame, iterating until it holds, and re-cut all stills
