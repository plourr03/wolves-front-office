import React from "react";
import { scaleLinear } from "d3";
import {
  COLORS,
  FONT,
  STAGE,
  HEIGHT,
  WIDTH,
  SCALE_MAX,
  LEAGUE_AVG,
  PICKUP_THRESHOLD,
  bucketKey,
  bucketColor,
} from "./config";
import { barGrow, ramp, shake, drawOn, pulse, rowSpotlight } from "./animation";
import { Beat, activeBeatIndex, SETUP_SEC, NAME_SEC } from "./timeline";

export type Row = { name: string; value: number; desc: string };

const CHART_TOP = STAGE.y + 150;
const CHART_BOTTOM = 1220;
const COUNT = 5;
const ROW_H = (CHART_BOTTOM - CHART_TOP) / COUNT;
const NAME_Y = 46;   // component name baseline, with room above the bar
const BAR_CY = 118;  // bar/track center within the row
const BAR_H = 60;
const TRACK_H = BAR_H + 14;
const VALUE_W = 150;

const BAR_X0 = STAGE.x;
const BAR_X1 = STAGE.x + STAGE.width - VALUE_W;
const VALUE_X = STAGE.x + STAGE.width;
const x = scaleLinear().domain([0, SCALE_MAX]).range([BAR_X0, BAR_X1]);

const slotTop = (i: number) => CHART_TOP + i * ROW_H;
const slotCy = (i: number) => slotTop(i) + BAR_CY;
export const rowCenterY = (i: number) => slotCy(i);

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const Fingerprint: React.FC<{
  frame: number;
  fps: number;
  beats: Beat[];
  data: Row[];
}> = ({ frame, fps, beats, data }) => {
  const furniture = ramp(frame, fps, SETUP_SEC + 0.1, 0.7);
  const zoneIn = ramp(frame, fps, 0.3, 0.6);
  const named = ramp(frame, fps, NAME_SEC, 0.5);

  const idx = activeBeatIndex(frame, beats);
  const cur = beats[idx];
  const annoRow = cur.scene === "fp" && typeof cur.view === "number" ? cur.view : null;
  const brightenAvg = !!cur.flags?.brightenAvg;
  const redPulse = cur.flags?.pulseRed ? pulse(frame, fps, cur.startSec, 1.0) : 0;

  return (
    <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", left: 0, top: 0 }}>
      {/* Pickup zone, present from the first frame. */}
      <g opacity={zoneIn}>
        <rect
          x={x(PICKUP_THRESHOLD)}
          y={CHART_TOP - 6}
          width={x(SCALE_MAX) - x(PICKUP_THRESHOLD)}
          height={CHART_BOTTOM - CHART_TOP + 6}
          fill={COLORS.error}
          fillOpacity={0.1}
        />
        <line
          x1={x(PICKUP_THRESHOLD)}
          x2={x(PICKUP_THRESHOLD)}
          y1={CHART_TOP - 6}
          y2={CHART_BOTTOM}
          stroke={COLORS.error}
          strokeWidth={2}
          strokeOpacity={0.45}
        />
        <text
          x={(x(PICKUP_THRESHOLD) + x(SCALE_MAX)) / 2}
          y={CHART_TOP - 22}
          textAnchor="middle"
          fill={COLORS.error}
          fontFamily={FONT.family}
          fontSize={FONT.tag}
          fontWeight={800}
          letterSpacing={2}
        >
          PICKUP ZONE
        </text>
      </g>

      {/* Title (morphs to the metric name) + scale endpoints + league line. */}
      <g opacity={furniture}>
        <rect x={STAGE.x} y={STAGE.y + 8} width={42} height={6} rx={3} fill={COLORS.text} />
        <text x={STAGE.x} y={STAGE.y + 52} fill={COLORS.text} fontFamily={FONT.family} fontSize={FONT.title} fontWeight={800} opacity={1 - named}>
          THE WOLVES' FINGERPRINT
        </text>
        <text x={STAGE.x} y={STAGE.y + 52} fill={COLORS.good} fontFamily={FONT.family} fontSize={FONT.title} fontWeight={800} opacity={named}>
          THE LA FITNESS INDEX
        </text>
        <text x={STAGE.x} y={STAGE.y + 92} fill={COLORS.subtext} fontFamily={FONT.family} fontSize={FONT.desc} fontWeight={500}>
          Every component scored 0 to 100, vs the NBA since 2014
        </text>
        {/* 0 and 100 scale endpoints */}
        <text x={BAR_X0} y={CHART_BOTTOM + 30} textAnchor="start" fill={COLORS.tertiary} fontFamily={FONT.mono} fontSize={22} fontWeight={700}>0</text>
        <text x={BAR_X1} y={CHART_BOTTOM + 30} textAnchor="end" fill={COLORS.tertiary} fontFamily={FONT.mono} fontSize={22} fontWeight={700}>100</text>
      </g>
      <g opacity={Math.max(furniture * 0.7, brightenAvg ? 1 : 0)}>
        <line
          x1={x(LEAGUE_AVG)}
          x2={x(LEAGUE_AVG)}
          y1={CHART_TOP - 6}
          y2={CHART_BOTTOM}
          stroke={brightenAvg ? COLORS.chalk : COLORS.subtext}
          strokeWidth={brightenAvg ? 3 : 2}
          strokeDasharray="2 9"
          strokeLinecap="round"
        />
        <text
          x={x(LEAGUE_AVG)}
          y={CHART_TOP - 22}
          textAnchor="middle"
          fill={brightenAvg ? COLORS.chalk : COLORS.subtext}
          fontFamily={FONT.family}
          fontSize={FONT.tag}
          fontWeight={700}
          letterSpacing={1.5}
        >
          LEAGUE AVG
        </text>
      </g>

      {/* Rows. Numbers animate on first (the intro), then the bars grow out. */}
      {data.map((d, i) => {
        const sp = rowSpotlight(frame, fps, beats, i);
        if (sp.opacity <= 0.001) return null;

        const cy = slotCy(i);
        // intro: the number counts up and rises into place, staggered.
        const numEnter = ramp(frame, fps, 0.6 + i * 0.5, 0.7);
        const labelEnter = ramp(frame, fps, 0.95 + i * 0.5, 0.6);
        const numTy = (1 - numEnter) * 16;
        const shown = Math.round(d.value * numEnter);

        const k = bucketKey(d.value);
        const color = bucketColor(d.value);
        const isRed = k === "error";
        const grow = barGrow(frame, fps, i, SETUP_SEC + 0.1);
        const w = (x(d.value) - x(0)) * grow;
        // a little snap as each red bar lands in the pickup zone
        const snap = isRed ? shake(frame, fps, SETUP_SEC + 0.6 + i * 0.12, 0.32, 6) : 0;
        const bright = isRed ? 1 + 0.5 * redPulse : 1;

        return (
          <g
            key={d.name}
            opacity={sp.opacity}
            style={sp.blur > 0.05 ? { filter: `blur(${sp.blur}px)` } : undefined}
          >
            <text
              x={STAGE.x}
              y={slotTop(i) + NAME_Y}
              fill={COLORS.text}
              fontFamily={FONT.family}
              fontSize={FONT.label}
              fontWeight={700}
              opacity={labelEnter}
            >
              {d.name}
            </text>

            <rect
              x={BAR_X0}
              y={cy - TRACK_H / 2}
              width={BAR_X1 - BAR_X0}
              height={TRACK_H}
              rx={TRACK_H / 2}
              fill={COLORS.inset}
              stroke={COLORS.insetEdge}
              strokeWidth={1}
              opacity={furniture}
            />
            <g transform={snap !== 0 ? `translate(${snap} 0)` : undefined}>
              <rect
                x={BAR_X0}
                y={cy - BAR_H / 2}
                width={w}
                height={BAR_H}
                rx={BAR_H / 2}
                fill={color}
                style={bright !== 1 ? { filter: `brightness(${bright})` } : undefined}
              />
              {w > BAR_H ? (
                <rect
                  x={BAR_X0 + 5}
                  y={cy - BAR_H / 2 + 4}
                  width={w - 10}
                  height={BAR_H * 0.28}
                  rx={BAR_H * 0.14}
                  fill="rgba(255,255,255,0.16)"
                />
              ) : null}
            </g>

            <text
              x={VALUE_X}
              y={cy + numTy}
              textAnchor="end"
              dominantBaseline="central"
              fill={color}
              fontFamily={FONT.mono}
              fontSize={FONT.value}
              fontWeight={800}
              opacity={numEnter}
            >
              {shown}
            </text>
          </g>
        );
      })}

      {/* Telestrator: a hand-marked circle around the number we're discussing. */}
      {annoRow !== null
        ? (() => {
            const p = drawOn(frame, fps, cur.startSec + 0.85, 0.7);
            if (p <= 0.001) return null;
            const cyA = slotCy(annoRow);
            const cxA = VALUE_X - 48;
            return (
              <g transform={`rotate(-7 ${cxA} ${cyA})`} opacity={Math.min(1, p * 1.3)}>
                <ellipse
                  cx={cxA}
                  cy={cyA}
                  rx={92}
                  ry={58}
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
