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
  | "h44"
  | "h44b"
  | "h1"
  | "y2029"
  | "y2029b"
  | "curve1"
  | "curve1c"
  | "curve1b"
  | "curve2"
  | "curve2s"
  | "curve2b"
  | "curve2c"
  | "curve3"
  | "unsig"
  | "unsig2"
  | "twomax"
  | "twomaxb"
  | "twomax2"
  | "cta1"
  | "cta2"
  | "loop";

export type Beat = {
  id: BeatId;
  startSec: number;
  caption?: string;
};

export const BEATS: Beat[] = [
  { id: "h44", startSec: 0.0, caption: "The odds of Ant leaving the Minnesota\nTimberwolves in his 2029 walk year" },
  { id: "h44b", startSec: 5.3, caption: "sit somewhere near 44%." },
  { id: "h1", startSec: 9.0, caption: "The whole LaMelo trade\ncomes down to that one summer." },
  { id: "y2029", startSec: 12.5, caption: "2029. Ant's walk year." },
  { id: "y2029b", startSec: 14.8, caption: "And history is not kind to teams\nwith stars on walk years." },
  { id: "curve1", startSec: 19.9, caption: "Ant has two years left on his contract." },
  { id: "curve1c", startSec: 22.5, caption: "And his odds of leaving this year?\nOnly about 1 percent." },
  { id: "curve1b", startSec: 26.2, caption: "But we're not worried about this year." },
  { id: "curve2", startSec: 28.8, caption: "In the walk year, the odds of Ant\nleaving skyrocket to 44 percent." },
  { id: "curve2s", startSec: 34.9, caption: "And that's if the Wolves keep winning\nat the clip they have been." },
  { id: "curve2b", startSec: 39.8, caption: "Let's say the Wolves have a bad year\nand win at just a 37-win pace?" },
  { id: "curve2c", startSec: 45.1, caption: "The odds of him leaving jump to 56." },
  { id: "curve3", startSec: 48.7, caption: "And this is based on forty years\nof data, not a gut feeling." },
  { id: "unsig", startSec: 54.3, caption: "Not only that, but LaMelo's deal\nends the same July." },
  { id: "unsig2", startSec: 58.2, caption: "And we still have not extended him." },
  { id: "twomax", startSec: 61.0, caption: "So, we have two max guys." },
  { id: "twomaxb", startSec: 63.7, caption: "One summer that the next decade of\nbasketball in Minnesota hinges on." },
  { id: "twomax2", startSec: 69.2, caption: "The Wolves and Charlotte both making\nopposite bets on that summer." },
  { id: "cta1", startSec: 75.3, caption: "What are the most likely futures\nfor that summer?" },
  // The CTA card carries the spoken words; no lower-third on the send line.
  { id: "cta2", startSec: 78.8 },
  // Loop-friendly ending: back onto the 44 card, so a rewatch reads as intentional.
  { id: "loop", startSec: 84.4 },
];

export const END_SEC = 84.9;

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
