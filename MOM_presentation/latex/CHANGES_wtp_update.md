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

## Commute basis for "fully remote" (16 Oct 2026, second update)
`3.place` = remote with no commute vs onsite with a long commute (commute dummies only for onsite jobs, base = long), so it includes the
end of commuting. Employers saw no commute attribute, so PMEs' fully remote is now shown **vs onsite with a moderate commute**
(`b[3.place] - b[commute_mod]`, 12.2 [9.0, 15.5]) on every slide, figure and table. Long (15.1), short (7.5) and own-commute (12.7)
values are in the backup `B-remote-commute` only.
Gender / age / caregiving panels: the point estimates are exact, but their SEs are PROVISIONAL (3.place SE x main-sample ratio) until
`nlcom` output is available (`wtp_deck.csv`, column `provisional`):
    nlcom (remote_mod: 100*(1-exp(-(_b[3.place]-_b[commute_mod])/_b[log_salary]))) , post   // per group, after the group's clogit
