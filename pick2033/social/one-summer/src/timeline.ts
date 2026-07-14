import { FPS } from "./config";

// The One Summer reel, third cut: cold-open on the biggest number (the 44),
// then spend the runtime earning it, and loop back onto it. One point, told
// slow, in the verdict-carousel look. Chrome is just the wordmark now; no
// date, no series label, no chapter chips.
//
// The VO script (Bobby records verbatim; captions match it, ~95 words):
//   B1  "44 percent. Those are Ant's odds of leaving in the 2029 walk year."
//   B2  "The whole LaMelo trade comes down to that one summer."
//   B3  "2029. Ant's walk year. History is blunt about walk years."
//   B4  "With two years left on his deal, his odds of leaving sit near
//        1 percent. In the walk year? 44. That cliff is forty years of stars,
//        not a hot take."
//        (Both numbers ride the same .600 winning path; the contract clock is
//        the only variable. That IS the Part 1 thesis; the VO must not imply
//        winning is what moves it.)
//   B5  "And LaMelo's deal ends the same July. Still unsigned."
//   B6  "Two max guys. One summer. That is the bet Charlotte made."
//   B7  "We priced all of it across fifty thousand futures. Comment BILL and
//        I'll send you Part 1."
//
// When the recorded VO lands in public/voiceover.mp3, re-time by editing the
// start seconds below only; every scene keys off these constants.

export type BeatId =
  | "h44"
  | "h1"
  | "y2029"
  | "curve1"
  | "curve2"
  | "curve3"
  | "unsig"
  | "twomax"
  | "cta"
  | "loop";

export type Beat = {
  id: BeatId;
  startSec: number;
  caption?: string;
};

export const BEATS: Beat[] = [
  { id: "h44", startSec: 0.0, caption: "44%. Those are Ant's odds of\nleaving in the 2029 walk year." },
  { id: "h1", startSec: 3.4, caption: "The whole LaMelo trade\ncomes down to that one summer." },
  { id: "y2029", startSec: 7.2, caption: "2029. Ant's walk year.\nHistory is blunt about walk years." },
  {
    id: "curve1",
    startSec: 11.8,
    caption: "With two years left on his deal,\nhis odds of leaving sit near 1 percent.",
  },
  { id: "curve2", startSec: 16.2, caption: "In the walk year? 44." },
  { id: "curve3", startSec: 19.2, caption: "That cliff is forty years of stars,\nnot a hot take." },
  { id: "unsig", startSec: 23.8, caption: "And LaMelo's deal ends the same July.\nStill unsigned." },
  { id: "twomax", startSec: 29.2, caption: "Two max guys. One summer.\nThat is the bet Charlotte made." },
  // The CTA card carries the spoken words itself; no lower-third on top of it.
  { id: "cta", startSec: 33.8 },
  // Loop-friendly ending: back onto the 44 card, so a rewatch reads as intentional.
  { id: "loop", startSec: 39.6 },
];

export const END_SEC = 40.1;

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
