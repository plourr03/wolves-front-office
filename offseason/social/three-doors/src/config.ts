// Carousel look-and-feel. Same warm-dark print stock and tokens as the rest of
// the feed (the chi-giddey trade post / fingerprint redesign): one accent (brand
// green) for the thing that matters, quiet chalk for everything else. Flat fills,
// squared corners, a whisper of grain, mono numerals. No glow, no rainbow.
//
// One functional exception, per the brief: apronBreak (a warm vermilion red) is a
// STATE signal, the over-the-first-apron portion of the cap meter (you broke the
// apron). It is the only red in the palette and is used only there.
import { SANS, MONO, DISPLAY, SCRAWL } from "./fonts";

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
  alert: "#00843D", // the accent: Wolves to a T brand green. the thing that matters
  alertDim: "rgba(0,132,61,0.18)", // fills behind the primary green

  apronBreak: "#E2503A", // FUNCTIONAL: over-the-first-apron state. the only red, used only in the cap meter
  apronBreakDim: "rgba(226,80,58,0.20)",

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

  hero: 150,
  title: 92,
  big: 64,
  body: 38,
  bodySans: 31,
  num: 52,
  numSmall: 34,
  kicker: 28,
  tag: 24,
  scrawlSize: 46,
  wordmark: 26,
  page: 24,
};

export const RADIUS = 4;

// Cap-meter scale (shared by every door so the three meters read as one progression).
export const CAP = {
  lo: 150, // $M, left edge
  hi: 225, // $M, right edge
  tax: 201.0,
  apron1: 209.1, // emphasized: the line the squeeze crosses
  apron2: 222.0,
};
