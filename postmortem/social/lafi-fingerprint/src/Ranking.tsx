import React from "react";
import { scaleLinear } from "d3";
import { COLORS, FONT, STAGE, WIDTH, HEIGHT } from "./config";
import { barGrow, ramp, drawOn } from "./animation";
import { Beat, activeBeatIndex, RANK_CUT_SEC } from "./timeline";

// The closing league ranking on Sharp LAFI, 2025-26 regular season. Real values
// from outputs/tables/q0a_lafi/lafi_composite_5component.csv (rounded). The
// Wolves sit 3rd, behind Philadelphia and the Clippers.
const RANKING = [
  { team: "76ERS", value: 93 },
  { team: "CLIPPERS", value: 92 },
  { team: "WOLVES", value: 90, me: true },
  { team: "ROCKETS", value: 84 },
  { team: "WIZARDS", value: 84 },
  { team: "SUNS", value: 82 },
  { team: "BUCKS", value: 78 },
  { team: "CELTICS", value: 77 },
];
const ME = RANKING.findIndex((r) => r.me);

const RANK_TOP = STAGE.y + 104;
const RANK_BOTTOM = 1250;
const ROW_H = (RANK_BOTTOM - RANK_TOP) / RANKING.length;
const LABEL_W = 250;
const VALUE_W = 120;
const BAR_X0 = STAGE.x + LABEL_W;
const BAR_X1 = STAGE.x + STAGE.width - VALUE_W;
const VALUE_X = STAGE.x + STAGE.width;
// Scale starts at 40 so the spread is legible. Bars are measured from BAR_X0
// (the visual zero of the axis), NOT from x(0), which lies far off-screen.
const x = scaleLinear().domain([40, 100]).range([BAR_X0, BAR_X1]);

export const Ranking: React.FC<{
  frame: number;
  fps: number;
  beats: Beat[];
}> = ({ frame, fps, beats }) => {
  const intro = ramp(frame, fps, RANK_CUT_SEC, 0.5);
  const emphasis = ramp(frame, fps, RANK_CUT_SEC + 2.4, 0.7);

  // During the outro title beats the ranking recedes behind the title card.
  const idx = activeBeatIndex(frame, beats);
  const cur = beats[idx];
  const firstRank = beats.find((b) => b.scene === "rank");
  const titleBeat = cur.scene === "rank" && cur !== firstRank;
  const dim = titleBeat ? 0.22 : 1;

  return (
    <svg
      width={WIDTH}
      height={HEIGHT}
      style={{ position: "absolute", left: 0, top: 0, opacity: intro * dim }}
    >
      {/* header */}
      <g>
        <rect x={STAGE.x} y={STAGE.y + 8} width={42} height={6} rx={3} fill={COLORS.good} />
        <text
          x={STAGE.x}
          y={STAGE.y + 52}
          fill={COLORS.text}
          fontFamily={FONT.family}
          fontSize={FONT.title}
          fontWeight={800}
        >
          SHARP LAFI, LEAGUE RANK
        </text>
        <text
          x={STAGE.x}
          y={STAGE.y + 92}
          fill={COLORS.subtext}
          fontFamily={FONT.family}
          fontSize={FONT.desc}
          fontWeight={500}
        >
          The 3 playoff-predictive components, scored 0 to 100
        </text>
      </g>

      {RANKING.map((r, i) => {
        const me = !!r.me;
        const grow = barGrow(frame, fps, i, RANK_CUT_SEC + 0.2);
        const w = (x(r.value) - BAR_X0) * grow;
        const cy = RANK_TOP + i * ROW_H + ROW_H / 2;
        const barH = Math.min(48, ROW_H * 0.5);
        // others recede as the camera "zooms" to the Wolves
        const rowOp = me ? 1 : 1 - 0.62 * emphasis;
        const color = me ? COLORS.good : "rgba(255,255,255,0.26)";

        return (
          <g key={r.team} opacity={rowOp}>
            <text
              x={STAGE.x}
              y={cy}
              dominantBaseline="central"
              fill={me ? COLORS.good : COLORS.tertiary}
              fontFamily={FONT.mono}
              fontSize={34}
              fontWeight={800}
            >
              {i + 1}
            </text>
            <text
              x={STAGE.x + 60}
              y={cy}
              dominantBaseline="central"
              fill={me ? COLORS.text : COLORS.subtext}
              fontFamily={FONT.family}
              fontSize={34}
              fontWeight={me ? 800 : 600}
            >
              {r.team}
            </text>
            <rect
              x={BAR_X0}
              y={cy - (barH + 8) / 2}
              width={BAR_X1 - BAR_X0}
              height={barH + 8}
              rx={(barH + 8) / 2}
              fill={COLORS.inset}
              stroke={COLORS.insetEdge}
              strokeWidth={1}
            />
            <rect
              x={BAR_X0}
              y={cy - barH / 2}
              width={w}
              height={barH}
              rx={barH / 2}
              fill={color}
            />
            <text
              x={VALUE_X}
              y={cy}
              textAnchor="end"
              dominantBaseline="central"
              fill={me ? COLORS.good : COLORS.tertiary}
              fontFamily={FONT.mono}
              fontSize={40}
              fontWeight={800}
            >
              {Math.round(r.value * grow)}
            </text>
          </g>
        );
      })}

      {/* Telestrator circle around the Wolves' number as the others recede. */}
      {(() => {
        const p = drawOn(frame, fps, RANK_CUT_SEC + 2.4, 0.7);
        if (p <= 0.001) return null;
        const cyA = RANK_TOP + ME * ROW_H + ROW_H / 2;
        const cxA = VALUE_X - 30;
        return (
          <g transform={`rotate(-7 ${cxA} ${cyA})`} opacity={Math.min(1, p * 1.3)}>
            <ellipse
              cx={cxA}
              cy={cyA}
              rx={72}
              ry={46}
              fill="none"
              stroke={COLORS.chalk}
              strokeWidth={4.5}
              strokeLinecap="round"
              pathLength={1}
              strokeDasharray={1}
              strokeDashoffset={1 - p}
            />
          </g>
        );
      })()}
    </svg>
  );
};
