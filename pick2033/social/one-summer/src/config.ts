// One Summer reel: look-and-feel. The reference is the LaMelo verdict carousel
// (lamelo/slide/carousel/slide_1..5.png, renderer render_lamelo_carousel.py):
// midnight navy, one faint green aurora, the dream-tail green reserved for the
// thing that matters, slate for everything quiet, mono numerals, a whisper of
// grain. One hero visual per beat, statement lines, real holds. No montage.
import { SANS, MONO, DISPLAY, SCRAWL } from "./fonts";

export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

// SAFE AREA per the render brief: IG/TikTok UI owns the top 220px and bottom
// 420px; the feed preview crops to the center 4:5 (y 285 to 1635). Critical
// copy stays inside both, so the working band is roughly y 300 to 1500.
export const SAFE = {
  top: 230,
  bottom: 430,
  x: 84,
};

export const CROP_4x5 = { top: 285, bottom: 1635 };

export const STAGE = {
  x: SAFE.x,
  y: SAFE.top,
  width: WIDTH - SAFE.x * 2,
  height: HEIGHT - SAFE.top - SAFE.bottom,
};

// Exact palette from render_lamelo_carousel.py (P = {...} and C_POP).
export const COLORS = {
  bgTop: "#051223", // (5, 18, 35)
  bgBot: "#0B1E35", // (11, 30, 53)
  tile: "#102136", // inset panels
  tileDeep: "#0C1A2C",
  hair: "#263C56", // hairlines on tiles and axes

  accent: "#84D668", // (132, 214, 104) the green: reserved for what matters
  accentPop: "#96E670", // (150, 230, 112) big type + the marker scrawl
  accentDeep: "#60B25C",
  accentDim: "rgba(132,214,104,0.15)", // interval-band fill

  text: "#F0F5FB", // (240, 245, 251)
  slate: "#96A8BE", // (150, 168, 190) quiet labels
  mute: "#657991", // (101, 121, 145) footnotes, method lines
};

export const FONT = {
  sans: SANS,
  mono: MONO,
  display: DISPLAY,
  scrawl: SCRAWL,

  statement: 116, // the statement lines (Bahnschrift bold)
  giant: 320, // the one number a beat exists for
  big: 66,
  body: 34, // Segoe supporting lines
  chyron: 48, // caption lines
  kicker: 26, // mono kickers
  tag: 22,
};

export const RADIUS = 4;
