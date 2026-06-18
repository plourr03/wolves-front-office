import { interpolate, spring, Easing } from "remotion";

// Every moving value is a pure function of the current frame. No CSS
// transitions, no d3 .transition(): that is what keeps the render deterministic.
// Weighty, confident ease-out rather than a springy bounce, per the human look.

const EASE = Easing.bezier(0.22, 1, 0.36, 1);
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// 0 -> 1 ramp across [startSec, startSec+durSec], clamped.
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

// Count a value from `from` to `to` across a window. Pair with tabular mono
// figures so the digits do not jiggle width as they climb.
export const countTo = (
  frame: number,
  fps: number,
  startSec: number,
  durSec: number,
  from: number,
  to: number
): number => lerp(from, to, ramp(frame, fps, startSec, durSec));

// Per-bar grow with a small stagger, for the chart assembling in.
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

// Telestrator draw-on: 0 to 1 across a window for stroke-dashoffset reveals.
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
