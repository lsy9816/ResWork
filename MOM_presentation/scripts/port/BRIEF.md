# Shared brief for the employer re-run (Python port of the professor's Stata do-files)

Goal: reproduce, in Python, the EMPLOYER part of the professor's Stata pipeline, validate it on the original 303-firm
sample (must match the professor's CSVs), then run it on the appended sample (397 firms) and write the CSVs.

Paths (SP = /tmp/claude-0/-home-user-ResWork/ddc3d860-5d1b-54ab-bc5b-0b5766ecc715/scratchpad/dl)
- Professor's do-files (READ ONLY): $SP/src/deck_aggregates.do, deck_mech_org.do, deck_mech_compressed.do, deck_eqpay.do, deck_zonetests.do
- Professor's output CSVs for the 303 sample (the validation targets): $SP/ds/data/*.csv and $SP/ds/mechanisms/*.csv
- Data: $SP/src/employer.dta (303 firms, 3,636 rows) and $SP/appended.dta (= snef_employer_appended.dta: 397 firms, 4,764 rows;
  columns identical to employer.dta plus id_new / choice_set_new / source; use id_new and choice_set_new as id / choice_set).
- Helper modules already written and VALIDATED (clogit b and se match Stata's appended_clogit.xlsx to all digits):
  /home/user/ResWork/MOM_presentation/scripts/port/stata_core.py  (clogit with two alternatives per set and cluster-robust
  variance, nlcom delta method, Wald test, wilson CI) and employer_data.py (loads either dta, builds choice-level variables, factor dummies).
  Import with sys.path.insert(0, '/home/user/ResWork/MOM_presentation/scripts/port'). You may extend them only by ADDING functions.
- Write your code in /home/user/ResWork/MOM_presentation/scripts/port/ (new file named in your task). Outputs for the appended
  sample go to the output directory you are given. Scratch/validation outputs go under $SP/val/ .
- Run python with `python3 -I` is NOT required for your own scripts; scipy, statsmodels, pandas, numpy, openpyxl are installed.

Rules
1. NEVER modify anything under the professor's folders or any file in $SP/src or $SP/ds (read only). Do not touch Dropbox, do not git commit/push.
2. Validate first: run your port on employer.dta (303) and compare every row to the professor's CSV
   (same keys; estimates, SE, CI, p within 1e-4 absolute, or 1e-3 for p-values from numerical approximations; counts exact).
   Report the number of rows compared and the max abs difference per column. If something does not reproduce, find out why
   (read the do-file again: sample restrictions, variable definitions, Stata conventions such as xtile, rounding, label text) and fix it.
   Do not hide mismatches; if a few rows cannot be reproduced, list them explicitly.
3. Then run on appended.dta (397 firms) with the same code, output the same CSV schema (same column names/order, same row keys/order as the
   professor's file) into the output directory. Where the do-file has hard-coded sample sizes (e.g. assert r(N) == 303, "303" in notes),
   parameterise them (e.g. n = 397) and keep notes meaningful.
4. Stata conventions to respect: clogit vce(cluster id) uses G/(G-1); `test` is a Wald chi2 test; `nlcom` is the delta method;
   Wilson CIs as in the `wilson` program; xtile/egen/round behaviours as in Stata. Benjamini-Hochberg as the do-file defines it.
5. Be careful with exact-fit/separation in small subgroups: if a Stata model would drop or fail, mimic what the professor's CSV shows.
6. Finish with a short report: files written, validation table (rows compared / max diff), anything not reproduced, and anything in the
   appended-sample result that looks odd (e.g. empty cells, perfect separation).
