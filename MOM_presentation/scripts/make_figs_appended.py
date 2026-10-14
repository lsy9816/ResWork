"""Redraw the employer figures of the MOM deck for the appended employer sample (n = 397).

Uses the professor's figure code in deck_support/scripts (figstyle.py, fig_main.py, fig_v2.py) READ-ONLY:
nothing is written into deck_support. Data come from MOM_presentation/data/, figures go to
MOM_presentation/figures/.

Run (Mac):
    python3 ~/Dropbox/MOM_presentation/scripts/make_figs_appended.py            # all three figures
    python3 ~/Dropbox/MOM_presentation/scripts/make_figs_appended.py F_meet_r5  # one figure
If deck_support is elsewhere:  DECK_SUPPORT=/path/to/deck_support python3 make_figs_appended.py
"""
import csv
import os
import sys
import warnings
from pathlib import Path

sys.dont_write_bytecode = True          # no __pycache__ inside deck_support

MOM = Path(__file__).resolve().parents[1]
DECK = Path(os.environ.get("DECK_SUPPORT",
                           Path.home() / "Dropbox" / "ResWork_SY" / "SNEF_survey" / "final" / "deck_support"))
if not (DECK / "scripts" / "fig_r5.py").exists():
    sys.exit(f"deck_support not found at {DECK}; set DECK_SUPPORT")

sys.path.insert(0, str(DECK / "scripts"))   # professor's modules (read only)
sys.path.insert(0, str(MOM / "scripts"))    # fig_r5_appended

import figstyle as S                        # noqa: E402
S.DATA = MOM / "data"                       # dce_eqpay.csv with the appended employer rows
S.FIGDIR = MOM / "figures"                  # never final/overleaf/figures

import fig_v2 as V                          # noqa: E402

# appended employer group shares for F_where_r5 (replaces mechanisms/employer_channels.csv in memory only)
rows = []
with open(MOM / "data" / "employer_channels_appended.csv", newline="", encoding="utf-8") as f:
    rd = csv.DictReader(f)
    for r in rd:
        r["_line"] = rd.line_num
        rows.append(r)
V._MC["employer_channels.csv"] = rows

import fig_r5_appended as F                 # noqa: E402

if __name__ == "__main__":
    warnings.simplefilter("error", UserWarning)
    names = sys.argv[1:] or ["F_org_eqpay", "F_where_r5", "F_meet_r5"]
    for nm in names:
        print("wrote", F.FIGS[nm]())
    try:
        for nm, (w, h, t) in F.M.measure().items():
            print(f"{nm}: {w:.3f} x {h:.3f} cm (target {t[0]} x {t[1]})")
    except ImportError:
        print("(pymupdf not installed: size check skipped)")
    for fl in dict.fromkeys(F.M.FLAGS):
        print("FLAG:", fl)
