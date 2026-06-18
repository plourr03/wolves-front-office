import React from "react";
import { Composition } from "remotion";
import { Clip, ClipProps } from "./Clip";
import { WIDTH, HEIGHT, FPS } from "./config";
import { DURATION_IN_FRAMES } from "./timeline";

// The script (acts, validated numbers, copy, timing) lives in src/timeline.ts.
// Every on-screen number is traced to a warehouse query in provenance.json and
// the six-band cross-check in src/shot_diet.json. Re-run
// `python social/ant-shot-diet/validate.py` to refresh both.
const defaultProps: ClipProps = {
  voiceoverSrc: "", // silent post: leave empty. Add music in the editor after render.
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
