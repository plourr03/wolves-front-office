// Real web fonts, loaded through Remotion so the render is pixel-accurate
// instead of falling back to system Helvetica. Inter for UI text, JetBrains Mono
// for the percentile numbers (both are the "Wolves to a T" site families).
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

const inter = loadInter("normal", {
  weights: ["400", "500", "600", "700", "800", "900"],
  subsets: ["latin"],
});

const mono = loadMono("normal", {
  weights: ["500", "700", "800"],
  subsets: ["latin"],
});

export const SANS = inter.fontFamily;
export const MONO = mono.fontFamily;
