import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { Beat, activeBeatIndex } from "./timeline";
import { ramp } from "./animation";
import { COLORS, FONT, SAFE } from "./config";

// The on-screen text. Editorial, not kinetic: a confident lower-third for the
// body of the clip (a colored rule, an optional chapter number, the whole line),
// and a centered title card only for a hook or the closing CTA. Whole lines
// fading in is what reads as "a person edited this" rather than a template.
// (Bouncing each word in one at a time is the single biggest AI tell. Avoid it.)
export const Captions: React.FC<{ beats: Beat[]; ruleColor?: string }> = ({
  beats,
  ruleColor = COLORS.chalk,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const idx = activeBeatIndex(frame, beats);
  const beat = beats[idx];
  if (!beat.caption) return null;

  const p = ramp(frame, fps, beat.startSec + 0.05, 0.45);
  const ty = (1 - p) * 24;
  const lines = beat.caption.split("\n");

  if (beat.cta) {
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: `0 ${SAFE.x}px` }}>
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
            fontSize: FONT.hook,
            fontWeight: 900,
            lineHeight: 1.04,
            letterSpacing: -1,
            opacity: p,
            transform: `translateY(${ty}px)`,
            textShadow: "0 6px 40px rgba(0,0,0,0.55)",
          }}
        >
          {lines.map((l, i) => (
            <div key={i}>{l}</div>
          ))}
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
              {beat.index}
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
            lineHeight: 1.06,
            letterSpacing: -0.5,
            opacity: p,
            transform: `translateY(${ty}px)`,
            textShadow: "0 4px 28px rgba(0,0,0,0.6)",
          }}
        >
          {lines.map((l, i) => (
            <div key={i}>{l}</div>
          ))}
        </div>
      </AbsoluteFill>
    </>
  );
};
