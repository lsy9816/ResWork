#!/bin/bash
# Assemble BUILD (a copy of the professor's folder layout) from: professor's read-only files + MOM_presentation data.
# usage: make_build_tree.sh SRC_DIR BUILD_DIR   (SRC_DIR holds the professor's scripts, CSVs, xlsx, EVIDENCE_BOOK as downloaded)
set -e
SRC=$1; B=$2; MOM="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p $B/table $B/deck_support/{data,mechanisms,scripts,redesign/v3,reviews} $B/overleaf/{figures,tables}
cp $SRC/ds/data/*.csv $B/deck_support/data/; cp $SRC/ds/mechanisms/*.csv $B/deck_support/mechanisms/
for f in dce_design dce_eqpay dce_modelfree dce_org_het dce_org_wtp dce_rank_vs_log org_attitudes org_composition org_fwa; do cp $MOM/data/$f.csv $B/deck_support/data/; done
cp $MOM/mechanisms/employer_channels.csv $MOM/mechanisms/compressed_puzzle.csv $B/deck_support/mechanisms/
cp $SRC/b/table/employee_*.xlsx $B/table/
cp $SRC/src/appended_wtp.xlsx $B/table/employer_wtp.xlsx; cp $SRC/src/appended_clogit.xlsx $B/table/employer_clogit.xlsx
cp $SRC/b/deck_support/EVIDENCE_BOOK.md $B/deck_support/
cp $MOM/latex/main-2.tex $B/overleaf/main.tex 2>/dev/null || cat $MOM/latex/parts/main-2_part*.tex > $B/overleaf/main.tex
for f in fig_backup fig_main fig_r5 fig_v2 figstyle make_tables; do cp $SRC/src/$f.py $B/deck_support/scripts/; done
cp $SRC/figstyle_fallback.py $B/deck_support/scripts/figstyle.py   # adds Liberation Sans after Arial (this machine has no Arial)
python3 $MOM/scripts/deck_patches.py $B/deck_support/scripts
