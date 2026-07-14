import { FPS } from "./config";

// The One Summer reel, seventh cut (the buddy cut): cold open ON the chart
// with the 1-to-44 rug-pull in the first breath, no second sensitivity
// number (the cumulative 56-to-71 pair stays whole for reel two), the ONE
// SUMMER statement card as the breather before LaMelo enters, and the loop
// landing on the flat-line 1% state. Runs 57.0s.
//
// Fact record: the .450-scenario walk-year hazard DOES exist in
// edwards_hazard_FINAL.json (0.5649 [80%: 0.4709, 0.6563]); it was cut on
// editorial grounds (two different 56s across assets), not accuracy.
//
// When re-timing, run scripts/make_ai_vo.py and paste its printed starts.

export type BeatId =
  | "curve1"
  | "curve1b"
  | "curve2"
  | "curve2r"
  | "curve2s"
  | "curve3"
  | "h1"
  | "unsig"
  | "unsig2"
  | "twomax"
  | "twomaxb"
  | "twomax2"
  | "twomax2b"
  | "cta1"
  | "cta2"
  | "loop";

export type Beat = {
  id: BeatId;
  startSec: number;
  caption?: string;
};

export const BEATS: Beat[] = [
  { id: "curve1", startSec: 0.0, caption: "One percent. Those are Ant's odds of\nleaving Minnesota this year," },
  // caption-only page inside the same clip
  { id: "curve1b", startSec: 3.7, caption: "with two years left on his deal." },
  { id: "curve2", startSec: 6.7, caption: "His 2029 walk year? Forty-four." },
  { id: "curve2r", startSec: 9.7, caption: "Really, it's anywhere\nbetween 35 and 53 percent." },
  { id: "curve2s", startSec: 15.1, caption: "And that's with the team winning." },
  { id: "curve3", startSec: 17.2, caption: "And this is based on forty years\nof data, not a gut feeling." },
  { id: "h1", startSec: 22.8, caption: "The whole LaMelo trade\ncomes down to that one summer." },
  { id: "unsig", startSec: 26.5, caption: "Not only that, but LaMelo's deal\nends the same July." },
  { id: "unsig2", startSec: 30.4, caption: "And we still have not extended him." },
  { id: "twomax", startSec: 33.0, caption: "So, we have two max guys." },
  { id: "twomaxb", startSec: 35.7, caption: "One summer that the next decade of\nbasketball in Minnesota hinges on." },
  { id: "twomax2", startSec: 41.2, caption: "The Wolves and Hornets both made" },
  { id: "twomax2b", startSec: 44.1, caption: "opposing bets on where\nthat summer will land." },
  { id: "cta1", startSec: 48.0, caption: "What are the most likely futures\nfor that summer?" },
  // The CTA card carries the spoken words; no lower-third on the send line.
  { id: "cta2", startSec: 51.5 },
  // Loop-friendly ending: back onto the chart's flat-line 1% state.
  { id: "loop", startSec: 56.5 },
];

export const END_SEC = 57.0;

export const secToFrame = (sec: number): number => Math.round(sec * FPS);

export const DURATION_IN_FRAMES = secToFrame(END_SEC);

// Beat starts by id, for keying scene-internal animation.
export const T: Record<BeatId, number> = BEATS.reduce(
  (acc, b) => ({ ...acc, [b.id]: b.startSec }),
  {} as Record<BeatId, number>
);

export const activeBeatIndex = (frame: number, beats: Beat[]): number => {
  let idx = 0;
  for (let i = 0; i < beats.length; i++) {
    if (frame >= secToFrame(beats[i].startSec)) idx = i;
  }
  return idx;
};
