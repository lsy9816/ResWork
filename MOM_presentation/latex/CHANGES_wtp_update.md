# WTP update (16 Oct 2026): what changed in main.tex (= latex/main-2.tex)

Decisions: use all respondents everywhere; no Lucid-excluded values (main or appendix); no equal-pay shares; both sides as
pay given up (positive = pay cut); gap = employers' required cut minus PMEs' accepted cut.

## Main slides
| Slide | Change |
|---|---|
| 5 M-framework | Zone map columns now "PMEs give up / Employers require" (pay, no hiring-penalty wording); spoken note rewritten |
| 8 M-estimation | Step 3 and note: one number, % of pay each side gives up or requires (equal-pay share removed) |
| 9 M-descriptive | F_landscape_m with all respondents (6%, no dagger); dagger note removed |
| 10 M-pmes | unchanged (already WTP) |
| 11 M-why-pmes | F_why_pmes: pay given up by career belief (2/10, 2/14, 6/16 vs compressed 10/6); tests p = .002 (location), p = .15 (compressed) |
| 12 M-employers | F_org_wtp: pay cut employers would require (49, 36, 20, 7, 10; reduced load 24, part-time 36); note that cuts above 33% go beyond the pay gaps shown |
| 13 M-where | F_where_r5: required cut by role need (52 vs 3) and creativity concern (61 vs 36); p = .025 (q = .14) and p = .14 |
| 14 M-meet | New title and F_gap_m: dumbbell, PMEs give up vs employers require, gap labels (overlap for the compressed week) |
| 15 M-groups | F_groups_m in WTP; joint tests p = .43 / .09 / .66 |
| 16 M-puzzle | F_puzzle_r5: card 1 = 7% vs 7% of pay (no equal-pay share); take-up 31% (no range) |
| 17 M-barriers | F_barriers_r5 with all-respondent values (45%, 29%, 4%) |
| 18 M-robust | Rows and note updated; Lucid row removed; employers added (up to 3 points) |
| 19 M-discussion | Zone map rewritten as WTP gap: PMEs give up / employers ask / gap / policy move |
| 21 M-limits | Employer splits row; larger employer cuts are extrapolated |

## Backups
Removed: B-panel, B-eqpay, B-org-yardstick (and T_panel, T_eqpay, T_yardstick). Added: B-org-robust (T_org_robust).
Rewritten on WTP: B-zones, B-methods (one formula, sign convention, gap), B-remote-commute, B-why-pmes (fully interacted WTP
tests), B-emp-groups, B-emp-robust (no panel column), B-why-org, B-org-splits, B-why-org-tests (11 tests, BH q), B-org-pct, B-gap.
Lucid/excluded-sample values removed from B-setup, B-approvals-tab, B-requestrate, B-access, B-flexiload, B-career, B-career-who,
B-awareness, B-approvals, B-tgfwar, B-triangulation, B-limits, B-followup, B-optA..C, B-language.

## Notes
* Employer cut sizes above 33% go beyond the 17-33% pay gaps shown; one footnote says so, no band in the figures.
* The employer split tests are now WTP ratio tests with group-specific pay slopes; BH q is over 11 tests (this differs from the
  earlier 20-split, equal-pay q values).
* Source note texts under figures were kept to what the slide needs.

## Commute basis for "fully remote" (final, 16 Oct 2026)
All slides, figures and tables use the logit coefficient `3.place`: fully remote (no commute) vs onsite with a long commute (commute dummies
apply to onsite jobs only, base = long), so PMEs' value includes the end of commuting; employers saw no commute attribute. Label "Fully remote",
footnote 1 says so. Moderate (12.2), short (7.5) and own-commute (12.7) values recombine the same coefficients and appear only in `B-remote-commute`.
PME fully remote 15 [11, 19]; employers 49; gap 34 [23, 44].

## B-remote-commute
Rows: fully remote vs onsite with a long (main), moderate and short commute (re-estimated from employee.dta: 15.08 / 12.23 / 7.51). The
"commute held in the design (weighted)" row (12.7) was removed: the held commute (tasks 1-5) was mis-recorded in the survey code, so
it is not the respondents' own commute. Note: Fully remote changes where you work and removes the commute at once; the estimate cannot separate them.

## Main-slide flow revision (20 Oct 2026) -- scripts/restructure_flow.py (one-off edit of main.tex)

Main deck is now 20 slides: title, motivation, question, **benchmark (new)**, data, design (**now includes the three estimation steps**),
current use, PMEs' value, career concern, employers' required cut, where employers differ, gap, **arrangement diagnosis (new, M-diag)**,
PME barriers, **employer barriers (new, M-employer-barriers)**, zones and policy, options, limits, conclusion, thanks.

Moved to the backups (not deleted; labels renamed M- to B-): literature table (B-literature), three-zone framework (B-framework),
estimation slide (B-estimation), subgroups (B-groups), robustness (B-robust), compressed-week puzzle (B-puzzle-main).
New backups: B-barriers-both (draft of the two barrier slides on one page), B-fwa-current (users vs non-users), B-fwa-table (numbers).
Both backup indexes list the moved and new slides.

New figures (scripts/fig_fwa_m.py, deck style): F_fwa_diag_m, F_fwa_challenge_m, F_fwa_current_m, F_barriers_both_m.
New table: T_fwa_diag (make_tables_wtp.py). Analysis: scripts/fwa_diagnosis.py, scripts/fwa_current.py -> results_fwa/.
Note: firms "offering" in F_fwa_diag_m is the ticked share (as M-descriptive: WFH 78, staggered 37, compressed 17, job sharing 20,
part-time 24); results_fwa/fwa_diagnosis.csv also holds the "adjusted" share (ticked or typical practice: 87, 57, 18, 37, 30).

## Figure simplification (20 Oct 2026)
- No subtitle above any WTP figure (nohead() in fig_wtp.py, fig_backup_wtp.py, fig_fwa_m.py): the slide title and the summary say what is
  shown, and the axis ticks end in %. Regenerated: F_emp_wtp, F_org_wtp, F_gap_m, F_why_pmes, F_where_r5, F_groups_m, F_emp_groups,
  F_org_splits, F_fwa_current_m.
- One colour per series: the grey for the hours-changing rows (job sharing, part-time) is gone; the separator line stays.
- M-design: the three estimation boxes are replaced by one sentence; M-benchmark: "1/3 / Fewer quits".
- F_fwa_diag_m (M-diag): the dot panel is replaced by one "Pay gap, points" column (employers' cut minus PMEs' give-up).
- scripts/restructure_flow.py is a historical one-off; main.tex is the source.
- F_gap_m (M-meet): now the gap itself (employers' cut minus PMEs' give-up) as a dot with 95% CI and a 0 line; no 'gap' word; one-line note under the summary.
- M-descriptive (slide 7) now shows firms offering, PMEs using, and use among PMEs who have access (F_use_m, three columns); the
  former M-diag slide is a backup (B-fwa-diag). Main deck = 19 slides. scripts/restructure_flow2.py (historical; main.tex is the source).
- M-descriptive (slide 7): columns now firms offering | PMEs with access | share using it among them (overall use is in B-fwa-diag/B-fwa-table). B-fwa-diag last column labelled 'Employers' cut minus PMEs' give-up, points'.
- Slide 7: third column now has bars too. B-fwa-diag removed (duplicated slide 12's gap and slide 7); B-fwa-table gained the access column.
- B-barriers-both (draft of a merged barriers slide) deleted: slides 13 and 14 stay separate.
- M-benchmark (slide 4): redrawn as F_benchmark_m (Poland: workers 2.9% vs employers 21% as bars; elsewhere: 4-8%, Singapore 4.8%); the quits-in-a-trial fact moved to the notes and the Trials backup.
- Slide 4 (M-benchmark) rebuilt from the references folder: Poland (workers 2.9% vs employers 21%) plus workers' WFH value in the US (Maestas et al., 4.1%; Mas & Pallais, 8%) and Singapore (Aksoy et al., 4.8%). New backup B-references (Studies) summarises Mas & Pallais, Maestas et al., Aum-Kim-Lee, Wang & Dong and the SNEF FWA Study II note.
- Slide 4 (M-benchmark) is a 3x2 table again (Workers / Employers / Singapore: known so far, this study adds); the Poland bars figure F_benchmark_m was dropped (numbers stay on B-emp-benchmarks).
- Slide 4: removed the closing sentence.
- F_emp_wtp: the grey 'WFH option abroad (4-8%)' band now spans the three WFH rows only.
