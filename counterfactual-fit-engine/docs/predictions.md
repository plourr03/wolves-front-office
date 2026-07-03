# Pre-committed predictions log (graded in public; never edited after the fact)

## P-F1 — 2026-07-02, logged at F0 before any model exists
The interaction layer improves on the additive baseline by a small but real
margin: 1-4% possession-weighted RMSE on the sealed window, not more. Fit is
real and modest; anyone promising huge fit effects from public data is
overfitting. (Graded at the G4 sealed one-shot, alongside the A6 noise-floor
ceiling so "small" is judged against what the data can support.)

## P-F2 — 2026-07-02, logged at F0
The Edwards-Ball redundancy score comes out negative but small relative to
their combined talent: the pairing is a net strong lineup with a measurable
redundancy tax, not a broken one. Direction and rough magnitude logged now;
graded when the FROZEN definition (config/redundancy_def.yaml) is first
computed at F6.

## P-F3 — 2026-07-02, logged at F0
The model's largest positive interaction terms league-wide involve elite
spacing bigs next to rim-pressure creators. A sanity prediction about what
the machine should discover if it works; graded from the F4 interaction
diagnostics.

## P-K — 2026-07-03, logged BEFORE the F3 K-selection runs (Bobby's pre-registered lean)
K (Layer 1b latent factor count, chosen from {6, 8, 10} on dev seasons)
resolves to 8. Rationale logged pre-selection so it cannot be back-fit: 6
likely cannot separate the skills the synergy function needs to see
interact; 10 risks noise dimensions; 8 is the usual landing spot for
basketball skill decompositions. Graded at the K-selection presentation,
judged on the reconstruction-vs-K elbow AND the dev-season G3 proxy, not
reconstruction alone. If reconstruction wants 10 but G3 is flat 8->10, 8
is taken for interpretability; disagreement of both -> memo to Bobby.
