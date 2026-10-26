"""run_all -- re-run the employer analyses of the MOM deck on the appended employer sample (397 firms) and write every CSV
the professor's figure and table scripts read for the employer side.

    python3 run_all.py            # uses ~/Dropbox/ResWork_SY/SNEF_survey/final (override: FINAL=/path/to/final)

Reads (read only): FINAL/snef_employer_appended.dta, and the professor's CSVs in FINAL/deck_support/{data,mechanisms} for the
employee side (copied unchanged into the output files that hold both sides). Writes into MOM_presentation/{data,mechanisms}.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
MOM = HERE.parents[1]
FINAL = Path(os.environ.get("FINAL", Path.home() / "Dropbox/ResWork_SY/SNEF_survey/final"))
DECK = Path(os.environ.get("DECK_SUPPORT", FINAL / "deck_support"))
os.environ["DECK_SUPPORT"] = str(DECK)
DTA = Path(os.environ.get("APPENDED_DTA", FINAL / "snef_employer_appended.dta"))
OUT_DATA, OUT_MECH = MOM / "data", MOM / "mechanisms"
OUT_DATA.mkdir(exist_ok=True); OUT_MECH.mkdir(exist_ok=True)

import pandas as pd  # noqa: E402

INT_COLS = {"n_resp", "n_obs", "n_clust", "n", "k", "df", "group", "lr_df", "n_a", "n_b", "n_resp"}


def normalize(path, cols=INT_COLS):
    """Write integer-valued count columns without '.0', as Stata exports them."""
    df = pd.read_csv(path, low_memory=False)
    for c in cols:
        if c in df.columns:
            x = pd.to_numeric(df[c], errors="coerce")
            if x.notna().any() and (x.dropna() == x.dropna().round()).all():
                df[c] = x.astype("Int64")
    df.to_csv(path, index=False)


def main():
    import org_survey, org_het, compressed_employer, run_dce, org_channels
    org_survey.run(str(DTA), True, str(OUT_DATA), expected_firms=int(os.environ.get("N_FIRMS", 397)))
    org_het.run(str(DTA), True, str(OUT_DATA))
    run_dce.run(str(DTA), True, str(OUT_DATA), str(DECK / "data"))
    compressed_employer.run(str(DTA), True, str(OUT_MECH))
    out = org_channels.run(str(DTA), True, None, str(DECK / "mechanisms" / "employer_channels.csv"))
    out.to_csv(OUT_MECH / "employer_channels.csv", index=False, float_format="%.9g")
    for f in ("dce_org_wtp", "dce_modelfree", "dce_rank_vs_log", "dce_org_het"):
        normalize(OUT_DATA / f"{f}.csv")
    normalize(OUT_MECH / "employer_channels.csv")
    print("wrote", sorted(p.name for p in OUT_DATA.glob("*.csv")), sorted(p.name for p in OUT_MECH.glob("*.csv")))


if __name__ == "__main__":
    main()
