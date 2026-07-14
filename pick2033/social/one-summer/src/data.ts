// Every on-screen number, verified against the FINAL exports on 2026-07-14
// before render (QA gate 1 of the render brief). Nothing here is eyeballed.
// If an export and this file ever disagree, the export wins and the render
// stops until the discrepancy is flagged.

// 2025-26 actual win total; cross-checked against the Part 1 article text
// ("the one that just won 49 games").
export const WINS_2526 = 49;

// slot_distribution_2033_FINAL.json: p_lottery = 0.61928 under the post-2026
// reform (16 drawn picks). Spoken as 62 percent; footnoted as 61.9.
export const LOTTERY_PCT_LABEL = "61.9";

// Session log s_final_run_0712.md, from the hazard_m2_full posterior:
// "Walk-year odds multiple ~70x [43x, 104x] (0 vs 2 years remaining)".
// Printed in Part 1 as "roughly seventy times (80% interval: 43x to 104x)".
export const WALK_MULT = "70";
export const WALK_MULT_INTERVAL = "80% INTERVAL: 43X TO 104X";

// edwards_hazard_FINAL.json, scenarios.central_win60.annual (hazard_mean).
// The winning-team (.600) scenario, exact export floats.
export const HAZARD: { season: number; h: number }[] = [
  { season: 2027, h: 0.00763666556107613 },
  { season: 2028, h: 0.0734374845592244 },
  { season: 2029, h: 0.4401955105028574 },
  { season: 2030, h: 0.00027908650713407947 },
  { season: 2031, h: 0.0024032468004610355 },
  { season: 2032, h: 0.01999080331843552 },
  { season: 2033, h: 0.14365940005538272 },
];

// 2029 walk-year spike interval, same export (lo80 0.349, hi80 0.533).
// Printed in Part 1 as "(80% interval: 35 to 53)".
export const SPIKE_LO = 0.3490510891651707;
export const SPIKE_HI = 0.5332502045000675;

// "1 percent with two years left": Part 1's counterfactual (Edwards' 2029
// profile run with two years remaining reads about 1 percent), and the 2027
// point on the curve (two years remaining, hazard 0.0076) rounds to 1.
export const TWO_YEARS_LEFT_LABEL = "1%";
export const SPIKE_LABEL = "44%";

// Engine D FINAL run: 50,000 paths (freeze 50f9b7bc5b19835b, seed 20330706).
export const PATHS = 50000;

// total_asset_cost.json, runs.top1_true, picks_swaps_total means:
// delivered_to_CHA 8.27 -> 8.3, forgone_by_MIN 4.51 -> 4.5 (cumulative title
// equity, percentage points, headline package). Printed in Part 3 as 8.3 / 4.5.
export const EQUITY_CHA = "8.3";
export const EQUITY_MIN = "4.5";
