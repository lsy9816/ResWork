"""pme_dominance -- dominance check of the PME choice experiment (port of the 'Dominance test' block of code_final.do).
Keeps choice sets where one option is better on BOTH non-salary attributes shown (orderings: location remote > 3-4 > 1-2 > onsite; schedule
compressed > staggered > fixed; workload part-time > job sharing > full time; risk low > moderate > high; culture collaborative > autonomous >
mixed > hierarchical; commute short > moderate > long). Observed share choosing the dominant job by salary gap vs the logit prediction.
Writes data/pme_dominance.csv (bin points + curve) and data/pme_dominance_task.csv.   usage: python3 pme_dominance.py employee.dta
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

MOM = Path(__file__).resolve().parents[1]
d = pd.read_stata(sys.argv[1], convert_categoricals=False)
cols = ["id", "choice_set", "task", "option", "chosen", "log_salary", "place", "timeflex", "load", "risk", "jobculture", "commutetime"]
d["option"] = d["option"].astype(int)
w = d[[c for c in cols if c not in ("id", "task")]].pivot(index="choice_set", columns="option")
w.columns = [f"{a}{b}" for a, b in w.columns]
w["task"] = d.drop_duplicates("choice_set").set_index("choice_set")["task"]
w["id"] = d.drop_duplicates("choice_set").set_index("choice_set")["id"]
assert ((w.chosen1 + w.chosen2) == 1).all()


def sc(x, lo, hi):
    return x.where(x.between(lo, hi))


S = {}
for j in (1, 2):
    S[("place", j)] = sc(w[f"place{j}"], 0, 3)
    S[("time", j)] = sc(w[f"timeflex{j}"], 0, 2)
    S[("load", j)] = sc(w[f"load{j}"], 0, 2)
    S[("risk", j)] = 2 - sc(w[f"risk{j}"], 0, 2)
    S[("culture", j)] = w[f"jobculture{j}"].map({1: 0, 2: 3, 3: 2, 4: 1})
    S[("commute", j)] = (2 - sc(w[f"commutetime{j}"], 0, 2)).where(w[f"place{j}"] != 3)
sg = {k: np.sign(S[(k, 1)] - S[(k, 2)]) for k in ("place", "time", "load", "risk", "culture", "commute")}
PAIR = {1: ("place", "time"), 2: ("place", "load"), 3: ("time", "load"), 4: ("load", "culture"), 5: ("risk", "time"), 6: ("place", "commute")}
c1 = pd.Series(np.nan, index=w.index)
c2 = c1.copy()
for t, (a, b) in PAIR.items():
    m = w.task == t
    c1[m], c2[m] = sg[a][m], sg[b][m]
w["dom"] = np.where((c1 == 1) & (c2 == 1), 1, np.where((c1 == -1) & (c2 == -1), 2, np.nan))
print("dominant pairs", int(w.dom.notna().sum()), "of", len(w))

x = pd.DataFrame(index=w.index)
x["d_log_salary"] = w.log_salary1 - w.log_salary2
for nm, v, lv in (("d_place12", "place", 1), ("d_place34", "place", 2), ("d_remote", "place", 3), ("d_stagger", "timeflex", 1),
                  ("d_compress", "timeflex", 2), ("d_jobshare", "load", 1), ("d_parttime", "load", 2), ("d_lowrisk", "risk", 0),
                  ("d_modrisk", "risk", 1), ("d_collab", "jobculture", 2), ("d_autonomy", "jobculture", 3), ("d_mixed", "jobculture", 4)):
    x[nm] = (w[f"{v}1"] == lv).astype(float) - (w[f"{v}2"] == lv).astype(float)
for nm, lv in (("d_commute_short", 0), ("d_commute_mod", 1)):
    x[nm] = ((w.place1 != 3) & (w.commutetime1 == lv)).astype(float) - ((w.place2 != 3) & (w.commutetime2 == lv)).astype(float)
ok = x.notna().all(axis=1)
fit = sm.Logit(w.chosen1[ok], x[ok]).fit(disp=0, cov_type="cluster", cov_kwds={"groups": w.id[ok]})
b = fit.params["d_log_salary"]
xb_non = (x[ok] @ fit.params) - b * x[ok].d_log_salary
w = w[ok].assign(xb_non=xb_non)
dm = w[w.dom.notna()].copy()
dom1 = dm.dom == 1
dm["chosen_dom"] = np.where(dom1, dm.chosen1, dm.chosen2)
dm["dsal"] = np.where(dom1, dm.log_salary1 - dm.log_salary2, dm.log_salary2 - dm.log_salary1)
dm["xb_dom"] = np.where(dom1, dm.xb_non, -dm.xb_non)
dm["bin"] = (np.round(dm.dsal / 0.05) * 0.05).round(2)
pts = dm.groupby("bin").agg(frac=("chosen_dom", "mean"), n=("chosen_dom", "size"), ncl=("id", "nunique")).reset_index()
p = pts.frac.values
pts["se"] = np.sqrt(p * (1 - p) / pts.n)
grid = np.round(np.arange(-0.42, 0.33, 0.01), 2)
curve = pd.DataFrame({"bin": grid, "pred": [float((1 / (1 + np.exp(-(dm.xb_dom + b * g)))).mean()) for g in grid]})
out = pts.merge(curve, on="bin", how="outer").sort_values("bin")
out.round(4).to_csv(MOM / "data" / "pme_dominance.csv", index=False)
bt = dm.groupby("task").chosen_dom.agg(["size", "mean"]).reset_index()
bt.round(4).to_csv(MOM / "data" / "pme_dominance_task.csv", index=False)
print(pts.round(3).to_string())
print(bt.round(3).to_string())
print("dominant respondents", dm.id.nunique(), "overall share", round(dm.chosen_dom.mean(), 3))
