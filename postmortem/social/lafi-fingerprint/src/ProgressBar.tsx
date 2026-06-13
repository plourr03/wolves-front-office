import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { WIDTH, HEIGHT, SAFE, COLORS } from "./config";
import { DURATION_IN_FRAMES } from "./timeline";

// A thin progress bar near the bottom safe edge. A small detail that makes the
// clip feel produced rather than thrown together.
export const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const total = durationInFrames || DURATION_IN_FRAMES;
  const p = Math.min(1, frame / (total - 1));

  const x = SAFE.x;
  const y = HEIGHT - 58;
  const w = WIDTH - SAFE.x * 2;
  const h = 6;

  return (
    <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0 }}>
      <rect x={x} y={y} width={w} height={h} rx={3} fill="rgba(255,255,255,0.12)" />
      <rect
        x={x}
        y={y}
        width={Math.max(h, w * p)}
        height={h}
        rx={3}
        fill={COLORS.accent}
        style={{ filter: `drop-shadow(0 0 8px ${COLORS.accent}aa)` }}
      />
    </svg>
  );
};
