import { interpolate, spring, Easing } from "remotion";
import { Beat, activeBeatIndex, focusRows } from "./timeline";
import { WIDTH, HEIGHT } from "./config";

// IMPORTANT RULE FOR REMOTION:
// Never animate with D3's .transition(), CSS transitions, CSS @keyframes, or
// Tailwind animation classes. They run on wall-clock time, not the render clock,
// so frames render at the wrong moment and the video flickers. Every value below
// is a pure function of the current frame, which keeps each frame deterministic.

const EASE = Easing.bezier(0.22, 1, 0.36, 1); // calm, confident ease-out
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// Smooth 0 to 1 ramp over a window, clamped at both ends.
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

// Bar growth fraction (0 to 1) with a per-bar stagger and a touch of spring life.
export const barGrow = (
  frame: number,
  fps: number,
  index: number,
  baseDelaySec = 0,
  staggerSec = 0.1
): number =>
  spring({
    frame,
    fps,
    delay: Math.round((baseDelaySec + index * staggerSec) * fps),
    config: { damping: 200 },
  });

// Caption entrance: a quick fade with a small upward slide.
export const captionIn = (
  frame: number,
  fps: number,
  startSec: number
): { opacity: number; translateY: number } => {
  const p = ramp(frame, fps, startSec, 0.4);
  return { opacity: p, translateY: (1 - p) * 24 };
};

// A decaying shake (px) for an impact, e.g. a bar slamming into a zone.
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

// Telestrator draw-on: 0 to 1 across a window, for stroke-dashoffset reveals.
export const drawOn = (
  frame: number,
  fps: number,
  startSec: number,
  durSec: number
): number => ramp(frame, fps, startSec, durSec, Easing.inOut(Easing.cubic));

// A single emphasis pulse (0 -> 1 -> 0).
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

// SPOTLIGHT. The workhorse focus move for vertical, full-width charts: keep the
// whole chart in place and dim + slightly blur the rows the script is not on.
// A beat's `focus` lists the lit row indices (null/empty means all lit). This
// cross-fades between the previous beat's state and the current one's, so a row
// that stays dim across two beats never flashes.
const DIM = 0.24;

export const rowSpotlight = (
  frame: number,
  fps: number,
  beats: Beat[],
  i: number
): { opacity: number; blur: number; lit: number } => {
  const idx = activeBeatIndex(frame, beats);
  const cur = beats[idx];
  const prev = idx > 0 ? beats[idx - 1] : cur;
  const lit = (b: Beat) => {
    const f = focusRows(b);
    return f === null || f.includes(i) ? 1 : 0;
  };
  const t = ramp(frame, fps, cur.startSec, 0.3, Easing.inOut(Easing.cubic));
  const litNow = lerp(lit(prev), lit(cur), t);
  return {
    opacity: DIM + (1 - DIM) * litNow,
    blur: (1 - litNow) * 3.0,
    lit: litNow,
  };
};

// CAMERA. Default is identity: the spotlight carries focus and nothing leaves
// frame. Avoid zooming a full-width row (it pushes the label and the right-
// aligned number off the edges). If a chart's subject is a compact mark with
// room around it, you can extend this to ease scale/translate toward it.
export const getCamera = (): { scale: number; ty: number; originX: number; originY: number } => ({
  scale: 1,
  ty: 0,
  originX: WIDTH / 2,
  originY: HEIGHT / 2,
});
