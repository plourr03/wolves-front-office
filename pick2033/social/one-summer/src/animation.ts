import { interpolate, Easing } from "remotion";

// IMPORTANT RULE FOR REMOTION:
// Never animate with D3's .transition(), CSS transitions, CSS @keyframes, or
// Tailwind animation classes. They run on wall-clock time, not the render
// clock, so frames render at the wrong moment and the video flickers. Every
// value below is a pure function of the current frame.

const EASE = Easing.bezier(0.22, 1, 0.36, 1); // calm, confident ease-out

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

// The carousel-cut entrance: a weighty rise. Slower, confident ease; no bounce.
export const riseIn = (
  frame: number,
  fps: number,
  startSec: number,
  durSec = 0.55
): { opacity: number; y: number } => {
  const p = ramp(frame, fps, startSec, durSec);
  return { opacity: p, y: (1 - p) * 34 };
};

// Number entrance for the stamp only: slam with a 2-frame scale settle.
export const slamIn = (
  frame: number,
  fps: number,
  startSec: number
): { opacity: number; scale: number } => {
  const f0 = startSec * fps;
  const opacity = interpolate(frame, [f0, f0 + 3], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(frame, [f0, f0 + 3, f0 + 6], [1.09, 0.992, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return { opacity, scale };
};

// A rubber-stamp entrance: drops from oversized, lands hard.
export const stampIn = (
  frame: number,
  fps: number,
  startSec: number
): { opacity: number; scale: number } => {
  const f0 = startSec * fps;
  const opacity = interpolate(frame, [f0, f0 + 2], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(frame, [f0, f0 + 4, f0 + 7], [1.65, 0.97, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return { opacity, scale };
};

// Tabular count-up for the 50,000 counter (ease-out so it locks confidently).
export const countUp = (
  frame: number,
  fps: number,
  startSec: number,
  durSec: number,
  to: number
): number =>
  Math.round(
    interpolate(frame, [startSec * fps, (startSec + durSec) * fps], [0, to], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    })
  );

// Telestrator draw-on: 0 to 1 across a window, for stroke-dashoffset reveals.
export const drawOn = (
  frame: number,
  fps: number,
  startSec: number,
  durSec: number
): number => ramp(frame, fps, startSec, durSec, Easing.inOut(Easing.cubic));

// A single emphasis pulse (0 -> 1 -> 0), for the red cell in scene 5.
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

// A decaying shake (px) for a stamp landing.
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
