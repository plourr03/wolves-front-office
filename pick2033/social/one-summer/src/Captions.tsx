import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { Beat, activeBeatIndex } from "./timeline";
import { ramp } from "./animation";
import { COLORS, FONT, SAFE } from "./config";

// Burned-in captions for muted viewers: an editorial lower-third (a green rule,
// a chapter chip, whole lines fading in), never kinetic word-by-word text. Max
// two lines, matching the spoken script verbatim, inside the safe zone.
export const Captions: React.FC<{ beats: Beat[] }> = ({ beats }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const idx = activeBeatIndex(frame, beats);
  const beat = beats[idx];
  if (!beat.caption) return null;

  const p = ramp(frame, fps, beat.startSec + 0.05, 0.4);
  const ty = (1 - p) * 22;
  const lines = beat.caption.split("\n");

  return (
    <>
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to top, rgba(4,12,24,0.85) 0%, rgba(4,12,24,0.45) 15%, rgba(4,12,24,0) 32%)",
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "flex-start",
          paddingBottom: SAFE.bottom + 30,
          paddingLeft: SAFE.x,
          paddingRight: SAFE.x,
        }}
      >
        <div
          style={{
            width: 46,
            height: 6,
            borderRadius: 3,
            background: COLORS.accent,
            transform: `scaleX(${p})`,
            transformOrigin: "left",
            marginBottom: 18,
          }}
        />
        <div
          style={{
            textAlign: "left",
            color: COLORS.text,
            fontFamily: FONT.sans,
            fontSize: FONT.chyron,
            fontWeight: 600,
            lineHeight: 1.22,
            letterSpacing: -0.3,
            opacity: p,
            transform: `translateY(${ty}px)`,
            textShadow: "0 4px 26px rgba(0,0,0,0.55)",
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
