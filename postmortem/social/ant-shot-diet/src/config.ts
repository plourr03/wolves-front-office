// Global look-and-feel. Warm-dark print stock, one accent, intensity (not a
// rainbow) carries good/bad. The baseline (regular season) is quiet chalk ink;
// only the thing that changed gets the warm vermilion. Brand green is reserved
// strictly as the signature (wordmark dot, progress, sign-off rule) and never
// touches a number or a bar.
import { SANS, MONO, DISPLAY, SCRAWL } from "./fonts";

export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

export const SAFE = {
  top: 210,
  bottom: 430,
  x: 96,
};

export const STAGE = {
  x: SAFE.x,
  y: SAFE.top,
  width: WIDTH - SAFE.x * 2, // 888
  height: HEIGHT - SAFE.top - SAFE.bottom,
};

const BASELINE = "#C9C5B6";

export const COLORS = {
  bgTop: "#12120F",
  bgBot: "#0A0A08",
  inset: "#0A0B08",
  insetEdge: "rgba(243,241,233,0.10)",

  baseline: BASELINE, // the "before" / regular-season state: quiet chalk ink
  alert: "#E4572E", // the "after" / playoff state: warm editorial vermilion
  twistAfter: BASELINE, // Act 3: hold exactly at chalk so it visibly refuses to redden

  chalk: "#F3F1E9", // telestrator, reference tick, scrawled word
  text: "#FBFAF6",
  subtext: "#C9C5B6",
  tertiary: "rgba(243,241,233,0.42)",
  hairline: "rgba(243,241,233,0.14)",

  good: "#1FBF66", // brand green, signature ONLY

  bg: "#0A0A08",
  accent: "#1FBF66",
};

export const FONT = {
  family: SANS,
  mono: MONO,
  display: DISPLAY,
  scrawl: SCRAWL,

  hero: 188, // the single giant before/after number (mono)
  card: 96, // hook / payoff / sign-off lines (Oswald)
  caption: 60, // the plain-spoken sentence under the bar (Oswald)
  kicker: 30, // per-act caps label (Oswald)
  unit: 27, // technical descriptor under the hero number
  fromTag: 42, // the "before 42%" tag (mono)
  scrawlSize: 64, // the hand-scrawled marker margin word
  delta: 30, // the small magnitude label by the mark
  wordmark: 24,
  footer: 22,
  pill: 24,
};
