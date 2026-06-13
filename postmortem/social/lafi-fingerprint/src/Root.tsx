import React from "react";
import { Composition } from "remotion";
import { Clip, ClipProps } from "./Clip";
import { WIDTH, HEIGHT, FPS } from "./config";
import { DURATION_IN_FRAMES } from "./timeline";
import { Row } from "./Fingerprint";

// The Wolves' 2025-26 LAFI fingerprint, straight from the article chart
// (postmortem/outputs/charts/q0a_lafi/fingerprint_fragment.html). Each value is
// a percentile against every team-season since 2014-15. Ordered high to low so
// the bars step down out of the red pickup zone into healthy green.
const FINGERPRINT: Row[] = [
  { name: "Isolation Reliance", value: 90, desc: "How often possessions end one on one" },
  { name: "Shot Quality Decay", value: 83, desc: "Whether the resulting shots are good" },
  { name: "Motion Death", value: 72, desc: "How much the off-ball players move" },
  { name: "Action Poverty", value: 45, desc: "How narrow the playbook is" },
  { name: "Ball Stickiness", value: 31, desc: "How much one player dominates the ball" },
];

const defaultProps: ClipProps = {
  data: FINGERPRINT,
  showCaptions: true,
  voiceoverSrc: "", // set to e.g. "voiceover.mp3" (placed in public/) to bake in audio
  handle: "@WolvesToaT",
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Clip"
      component={Clip}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
      defaultProps={defaultProps}
    />
  );
};
