# Shot grammar: timing motion to the script

A clip is a short list of beats. Each beat is one moment that lines up with one
line of the spoken script, so the picture moves exactly when the words land.
Beats live in `src/timeline.ts` as objects with a start time in seconds, a kind,
a caption, and an optional target.

The job when building a clip is to write the script first, then place one beat
per line, then pick a move for each beat.

## The moves

draw. The chart animates in (bars grow, a line draws itself). Use it once, right
after the hook, the instant you first reveal the data. In the template the bars
hold at zero through the opening hook and grow in on the first draw beat.

zoom. The camera pushes in so one item fills the frame. Use it when the script
names the subject, for example "and here is where the Wolves sit." Set target to
the index of the row to focus on. The push-in anchors on that item so it grows
in place instead of jumping.

WARNING: do not zoom a row whose content spans the full width (a label on the
left, a bar, a right-aligned number). The zoom pushes the label and the number
off the edges. For vertical, full-width charts, use spotlight instead. Reserve
zoom for charts where the subject is a compact mark (a scatter dot, a single bar
in a horizontal field) with room around it.

spotlight. Keep the whole chart in place and dim plus slightly blur every row
except the one (or few) the script is on. This is the workhorse focus move for
vertical charts, because nothing ever leaves the frame. Drive it from a `focus`
array on the beat (the row indices that stay lit). Cross-fade between beats so a
row that stays dim across two beats does not flash. Pair it with a telestrator
mark for the "we are looking at this one" read.

telestrator. A hand-drawn circle (or underline/bracket) marked onto the number
or mark you are discussing, like a coach on film. Draw an SVG `ellipse` with
`pathLength={1}`, `strokeDasharray={1}`, and `strokeDashoffset={1 - p}` where `p`
ramps 0 to 1, rotate it a few degrees, and give it a round-cap chalk stroke so it
reads as marked by hand, not printed. This is the highest-value "a person made
this" move in the whole kit.

reset. The camera pulls back out to show the whole field again. Use it near the
end when you widen back out for the closing line or the call to action.

hold. Nothing moves. Use it to let a viewer read a number or a caption. Keep
holds short, a second or two, or the clip feels dead.

punch. A quick scale pop on the target for emphasis. Use it on the single most
important line, usually the payoff ("and it cost them the season").

## The timing rule

Something should change about every two to three seconds. If a stretch longer
than that has no new move and no new caption, the clip drags and people scroll.
You do not need a different move every beat, a fresh caption counts as change.

A clean default rhythm for a 20 to 25 second clip:

0 to 2s, hold on the hook (chart hidden).
2 to 6s, draw the chart in.
6 to 9s, zoom to the subject.
9 to 13s, hold on the key insight.
13 to 17s, punch on the payoff.
17s to end, reset and show the call to action.

The sample beats in `timeline.ts` follow exactly this shape, so you can use them
as a starting skeleton and just change the times, captions, and target.

## Matching the move to the chart type

The template chart is a ranking of bars, so draw means bar growth. If you swap in
a different D3 chart, keep the same beat kinds but change how the chart reacts to
the frame:

Line or trend chart. For draw, animate the line drawing itself: give the path a
stroke-dasharray equal to its length and interpolate stroke-dashoffset from that
length down to zero across the draw window. Reveal a marker at the end as it
finishes.

Scatter. For draw, fade and scale the dots in with a short per-dot stagger. For
zoom, target the dot you are discussing and aim the camera at its position.

Fingerprint / multi-component (several percentile bars on one 0 to 100 scale).
Walk it one component at a time with spotlight, not zoom. Number-led intro reads
well here: hold the bars at zero and let the value labels count up and stagger
onto the screen first, then grow the bars out to meet them. Tell the viewer it is
a 0 to 100 metric, not a rank: show `0` and `100` endpoints and say "scored 0 to
100" so a "90" is not misread as 90th place.

Any chart. Whatever the type, the two rules never change: delete every animation
the chart library does on its own (no .transition, no .duration), and compute
every moving value from the current frame. That is what keeps the render clean.

## Intros, naming, and multi-scene clips

A few structural moves that earn their keep:

numbers-on intro. Instead of a generic "chart draws in," let the key numbers
animate onto a near-empty screen while the hook is spoken (count up, staggered),
then resolve into the chart. Numbers are inherently dramatic and feel like data,
not decoration.

name-the-metric in place. When the clip defines a composite ("all of these
together I call X"), name it while the components are still on screen, by morphing
the chart title (crossfade the old title out, the new name in) rather than cutting
to a separate title card. The viewer sees the parts become the whole.

scene cut. A clip can hold more than one chart (e.g. a fingerprint that cuts to a
league ranking). Render scene A or B by frame with a ~0.4s crossfade, and key
each scene's internal animation off the second it starts, not off frame zero.

## Adding a new move

To add a move (say a "split" that highlights two items at once), add its name to
BeatKind in `timeline.ts`, then handle that name in `getCamera` in
`src/animation.ts` and, if it changes the chart itself, in the chart component.
Keep each move a pure function of the frame.
