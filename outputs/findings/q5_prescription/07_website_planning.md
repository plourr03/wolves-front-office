# Website planning: Timberwolves 2025-26 Postmortem and Roster Construction Analysis

**Date:** 2026-05-18
**Status:** Planning doc. Per the data scientist's Option 1 recommendation (start website prep now rather than completing Phase 3 infrastructure first). The website is what makes the work reach the intended audiences.

## Purpose

A public-facing presentation of the project that lets the intended audiences (Timberwolves front office contacts, basketball analytics community, public Wolves observers) engage at the depth that fits them. Layered architecture: headline at the top, paths to depth below, methodology at the bottom.

## Audiences and what each reads

**Timberwolves front office contact (the primary intended reader).** Wants the prescription and the architectural-ceiling framing. Reads the landing page and the prescription page. Maybe browses one or two supporting-evidence pages. Probably never reads methodology unless skeptical.

**Coaching staff contact.** Wants the system analysis (Q0D coaching system findings + the Gobert PR-Roll-Man + Edwards PR-Ball-Handler restoration). Reads the diagnosis page (with emphasis on Section 3 / Q3 mechanism) and the system-restoration section of prescription.

**Analytics colleague (basketball professional).** Wants the analytical depth. Reads the methodology section and dives into specific analyses (LAFI, RAPM, Q4 cluster work). May engage with the findings folder pattern itself.

**Public Wolves observer (educated fan).** Wants the story. Reads the landing page and follows the diagnosis narrative. May skim prescription. Reads the KAT trade in retrospect section because it's politically interesting.

The website's information architecture serves all four. Each can find their entry point and go as deep as their interest carries them.

## Recommended structure

**Page 1: Landing**
- Headline: the architectural ceiling finding + the prescription's path out
- Hero visualization: Q0C cohort outcomes OR Q4 cluster matrix (one of these is the most striking single image)
- Two-paragraph summary
- Navigation to the four substantive sections

**Page 2: The diagnosis**
- Why the Wolves lost in R2
- Section structure: LAFI architecture, Spurs mechanism, matchup vulnerability, DiVincenzo injury timing
- Each section with a clear visualization
- Link to underlying analyses for depth

**Page 3: The prescription**
- The two-archetype framework (Cat B wing + skilled secondary creator)
- The three portfolios (A default, B upside, C trade-driven 2027 path)
- Active trade windows and the contract structure correction
- The Iverson vs Kobe template framing (as illustrative)
- Non-prescriptions section (Giannis/Durant, Gobert trade, roster overhaul) with PHX 23-24 + Embiid 21-22 as cautionary evidence

**Page 4: Supporting evidence (analytics-deep readers)**
- One page per analysis (LAFI / Q1 / Q2 / Q3 / Q4 / Q6 KAT counterfactual / Q7 / Q8 / Q0B / Q0C / Q0D)
- Each summary 200-400 words with the headline finding and the visualization
- Link to the findings folder document for full depth

**Page 5: Methodology**
- The findings folder pattern (chronological reasoning trail, calibration scorecard)
- Confound checks (DiVincenzo lineup confound, Gobert+Naz mislabel, Spurs-specific framing)
- Error corrections (KAT counterfactual v1 to v2, contract structure correction)
- This is the credibility-establishing section for analytically literate readers; demonstrates the project's discipline

## Visualizations needed

**Hero candidates (for landing page):**
- Q0C cohort outcomes (table of 8 teams + outcomes)
- Q4 cluster matrix (5 clusters + Wolves performance per cluster)
- The Edwards-era LAFI trajectory (4 years, 5 components, Q1 to Q4 drift)

**Supporting visualizations:**
- Q0B contention window (per-player trajectory grid)
- Iverson vs Kobe template comparison
- KAT counterfactual Synergy swap (v2)
- Gobert career arc chart (already exists in Q8 findings)
- The four-quadrant framework (Q1/Q2/Q3/Q4 with Wolves' position)
- Spurs vs Wolves LAFI comparison (the 72-percentile-point gap)
- RAPM leaderboard (Wolves rotation + comparison players)
- Salary efficiency table (surplus vs tier threshold)

**Visualization style:** clean, monochrome with one accent color, prioritize legibility over decoration. Basketball charts are a crowded genre; the visual restraint helps the analytical work stand out.

## Technical considerations

**Tech stack options:**
1. **Static site generator (Hugo, Astro, or Eleventy).** Fast, version-controlled, easy to maintain. Markdown-based content matches the findings folder pattern. Recommended.
2. **Notion or Substack.** Faster to publish; less control over visualizations and structure. Acceptable if speed matters more than design.
3. **Custom Next.js / React.** Maximum control; slower to build. Unnecessary for this project.

Recommendation: Astro with Markdown content. Allows embedding the existing analysis CSVs as data sources for visualizations. Good developer experience. Fast page loads.

**Hosting:** GitHub Pages (free, version-controlled) or Vercel (free for small projects, better DX). Either works.

**Charts:** D3.js for custom (Q0C cohort matrix, cluster grid), Observable Plot for simpler bar/line charts, or Plotly for interactive options. Recommendation: Observable Plot for simplicity; D3 only where customization requires it.

**Visual style:** the Pudding (https://pudding.cool) is a good aesthetic reference for sports data journalism. Restrained typography, generous whitespace, clean tables.

## Content sourcing

The findings folder already contains the substantive content. The website pass is principally writing for a different audience:
- More accessible language (less analytical jargon where plain English works)
- Clearer narrative arc per page (landing page especially needs a hook)
- Specific factors acknowledged in the comps (per the v4 refinement notes)
- Illustrative framing on the templates (per the v4 refinement notes)

Estimated content writing time: ~5-7 working days for first draft of all five pages.

## Phasing

**Phase A (week 1):** Tech stack setup, landing page draft, diagnosis page draft.

**Phase B (week 2):** Prescription page draft, supporting-evidence pages (start with 3-4 highest-leverage analyses: LAFI, Q4, Q7, Q0C).

**Phase C (week 3):** Methodology page, remaining supporting-evidence pages, visualizations.

**Phase D (week 4):** Polish, navigation, accessibility, distribution plan.

Total estimate: ~4 weeks to a shippable v1 of the website.

## Distribution plan (rough)

**Soft launch:** share with Bobby's brother-in-law Scott (per CLAUDE.md, a serious Wolves observer whose intuitions have been useful checkpoint data) and one or two analytics colleagues for feedback before any Wolves front office outreach.

**Front office outreach:** through Bobby's existing professional network at MaxPreps and any direct Wolves contacts. Specific page link for each contact based on their role.

**Public release:** Twitter/Threads thread linking to the landing page; HN/Reddit r/timberwolves posts if the work merits broader attention.

**The deliberate pace:** soft launch first to get qualified feedback before the work is exposed to public scrutiny.

## Open questions for Bobby (decisions before deep build)

1. **Tech stack confirmation.** Astro/Markdown recommended. Other options if preferred (Hugo if more familiar; Notion if speed matters most; custom if specific design needed).

2. **Hosting domain.** Use an existing personal domain or buy something Wolves-themed (e.g., wolvesfrontoffice.com if available)?

3. **Pseudonym vs real name.** The deliverable's analytical rigor is the credibility; Bobby's MaxPreps role provides professional context. Probably real name + brief bio paragraph linking to the work.

4. **Phase 3 infrastructure interleave.** Pause Phase 3 entirely until website ships, or run Phase 3 in parallel as background work? Either is defensible.

5. **Publication target date.** Soft launch in ~4 weeks (mid-June 2026) or longer runway? The 2026-27 NBA roster construction window opens in summer 2026, so getting the work in front of front office contacts before they make major moves is the implicit time constraint.

## Recommendation

Confirm tech stack + hosting + name decisions with Bobby before deep build. Then proceed with Phase A (week 1 of the 4-week plan). The four v4 refinement notes get incorporated during the writing pass naturally.

The Phase 3 infrastructure work (full league-wide RAPM, Spotrac integration) can run in parallel as background work if Bobby wants both. Or pause Phase 3 entirely until the website ships.
