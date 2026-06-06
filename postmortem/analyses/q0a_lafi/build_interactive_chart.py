"""Build the interactive D3 quadrant chart for the LAFI article.

Output: a self-contained HTML file at outputs/charts/q0a_lafi/quadrant_interactive.html

The chart tells a three-layer story:
  1. The Wolves' 2025-26 placement in Q4 (distributed pickup) is the visual punch.
  2. The 7 historical cohort teams are highlighted in amber as the cautionary group.
  3. The Wolves' 4-year drift INTO Q4 (2022-23 to 2025-26) animates on load.

Hover any dot to see team-season + LAFI components + playoff outcome.
Click a quadrant label to isolate teams in that quadrant.
Click "Replay" to re-run the trajectory animation.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / ".env")


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
# The chart embeds in the Chasing the First Banner site, which is dark mode.
# Flip THEME to "light" to regenerate a light-background version.
THEME = "dark"

PALETTES = {
    "light": {
        "bg": "#FAFAF9",
        "panel": "#FFFFFF",
        "panel-border": "#E2E8F0",
        "panel-hover": "#F1F5F9",
        "panel-shadow": "0 6px 24px rgba(15,23,42,0.12), 0 1px 3px rgba(15,23,42,0.06)",
        "text": "#1E293B",
        "muted": "#64748B",
        "dot-stroke": "#FAFAF9",
        "bg-dot-opacity": "0.30",
        "wolves-blue": "#0C2340",
        "wolves-green": "#78BE20",
        "wolves-green-glow": "rgba(120,190,32,0.35)",
        "wolves-shadow": "rgba(12,35,64,0.30)",
        "cohort-amber": "#D97706",
        "cohort-shadow": "rgba(217,119,6,0.25)",
        "contender-teal": "#0D9488",
        "contender-shadow": "rgba(13,148,136,0.25)",
        "anchor-grey": "#475569",
        "background-grey": "#94A3B8",
        "axis-grey": "#64748B",
        "bg-q1": "rgba(34,197,94,0.025)",
        "bg-q2": "rgba(99,102,241,0.025)",
        "bg-q3": "rgba(244,63,94,0.025)",
        "bg-q4": "rgba(217,119,6,0.045)",
        "result-good": "#16A34A",
        "result-good-bg": "#DCFCE7",
        "result-mid": "#CA8A04",
        "result-mid-bg": "#FEF9C3",
        "result-bad": "#DC2626",
        "result-bad-bg": "#FEE2E2",
        "badge-text": "#FFFFFF",
    },
    "dark": {
        "bg": "#0F172A",
        "panel": "#1E293B",
        "panel-border": "#334155",
        "panel-hover": "#334155",
        "panel-shadow": "0 8px 28px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.40)",
        "text": "#E2E8F0",
        "muted": "#94A3B8",
        "dot-stroke": "#0F172A",
        "bg-dot-opacity": "0.45",
        "wolves-blue": "#6FA8DC",
        "wolves-green": "#78BE20",
        "wolves-green-glow": "rgba(120,190,32,0.55)",
        "wolves-shadow": "rgba(111,168,220,0.45)",
        "cohort-amber": "#FBBF24",
        "cohort-shadow": "rgba(251,191,36,0.40)",
        "contender-teal": "#2DD4BF",
        "contender-shadow": "rgba(45,212,191,0.40)",
        "anchor-grey": "#94A3B8",
        "background-grey": "#94A3B8",
        "axis-grey": "#94A3B8",
        "bg-q1": "rgba(45,212,191,0.05)",
        "bg-q2": "rgba(129,140,248,0.05)",
        "bg-q3": "rgba(248,113,113,0.05)",
        "bg-q4": "rgba(251,191,36,0.08)",
        "result-good": "#4ADE80",
        "result-good-bg": "rgba(34,197,94,0.16)",
        "result-mid": "#FBBF24",
        "result-mid-bg": "rgba(202,138,4,0.20)",
        "result-bad": "#F87171",
        "result-bad-bg": "rgba(239,68,68,0.16)",
        "badge-text": "#0F172A",
    },
}


def build_root_css(theme: str) -> str:
    pal = PALETTES[theme]
    lines = "\n".join(f"    --{k}: {v};" for k, v in pal.items())
    return ":root {\n" + lines + "\n  }"


# ---------------------------------------------------------------------------
# Data assembly
# ---------------------------------------------------------------------------

def season_label(year: int) -> str:
    """2022 -> '22-23'."""
    return f"'{year % 100:02d}-{(year + 1) % 100:02d}"


def get_playoff_result(made_po: bool, wins: int) -> str:
    """For COMPLETED playoff runs: map total win count to result.

    Do not use this for in-progress runs; see compute_2026_playoff_states below
    which walks games per series to correctly label still-active teams.
    """
    if not made_po or wins is None:
        return "Missed playoffs"
    wins = int(wins)
    if wins < 4:
        return f"Lost R1 ({wins}-4)"
    if wins < 8:
        return f"Lost R2"
    if wins < 12:
        return f"Lost CF"
    if wins < 16:
        return f"Lost Finals"
    return "Champion"


_OPP_RE = re.compile(r"(?:vs\.|@)\s+(\w+)")


def _extract_opponent(matchup: str) -> str | None:
    m = _OPP_RE.search(matchup or "")
    return m.group(1) if m else None


def compute_2026_playoff_states(cur) -> dict[str, tuple[str, int]]:
    """For each team that played in 2025-26 playoffs, walk their games in order
    and determine current status (eliminated, advanced between rounds, or active
    in a current series). Returns {team_abbr: (status_label, total_wins)}.
    """
    cur.execute(
        """
        SELECT team_abbreviation, game_date, matchup, wl
        FROM nba_games
        WHERE season_type = 'Playoffs'
          AND game_date BETWEEN '2026-04-01' AND '2026-08-31'
        ORDER BY team_abbreviation, game_date
        """
    )
    by_team: dict[str, list[tuple]] = {}
    for team, date, matchup, wl in cur.fetchall():
        by_team.setdefault(team, []).append((date, matchup, wl))

    round_names = ["R1", "R2", "CF", "Finals"]
    states: dict[str, tuple[str, int]] = {}
    for team, games in by_team.items():
        # Walk chronologically, splitting into series by opponent.
        series: list[list] = []  # each entry: [opp, wins, losses]
        for _, matchup, wl in games:
            opp = _extract_opponent(matchup)
            if not series or series[-1][0] != opp:
                series.append([opp, 0, 0])
            if wl == "W":
                series[-1][1] += 1
            else:
                series[-1][2] += 1

        total_wins = sum(s[1] for s in series)
        n_round = len(series)
        round_name = round_names[min(n_round - 1, 3)]
        last_opp, last_w, last_l = series[-1]

        if last_l >= 4:
            label = f"Lost {round_name} ({last_w}-{last_l})"
        elif last_w >= 4:
            # Won this series. If they won the Finals, champion; otherwise advanced.
            if total_wins >= 16:
                label = "Champion"
            elif n_round == 4:
                label = f"Won Finals (active)"
            else:
                label = f"Won {round_name}, advanced"
        else:
            # Series ongoing.
            label = f"In {round_name} ({last_w}-{last_l})"

        states[team] = (label, total_wins)
    return states


def load_data() -> list[dict]:
    composite = pd.read_csv(ROOT / "outputs/tables/q0a_lafi/lafi_composite_5component.csv")
    validation = pd.read_csv(ROOT / "outputs/tables/q0a_lafi/validation/validation_dataset_playoff_teams.csv")

    # Pull 2025-26 playoff outcomes from warehouse since validation excludes the in-progress year.
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    cur = conn.cursor()
    cur.execute("SET search_path TO nba")
    states_2026 = compute_2026_playoff_states(cur)
    cur.close()
    conn.close()

    # Index validation by (team, year)
    val_idx = {(r.team_abbreviation, int(r.season_start_year)): r for r in validation.itertuples()}

    # Anchors: most-canonical teams to label in each non-Q4 quadrant.
    # is_contender = True for teams that reached the conference finals or won the title.
    # Others are archetype landmarks (Q3 iso peaks for context).
    ANCHORS = {
        ("SAS", 2025): {"label": "Spurs",     "is_contender": True},   # Q1 / beat the Wolves in R2
        ("OKC", 2024): {"label": "Thunder",   "is_contender": True},   # Q1 / 2024-25 champs
        ("GSW", 2015): {"label": "Warriors",  "is_contender": True},   # Q1 / 73-win season, lost Finals
        ("DEN", 2022): {"label": "Nuggets",   "is_contender": True},   # Q2 / 2022-23 champs
        ("HOU", 2017): {"label": "Rockets",   "is_contender": False},  # Q3 / Harden iso peak (cautionary)
        ("DAL", 2022): {"label": "Mavericks", "is_contender": False},  # Q3 / Luka iso peak (cautionary)
    }

    rows = composite[composite["season_type"] == "Regular Season"]
    out: list[dict] = []
    for r in rows.itertuples():
        team = r.team_abbreviation
        year = int(r.season_start_year)

        if year == 2025:
            if team in states_2026:
                po_label, wins = states_2026[team]
                made = True
            else:
                po_label, wins = "Missed playoffs", 0
                made = False
        else:
            v = val_idx.get((team, year))
            if v is None:
                made = False
                wins = 0
            else:
                made = bool(v.made_playoffs)
                wins = int(v.playoff_wins) if v.playoff_wins is not None else 0
            po_label = get_playoff_result(made, wins)

        is_cohort = (
            r.sharp_lafi_pct >= 80
            and r.C1_ball_stickiness_pct < 50
            and r.C2_movement_death_pct > 50
        )
        is_wolves_traj = team == "MIN" and year in (2022, 2023, 2024, 2025)

        out.append({
            "team": team,
            "year": year,
            "season": season_label(year),
            "C1": round(r.C1_ball_stickiness_pct, 1),
            "C2": round(r.C2_movement_death_pct, 1),
            "C3": round(r.C3_isolation_reliance_pct, 1),
            "C4": round(r.C4_action_poverty_pct, 1),
            "C5": round(r.C5_shot_quality_decay_pct, 1),
            "full_lafi": round(r.lafi_pct, 1),
            "sharp_lafi": round(r.sharp_lafi_pct, 1),
            "po_result": po_label,
            "is_cohort": bool(is_cohort),
            "is_wolves_traj": bool(is_wolves_traj),
            "anchor_label": ANCHORS[(team, year)]["label"] if (team, year) in ANCHORS else None,
            "is_contender": ANCHORS[(team, year)]["is_contender"] if (team, year) in ANCHORS else False,
        })

    return out


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>The LAFI Four-Quadrant Framework</title>
<style>
  :root {
    --wolves-blue: #0C2340;
    --wolves-green: #78BE20;
    --wolves-green-glow: rgba(120, 190, 32, 0.35);
    --cohort-amber: #D97706;
    --cohort-amber-bg: #FEF3C7;
    --anchor-grey: #475569;
    --contender-teal: #0D9488;
    --contender-teal-bg: #CCFBF1;
    --background-grey: #94A3B8;
    --axis-grey: #64748B;
    --bg: #FAFAF9;
    --bg-q1: rgba(34, 197, 94, 0.025);
    --bg-q2: rgba(99, 102, 241, 0.025);
    --bg-q3: rgba(244, 63, 94, 0.025);
    --bg-q4: rgba(217, 119, 6, 0.045);
    --text: #1E293B;
    --muted: #64748B;
    --result-good: #16A34A;
    --result-mid: #CA8A04;
    --result-bad: #DC2626;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 24px;
    background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }
  .chart-wrap {
    max-width: 880px; margin: 0 auto;
  }
  .chart-header { margin-bottom: 8px; }
  h1 { font-size: 21px; margin: 0 0 4px 0; font-weight: 700; letter-spacing: -0.01em; }
  .subtitle-wrap {
    position: relative; min-height: 42px; margin-bottom: 18px;
  }
  .subtitle {
    font-size: 13px; color: var(--muted); margin: 0; line-height: 1.5;
    transition: opacity 320ms cubic-bezier(0.4, 0, 0.2, 1);
  }
  .subtitle.narrative {
    color: var(--text); font-weight: 500;
  }
  .subtitle .narrative-year {
    display: inline-block; padding: 1px 7px; border-radius: 4px;
    background: var(--wolves-blue); color: white; font-weight: 700;
    font-variant-numeric: tabular-nums; margin-right: 6px;
    font-size: 12px; letter-spacing: 0.01em;
  }
  .subtitle.narrative.final .narrative-year { background: var(--wolves-green); }
  .onboard-hint {
    margin-top: 6px; font-size: 12px; color: var(--muted);
    opacity: 0; transition: opacity 500ms ease;
  }
  .onboard-hint.visible { opacity: 1; }
  svg { width: 100%; height: auto; display: block; background: var(--bg); }
  .quad-bg { transition: fill 300ms ease; }
  .quad-bg.q4-highlight { fill: var(--bg-q4); }
  .axis text { font-size: 11px; fill: var(--axis-grey); }
  .axis path, .axis line { stroke: var(--axis-grey); stroke-opacity: 0.25; }
  .axis-label {
    font-size: 12px; fill: var(--text); font-weight: 600; letter-spacing: 0.005em;
  }
  .quad-line {
    stroke: var(--axis-grey); stroke-opacity: 0.35; stroke-dasharray: 3 4; stroke-width: 1;
  }
  .quad-label {
    font-size: 12.5px; font-weight: 700; fill: var(--axis-grey); letter-spacing: 0.01em;
    cursor: pointer; user-select: none;
    transition: fill 220ms ease, opacity 220ms ease;
  }
  .quad-label.q4 { fill: var(--cohort-amber); }
  .quad-label:hover { fill: var(--wolves-blue); }
  .quad-label.active { fill: var(--wolves-blue); }
  .dot { cursor: pointer; transition: stroke 200ms ease; }
  .bg-dot { fill: var(--background-grey); fill-opacity: 0.28; }
  .bg-dot:hover { fill-opacity: 0.95; stroke: var(--wolves-blue); stroke-width: 1.5; }
  .anchor-dot { fill: var(--anchor-grey); fill-opacity: 0.7; stroke: white; stroke-width: 1; }
  .anchor-dot:hover { fill-opacity: 1; }
  .anchor-dot.contender {
    fill: var(--contender-teal); fill-opacity: 0.92; stroke-width: 1.75;
    filter: drop-shadow(0 1px 2px rgba(13, 148, 136, 0.25));
  }
  .anchor-label {
    font-size: 10.5px; fill: var(--anchor-grey); pointer-events: none; font-weight: 500;
  }
  .anchor-label.contender {
    fill: var(--contender-teal); font-weight: 700; font-size: 10.75px;
  }
  .cohort-dot {
    fill: var(--cohort-amber); fill-opacity: 0.88;
    stroke: white; stroke-width: 1.75;
    filter: drop-shadow(0 1px 2px rgba(217, 119, 6, 0.25));
  }
  .cohort-dot:hover { fill-opacity: 1; }
  .cohort-label {
    font-size: 10.5px; fill: var(--cohort-amber); font-weight: 700; pointer-events: none;
    letter-spacing: 0.01em;
  }
  .wolves-dot {
    fill: var(--wolves-blue); stroke: white; stroke-width: 2;
    filter: drop-shadow(0 2px 3px rgba(12, 35, 64, 0.3));
  }
  .wolves-dot.current {
    fill: var(--wolves-green); stroke-width: 2.5;
    filter: drop-shadow(0 0 12px var(--wolves-green-glow));
  }
  .wolves-label {
    font-size: 11px; font-weight: 700; fill: var(--wolves-blue); pointer-events: none;
    letter-spacing: 0.01em;
  }
  .wolves-label.current {
    fill: var(--wolves-green); font-size: 12.5px;
  }
  .wolves-arrow { stroke: var(--wolves-blue); stroke-width: 2; fill: none; opacity: 0.85; }
  .pulse-ring { fill: none; stroke: var(--wolves-green); stroke-width: 2; opacity: 0; }
  .controls {
    display: flex; gap: 14px; align-items: center; margin-top: 14px;
    font-size: 13px; flex-wrap: wrap;
  }
  button {
    background: white; border: 1px solid #CBD5E1; border-radius: 8px;
    padding: 7px 14px; font-size: 13px; cursor: pointer; color: var(--text);
    font-family: inherit; font-weight: 500;
    display: inline-flex; align-items: center; gap: 6px;
    transition: background 180ms ease, border-color 180ms ease, transform 80ms ease;
  }
  button:hover { background: #F1F5F9; border-color: #94A3B8; }
  button:active { transform: scale(0.97); }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  button svg { width: 13px; height: 13px; }
  .legend {
    display: flex; gap: 18px; align-items: center; font-size: 12px;
    color: var(--muted); flex-wrap: wrap;
  }
  .legend-item {
    display: flex; align-items: center; gap: 6px;
    cursor: pointer; padding: 3px 7px; border-radius: 6px;
    transition: background 160ms ease, opacity 160ms ease;
    user-select: none;
  }
  .legend-item:hover { background: #F1F5F9; }
  .legend-item.legend-dim { opacity: 0.4; }
  .legend-dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
  .legend-dot.glow {
    background: var(--wolves-green); box-shadow: 0 0 0 2px white, 0 0 8px var(--wolves-green-glow);
  }
  #tooltip {
    position: absolute; pointer-events: none; opacity: 0;
    background: white; border: 1px solid #E2E8F0; border-radius: 8px;
    padding: 11px 13px; font-size: 12px; line-height: 1.5;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.12), 0 1px 3px rgba(15, 23, 42, 0.06);
    transition: opacity 160ms cubic-bezier(0.4, 0, 0.2, 1),
                transform 160ms cubic-bezier(0.4, 0, 0.2, 1);
    transform: translateY(4px);
    max-width: 260px; z-index: 10;
  }
  #tooltip.visible { opacity: 1; transform: translateY(0); }
  #tooltip .tt-team {
    font-weight: 700; font-size: 13.5px; margin-bottom: 5px;
    letter-spacing: -0.005em;
  }
  #tooltip .tt-result {
    display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px;
    font-weight: 600; margin-bottom: 6px;
  }
  #tooltip .tt-result.good { background: #DCFCE7; color: var(--result-good); }
  #tooltip .tt-result.mid  { background: #FEF9C3; color: var(--result-mid); }
  #tooltip .tt-result.bad  { background: #FEE2E2; color: var(--result-bad); }
  #tooltip table { border-collapse: collapse; margin-top: 4px; width: 100%; }
  #tooltip td { padding: 2px 0; }
  #tooltip td.lbl { color: var(--muted); padding-right: 14px; }
  #tooltip td.val { text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }
  .dim-target { transition: opacity 280ms cubic-bezier(0.4, 0, 0.2, 1); }
  @media (prefers-reduced-motion: reduce) {
    * { animation-duration: 0.01ms !important; transition-duration: 50ms !important; }
  }
</style>
</head>
<body>
<div class="chart-wrap">
  <div class="chart-header">
    <h1>The four-quadrant framework: where every NBA team sits since 2014</h1>
    <div class="subtitle-wrap">
      <p class="subtitle" id="subtitle">Each dot is one team-season. Ball stickiness on x, motion death on y. The 2025-26 Wolves are deep in Q4 (distributed pickup), and they got there by walking across three quadrants in four years.</p>
    </div>
  </div>

  <svg id="chart" viewBox="0 0 860 760" aria-label="LAFI quadrant scatter"></svg>

  <div class="controls">
    <button id="replay" type="button">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg>
      Replay trajectory
    </button>
    <button id="reset" type="button">Reset view</button>
    <div class="legend">
      <span class="legend-item" data-group="wolves-current"><span class="legend-dot glow"></span>Wolves 2025-26</span>
      <span class="legend-item" data-group="wolves-traj"><span class="legend-dot" style="background: var(--wolves-blue);"></span>Wolves trajectory</span>
      <span class="legend-item" data-group="cohort"><span class="legend-dot" style="background: var(--cohort-amber);"></span>Cohort (7 historical comps)</span>
      <span class="legend-item" data-group="contender"><span class="legend-dot" style="background: var(--contender-teal);"></span>Contender (reached CF or further)</span>
      <span class="legend-item" data-group="archetype"><span class="legend-dot" style="background: var(--anchor-grey);"></span>Iso archetype landmark</span>
      <span class="legend-item" data-group="background"><span class="legend-dot" style="background: var(--background-grey); opacity: 0.5;"></span>Other team-seasons</span>
    </div>
  </div>
  <p class="onboard-hint" id="onboard">Hover any dot to see team-season detail. Click a quadrant label to focus on just that quadrant. Hover a legend item to highlight that group.</p>
</div>

<div id="tooltip"></div>

<script id="lafi-data" type="application/json">__DATA__</script>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
(() => {
  const raw = JSON.parse(document.getElementById('lafi-data').textContent);
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Per-season narrative for the Wolves trajectory ----------
  const SEASON_STORY = {
    2022: "Gobert's first year. Already dead off-ball, not yet an iso team.",
    2023: "The WCF year. Designed offense. Right next to the Spurs in Q1.",
    2024: "Randle's first year. Stickier ball, more iso, shot quality drops.",
    2025: "Distributed pickup. Iso load decentralizes. The shots get worse.",
  };
  const DEFAULT_SUBTITLE = "Each dot is one team-season. Ball stickiness on x, motion death on y. The 2025-26 Wolves are deep in Q4 (distributed pickup), and they got there by walking across three quadrants in four years.";
  const subtitleEl = document.getElementById('subtitle');
  const onboardEl = document.getElementById('onboard');

  function setSubtitleNarrative(season, isFinal) {
    const story = SEASON_STORY[season];
    if (!story) return;
    subtitleEl.style.opacity = 0;
    setTimeout(() => {
      const label = `MIN '${(season % 100).toString().padStart(2,'0')}-${((season+1) % 100).toString().padStart(2,'0')}`;
      subtitleEl.innerHTML = `<span class="narrative-year">${label}</span>${story}`;
      subtitleEl.className = 'subtitle narrative' + (isFinal ? ' final' : '');
      subtitleEl.style.opacity = 1;
    }, 200);
  }
  function setSubtitleDefault() {
    subtitleEl.style.opacity = 0;
    setTimeout(() => {
      subtitleEl.textContent = DEFAULT_SUBTITLE;
      subtitleEl.className = 'subtitle';
      subtitleEl.style.opacity = 1;
    }, 200);
  }

  // ---------- Layout ----------
  const W = 860, H = 760;
  const margin = { top: 60, right: 50, bottom: 70, left: 70 };
  const innerW = W - margin.left - margin.right;
  const innerH = H - margin.top - margin.bottom;

  const svg = d3.select('#chart').attr('viewBox', `0 0 ${W} ${H}`);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain([0, 100]).range([0, innerW]);
  const y = d3.scaleLinear().domain([0, 100]).range([innerH, 0]); // y inverted

  // ---------- Quadrant background tints (very subtle) ----------
  const quadBgLayer = g.append('g').attr('class', 'quad-bg-layer');
  const quadBgs = [
    { id: 'Q1', x: 0,        y: y(50),   w: x(50),         h: innerH - y(50),  fill: 'var(--bg-q1)' },
    { id: 'Q2', x: x(50),    y: y(50),   w: innerW - x(50), h: innerH - y(50), fill: 'var(--bg-q2)' },
    { id: 'Q3', x: x(50),    y: 0,       w: innerW - x(50), h: y(50),          fill: 'var(--bg-q3)' },
    { id: 'Q4', x: 0,        y: 0,       w: x(50),         h: y(50),           fill: 'var(--bg-q4)' },
  ];
  quadBgLayer.selectAll('rect').data(quadBgs).enter()
    .append('rect')
    .attr('class', d => `quad-bg quad-bg-${d.id}`)
    .attr('x', d => d.x).attr('y', d => d.y)
    .attr('width', d => d.w).attr('height', d => d.h)
    .attr('fill', d => d.fill);

  // ---------- Axes ----------
  g.append('g').attr('class', 'axis')
    .attr('transform', `translate(0,${innerH})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(d => d + ''))
    .style('opacity', 0)
    .transition().delay(50).duration(500).style('opacity', 1);
  g.append('g').attr('class', 'axis')
    .call(d3.axisLeft(y).ticks(5).tickFormat(d => d + ''))
    .style('opacity', 0)
    .transition().delay(50).duration(500).style('opacity', 1);

  g.append('text').attr('class', 'axis-label')
    .attr('x', innerW / 2).attr('y', innerH + 44).attr('text-anchor', 'middle')
    .text('Ball Stickiness percentile  →  one player dominating possession');
  g.append('text').attr('class', 'axis-label')
    .attr('transform', `translate(-46,${innerH / 2}) rotate(-90)`)
    .attr('text-anchor', 'middle')
    .text('Motion Death percentile  →  bodies standing still');

  // ---------- Quadrant lines ----------
  g.append('line').attr('class', 'quad-line')
    .attr('x1', x(50)).attr('x2', x(50)).attr('y1', 0).attr('y2', innerH);
  g.append('line').attr('class', 'quad-line')
    .attr('x1', 0).attr('x2', innerW).attr('y1', y(50)).attr('y2', y(50));

  // ---------- Quadrant labels (clickable) ----------
  // Placement note: y-axis is inverted, so high motion death (C2) renders at the
  // TOP of the chart. Q1/Q2 are low-C2 (bottom); Q3/Q4 are high-C2 (top).
  const quadDefs = [
    { id: 'Q1', text: 'Q1 · Designed offense',          tx: 8,   ty: 4,  anchor: 'start' },
    { id: 'Q2', text: 'Q2 · Star-anchored design',       tx: 92,  ty: 4,  anchor: 'end'   },
    { id: 'Q3', text: 'Q3 · Single-star pickup',         tx: 92,  ty: 96, anchor: 'end'   },
    { id: 'Q4', text: 'Q4 · Distributed pickup',         tx: 8,   ty: 96, anchor: 'start' },
  ];
  let isolatedQuad = null;

  g.selectAll('.quad-label').data(quadDefs).enter()
    .append('text')
    .attr('class', d => `quad-label ${d.id === 'Q4' ? 'q4' : ''}`)
    .attr('x', d => x(d.tx)).attr('y', d => y(d.ty))
    .attr('text-anchor', d => d.anchor)
    .text(d => d.text)
    .on('click', (event, d) => toggleQuadrant(d.id));

  function inQuadrant(d, q) {
    if (q === 'Q1') return d.C1 <  50 && d.C2 <  50;
    if (q === 'Q2') return d.C1 >= 50 && d.C2 <  50;
    if (q === 'Q3') return d.C1 >= 50 && d.C2 >= 50;
    if (q === 'Q4') return d.C1 <  50 && d.C2 >= 50;
  }

  function toggleQuadrant(q) {
    isolatedQuad = (isolatedQuad === q) ? null : q;
    g.selectAll('.quad-label').classed('active', false);
    if (isolatedQuad) g.selectAll('.quad-label').filter(d => d.id === isolatedQuad).classed('active', true);

    g.selectAll('.dot.dim-target, .label-group.dim-target')
      .transition().duration(280).ease(d3.easeCubicInOut)
      .style('opacity', d => isolatedQuad && !inQuadrant(d, isolatedQuad) ? 0.08 : 1);

    // Special handling for Wolves trajectory: dim entire layer unless Q4 selected or no isolation
    g.select('.wolves-layer')
      .transition().duration(280).ease(d3.easeCubicInOut)
      .style('opacity', (isolatedQuad && isolatedQuad !== 'Q4') ? 0.08 : 1);
  }

  // ---------- Partition the data ----------
  const background = raw.filter(d => !d.is_cohort && !d.is_wolves_traj && !d.anchor_label);
  const anchors    = raw.filter(d => d.anchor_label && !d.is_cohort && !d.is_wolves_traj);
  const cohort     = raw.filter(d => d.is_cohort && !d.is_wolves_traj);
  const wolves     = raw.filter(d => d.is_wolves_traj).sort((a, b) => a.year - b.year);

  // ---------- Layers (order matters for z-stacking) ----------
  const bgLayer       = g.append('g').attr('class', 'bg-layer');
  const anchorLayer   = g.append('g').attr('class', 'anchor-layer');
  const cohortLayer   = g.append('g').attr('class', 'cohort-layer');
  const wolvesLayer   = g.append('g').attr('class', 'wolves-layer');

  // ---------- Tooltip ----------
  const tt = d3.select('#tooltip');
  let tipTimer = null;

  function resultClass(po) {
    if (!po) return 'mid';
    // Reached or won the Finals
    if (po === 'Champion' || po.startsWith('Won Finals') || po.startsWith('In Finals')) return 'good';
    // Made the conference finals (eliminated there, won there, or currently there)
    if (po.startsWith('Lost CF') || po.startsWith('Won CF') || po.startsWith('In CF')
        || po.startsWith('Lost Finals') || po.startsWith('Won R2')) return 'good';
    // Made round 2 (eliminated there or currently there)
    if (po.startsWith('Lost R2') || po.startsWith('In R2') || po.startsWith('Won R1')) return 'mid';
    return 'bad';
  }
  function showTip(event, d) {
    clearTimeout(tipTimer);
    const team_year = `${d.team} ${d.season}`;
    tt.html(`
      <div class="tt-team">${team_year}</div>
      <div class="tt-result ${resultClass(d.po_result)}">${d.po_result}</div>
      <table>
        <tr><td class="lbl">Sharp LAFI</td><td class="val">${d.sharp_lafi}</td></tr>
        <tr><td class="lbl">Full LAFI</td><td class="val">${d.full_lafi}</td></tr>
        <tr><td class="lbl">Ball Stickiness</td><td class="val">${d.C1}</td></tr>
        <tr><td class="lbl">Motion Death</td><td class="val">${d.C2}</td></tr>
        <tr><td class="lbl">Iso Reliance</td><td class="val">${d.C3}</td></tr>
        <tr><td class="lbl">Action Poverty</td><td class="val">${d.C4}</td></tr>
        <tr><td class="lbl">Shot Quality Decay</td><td class="val">${d.C5}</td></tr>
      </table>
    `);
    moveTip(event);
    tt.classed('visible', true);
  }
  function moveTip(event) {
    const pad = 16;
    const ttNode = tt.node();
    const ttRect = ttNode.getBoundingClientRect();
    let left = event.clientX + pad;
    let top  = event.clientY + pad;
    if (left + ttRect.width  > window.innerWidth)  left = event.clientX - ttRect.width  - pad;
    if (top  + ttRect.height > window.innerHeight) top  = event.clientY - ttRect.height - pad;
    tt.style('left', `${left + window.scrollX}px`).style('top', `${top + window.scrollY}px`);
  }
  function hideTip() {
    tipTimer = setTimeout(() => tt.classed('visible', false), 60);
  }

  function bindTip(sel, scaleOnHover) {
    sel
      .on('mouseover', function(event, d) {
        showTip(event, d);
        if (scaleOnHover) {
          d3.select(this).transition().duration(160).ease(d3.easeCubicOut)
            .attr('r', scaleOnHover.hover);
        }
      })
      .on('mousemove', moveTip)
      .on('mouseout', function() {
        hideTip();
        if (scaleOnHover) {
          d3.select(this).transition().duration(220).ease(d3.easeCubicOut)
            .attr('r', scaleOnHover.base);
        }
      });
  }

  // ---------- Background dots (cascade in by distance from center) ----------
  const bgDots = bgLayer.selectAll('circle').data(background).enter()
    .append('circle')
    .attr('class', 'dot dim-target bg-dot')
    .attr('cx', d => x(d.C1)).attr('cy', d => y(d.C2)).attr('r', 0);
  bindTip(bgDots, { base: 3.2, hover: 5.5 });

  if (reducedMotion) {
    bgDots.attr('r', 3.2);
  } else {
    bgDots
      .transition()
      .delay((d, i) => {
        // Stagger by distance from (50, 50): center dots first, outer last.
        const dx = d.C1 - 50, dy = d.C2 - 50;
        const dist = Math.sqrt(dx*dx + dy*dy);
        return 150 + dist * 9;
      })
      .duration(420).ease(d3.easeCubicOut)
      .attr('r', 3.2);
  }

  // ---------- Anchor dots + labels ----------
  const anchorDots = anchorLayer.selectAll('circle').data(anchors).enter()
    .append('circle')
    .attr('class', d => `dot dim-target anchor-dot ${d.is_contender ? 'contender' : ''}`)
    .attr('cx', d => x(d.C1)).attr('cy', d => y(d.C2)).attr('r', 0);
  bindTip(anchorDots, { base: 5.5, hover: 7.5 });

  const anchorLabels = anchorLayer.selectAll('text').data(anchors).enter()
    .append('text')
    .attr('class', d => `anchor-label label-group dim-target ${d.is_contender ? 'contender' : ''}`)
    .attr('x', d => x(d.C1) + 8).attr('y', d => y(d.C2) + 3)
    .text(d => `${d.anchor_label} ${d.season}`)
    .style('opacity', 0);

  if (reducedMotion) {
    anchorDots.attr('r', 5.5);
    anchorLabels.style('opacity', 1);
  } else {
    anchorDots
      .transition().delay((d, i) => 1500 + i * 60).duration(380).ease(d3.easeBackOut.overshoot(1.4))
      .attr('r', 5.5);
    anchorLabels
      .transition().delay((d, i) => 1700 + i * 60).duration(380).ease(d3.easeCubicOut)
      .style('opacity', 1);
  }

  // ---------- Cohort dots + labels ----------
  const cohortDots = cohortLayer.selectAll('circle').data(cohort).enter()
    .append('circle')
    .attr('class', 'dot dim-target cohort-dot')
    .attr('cx', d => x(d.C1)).attr('cy', d => y(d.C2)).attr('r', 0);
  bindTip(cohortDots, { base: 7.5, hover: 10 });

  const cohortLabels = cohortLayer.selectAll('text').data(cohort).enter()
    .append('text')
    .attr('class', 'cohort-label label-group dim-target')
    .attr('x', d => x(d.C1) + 11).attr('y', d => y(d.C2) + 4)
    .text(d => `${d.team} ${d.season}`)
    .style('opacity', 0);

  if (reducedMotion) {
    cohortDots.attr('r', 7.5);
    cohortLabels.style('opacity', 1);
  } else {
    cohortDots
      .transition().delay((d, i) => 2100 + i * 80).duration(460).ease(d3.easeBackOut.overshoot(1.8))
      .attr('r', 7.5);
    cohortLabels
      .transition().delay((d, i) => 2350 + i * 80).duration(380).ease(d3.easeCubicOut)
      .style('opacity', 1);
  }

  // ---------- Wolves trajectory setup ----------
  // Arrow marker definition (drop-in)
  svg.append('defs').append('marker')
    .attr('id', 'arrow').attr('viewBox', '0 0 10 10').attr('refX', 8).attr('refY', 5)
    .attr('markerWidth', 7).attr('markerHeight', 7).attr('orient', 'auto-start-reverse')
    .append('path').attr('d', 'M 0 0 L 10 5 L 0 10 z').attr('fill', 'var(--wolves-blue)');

  const arrowPaths = wolvesLayer.selectAll('path').data(d3.pairs(wolves)).enter()
    .append('path')
    .attr('class', 'wolves-arrow')
    .attr('d', ([a, b]) => {
      const x1 = x(a.C1), y1 = y(a.C2), x2 = x(b.C1), y2 = y(b.C2);
      const dx = x2 - x1, dy = y2 - y1;
      const len = Math.sqrt(dx*dx + dy*dy);
      const pad = 14;
      const ux = dx / len, uy = dy / len;
      return `M ${x1 + ux * pad} ${y1 + uy * pad} L ${x2 - ux * pad} ${y2 - uy * pad}`;
    })
    .attr('marker-end', 'url(#arrow)')
    .style('opacity', 0);

  const wolvesDots = wolvesLayer.selectAll('circle.wolves-dot').data(wolves).enter()
    .append('circle')
    .attr('class', (d, i) => `dot wolves-dot ${i === wolves.length - 1 ? 'current' : ''}`)
    .attr('cx', d => x(d.C1)).attr('cy', d => y(d.C2))
    .attr('r', 0);

  const baseRadius = (d, i) => i === wolves.length - 1 ? 10 : 6.5;
  const hoverRadius = (d, i) => i === wolves.length - 1 ? 13 : 9;
  wolvesDots.each(function(d, i) {
    d3.select(this).datum({...d, _i: i});
  });
  wolvesDots
    .on('mouseover', function(event, d) {
      showTip(event, d);
      d3.select(this).transition().duration(160).ease(d3.easeCubicOut).attr('r', hoverRadius(d, d._i));
    })
    .on('mousemove', moveTip)
    .on('mouseout', function(event, d) {
      hideTip();
      d3.select(this).transition().duration(220).ease(d3.easeCubicOut).attr('r', baseRadius(d, d._i));
    });

  const wolvesLabels = wolvesLayer.selectAll('text').data(wolves).enter()
    .append('text')
    .attr('class', (d, i) => `wolves-label label-group ${i === wolves.length - 1 ? 'current' : ''}`)
    .attr('x', d => x(d.C1) + 13)
    .attr('y', d => y(d.C2) - 9)
    .text(d => `MIN ${d.season}`)
    .style('opacity', 0);

  // Continuous pulse ring around the current dot (added once, reused)
  const currentWolves = wolves[wolves.length - 1];
  const pulseRing = wolvesLayer.append('circle')
    .attr('class', 'pulse-ring')
    .attr('cx', x(currentWolves.C1)).attr('cy', y(currentWolves.C2))
    .attr('r', 10);

  let pulseActive = false;
  function startPulse() {
    if (pulseActive || reducedMotion) return;
    pulseActive = true;
    const tick = () => {
      if (!pulseActive) return;
      pulseRing
        .attr('r', 10).style('opacity', 0.6).attr('stroke-width', 2)
        .transition().duration(1600).ease(d3.easeCubicOut)
        .attr('r', 26).style('opacity', 0).attr('stroke-width', 0.5)
        .on('end', tick);
    };
    tick();
  }
  function stopPulse() {
    pulseActive = false;
    pulseRing.interrupt().style('opacity', 0);
  }

  // ---------- Trajectory animation ----------
  const replayBtn = d3.select('#replay');

  function runTrajectoryAnimation() {
    stopPulse();
    replayBtn.attr('disabled', true);

    wolvesDots.interrupt().attr('r', 0);
    wolvesLabels.interrupt().style('opacity', 0);
    arrowPaths.interrupt()
      .style('opacity', 0)
      .attr('stroke-dashoffset', null)
      .attr('stroke-dasharray', null);

    const dwell = reducedMotion ? 150 : 850;  // ms per Wolves season
    const totalMs = wolves.length * dwell + 600;

    wolves.forEach((d, i) => {
      const isCurrent = i === wolves.length - 1;

      // Dot pops in with overshoot
      wolvesDots.filter((_, idx) => idx === i)
        .transition().delay(i * dwell).duration(reducedMotion ? 60 : 520)
        .ease(d3.easeBackOut.overshoot(2))
        .attr('r', baseRadius(d, i));

      // Label fades in slightly after the dot
      wolvesLabels.filter((_, idx) => idx === i)
        .transition().delay(i * dwell + (reducedMotion ? 20 : 160)).duration(reducedMotion ? 60 : 420)
        .ease(d3.easeCubicOut)
        .style('opacity', 1);

      // Arrow draws from previous dot to this one
      if (i > 0) {
        const path = arrowPaths.filter((_, idx) => idx === i - 1);
        const node = path.node();
        if (node) {
          const total = node.getTotalLength();
          path
            .attr('stroke-dasharray', `${total} ${total}`)
            .attr('stroke-dashoffset', total)
            .style('opacity', 1)
            .transition().delay(i * dwell - (reducedMotion ? 0 : 300)).duration(reducedMotion ? 60 : 600)
            .ease(d3.easeCubicInOut)
            .attr('stroke-dashoffset', 0);
        }
      }

      // Synchronize the subtitle narrative with this season landing.
      const narrativeDelay = i * dwell + (reducedMotion ? 30 : 240);
      setTimeout(() => setSubtitleNarrative(d.year, isCurrent), narrativeDelay);
    });

    // After all dots in, emphasize the current dot, start pulse, show onboard hint
    setTimeout(() => {
      replayBtn.attr('disabled', null);
      startPulse();
      if (onboardEl) onboardEl.classList.add('visible');
    }, totalMs);
  }

  // ---------- Initial choreography ----------
  // Background dots cascade ~150ms - 1500ms
  // Anchors enter ~1500ms - 1900ms
  // Cohort enters ~2100ms - 2800ms
  // Trajectory begins ~3000ms
  setTimeout(runTrajectoryAnimation, reducedMotion ? 100 : 3000);

  replayBtn.on('click', () => {
    if (replayBtn.attr('disabled')) return;
    runTrajectoryAnimation();
  });

  d3.select('#reset').on('click', () => {
    isolatedQuad = null;
    g.selectAll('.quad-label').classed('active', false);
    g.selectAll('.dot.dim-target, .label-group.dim-target')
      .transition().duration(240).ease(d3.easeCubicInOut)
      .style('opacity', 1);
    g.select('.wolves-layer')
      .transition().duration(240).ease(d3.easeCubicInOut)
      .style('opacity', 1);
  });

  // Subtle quadrant highlight on label hover
  g.selectAll('.quad-label')
    .on('mouseenter', function(event, d) {
      g.select(`.quad-bg-${d.id}`).classed('q4-highlight', true);
    })
    .on('mouseleave', function(event, d) {
      g.select(`.quad-bg-${d.id}`).classed('q4-highlight', false);
    });

  // ---------- Legend hover-to-highlight ----------
  // Each legend item gets data-group; map group to selector + label predicate.
  const GROUP_DOT_PREDICATE = {
    'wolves-current': d => d.is_wolves_traj && d.year === 2025,
    'wolves-traj':    d => d.is_wolves_traj,
    'cohort':         d => d.is_cohort && !d.is_wolves_traj,
    'contender':      d => d.is_contender,
    'archetype':      d => d.anchor_label && !d.is_contender,
    'background':     d => !d.is_cohort && !d.is_wolves_traj && !d.anchor_label,
  };
  const legendItems = document.querySelectorAll('.legend-item');
  legendItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
      const group = item.dataset.group;
      const pred = GROUP_DOT_PREDICATE[group];
      if (!pred) return;
      legendItems.forEach(li => {
        if (li !== item) li.classList.add('legend-dim');
      });
      g.selectAll('.dot').transition().duration(200).ease(d3.easeCubicInOut)
        .style('opacity', d => pred(d) ? 1 : 0.08);
      g.selectAll('.label-group').transition().duration(200).ease(d3.easeCubicInOut)
        .style('opacity', d => pred(d) ? 1 : 0.08);
      // The wolves layer overall - keep visible if any wolves match
      const wolvesMatch = group === 'wolves-traj' || group === 'wolves-current';
      g.select('.wolves-layer').transition().duration(200).ease(d3.easeCubicInOut)
        .style('opacity', (group === 'background' || group === 'cohort' || group === 'contender' || group === 'archetype') ? 0.08 : 1);
    });
    item.addEventListener('mouseleave', () => {
      legendItems.forEach(li => li.classList.remove('legend-dim'));
      // Restore (respect any active quadrant isolation)
      const restorePredicate = isolatedQuad
        ? d => inQuadrant(d, isolatedQuad)
        : () => true;
      g.selectAll('.dot').transition().duration(200).ease(d3.easeCubicInOut)
        .style('opacity', d => restorePredicate(d) ? 1 : 0.08);
      g.selectAll('.label-group').transition().duration(200).ease(d3.easeCubicInOut)
        .style('opacity', d => restorePredicate(d) ? 1 : 0.08);
      g.select('.wolves-layer').transition().duration(200).ease(d3.easeCubicInOut)
        .style('opacity', (isolatedQuad && isolatedQuad !== 'Q4') ? 0.08 : 1);
    });
  });

  // ---------- Reset button also resets subtitle ----------
  d3.select('#reset').on('click.subtitle', () => {
    setSubtitleDefault();
  });

  // ---------- Replay also resets subtitle to default before animating ----------
  replayBtn.on('click.subtitle', () => {
    if (replayBtn.attr('disabled')) return;
    setSubtitleDefault();
    if (onboardEl) onboardEl.classList.remove('visible');
  });

  // ---------- Cohort label collision avoidance (simple vertical offset) ----------
  // After cohort labels are placed, walk through pairs and offset any that overlap.
  function resolveCohortLabelCollisions() {
    const labels = cohortLayer.selectAll('text.cohort-label').nodes();
    if (labels.length === 0) return;
    const boxes = labels.map(n => {
      const b = n.getBBox();
      return { node: n, x: b.x, y: b.y, w: b.width, h: b.height };
    });
    const overlap = (a, b) =>
      a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;

    // Multi-pass: sort by y, push overlapping pairs downward by 14px
    for (let pass = 0; pass < 6; pass++) {
      boxes.sort((a, b) => a.y - b.y);
      let moved = false;
      for (let i = 0; i < boxes.length; i++) {
        for (let j = i + 1; j < boxes.length; j++) {
          if (overlap(boxes[i], boxes[j])) {
            const shift = (boxes[i].y + boxes[i].h) - boxes[j].y + 2;
            boxes[j].y += shift;
            const cy = parseFloat(boxes[j].node.getAttribute('y'));
            boxes[j].node.setAttribute('y', cy + shift);
            moved = true;
          }
        }
      }
      if (!moved) break;
    }
  }
  // Run after the cohort labels are rendered (post initial animation).
  setTimeout(resolveCohortLabelCollisions, reducedMotion ? 100 : 2900);
})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data = load_data()
    print(f"Loaded {len(data)} team-seasons.")
    n_cohort = sum(1 for d in data if d["is_cohort"])
    n_traj   = sum(1 for d in data if d["is_wolves_traj"])
    n_anchor = sum(1 for d in data if d["anchor_label"])
    print(f"  Cohort: {n_cohort} | Wolves trajectory: {n_traj} | Anchors: {n_anchor}")

    # Sanity check the cohort
    cohort_teams = [(d["team"], d["season"], d["sharp_lafi"], d["po_result"])
                    for d in data if d["is_cohort"]]
    print("  Cohort members:")
    for t in cohort_teams:
        print(f"    {t[0]} {t[1]} | Sharp LAFI {t[2]} | {t[3]}")

    out_dir = ROOT / "outputs/charts/q0a_lafi"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "quadrant_interactive.html"

    json_data = json.dumps(data, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("__DATA__", json_data)
    out_path.write_text(html, encoding="utf-8")
    print(f"\nWrote {out_path} ({len(html)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
