# Overleaf upload (employer results = appended sample, n = 397)

Upload `main.tex`, `figures/` (30 PDFs) and `tables/` (17 .tex; `T_*_main` / `T_remote` are not used by the deck) to the root
of an Overleaf project, or upload `../MOM_overleaf_upload.zip`. Compile with pdfLaTeX (twice). Tested here with
TeX Live 2023: 89 pages, no errors, no undefined references.

* figures/: 14 were redrawn for the appended sample (F_approvals_two, F_awareness, F_industry, F_landscape, F_landscape_m,
  F_meet_r5, F_org_eqpay, F_org_splits, F_org_view, F_paygaps, F_puzzle_r5, F_sample, F_sample_m, F_where_r5); the other 16 are the
  professor's files, unchanged (see fig_sources.json).
* tables/: 10 changed (T_approvals, T_concerns, T_eqpay, T_flexiload, T_gap, T_modelfree, T_org_pct, T_org_salary, T_setup,
  T_yardstick); 7 unchanged (copied from the professor's overleaf/tables).
* main_compiled_preview.pdf: the compiled deck.
* Text changes in main.tex: ../latex/CHANGES_employer_text.md.

Re-run everything (Mac): `python3 ../scripts/port/run_all.py` (analysis -> data/*.csv, mechanisms/*.csv), then build with
`scripts/make_build_tree.sh` + `scripts/build_all.py` (figures and tables from the professor's scripts, copied and patched; originals untouched).
