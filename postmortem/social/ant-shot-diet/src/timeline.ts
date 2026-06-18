import { FPS } from "./config";

// The script. One story told as three full-screen ACTS, book-ended by cards.
// Each act is a single giant before/after number bound to one bar by a shared
// frame-ramp, so the number and the bar always finish on the same frame.
//
// EVERY on-screen number is validated against the warehouse and logged in
// provenance.json (claim id in brackets). The deltas are exact arithmetic on the
// validated before/after values. Captions are kept descriptive and matched to
// the magnitude so they never claim more than the data shows.
//
// Units name the metric TYPE in plain words ("were threes" = a share of attempts,
// "went in" = a make rate) so the giant percent can't be misread as a shooting %.

export const secToFrame = (sec: number): number => Math.round(sec * FPS);

export type Mark = "slash" | "lasso" | "bracket";

export type ActSpec = {
  id: string;
  startSec: number;
  morphSec: number;
  endSec: number;
  kicker: string;
  unit: string;
  before: number;
  after: number;
  decimals: number;
  delta: string; // exact magnitude of the move, derived from before/after
  barMax: number; // bar scale domain (percent), tuned so the move reads honestly
  grow: boolean;
  twist: boolean; // Act 3: tease red, then refuse it
  mark: Mark;
  scrawl: string;
  revealCaption: string;
  morphCaption: string;
};

export const MORPH_DUR = 1.1;

export const ACTS: ActSpec[] = [
  {
    id: "arc",
    startSec: 5.6,
    morphSec: 9.0,
    endSec: 12.8,
    kicker: "WHAT THEY TOOK",
    unit: "of his attempts were threes",
    before: 42, // [rs_3pa_rate]
    after: 28, //  [sas_3pa_rate]
    decimals: 0,
    delta: "14 pts fewer",
    barMax: 48,
    grow: false,
    twist: false,
    mark: "slash",
    scrawl: "took",
    revealCaption: "The three was his go-to look.",
    morphCaption: "San Antonio pushed him off the line.",
  },
  {
    id: "floater",
    startSec: 12.8,
    morphSec: 15.0,
    endSec: 20.0,
    kicker: "WHERE THEY PUT HIM",
    unit: "of his attempts came from 11-16 ft",
    before: 15, // [rs_floater_share]
    after: 21, //  [sas_floater_share]
    decimals: 0,
    delta: "6 pts more",
    barMax: 48,
    grow: true,
    twist: false,
    mark: "lasso",
    scrawl: "moved",
    revealCaption: "They walled off the arc,",
    morphCaption: "and funneled him to where the bigs wait.",
  },
  {
    id: "fg",
    startSec: 20.0,
    morphSec: 21.3,
    endSec: 24.0,
    kicker: "AND YET",
    unit: "of his shots went in  ·  field goal %",
    before: 48.9, // [rs_fg_pct]
    after: 46.9, //  [sas_fg_pct]
    decimals: 1,
    delta: "2.0 pts lower",
    barMax: 60,
    grow: false,
    twist: true,
    mark: "bracket",
    scrawl: "barely",
    revealCaption: "His shot diet was wrecked.",
    morphCaption: "And yet his make rate barely moved.",
  },
];

export type CardSpec = { startSec: number; endSec: number; text: string; underline?: boolean };

export const HOOK: CardSpec[] = [
  { startSec: 0.0, endSec: 3.0, text: "San Antonio didn't beat Ant's shot." },
  { startSec: 3.0, endSec: 5.6, text: "They moved it.", underline: true },
];
export const PAYOFF_SEC = 24.0;
export const SIGNOFF_SEC = 27.0;
export const PAYOFF: CardSpec = { startSec: PAYOFF_SEC, endSec: SIGNOFF_SEC, text: "They changed the shape. Not the shooter." };
export const SIGNOFF: CardSpec = { startSec: SIGNOFF_SEC, endSec: 99, text: "More at Wolves to a T.", underline: true };

// The playoff comparison rests on a 6-game series; disclose it on screen the
// whole time the "after" numbers are up.
export const DISCLOSURE_PRE = "REG. SEASON 61 GP";
export const DISCLOSURE_POST = "ROUND 2 vs SAS 6 GP";

const TAIL_SEC = 2.6;
export const DURATION_IN_FRAMES = secToFrame(SIGNOFF_SEC + TAIL_SEC);
