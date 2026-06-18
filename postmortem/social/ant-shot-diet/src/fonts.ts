// Real web fonts, four jobs. A condensed athletic sans for the voice (broadcast /
// sports-graphic energy), a monospace for the numbers (data-desk receipts), a
// clean sans demoted to small chrome, and a marker face for the hand-scrawled
// chalk annotations (the film-room telestrator touch).
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";
import { loadFont as loadOswald } from "@remotion/google-fonts/Oswald";
import { loadFont as loadMarker } from "@remotion/google-fonts/PermanentMarker";

const inter = loadInter("normal", {
  weights: ["400", "500", "600", "700", "800", "900"],
  subsets: ["latin"],
});
const mono = loadMono("normal", { weights: ["500", "700", "800"], subsets: ["latin"] });
const oswald = loadOswald("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin"] });
const marker = loadMarker("normal", { weights: ["400"], subsets: ["latin"] });

export const SANS = inter.fontFamily;
export const MONO = mono.fontFamily;
export const DISPLAY = oswald.fontFamily;
export const SCRAWL = marker.fontFamily;
