import React from "react";
import { interpolateColors } from "remotion";
import { scaleLinear } from "d3";
import { COLORS, FONT, SAFE, WIDTH, HEIGHT, STAGE } from "./config";
import { ramp, drawOn, pulse, lerp } from "./animation";
import { ActSpec, MORPH_DUR } from "./timeline";

// One act: a single giant before/after number bound to ONE squared bar by a
// shared frame-ramp, so the digit and the bar tip always finish on the same
// frame. The baseline is quiet chalk; only the thing that changed reddens. Act 3
// teases red then withholds it, so "barely moved" reads as deliberate restraint.

const KICKER_Y = 348;
const FROM_Y = 452;
const HERO_Y = 520; // top of the big number
const UNIT_Y = 748;
const BAR_CY = 956;
const BAR_H = 88;
const CAPTION_Y = 1172;

const BAR_X0 = SAFE.x;
const BAR_X1 = WIDTH - SAFE.x; // 984
const LIVE_W = BAR_X1 - BAR_X0; // 888

const ARROW_CX = 818;
const ARROW_CY = 588;

export const Act: React.FC<{ frame: number; fps: number; act: ActSpec }> = ({ frame, fps, act }) => {
  const reveal = ramp(frame, fps, act.startSec, 0.5);
  const morph = ramp(frame, fps, act.morphSec, MORPH_DUR);

  // Act 3 teases the red (a brief flush mid-morph) then settles back to chalk;
  // the other acts redden and stay red.
  const tease = act.twist ? pulse(frame, fps, act.morphSec, MORPH_DUR) : 0;
  const stateColor = act.twist
    ? interpolateColors(0.4 * tease, [0, 1], [COLORS.baseline, COLORS.alert])
    : interpolateColors(morph, [0, 1], [COLORS.baseline, COLORS.alert]);

  // The shared value: hero number and bar both read it, so they cannot disagree.
  const current = lerp(act.before, act.after, morph);
  const x = scaleLinear().domain([0, act.barMax]).range([0, LIVE_W]);
  const barW = x(current) * reveal;
  const tickX = BAR_X0 + x(act.before);
  const tipX = BAR_X0 + x(act.after);

  const afterIn = ramp(frame, fps, act.morphSec + 0.05, 0.45);
  const markP = drawOn(frame, fps, act.morphSec + 0.35, 0.7);

  const arrowDeg = act.twist ? 0 : act.grow ? -23 : 23;

  const capMorphIn = ramp(frame, fps, act.morphSec, 0.4);
  const revealCapO = reveal * (1 - capMorphIn);
  const morphCapO = capMorphIn;

  const num = (v: number) => `${v.toFixed(act.decimals)}%`;

  // marker scrawl + delta sit near the act's telestrator mark
  const scrawlLeft = act.mark === "bracket" ? (tipX + tickX) / 2 - 30 : act.mark === "lasso" ? tipX + 30 : tickX + 22;
  const scrawlTop = act.twist ? BAR_CY - 208 : BAR_CY - 176;

  return (
    <>
      {/* Kicker */}
      <div style={{ position: "absolute", top: KICKER_Y, left: SAFE.x, opacity: reveal, display: "flex", alignItems: "center" }}>
        <div style={{ width: 13, height: 13, background: stateColor, marginLeft: -28, marginRight: 15 }} />
        <span style={{ color: stateColor, fontFamily: FONT.display, fontSize: FONT.kicker, fontWeight: 600, letterSpacing: 3, textTransform: "uppercase" }}>
          {act.kicker}
        </span>
      </div>

      {/* "BEFORE 42%" anchor: legible (no templated strikethrough); the chalk tick
          on the bar shows where it sat. */}
      <div style={{ position: "absolute", top: FROM_Y, left: SAFE.x, opacity: afterIn, display: "flex", alignItems: "baseline", gap: 14 }}>
        <span style={{ color: COLORS.tertiary, fontFamily: FONT.display, fontSize: 28, fontWeight: 600, letterSpacing: 3 }}>BEFORE</span>
        <span style={{ color: COLORS.subtext, fontFamily: FONT.mono, fontSize: FONT.fromTag, fontWeight: 700, letterSpacing: 0.5 }}>{num(act.before)}</span>
      </div>

      {/* The single giant number: the current (morphing) value. */}
      <div style={{ position: "absolute", top: HERO_Y, left: SAFE.x, opacity: reveal, color: stateColor, fontFamily: FONT.mono, fontSize: FONT.hero, fontWeight: 800, lineHeight: 1, letterSpacing: -2, fontVariantNumeric: "tabular-nums" }}>
        {num(current)}
      </div>

      {/* Metric TYPE in plain words, raised contrast: "were threes" = a share of
          attempts, "went in" = a make rate. Prevents the 3P% misread. */}
      <div style={{ position: "absolute", top: UNIT_Y, left: SAFE.x, opacity: reveal, color: COLORS.subtext, fontFamily: FONT.display, fontSize: FONT.unit, fontWeight: 500, letterSpacing: 0.5 }}>
        {act.unit}
      </div>

      {/* Vector layer: bar, reference tick, telestrator mark, direction glyph. */}
      <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0 }}>
        <rect x={BAR_X0} y={BAR_CY - BAR_H / 2} width={LIVE_W} height={BAR_H} rx={4} fill={COLORS.inset} stroke={COLORS.insetEdge} strokeWidth={1} opacity={reveal} />
        <rect x={BAR_X0} y={BAR_CY - BAR_H / 2} width={Math.max(0, barW)} height={BAR_H} rx={4} fill={stateColor} />

        {/* reference tick: where the regular-season value sat */}
        {morph > 0.02 ? (
          <line x1={tickX} x2={tickX} y1={BAR_CY - BAR_H / 2 - 16} y2={BAR_CY + BAR_H / 2 + 16} stroke={COLORS.chalk} strokeWidth={2.5} strokeDasharray="2 7" strokeLinecap="round" opacity={0.8 * morph} />
        ) : null}

        {/* direction glyph: a drawn arrow (down / up) or, for the twist, an
            "unchanged" equals mark. Draws on like the telestrator. */}
        {act.twist ? (
          <g opacity={afterIn}>
            <line x1={ARROW_CX - 46} x2={ARROW_CX + 46} y1={ARROW_CY - 12} y2={ARROW_CY - 12} stroke={stateColor} strokeWidth={9} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - markP} />
            <line x1={ARROW_CX - 46} x2={ARROW_CX + 46} y1={ARROW_CY + 12} y2={ARROW_CY + 12} stroke={stateColor} strokeWidth={9} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - markP} />
          </g>
        ) : (
          <g transform={`rotate(${arrowDeg} ${ARROW_CX} ${ARROW_CY})`} opacity={afterIn}>
            <path d={`M ${ARROW_CX - 64} ${ARROW_CY} L ${ARROW_CX + 58} ${ARROW_CY} M ${ARROW_CX + 18} ${ARROW_CY - 34} L ${ARROW_CX + 62} ${ARROW_CY} L ${ARROW_CX + 18} ${ARROW_CY + 34}`} fill="none" stroke={stateColor} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - markP} />
          </g>
        )}

        {/* telestrator: one chalk mark per act, hand-drawn reveal */}
        {act.mark === "slash" && markP > 0.001 ? (
          <line x1={tickX - 28} x2={tickX + 28} y1={BAR_CY + 32} y2={BAR_CY - 32} stroke={COLORS.chalk} strokeWidth={5} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - markP} />
        ) : null}
        {act.mark === "lasso" && markP > 0.001 ? (
          <g transform={`rotate(-7 ${tipX} ${BAR_CY})`} opacity={Math.min(1, markP * 1.3)}>
            <ellipse cx={tipX} cy={BAR_CY} rx={62} ry={64} fill="none" stroke={COLORS.chalk} strokeWidth={5} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - markP} />
          </g>
        ) : null}
        {act.mark === "bracket" && markP > 0.001 ? (
          <>
            {/* dark backing so the chalk bracket separates from the near-chalk bar */}
            <path d={`M ${tipX} ${BAR_CY - BAR_H / 2 - 20} L ${tipX} ${BAR_CY - BAR_H / 2 - 34} L ${tickX} ${BAR_CY - BAR_H / 2 - 34} L ${tickX} ${BAR_CY - BAR_H / 2 - 20}`} fill="none" stroke={COLORS.bgBot} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - markP} />
            <path d={`M ${tipX} ${BAR_CY - BAR_H / 2 - 20} L ${tipX} ${BAR_CY - BAR_H / 2 - 34} L ${tickX} ${BAR_CY - BAR_H / 2 - 34} L ${tickX} ${BAR_CY - BAR_H / 2 - 20}`} fill="none" stroke={COLORS.chalk} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - markP} />
          </>
        ) : null}
      </svg>

      {/* magnitude of the move, with the direction glyph in the right gutter */}
      <div style={{ position: "absolute", top: ARROW_CY + 44, left: ARROW_CX - 70, opacity: afterIn, color: COLORS.subtext, fontFamily: FONT.display, fontSize: FONT.delta, fontWeight: 600, letterSpacing: 0.5 }}>
        {act.delta}
      </div>

      {/* hand-scrawled marker word */}
      <div style={{ position: "absolute", top: scrawlTop, left: scrawlLeft, opacity: markP, color: COLORS.chalk, fontFamily: FONT.scrawl, fontSize: FONT.scrawlSize, transform: "rotate(-6deg)", textShadow: `0 2px 10px ${COLORS.bgBot}` }}>
        {act.scrawl}
      </div>

      {/* caption: plain spoken language, Oswald, crossfading reveal -> morph */}
      <div style={{ position: "absolute", top: CAPTION_Y, left: SAFE.x, width: STAGE.width, fontFamily: FONT.display, fontSize: FONT.caption, fontWeight: 500, lineHeight: 1.14, color: COLORS.text, letterSpacing: 0 }}>
        <span style={{ position: "absolute", left: 0, top: 0, opacity: revealCapO }}>{act.revealCaption}</span>
        <span style={{ position: "absolute", left: 0, top: 0, opacity: morphCapO }}>{act.morphCaption}</span>
      </div>
    </>
  );
};
