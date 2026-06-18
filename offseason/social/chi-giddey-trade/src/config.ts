// Carousel look-and-feel. Same warm-dark print stock and tokens as the rest of
// the feed (the ant-shot-diet / fingerprint redesign): one accent (warm
// vermilion) for the thing that matters, quiet chalk for everything else, and
// brand green reserved strictly as the signature (wordmark dot, page rule). Flat
// fills, squared corners, a whisper of grain, mono numerals. No glow, no rainbow.
import { SANS, MONO, DISPLAY, SCRAWL } from "./fonts";

// Instagram / TikTok portrait carousel.
export const WIDTH = 1080;
export const HEIGHT = 1350;
export const FPS = 30;

export const SAFE = {
  top: 96,
  bottom: 104,
  x: 84,
};

export const COLORS = {
  bgTop: "#12120F",
  bgBot: "#0A0A08",
  inset: "#0E0F0C",
  insetEdge: "rgba(243,241,233,0.10)",

  baseline: "#C9C5B6", // the "before" / quiet state: chalk ink
  alert: "#00843D", // the accent: Wolves to a T brand green (--accent-default). the thing that matters
  alertDim: "rgba(0,132,61,0.18)", // --accent-subtle: fills behind the primary green

  chalk: "#F3F1E9", // telestrator scrawl, reference ticks
  text: "#FBFAF6",
  subtext: "#C9C5B6",
  tertiary: "rgba(243,241,233,0.46)",
  hairline: "rgba(243,241,233,0.14)",
  hairlineSoft: "rgba(243,241,233,0.08)",

  good: "#00843D", // brand green, unified with the accent (one green: the Wolves)
};

export const FONT = {
  sans: SANS,
  mono: MONO,
  display: DISPLAY,
  scrawl: SCRAWL,

  hero: 150, // the single biggest number on a slide (mono)
  title: 92, // hook headline (Oswald)
  big: 64, // section headline / large card line (Oswald)
  body: 38, // plain-spoken sentence (Oswald 400/500)
  bodySans: 31, // explanatory sentence (Inter)
  num: 52, // salary / threshold numbers (mono)
  numSmall: 34, // secondary numbers (mono)
  kicker: 28, // section label / eyebrow (Inter, tracked)
  tag: 24, // hypothetical tag, "my model" tag
  scrawlSize: 46, // hand-scrawled annotation
  wordmark: 26,
  page: 24,
};

// shared radius for squared (not pill) corners
export const RADIUS = 4;
