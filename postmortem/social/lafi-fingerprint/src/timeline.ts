import { FPS } from "./config";

// The full cut, beat by beat, lined up with the spoken script. Every metric
// gets a real hold. The LA Fitness Index gets named while all five components
// are still on screen, before we narrow to the three that predict playoff
// offense and cut to the league ranking.
//
// scene   "fp"   = the offensive fingerprint chart
//         "rank" = the closing league-ranking chart
// view    "hero"   = the opening, where the five numbers animate on
//         "whole"  = the full fingerprint, camera pulled back
//         "filter" = the full fingerprint with the two non-predictive bars gone
//         0..4     = push the camera to that one row and hold
// screen  the on-screen caption
// index   "01".."05" chapter number on the metric-walk beats
// flags   per-beat one-offs

export type Scene = "fp" | "rank";
export type View = "hero" | "whole" | "filter" | number;

export type Beat = {
  startSec: number;
  scene: Scene;
  view: View;
  screen: string;
  index?: string;
  flags?: {
    pulseRed?: boolean;
    brightenAvg?: boolean;
    nameMetric?: boolean;
    cta?: boolean;
  };
};

export const secToFrame = (sec: number): number => Math.round(sec * FPS);

export const activeBeatIndex = (frame: number, beats: Beat[]): number => {
  let idx = 0;
  for (let i = 0; i < beats.length; i++) {
    if (frame >= secToFrame(beats[i].startSec)) idx = i;
  }
  return idx;
};

export const secondsIntoBeat = (frame: number, beat: Beat): number =>
  Math.max(0, frame / FPS - beat.startSec);

export const focusRows = (view: View): number[] | null => {
  if (typeof view === "number") return [view];
  if (view === "filter") return [0, 1, 2];
  return null;
};

export const BEATS: Beat[] = [
  // 0:00 HOOK. The five percentile numbers animate onto the screen.
  { startSec: 0.0, scene: "fp", view: "hero", screen: "Hard to watch" },
  // 0:05 SETUP. The bars grow out to the numbers; the chart finishes assembling.
  { startSec: 5.0, scene: "fp", view: "whole", screen: "Five offensive fingerprints" },
  // 0:13 - 0:51 THE WALK. One component at a time, with a hold and a mark.
  { startSec: 13.0, scene: "fp", view: 0, index: "01", screen: "Isolation reliance: 90" },
  { startSec: 23.0, scene: "fp", view: 1, index: "02", screen: "Shot quality decay: 83" },
  { startSec: 32.0, scene: "fp", view: 2, index: "03", screen: "Motion death: 72" },
  { startSec: 41.0, scene: "fp", view: 3, index: "04", screen: "The playbook was fine", flags: { brightenAvg: true } },
  { startSec: 51.0, scene: "fp", view: 4, index: "05", screen: "The ball moved" },
  // 0:59 NAME THE PATTERN.
  { startSec: 59.0, scene: "fp", view: "whole", screen: "Distributed pickup", flags: { pulseRed: true } },
  // 1:09 NAME THE METRIC, while all five are still on screen.
  { startSec: 69.0, scene: "fp", view: "whole", screen: "I call it the LA Fitness Index", flags: { nameMetric: true } },
  // 1:19 NARROW to the three that predict playoff offense.
  { startSec: 79.0, scene: "fp", view: "filter", screen: "The 3 that predict playoff offense" },
  // 1:28 THE RANK. Cut to the league ranking; the Wolves sit 3rd.
  { startSec: 88.0, scene: "rank", view: "whole", screen: "3rd-most in the NBA" },
  // 1:36 CLOSE.
  { startSec: 96.0, scene: "rank", view: "whole", screen: "Wolves to a T  ·  link in bio", flags: { cta: true } },
];

const TAIL_SEC = 2.5;

export const SETUP_SEC = BEATS[1].startSec;
export const NAME_SEC = BEATS.find((b) => b.flags?.nameMetric)!.startSec;
export const RANK_CUT_SEC = BEATS.find((b) => b.scene === "rank")!.startSec;

export const DURATION_IN_FRAMES = secToFrame(
  BEATS[BEATS.length - 1].startSec + TAIL_SEC
);
