import React from "react";
import { AbsoluteFill, Composition, Still } from "remotion";
import { Clip, ClipProps } from "./Clip";
import { Background } from "./Background";
import { Cover } from "./Scenes";
import { WIDTH, HEIGHT, FPS } from "./config";
import { DURATION_IN_FRAMES } from "./timeline";

const defaultProps: ClipProps = {
  showCaptions: true,
  voiceoverSrc: "", // set to "voiceover.mp3" (placed in public/) to bake in Bobby's VO
};

const CoverComp: React.FC = () => (
  <AbsoluteFill>
    <Background />
    <Cover />
  </AbsoluteFill>
);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Clip"
        component={Clip}
        durationInFrames={DURATION_IN_FRAMES}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={defaultProps}
      />
      <Still id="Cover" component={CoverComp} width={WIDTH} height={HEIGHT} />
    </>
  );
};
