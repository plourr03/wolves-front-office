// Real web fonts, loaded through Remotion so the render is pixel-accurate
// instead of falling back to system Helvetica (which looks cheap instantly).
// Swap these for the source publication's actual typefaces.
import { loadFont as loadSans } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

const sans = loadSans("normal", {
  weights: ["400", "500", "600", "700", "800", "900"],
  subsets: ["latin"],
});

const mono = loadMono("normal", {
  weights: ["500", "700", "800"],
  subsets: ["latin"],
});

export const SANS = sans.fontFamily;
export const MONO = mono.fontFamily;
