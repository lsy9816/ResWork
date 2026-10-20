"""fwa_employer_splits -- employers' required pay cut for ALL seven arrangements, by on-site presence need and by the four concerns
(productivity, coordination, creativity, fairness).  Uses the same fully interacted conditional logit as scripts/port/org_het.py
(group-specific pay slope; employers, 397 firms, snef_employer_appended.dta, read only) and adds the fairness concern.

Pay cut required = minus the model's WTP (positive = cut).  Difference = group 1 minus group 0 (1 = most roles need presence /
agrees with the concern), SE from independent groups; p from a test that the pay-equivalent value is equal across groups.
Joint tests: location (3 restrictions), non-location (staggered, compressed, job sharing, part-time: 4), all seven.

Writes results_fwa/employer_splits.csv.   usage: python3 fwa_employer_splits.py DIR_WITH_appended.dta
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
ITEMS = [("p1", "1–2 days WFH"), ("p2", "3–4 days WFH"), ("p3", "Fully remote"), ("s2", "Compressed week"),
         ("s1", "Staggered hours"), ("j1", "Job sharing"), ("j2", "Part-time")]

raw = ed.load(Path(sys.argv[1]) / "appended.dta", True)
d = ed.dce_frame(raw)
d = ed.dummies(d)
d["tagid"] = (~d["id"].duplicated()).astype(int)
d["log_salary"] = d["log_salary"].astype(float)
nan = np.nan
d["physical"] = d["physical_presence"].where(d["physical_presence"] != 3, 2)
for nm, v in (("prod", "productivity_concern"), ("coord", "coordination_concern"), ("creat", "creativity_concern"),
              ("fair", "fairness_concern")):
    d[nm] = np.where(d[v].isna(), nan, (d[v] > 3).astype(float))
d["pres"] = np.where(d["physical"].isin([1, 2]), (d["physical"] == 1).astype(float), nan)

SPLITS = [("pres", "On-site presence needed", "Most roles need presence", "Some or few roles"),
          ("prod", "Productivity concern", "Concerned", "Not concerned"),
          ("coord", "Coordination concern", "Concerned", "Not concerned"),
          ("creat", "Creativity concern", "Concerned", "Not concerned"),
          ("fair", "Fairness concern", "Concerned", "Not concerned")]


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
for var, title, la, lb in SPLITS:
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
        rows.append(dict(split=var, split_label=title, item=a, arrangement=lab, group1=la, group0=lb, n1=n[1], n0=n[0],
                         cut1=r[1][0], se1=r[1][1], lb1=r[1][0] - 1.96 * r[1][1], ub1=r[1][0] + 1.96 * r[1][1],
                         cut0=r[0][0], se0=r[0][1], lb0=r[0][0] - 1.96 * r[0][1], ub0=r[0][0] + 1.96 * r[0][1],
                         diff=dff, diff_se=dse, diff_lb=dff - 1.96 * dse, diff_ub=dff + 1.96 * dse, p_item=p))
    def rf(a):
        return lambda B: B["%s_1" % a] / B["ls_1"] - B["%s_0" % a] / B["ls_0"]
    joint = {}
    for nm, items in (("location", ["p1", "p2", "p3"]), ("nonlocation", ["s2", "s1", "j1", "j2"]),
                      ("all7", ["p1", "p2", "p3", "s2", "s1", "j1", "j2"])):
        chi, df_, p = oh.testnl(f, [rf(a) for a in items])
        joint[nm] = p
    for r_ in rows:
        if r_["split"] == var:
            r_["p_location"], r_["p_nonlocation"], r_["p_all7"] = joint["location"], joint["nonlocation"], joint["all7"]

out = pd.DataFrame(rows)
(MOM / "results_fwa").mkdir(exist_ok=True)
out.round(4).to_csv(MOM / "results_fwa" / "employer_splits.csv", index=False)
show = out.pivot_table(index="arrangement", columns="split", values="diff", sort=False).round(1)
print(show.to_string())
print(out.groupby("split")[["p_location", "p_nonlocation", "p_all7", "n1", "n0"]].first().round(3).to_string())
print(out[out.split == "pres"][["arrangement", "cut1", "cut0", "diff", "diff_lb", "diff_ub", "p_item"]].round(1).to_string())
