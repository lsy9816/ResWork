# results_fwa: why are the other FWAs used so little?

Made by `scripts/fwa_diagnosis.py` from the Dropbox `final/` data (read only: employee.dta, snef_employer_appended.dta)
and `data/wtp_deck.csv`. Run: `python3 -I scripts/fwa_diagnosis.py DIR_WITH_employee.dta_and_appended.dta`.
PMEs: 1,004 employed respondents; employers: 397. Employer offering reproduces data/org_fwa.csv exactly.

- `fwa_diagnosis.csv` / `F_fwa_diag.png`: firms offering, PMEs using, pay PMEs would give up, pay cut employers would require, gap
- `fwa_takeup.csv` / `F_fwa_takeup.png`: PME access, use and use among those with access (Wilson 95% intervals)
- `fwa_employer_challenge.csv` / `F_fwa_challenge.png`: employers' biggest challenge (QID50)
- `fwa_current.csv` / `F_fwa_current.png` (scripts/fwa_current.py): pay PMEs would give up, by whether the PME already uses
  the arrangement (current-arrangement interaction model of code_final.do; reproduces the Dropbox figure employee_current_arrangement)
