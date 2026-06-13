import { interpolate, spring, Easing } from "remotion";
import { Beat, activeBeatIndex, focusRows } from "./timeline";
import { WIDTH, HEIGHT } from "./config";

// Every moving value is a pure function of the current frame. No CSS
// transitions, no d3 .transition(): that is what keeps the render deterministic.

const EASE = Easing.bezier(0.22, 1, 0.36, 1); // calm, confident ease-out
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const ramp = (
  frame: number,
  fps: number,
  startSec: number,
  durSec: number,
  easing = EASE
): number =>
  interpolate(frame, [startSec * fps, (startSec + durSec) * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

// A fast, weighty grow for the opening bar: races up, then settles.
export const raceGrow = (
  frame: number,
  fps: number,
  startSec: number,
  durSec: number
): number =>
  interpolate(frame, [startSec * fps, (startSec + durSec) * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

// Per-bar grow with a small stagger, for the chart assembling in.
export const barGrow = (
  frame: number,
  fps: number,
  index: number,
  baseDelaySec = 0,
  staggerSec = 0.12
): number =>
  spring({
    frame,
    fps,
    delay: Math.round((baseDelaySec + index * staggerSec) * fps),
    config: { damping: 200 },
  });

// A decaying shake (px) for the "slam into the red" impact.
export const shake = (
  frame: number,
  fps: number,
  startSec: number,
  durSec: number,
  amp: number
): number => {
  const t = frame / fps - startSec;
  if (t < 0 || t > durSec) return 0;
  const decay = 1 - t / durSec;
  return Math.sin(t * 46) * amp * decay * decay;
};

// Telestrator draw-on: 0 to 1 across a window for stroke-dashoffset reveals.
export const drawOn = (
  frame: number,
  fps: number,
  startSec: number,
  durSec: number
): number => ramp(frame, fps, startSec, durSec, Easing.inOut(Easing.cubic));

// A single emphasis pulse (0 -> 1 -> 0) for the red-bar pulse.
export const pulse = (
  frame: number,
  fps: number,
  startSec: number,
  durSec: number
): number => {
  const p = interpolate(frame, [startSec * fps, (startSec + durSec) * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return Math.sin(p * Math.PI);
};

// SPOTLIGHT. Rows the script is not on dim and blur back; on the "filter" beat
// the two non-predictive rows fully fade out. Cross-faded between beats so a row
// never flashes.
const DIM = 0.22;

const opacityTarget = (beat: Beat, i: number): number => {
  const f = focusRows(beat.view);
  if (f === null) return 1;
  if (f.includes(i)) return 1;
  return beat.view === "filter" ? 0 : DIM;
};
const litTarget = (beat: Beat, i: number): number => {
  const f = focusRows(beat.view);
  if (f === null) return 1;
  return f.includes(i) ? 1 : 0;
};

export const rowSpotlight = (
  frame: number,
  fps: number,
  beats: Beat[],
  i: number
): { opacity: number; blur: number; lit: number } => {
  const idx = activeBeatIndex(frame, beats);
  const cur = beats[idx];
  const prev = idx > 0 ? beats[idx - 1] : cur;
  const t = ramp(frame, fps, cur.startSec, 0.5, Easing.inOut(Easing.cubic));
  const opacity = lerp(opacityTarget(prev, i), opacityTarget(cur, i), t);
  const lit = lerp(litTarget(prev, i), litTarget(cur, i), t);
  return { opacity, blur: (1 - lit) * 3.0, lit };
};

// CAMERA. The fingerprint reads as a whole and the focused row is already
// carried by the spotlight (dim + blur + the telestrator circle), so the camera
// stays put. Zooming a single full-width row pushed the right-aligned number and
// its circle off the edge, so we do not zoom at all. Kept as identity here in
// case a future beat wants a move.
export const getCamera = (
  _frame: number,
  _fps: number,
  _beats: Beat[],
  _rowY: (i: number) => number
): { scale: number; ty: number; originX: number; originY: number } => {
  return { scale: 1, ty: 0, originX: WIDTH / 2, originY: HEIGHT / 2 };
};
