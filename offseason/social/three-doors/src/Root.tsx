import React from "react";
import { Composition } from "remotion";
import { WIDTH, HEIGHT, FPS } from "./config";
import { Hook, Setup, Swing, Flip, Stockpile, Plane, CTA } from "./Slides";
import { FdHook, FdPlan, FdCap, FdVerdict, FdTakeaway, FdCTA } from "./FourthDoor";

// Two carousels in one project, same house look. (1) "Three Doors", the seven-slide
// original. (2) "The Fourth Door" (fd-*), the six-slide continuation: the keep-core
// Package A build (Randle+DiVincenzo -> Jrue, the MLE shooter, re-sign Ayo, develop Joan).
// Every on-screen number is validated: cap/salary figures trace to the warehouse contracts
// and the Package A gate ($206.6M, $2.5M under the first apron); title odds are the model
// run, framed "my model says". HYPOTHETICAL, tagged as such. Render with `remotion still`.
const slides: { id: string; component: React.FC }[] = [
  { id: "01-hook", component: Hook },
  { id: "02-setup", component: Setup },
  { id: "03-swing", component: Swing },
  { id: "04-flip", component: Flip },
  { id: "05-stockpile", component: Stockpile },
  { id: "06-plane", component: Plane },
  { id: "07-cta", component: CTA },
  // The Fourth Door (six slides)
  { id: "fd-1-hook", component: FdHook },
  { id: "fd-2-plan", component: FdPlan },
  { id: "fd-3-cap", component: FdCap },
  { id: "fd-4-verdict", component: FdVerdict },
  { id: "fd-5-takeaway", component: FdTakeaway },
  { id: "fd-6-cta", component: FdCTA },
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
