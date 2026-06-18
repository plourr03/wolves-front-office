import React from "react";
import { AbsoluteFill } from "remotion";
import { Background } from "./Background";
import { WIDTH, HEIGHT, SAFE, COLORS, FONT, RADIUS } from "./config";
import deal from "./deal.json";

// ----------------------------------------------------------------------------
// Shared editorial chrome: left spine, tracked kicker, page indicator, wordmark.
// ----------------------------------------------------------------------------
const Frame: React.FC<{ kicker?: string; page: number; children: React.ReactNode }> = ({
  kicker,
  page,
  children,
}) => (
  <AbsoluteFill style={{ fontFamily: FONT.sans }}>
    <Background />
    <AbsoluteFill
      style={{
        paddingTop: SAFE.top,
        paddingBottom: SAFE.bottom,
        paddingLeft: SAFE.x,
        paddingRight: SAFE.x,
        display: "flex",
        flexDirection: "column",
      }}
    >
      {kicker !== undefined && (
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 26 }}>
          <div style={{ width: 46, height: 5, background: COLORS.alert, borderRadius: RADIUS }} />
          <div
            style={{
              fontWeight: 700,
              fontSize: FONT.kicker,
              letterSpacing: 4,
              textTransform: "uppercase",
              color: COLORS.subtext,
            }}
          >
            {kicker}
          </div>
        </div>
      )}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>{children}</div>
      <Footer page={page} />
    </AbsoluteFill>
  </AbsoluteFill>
);

const Footer: React.FC<{ page: number }> = ({ page }) => (
  <div
    style={{
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      borderTop: `1px solid ${COLORS.hairline}`,
      paddingTop: 20,
      marginTop: 18,
    }}
  >
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <div style={{ width: 12, height: 12, borderRadius: 12, background: COLORS.good }} />
      <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: FONT.wordmark, letterSpacing: 1, color: COLORS.text }}>
        WOLVES TO A T
      </span>
    </div>
    <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: FONT.page, color: COLORS.tertiary }}>{page} / 6</span>
  </div>
);

const Tag: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color }) => (
  <span
    style={{
      display: "inline-block",
      fontWeight: 700,
      fontSize: FONT.tag,
      letterSpacing: 2,
      textTransform: "uppercase",
      color: color ?? COLORS.alert,
      border: `1.5px solid ${color ?? COLORS.alert}`,
      borderRadius: RADIUS,
      padding: "8px 14px",
    }}
  >
    {children}
  </span>
);

// ----------------------------------------------------------------------------
// 1. THE HOOK  (hot take: a spicy verdict up top)
// ----------------------------------------------------------------------------
export const Hook: React.FC = () => (
  <Frame page={1}>
    <div style={{ display: "flex", gap: 12, marginBottom: 28 }}>
      <Tag>Hypothetical</Tag>
      <Tag color={COLORS.subtext}>Trade idea</Tag>
    </div>

    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT.sans, fontWeight: 700, fontSize: FONT.tag, letterSpacing: 3, textTransform: "uppercase", color: COLORS.tertiary, marginBottom: 18 }}>
        My model &middot; Wolves title odds
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: 22 }}>
        <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 92, color: COLORS.baseline }}>{deal.title.baseline_pct}</span>
        <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 66, color: COLORS.tertiary }}>&rarr;</span>
        <span style={{ fontFamily: FONT.mono, fontWeight: 800, fontSize: 186, color: COLORS.alert, lineHeight: 0.9 }}>{deal.title.best_estimate_pct}</span>
      </div>

      <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 76, lineHeight: 1.02, color: COLORS.text, letterSpacing: -0.5, marginTop: 34 }}>
        A title bump for just <span style={{ color: COLORS.alert }}>one pick</span>. 2027 stays clean.
      </div>

      <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 44, color: COLORS.chalk, marginTop: 26 }}>
        Randle &nbsp;&rarr;&nbsp; Nembhard + Toppin
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 22 }}>
        <span style={{ fontFamily: FONT.scrawl, fontSize: 40, color: COLORS.alert, transform: "rotate(-2deg)" }}>&darr;</span>
        <span style={{ fontFamily: FONT.sans, fontWeight: 700, fontSize: 26, letterSpacing: 1, color: COLORS.chalk }}>HOW IT WORKS</span>
      </div>
    </div>
  </Frame>
);

// ----------------------------------------------------------------------------
// 2. THE DEAL
// ----------------------------------------------------------------------------
const PlayerRow: React.FC<{ name: string; salary: string }> = ({ name, salary }) => (
  <div
    style={{
      display: "flex",
      justifyContent: "space-between",
      alignItems: "baseline",
      padding: "18px 0",
      borderBottom: `1px solid ${COLORS.hairlineSoft}`,
    }}
  >
    <span style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 46, color: COLORS.text }}>{name}</span>
    <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: FONT.num, color: COLORS.subtext }}>{salary}</span>
  </div>
);

const SideHead: React.FC<{ label: string; total: string; accent?: boolean }> = ({ label, total, accent }) => (
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 6 }}>
    <span style={{ fontWeight: 800, fontSize: 30, letterSpacing: 3, textTransform: "uppercase", color: accent ? COLORS.alert : COLORS.subtext }}>
      {label}
    </span>
    <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 30, color: COLORS.tertiary }}>{total}</span>
  </div>
);

export const Deal: React.FC = () => (
  <Frame kicker="The deal" page={2}>
    <div style={{ display: "flex", flexDirection: "column", gap: 44, marginTop: 14 }}>
      <div>
        <SideHead label="Wolves get" total={deal.deal.in_total} accent />
        {deal.deal.min_gets.map((p) => (
          <PlayerRow key={p.name} name={p.name} salary={p.salaryLabel} />
        ))}
      </div>
      <div>
        <SideHead label="Wolves send" total={deal.deal.out_total} />
        {deal.deal.min_sends.map((p) => (
          <PlayerRow key={p.name} name={p.name} salary={p.salaryLabel} />
        ))}
        <div style={{ display: "flex", alignItems: "center", gap: 14, paddingTop: 20 }}>
          <span style={{ fontFamily: FONT.scrawl, fontSize: 40, color: COLORS.alert }}>+</span>
          <span style={{ fontFamily: FONT.display, fontWeight: 500, fontSize: 40, color: COLORS.chalk }}>one future first</span>
          <span style={{ fontFamily: FONT.sans, fontWeight: 500, fontSize: 24, color: COLORS.tertiary }}>
            ({deal.deal.picks_note})
          </span>
        </div>
      </div>
    </div>
    <div style={{ flex: 1 }} />
    <div style={{ fontFamily: FONT.sans, fontSize: 25, color: COLORS.tertiary, lineHeight: 1.3 }}>
      A $33M forward and a young wing for a starting playmaker and a stretch four. Nearly even money, in and out.
    </div>
  </Frame>
);

// ----------------------------------------------------------------------------
// 3. THE CAP REALITY  (the credibility slide — design unchanged, numbers updated)
// ----------------------------------------------------------------------------
export const Cap: React.FC = () => {
  const trackW = WIDTH - SAFE.x * 2;
  const lo = 190_000_000;
  const hi = 224_000_000;
  const top = 18;
  const drawH = 360;
  const y = (v: number) => top + (1 - (v - lo) / (hi - lo)) * drawH;

  const tax = 201_000_000;
  const apron1 = 209_100_000;
  const apron2 = 222_000_000;
  const minPost = 192_478_532;

  const x0 = 8;
  const xLine = 430;
  const xLabel = 454;

  const rows = [
    { v: apron2, name: "2nd apron", money: "$222M", color: COLORS.subtext, bold: false, tag: null },
    { v: apron1, name: "1st apron", money: "$209.1M", color: COLORS.chalk, bold: true, tag: "Hard-cap line" },
    { v: tax, name: "Tax", money: "$201M", color: COLORS.subtext, bold: false, tag: null },
  ];

  return (
    <Frame kicker="The cap reality" page={3}>
      <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: FONT.big, lineHeight: 1.05, color: COLORS.text, marginTop: 2 }}>
        Stays <span style={{ color: COLORS.alert }}>under the tax</span>, and never trips the hard cap.
      </div>

      <div style={{ position: "relative", height: drawH + top + 18, marginTop: 22 }}>
        <svg width={trackW} height={drawH + top + 18} style={{ position: "absolute", left: 0, top: 0 }}>
          {/* room band: everything MIN has free, from where they land up to the hard-cap line */}
          <rect x={x0} y={y(apron1)} width={xLine - x0} height={y(minPost) - y(apron1)} fill={COLORS.alertDim} />
          {rows.map((r) => (
            <line key={r.name} x1={x0} y1={y(r.v)} x2={xLine} y2={y(r.v)} stroke={r.color} strokeWidth={r.bold ? 4 : 2} strokeDasharray={r.bold ? undefined : "2 7"} />
          ))}
          <line x1={x0} y1={y(minPost)} x2={xLine} y2={y(minPost)} stroke={COLORS.good} strokeWidth={3} />
          <circle cx={x0} cy={y(minPost)} r={12} fill={COLORS.good} />
          <line x1={x0 + 26} y1={y(minPost) - 6} x2={x0 + 26} y2={y(apron1) + 6} stroke={COLORS.alert} strokeWidth={2.5} />
          <path d={`M${x0 + 20} ${y(apron1) + 12} L${x0 + 26} ${y(apron1) + 4} L${x0 + 32} ${y(apron1) + 12}`} fill="none" stroke={COLORS.alert} strokeWidth={2.5} />
          <path d={`M${x0 + 20} ${y(minPost) - 12} L${x0 + 26} ${y(minPost) - 4} L${x0 + 32} ${y(minPost) - 12}`} fill="none" stroke={COLORS.alert} strokeWidth={2.5} />
        </svg>

        {rows.map((r) => (
          <div key={r.name} style={{ position: "absolute", left: xLabel, top: y(r.v) - 26, display: "flex", alignItems: "baseline", gap: 16, whiteSpace: "nowrap" }}>
            <span style={{ fontFamily: FONT.mono, fontWeight: r.bold ? 800 : 700, fontSize: r.bold ? 46 : 40, color: r.color }}>{r.money}</span>
            <span style={{ fontWeight: 700, fontSize: 23, letterSpacing: 1.5, textTransform: "uppercase", color: r.color }}>{r.name}</span>
            {r.tag && (
              <span style={{ fontWeight: 800, fontSize: 18, letterSpacing: 1.2, textTransform: "uppercase", color: COLORS.chalk, border: `1.5px solid ${COLORS.hairline}`, borderRadius: RADIUS, padding: "4px 8px" }}>
                {r.tag}
              </span>
            )}
          </div>
        ))}

        <div style={{ position: "absolute", left: xLabel, top: y(minPost) - 30, display: "flex", alignItems: "baseline", gap: 16, whiteSpace: "nowrap" }}>
          <span style={{ fontFamily: FONT.mono, fontWeight: 800, fontSize: 46, color: COLORS.good }}>$192.5M</span>
          <span style={{ fontWeight: 700, fontSize: 23, color: COLORS.good }}>WOLVES</span>
        </div>

        <div style={{ position: "absolute", left: x0 + 56, top: (y(minPost) + y(apron1)) / 2 - 36, transform: "rotate(-3deg)" }}>
          <div style={{ fontFamily: FONT.scrawl, fontSize: FONT.scrawlSize, color: COLORS.chalk, lineHeight: 1 }}>no hard cap</div>
          <div style={{ fontWeight: 500, fontSize: 22, color: COLORS.tertiary, marginTop: 6 }}>$8.5M under the tax. every tool intact</div>
        </div>
      </div>

      <div style={{ flex: 1 }} />

      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        <div style={{ fontWeight: 500, fontSize: 30, color: COLORS.subtext, lineHeight: 1.32 }}>
          A near-even swap that even <span style={{ color: COLORS.text, fontWeight: 700 }}>sheds a little salary</span>, so it never trips a hard cap.
          The win-now deals slam into the first apron and freeze the roster. this one leaves Minnesota free.
        </div>
        <div style={{ fontWeight: 500, fontSize: 25, color: COLORS.tertiary, lineHeight: 1.3 }}>
          Indiana&rsquo;s side is clean: they take Randle&rsquo;s expiring back and land near $201M.
        </div>
      </div>
    </Frame>
  );
};

// ----------------------------------------------------------------------------
// 4. THE TITLE ODDS
// ----------------------------------------------------------------------------
export const Title: React.FC = () => {
  const views = deal.title.views;
  const order: [string, string][] = [
    ["Cautious (DARKO)", views.darko],
    ["Box", views.box],
    ["RAPM", views.rapm],
    ["Consensus", views.consensus],
  ];
  return (
    <Frame kicker="The title odds" page={4}>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 30, marginTop: 14 }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 24, letterSpacing: 2, textTransform: "uppercase", color: COLORS.tertiary }}>Before</div>
          <div style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 84, color: COLORS.baseline }}>{deal.title.baseline_pct}</div>
        </div>
        <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 60, color: COLORS.tertiary, paddingBottom: 16 }}>&rarr;</div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 24, letterSpacing: 2, textTransform: "uppercase", color: COLORS.alert }}>After (best estimate)</div>
          <div style={{ fontFamily: FONT.mono, fontWeight: 800, fontSize: FONT.hero, color: COLORS.alert }}>{deal.title.best_estimate_pct}</div>
        </div>
      </div>

      <div style={{ fontWeight: 500, fontSize: 27, color: COLORS.subtext, marginTop: 8 }}>
        Modeled championship probability. Range {deal.title.band_low_pct} to {deal.title.band_high_pct} across four ways of valuing the players.
      </div>

      <div style={{ marginTop: 34 }}>
        {order.map(([name, v], i) => (
          <div key={name} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 0", borderTop: i === 0 ? `1px solid ${COLORS.hairline}` : `1px solid ${COLORS.hairlineSoft}` }}>
            <span style={{ fontWeight: 600, fontSize: 30, color: COLORS.subtext }}>{name}</span>
            <span style={{ fontFamily: FONT.mono, fontWeight: 700, fontSize: 40, color: COLORS.text }}>{v} pts</span>
          </div>
        ))}
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <span style={{ fontFamily: FONT.scrawl, fontSize: 40, color: COLORS.chalk, transform: "rotate(-2deg)" }}>the good part:</span>
        <span style={{ fontWeight: 500, fontSize: 26, color: COLORS.subtext, maxWidth: 640, lineHeight: 1.28 }}>
          even the skeptical view likes it. the best floor of any realistic Wolves deal.
        </span>
      </div>
    </Frame>
  );
};

// ----------------------------------------------------------------------------
// 5. WOULD THEY SAY YES
// ----------------------------------------------------------------------------
const YesCard: React.FC<{ team: string; verdict: string; why: string; sub: string; borderAccent: boolean; verdictColor: string }> = ({ team, verdict, why, sub, borderAccent, verdictColor }) => (
  <div style={{ background: COLORS.inset, border: `1px solid ${borderAccent ? "rgba(0,132,61,0.45)" : COLORS.hairline}`, borderRadius: RADIUS, padding: "28px 32px" }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
      <span style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 46, color: COLORS.text }}>{team}</span>
      <span style={{ fontWeight: 800, fontSize: 28, letterSpacing: 2, color: verdictColor }}>{verdict}</span>
    </div>
    <div style={{ fontWeight: 500, fontSize: 27, color: COLORS.subtext, lineHeight: 1.3 }}>{why}</div>
    <div style={{ fontWeight: 500, fontSize: 23, color: COLORS.tertiary, lineHeight: 1.3, marginTop: 11 }}>{sub}</div>
  </div>
);

export const SayYes: React.FC = () => (
  <Frame kicker="Would they say yes?" page={5}>
    <div style={{ fontFamily: FONT.display, fontWeight: 500, fontSize: 40, color: COLORS.chalk, marginTop: 2, marginBottom: 24 }}>My model says&hellip;</div>
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <YesCard team="Indiana" verdict={deal.sayyes.ind.verdict} why={deal.sayyes.ind.why} sub={deal.sayyes.ind.margin_note} borderAccent={false} verdictColor={COLORS.chalk} />
      <YesCard team="Minnesota" verdict="THE SMART YES" why={deal.sayyes.min.why} sub="Good now AND keeps the 2027 picks. the rare trade that does both." borderAccent verdictColor={COLORS.good} />
    </div>
    <div style={{ flex: 1 }} />
    <div style={{ fontWeight: 500, fontSize: 24, color: COLORS.tertiary, lineHeight: 1.3 }}>{deal.sayyes.disclaimer}</div>
  </Frame>
);

// ----------------------------------------------------------------------------
// 6. THE VERDICT  (with the good-now / keep-the-future contrast)
// ----------------------------------------------------------------------------
const ContrastCol: React.FC<{ title: string; picks: string; flex: string; good: boolean }> = ({ title, picks, flex, good }) => (
  <div style={{ flex: 1, padding: "20px 24px", border: `1px solid ${good ? "rgba(0,132,61,0.45)" : COLORS.hairline}`, borderRadius: RADIUS, background: COLORS.inset }}>
    <div style={{ fontWeight: 800, fontSize: 22, letterSpacing: 1.5, textTransform: "uppercase", color: good ? COLORS.good : COLORS.tertiary, marginBottom: 12 }}>{title}</div>
    <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 32, color: COLORS.text }}>{picks}</div>
    <div style={{ fontWeight: 500, fontSize: 24, color: COLORS.subtext, marginTop: 4 }}>{flex}</div>
  </div>
);

export const Verdict: React.FC = () => (
  <Frame kicker="The verdict" page={6}>
    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT.display, fontWeight: 600, fontSize: 58, lineHeight: 1.08, color: COLORS.text }}>
        Better now, <span style={{ color: COLORS.alert }}>without mortgaging 2027</span>.
      </div>
      <div style={{ fontWeight: 500, fontSize: 32, lineHeight: 1.32, color: COLORS.subtext, marginTop: 22 }}>
        A high-floor playmaker for an expiring and one pick, with the war chest still intact.
      </div>

      <div style={{ display: "flex", gap: 18, marginTop: 34 }}>
        <ContrastCol title="This trade" picks="1 pick" flex="2027 stays open" good />
        <ContrastCol title="The blockbuster" picks="2 picks" flex="2027 clogged" good={false} />
      </div>

      <div style={{ marginTop: 40, paddingTop: 28, borderTop: `1px solid ${COLORS.hairline}` }}>
        <div style={{ fontFamily: FONT.display, fontWeight: 700, fontSize: 50, color: COLORS.text, lineHeight: 1.08 }}>{deal.verdict.question}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 20 }}>
          <span style={{ fontFamily: FONT.scrawl, fontSize: 42, color: COLORS.alert, transform: "rotate(-2deg)" }}>&darr;</span>
          <span style={{ fontWeight: 600, fontSize: 28, color: COLORS.chalk }}>Drop a trade in the comments and I&rsquo;ll run it through the model.</span>
        </div>
      </div>
    </div>
  </Frame>
);
