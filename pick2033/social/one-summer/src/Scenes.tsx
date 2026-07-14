import React from "react";
import { AbsoluteFill } from "remotion";
import { COLORS, FONT, RADIUS, SAFE } from "./config";
import { T } from "./timeline";
import { drawOn, ramp, riseIn, shake, stampIn } from "./animation";
import { HAZARD, SPIKE_HI, SPIKE_LO } from "./data";

// One hero visual per beat, statement lines, real holds. Every scene is a pure
// function of the frame; motion happens at the top of a beat, then stillness.

type SceneProps = { frame: number; fps: number };

// Left-aligned content column (the slides' grammar), vertically centered in the
// band between the masthead and the caption zone.
const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill
    style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "flex-start",
      justifyContent: "center",
      paddingTop: 280,
      paddingBottom: 600,
      paddingLeft: SAFE.x,
      paddingRight: SAFE.x,
    }}
  >
    {children}
  </AbsoluteFill>
);

const kickerStyle: React.CSSProperties = {
  fontFamily: FONT.mono,
  fontSize: FONT.kicker,
  fontWeight: 700,
  letterSpacing: 4,
  color: COLORS.mute,
  textTransform: "uppercase",
};

const statementStyle: React.CSSProperties = {
  fontFamily: FONT.display,
  fontWeight: 700,
  fontSize: FONT.statement,
  lineHeight: 1.06,
  color: COLORS.text,
};

const subStyle: React.CSSProperties = {
  fontFamily: FONT.sans,
  fontWeight: 400,
  fontSize: 36,
  color: COLORS.slate,
};

// Chrome, pared down per Bobby: the green bar and the wordmark all the way at
// the top, nothing else. No date, no series label, no chapter chips.
export const Chrome: React.FC = () => {
  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 7,
          background: `linear-gradient(90deg, ${COLORS.accentDeep} 0%, rgba(96,178,92,0.12) 100%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 236, // just inside the safe zone so no app UI ever covers it
          left: SAFE.x,
          fontFamily: FONT.sans,
          fontWeight: 600,
          fontSize: 29,
          letterSpacing: 7,
          color: COLORS.text,
        }}
      >
        WOLVES TO A T
      </div>
    </>
  );
};

// ------------------------------------------------------------ statements ---

const Statement: React.FC<{
  frame: number;
  fps: number;
  startSec: number;
  kicker?: string;
  lines: { text: string; green?: boolean }[];
  sub?: string;
  settled?: boolean;
}> = ({ frame, fps, startSec, kicker, lines, sub, settled = false }) => {
  const at = (delay: number) =>
    settled ? { opacity: 1, y: 0 } : riseIn(frame, fps, startSec + delay);
  const k = at(0);
  const s = at(0.14 + lines.length * 0.12);
  return (
    <Stage>
      {kicker ? (
        <div style={{ ...kickerStyle, opacity: k.opacity, transform: `translateY(${k.y}px)`, marginBottom: 30 }}>
          {kicker}
        </div>
      ) : null}
      {lines.map((l, i) => {
        const a = at(0.12 + i * 0.12);
        return (
          <div
            key={i}
            style={{
              ...statementStyle,
              color: l.green ? COLORS.accentPop : COLORS.text,
              opacity: a.opacity,
              transform: `translateY(${a.y}px)`,
            }}
          >
            {l.text}
          </div>
        );
      })}
      {sub ? (
        <div style={{ ...subStyle, marginTop: 30, opacity: s.opacity, transform: `translateY(${s.y}px)` }}>
          {sub}
        </div>
      ) : null}
    </Stage>
  );
};

// The cold open: the biggest number in the series, fully legible inside the
// first second. The reel spends its runtime earning this card, and the loop
// lands back on it.
export const Hook44: React.FC<SceneProps & { settled?: boolean }> = ({ frame, fps, settled }) => {
  const at = (delay: number) =>
    settled ? { opacity: 1, y: 0 } : riseIn(frame, fps, T.h44 + delay, 0.32);
  const k = at(0);
  const a = at(0.04);
  const b = at(0.12);
  return (
    <Stage>
      {/* three small words that turn a naked doom-stat into an owned claim */}
      <div style={{ ...kickerStyle, opacity: k.opacity, transform: `translateY(${k.y}px)`, marginBottom: 26 }}>
        THE MODEL SAYS
      </div>
      <div
        style={{
          fontFamily: FONT.mono,
          fontWeight: 700,
          fontSize: 330,
          lineHeight: 1.0,
          color: COLORS.accentPop,
          fontVariantNumeric: "tabular-nums",
          marginLeft: -14,
          opacity: a.opacity,
          transform: `translateY(${a.y}px)`,
        }}
      >
        44%
      </div>
      <div
        style={{
          fontFamily: FONT.display,
          fontWeight: 700,
          fontSize: 60,
          lineHeight: 1.14,
          color: COLORS.text,
          marginTop: 22,
          opacity: b.opacity,
          transform: `translateY(${b.y}px)`,
        }}
      >
        ANT'S ODDS OF LEAVING
        <br />
        IN THE 2029 WALK YEAR.
      </div>
    </Stage>
  );
};

export const HookOneSummer: React.FC<SceneProps & { settled?: boolean }> = ({ frame, fps, settled }) => (
  <Statement
    frame={frame}
    fps={fps}
    startSec={T.h1}
    settled={settled}
    kicker="THE LAMELO TRADE, PRICED"
    lines={[
      { text: "IT COMES DOWN" },
      { text: "TO ONE SUMMER.", green: true },
    ]}
  />
);

export const TwoMax: React.FC<SceneProps> = ({ frame, fps }) => (
  <Statement
    frame={frame}
    fps={fps}
    startSec={T.twomax}
    lines={[
      { text: "TWO MAX GUYS." },
      { text: "ONE SUMMER.", green: true },
    ]}
    sub="Opposite bets on the same summer."
  />
);

// ------------------------------------------------------------- the year ---

export const Y2029: React.FC<SceneProps> = ({ frame, fps }) => {
  const a = riseIn(frame, fps, T.y2029);
  const b = riseIn(frame, fps, T.y2029 + 0.16);
  const c = riseIn(frame, fps, T.y2029 + 0.34);
  return (
    <Stage>
      <div style={{ ...kickerStyle, opacity: a.opacity, transform: `translateY(${a.y}px)` }}>
        THE SUMMER OF
      </div>
      <div
        style={{
          fontFamily: FONT.mono,
          fontWeight: 700,
          fontSize: 330,
          lineHeight: 1.02,
          color: COLORS.text,
          fontVariantNumeric: "tabular-nums",
          marginLeft: -14, // optical alignment for Consolas' side bearing
          opacity: b.opacity,
          transform: `translateY(${b.y}px)`,
        }}
      >
        2029
      </div>
      <div
        style={{
          fontFamily: FONT.display,
          fontWeight: 700,
          fontSize: 64,
          letterSpacing: 5,
          color: COLORS.accentPop,
          marginTop: 6,
          opacity: c.opacity,
          transform: `translateY(${c.y}px)`,
        }}
      >
        ANT'S WALK YEAR
      </div>
      <div style={{ ...subStyle, marginTop: 26, opacity: c.opacity, transform: `translateY(${c.y}px)` }}>
        History is blunt about walk years.
      </div>
    </Stage>
  );
};

// ------------------------------------------------------------- the cliff ---

const CURVE = { w: 912, h: 600, l: 46, r: 30, top: 96, bottom: 64, yMax: 0.6 };
const cx = (i: number) => CURVE.l + (i * (CURVE.w - CURVE.l - CURVE.r)) / 6;
const cy = (h: number) =>
  CURVE.h - CURVE.bottom - (h / CURVE.yMax) * (CURVE.h - CURVE.bottom - CURVE.top);

export const HazardCurve: React.FC<SceneProps> = ({ frame, fps }) => {
  const intro = ramp(frame, fps, T.curve1, 0.4);
  const p = drawOn(frame, fps, T.curve1 + 0.2, 3.2);
  const callout1 = ramp(frame, fps, T.curve1 + 1.2, 0.45);
  const band = ramp(frame, fps, T.curve2 - 0.1, 0.35);
  const label44 = riseIn(frame, fps, T.curve2 + 0.15, 0.4);
  const circle = drawOn(frame, fps, T.curve2 + 0.35, 0.6);
  const scrawl = ramp(frame, fps, T.curve2 + 0.85, 0.35);
  const arrow = drawOn(frame, fps, T.curve2 + 1.0, 0.4);
  const method = ramp(frame, fps, T.curve3 + 0.2, 0.45);

  const pts = HAZARD.map((d, i) => [cx(i), cy(d.h)] as const);
  const path = pts.map(([x, y], i) => `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
  const spike = pts[2];

  return (
    <Stage>
      <div style={{ ...kickerStyle, opacity: intro, marginBottom: 16 }}>
        EDWARDS · ANNUAL DEPARTURE ODDS, MODELED
      </div>
      <svg width={CURVE.w} height={CURVE.h} style={{ opacity: intro, overflow: "visible" }}>
        {/* 80% interval band at the spike (drawn intervals, spoken point estimates) */}
        <rect
          x={spike[0] - 30}
          y={cy(SPIKE_HI)}
          width={60}
          height={cy(SPIKE_LO) - cy(SPIKE_HI)}
          rx={6}
          fill={COLORS.accentDim}
          opacity={band}
        />
        {/* baseline + year ticks */}
        <line
          x1={CURVE.l - 8}
          x2={CURVE.w - CURVE.r + 8}
          y1={cy(0)}
          y2={cy(0)}
          stroke={COLORS.hair}
          strokeWidth={2}
        />
        {[0, 2, 4, 6].map((i) => (
          <text
            key={i}
            x={cx(i)}
            y={cy(0) + 42}
            textAnchor="middle"
            fill={i === 2 ? COLORS.text : COLORS.mute}
            fontFamily={FONT.mono}
            fontSize={24}
            fontWeight={700}
          >
            {HAZARD[i].season}
          </text>
        ))}
        {/* the curve itself, drawn on slow */}
        <path
          d={path}
          fill="none"
          stroke={COLORS.text}
          strokeWidth={5}
          strokeLinejoin="round"
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - p}
        />
        {pts.map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r={6.5} fill={COLORS.text} opacity={p >= i / 6 - 0.001 ? 1 : 0} />
        ))}
        {/* callout: 1% with two years left (the 2027 point) */}
        <g opacity={callout1}>
          <text x={pts[0][0] - 8} y={pts[0][1] - 118} fill={COLORS.text} fontFamily={FONT.mono} fontSize={46} fontWeight={700}>
            1%
          </text>
          <text x={pts[0][0] - 8} y={pts[0][1] - 80} fill={COLORS.mute} fontFamily={FONT.mono} fontSize={20} letterSpacing={2}>
            TWO YEARS LEFT
          </text>
        </g>
        {/* the spike: green dot, green number, hand-drawn circle, marker scrawl */}
        <circle cx={spike[0]} cy={spike[1]} r={9} fill={COLORS.accentPop} opacity={label44.opacity} />
        <g opacity={label44.opacity} transform={`translate(0 ${label44.y * 0.5})`}>
          <text x={spike[0] + 128} y={spike[1] - 6} fill={COLORS.accentPop} fontFamily={FONT.mono} fontSize={84} fontWeight={700}>
            44%
          </text>
          <text x={spike[0] + 130} y={spike[1] + 30} fill={COLORS.slate} fontFamily={FONT.mono} fontSize={20} letterSpacing={2}>
            THE WALK YEAR
          </text>
        </g>
        <ellipse
          cx={spike[0]}
          cy={spike[1]}
          rx={104}
          ry={70}
          transform={`rotate(-6 ${spike[0]} ${spike[1]})`}
          fill="none"
          stroke={COLORS.accentPop}
          strokeWidth={5}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - circle}
        />
        <text
          x={64}
          y={128}
          fill={COLORS.accentPop}
          fontFamily={FONT.scrawl}
          fontSize={48}
          transform="rotate(-5 64 128)"
          opacity={scrawl}
        >
          the cliff
        </text>
        <path
          d="M 208 138 Q 252 150 246 178"
          fill="none"
          stroke={COLORS.accentPop}
          strokeWidth={4}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - arrow}
        />
        <path d="M 238 172 L 246 184 L 254 172 Z" fill={COLORS.accentPop} opacity={arrow >= 0.98 ? 1 : 0} />
      </svg>
      <div style={{ ...kickerStyle, fontSize: 20, letterSpacing: 2, marginTop: 20, opacity: method }}>
        291 STAR TENURES SINCE 1990 · .600 SCENARIO · 80% BAND: 35 TO 53
      </div>
    </Stage>
  );
};

// ------------------------------------------------------------- unsigned ---

export const Unsigned: React.FC<SceneProps> = ({ frame, fps }) => {
  const a = riseIn(frame, fps, T.unsig);
  const st = stampIn(frame, fps, T.unsig + 0.9);
  const sx = shake(frame, fps, T.unsig + 1.03, 0.4, 5);
  return (
    <Stage>
      <div
        style={{
          width: 880,
          background: COLORS.tile,
          border: `1.5px solid ${COLORS.hair}`,
          borderRadius: RADIUS,
          padding: "44px 52px 52px",
          opacity: a.opacity,
          transform: `translateY(${a.y}px)`,
          position: "relative",
        }}
      >
        <div style={{ ...kickerStyle }}>LAMELO BALL · CONTRACT</div>
        <div style={{ height: 1, background: COLORS.hair, margin: "26px 0 34px" }} />
        <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 76, color: COLORS.text, lineHeight: 1.12 }}>
          DEAL ENDS:
          <br />
          SUMMER 2029
        </div>
        <div style={{ ...subStyle, fontSize: 30, marginTop: 26 }}>
          the same July as Edwards' walk year
        </div>
        {/* an empty band at the bottom of the document for the stamp to land in,
            so the contract line itself stays readable (the mute pass) */}
        <div style={{ height: 150 }} />
        <div
          style={{
            position: "absolute",
            bottom: 26,
            right: 24,
            transform: `rotate(-7deg) translateX(${sx}px) scale(${st.scale})`,
            opacity: st.opacity * 0.94,
            border: `6px solid ${COLORS.text}`,
            borderRadius: 6,
            padding: "8px 34px",
            fontFamily: FONT.display,
            fontWeight: 700,
            fontSize: 100,
            letterSpacing: 12,
            color: COLORS.text,
          }}
        >
          UNSIGNED
        </div>
      </div>
    </Stage>
  );
};

// ------------------------------------------------------------------ cta ---

export const Cta: React.FC<SceneProps> = ({ frame, fps }) => {
  const k = riseIn(frame, fps, T.cta);
  const a = riseIn(frame, fps, T.cta + 0.12);
  const b = riseIn(frame, fps, T.cta + 0.24);
  const bar = ramp(frame, fps, T.cta + 0.4, 0.45);
  const c = riseIn(frame, fps, T.cta + 0.5);
  return (
    <Stage>
      <div style={{ ...kickerStyle, opacity: k.opacity, transform: `translateY(${k.y}px)`, marginBottom: 30 }}>
        THE FULL PRICE, IN THREE PARTS
      </div>
      <div style={{ ...statementStyle, opacity: a.opacity, transform: `translateY(${a.y}px)` }}>COMMENT</div>
      <div
        style={{
          ...statementStyle,
          color: COLORS.accentPop,
          opacity: b.opacity,
          transform: `translateY(${b.y}px)`,
        }}
      >
        "BILL"
      </div>
      <div
        style={{
          width: 280,
          height: 6,
          borderRadius: 3,
          background: COLORS.accent,
          transform: `scaleX(${bar})`,
          transformOrigin: "left",
          margin: "34px 0",
        }}
      />
      <div style={{ ...subStyle, fontSize: 40, opacity: c.opacity, transform: `translateY(${c.y}px)` }}>
        and I'll send you Part 1
      </div>
      <div style={{ ...kickerStyle, fontSize: 22, marginTop: 26, opacity: c.opacity, transform: `translateY(${c.y}px)` }}>
        PRICED ACROSS 50,000 FUTURES · WOLVESTOAT.COM
      </div>
    </Stage>
  );
};

// The static grid cover: the year, the series, the wordmark.
export const Cover: React.FC = () => {
  return (
    <AbsoluteFill>
      <Chrome />
      <Stage>
        <div style={{ ...kickerStyle, marginBottom: 30 }}>PRICING THE LAMELO TRADE · A THREE-PART SERIES</div>
        <div
          style={{
            fontFamily: FONT.mono,
            fontWeight: 700,
            fontSize: 330,
            lineHeight: 1.02,
            color: COLORS.text,
            fontVariantNumeric: "tabular-nums",
            marginLeft: -14,
          }}
        >
          2029
        </div>
        <div
          style={{
            fontFamily: FONT.display,
            fontWeight: 700,
            fontSize: 96,
            letterSpacing: 6,
            color: COLORS.accentPop,
            marginTop: 8,
          }}
        >
          ONE SUMMER.
        </div>
      </Stage>
    </AbsoluteFill>
  );
};
