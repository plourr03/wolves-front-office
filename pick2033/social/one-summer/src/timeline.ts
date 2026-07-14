import { FPS } from "./config";

// The One Summer reel, sixth cut: Bobby's rewritten script (from the posting
// kit), voiced by the "upbeat bob" clone and re-timed to its actual read
// (this voice reads slow; 84.9s total). Grammar normalized; flagged fixes:
// "honestly" dropped (house banned word), "this summer" -> "that summer",
// "similar clip then they have been" -> "the clip they have been."
//
// Captions match the spoken words verbatim; long sentences page across
// multiple beats. h44b is a caption-only page inside the hook clip.
//
// When re-timing, run scripts/make_ai_vo.py and paste its printed starts.

export type BeatId =
  | "curve1"
  | "curve1c"
  | "curve1b"
  | "curve2"
  | "curve2r"
  | "curve2s"
  | "curve2b"
  | "curve2c"
  | "curve3"
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
  { id: "curve1", startSec: 0.0, caption: "Anthony Edwards has two years left on\nhis contract with Minnesota." },
  { id: "curve1c", startSec: 4.2, caption: "The odds he leaves this year?\nOnly around 1 percent." },
  { id: "curve1b", startSec: 9.4, caption: "But we're not worried about this year." },
  { id: "curve2", startSec: 12.0, caption: "In the walk year, the odds of Ant\nleaving skyrocket to 44 percent." },
  { id: "curve2r", startSec: 17.8, caption: "Really, it's anywhere\nbetween 35 and 53 percent." },
  { id: "curve2s", startSec: 23.2, caption: "And that's if the Wolves keep winning\nat the clip they have been." },
  { id: "curve2b", startSec: 28.1, caption: "Let's say the Wolves have a bad year\nand win at just a 37-win pace?" },
  { id: "curve2c", startSec: 33.4, caption: "The odds of him leaving jump to 56." },
  { id: "curve3", startSec: 37.0, caption: "And this is based on forty years\nof data, not a gut feeling." },
  { id: "unsig", startSec: 42.6, caption: "Not only that, but LaMelo's deal\nends the same July." },
  { id: "unsig2", startSec: 46.5, caption: "And we still have not extended him." },
  { id: "twomax", startSec: 49.1, caption: "So, we have two max guys." },
  { id: "twomaxb", startSec: 51.8, caption: "One summer that the next decade of\nbasketball in Minnesota hinges on." },
  { id: "twomax2", startSec: 57.3, caption: "The Wolves and Hornets both made" },
  { id: "twomax2b", startSec: 60.2, caption: "opposing bets on where\nthat summer will land." },
  { id: "cta1", startSec: 64.1, caption: "What are the most likely futures\nfor that summer?" },
  { id: "cta2", startSec: 67.6 },
  { id: "loop", startSec: 73.2 },
];

export const END_SEC = 73.7;

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
