import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { Background } from "./Background";
import { WIDTH, HEIGHT, SAFE, COLORS, FONT, RADIUS, CAP } from "./config";
import data from "./doors.json";

const TOTAL = 7;
const TRACK = WIDTH - SAFE.x * 2; // 912

// ----------------------------------------------------------------------------
// Shared editorial chrome
// ----------------------------------------------------------------------------
const Frame: React.FC<{ kicker?: string; page: number; children: React.ReactNode }> = ({ kicker, page, children }) => (
  <AbsoluteFill style={{ fontFamily: FONT.sans }}>
    <Background />
    <AbsoluteFill
      style={{ paddingTop: SAFE.top, paddingBottom: SAFE.bottom, paddingLeft: SAFE.x, paddingRight: SAFE.x, display: "flex", flexDirection: "column" }}
    >
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

const Tag: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color }) => (
  <span style={{ display: "inline-block", fontWeight: 700, fontSize: FONT.tag, letterSpacing: 2, textTransform: "uppercase", color: color ?? COLORS.alert, border: `1.5px solid ${color ?? COLORS.alert}`, borderRadius: RADIUS, padding: "8px 14px" }}>
    {children}
  </span>
);

// ----------------------------------------------------------------------------
// The cap meter (signature). Horizontal, $150M -> $225M. Solid bar = resulting
// cap; hatched ghost = books after re-signing Dosunmu; the part over the first
// apron renders in apron-break red. That red is the crossing.
// ----------------------------------------------------------------------------
const CapMeter: React.FC<{
  lands: number; landsLabel: string; landNote: string;
  ghost: number | null; ghostLabel?: string; landColor?: string;
}> = ({ lands, landsLabel, landNote, ghost, ghostLabel, landColor }) => {
  const { lo, hi, tax, apron1, apron2 } = CAP;
  const x = (v: number) => ((v - lo) / (hi - lo)) * TRACK;
  const railY = 70, railH = 48, H = 210;
  const apronX = x(apron1);
  const landX = x(lands);
  const gX = ghost != null ? x(ghost) : landX;
  const bar = landColor ?? COLORS.good;
  const crosses = ghost != null && gX > apronX;

  const markers = [
    { v: tax, label: "TAX", money: "$201M", emph: false },
    { v: apron1, label: "1ST APRON", money: "$209.1M", emph: true },
    { v: apron2, label: "2ND APRON", money: "$222M", emph: false },
  ];

  return (
    <div style={{ position: "relative", width: TRACK, height: H }}>
      <svg width={TRACK} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
        <defs>
          <pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="9" height="9" fill={COLORS.hairlineSoft} />
            <line x1="0" y1="0" x2="0" y2="9" stroke={COLORS.tertiary} strokeWidth="3" />
          </pattern>
          {/* over-the-apron = a DENSE CROSS-hatch: a third, distinct texture (vs the solid bar and the
              single-diagonal ghost), so the alert zone reads by pattern even in grayscale, not by hue alone */}
          <pattern id="hatchRed" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="7" height="7" fill={COLORS.apronBreakDim} />
            <line x1="0" y1="0" x2="0" y2="7" stroke={COLORS.apronBreak} strokeWidth="2.6" />
            <line x1="0" y1="0" x2="7" y2="0" stroke={COLORS.apronBreak} strokeWidth="2.6" />
          </pattern>
        </defs>

        {/* rail */}
        <rect x={0} y={railY} width={TRACK} height={railH} rx={RADIUS} fill="rgba(255,255,255,0.045)" />

        {/* ghost extension: hatched after re-signing Dosunmu; the part over the first apron is red cross-hatch */}
        {ghost != null && gX > landX && (
          <>
            <rect x={landX} y={railY} width={Math.max(0, Math.min(gX, apronX) - landX)} height={railH} fill="url(#hatch)" />
            {crosses && <rect x={Math.max(landX, apronX)} y={railY} width={gX - Math.max(landX, apronX)} height={railH} fill="url(#hatchRed)" />}
            {crosses && gX - Math.max(landX, apronX) > 66 && (
              <text x={(Math.max(landX, apronX) + gX) / 2} y={railY + railH / 2 + 6} textAnchor="middle" fontFamily={FONT.sans} fontWeight="800" fontSize="17" letterSpacing="1.5" fill={COLORS.text}>OVER</text>
            )}
          </>
        )}

        {/* solid bar = the resulting cap number, with a bright end tick */}
        <rect x={0} y={railY} width={landX} height={railH} rx={RADIUS} fill={bar} />
        <rect x={landX - 3} y={railY - 6} width={6} height={railH + 12} rx={2} fill={bar} />

        {/* marker lines (first apron emphasized) */}
        {markers.map((m) => (
          <line key={m.label} x1={x(m.v)} y1={railY - 18} x2={x(m.v)} y2={railY + railH + 16}
            stroke={m.emph ? COLORS.chalk : COLORS.tertiary} strokeWidth={m.emph ? 3.5 : 1.6} strokeDasharray={m.emph ? undefined : "2 6"} />
        ))}
      </svg>

      {/* resulting-cap callout (compact), above the bar end */}
      <div style={{ position: "absolute", left: Math.min(landX - 4, TRACK - 200), top: 2, width: 240 }}>
        <div style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 46, color: bar, lineHeight: 1 }}>{landsLabel}</div>
        <div style={{ fontWeight: 500, fontSize: 20, color: COLORS.subtext, marginTop: 4 }}>{landNote}</div>
      </div>

      {/* marker labels: only the first-apron line (the hero) and the tax keep a name; the 2nd apron is a
          value pinned to the right edge, so the busy right corner around the apron reads clean */}
      {markers.map((m) => {
        const isA2 = m.v === apron2;
        return (
          <div key={m.label} style={{ position: "absolute", top: railY + railH + 22, textAlign: isA2 ? "right" : "left",
            left: isA2 ? undefined : Math.min(Math.max(0, x(m.v) - 44), TRACK - 150), right: isA2 ? 0 : undefined }}>
            <div style={{ fontFamily: FONT.mono, fontWeight: m.emph ? 700 : 500, fontSize: m.emph ? 29 : 22, color: m.emph ? COLORS.chalk : COLORS.tertiary, lineHeight: 1 }}>{m.money}</div>
            {!isA2 && <div style={{ fontWeight: m.emph ? 600 : 500, fontSize: m.emph ? 16 : 14, letterSpacing: 1.8, color: m.emph ? COLORS.subtext : COLORS.tertiary, marginTop: 6 }}>{m.label}</div>}
          </div>
        );
      })}
    </div>
  );
};

const LegItem: React.FC<{ color: string; label: string; hatch?: boolean; cross?: boolean }> = ({ color, label, hatch, cross }) => {
  const bg = cross
    ? `repeating-linear-gradient(45deg, ${color} 0 2px, transparent 2px 6px), repeating-linear-gradient(-45deg, ${color} 0 2px, transparent 2px 6px)`
    : hatch
      ? `repeating-linear-gradient(45deg, ${color} 0 3px, transparent 3px 9px)`
      : color;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
      <span style={{ width: 26, height: 16, borderRadius: 3, background: bg, border: (hatch || cross) ? `1px solid ${color}` : "none" }} />
      <span style={{ fontWeight: 500, fontSize: 20, color: COLORS.subtext }}>{label}</span>
    </div>
  );
};

const CapLegend: React.FC<{ withGhost?: boolean; barLabel?: string }> = ({ withGhost = true, barLabel = "the trade" }) => (
  <div style={{ display: "flex", gap: 22, alignItems: "center" }}>
    <LegItem color={COLORS.good} label={barLabel} />
    {withGhost && <LegItem color={COLORS.tertiary} label="re-sign Ayo" hatch />}
    {withGhost && <LegItem color={COLORS.apronBreak} label="over the apron" cross />}
  </div>
);

// ----------------------------------------------------------------------------
// 1. HOOK
// ----------------------------------------------------------------------------
export const Hook: React.FC = () => (
  <Frame page={1}>
    <div style={{ display: "flex", gap: 12, marginBottom: 30 }}>
      <Tag>Timberwolves</Tag>
      <Tag color={COLORS.subtext}>Hypothetical</Tag>
      <Tag color={COLORS.subtext}>Trade idea</Tag>
    </div>
    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT.sans, fontWeight: 700, fontSize: FONT.tag, letterSpacing: 3, textTransform: "uppercase", color: COLORS.tertiary, marginBottom: 22 }}>
        <span style={{ color: COLORS.subtext }}>Timberwolves</span> &middot; Trade model &middot; Draft night
      </div>
      <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 140, lineHeight: 0.9, color: COLORS.text, letterSpacing: -1 }}>
        THREE<br />DOORS.
      </div>
      <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 54, lineHeight: 1.06, color: COLORS.text, marginTop: 34 }}>
        The boldest one grades out <span style={{ color: COLORS.alert }}>the worst.</span>
      </div>
      <div style={{ display: "flex", gap: 24, marginTop: 44, fontFamily: FONT.display, fontWeight: 600, fontSize: 32, letterSpacing: 1, color: COLORS.chalk }}>
        <span>SWING</span><span style={{ color: COLORS.tertiary }}>/</span><span>FLIP</span><span style={{ color: COLORS.tertiary }}>/</span><span>STOCKPILE</span>
      </div>
      <div style={{ marginTop: 22 }}>
        <span style={{ fontFamily: FONT.scrawl, fontSize: 40, color: COLORS.alert, transform: "rotate(-3deg)", display: "inline-block" }}>the cap decides</span>
      </div>
    </div>
  </Frame>
);

// ----------------------------------------------------------------------------
// 2. SETUP (teaches the cap meter)
// ----------------------------------------------------------------------------
export const Setup: React.FC = () => (
  <Frame kicker="The setup" page={2}>
    <div style={{ flex: 0.85 }} />
    <div style={{ display: "flex", alignItems: "baseline", gap: 20, flexWrap: "wrap" }}>
      <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 64, lineHeight: 1.02, color: COLORS.text }}>
        The rare contender <span style={{ color: COLORS.alert }}>with room</span>.
      </div>
      <span style={{ fontFamily: FONT.scrawl, fontSize: 44, color: COLORS.apronBreak, transform: "rotate(-3deg)", whiteSpace: "nowrap" }}>do we really??</span>
    </div>

    <div style={{ marginTop: 38 }}>
      <CapMeter lands={data.baseline.cap} landsLabel={data.baseline.capLabel} landNote="today, under the tax" ghost={209.6} />
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 4 }}>
        <CapLegend barLabel="today" />
        <span style={{ fontFamily: FONT.scrawl, fontSize: 32, color: COLORS.apronBreak, transform: "rotate(-2deg)", whiteSpace: "nowrap" }}>Ayo lands us right here</span>
      </div>
    </div>

    {/* The Ayo context: re-signing the starting guard alone pushes MIN to the first apron */}
    <div style={{ marginTop: 34, display: "flex", alignItems: "center", gap: 18, padding: "22px 26px", border: `1px solid ${COLORS.hairline}`, borderRadius: RADIUS, background: COLORS.inset }}>
      <span style={{ fontFamily: FONT.scrawl, fontSize: 38, color: COLORS.alert, transform: "rotate(-3deg)", whiteSpace: "nowrap" }}>keep Ayo?</span>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 36, color: COLORS.text }}>
          Re-sign Ayo Dosunmu <span style={{ fontFamily: FONT.mono, fontWeight: 700, color: COLORS.subtext }}>{data.dosunmu.salaryLabel}</span>
        </span>
        <span style={{ fontWeight: 500, fontSize: 24, color: COLORS.subtext }}>the starting guard, and that alone is the first apron</span>
      </div>
    </div>

    <div style={{ flex: 0.55 }} />
  </Frame>
);

// ----------------------------------------------------------------------------
// 3 to 5. THE DOORS
// ----------------------------------------------------------------------------
const TradeLine: React.FC<{ label: string; value: string; accent?: boolean }> = ({ label, value, accent }) => (
  <div style={{ display: "flex", alignItems: "baseline", gap: 16 }}>
    <span style={{ width: 96, fontWeight: 800, fontSize: 21, letterSpacing: 2, textTransform: "uppercase", color: accent ? COLORS.alert : COLORS.tertiary }}>{label}</span>
    <span style={{ fontFamily: FONT.display, fontWeight: 500, fontSize: 33, color: COLORS.text }}>{value}</span>
  </div>
);

const TitleBlock: React.FC<{ title: any }> = ({ title }) => {
  if (title.kind === "range") {
    const cell = (k: string, v: string, hot?: boolean) => (
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, fontSize: 18, letterSpacing: 1.5, textTransform: "uppercase", color: COLORS.tertiary }}>{k}</div>
        <div style={{ fontFamily: FONT.mono, fontWeight: 800, fontSize: 46, color: hot ? COLORS.text : COLORS.subtext, marginTop: 4 }}>{v}</div>
      </div>
    );
    return (
      <div>
        <div style={{ fontWeight: 700, fontSize: 22, letterSpacing: 2, textTransform: "uppercase", color: COLORS.tertiary, marginBottom: 12 }}>Trade model &middot; title odds, a range</div>
        <div style={{ display: "flex", gap: 14, alignItems: "flex-end" }}>
          {cell("Box", title.box)}{cell("Consensus", title.consensus, true)}{cell("RAPM", title.rapm)}
        </div>
        <div style={{ fontWeight: 600, fontSize: 23, color: COLORS.subtext, marginTop: 12 }}>
          Even the trade model can&rsquo;t agree. {title.anchorLabel}, {title.riskLabel}.
        </div>
      </div>
    );
  }
  return (
    <div>
      <div style={{ fontWeight: 700, fontSize: 22, letterSpacing: 2, textTransform: "uppercase", color: COLORS.tertiary, marginBottom: 6 }}>Trade model &middot; title odds</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 18 }}>
        <span style={{ fontFamily: FONT.mono, fontWeight: 800, fontSize: 100, color: COLORS.text, lineHeight: 0.9 }}>{title.headline}</span>
        <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 40, color: COLORS.subtext }}>{title.unit}</span>
        <span style={{ fontWeight: 600, fontSize: 24, color: COLORS.tertiary }}>({title.anchorLabel})</span>
      </div>
    </div>
  );
};

const DoorSlide: React.FC<{ d: any }> = ({ d }) => (
  <Frame kicker={d.kicker} page={d.page}>
    <div style={{ display: "flex", alignItems: "baseline", gap: 16, flexWrap: "wrap" }}>
      <span style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 58, color: COLORS.text, letterSpacing: -0.5 }}>{d.name}</span>
      {d.acceptTag && <Tag color={COLORS.tertiary}>{d.acceptTag}</Tag>}
    </div>

    <div style={{ display: "flex", flexDirection: "column", gap: 9, marginTop: 22 }}>
      <TradeLine label="Send" value={d.send} />
      <TradeLine label="Get" value={d.get} accent />
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 2 }}>
        <span style={{ fontWeight: 800, fontSize: 18, letterSpacing: 1.5, color: COLORS.apronBreak, border: `1.5px solid ${COLORS.apronBreak}`, borderRadius: RADIUS, padding: "5px 10px" }}>BLOCKED</span>
        <span style={{ fontFamily: FONT.sans, fontWeight: 500, fontSize: 24, color: COLORS.subtext }}>{d.legs[1].text}.</span>
      </div>
    </div>

    <div style={{ marginTop: 22 }}>
      <CapMeter lands={d.cap.lands} landsLabel={d.cap.landsLabel} landNote={d.cap.landNote} ghost={d.cap.ghost} />
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16, marginTop: 4 }}>
        <CapLegend withGhost={d.cap.ghost != null} />
        <span style={{ fontFamily: FONT.scrawl, fontSize: 32, color: d.cap.crosses ? COLORS.apronBreak : COLORS.chalk, transform: "rotate(-2deg)", whiteSpace: "nowrap" }}>{d.scrawl}</span>
      </div>
    </div>

    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginTop: 18 }}>
      <TitleBlock title={d.title} />
      <div style={{ textAlign: "right" }}>
        <div style={{ fontWeight: 700, fontSize: 19, letterSpacing: 1.5, textTransform: "uppercase", color: COLORS.tertiary }}>Capital</div>
        <div style={{ fontFamily: FONT.display, fontWeight: 500, fontSize: 28, color: COLORS.text, marginTop: 2 }}>{d.capital}</div>
        <div style={{ fontWeight: 600, fontSize: 23, color: d.id === "stockpile" ? COLORS.alert : COLORS.subtext }}>{d.room}</div>
        <div style={{ fontWeight: 600, fontSize: 19, color: COLORS.tertiary, marginTop: 8 }}>trade model: {d.acceptShort}</div>
      </div>
    </div>

    <div style={{ flex: 1 }} />
    <div style={{ borderTop: `1px solid ${COLORS.hairline}`, paddingTop: 16 }}>
      <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 38, color: COLORS.text, lineHeight: 1.12 }}>{d.catch}</span>
    </div>
  </Frame>
);

export const Swing: React.FC = () => <DoorSlide d={data.doors[0]} />;
export const Flip: React.FC = () => <DoorSlide d={data.doors[1]} />;
export const Stockpile: React.FC = () => <DoorSlide d={data.doors[2]} />;

// ----------------------------------------------------------------------------
// 6. THE PLANE (future vs win-now)
// ----------------------------------------------------------------------------
const QLabel: React.FC<{ x: number; y: number; text: string; color: string; right?: boolean }> = ({ x, y, text, color, right }) => (
  <div style={{ position: "absolute", left: x, top: y, fontWeight: 800, fontSize: 16, letterSpacing: 1.4, color, opacity: 0.85, textTransform: "uppercase", textAlign: right ? "right" : "left" }}>{text}</div>
);

export const Plane: React.FC = () => {
  const W = TRACK, H = 712;
  const x0 = 64, x1 = W - 18, yT = 12, yB = H - 50;     // field bounds
  const fieldH = yB - yT;
  const xlo = -2.2, xhi = 2.6, ylo = 0, yhi = 5;
  const px = (v: number) => x0 + ((v - xlo) / (xhi - xlo)) * (x1 - x0);
  const py = (v: number) => yT + (1 - (v - ylo) / (yhi - ylo)) * fieldH;
  const midX = px(0), midY = py(2.6);
  const pts = (data.plane as any[]);
  const colorFor = (id: string) => (id === "swing" ? COLORS.apronBreak : id === "flip" ? COLORS.chalk : COLORS.good);
  const dreamX = px(1.45), dreamY = py(3.85);
  return (
    <Frame kicker="The payoff" page={6}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
        <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 58, lineHeight: 1.0, color: COLORS.text }}>
          Win now, or the future.<br /><span style={{ color: COLORS.alert }}>Nobody gets both.</span>
        </div>
        <Img src={staticFile("logo.png")} style={{ width: 96, height: 96, objectFit: "contain", flexShrink: 0 }} />
      </div>

      <div style={{ position: "relative", width: W, height: H, marginTop: 8 }}>
        <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
          {/* the "dream" quadrant (win now AND keep the future): faint green wash */}
          <rect x={midX} y={yT} width={x1 - midX} height={midY - yT} fill="rgba(0,132,61,0.06)" />
          {/* quadrant dividers */}
          <line x1={midX} y1={yT} x2={midX} y2={yB} stroke={COLORS.hairlineSoft} strokeWidth={2} strokeDasharray="3 8" />
          <line x1={x0} y1={midY} x2={x1} y2={midY} stroke={COLORS.hairlineSoft} strokeWidth={2} strokeDasharray="3 8" />
          {/* axes */}
          <line x1={x0} y1={yB} x2={x1} y2={yB} stroke={COLORS.hairline} strokeWidth={2.5} />
          <line x1={x0} y1={yT} x2={x0} y2={yB} stroke={COLORS.hairline} strokeWidth={2.5} />
          {/* the empty-dream ghost ring */}
          <circle cx={dreamX} cy={dreamY} r={52} fill="none" stroke={COLORS.tertiary} strokeWidth={2} strokeDasharray="5 7" />
          {/* door tokens with a soft halo */}
          {pts.map((p) => (
            <g key={p.id}>
              <circle cx={px(p.winNow)} cy={py(p.future)} r={30} fill={colorFor(p.id)} opacity={0.16} />
              <circle cx={px(p.winNow)} cy={py(p.future)} r={15} fill={colorFor(p.id)} />
            </g>
          ))}
        </svg>

        {/* quadrant corner labels */}
        <QLabel x={midX + 16} y={yT + 8} text="win now + keep it" color={COLORS.good} />
        <QLabel x={x0 + 10} y={yT + 8} text="bank the future" color={COLORS.tertiary} />
        <QLabel x={x0 + 10} y={midY + 12} text="give up both" color={COLORS.tertiary} />
        <QLabel x={midX + 16} y={midY + 12} text="spend it all" color={COLORS.tertiary} />

        {/* the empty door (the payoff) */}
        <div style={{ position: "absolute", left: dreamX - 60, top: dreamY - 16, width: 120, textAlign: "center", fontFamily: FONT.display, fontWeight: 700, fontSize: 26, letterSpacing: 2, color: COLORS.tertiary }}>EMPTY</div>
        <div style={{ position: "absolute", left: dreamX - 188, top: dreamY - 96, fontFamily: FONT.scrawl, fontSize: 29, color: COLORS.chalk, transform: "rotate(-3deg)", whiteSpace: "nowrap" }}>the door fans dream of</div>

        {/* door labels: name + stat */}
        {pts.map((p) => (
          <div key={p.id} style={{ position: "absolute", left: Math.min(px(p.winNow) + 26, W - 220), top: py(p.future) - 28 }}>
            <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 36, color: colorFor(p.id), letterSpacing: 0.5, lineHeight: 1 }}>{p.label}</div>
            <div style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 21, color: COLORS.subtext, marginTop: 4 }}>{p.stat}</div>
          </div>
        ))}

        {/* the irony: the move fans want most sits in the worst corner */}
        <div style={{ position: "absolute", left: Math.max(8, px(-0.74) - 14), top: py(0.8) + 36, fontFamily: FONT.scrawl, fontSize: 30, color: COLORS.apronBreak, transform: "rotate(-3deg)", whiteSpace: "nowrap" }}>fans want this one</div>

        {/* axis labels */}
        <div style={{ position: "absolute", left: x1 - 132, top: yB + 14, fontWeight: 700, fontSize: 20, letterSpacing: 1, color: COLORS.tertiary }}>WIN NOW &rarr;</div>
        <div style={{ position: "absolute", left: -4, top: yT + fieldH / 2 - 50, fontWeight: 700, fontSize: 20, letterSpacing: 1, color: COLORS.tertiary, writingMode: "vertical-rl", transform: "rotate(180deg)" }}>FUTURE &rarr;</div>
      </div>
      <div style={{ flex: 1, minHeight: 14 }} />
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <span style={{ fontFamily: FONT.scrawl, fontSize: 36, color: COLORS.alert, transform: "rotate(-2deg)", whiteSpace: "nowrap" }}>your move</span>
        <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 33, color: COLORS.text, lineHeight: 1.12 }}><span style={{ color: COLORS.alert }}>Comment</span> a trade that wins now AND keeps the future.</span>
      </div>
    </Frame>
  );
};

// ----------------------------------------------------------------------------
// 7. CTA
// ----------------------------------------------------------------------------
export const CTA: React.FC = () => (
  <Frame page={7}>
    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 84, lineHeight: 1.0, color: COLORS.text, letterSpacing: -0.5 }}>
        Which door would you open, <span style={{ color: COLORS.alert }}>knowing the catch?</span>
      </div>
      <div style={{ display: "flex", gap: 32, marginTop: 52, fontFamily: FONT.display, fontWeight: 700, fontSize: 42, color: COLORS.text }}>
        <Dot c={COLORS.apronBreak} t="SWING" />
        <Dot c={COLORS.chalk} t="FLIP" />
        <Dot c={COLORS.good} t="STOCKPILE" />
      </div>
      <div style={{ marginTop: 58 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ fontFamily: FONT.scrawl, fontSize: 48, color: COLORS.alert, transform: "rotate(-2deg)" }}>&darr;</span>
          <span style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 46, color: COLORS.text, letterSpacing: -0.3 }}>
            <span style={{ color: COLORS.alert }}>Comment</span> your trade.
          </span>
        </div>
        <div style={{ fontWeight: 500, fontSize: 29, color: COLORS.subtext, lineHeight: 1.3, marginTop: 14, marginLeft: 64 }}>
          I&rsquo;ll run it through the trade model, and the sharpest one gets its own post next.
        </div>
      </div>
    </div>
  </Frame>
);

const Dot: React.FC<{ c: string; t: string }> = ({ c, t }) => (
  <span style={{ display: "flex", alignItems: "center", gap: 12 }}>
    <span style={{ width: 16, height: 16, borderRadius: 16, background: c }} />
    {t}
  </span>
);
