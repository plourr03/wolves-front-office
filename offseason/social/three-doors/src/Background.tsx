import React from "react";
import { AbsoluteFill } from "remotion";
import { WIDTH, HEIGHT, COLORS } from "./config";

// A quiet, editorial backdrop: a soft vertical gradient, a gentle corner
// vignette, and a fine film grain. Deliberately understated so the chart, not
// the background, carries the screen. The grain is the single fastest signal
// that a person made this in a design tool rather than a generator.
export const Background: React.FC = () => {
  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, ${COLORS.bgTop} 0%, ${COLORS.bgBot} 100%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(125% 80% at 50% 36%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.5) 100%)`,
        }}
      />
      <svg
        width={WIDTH}
        height={HEIGHT}
        style={{ position: "absolute", inset: 0, opacity: 0.12, mixBlendMode: "overlay" }}
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
