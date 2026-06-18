import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Background } from "./Background";
import { ProgressBar } from "./ProgressBar";
import { Act } from "./Act";
import { HookScene, EndCard } from "./Cards";
import { ramp } from "./animation";
import { ACTS, PAYOFF, SIGNOFF, PAYOFF_SEC, SIGNOFF_SEC, DISCLOSURE_PRE, DISCLOSURE_POST } from "./timeline";
import { COLORS, FONT, SAFE } from "./config";

export type ClipProps = {
  voiceoverSrc: string;
  handle: string;
};

const HOOK_END = ACTS[0].startSec;

// A scene lingers 0.3s into the next so adjacent scenes cross-fade instead of
// hard-cutting; content fades in via each scene's own ramps.
const fadeOut = (frame: number, fps: number, endSec: number) =>
  1 - ramp(frame, fps, endSec, 0.3);

export const Clip: React.FC<ClipProps> = ({ voiceoverSrc, handle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sec = frame / fps;

  const mastheadO = ramp(frame, fps, 0.1, 0.6) * (1 - ramp(frame, fps, SIGNOFF_SEC, 0.4));
  // Persistent chrome ramps in ONCE at the first act and holds through all acts
  // (decoupled from the act index, so it never re-fades at a boundary).
  const actIdx = ACTS.reduce((acc, a, i) => (sec >= a.startSec ? i : acc), -1);
  const chromeO = ramp(frame, fps, ACTS[0].startSec, 0.4) * (1 - ramp(frame, fps, PAYOFF_SEC, 0.3));

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <Background />

      {/* ---- Scenes (cross-fade at boundaries) ---- */}
      {sec < HOOK_END + 0.3 ? (
        <AbsoluteFill style={{ opacity: fadeOut(frame, fps, HOOK_END) }}>
          <HookScene frame={frame} fps={fps} />
        </AbsoluteFill>
      ) : null}

      {ACTS.map((act) =>
        sec >= act.startSec - 0.05 && sec < act.endSec ? (
          // No linger past endSec: the fade-out completes AT the boundary and the
          // next act's reveal carries the hand-off, so two giant numbers never stack.
          <AbsoluteFill key={act.id} style={{ opacity: 1 - ramp(frame, fps, act.endSec - 0.3, 0.3) }}>
            <Act frame={frame} fps={fps} act={act} />
          </AbsoluteFill>
        ) : null
      )}

      {sec >= PAYOFF_SEC - 0.05 && sec < SIGNOFF_SEC + 0.3 ? (
        <AbsoluteFill style={{ opacity: fadeOut(frame, fps, SIGNOFF_SEC) }}>
          <EndCard frame={frame} fps={fps} startSec={PAYOFF.startSec} text={PAYOFF.text} />
        </AbsoluteFill>
      ) : null}

      {sec >= SIGNOFF_SEC - 0.05 ? (
        <EndCard frame={frame} fps={fps} startSec={SIGNOFF.startSec} text={SIGNOFF.text} signoff />
      ) : null}

      {/* ---- Persistent masthead ---- */}
      {handle ? (
        <div style={{ position: "absolute", top: SAFE.top, left: SAFE.x, right: SAFE.x, opacity: mastheadO }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
              <div style={{ width: 13, height: 13, borderRadius: 7, background: COLORS.good }} />
              <span style={{ color: COLORS.text, fontFamily: FONT.family, fontSize: FONT.wordmark, fontWeight: 800, letterSpacing: 2.5 }}>
                WOLVES TO A T
              </span>
            </div>
            <span style={{ color: COLORS.tertiary, fontFamily: FONT.mono, fontSize: FONT.footer, fontWeight: 700, letterSpacing: 1 }}>
              NO. 07
            </span>
          </div>
          <div style={{ marginTop: 16, height: 1, background: COLORS.hairline }} />
        </div>
      ) : null}

      {/* ---- Sample disclosure (honest about the 6-game series), during acts ---- */}
      <div
        style={{
          position: "absolute",
          top: SAFE.top + 80,
          left: SAFE.x,
          opacity: chromeO,
          fontFamily: FONT.mono,
          fontSize: FONT.pill,
          fontWeight: 600,
          letterSpacing: 1,
          color: COLORS.subtext,
        }}
      >
        {DISCLOSURE_PRE}
        <span style={{ color: COLORS.tertiary, margin: "0 8px" }}>{"→"}</span>
        <span style={{ color: COLORS.text, fontWeight: 800 }}>{DISCLOSURE_POST}</span>
      </div>

      {/* ---- Footer: act counter + the warehouse table it came from ---- */}
      <div style={{ position: "absolute", top: 1430, left: SAFE.x, right: SAFE.x, opacity: chromeO }}>
        <div style={{ height: 1, background: COLORS.hairline, marginBottom: 14 }} />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ color: COLORS.subtext, fontFamily: FONT.mono, fontSize: FONT.footer, fontWeight: 700, letterSpacing: 1 }}>
            ACT {String(Math.max(0, actIdx) + 1).padStart(2, "0")} / 03
          </span>
          <span style={{ color: COLORS.subtext, fontFamily: FONT.family, fontSize: 20, fontWeight: 500, letterSpacing: 0.5 }}>
            nba_shot_chart_detail · 2025-26
          </span>
        </div>
      </div>

      <ProgressBar />

      {voiceoverSrc ? <Audio src={staticFile(voiceoverSrc)} /> : null}
    </AbsoluteFill>
  );
};
