// The carousel's real faces (render_lamelo_carousel.py): Bahnschrift Bold for
// condensed display, Consolas Bold for numerals, Segoe UI for body, Ink Free
// for the analyst's marker scrawl. These are Windows system fonts and this
// renders on the same machine, so use them first; the Google faces load as
// fallbacks so a render on another box degrades gracefully instead of to
// system Helvetica.
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";
import { loadFont as loadOswald } from "@remotion/google-fonts/Oswald";
import { loadFont as loadMarker } from "@remotion/google-fonts/PermanentMarker";

const inter = loadInter("normal", {
  weights: ["400", "500", "600", "700", "800"],
  subsets: ["latin"],
});
const mono = loadMono("normal", { weights: ["500", "700", "800"], subsets: ["latin"] });
const oswald = loadOswald("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin"] });
const marker = loadMarker("normal", { weights: ["400"], subsets: ["latin"] });

export const SANS = `"Segoe UI", ${inter.fontFamily}`;
export const MONO = `Consolas, ${mono.fontFamily}`;
export const DISPLAY = `Bahnschrift, ${oswald.fontFamily}`;
export const SCRAWL = `"Ink Free", ${marker.fontFamily}`;
