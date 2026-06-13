import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { Beat, activeBeatIndex } from "./timeline";
import { ramp } from "./animation";
import { COLORS, FONT, SAFE } from "./config";

// The on-screen text. Editorial, not kinetic: a confident lower-third for the
// body of the clip (a colored rule, a chapter number, the line), and a centered
// title card for the hook and the close. Whole lines, not bouncing words, is
// what reads as "a person edited this" rather than a template.
export const Chyron: React.FC<{ beats: Beat[]; ruleColor: string }> = ({
  beats,
  ruleColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const idx = activeBeatIndex(frame, beats);
  const beat = beats[idx];
  if (!beat.screen) return null;

  // Only the closing CTA is a centered card. Everything else, including the hook
  // (numbers fill the screen above it) and the metric-name beat (the components
  // stay visible), is a lower-third.
  const centered = !!beat.flags?.cta;

  const p = ramp(frame, fps, beat.startSec + 0.05, 0.45);
  const ty = (1 - p) * 24;

  if (centered) {
    return (
      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center", padding: `0 ${SAFE.x}px` }}
      >
        <div
          style={{
            width: 60,
            height: 7,
            borderRadius: 4,
            background: ruleColor,
            transform: `scaleX(${p})`,
            marginBottom: 30,
          }}
        />
        <div
          style={{
            textAlign: "center",
            color: COLORS.text,
            fontFamily: FONT.family,
            fontSize: beat.flags?.cta ? 64 : FONT.hook,
            fontWeight: 900,
            lineHeight: 1.04,
            letterSpacing: -1,
            opacity: p,
            transform: `translateY(${ty}px)`,
            textShadow: "0 6px 40px rgba(0,0,0,0.55)",
          }}
        >
          {beat.screen}
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <>
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.45) 16%, rgba(0,0,0,0) 34%)",
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "flex-start",
          paddingBottom: SAFE.bottom + 26,
          paddingLeft: SAFE.x,
          paddingRight: SAFE.x,
        }}
      >
        {/* kicker row: a colored tick and the chapter number */}
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
          <div
            style={{
              width: 44,
              height: 6,
              borderRadius: 3,
              background: ruleColor,
              transform: `scaleX(${p})`,
              transformOrigin: "left",
            }}
          />
          {beat.index ? (
            <span
              style={{
                color: ruleColor,
                fontFamily: FONT.mono,
                fontSize: FONT.index,
                fontWeight: 800,
                letterSpacing: 1,
                opacity: p,
              }}
            >
              {beat.index} <span style={{ color: COLORS.tertiary }}>/ 05</span>
            </span>
          ) : null}
        </div>
        <div
          style={{
            textAlign: "left",
            color: COLORS.text,
            fontFamily: FONT.family,
            fontSize: FONT.chyron,
            fontWeight: 800,
            lineHeight: 1.05,
            letterSpacing: -0.5,
            opacity: p,
            transform: `translateY(${ty}px)`,
            textShadow: "0 4px 28px rgba(0,0,0,0.6)",
          }}
        >
          {beat.screen}
        </div>
      </AbsoluteFill>
    </>
  );
};
