import React from "react";
import {
  AbsoluteFill,
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Fingerprint, Row, rowCenterY } from "./Fingerprint";
import { Ranking } from "./Ranking";
import { Chyron } from "./Chyron";
import { Background } from "./Background";
import { ProgressBar } from "./ProgressBar";
import { getCamera, ramp } from "./animation";
import { BEATS, RANK_CUT_SEC, activeBeatIndex } from "./timeline";
import { COLORS, FONT, SAFE, bucketColor } from "./config";

export type ClipProps = {
  data: Row[];
  showCaptions: boolean;
  voiceoverSrc: string;
  handle: string;
};

export const Clip: React.FC<ClipProps> = ({
  data,
  showCaptions,
  voiceoverSrc,
  handle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Scene crossfade: fingerprint out, ranking in, at the cut.
  const toRank = ramp(frame, fps, RANK_CUT_SEC, 0.45);
  const showFp = frame < (RANK_CUT_SEC + 1) * fps;
  const showRank = frame > (RANK_CUT_SEC - 0.6) * fps;

  // Camera for the fingerprint scene (slide-to-row + push, then pull back).
  const cam = getCamera(frame, fps, BEATS, rowCenterY);

  // The chyron's accent rule color tracks whatever we are looking at.
  const cur = BEATS[activeBeatIndex(frame, BEATS)];
  const ruleColor =
    cur.scene === "fp" && typeof cur.view === "number"
      ? bucketColor(data[cur.view].value)
      : cur.scene === "rank"
      ? COLORS.good
      : COLORS.chalk;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <Background />

      {showFp ? (
        <AbsoluteFill
          style={{
            opacity: 1 - toRank,
            transform: `translateY(${cam.ty}px) scale(${cam.scale})`,
            transformOrigin: `${cam.originX}px ${cam.originY}px`,
          }}
        >
          <Fingerprint frame={frame} fps={fps} beats={BEATS} data={data} />
        </AbsoluteFill>
      ) : null}

      {showRank ? (
        <AbsoluteFill style={{ opacity: toRank }}>
          <Ranking frame={frame} fps={fps} beats={BEATS} />
        </AbsoluteFill>
      ) : null}

      {/* Brand wordmark, top-left, inside the safe area. */}
      {handle ? (
        <div
          style={{
            position: "absolute",
            top: SAFE.top - 96,
            left: SAFE.x,
            display: "flex",
            alignItems: "center",
            gap: 11,
          }}
        >
          <div style={{ width: 14, height: 14, borderRadius: 7, background: COLORS.good }} />
          <span
            style={{
              color: COLORS.text,
              fontFamily: FONT.family,
              fontSize: FONT.small,
              fontWeight: 800,
              letterSpacing: 2.5,
            }}
          >
            WOLVES TO A T
          </span>
        </div>
      ) : null}

      {showCaptions ? <Chyron beats={BEATS} ruleColor={ruleColor} /> : null}

      <ProgressBar />

      {voiceoverSrc ? <Audio src={staticFile(voiceoverSrc)} /> : null}
    </AbsoluteFill>
  );
};
