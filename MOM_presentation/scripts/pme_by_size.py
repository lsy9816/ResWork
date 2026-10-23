"""pme_by_size -- PME pay given up for the seven arrangements, by the size of the PME's own organisation (QID19, three groups)
and, as a check, the full sample (should reproduce the main model: 1-2 days 7.4, 3-4 days 9.5, remote 15.1).
Model as code_final.do: clogit chosen log_salary ib0.place ib0.timeflex ib0.load ib2.risk ib1.jobculture commute_short commute_mod,
group(choice_set) vce(cluster id). WTP = 100*(1-exp(-b_k/b_pay)), delta-method 95% CI. Groups: <=200 staff (codes 1-3), 201-1,000 (4-5), 1,001+ (6).
Writes data/pme_by_size.csv.   usage: python3 pme_by_size.py employee.dta
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MOM = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOM / "scripts" / "port"))
import org_het as oh  # noqa: E402

sc = oh.sc
d = pd.read_stata(sys.argv[1], convert_categoricals=False)
d["choice_set"] = d["choice_set"].astype(int)
d["id"] = d["id"].astype(int)
for nm, v, lv in (("p1", "place", 1), ("p2", "place", 2), ("p3", "place", 3), ("tf1", "timeflex", 1), ("tf2", "timeflex", 2),
                  ("tf3", "timeflex", 3), ("l1", "load", 1), ("l2", "load", 2), ("r0", "risk", 0), ("r1", "risk", 1),
                  ("c2", "jobculture", 2), ("c3", "jobculture", 3), ("c4", "jobculture", 4)):
    d[nm] = (d[v] == lv).astype(float)
X = ["log_salary", "p1", "p2", "p3", "tf1", "tf2", "tf3", "l1", "l2", "r0", "r1", "c2", "c3", "c4", "commute_short", "commute_mod"]
ITEMS = [("p1", "p1"), ("p2", "p2"), ("p3", "p3"), ("t2", "tf2"), ("t1", "tf1"), ("l1", "l1"), ("l2", "l2")]
d["size3"] = np.select([d.orgsize.isin([1, 2, 3]), d.orgsize.isin([4, 5]), d.orgsize == 6], [1, 2, 3], np.nan)
rows = []
for g, s in [(0, d)] + [(k, d[d.size3 == k]) for k in (1, 2, 3)]:
    f = oh.fit_clogit(s, X)
    n = s["id"].nunique()
    for item, term in ITEMS:
        est, se, _ = sc.nlcom(f, lambda B, term=term: 100 * (1 - np.exp(-B[term] / B["log_salary"])))
        rows.append(dict(group=g, n=n, item=item, giveup=est[0], se=se[0], lb=est[0] - 1.96 * se[0], ub=est[0] + 1.96 * se[0]))
out = pd.DataFrame(rows)
out.round(4).to_csv(MOM / "data" / "pme_by_size.csv", index=False)
print(out.pivot(index="item", columns="group", values="giveup").round(1).to_string())
print(out[out.item == "p1"][["group", "n"]].to_string())
