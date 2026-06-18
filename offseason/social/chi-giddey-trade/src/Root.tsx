import React from "react";
import { Composition } from "remotion";
import { WIDTH, HEIGHT, FPS } from "./config";
import { Hook, Deal, Cap, Title, SayYes, Verdict } from "./Slides";

// Six still compositions, one per carousel slide, rendered at 1080 x 1350 with
// `remotion still`. Every on-screen number traces to a trade-model run; see
// claims.json + provenance.json (run validate.py to refresh). This is a
// HYPOTHETICAL trade idea, tagged as such on slide 1.
const slides: { id: string; component: React.FC }[] = [
  { id: "S1-Hook", component: Hook },
  { id: "S2-Deal", component: Deal },
  { id: "S3-Cap", component: Cap },
  { id: "S4-Title", component: Title },
  { id: "S5-SayYes", component: SayYes },
  { id: "S6-Verdict", component: Verdict },
];

export const RemotionRoot: React.FC = () => (
  <>
    {slides.map((s) => (
      <Composition
        key={s.id}
        id={s.id}
        component={s.component}
        durationInFrames={1}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    ))}
  </>
);
