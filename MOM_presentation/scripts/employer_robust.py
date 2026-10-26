"""employer_robust -- the two employer robustness checks that appended.do ran in Stata (the 26 Oct 2026 code_final.do keeps only
the same-side check): (0) same-side respondents excluded (checked against the Stata sheet), (1) exclude salary outliers (salary_out == 0: monthly salary outside S$2,000-50,000) and (2) exclude the
top and bottom 1% of baseline salary (base_salary_orig, percentiles over respondents, Stata's `summarize, detail` rule).
Model as the main employer model: clogit chosen log_salary ib0.place ib0.timeflex ib0.load ib0.retention ib1.collaborative,
vce(cluster id).  Pay cut required = -wtp, wtp = 100*(exp(-b/b_pay)-1) (nlcom).  Writes data/employer_robust.csv.
usage: python3 employer_robust.py DIR_WITH_appended.dta
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MOM = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOM / "scripts" / "port"))
import org_het as oh  # noqa: E402

sc, ed = oh.sc, oh.ed
raw = ed.load(Path(sys.argv[1]) / "appended.dta", True)
d = ed.dummies(ed.dce_frame(raw))
full = pd.read_stata(Path(sys.argv[1]) / "appended.dta", convert_categoricals=False)[["id", "base_salary_orig"]].drop_duplicates("id")
full["base_salary_orig"] = pd.to_numeric(full["base_salary_orig"], errors="coerce")
d = d.merge(full, on="id", how="left")
TERMS = ["1.place", "2.place", "3.place", "1.timeflex", "2.timeflex", "1.load", "2.load", "1.retention", "2.retention"]
X = ["log_salary"] + TERMS + ["0.collaborative"]


def stata_pct(x, p):
    x = np.sort(np.asarray(x, float))
    n = len(x)
    k = n * p / 100
    return (x[int(k) - 1] + x[int(k)]) / 2 if abs(k - round(k)) < 1e-9 else x[math.ceil(k) - 1]


p1, p99 = stata_pct(full["base_salary_orig"].dropna(), 1), stata_pct(full["base_salary_orig"].dropna(), 99)
d["salary_trim"] = d["base_salary_orig"].between(p1, p99)
rows = []
for name, mask in (("excl_salary_out", d["salary_out"] == 0), ("trim1pct", d["salary_trim"]), ("same_side", d["ss"] == 0)):
    s = d[mask]
    f = oh.fit_clogit(s, X)
    n = s["id"].nunique()
    for t in TERMS:
        est, se, _ = sc.nlcom(f, lambda B, t=t: 100 * (math.exp(-B[t] / B["log_salary"]) - 1))
        rows.append(dict(sample=name, term=t, n_resp=n, wtp=est[0], se=se[0], lb=est[0] - 1.96 * se[0], ub=est[0] + 1.96 * se[0]))
out = pd.DataFrame(rows)
out.round(6).to_csv(MOM / "data" / "employer_robust.csv", index=False)
print(out.pivot(index="term", columns="sample", values="wtp").round(1).to_string(), out.groupby("sample").n_resp.first().to_dict(), p1, p99)
