// "The Fourth Door" — the continuation of Three Doors. Same warm-dark print stock,
// same tokens (one brand green for the thing that matters, chalk for everything else,
// the lone vermilion reserved for cap state). Six 1080x1350 stills.
//
// Every number here is validated: cap/salary figures trace to the warehouse contracts
// and the Package A gate run ($206.6M payroll, $2.5M under the first apron); the title
// odds are the model run, framed "my model says". See fourth-door.json / provenance.json.
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { Background } from "./Background";
import { SAFE, COLORS, FONT, RADIUS, CAP } from "./config";
import fd from "./fourth-door.json";

const WIDTH = 1080;
const TOTAL = 6;
const TRACK = WIDTH - SAFE.x * 2; // 912

// ---------------------------------------------------------------- shared chrome
const Footer: React.FC<{ page: number }> = ({ page }) => (
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: `1px solid ${COLORS.hairline}`, paddingTop: 16, marginTop: 16 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <Img src={staticFile("logo.png")} style={{ width: 34, height: 34, objectFit: "contain" }} />
      <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: FONT.wordmark, letterSpacing: 1, color: COLORS.text }}>WOLVES TO A T</span>
      <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: FONT.page, color: COLORS.tertiary }}>{page} / {TOTAL}</span>
    </div>
    <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 22, color: COLORS.alert, letterSpacing: 0.5, opacity: 0.9 }}>@wolvestoat</span>
  </div>
);

const Frame: React.FC<{ kicker?: string; page: number; children: React.ReactNode }> = ({ kicker, page, children }) => (
  <AbsoluteFill style={{ fontFamily: FONT.sans }}>
    <Background />
    <AbsoluteFill style={{ paddingTop: SAFE.top, paddingBottom: SAFE.bottom, paddingLeft: SAFE.x, paddingRight: SAFE.x, display: "flex", flexDirection: "column" }}>
      {kicker !== undefined && (
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 22 }}>
          <div style={{ width: 46, height: 5, background: COLORS.alert, borderRadius: RADIUS }} />
          <div style={{ fontWeight: 700, fontSize: FONT.kicker, letterSpacing: 4, textTransform: "uppercase", color: COLORS.subtext }}>{kicker}</div>
        </div>
      )}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>{children}</div>
      <Footer page={page} />
    </AbsoluteFill>
  </AbsoluteFill>
);

const Tag: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color }) => (
  <span style={{ display: "inline-block", fontWeight: 700, fontSize: FONT.tag, letterSpacing: 2, textTransform: "uppercase", color: color ?? COLORS.alert, border: `1.5px solid ${color ?? COLORS.alert}`, borderRadius: RADIUS, padding: "8px 14px" }}>
    {children}
  </span>
);

const Scrawl: React.FC<{ children: React.ReactNode; color?: string; size?: number; rot?: number }> = ({ children, color, size, rot }) => (
  <span style={{ fontFamily: FONT.scrawl, fontSize: size ?? 40, color: color ?? COLORS.alert, transform: `rotate(${rot ?? -3}deg)`, display: "inline-block", whiteSpace: "nowrap" }}>{children}</span>
);

// ---------------------------------------------------------------- the cap meter
// Reframed: the prize is the TIER, not a bigger MLE. Two worlds on one rail — keep
// Randle (jammed in the second-apron zone) vs trade for Jrue (back under the first
// apron). The tier drop is the whole point; the shooter is a footnote.
const CapMeter: React.FC = () => {
  const { apron1, apron2 } = CAP;
  const lo = 196, hi = 224;
  const x = (v: number) => Math.max(0, ((v - lo) / (hi - lo)) * TRACK);
  const barH = 64, topY = 52, gap = 70;
  const botY = topY + barH + gap, H = botY + barH + 88;
  const rows = [
    { y: topY, end: fd.cap.keep, label: fd.cap.keepLabel, tag: "KEEP RANDLE", fill: COLORS.apronBreak, txt: COLORS.apronBreak },
    { y: botY, end: fd.cap.trade, label: fd.cap.tradeLabel, tag: "TRADE FOR JRUE", fill: COLORS.good, txt: COLORS.good },
  ];
  return (
    <div style={{ position: "relative", width: TRACK, height: H }}>
      <svg width={TRACK} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
        {/* the restricted zone: everything between the two aprons */}
        <rect x={x(apron1)} y={topY - 22} width={x(apron2) - x(apron1)} height={botY + barH - topY + 44} fill="rgba(226,80,58,0.09)" />
        {/* the two world-bars */}
        {rows.map((r) => <rect key={r.tag} x={0} y={r.y} width={x(r.end)} height={barH} rx={RADIUS} fill={r.fill} />)}
        {/* apron lines (first apron emphasized) */}
        {[{ v: apron1, emph: true }, { v: apron2, emph: false }].map((m) => (
          <line key={m.v} x1={x(m.v)} y1={topY - 22} x2={x(m.v)} y2={botY + barH + 22}
            stroke={COLORS.chalk} strokeWidth={m.emph ? 4 : 2} strokeDasharray={m.emph ? undefined : "3 7"} />
        ))}
      </svg>
      {/* value above each bar end, tag inside the bar */}
      {rows.map((r) => (
        <React.Fragment key={r.tag}>
          <div style={{ position: "absolute", left: Math.max(0, x(r.end) - 240), top: r.y - 48, width: 236, textAlign: "right", fontFamily: FONT.mono, fontWeight: 800, fontSize: 38, color: r.txt, lineHeight: 1 }}>{r.label}</div>
          <div style={{ position: "absolute", left: 20, top: r.y + barH / 2 - 11, fontWeight: 800, fontSize: 17, letterSpacing: 1.6, color: COLORS.text }}>{r.tag}</div>
        </React.Fragment>
      ))}
      {/* apron labels */}
      <div style={{ position: "absolute", top: botY + barH + 24, left: Math.max(0, x(apron1) - 50) }}>
        <div style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 26, color: COLORS.chalk, lineHeight: 1 }}>$209.1M</div>
        <div style={{ fontWeight: 600, fontSize: 14, letterSpacing: 1.6, color: COLORS.subtext, marginTop: 6 }}>1ST APRON</div>
      </div>
      <div style={{ position: "absolute", top: botY + barH + 24, right: 0, textAlign: "right" }}>
        <div style={{ fontFamily: FONT.mono, fontWeight: 500, fontSize: 26, color: COLORS.tertiary, lineHeight: 1 }}>$222M</div>
        <div style={{ fontWeight: 500, fontSize: 14, letterSpacing: 1.6, color: COLORS.tertiary, marginTop: 6 }}>2ND APRON</div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- Joan's range
// The honest payoff viz, focused on the UPSIDE tiers (what you're betting on) while
// the bust base rate stays stated, not hidden. Three ascending cards climb to the
// "two-way anchor" ceiling; the 64% that never gets there is named up top.
const TONE: Record<string, { bar: string; border: string; bg: string; pct: string; desc: string }> = {
  mid: { bar: "rgba(0,132,61,0.40)", border: "rgba(243,241,233,0.14)", bg: "#0E0F0C", pct: "#FBFAF6", desc: "#C9C5B6" },
  up: { bar: "rgba(0,132,61,0.66)", border: "rgba(0,132,61,0.40)", bg: "#0E0F0C", pct: "#FBFAF6", desc: "#C9C5B6" },
  dream: { bar: "#00843D", border: "#00843D", bg: "rgba(0,132,61,0.12)", pct: "#00843D", desc: "#00843D" },
};
const JoanDev: React.FC = () => {
  const J = fd.joanDev;
  return (
    <div style={{ display: "flex", gap: 18, alignItems: "stretch", width: TRACK }}>
      {(J.tiers as any[]).map((t, i) => {
        const k = TONE[t.tone as keyof typeof TONE];
        const isDream = t.tone === "dream";
        return (
          <div key={t.label} style={{ flex: 1, border: `${isDream ? 2 : 1.5}px solid ${k.border}`, borderRadius: RADIUS, background: k.bg, padding: "28px 24px", position: "relative" }}>
            {isDream && <div style={{ position: "absolute", top: -13, right: 16, background: COLORS.good, color: "#0A0A08", fontWeight: 800, fontSize: 14, letterSpacing: 1.5, textTransform: "uppercase", padding: "4px 10px", borderRadius: 3 }}>the dream</div>}
            <div style={{ height: 9, borderRadius: 3, background: k.bar, width: `${Math.min(100, parseInt(t.pct, 10) * 5)}%`, marginBottom: 22 }} />
            <div style={{ fontFamily: FONT.mono, fontWeight: 800, fontSize: 50, color: k.pct, lineHeight: 1 }}>{t.pct}</div>
            <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 32, color: COLORS.text, marginTop: 14 }}>{t.label}</div>
            <div style={{ fontWeight: 500, fontSize: 21, color: k.desc, marginTop: 6 }}>{t.desc}</div>
          </div>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------- 1 / HOOK
// The genesis: a real comment built this door. (Featured, not narrated in first person.)
export const FdHook: React.FC = () => (
  <Frame page={1}>
    <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
      <Tag>Timberwolves</Tag>
      <Tag color={COLORS.subtext}>Hypothetical</Tag>
      <Tag color={COLORS.subtext}>From the comments</Tag>
    </div>
    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 116, lineHeight: 0.88, color: COLORS.text, letterSpacing: -1 }}>
        THE FOURTH<br />DOOR.
      </div>
      <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 44, lineHeight: 1.1, color: COLORS.text, marginTop: 26 }}>
        None of the three doors cleanly worked.<br />You built the one that grades out <span style={{ color: COLORS.alert }}>best.</span>
      </div>
      {/* the comment that opened the fourth door */}
      <div style={{ marginTop: 34 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
          <span style={{ width: 30, height: 4, background: COLORS.alert, borderRadius: 2 }} />
          <span style={{ fontWeight: 700, fontSize: 21, letterSpacing: 2.5, textTransform: "uppercase", color: COLORS.subtext }}>From the comments</span>
        </div>
        <div style={{ border: `1px solid ${COLORS.hairline}`, borderRadius: 10, background: "#fff", padding: 0, overflow: "hidden" }}>
          <Img src={staticFile("comment.jpg")} style={{ width: "100%", display: "block" }} />
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 16 }}>
          <Scrawl color={COLORS.alert} size={44} rot={-3}>you built this one</Scrawl>
        </div>
      </div>
    </div>
  </Frame>
);

// ---------------------------------------------------------------- 2 / THE PLAN
const SectionLabel: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ fontWeight: 700, fontSize: 18, letterSpacing: 2.5, textTransform: "uppercase", color: COLORS.tertiary, marginBottom: 12 }}>{children}</div>
);
const RestRow: React.FC<{ verb: string; sub?: string; text: string; note: string; accent?: boolean }> = ({ verb, sub, text, note, accent }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "13px 0", borderBottom: `1px solid ${COLORS.hairlineSoft}` }}>
    <span style={{ width: 138, flexShrink: 0 }}>
      <span style={{ fontWeight: 800, fontSize: 19, letterSpacing: 1.5, textTransform: "uppercase", color: accent ? COLORS.alert : COLORS.subtext }}>{verb}</span>
      {sub && <span style={{ fontWeight: 600, fontSize: 15, color: COLORS.tertiary, marginLeft: 6 }}>{sub}</span>}
    </span>
    <span style={{ flex: 1, fontFamily: FONT.display, fontWeight: 500, fontSize: 29, color: COLORS.text, lineHeight: 1.05 }}>{text}</span>
    <Scrawl color={accent ? COLORS.alert : COLORS.tertiary} size={26} rot={-1}>{note}</Scrawl>
  </div>
);

export const FdPlan: React.FC = () => (
  <Frame kicker="The plan" page={2}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
      <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 56, lineHeight: 1.0, color: COLORS.text }}>
        One real trade.<br /><span style={{ color: COLORS.alert }}>The rest is patience.</span>
      </div>
      <div style={{ paddingTop: 8 }}><Scrawl color={COLORS.alert} size={44} rot={4}>keep Gobert?</Scrawl></div>
    </div>

    {/* THE ONE MOVE — the hero swap */}
    <div style={{ marginTop: 26, border: `1.5px solid rgba(0,132,61,0.42)`, borderRadius: RADIUS, background: "rgba(0,132,61,0.07)", padding: "22px 26px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <span style={{ fontWeight: 800, fontSize: 19, letterSpacing: 2.5, textTransform: "uppercase", color: COLORS.alert }}>The one move that matters</span>
        <Scrawl color={COLORS.subtext} size={28} rot={-2}>Donte = the salary matcher</Scrawl>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 15, letterSpacing: 1.5, color: COLORS.tertiary, marginBottom: 4 }}>OUT</div>
          <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 33, color: COLORS.subtext, lineHeight: 1.14 }}>
            Randle <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 23 }}>$33.3M</span><br />
            DiVincenzo <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 23 }}>$12.5M</span>
          </div>
        </div>
        <span style={{ fontFamily: FONT.display, fontWeight: 400, fontSize: 58, color: COLORS.alert }}>&rarr;</span>
        <div style={{ flex: 1.05 }}>
          <div style={{ fontWeight: 700, fontSize: 15, letterSpacing: 1.5, color: COLORS.alert, marginBottom: 4 }}>IN</div>
          <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 46, color: COLORS.alert, lineHeight: 1 }}>Jrue Holiday</div>
          <div style={{ fontWeight: 500, fontSize: 21, color: COLORS.subtext, marginTop: 5 }}>lead guard + elite defense</div>
        </div>
      </div>
    </div>

    {/* ...and barely touch the rest */}
    <div style={{ marginTop: 24, position: "relative" }}>
      <SectionLabel>&hellip; and barely touch the rest</SectionLabel>
      <RestRow verb="Keep" text="Edwards, McDaniels, Naz, Gobert" note="the whole core" />
      <RestRow verb="Draft" sub="No. 28" text="Christian Anderson" note="basically free" />
      <RestRow verb="Sign" sub="MLE" text="Kennard / Middleton" note="the room Randle frees" />
      <RestRow verb="Re-sign" text="Ayo Dosunmu" note="hold the guard" />
      <RestRow verb="Develop" text="Joan Beringer + Shannon" note="the bet" accent />
      {/* honest footnote on the draft + a hand-drawn arrow pointing up to the Draft row */}
      <div style={{ marginTop: 18, marginLeft: 30 }}>
        <Scrawl color={COLORS.subtext} size={25} rot={-1}>Momcilovic pulled out of the draft, so Anderson</Scrawl>
      </div>
      <svg width={TRACK} height={420} style={{ position: "absolute", left: 0, top: 0, overflow: "visible", pointerEvents: "none" }}>
        {/* tail starts at the footnote (right of all row text) and rises up the clear channel to the Draft row */}
        <path d="M 588 352 C 632 258, 548 172, 420 122" stroke={COLORS.subtext} strokeWidth={4} fill="none" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M 420 122 l 26 5" stroke={COLORS.subtext} strokeWidth={4} fill="none" strokeLinecap="round" />
        <path d="M 420 122 l 6 26" stroke={COLORS.subtext} strokeWidth={4} fill="none" strokeLinecap="round" />
      </svg>
    </div>
    <div style={{ flex: 1 }} />
    {/* hand-written sign-off (the font carries the analyst-aside cue; no label needed) */}
    <div style={{ paddingTop: 8 }}>
      <Scrawl color={COLORS.alert} size={40} rot={-2}>Love this. It bets on<br />the guys we already have.</Scrawl>
    </div>
  </Frame>
);

// ---------------------------------------------------------------- 3 / THE CAP (the tier drop)
export const FdCap: React.FC = () => (
  <Frame kicker="The setup" page={3}>
    {/* one vertically-centered block: balanced margins, no bottom void */}
    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
        <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 60, lineHeight: 1.0, color: COLORS.text }}>
          Move Randle, and you<br /><span style={{ color: COLORS.alert }}>drop a whole tier.</span>
        </div>
        <div style={{ paddingTop: 10 }}><Scrawl color={COLORS.alert} size={34} rot={4}>the tier is the prize</Scrawl></div>
      </div>
      <div style={{ fontWeight: 500, fontSize: 28, lineHeight: 1.4, color: COLORS.subtext, marginTop: 22 }}>
        Randle and DiVincenzo for Jrue takes about <span style={{ fontFamily: FONT.mono, fontWeight: 700, color: COLORS.text }}>{fd.cap.shed}</span> off the books. Keep him and you&rsquo;re jammed in the second-apron zone: frozen picks, no aggregating, hard-cap handcuffs. Trade him and you&rsquo;re back under the first apron, flexible again. The shooter is just a normal <span style={{ fontFamily: FONT.mono, fontWeight: 700, color: COLORS.text }}>{fd.cap.shooter}</span> add on top.
      </div>
      <div style={{ marginTop: 56 }}>
        <CapMeter />
      </div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 24 }}>
        <Scrawl color={COLORS.good} size={34} rot={-2}>flexibility, not a splash</Scrawl>
      </div>
    </div>
  </Frame>
);

// ---------------------------------------------------------------- 4 / THE VERDICT
export const FdVerdict: React.FC = () => (
  <Frame kicker="Trade model &middot; the verdict" page={4}>
    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ fontWeight: 800, fontSize: 46, letterSpacing: 7, textTransform: "uppercase", color: COLORS.subtext }}>Title odds</div>
      <div style={{ display: "flex", alignItems: "center", gap: 30, marginTop: 6 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 20 }}>
          <span style={{ fontFamily: FONT.mono, fontWeight: 800, fontSize: 184, color: COLORS.alert, lineHeight: 0.84, letterSpacing: -5 }}>{fd.verdict.delta}</span>
          <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 56, color: COLORS.subtext }}>{fd.verdict.unit}</span>
        </div>
        <Scrawl color={COLORS.subtext} size={32} rot={-4}>no hopium,<br />just the math</Scrawl>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 16 }}>
        <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 46, color: COLORS.subtext }}>{fd.verdict.from}</span>
        <span style={{ fontFamily: FONT.display, fontSize: 44, color: COLORS.tertiary }}>&rarr;</span>
        <span style={{ fontFamily: FONT.mono, fontWeight: 800, fontSize: 46, color: COLORS.alert }}>{fd.verdict.to}</span>
        <span style={{ fontWeight: 600, fontSize: 23, letterSpacing: 1, textTransform: "uppercase", color: COLORS.tertiary, marginLeft: 10 }}>&middot; my model says</span>
      </div>
      <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 44, lineHeight: 1.12, color: COLORS.text, marginTop: 46 }}>
        Real, and small. <span style={{ color: COLORS.alert }}>The best realistic move on the board.</span>
      </div>
      <div style={{ marginTop: 28 }}>
        <Scrawl color={COLORS.alert} size={42} rot={-2}>the boring one wins</Scrawl>
      </div>
    </div>
  </Frame>
);

// ---------------------------------------------------------------- 5 / THE BET (where Joan could go)
export const FdTakeaway: React.FC = () => (
  <Frame kicker="The bet" page={5}>
    {/* one vertically-centered block: even margins top and bottom, no mid-slide void */}
    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 58, lineHeight: 1.0, color: COLORS.text }}>
        You can&rsquo;t buy your way up.<br />So you <span style={{ color: COLORS.alert }}>bet on the kid.</span>
      </div>
      {/* the honest base rate, then reframe it as the point */}
      <div style={{ display: "flex", alignItems: "stretch", gap: 16, marginTop: 26 }}>
        <div style={{ width: 4, background: COLORS.hairline, borderRadius: 2, flexShrink: 0 }} />
        <span style={{ fontWeight: 500, fontSize: 26, color: COLORS.subtext, lineHeight: 1.32 }}>
          The model is clear-eyed: <span style={{ fontFamily: FONT.mono, fontWeight: 700, color: COLORS.text }}>{fd.joanDev.bustPct}</span> of kids like Joan never become anything. That&rsquo;s not the catch. It&rsquo;s the whole point of a bet.
        </span>
      </div>
      <div style={{ marginTop: 50, display: "flex", alignItems: "baseline", justifyContent: "space-between" }}>
        <span style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 36, color: COLORS.text }}>{fd.joanDev.title}</span>
        <span style={{ fontWeight: 500, fontSize: 22, color: COLORS.tertiary }}>{fd.joanDev.sub}</span>
      </div>
      <div style={{ marginTop: 24 }}>
        <JoanDev />
      </div>
      {/* the belief payoff */}
      <div style={{ marginTop: 50, borderTop: `1px solid ${COLORS.hairline}`, paddingTop: 26, display: "flex", alignItems: "center", gap: 18 }}>
        <Scrawl color={COLORS.alert} size={40} rot={-3}>bet on the kid</Scrawl>
        <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 32, color: COLORS.text, lineHeight: 1.16 }}>
          You&rsquo;re buying that <span style={{ color: COLORS.alert }}>6%</span> where he&rsquo;s the next great two-way center. That&rsquo;s the whole dream.
        </span>
      </div>
    </div>
  </Frame>
);

// ---------------------------------------------------------------- 6 / CTA
export const FdCTA: React.FC = () => (
  <Frame page={6}>
    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 92, lineHeight: 0.98, color: COLORS.text, letterSpacing: -0.5 }}>
        Your turn.<br /><span style={{ color: COLORS.alert }}>For real this time.</span>
      </div>
      <div style={{ marginTop: 46 }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
          <Scrawl color={COLORS.alert} size={48} rot={-2}>&darr;</Scrawl>
          <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 40, color: COLORS.text, lineHeight: 1.18 }}>
            What&rsquo;s your offseason? Drop the whole thing: <span style={{ color: COLORS.alert }}>trades, draft, signings</span>, and I&rsquo;ll run it through the model.
          </span>
        </div>
        <div style={{ fontWeight: 500, fontSize: 30, color: COLORS.subtext, lineHeight: 1.3, marginTop: 18, marginLeft: 64 }}>
          The sharpest one gets its own post.
        </div>
      </div>
    </div>
    <div style={{ fontWeight: 500, fontSize: 22, color: COLORS.tertiary, letterSpacing: 0.5 }}>
      My model says. These are estimates.
    </div>
  </Frame>
);
