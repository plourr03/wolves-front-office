import { FPS } from "./config";

// The One Summer reel, eighth cut: Bobby's reworded chart act. Cold open on
// "about 1 percent," the 44 lands as "Forty-four percent," the range line is
// out, and the sensitivity beat is back in the bad-year shape with the band
// top spoken honestly: "jump to 56, maybe as high as 66 percent" (decline
// walk-year hazard 0.5649 [80%: 0.4709, 0.6563], receipt in the repo). The
// 80% band 47-66 is printed on screen under the 56. Calmer delivery settings
// on the whole act. Runs 64.4s.
//
// When re-timing, run scripts/make_ai_vo.py and paste its printed starts.

export type BeatId =
  | "curve1"
  | "curve1b"
  | "curve2"
  | "curve2s"
  | "curve2b"
  | "curve2b2"
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
  { id: "curve1", startSec: 0.0, caption: "Anthony Edwards' odds of leaving\nMinnesota this year are about 1%," },
  // caption-only page inside the same clip
  { id: "curve1b", startSec: 4.7, caption: "with two years left on his contract." },
  { id: "curve2", startSec: 8.4, caption: "His 2029 walk year?\nForty-four percent." },
  { id: "curve2s", startSec: 12.5, caption: "And that's with the team winning." },
  { id: "curve2b", startSec: 14.9, caption: "Let's say the Wolves have a bad year\nand win just 37 games?" },
  // caption-only page inside the same clip
  { id: "curve2b2", startSec: 20.4, caption: "The odds of Ant leaving jump to 56,\nmaybe as high as 66 percent." },
  { id: "curve3", startSec: 25.7, caption: "And this is based on forty years\nof data, not a gut feeling." },
  { id: "h1", startSec: 30.2, caption: "The whole LaMelo trade\ncomes down to that one summer." },
  { id: "unsig", startSec: 33.9, caption: "Not only that, but LaMelo's deal\nends the same July." },
  { id: "unsig2", startSec: 37.8, caption: "And we still have not extended him." },
  { id: "twomax", startSec: 40.4, caption: "So, we have two max guys." },
  { id: "twomaxb", startSec: 43.1, caption: "One summer that the next decade of\nbasketball in Minnesota hinges on." },
  { id: "twomax2", startSec: 48.6, caption: "The Wolves and Hornets both made" },
  { id: "twomax2b", startSec: 51.5, caption: "opposing bets on where\nthat summer will land." },
  { id: "cta1", startSec: 55.4, caption: "What are the most likely futures\nfor that summer?" },
  // The CTA card carries the spoken words; no lower-third on the send line.
  { id: "cta2", startSec: 58.9 },
  // Loop-friendly ending: back onto the chart's flat-line 1% state.
  { id: "loop", startSec: 63.9 },
];

export const END_SEC = 64.4;

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
