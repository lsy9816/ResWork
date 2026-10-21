"""fwa_employer_other -- employers' required pay cut for the three WFH arrangements, by five further firm characteristics
(plans for FWAs, hiring difficulty, belief that FWAs help attract talent, voluntary turnover, technology readiness).
Same fully interacted conditional logit as fwa_employer_splits.py (397 firms, read only); pay cut = minus WTP; no joint tests.

Groups (1 = first listed): plan to expand FWAs (codes 1-2) vs maintain or reduce (3-5; 6 = not sure, dropped);
difficulty filling PME vacancies (1-2) vs none (3; 4 = not sure dropped); agrees FWAs help attract and retain talent (4-5) vs 1-3;
voluntary turnover 10% or more (2-3) vs under 10% (1; 4 = not sure dropped); technology fully ready (3) vs not fully ready (1-2).
Writes results_fwa/employer_other.csv.   usage: python3 fwa_employer_other.py DIR_WITH_appended.dta
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

MOM = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOM / "scripts" / "port"))
import org_het as oh  # noqa: E402

sc, ed = oh.sc, oh.ed
ATT, ATT_SRC = oh.ATT, oh.ATT_SRC
ITEMS = [("p1", "1–2 days WFH"), ("p2", "3–4 days WFH"), ("p3", "Fully remote")]

raw = ed.load(Path(sys.argv[1]) / "appended.dta", True)
d = ed.dce_frame(raw)
d = ed.dummies(d)
d["tagid"] = (~d["id"].duplicated()).astype(int)
d["log_salary"] = d["log_salary"].astype(float)
nan = np.nan


def grp(v, one, zero):
    return np.where(d[v].isin(one), 1.0, np.where(d[v].isin(zero), 0.0, nan))


d["plan"] = grp("fwa_plan", [1, 2], [3, 4, 5])
d["hire"] = grp("hiring_difficulty", [1, 2], [3])
d["talent"] = grp("talent_benefit", [4, 5], [1, 2, 3])
d["turn"] = grp("turnover", [2, 3], [1])
d["tech"] = grp("tech_readiness", [3], [1, 2])

SPLITS = [("plan", "Plans to expand FWAs"), ("hire", "Difficulty filling vacancies"),
          ("talent", "FWAs help attract talent"), ("turn", "Turnover 10% or more"), ("tech", "Technology fully ready")]


def interacted(s, levels, gvar):
    rhs = []
    for l in levels:
        m = (s[gvar] == l).astype(float)
        s["ls_%d" % l] = s["log_salary"] * m
        rhs.append("ls_%d" % l)
        for a in ATT:
            v, lv = ATT_SRC[a]
            s["%s_%d" % (a, l)] = (s[v] == lv).astype(float) * m
            rhs.append("%s_%d" % (a, l))
        s["in_%d" % l] = (s["collaborative"] == 0).astype(float) * m
        rhs.append("in_%d" % l)
    return rhs


rows = []
for var, title in SPLITS:
    s = d[d[var].isin([0.0, 1.0])].copy()
    levels = [0, 1]
    s[var] = s[var].astype(int)
    rhs = interacted(s, levels, var)
    s = s.dropna(subset=rhs)
    f = oh.fit_clogit(s, rhs)
    n = {l: int(((s[var] == l) & (s["tagid"] == 1)).sum()) for l in levels}
    res = {}
    for a, lab in ITEMS:
        r = {}
        for l in levels:
            est, se, _ = sc.nlcom(f, lambda B, a=a, l=l: 100 * (1 - np.exp(-B["%s_%d" % (a, l)] / B["ls_%d" % l])))
            # = 100*(1-exp(-b/b_pay)) = minus the port's wtp_a (employers: pay cut required)
            cut = est[0]
            r[l] = (cut, se[0])
        dff = r[1][0] - r[0][0]
        dse = float(np.hypot(r[1][1], r[0][1]))
        rt = lambda B, a=a: B["%s_1" % a] / B["ls_1"] - B["%s_0" % a] / B["ls_0"]
        chi, df_, p = oh.testnl(f, [rt])
        res[a] = dict(r=r, diff=dff, dse=dse, p=p)
        rows.append(dict(split=var, split_label=title, item=a, arrangement=lab, n1=n[1], n0=n[0],
                         cut1=r[1][0], se1=r[1][1], lb1=r[1][0] - 1.96 * r[1][1], ub1=r[1][0] + 1.96 * r[1][1],
                         cut0=r[0][0], se0=r[0][1], lb0=r[0][0] - 1.96 * r[0][1], ub0=r[0][0] + 1.96 * r[0][1],
                         diff=dff, diff_se=dse, diff_lb=dff - 1.96 * dse, diff_ub=dff + 1.96 * dse, p_item=p))

out = pd.DataFrame(rows)
(MOM / "results_fwa").mkdir(exist_ok=True)
out.round(4).to_csv(MOM / "results_fwa" / "employer_other.csv", index=False)
print(out[["split","arrangement","n1","n0","cut1","cut0","diff","diff_lb","diff_ub","p_item"]].round(1).to_string())
