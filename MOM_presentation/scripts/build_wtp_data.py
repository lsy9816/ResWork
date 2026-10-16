"""build_wtp_data -- one tidy table of every WTP the deck shows, both sides in ONE convention.

Convention (user decision, 16 Oct 2026): `giveup` = % of pay given up for the arrangement; positive = amount of pay cut.
  PMEs:      pay they would give up                       (= the model's WTP, positive when they value it)
  Employers: pay cut they would require of a candidate    (= minus the model's WTP, which is negative for a discount)
  Gap = employers' required cut minus PMEs' accepted cut   (positive = friction).
Confidence limits are swapped for employers (lb = -ub_wtp, ub = -lb_wtp). All main results use ALL respondents.

Inputs (read only):  data/dce_org_het.csv, data/dce_org_wtp.csv (this repo), the Dropbox files appended_wtp.xlsx,
employee_wtp.xlsx and the professor's dce_emp_wtp.csv, dce_emp_het.csv, pme_channels.csv (paths via argv).
Output: data/wtp_deck.csv

usage: python3 build_wtp_data.py DIR_WITH_INPUTS      (DIR holds appended_wtp.xlsx, employee_wtp.xlsx, dce_emp_wtp.csv,
                                                       dce_emp_het.csv, pme_channels.csv)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MOM = Path(__file__).resolve().parents[1]
IN = Path(sys.argv[1])
OUT = []

# term -> item key shared by both sides
TERM = {"1.place": "p1", "2.place": "p2", "3.place": "p3", "1.timeflex": "t1", "2.timeflex": "t2",
        "1.load": "l1", "2.load": "l2", "1.retention": "r1", "2.retention": "r2", "0.collaborative": "cult", "remote_vs_mod": "p3m",
        "0.risk": "risk0", "1.risk": "risk1"}


def add(side, sample, split, group, glabel, n, item, est, se, lb, ub):
    if side == "emp":      # employers: pay cut required = minus WTP
        est, lb, ub = -est, -ub, -lb
    OUT.append(dict(side=side, sample=sample, split=split, group=group, glabel=glabel, n=n, item=item,
                    giveup=round(est, 4), se=round(se, 4), lb=round(lb, 4), ub=round(ub, 4)))


# ---------------- PMEs ----------------
w = pd.read_csv(IN / "dce_emp_wtp.csv")
w = w[w.block == "wtp"]
keep = {"main": "main", "excl_salary_out": "excl_salary_out", "trim1pct": "trim1pct", "excl_same_side": "same_side",
        "left_asc": "left_asc", "block_cluster": "version_cluster"}
for smp, nm in keep.items():
    for _, r in w[w["sample"] == smp].iterrows():
        k = TERM.get(r["item"])
        if k and k in ("p1", "p2", "p3", "p3m", "t1", "t2", "l1", "l2"):
            add("pme", nm, "all", 0, "All PMEs", int(r["n_resp"]), k, r.est, r.se, r.lb, r.ub)
pc = pd.read_csv(IN / "pme_channels.csv")
pc = pc[(pc.block == "wtp") & (pc["sample"] == "all")]
for _, r in pc[(pc.split == "all") & (pc.item.isin(["p3own"]))].iterrows():
    add("pme", "main", "all", 0, "All PMEs", int(r.n_resp), r["item"], r.est, r.se, r.lb, r.ub)
for _, r in pc[pc.split == "career"].iterrows():
    if r["item"] in ("p1", "p2", "p3", "p3m", "t1", "t2", "l1", "l2"):
        add("pme", "main", "career", int(r.group), "Expects penalty" if r.group == 1 else "No expected penalty",
            int(r.n_resp), r["item"], r.est, r.se, r.lb, r.ub)

het = pd.read_csv(IN / "dce_emp_het.csv")
xl = pd.ExcelFile(IN / "employee_wtp.xlsx")
SPL = {"gender": ("female", ["Male", "Female"]), "age": ("age40", ["Age 19-39", "Age 40+"]),
       "care_any": ("care_any", ["No caregiving", "Any caregiving"]),
       "care_type": ("care3", ["No caregiving", "Caregiving, no child 0-6", "Child aged 0-6"])}
for sheet, (hs, labs) in SPL.items():
    t = xl.parse(sheet)
    pw = het[(het.block == "pairwise") & (het.split == hs)].iloc[0]
    ns = {0: int(pw.n_a), 1: int(pw.n_b)}
    if sheet == 'care_type':     # none 360 / other caregiving 1,020-360-258 / child 0-6 258 (care3 pairwise gives none vs child 0-6)
        ns = {0: 360, 1: 402, 2: 258}
    for _, r in t.iterrows():
        k = TERM.get(r["term"])
        if k in ("p1", "p2", "p3", "t1", "t2", "l1", "l2"):
            g = int(r["group"])
            add("pme", "main", sheet, g, labs[g] if g < len(labs) else str(g), ns.get(g, 0), k,
                r.wtp, r.se, r.lb, r.ub)
    # Fully remote vs onsite with a MODERATE commute (= b[3.place] - b[commute_mod]); the covariance is not in the xlsx, so the point
    # estimate is exact (ratio form) but the SE is PROVISIONAL: the 3.place SE scaled by the main-sample ratio se(remote_vs_mod)/se(3.place).
    # Replace with nlcom output (see CHANGES_wtp_update.md) when available.
    t3 = {(int(r["group"]), r["term"]): r for _, r in t.iterrows()}
    ratio = 1.6428 / 2.0519
    for g in sorted({k[0] for k in t3}):
        w3, wm = t3[(g, "3.place")], t3[(g, "commute_mod")]
        x = -np.log(1 - w3.wtp / 100) + np.log(1 - wm.wtp / 100)
        est = 100 * (1 - np.exp(-x))
        se = w3.se * ratio
        OUT.append(dict(side="pme", sample="main", split=sheet, group=g, glabel=labs[g] if g < len(labs) else str(g), n=ns.get(g, 0),
                        item="p3m", giveup=round(est, 4), se=round(se, 4), lb=round(est - 1.96 * se, 4), ub=round(est + 1.96 * se, 4),
                        provisional=1))
    jt = het[(het.block == "joint_test") & (het.split == hs) & (het["item"] == "wtp")].iloc[0]
    OUT.append(dict(side="pme", sample="main", split=sheet, group=-1, glabel="joint test: all WTP ratios equal",
                    n=0, item="joint_p", giveup=round(float(jt.p), 5), se=0, lb=0, ub=0))

# ---------------- employers ----------------
ap = pd.ExcelFile(IN / "appended_wtp.xlsx")
m = ap.parse("main")
for _, r in m.iterrows():
    k = TERM.get(r.term)
    if k:
        add("emp", "main", "all", 0, "All employers", 397, k, r.wtp, r.se, r.lb, r.ub)
NR = {"robust_outlier": ("excl_salary_out", 392), "robust_trim": ("trim1pct", 391), "robust_same_side": ("same_side", 381)}
for sh, (nm, n) in NR.items():
    t = ap.parse(sh)
    for _, r in t[t.group == 1].iterrows():
        k = TERM.get(r.term)
        if k in ("p1", "p2", "p3", "t1", "t2", "l1", "l2"):
            add("emp", nm, "all", 0, "All employers", n, k, r.wtp, r.se, r.lb, r.ub)
org = pd.read_csv(MOM / "data" / "dce_org_het.csv")
gw = org[org.block == "group_wtp"]
lt = org[org.block == "linear_test"]
rt = org[org.block == "ratio_test_place"]
ITM = {"p1": "p1", "p2": "p2", "p3": "p3", "s1": "t1", "s2": "t2", "j1": "l1", "j2": "l2", "t1": "r1", "t2": "r2"}
for split, g in gw.groupby("split"):
    if split in ("size", "role", "tech"):
        labs = list(dict.fromkeys(g.group_a))
        ns = {l: int(g[g.group_a == l].n_a.iloc[0]) for l in labs}
        pgroups = [(l, i) for i, l in enumerate(labs)]
    else:
        L = lt[(lt.split == split) & (lt["item"] == "place")].iloc[0]
        pgroups = [(L.group_a, 0), (L.group_b, 1)]
        ns = {L.group_a: int(L.n_a), L.group_b: int(L.n_b)}
    for lab, gi in pgroups:
        if split in ("size", "role", "tech"):
            sub = g[g.group_a == lab]
        else:
            sub = g[g.n_a == ns[lab]]
        for _, r in sub.iterrows():
            k = ITM.get(r["item"])
            if k:
                est, se = r.wtp_a, r.se
                add("emp", "main", split, gi, lab, ns[lab], k, est, se, est - 1.96 * se, est + 1.96 * se)
    if split in ("size", "role", "tech"):
        rr = rt[(rt.split == split) & rt.n_a.isna()]
    else:
        rr = rt[rt.split == split]
    OUT.append(dict(side="emp", sample="main", split=split, group=-1, glabel="ratio test: location WTPs equal",
                    n=0, item="ratio_p", giveup=round(float(rr.p.iloc[0]), 5) if len(rr) else np.nan, se=0, lb=0, ub=0))
    ll = lt[(lt.split == split) & (lt["item"] == "place")]
    if len(ll):
        OUT.append(dict(side="emp", sample="main", split=split, group=-1, glabel="location interactions = 0 (common slope)",
                        n=0, item="linear_p", giveup=round(float(ll.p.iloc[0]), 5), se=0, lb=0, ub=0))

df = pd.DataFrame(OUT)
df.to_csv(MOM / "data" / "wtp_deck.csv", index=False)
print(df.groupby(["side", "sample", "split"]).size().to_string())
