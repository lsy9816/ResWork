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

- Slide 13 figure: five arrangements (job sharing and part-time dropped; full seven in backup B-org-concerns4).

- Slide 13 legend: "Agrees with the concern (4-5 of 5)" vs "Neutral or disagrees (1-3)" (split is score > 3 in the code).

- Slide 13 legend shortened to "Agree" / "Neutral or disagree"; definition (4-5 vs 1-3) in the note.

- Legends moved to the bottom (centred) on slides 12 and 13 and the four-concern backup, as on the other figures; slide 12 figure 5.5 cm tall.

- Slide 12 legend shortened to "Most roles" / "Some or few roles".

- Legends without n on slides 12 and 14 (F_where_pres_m, F_why_pmes).

- Slide 14: test annotations (Groups differ / No difference detected) removed from F_why_pmes; group sizes added to the speaker notes of slides 12-14.

- Slides 8-9 captions: plain wording (more days at home -> more value / bigger cut; fully remote most), numbers left to the figure.

- Slides 8-9 captions now name each figure's own feature (compressed week = 1-2 days at home; staggered hours not valued / part-time cut large, compressed and staggered smallest).

- Slide 14 legend: "Expect a penalty" (agree 4-5, n=455) vs "Neutral or disagree" (1-3, n=565); the old "No expected penalty" was wrong because the comparison group includes neutral answers.

- Slides 14-19 reworked: 14 caption states 45%; 15 = awareness by seniority + route by which an FWA is set up (F_barriers_r5 rebuilt, request item not used because it was partly misread); 16 zone table covers all seven arrangements grouped by gap (no policy-move column); limits slide moved before the options; options banner shortened and tied to zones A-C; conclusion takeaways rewritten; speaker notes updated.

- Slide 15: awareness card now shows heard-of (83%) and know-key-provisions (55%) with the seniority split; route card adds the don't-know row.

- Slides 14-15 swapped and slide 14 (now by job level) rebuilt: F_barriers_r5 shows familiarity with the Guidelines and pay given up for WFH (three levels) by junior/middle/senior; career-penalty slide is now 15 and leads into the synthesis. Notes updated.

- Joint-test statements removed from the main-slide speaker notes (slides 13-14); results are reported test by test.

- Slides 16-18: zone table replaced by a findings-to-implications synthesis (no zone letters); limits slide removed from the main deck (B-limits stays); options rebuilt as A pilot, B review (tasks and 3-4 day trial where roles allow), C inform and safeguard, D measure; takeaways and notes updated.

- Slides 16-18 simplified: one short line per finding and per option; takeaways shortened.

- HR/manager guidance and training added: slide 16 row 3 points to "Guidance and HR training"; option C "Inform: juniors, HR; appraise by output"; notes cite 14% managerial resistance and 58% employer familiarity.

- Slide 14: left card now shows FWA availability (any of five) and Guidelines familiarity by job level (scripts/pme_level_access.py -> data/pme_level_access.csv); title "All levels value WFH alike, but juniors have less access".

- Slides 16-17: row and option wording follow the job-level findings (little WFH cut where roles need no presence -> start with 1-2 days; juniors have less access -> open access; appraise by output at all levels); notes updated.

- Slides 16-17 merged into one findings-to-directions table with option letters A-D (links to back-ups); options table with owners and evidence strength removed from the main deck; closing slide now "Summary and discussion" with a neutral discussion prompt (no "we propose D and A"). Main deck is 18 slides.

- Slides 16-17: results summary ("What we found", four lines) and policy directions (Direction / Based on, slide numbers, letters A-D link to the back-ups); discussion prompt on the policy slide; old summary-and-decision slide removed.

- Appendix aligned with the main deck: zone slides (B-framework, B-zones) removed; direction back-ups A-E (B-optA..E; new C managers and HR, new D juniors, old D measurement is now E); new B-level-access; index updated; joint-test p values removed from captions and T_concerns; M-conclusion back-links relabelled Summary; Findings -> Directions.

- Joint tests removed everywhere: p/q columns dropped from F_emp_groups, F_groups_m, F_org_splits (figures regenerated), B-why-pmes and B-why-org tables, T_access; B-why-org-tests removed; slide 12 note no longer cites the joint presence test. Individual tests and 95% intervals stay.

## 21 Oct 2026 - links, new appendix pages, background checks
- Main links: policy slide letters A-E -> B-optA..B-optE (C, D linked; E fixed; B-optE added to the frame list); buttons: policy slide -> Next steps / Survey items / Pilot checklist; results summary -> Limits / Robustness; slides 8-10 got back-up buttons; slide 13 -> Other traits; slide 15 -> Use / Value.
- New back-ups: B-org-other (employer values by plans, hiring difficulty, talent belief, turnover, technology; scripts/fwa_employer_other.py -> results_fwa/employer_other.csv), B-use-att and B-wtp-att (use and PME values by career worry and stigma; data/emp_*.csv from Dropbox dta; scripts/fig_backup_att.py), B-sg-reports (MOM WC 2024 demand/provision; WLH 2020 penalties). No joint tests. "Dominance" check not added (definition not recoverable).
- Background corrections: B-laboursupply support ratio 3.3 (2025) -> 2.7 (2030) and 22.0% housework/caregiving share (LFS 2025), unverifiable 133,500->72,500 removed; B-guidelines grounds wording follows the SNEF-SUSS report.

## 22 Oct 2026 - dominance check added
- B-dominance (Backup after Validity): port of the "Dominance test" in code_final.do (scripts/pme_dominance.py -> data/pme_dominance.csv, pme_dominance_task.csv; scripts/fig_backup_att.py F_dominance). Reproduces the Dropbox plot points exactly (3,150 of 6,120 sets; shares 25-40% when the dominant job pays less, 79-86% when more). Linked from B-validity and the full index.

## 22 Oct 2026 - subgroup slide (B-groups) redone
- B-groups now shows, for all seven arrangements, the difference in pay given up between groups (women-men, 40+ vs under 40, caregiving-none) with 95% CIs (F_groups_diff, scripts/fig_backup_att.py; data deck_support/data/dce_emp_het.csv pairwise rows). Old title "No clear subgroup differences" rested on joint tests / BH over 198 contrasts and was not supported at the individual level: women +8.5 points for 3-4 WFH days (p = .004), 40+ -7.0 for staggered hours (p = .02). Title, caption, note, B-emp-groups title and B-ra-* captions (gender, age, care, role, edu) rewritten on individual tests.

## 22 Oct 2026 - appendix cleaned and reordered (96 -> 83 pages; 78 -> 65 back-ups)
- Removed: B-literature (same table as main slide 4; B-references kept), B-talent (covered by B-org-view / B-triangulation), B-gap and B-org-pct (same numbers as B-fwa-table; the A/B/C "zone" column clashed with Directions A-E), B-why-org (subset of B-org-splits), B-emp-groups (levels already on B-ra-*), B-ra-sameside and B-ra-trim (columns of B-emp-robust), B-industry-note (one line moved to B-industry; its joint-test p removed), B-approvals-tab (6.9% moved to B-approvals note), B-nextsteps (merged into B-limits/B-followup), B-language (speaker guidance, not for the audience), B-governance ([PI to confirm] placeholders; also removed the placeholder line on B-followup).
- Order now follows the main deck: index; background; data and design; PME values; employer values; barriers; compressed week; robustness; limits and directions. Full index and FAQ index rebuilt; all main-slide buttons re-pointed (checked: no dangling links, every back-up is in the full index).

## 22 Oct 2026 - one convention for legends and notes
- Legends: every figure key now sits at the bottom, centred, without n: F_motivation (key moved out of the plot), F_ra_gender/age/care/role/edu (head, n and "lines: 95% CI" removed, key at the bottom), F_career (single key "dashed line: one third" at the bottom). In-figure footnotes removed (F_ra: footnote markers and note; F_career: adjusted-gap and PAP-NTUC lines). scripts/fig_backup_wtp.py patches the professor's figure code in memory (originals untouched). F_emp_wtp, F_org_wtp and F_gap_m are 0.3-0.5 cm shorter so the caption clears the back-up buttons.
- Notes: slide notes trimmed to definitions that are needed to read the figure; dropped "Checked <date>", unweighted/obvious restatements, MOM PQ comparisons that cannot be verified, and notes duplicated between a table's footnote and the slide note (B-hedonic, B-org-salary, B-requestrate, B-setup, B-sample, B-tgfwar, B-validity, B-flexiload, B-org-robust). Table footnote rows shortened (T_access, T_modelfree, T_org_salary, T_emp_all, T_hedonic, T_flexiload, T_fwa_diag); unused tables T_approvals, T_org_pct, T_gap deleted. [PI to confirm] line removed from B-pilot.
