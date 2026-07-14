import React from "react";
import { AbsoluteFill } from "remotion";
import { WIDTH, HEIGHT, COLORS } from "./config";

// The carousel backdrop: midnight navy gradient, one faint green aurora up and
// to the right, a gentle vignette, and a whisper of grain. The aurora is the
// only glow in the whole video, exactly like the slides.
export const Background: React.FC = () => {
  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{ background: `linear-gradient(180deg, ${COLORS.bgTop} 0%, ${COLORS.bgBot} 100%)` }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(60% 42% at 78% 14%, rgba(96,178,92,0.22) 0%, rgba(96,178,92,0.07) 45%, rgba(96,178,92,0) 72%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(125% 80% at 50% 38%, rgba(0,0,0,0) 55%, rgba(2,8,16,0.5) 100%)`,
        }}
      />
      <svg
        width={WIDTH}
        height={HEIGHT}
        style={{ position: "absolute", inset: 0, opacity: 0.05, mixBlendMode: "overlay" }}
      >
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="2" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width={WIDTH} height={HEIGHT} filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};
