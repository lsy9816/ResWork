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

## 22 Oct 2026 - slide order
- Employer block now: challenges (11) -> concerns (12) -> on-site needs (13) -> PME levels (14) -> career penalty (15). Speaker-note transitions rewritten; on-site note now says it is a more reliable guide than the concerns.
- Slide 16 Employers row: hurdles named, but concerns do not reliably change the pay cut; on-site needs do (WFH). Note updated.

## 22 Oct 2026 - second appendix pass
- In-figure subtitles removed: F_benchmarks (also its in-figure Poland note), F_paygaps, F_career, F_motivation, F_fwa_challenge_m, F_dominance (slide 2 and slide 11 now say the metric in the slide note). Patches in scripts/fig_backup_wtp.py (professor's code untouched).
- "with feature / others" legend renamed "Yes / No" (F_org_splits, F_org_other); the note says yes = as labelled (agree = 4-5 of 5).
- Joint/BH remnants removed: B-methods "Tests" bullet, Wiswall & Zafar joint test on B-validity.
- Back-links fixed: B-org-view (Challenges, Concerns), B-flexiload (Two sides, Directions), B-intl (Slide 4, Directions), B-fwa-table (Practice, Two sides), B-org-concerns (Concerns); B-tgfwar buttons to Approvals and Awareness; "Reservations" renamed "On-site needs". Unused figure files deleted (F_emp_groups, F_groups_m, F_landscape_m, F_ra_sameside, F_ra_trim, F_where_r5).
- B-intl: removed the slide note; the Trip.com co-founder disclosure now sits in the trial bullet.

## 23 Oct 2026 - sample slide and a third notes pass
- F_sample: "Prefer not to say" (0.3%) is now a gender row (the note is gone); the PMEs and Employers headers are centred over their columns with more room above the first sub-head.
- F_landscape: in-figure take-up lines removed (numbers are in B-fwa-table).
- Slide notes removed: M-meet, B-landscape, B-paygaps, B-remote-commute, B-fwa-current, B-modelfree, B-pilot, B-why-pmes (header now "Compressed"), the direction-A footer; others shortened (M-employer-barriers, B-hedonic, B-emp-all, B-org-concerns, B-org-concerns4, B-limits, direction D/E footers).
- B-groups and B-ra-gender/age/care/role/edu: slide notes removed (empty notes no longer print). B-modelfree and B-org-salary: table footnote rows and markers removed; B-org-splits/B-org-other keep only the "Yes = as labelled" line; B-org-concerns4 keeps only the agree definition.
- F_org_splits / F_org_other: n moved to two muted columns ("n yes", "n no") beside the row labels; note now defines Yes and No.
- F_org_splits / F_org_other: n columns dropped again (too busy); the note gives the range of group sizes instead.

## 23 Oct 2026 - employer splits restructured
- B-org-splits "Employer pay cut by firm characteristic: WFH" now shows all 13 splits (8 from wtp_deck.csv + the 5 from results_fwa/employer_other.csv), WFH options only, no n beside labels (group-size range in the note). B-org-other removed (merged). New B-org-policy: no written policy, no WFH today, salary-offset belief and high overall concern, all seven arrangements (same layout as B-org-concerns4). Figures from scripts/fig_backup_att.py (F_org_splits, F_org_policy); F_org_other deleted. Buttons on slide 13 and the index updated.
- Reverted the merge (too busy): B-org-splits (8 splits: roles, policy, concerns) and B-org-other (5 hiring/readiness splits) are separate again, WFH options only, no n beside labels; the four-panel all-arrangements slide (B-org-policy) removed.
- One scale definition everywhere an agree item appears: "Agree = 4-5 of 5; neutral or disagree = 1-3" on M-why-pmes, B-org-concerns, B-career, B-career-who, B-org-view; B-use-att gets disagree/neutral/agree. T_concerns footnote cut to the one marker.
- Outlier definition stated everywhere: monthly salary outside S$2,000-50,000 (both PME and employer samples): B-robust table, B-emp-robust and B-org-robust notes, B-methods, limits note text.
- B-limits: capped salaries made precise (outside S$2,000-50,000: 129 of 1,020 PMEs, 5 of 397 employers; same group as the outlier check).

## 23 Oct 2026 - merged duplicates (83 -> 81 pages)
- B-org-concerns (concerns table) merged into B-org-concerns4: each panel now shows the share of firms that agree (56/54/51/46%, from employer_splits.csv; same numbers as the old table, fairness is new); T_concerns deleted.
- B-tgfwar ("What we can say about the Guidelines") removed: its bullets repeated B-awareness, B-approvals and B-setup; "no before-and-after: we cannot say whether the Guidelines changed outcomes" moved into the B-approvals note. Slide 14 button now "Awareness"; FAQ "Did the Guidelines change outcomes?" points to B-approvals. Links, indexes and frame list checked: no dangling links, every back-up is in the full index.
- B-dominance: title and caption say the choice share rises with the pay gap.
- B-dominance (option A): title "choices rise with pay, as the model predicts"; caption states the rise 25-40% -> 79-86% as modelled.
- F_dominance: the model-prediction key is a line (was a square).

## 23 Oct 2026 - size and respondent-role analyses added (83 pages)
- B-size "No clear difference by organisation size": PMEs by the size of their own organisation (new, scripts/pme_by_size.py -> data/pme_by_size.csv; same model as code_final.do, full sample reproduces 7.4 / 9.5 / 15.1 / 7.4 / -0.7 / 6.0 / 3.9) and employers by firm size (wtp_deck.csv), three size groups x seven arrangements, 0 of 21 pairwise differences significant at 5% on each side. Figure F_size in scripts/fig_backup_att.py; buttons "By size" on slides 8 and 9, link from B-org-view.
- B-org-role "Employer pay cut by who answered" (owner / HR / hiring manager, wtp_deck.csv): 2 of 21 pairwise differences significant (HR vs hiring manager, 3-4 days and job sharing).
- Joint-test remnants removed from source comments (Wiswall-Zafar, groups slide, T_access); no visible joint-test sentence remains.

## 26 Oct 2026 - employer sample updated to 465 firms (303 original + 162 SNEF list; Dropbox final/employer.dta, code_final.do)
- New scripts: make_employer465.py (employer.dta -> port layout), employer_robust.py (outlier-exclusion and 1% trim checks computed in Python, because the new Stata file only has the same-side check). Employer main model reproduces the new Stata employer_wtp.xlsx exactly. The 4 unfinished employer responses are kept, as in code_final.do (Finished==1 | Progress==98). PME side unchanged.
- All employer figures, tables, CSVs regenerated; hard-coded 397 / "2 Oct" removed (F_sample, F_landscape now 465 firms, fielded 12 Aug-21 Oct).
- Main employer pay cuts: 1-2 days 19.6, 3-4 days 39.8, remote 51.9, staggered 9.4, compressed week 10.6 [0.05, 21.1], job sharing 25.8, part-time 37.8. Compressed week gap vs PMEs about 3 points, not significant.
- Text updated: compressed-week puzzle (offered by 71 of 465 firms = 15%; policy 17.8% vs 8.6%; size 11/16/24%, p = .013), cheaper-option share 92% of employer pairs, Guidelines familiarity 63% / heard 32%, challenge shares (productivity 24, fairness 23, coordination 23, managerial 14, security 6, digital 5), group-size ranges, B-org-role (5 of 21 significant, HR > line managers), B-size (0 of 21 on both sides), fairness no longer the top challenge in firms of 200 or fewer staff (productivity 26%, fairness 24%).

## 26 Oct 2026 - three new main slides (86 pages)
- M-intl "Remote work: Singapore and abroad" (after M-motivation): prevalence only (WFH days per week, share working from home, firms offering FWAs); Singapore vs world, English-speaking countries, Asia, EU, Netherlands. Not like-for-like. Numbers come from search-result snippets of the sources (Aksoy et al. PNAS 2025 / GSWA 2023, SIEPR, Eurostat, CBS, MOM PQ 2023, MRSD); primary pages could not be opened here: TODO(PI) check each against its source. The WTP benchmarks stay on M-benchmark / B-emp-benchmarks, so there is little overlap.
- M-keyfindings "Key findings" (after M-benchmark): three headline results + juniors/career line; the fuller summary stays on M-conclusion.
- M-nextsteps "Possible next steps" (after M-discussion): four steps with who could lead; links to B-pilot, B-followup, B-optE, B-limits.
- Added to \ShortLabels / \includeonlyframes; "Slide 4" button labels now read "Literature".
- PME defined at first body use (data slide card: Professionals, managers, executives). Decision on replacing PMEs with "employees": kept PMEs (see reply).
- M-motivation synced with the Overleaf edit (title "Flexible work is mainstream now", caption = definition only, source line only).

- M-intl-wtp "PME values for WFH are at or above estimates abroad" (slide 4, alternative to M-intl; same figure as B-emp-benchmarks). Delete whichever is not used (87 pages with both).

- Title page: optional SNEF and SMU logos (figures/logo_snef.png, figures/logo_smu.png; skipped if missing). Logo files must be added by the PI.

- M-intl-wtp removed from the main flow (same figure is backup B-emp-benchmarks, retitled "Our WFH values are at or above estimates abroad"). M-intl table now Definition / Population / Country / Value / Year; the Singapore "firms offering FWA" row removed (provision, not use; it is on M-motivation). 86 pages.

- M-design (slide 9): drawn cards replaced by screenshots of the survey screens (figures/survey_pme.png, figures/survey_employer.png), side by side; the example screens differ from the old card text (PME S$2,550 vs S$3,300; employer S$4,500 vs S$5,500).

- M-design (slide 9): screenshots redrawn as two LaTeX tables with the survey wording (equal widths, centred cells, shaded rows = attributes that differ); figures/survey_pme.png and survey_employer.png are no longer used. Needs colortbl (added to the preamble).

## 26 Oct 2026 - M-nextsteps emptied (PI request)
Earlier draft, kept here: (1) Trial the compressed week with volunteer firms, independent evaluation (SNEF, with NTUC safeguards; B-pilot); (2) Follow up with the 490 PMEs who agreed to one short survey, Feb-Aug 2027 (NTUC reach; MOM only with fresh consent; B-followup); (3) Add why-not-request and partial-approval items to MRSD surveys (MOM, with NTUC and SNEF; Direction E); (4) Ask on-site need before the choices in any next employer survey (SNEF).

## 26 Oct 2026 - policy directions cut to three, specific (85 pages)
- M-discussion: three rows, each with a concrete action, the result it rests on and how to track it: A trial the compressed week in volunteer firms' written FWA policies (SNEF runs, evaluated); B check roles for on-site need in FWA guidance, start with 1-2 WFH days where none (employer cut 49% vs 3%); C reach juniors through company policies and train HR/managers (access 80 vs 94, familiarity 29 vs 77, 45% career worry).
- Old D (juniors) merged into B-optC; B-optD deleted. Old E now "Measure what is missing (for next steps)" (B-optE) and "Draft survey items" (B-optD-items) stay as backups; index updated.
- B-optB corrected: 49% (was 52%) for 1-2 WFH days; compressed week 6% vs 11%, not significant (was "about 1%").

## 2 Nov 2026 - WFH values abroad back in the main flow
- Backup B-emp-benchmarks moved to the main deck as M-intl-wtp "Our WFH values are at or above estimates abroad", right after M-meet (slide 13); Poland pair in the caption. Buttons and links to B-emp-benchmarks now point to M-intl-wtp; backup index entry kept under the same name. The prevalence slide M-intl stays at slide 3. 85 pages.

## 2 Nov 2026 - partners backups merged; Next steps written
- B-partners (positions) and B-triangulation (their evidence vs ours) merged into one backup "What the partners have said, and what we find": rows MOM / SNEF / NTUC, columns Position / Their evidence / We find. B-triangulation removed; index entry merged. 84 pages.
- M-nextsteps: three steps: matched employer-employee panel (willing firms approached through SNEF, a few PMEs each consenting directly); follow-up of the 490 consenting PMEs plus six-monthly re-surveys; compressed-week trial with a random half of volunteer firms first. Design features follow the harmonised employer-employee panel of the P1 SWDA application (29 Oct 2026); its numbers (firms, waves, skills items) are not used.

## 2 Nov 2026 - Aksoy et al. (2025) checked against the policy brief in Dropbox
- M-intl (slide 3): days-per-week rows replaced by the values in Figure 1 of Aksoy et al. (2025), EconPol Policy Brief 73 (40 countries, 16,422 full-time college-educated workers aged 20-64, Nov 2024-Feb 2025; days with 6+ hours worked at home last week): average 1.2, Singapore 1.2 (N = 419), UK 1.8, USA 1.6, Japan 0.7, South Korea 0.5. The earlier rows (world 1.2-1.3, English-speaking 1.5-2.0, Asia 0.5-1.0, Singapore 0.9 in 2023) came from search snippets and were wrong or not comparable (Singapore 0.9 was an earlier wave, 1.27 is a 22-country balanced panel).
- B-references: Aksoy et al. (2022) setting reworded (Singapore sample about 90% tertiary-educated); row for Aksoy et al. (2025) added. The 2022 paper (27 countries, 5% / Singapore 4.8%) is not in the Dropbox folder: numbers rest on EVIDENCE_BOOK E16 and the 2025 brief's "about 5% of current pay (Aksoy et al 2022)".

## 2 Nov 2026 - Aksoy et al. (BPEA 2022) checked against the paper
- Verified in the paper: WTP for the option to WFH 2-3 days a week = 5% of pay on average (simple mean of country values); Singapore 4.8% (country-level conditional mean, "HE" sample that greatly over-represents highly educated persons); Singapore wave 2 only (27 Jan-4 Feb 2022), raw 1,153, analysis sample 1,002; 89.8% tertiary or more (Table A.4). Mas & Pallais 8% is cited in the paper. Also in the paper (not yet on a slide): Singapore WFH days 2.4 (average 1.5, US 1.6); workers' desired days after COVID 2.3 (average 1.7); employer plans 1.1 (average 0.7); raw means 2.9 / 2.6 / 1.4 days, WTP 6.1.
- M-benchmark Singapore cell: no longer says "No study measures what FWAs are worth" (Aksoy measures WFH in Singapore); now "the one value estimate is for WFH only (4.8%). No study prices other FWAs, or the employer side."
- B-references: Aksoy 2022 setting now "Singapore: n = 1,002, early 2022; about 90% tertiary"; table font reduced to fit.

## 2 Nov 2026 - slide 3 reduced to current use
- M-intl now only the days-worked-from-home block (Aksoy et al. 2025, Fig. 1); the Eurostat, CBS and MOM rows were removed. The WFH value comparison stays after the results (M-intl-wtp, slide 13).

## 2 Nov 2026 - audit
- B-org-concerns4 title: "creativity shows the clearest signal" (4 of 28 concern differences are significant at 5%: creativity 3, productivity 1 for staggered hours; none after correction). The M-concerns speaker note said three of 28; now four.
- B54 (PME robustness) retitled "PME values hold in every sample" (staggered hours is about -0.7, not positive).
- Open: Barrero, Bloom & Davis value in F_benchmarks is 8% (EVIDENCE_BOOK, JEP 2023) but the NBER WP 28731 in the Dropbox folder reports 7.2% (about 7%) for the option to WFH 2-3 days; 8% there is Mas & Pallais. Not changed: the JEP version needs checking.

## 2 Nov 2026 - appendix merge, BBD citation
- B-optE ("Measure what is missing") and B-optD-items ("Draft survey items") merged into one backup, label B-optE, title "Measure what is missing: draft survey items". Links, buttons and the backup index updated. 83 pages.
- M-intl-wtp source note names the Barrero, Bloom & Davis paper behind the 8%: The Evolution of Work from Home (JEP 37(4), 2023; NBER WP 31686). Their earlier paper Why Working from Home Will Stick (NBER WP 28731, 2021) reports 7.2%. The 8% in the 2023 paper rests on search summaries (SIEPR) and is not yet checked verbatim.
- Kept as they are: B5/B6/B7 (different content), B47/B48 (request outcomes vs request-rate base).

## 2 Nov 2026 - Barrero, Bloom & Davis (JEP 2023) verified against the paper
- Barrero, Bloom & Davis (2023), The Evolution of Work from Home, JEP 37(4): 23-50, p. 37: "On average, Americans value the option to work from home two or three days a week at 8 percent of pay, according to data from the Survey of Working Arrangements and Attitudes"; Mas & Pallais find similar estimates for a narrower group. So the 8% (2-3 days, US workers) in F_benchmarks is correct; their 2021 NBER paper (7.2%) is a different paper. The same paper cites Aksoy et al. (2022) for 27 countries and higher WTP among workers with children under 14.
- B-references: row for Barrero, Bloom & Davis (2023) added.

## 2 Nov 2026 - slide 3 takeaway; Next steps redesigned
- M-intl (slide 3): one-line interpretation added ("Singapore's WFH use is at the international average. The open question is less how much, more which arrangements fit whom"), leading into M-question; speaker note extended.
- M-nextsteps redesigned as "Next steps for our research": three cards (1 match firms and their PMEs; 2 follow up our PMEs, the 490 who agreed; 3 evaluate the compressed week in volunteer firms, random half first); "who could lead" removed.

- M-nextsteps: "which step first" line removed; card 2 now "Follow up over time" (panel re-surveyed every six months plus the 490 PMEs who agreed to follow-up). No funding mention on the slide.

- M-nextsteps rebuilt from the P1 application: 1 match firms and their staff; 2 track over time (six-monthly waves, hiring and departures); 3 test a manager guide (random half of firms first). Compressed-week trial and the 490-PME card removed from the slide (both remain in backups B-pilot, B-followup).

## 2 Nov 2026 - slide text cut to what is not obvious from the chart or title
- Removed: slide 3 takeaway (stays in the note); slide 14 both lines; slide 17 both lines; slide 18 both lines; slide 20 "For discussion" line.
- Shortened to the one line that adds something: slide 8 (3 in 10 use), 10 (compressed week = 1-2 days; staggered not valued), 11 (smallest cuts), 15 (creativity signal), 16 (other arrangements, early evidence only). Kept: slides 6, 9, 12, 13 and the backups. The spoken versions are in the speaker notes.

## 2 Nov 2026 - more caption cuts; slides 19 and 20 sharpened
- Removed the captions on slides 10, 11 and 15; slide 14 note "Single biggest challenge per employer" removed and the title now carries it ("Employers' biggest challenge: productivity, coordination, fairness"); slide 16 caption rewritten ("Staggered hours, the compressed week, job sharing and part-time show no such difference. Early evidence only.").
- Slide 19 (What we found): numbers added (7-15% vs 20-52%, gap 12-37 points; compressed week about 7% vs 11%, 15% of firms offer it; 49% vs 3%; access 80% vs 94%; those who fear a penalty give up much less).
- Slide 20 (Policy directions): A pilot the compressed week (same hours over four days) with a comparison group; B add a role-by-role on-site check to FWA guidance, start with 1-2 WFH days in roles that need none; C put what is on offer and how use is appraised into company policy, brief managers on requests; row rules added.

- Slides 10, 11, 14, 15, 17, 18: figures enlarged to 14.5 cm wide (was 13.0) to use the space freed by removed captions (new macro \FigL). Slides 3, 12, 16 unchanged in size.

## 2 Nov 2026 - backup clean-up (81 pages)
- Removed B-landscape ("Flexible work today": PME use is also in the numbers table, employers' typical arrangement only here) and B-laboursupply ("Keeping people in work": MOM context); buttons, index entries and the slide-2 note updated.
- B-partners: Position column removed (partners' positions are not paraphrased to the partners); title "Partners' evidence and ours".
- B-methods (Equations and inference) cut to the equation, two definitions and two caveats.
- B-emp-all note reworded. Kept after review: B-sg-reports, B-cards, B-hedonic, B-validity, B-emp-all, B-fwa-table, B-groups with B-ra-* (gender, age, caregiving, role, education stay by earlier request).

## 2 Nov 2026 - more backup clean-up (78 pages)
- T_emp_all (B-emp-all): "Collaborative culture" row removed.
- B-ra-gender, B-ra-age, B-ra-care removed: B-groups (differences with intervals for gender, age, caregiving) is kept; role and education backups stay because B-groups does not cover them. figures/F_ra_gender, F_ra_age, F_ra_care deleted from the upload folder (scripts/fig_backup_wtp.py can regenerate them).

## 2 Nov 2026 - gender, age and caregiving backups restored (81 pages)
- B-ra-gender, B-ra-age, B-ra-care and their figures put back (PI: keep both the differences, B-groups, and the group-by-group levels). T_emp_all stays without the culture row.

## 2 Nov 2026 - appendix review (80 pages)
- B-why-pmes ("PME splits by seven characteristics") removed (rounded values without intervals; career concern is on slide 18, groups on B-groups); its button on slide 18 and its index entry removed.
- B-fwa-current ("Current users value part-time and staggered hours more") is now a table (tables/T_fwa_current.tex, scripts/make_table_fwa_current.py).
- B-org-concerns4: the "% agree" line above the panels removed (scripts/fig_fwa_m.py, F_org_concerns4_m regenerated).
- Retitled: B-org-salary "Employers respond less to pay, so their % values are less firm" (+ one-line note), B-org-role "Employers' pay cut by respondent role: owner, HR, hiring manager", B-use-att "Use of the arrangement, by career worry and stigma", B-wtp-att "Pay given up, by career worry and stigma". B-career-who: takeaway line added, parents/MOM paragraph removed.
- B-partners: employers who agree FWAs help attract and retain talent corrected to 68% (was 66%, 397-firm value).
- Slide 20 buttons: Follow-up and Survey items removed (not part of the three directions).
- Link check: all 286 internal links in the compiled PDF resolve to the intended page.

- B-partners ("Partners' evidence and ours") removed (PI): other surveys are not like-for-like; slide 4 button and index entry removed. The Guidelines backup restored (it was removed by mistake). 79 pages.

## 2 Nov 2026 - technical backups cut for the government audience (75 pages)
- Removed: B-paygaps ("Every pair differed in pay by 17-33%"), B-methods ("Equations and inference"), B-dominance ("Dominance check"), B-org-salary ("Employers respond less to pay..."). Buttons, index entries and the validity note that pointed to them updated; the pay-gap range stays in B-cards and B-limits.
- B-cards design row: multipliers removed. B-puzzle: odds-ratio column replaced by plain shares of firms offering the compressed week (with p), PME odds ratio removed.
- B-partners removed earlier; B-guidelines kept.
