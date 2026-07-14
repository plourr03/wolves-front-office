import React from "react";
import { AbsoluteFill, Audio, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Background } from "./Background";
import { Captions } from "./Captions";
import { Chrome, Cta, HazardCurve, Hook44, HookOneSummer, TwoMax, Unsigned, Y2029 } from "./Scenes";
import { BEATS, BeatId, activeBeatIndex } from "./timeline";
import { COLORS } from "./config";

export type ClipProps = {
  showCaptions: boolean;
  voiceoverSrc: string;
};

// Which visual a beat renders. Beats that share a scene (the three curve
// beats) never transition between themselves.
const sceneKey = (id: BeatId): string =>
  id === "curve1" || id === "curve2" || id === "curve3" ? "curve" : id === "loop" ? "h44" : id;

// One directional gesture for the whole video: on every beat change the
// outgoing scene drifts UP and fades while the incoming one rises from below
// (the scenes' own entrances). A short overlap, a confident ease, no wipes.
const OVERLAP_SEC = 0.3;

export const Clip: React.FC<ClipProps> = ({ showCaptions, voiceoverSrc }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const idx = activeBeatIndex(frame, BEATS);
  const beat = BEATS[idx];
  const prev = idx > 0 ? BEATS[idx - 1] : null;

  const scene = (id: BeatId): React.ReactNode => {
    switch (sceneKey(id)) {
      case "h44":
        return <Hook44 frame={frame} fps={fps} settled={id === "loop"} />;
      case "h1":
        return <HookOneSummer frame={frame} fps={fps} />;
      case "y2029":
        return <Y2029 frame={frame} fps={fps} />;
      case "curve":
        return <HazardCurve frame={frame} fps={fps} />;
      case "unsig":
        return <Unsigned frame={frame} fps={fps} />;
      case "twomax":
        return <TwoMax frame={frame} fps={fps} />;
      default:
        return <Cta frame={frame} fps={fps} />;
    }
  };

  // Outgoing-scene progress across the overlap window at the top of this beat.
  const out = interpolate(
    frame,
    [beat.startSec * fps, (beat.startSec + OVERLAP_SEC) * fps],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.22, 1, 0.36, 1) }
  );
  // No dissolve into the loop card: the hard cut back to the hook IS the loop.
  const showPrev =
    prev !== null && beat.id !== "loop" && sceneKey(prev.id) !== sceneKey(beat.id) && out < 1;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bgBot }}>
      <Background />
      {showPrev ? (
        <AbsoluteFill style={{ opacity: 1 - out, transform: `translateY(${-44 * out}px)` }}>
          {scene(prev!.id)}
        </AbsoluteFill>
      ) : null}
      {scene(beat.id)}
      <Chrome />
      {showCaptions ? <Captions beats={BEATS} /> : null}
      {voiceoverSrc ? <Audio src={staticFile(voiceoverSrc)} /> : null}
    </AbsoluteFill>
  );
};
