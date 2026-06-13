import React from "react";
import { Composition } from "remotion";
import { Clip, ClipProps } from "./Clip";
import { WIDTH, HEIGHT, FPS } from "./config";
import { DURATION_IN_FRAMES } from "./timeline";
import { Row } from "./LafiBarChart";

// Sample data so the clip renders out of the box. Replace with real LAFI output.
// Ordered high to low; the featured team is index 0.
const SAMPLE_DATA: Row[] = [
  { team: "Wolves", value: 18.7 },
  { team: "Hawks", value: 15.2 },
  { team: "Pacers", value: 14.6 },
  { team: "Spurs", value: 12.1 },
  { team: "Magic", value: 10.9 },
  { team: "Heat", value: 9.4 },
];

const defaultProps: ClipProps = {
  data: SAMPLE_DATA,
  highlightIndex: 0,
  showCaptions: true,
  voiceoverSrc: "", // set to e.g. "voiceover.mp3" (placed in public/) to bake in audio
  handle: "@wolvestoat",
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
