// Global look-and-feel. This is the first file to edit when you adapt the
// template to a brand. Paste the SOURCE SITE'S real color tokens here so the clip
// looks like the published chart, not a generic template.
import { SANS, MONO } from "./fonts";

// 9:16 vertical, the native shape for TikTok, Reels, and Shorts. 30fps renders
// fast and is plenty smooth for chart motion.
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

// SAFE AREA: the app UI covers the top and bottom of the screen. Keep anything
// important (chart, numbers, captions) inside these insets.
export const SAFE = {
  top: 230,
  bottom: 430,
  x: 70,
};

export const STAGE = {
  x: SAFE.x,
  y: SAFE.top,
  width: WIDTH - SAFE.x * 2,
  height: HEIGHT - SAFE.top - SAFE.bottom,
};

// COLORS. Editorial and restrained by default: a near-flat dark background and
// solid marks, NOT gradients/glow/neon (that look reads as AI slop). Replace
// these with the source site's exact tokens.
export const COLORS = {
  bgTop: "#101216",
  bgBot: "#08090B",
  inset: "#0A0B0E", // bar track
  insetEdge: "rgba(255,255,255,0.07)",
  highlight: "#1FBF66", // the featured series (replace with brand accent)
  dim: "rgba(255,255,255,0.26)", // everyone else
  chalk: "#F3F1E9", // telestrator / hand-marked annotations
  text: "#FFFFFF",
  subtext: "rgba(255,255,255,0.72)",
  tertiary: "rgba(255,255,255,0.46)",
  hairline: "rgba(255,255,255,0.10)",
  accent: "#1FBF66", // progress bar + flourishes
  // legacy
  bg: "#0A0B0E",
};

// FONT SIZES. Big for a muted phone audience.
export const FONT = {
  hook: 92,
  chyron: 76, // the main caption line
  kicker: 28,
  index: 30, // chapter number
  value: 80, // big numbers
  label: 44, // row names
  tag: 24,
  title: 38,
  small: 26,
  family: SANS,
  mono: MONO,
};
