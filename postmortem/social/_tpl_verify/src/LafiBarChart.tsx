import React from "react";
import { scaleLinear } from "d3";
import { COLORS, FONT, STAGE, WIDTH, HEIGHT } from "./config";
import { barGrow, rowSpotlight, drawOn } from "./animation";
import { Beat, activeBeatIndex, focusRows } from "./timeline";

// =============================================================================
// THIS IS THE PART YOU SWAP OUT.
//
// Drop your real D3 chart in here. Keep the pieces that define WHAT it looks like
// (scaleLinear / scaleBand, axes, line/area generators, color encodings, data
// shaping). Delete the parts that ANIMATE (.transition(), .duration(), .ease())
// and drive motion off the frame instead. Render marks as React/SVG elements.
//
// The sample is a horizontal ranking. It shows the three moves you will reuse on
// almost any chart: a frame-driven DRAW (bars grow), a SPOTLIGHT (dim + blur the
// rows the script is not on), and a TELESTRATOR mark (a hand-drawn circle on the
// number you are discussing).
// =============================================================================

export type Row = { team: string; value: number };

const LABEL_W = 250;
const VALUE_W = 130;
const BAR_X0 = STAGE.x + LABEL_W;
const BAR_X1 = STAGE.x + STAGE.width - VALUE_W;
const VALUE_X = STAGE.x + STAGE.width;

const rowH = (count: number) => STAGE.height / count;
const rowCy = (i: number, count: number) => STAGE.y + i * rowH(count) + rowH(count) / 2;

export const LafiBarChart: React.FC<{
  frame: number;
  fps: number;
  data: Row[];
  beats: Beat[];
  highlightIndex: number;
  growDelaySec?: number;
}> = ({ frame, fps, data, beats, highlightIndex, growDelaySec = 0 }) => {
  const count = data.length;
  const maxValue = Math.max(...data.map((d) => d.value));
  // NOTE: measure bar width from BAR_X0 (the axis start), not x(value) - x(0).
  // If your domain does not start at 0, x(0) is extrapolated off-canvas and the
  // bar runs off the screen.
  const x = scaleLinear().domain([0, maxValue]).range([BAR_X0, BAR_X1]);

  const cur = beats[activeBeatIndex(frame, beats)];
  const focus = focusRows(cur);
  const annoRow = focus && focus.length === 1 ? focus[0] : null;
  const barH = Math.min(64, rowH(count) * 0.4);

  return (
    <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", left: 0, top: 0 }}>
      {data.map((d, i) => {
        const featured = i === highlightIndex;
        const sp = rowSpotlight(frame, fps, beats, i);
        const grow = barGrow(frame, fps, i, growDelaySec);
        const w = (x(d.value) - BAR_X0) * grow;
        const cy = rowCy(i, count);
        const color = featured ? COLORS.highlight : COLORS.dim;

        return (
          <g
            key={d.team}
            opacity={sp.opacity}
            style={sp.blur > 0.05 ? { filter: `blur(${sp.blur}px)` } : undefined}
          >
            <text
              x={BAR_X0 - 22}
              y={cy}
              textAnchor="end"
              dominantBaseline="central"
              fill={featured ? COLORS.text : COLORS.subtext}
              fontFamily={FONT.family}
              fontSize={FONT.label}
              fontWeight={featured ? 800 : 600}
            >
              {d.team}
            </text>
            <rect
              x={BAR_X0}
              y={cy - (barH + 10) / 2}
              width={BAR_X1 - BAR_X0}
              height={barH + 10}
              rx={(barH + 10) / 2}
              fill={COLORS.inset}
              stroke={COLORS.insetEdge}
              strokeWidth={1}
            />
            <rect x={BAR_X0} y={cy - barH / 2} width={w} height={barH} rx={barH / 2} fill={color} />
            <text
              x={VALUE_X}
              y={cy}
              textAnchor="end"
              dominantBaseline="central"
              fill={featured ? COLORS.highlight : COLORS.tertiary}
              fontFamily={FONT.mono}
              fontSize={FONT.value}
              fontWeight={800}
              opacity={grow}
            >
              {Math.round(d.value * grow)}
            </text>
          </g>
        );
      })}

      {/* Telestrator: a hand-marked circle around the number we are discussing. */}
      {annoRow !== null
        ? (() => {
            const p = drawOn(frame, fps, cur.startSec + 0.85, 0.7);
            if (p <= 0.001) return null;
            const cyA = rowCy(annoRow, count);
            const cxA = VALUE_X - 42;
            return (
              <g transform={`rotate(-7 ${cxA} ${cyA})`} opacity={Math.min(1, p * 1.3)}>
                <ellipse
                  cx={cxA}
                  cy={cyA}
                  rx={80}
                  ry={52}
                  fill="none"
                  stroke={COLORS.chalk}
                  strokeWidth={5}
                  strokeLinecap="round"
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={1 - p}
                />
              </g>
            );
          })()
        : null}
    </svg>
  );
};
