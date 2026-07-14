import { FPS } from "./config";

// The One Summer reel, fifth cut: Bobby's sheet edits incorporated. The hook
// leads with his wording, B4 grows into a four-moment chart act (1% setup,
// the pivot, the 44 payoff, the declining-team 56), and the stamp now says
// NO EXTENSION to match "Still not extended." Runs about 62s, a true deep cut.
//
// The VO script (Bobby records verbatim; captions match it):
//   B1  "The odds of Ant leaving in his 2029 walk year are somewhere around
//        44 percent."
//   B2  "The whole LaMelo trade comes down to that one summer."
//   B3  "2029. Ant's walk year. And history is blunt about walk years."
//   B4  "With two years left on his deal, his odds of leaving this year are
//        near 1 percent. But that isn't what we're worried about. [beat]
//        In the walk year, however? 44. And that's with the team winning.
//        [beat] On a 37-win pace? It jumps to 56. [beat] That cliff is forty
//        years of stars, not a hot take."
//        (44 and 1 ride the same .600 path; the clock is the variable. The 56
//        is the published decline_win45 walk-year spike from the same export,
//        and .450 x 82 = 36.9, spoken as a 37-win pace.)
//   B5  "And LaMelo's deal ends the same July. Still not extended."
//        (plus the insurance take without "Still not extended.")
//   B6  "Two max guys. One summer. The Wolves and Charlotte both making
//        opposite bets on that summer."  (Bobby's line)
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
  | "curve1b"
  | "curve2"
  | "curve2b"
  | "curve3"
  | "unsig"
  | "twomax"
  | "twomax2"
  | "cta"
  | "loop";

export type Beat = {
  id: BeatId;
  startSec: number;
  caption?: string;
};

export const BEATS: Beat[] = [
  { id: "h44", startSec: 0.0, caption: "The odds of Ant leaving in his 2029\nwalk year are somewhere around 44%." },
  { id: "h1", startSec: 5.9, caption: "The whole LaMelo trade\ncomes down to that one summer." },
  { id: "y2029", startSec: 9.2, caption: "2029. Ant's walk year.\nAnd history is blunt about walk years." },
  {
    id: "curve1",
    startSec: 14.6,
    caption: "With two years left on his deal, his\nodds of leaving this year are near 1%.",
  },
  { id: "curve1b", startSec: 19.8, caption: "But that isn't what\nwe're worried about." },
  { id: "curve2", startSec: 21.9, caption: "In the walk year, however? 44.\nAnd that's with the team winning." },
  { id: "curve2b", startSec: 28.0, caption: "On a 37-win pace?\nIt jumps to 56." },
  { id: "curve3", startSec: 31.3, caption: "That cliff is forty years of stars,\nnot a hot take." },
  { id: "unsig", startSec: 35.2, caption: "And LaMelo's deal ends the same July.\nStill not extended." },
  { id: "twomax", startSec: 39.1, caption: "Two max guys. One summer." },
  {
    id: "twomax2",
    startSec: 41.3,
    caption: "The Wolves and Charlotte both\nmaking opposite bets on that summer.",
  },
  // The CTA card carries the spoken words itself; no lower-third on top of it.
  { id: "cta", startSec: 45.7 },
  // Loop-friendly ending: back onto the 44 card, so a rewatch reads as intentional.
  { id: "loop", startSec: 53.4 },
];

export const END_SEC = 53.9;

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
