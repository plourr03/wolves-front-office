import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { LafiBarChart, Row } from "./LafiBarChart";
import { Captions } from "./Captions";
import { Background } from "./Background";
import { ProgressBar } from "./ProgressBar";
import { ramp } from "./animation";
import { BEATS, activeBeatIndex, focusRows } from "./timeline";
import { COLORS, FONT, SAFE } from "./config";

export type ClipProps = {
  data: Row[];
  highlightIndex: number;
  showCaptions: boolean;
  voiceoverSrc: string;
  handle: string;
};

export const Clip: React.FC<ClipProps> = ({
  data,
  highlightIndex,
  showCaptions,
  voiceoverSrc,
  handle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Bars begin growing at the first "draw" beat so the chart stays hidden under
  // the opening hook.
  const drawBeat = BEATS.find((b) => b.kind === "draw");
  const growDelaySec = drawBeat ? drawBeat.startSec : 0;

  // The chyron rule tracks what we are looking at.
  const cur = BEATS[activeBeatIndex(frame, BEATS)];
  const focus = focusRows(cur);
  const ruleColor = focus && focus.includes(highlightIndex) ? COLORS.highlight : COLORS.chalk;

  // Recede the chart behind the centered CTA card so the closing line reads clean.
  const chartOpacity = cur.cta ? 1 - 0.78 * ramp(frame, fps, cur.startSec, 0.4) : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <Background />

      <AbsoluteFill style={{ opacity: chartOpacity }}>
        <LafiBarChart
          frame={frame}
          fps={fps}
          data={data}
          beats={BEATS}
          highlightIndex={highlightIndex}
          growDelaySec={growDelaySec}
        />
      </AbsoluteFill>

      {/* Brand wordmark, top-left, inside the safe area. */}
      {handle ? (
        <div
          style={{
            position: "absolute",
            top: SAFE.top - 92,
            left: SAFE.x,
            display: "flex",
            alignItems: "center",
            gap: 11,
          }}
        >
          <div style={{ width: 14, height: 14, borderRadius: 7, background: COLORS.accent }} />
          <span
            style={{
              color: COLORS.text,
              fontFamily: FONT.family,
              fontSize: FONT.small,
              fontWeight: 800,
              letterSpacing: 2,
            }}
          >
            {handle}
          </span>
        </div>
      ) : null}

      {showCaptions ? <Captions beats={BEATS} ruleColor={ruleColor} /> : null}

      <ProgressBar />

      {voiceoverSrc ? <Audio src={staticFile(voiceoverSrc)} /> : null}
    </AbsoluteFill>
  );
};
