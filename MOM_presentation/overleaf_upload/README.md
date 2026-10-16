# Overleaf upload (WTP basis; employer results = appended sample, n = 397)

Upload `main.tex`, `figures/` and `tables/` to the root of an Overleaf project, or upload `../MOM_overleaf_upload.zip`.
Compile with pdfLaTeX (twice). Tested here with TeX Live: 0 errors, no undefined references, no overfull frames.

Rules applied (16 Oct 2026):
* All main and appendix results use **all respondents** (no Lucid-excluded values, no dagger ranges).
* **No equal-pay shares**: everything is a WTP in % of pay.
* One sign convention: **positive = pay given up**. PMEs: pay they would give up; employers: pay cut they would require
  (= minus the employer model's WTP). Gap = employers' required cut minus PMEs' accepted cut (positive = friction).
* The appendix shows robustness for both sides: excluding `salary_out` outliers, top/bottom 1% income trim, same-side
  respondents, position term (`T_emp_robust` PMEs, `T_org_robust` employers).

Figures: `scripts/fig_wtp.py`, `scripts/fig_backup_wtp.py` read `data/wtp_deck.csv` (built by `scripts/build_wtp_data.py`).
Tables: `scripts/make_tables_wtp.py` writes T_gap, T_org_pct, T_emp_robust, T_org_robust; the other tables were edited in place.
Slide-by-slide changes: `../latex/CHANGES_wtp_update.md`. `main_compiled_preview.pdf` is the compiled deck.
