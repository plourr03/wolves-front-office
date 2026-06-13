import { FPS } from "./config";

// A "beat" is one moment in the clip. Each beat lines up with a line of your
// spoken script, so when you say a sentence, the matching thing happens on
// screen. This is the heart of "transitions synced to the script".
//
// kind controls the headline move:
//   draw   = the chart animates in (bars grow)
//   hold   = nothing moves; let the viewer read (use these for real holds)
//   punch  = a quick emphasis pop
// focus lists the row indices that stay LIT; every other row dims and blurs
//   (the spotlight). Leave it off to light the whole chart. This is the focus
//   move to use instead of a cropping camera zoom on full-width rows.
// caption is the on-screen text (a few words). index is an optional chapter
//   number ("01") shown on the editorial chyron.
export type BeatKind = "draw" | "hold" | "punch";

export type Beat = {
  startSec: number;
  kind: BeatKind;
  caption: string;
  focus?: number[];
  index?: string;
  cta?: boolean; // render this caption as a centered title card
};

export const secToFrame = (sec: number): number => Math.round(sec * FPS);

export const activeBeatIndex = (frame: number, beats: Beat[]): number => {
  let idx = 0;
  for (let i = 0; i < beats.length; i++) {
    if (frame >= secToFrame(beats[i].startSec)) idx = i;
  }
  return idx;
};

export const secondsIntoBeat = (frame: number, beat: Beat): number =>
  Math.max(0, frame / FPS - beat.startSec);

// The lit rows for a beat (null means all lit).
export const focusRows = (beat: Beat): number[] | null =>
  beat.focus && beat.focus.length ? beat.focus : null;

// ---------------------------------------------------------------------------
// SAMPLE BEATS. Replace with the beats for your clip. Size each beat to how long
// its spoken line takes (about 3.3 words/second); give ideas room to breathe.
// ---------------------------------------------------------------------------
export const BEATS: Beat[] = [
  { startSec: 0.0, kind: "hold", caption: "Most pickup-style\noffense in the NBA" },
  { startSec: 3.5, kind: "draw", caption: "Every team, ranked" },
  { startSec: 8.0, kind: "hold", caption: "And it's not close", focus: [0], index: "01" },
  { startSec: 13.0, kind: "punch", caption: "Why the ceiling\ncollapsed", focus: [0] },
  { startSec: 18.0, kind: "hold", caption: "Full breakdown,\nlink in bio", cta: true },
];

const TAIL_SEC = 3.0;

export const DURATION_IN_FRAMES = secToFrame(
  BEATS[BEATS.length - 1].startSec + TAIL_SEC
);
