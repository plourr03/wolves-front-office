import React from "react";
import { COLORS, FONT, SAFE, STAGE } from "./config";
import { ramp, drawOn } from "./animation";
import { HOOK } from "./timeline";

// The Fraunces book-end cards: hook, payoff, sign-off. Left-aligned editorial
// voice on a clean page, no chart. A brand-green rule draws in like an editor's
// pen stroke; green appears only here and on the wordmark/progress.

const Line: React.FC<{
  text: string;
  top: number;
  opacity: number;
  size?: number;
}> = ({ text, top, opacity, size = FONT.card }) => (
  <div
    style={{
      position: "absolute",
      top,
      left: SAFE.x,
      width: STAGE.width,
      opacity,
      color: COLORS.text,
      fontFamily: FONT.display,
      fontSize: size,
      fontWeight: 600,
      lineHeight: 1.06,
      letterSpacing: -1,
    }}
  >
    {text}
  </div>
);

const Rule: React.FC<{ top: number; p: number }> = ({ top, p }) => (
  <div
    style={{
      position: "absolute",
      top,
      left: SAFE.x,
      width: 150,
      height: 8,
      borderRadius: 4,
      background: COLORS.good,
      transform: `scaleX(${p})`,
      transformOrigin: "left",
    }}
  />
);

export const HookScene: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const l1 = ramp(frame, fps, HOOK[0].startSec + 0.15, 0.6);
  const l2In = ramp(frame, fps, HOOK[1].startSec + 0.05, 0.5);
  const rule = drawOn(frame, fps, HOOK[1].startSec + 0.2, 0.6);
  // line 1 holds, then dims as line 2 lands
  const l1o = l1 * (1 - 0.55 * l2In);
  return (
    <>
      <Line text={HOOK[0].text} top={610} opacity={l1o} />
      <Line text={HOOK[1].text} top={846} opacity={l2In} />
      <Rule top={1004} p={rule} />
    </>
  );
};

export const EndCard: React.FC<{
  frame: number;
  fps: number;
  startSec: number;
  text: string;
  signoff?: boolean;
}> = ({ frame, fps, startSec, text, signoff }) => {
  const inP = ramp(frame, fps, startSec + 0.1, 0.6);
  const rule = drawOn(frame, fps, startSec + 0.3, 0.6);
  const ty = (1 - inP) * 16;
  const size = signoff ? 76 : FONT.card;
  // Flex column: the rule always sits BELOW the text, whatever the line count.
  return (
    <div
      style={{
        position: "absolute",
        top: signoff ? 720 : 640,
        left: SAFE.x,
        width: STAGE.width,
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        transform: `translateY(${ty}px)`,
      }}
    >
      {signoff ? (
        <div style={{ width: 18, height: 18, borderRadius: 9, background: COLORS.good, opacity: inP, marginBottom: 30 }} />
      ) : null}
      <div
        style={{
          opacity: inP,
          color: COLORS.text,
          fontFamily: FONT.display,
          fontSize: size,
          fontWeight: 600,
          lineHeight: 1.08,
          letterSpacing: -1,
        }}
      >
        {text}
      </div>
      <div style={{ marginTop: 34, width: 150, height: 8, borderRadius: 4, background: COLORS.good, transform: `scaleX(${rule})`, transformOrigin: "left" }} />
    </div>
  );
};
