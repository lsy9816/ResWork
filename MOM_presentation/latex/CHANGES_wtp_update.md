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
- F_emp_wtp: grey 'abroad' band removed (slide 8 compares remote work with the other arrangements; the abroad range is on slide 4 and B-emp-benchmarks).
- Order: data (5), current use (6), design (7), PMEs' value (8). F_emp_wtp / F_org_wtp / F_gap_m are taller (13 x 5.8 / 5.8 / 5.4 cm) now that they have no subtitle.
- Employer heterogeneity (slides 11-12): new analysis scripts/fwa_employer_splits.py (all seven arrangements, by on-site presence need and by the
  productivity, coordination, creativity and fairness concerns; fully interacted model, 397 firms) -> results_fwa/employer_splits.csv.
  Slide 11 (M-where) = F_where_pres_m (presence need x all arrangements); new slide 12 (M-concerns) = F_org_concerns_m (difference per concern).
  Main deck is now 20 slides; the earlier F_where_r5 (presence + creativity, location only) is no longer on a main slide.
- Slide 11 (M-where) summary adds that the other arrangements are rarely offered; M-employer-barriers (firms' main challenge) now comes before it.
  Slide 13 (M-concerns): both groups shown (firm shares the concern / does not) instead of the difference; title "Employers who share a concern tend to ask for more".
- Order (20 Oct 2026, evening): ... 8 PMEs' value, 9 employers' required cut, 10 gap, 11 employers' main challenge, 12 on-site need, 13 concerns,
  14 PMEs' career worry, 15 PME barriers, 16 zones, 17 options, 18 limits, 19 conclusion, 20 thanks. Plain-language titles on slides 5, 7, 9, 14;
  take-aways on the conclusion slide now state the pay PMEs would accept and the 12-34 point gap; notes' transitions follow the new order.
- Slide 4: Employers row now gives the Poland numbers (21% vs 2.9%); Singapore row says official surveys count provision and employers' views but not pay trade-offs. B-references gained Lewandowski et al. and the SNEF-SUSS report.
- Slide 4 Employers row: 'about seven times' the 2.9% workers would give up (21 / 2.9 = 7.2).
- Slide 4 table rewritten around the gap: workers (WFH known, other arrangements much less), employers (one two-sided study found, WFH only), Singapore (official surveys do not measure pay trade-offs).
- Slide 4 'This study adds' column: workers = beyond WFH (hours and workload); employers = the employer side in Singapore on the same cards; Singapore = both sides in one study. Workers' known cell says 'four studies'.
- Slide 4 adds: 'Other FWAs, not only WFH' / 'Singapore employers' required pay cut for each FWA, from the same choices PMEs make' / 'The gap between what PMEs give up and what employers require, FWA by FWA'.
- Slide 4 adds shortened: 'Other FWAs, not only WFH' / 'Singapore employers, for each FWA' / 'The gap between the two sides'.
- Slide 4 Singapore row: official surveys and regressions (MRSD CoE 2024, Working Conditions 2024) show who offers FWAs and how firms and workers rate them, not what they are worth; adds: both sides' prices for each FWA, and the gap. B-references gained the MRSD CoE 2024 row.
- Slide 4 Singapore row: 'No Singapore study measures what FWAs are worth; official surveys show only who offers them'; Workers row notes Singapore 4.8% comes from a 27-country survey.

- Slide 4 / B-references: Aksoy et al. (2022) described as one direct question (2-3 WFH days); Aksoy row added, planning-note row dropped, MRSD row shortened.

- Slide 4 table rewritten: Known so far / This study adds now state direct-question WFH value, Poland WFH-only, seven FWAs incl. WFH, Singapore surveys cover use and provision.

- Slide 4 "This study adds" column: six more FWAs; employers measured the same way; FWA values estimated for Singapore, gap.

- Main slides: centred slides 8-9 (bottom glue), unclipped markers on slides 12-13 (figures regenerated), captions rewritten (days-at-home gradient; employers "expect a pay cut/bigger cuts" instead of "ask for").

- Slide 13: three panels (productivity, coordination, fairness) matching slide 11, title/caption say concerns do not reliably change the cut; creativity shown in new backup B-org-concerns4 (F_org_concerns4_m).
