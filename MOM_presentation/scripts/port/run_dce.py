"""Run the employer DCE port on a dta and write the five CSVs (employee rows copied from the professor's files)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import dce_org as D
from employer_data import load, dce_frame, dummies


def fmt(df, dec):
    """Round to the Stata display formats the professor's CSVs were exported with (datafmt)."""
    df = df.copy()
    for c, n in dec.items():
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").round(n)
    return df


def run(dta, appended, outdir, prof_dir):
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    prof = Path(prof_dir)
    d = dummies(dce_frame(load(dta, appended)))
    w = D.run_dce_wtp(d, prof / "dce_emp_wtp.csv")
    fmt(w, {"est": 4, "se": 4, "lb": 4, "ub": 4, "p": 6}).to_csv(outdir / "dce_org_wtp.csv", index=False)
    mf = D.run_modelfree(d)
    pm = pd.read_csv(prof / "dce_modelfree.csv")
    pd.concat([pm[pm.side == "employee"], fmt(mf[pm.columns], {"share": 4, "lb": 4, "ub": 4, "value": 4})], ignore_index=True).to_csv(outdir / "dce_modelfree.csv", index=False)
    rk = D.run_rank(d)
    pr = pd.read_csv(prof / "dce_rank_vs_log.csv")
    pd.concat([pr[pr.side == "employee"], fmt(rk[pr.columns], {"ll": 3, "aic": 3, "bic": 3, "lr": 3, "b_logsal": 4, "se_logsal": 4, "b_rank": 4, "se_rank": 4, "b_left": 4, "se_left": 4, "lr_p": 6})], ignore_index=True).to_csv(outdir / "dce_rank_vs_log.csv", index=False)
    ds, _ = D.run_design(d)
    pg = pd.read_csv(prof / "dce_design.csv")
    pd.concat([pg[pg.side == "employee"], fmt(ds[pg.columns], {"value": 4})], ignore_index=True).to_csv(outdir / "dce_design.csv", index=False)
    eq = D.run_eqpay(d)
    pe = pd.read_csv(prof / "dce_eqpay.csv")
    pd.concat([pe[pe.side == "employee"], eq[pe.columns]], ignore_index=True).to_csv(outdir / "dce_eqpay.csv", index=False)
    return w, mf, rk, ds, eq


if __name__ == "__main__":
    SP = "/tmp/claude-0/-home-user-ResWork/ddc3d860-5d1b-54ab-bc5b-0b5766ecc715/scratchpad/dl"
    w, mf, rk, ds, eq = run(f"{SP}/appended.dta", True, "/home/user/ResWork/MOM_presentation/data", f"{SP}/ds/data")
    print(w[(w['sample']=='main')&(w.block=='eqpay')][['item','est','se']].round(2).to_string())
    print(ds[['block','item','value']].round(3).to_string())
