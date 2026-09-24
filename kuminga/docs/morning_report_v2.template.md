# Morning report: where piece 2 stands

*Rendered from `morning_report_v2.template.md`; every number comes from `outputs/final_numbers.csv`, where each carries its run ID. Supersedes the overnight report of the first run.*

---

## In plain language

**The number.** Minnesota's modelled title odds are **{{title}}** (band {{title_lo}} to {{title_hi}}), **{{title_aged}}** on the aged basis, against a market price of **{{mkt_min}}, {{mkt_min_rank}}th**. On the primary basis all four views price Minnesota below the market (ranks {{min_view_ranks}}). On the aged basis all four still rank it lower ({{min_view_ranks_aged}}) but {{min_above_aged}} views price it above {{mkt_min}}, so the probability gap is all-views only on the primary basis.

**What ships.** {{n_ship}} verdicts hold their sign on both aging bases and clear every view's floor, down from {{n_ship_pre}}: Ball in ({{v_ball_in_u}} un-aged, {{v_ball_in_a}} aged), Reid out ({{v_reid_out_u}}, {{v_reid_out_a}}), DiVincenzo's injury, and Kuminga against four internal alternatives for his minutes. The decomposition had been pricing every combination of moves without Cody Williams on the roster and without the new-arrival minutes rule; with both fixed, other departures, Randle out and Dosunmu re-signed no longer ship, and no single departure ships on its own. "The offseason made Minnesota worse" does not ship: {{off_delta_u}} un-aged but mixed aged, and it turns mixed below {{williams_threshold}} minutes of Cody Williams a night.

**Kuminga.** He beats the most likely internal fill for his minutes by {{v_A_c3_default_shannon_u}} points un-aged and {{v_A_c3_default_shannon_a}} aged, clearing on size. As a scorer and a defender against assigned matchups he sits at or slightly better than the norm. His playoff on-court record is poor ({{po_net}} per {{per100}} possessions over {{po_games}} games) on a small, confounded sample. An opt-out after one season leaves Minnesota a Non-Bird ceiling of {{k_nonbird}}.

**What the evidence can't carry.** Style matchups, playoff translation, versatility and individual matchups all come back as nulls, and "defense travels" is not supported: the estimate is {{ds_coef}} points per game in the other direction, short of the bar.

**Two sentences retracted.** Reid alongside Gobert was no better than Randle alongside Gobert ({{reid_gobert}} against {{randle_gobert}} on correct points), and Kuminga's on/off does not flip sign between his two teams. Both came from a stint pipeline that credited some baskets to the wrong team.

---

## Status

**Done:** M1 to M5, N1 to N8, H1 to H5, W1 to W2, R2 (its Anderson reading superseded by D85), and the eight-section restructure.

**Withheld:** the late-clock split (reconstruction {{lc_g1}} against a bar of {{lc_bar}}).

**Open:** pre-playoff odds for the champion seasons (the preseason column is filled for all eleven from Basketball-Reference); and one hash-pinned fork of the old stint library in the fit engine, which is the last place the points defect lives (D89).

**Settled since:** both points grains are fixed at the source, the lineup one and the possession one under it, and everything built on them is recomputed: five playoff sign changes in the postmortem lineup figures (D88), and RAPM refit across all four views with consensus re-derived (D89). Possession points now reconcile to the box score exactly. The seven shipping verdicts hold under both minutes allocators as well as both aging bases (D87). Run ids are unique by construction (D86).

**To watch first:** Boston's net rating through its {{bos_dec_game}}th game against a threshold of {{bos_dec_threshold}}, and the five claims at game {{w_game}}.
