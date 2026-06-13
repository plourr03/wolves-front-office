// Global look-and-feel for the vertical clip.
import { SANS, MONO } from "./fonts";

export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

// SAFE AREA: the app UI covers the top and bottom of the screen.
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

// COLORS. Editorial and restrained, straight off the article chart. No neon, no
// heavy glow: the credibility comes from looking like the published chart, not
// like a default "premium" template.
export const COLORS = {
  bgTop: "#101216",
  bgBot: "#08090B",
  panel: "#121419",
  inset: "#0A0B0E", // bar track
  insetEdge: "rgba(255,255,255,0.07)",
  error: "#FF5C5C", // pickup zone, extreme components
  warning: "#F5A623", // middling components
  good: "#1FBF66", // healthy components
  info: "#4A9EFF",
  chalk: "#F3F1E9", // telestrator / hand-marked annotations
  text: "#FFFFFF",
  subtext: "rgba(255,255,255,0.72)",
  tertiary: "rgba(255,255,255,0.46)",
  hairline: "rgba(255,255,255,0.10)",
  gridline: "rgba(255,255,255,0.16)",
  // legacy
  bg: "#0A0B0E",
  accent: "#1FBF66",
};

export const PICKUP_THRESHOLD = 66;
export const LEAGUE_AVG = 50;
export const SCALE_MAX = 100;

export type BucketKey = "error" | "warning" | "good";
export const bucketKey = (v: number): BucketKey =>
  v >= PICKUP_THRESHOLD ? "error" : v >= 34 ? "warning" : "good";
export const bucketColor = (v: number): string => COLORS[bucketKey(v)];

export const FONT = {
  hook: 96,
  chyron: 80,   // the main caption line
  kicker: 28,   // small uppercase context label
  index: 30,    // chapter number 01..05
  value: 84,    // big percentile number
  label: 44,    // component names
  desc: 29,     // component descriptions
  tag: 23,      // PICKUP ZONE / LEAGUE AVG pills
  title: 38,
  small: 26,
  family: SANS,
  mono: MONO,
};
