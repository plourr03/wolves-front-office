# Ant shot-diet: "THE MOVE" (silent cut, beat by beat)

A silent 9:16 vertical social post (1080x1920, 30fps, ~29.6s, no voiceover, music
added in the editor). One story told as three full-screen ACTS: San Antonio
didn't beat Anthony Edwards' shot in the 2025-26 playoffs, they relocated it.

Design: each act is ONE giant before/after number bound to ONE squared bar by a
shared frame-ramp, so the number and the bar always finish on the same frame.
Warm paper-dark stock under grain; Oswald (condensed athletic sans) for the
voice; JetBrains Mono for the numbers; Inter for small chrome; Permanent Marker
for the hand-scrawled chalk words. The regular-season "before" is quiet chalk;
only the thing that changed reddens to warm vermilion. Brand green is reserved as
the signature (wordmark dot, progress, sign-off rule).

Source: Q3 mechanism analysis, re-validated for this post against
nba_shot_chart_detail on 2026-06-17. Every on-screen number is in provenance.json.

## Beat sheet

| Time | On screen | Motion |
|------|-----------|--------|
| 0:00 | "San Antonio didn't beat Ant's shot." | Hook card (Oswald) fades up on the page; masthead draws in. |
| 0:03 | "They moved it." | Second line lands bold; a brand-green rule draws in beneath it. |
| 0:05 | ACT 1 "WHAT THEY TOOK" / 42% / "The three was his go-to look." | Number + bar assemble in chalk at the baseline. |
| 0:09 | 42% -> 28% / "San Antonio pushed him off the line." | Number counts down and the bar RETREATS and reddens in lockstep; chalk tick marks where 42% sat; down-arrow + "14 pts fewer"; slash + scrawled "took". |
| 0:13 | ACT 2 "WHERE THEY PUT HIM" / 15% / "They walled off the arc," | Baseline holds ~2.2s so 15% registers. |
| 0:15 | 15% -> 21% / "and funneled him to where the bigs wait." | Bar GROWS rightward (opposite of Act 1) and reddens; up-arrow + "6 pts more"; lasso + scrawled "moved". |
| 0:20 | ACT 3 "AND YET" / 48.9% / "His shot diet was wrecked." | The make-rate act; unit reads "field goal %" so the metric type flips. |
| 0:21 | 48.9% -> 46.9% / "And yet his make rate barely moved." | The number/bar tease a faint red then settle back to CHALK (refuse to redden); an "=" unchanged glyph; bracket over the tiny gap + "2.0 pts lower" + scrawled "barely". |
| 0:24 | "They changed the shape. Not the shooter." | Stage clears to a clean Oswald payoff card + green rule. |
| 0:27 | "More at Wolves to a T." | Sign-off card: green dot, line, green rule; progress completes. |

A persistent masthead (wordmark + "NO. 07" + hairline), a sample disclosure
("REG. SEASON 61 GP -> ROUND 2 vs SAS 6 GP", the 6-game series stated on screen),
and a footer ("ACT 0n / 03" + "nba_shot_chart_detail · 2025-26") sit through the
acts. The acts mix two metric TYPES on purpose: Acts 1-2 are shares of his
attempts ("were threes", "came from 11-16 ft"), Act 3 is a make rate ("went in ·
field goal %"); the unit line names the type so the giant percent can't be misread
as a shooting percentage.

## The numbers (all validated, see provenance.json)

| Claim | Regular season | R2 vs SAS | Move |
|-------|----------------|-----------|------|
| Share of his attempts that were threes | 42% | 28% | 14 pts fewer |
| Share from the floater zone (11-16 ft) | 15% | 21% | 6 pts more |
| Field goal % | 48.9% | 46.9% | 2.0 pts lower |
| Games | 61 | 6 | (disclosed on screen) |

## Rebuild / re-render

```
# 1. re-validate every on-screen number against the warehouse (from postmortem/)
python social/ant-shot-diet/validate.py

# 2. preview in the studio
cd social/ant-shot-diet && npm run dev

# 3. render the silent video (no audio track; add music in the editor)
npm run render          # -> out/ant-shot-diet.mp4 (passes --muted)
```

## Why it reads human (not templated)

- A condensed athletic voice (Oswald) + mono data numerals + a real marker face
  for the chalk scrawls; warm paper stock under visible grain.
- One idea per breath: a single number and a single bar per act, never a grid.
- Intensity, not a rainbow, carries the story: chalk baseline, one vermilion
  alert, and the Act-3 restraint (it refuses to redden) IS the punchline.
- Film-room telestrator marks (slash, lasso, bracket) drawn on by hand; a chalk
  reference tick shows where the value used to be.
- Left-aligned spine, an issue number, an act counter, and a footer that names
  the warehouse table the numbers came from.
- No glow, no bloom, no drop shadows (flat editorial film-room look).
