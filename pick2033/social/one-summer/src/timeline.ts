import { FPS } from "./config";

// The One Summer reel, ninth cut: Bobby's line notes. Faster intro split into
// two clips with a real half-second breath before the contract line, "But
// we're not worried about this year." restored, his 44 / keep-pace / bad-year
// wordings, "two guys on max contracts," and a global 1.05x tempo lift baked
// into every clip (atempo before probing, so these starts match the audio).
// Runs 70.5s.
//
// When re-timing, run scripts/make_ai_vo.py and paste its printed starts.

export type BeatId =
  | "curve1"
  | "curve1t"
  | "curve1b"
  | "curve2"
  | "curve2s"
  | "curve2s2"
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
  { id: "curve1", startSec: 0.0, caption: "Anthony Edwards' odds of leaving\nMinnesota this year are about 1%." },
  { id: "curve1t", startSec: 5.6, caption: "With two years left on his contract." },
  { id: "curve1b", startSec: 8.0, caption: "But we're not worried about this year." },
  { id: "curve2", startSec: 10.3, caption: "However, his 2029 walk year has him at\nabout a 44% chance of leaving." },
  { id: "curve2s", startSec: 17.1, caption: "And that assumes the Wolves keep pace" },
  // caption-only page inside the same clip
  { id: "curve2s2", startSec: 19.6, caption: "with how they've been doing\nthis past year." },
  { id: "curve2b", startSec: 22.3, caption: "Let's say the Wolves have a bad year\nand win just 37 games." },
  // caption-only page inside the same clip
  { id: "curve2b2", startSec: 27.6, caption: "The odds jump to as high as a 66%\nchance of him leaving." },
  { id: "curve3", startSec: 33.7, caption: "And this is based on forty years\nof data, not a gut feeling." },
  { id: "h1", startSec: 37.9, caption: "The whole LaMelo trade\ncomes down to that one summer." },
  { id: "unsig", startSec: 41.3, caption: "Not only that, but LaMelo's deal\nends the same July." },
  { id: "unsig2", startSec: 44.9, caption: "And we still have not extended him." },
  { id: "twomax", startSec: 47.2, caption: "So, we have two guys on max contracts." },
  { id: "twomaxb", startSec: 50.6, caption: "One summer that the next decade of\nbasketball in Minnesota hinges on." },
  { id: "twomax2", startSec: 55.8, caption: "The Wolves and Hornets both made" },
  { id: "twomax2b", startSec: 58.6, caption: "opposing bets on where\nthat summer will land." },
  { id: "cta1", startSec: 62.1, caption: "What are the most likely futures\nfor that summer?" },
  // The CTA card carries the spoken words; no lower-third on the send line.
  { id: "cta2", startSec: 65.3 },
  // Loop-friendly ending: back onto the chart's flat-line 1% state.
  { id: "loop", startSec: 70.0 },
];

export const END_SEC = 70.5;

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
