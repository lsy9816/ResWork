"""fwa_diagnosis -- why are the FWAs other than remote work used so little?  (analysis for the main-slide rethink)

Reads the survey data READ-ONLY (Dropbox copies of employee.dta and snef_employer_appended.dta, passed on the command
line) and data/wtp_deck.csv (WTP, both sides, % of pay given up; built by build_wtp_data.py).
Writes only into MOM_presentation/results_fwa/:
  fwa_diagnosis.csv        one row per arrangement: offered / available / used / take-up / WTP / required cut / gap
  fwa_takeup.csv           PME availability, use and take-up with Wilson 95% intervals
  fwa_employer_challenge.csv  employers' biggest challenge (QID50), Wilson intervals
  F_fwa_diag.png, F_fwa_takeup.png, F_fwa_challenge.png

Definitions (as in code_final.do / appended.do):
  PME sample: respondents who answered QID38 (currently employed, n = 1,004).
    available (adjusted) = ticked in QID38 or currently used;   used: remote QID31 in 2-4, staggered QID32 = 2,
    compressed QID32 = 3, job sharing QID33 = 2, part-time QID33 = 3.   take-up = used / available (adjusted).
  Employers (n = 397): offered (adjusted) = ticked in QID15 or the typical practice for its PMEs (QID16 remote days > 0,
    QID61 = 2 staggered / 3 compressed, QID17 = 2 job sharing / 3 part-time), as org_fwa.csv.

usage: python3 fwa_diagnosis.py DIR_WITH_employee.dta_and_appended.dta
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MOM = Path(__file__).resolve().parents[1]
IN = Path(sys.argv[1])
OUT = MOM / "results_fwa"
OUT.mkdir(exist_ok=True)

BLUE, RED, INK, MUTED, LBLUE, LRED = "#003366", "#990000", "#1A1A1A", "#555555", "#9DB5D3", "#D9A3A3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * p, 100 * (c - h), 100 * (c + h)


# ------------------------------------------------------------------ PMEs
e = pd.read_stata(IN / "employee.dta", convert_categoricals=False).drop_duplicates("ResponseId")
e = e[e.fwa_avail.fillna("") != ""]
NE = len(e)
use = {"remote": e.remote.isin([2, 3, 4]), "staggered": e.schedule == 2, "compressed": e.schedule == 3,
       "jobshare": e.workload == 2, "parttime": e.workload == 3}
ticked = {"remote": e[["fwa_adhoc", "fwa_schedremote", "fwa_fullremote"]].max(axis=1) == 1,
          "staggered": e.fwa_staggered == 1, "compressed": e.fwa_compressed == 1,
          "jobshare": e.fwa_jobshare == 1, "parttime": e.fwa_parttime == 1}
KEYS = ["remote", "staggered", "compressed", "jobshare", "parttime"]
LAB = {"remote": "Work from home", "staggered": "Staggered hours", "compressed": "Compressed week",
       "jobshare": "Job sharing", "parttime": "Part-time"}
rows = []
for k in KEYS:
    av = ticked[k] | use[k]
    a = wilson(int(av.sum()), NE)
    u = wilson(int(use[k].sum()), NE)
    t = wilson(int(use[k][av].sum()), int(av.sum()))
    rows.append(dict(arrangement=k, n_pme=NE, avail=a[0], avail_lb=a[1], avail_ub=a[2], used=u[0], used_lb=u[1],
                     used_ub=u[2], n_avail=int(av.sum()), takeup=t[0], takeup_lb=t[1], takeup_ub=t[2]))
tk = pd.DataFrame(rows)
tk.round(2).to_csv(OUT / "fwa_takeup.csv", index=False)

# ------------------------------------------------------------------ employers
a = pd.read_stata(IN / "appended.dta", convert_categoricals=False).drop_duplicates("ResponseId")
NO = len(a)
av = a.fwa_avail.fillna("").str.replace(" ", "")
has = lambda c: av.apply(lambda s: c in s.split(","))
off_t = {"remote": has("1") | has("2") | has("3"), "staggered": has("4"), "compressed": has("5"),
         "jobshare": has("7"), "parttime": has("6")}
off_a = {"remote": off_t["remote"] | (a.remote >= 2), "staggered": off_t["staggered"] | (a.schedule == 2),
         "compressed": off_t["compressed"] | (a.schedule == 3), "jobshare": off_t["jobshare"] | (a.workload == 2),
         "parttime": off_t["parttime"] | (a.workload == 3)}
chk = pd.read_csv(MOM / "data" / "org_fwa.csv")
chk = chk[chk.block == "offered_adjusted"].set_index("item")["k"].to_dict()
for k, item in [("remote", "Remote work"), ("staggered", "Staggered hours"), ("compressed", "Compressed workweek"),
                ("jobshare", "Job sharing"), ("parttime", "Part-time / reduced hours")]:
    assert int(off_a[k].sum()) == int(chk[item]), (k, int(off_a[k].sum()), chk[item])   # reproduces org_fwa.csv
off = {k: wilson(int(off_a[k].sum()), NO) for k in KEYS}

CH = {1: "Productivity and output quality", 2: "Team coordination and communication",
      3: "Fairness across roles (not every role can be flexible)", 5: "Managerial resistance or lack of trust",
      4: "Lack of digital infrastructure", 6: "Security, confidentiality or compliance", 7: "Other"}
ch = []
for code, lab in CH.items():
    s = wilson(int((a.fwa_challenge == code).sum()), NO)
    ch.append(dict(challenge=lab, k=int((a.fwa_challenge == code).sum()), n=NO, share=s[0], lb=s[1], ub=s[2]))
ch = pd.DataFrame(ch).sort_values("share", ascending=False)
ch.round(2).to_csv(OUT / "fwa_employer_challenge.csv", index=False)

# ------------------------------------------------------------------ WTP, both sides (% of pay)
w = pd.read_csv(MOM / "data" / "wtp_deck.csv")
w = w[(w["sample"] == "main") & (w.split == "all")]


def g(side, item):
    r = w[(w.side == side) & (w["item"] == item)].iloc[0]
    return r.giveup, r.lb, r.ub, r.se


ITEM = {"remote": ["p1", "p2", "p3"], "staggered": ["t1"], "compressed": ["t2"], "jobshare": ["l1"], "parttime": ["l2"]}
SUB = {"p1": "1–2 days WFH", "p2": "3–4 days WFH", "p3": "Fully remote", "t1": "", "t2": "", "l1": "", "l2": ""}
out = []
for k in KEYS:
    for it in ITEM[k]:
        pm, pl, pu, ps = g("pme", it)
        em, el, eu, es = g("emp", it)
        gap = em - pm
        gs = np.hypot(ps, es)
        out.append(dict(arrangement=LAB[k], level=SUB[it] or LAB[k], item=it,
                        firms_offering=off[k][0], firms_lb=off[k][1], firms_ub=off[k][2],
                        pme_available=float(tk[tk.arrangement == k].avail.iloc[0]),
                        pme_used=float(tk[tk.arrangement == k].used.iloc[0]),
                        pme_takeup=float(tk[tk.arrangement == k].takeup.iloc[0]),
                        pme_giveup=pm, pme_lb=pl, pme_ub=pu, emp_require=em, emp_lb=el, emp_ub=eu,
                        gap=gap, gap_lb=gap - 1.96 * gs, gap_ub=gap + 1.96 * gs))
dg = pd.DataFrame(out)
dg.round(1).to_csv(OUT / "fwa_diagnosis.csv", index=False)
print(dg.round(1).to_string())
print(tk.round(1).to_string())
print(ch.round(1).to_string())


# ------------------------------------------------------------------ figures
def lab_bar(ax, x, y, v, **kw):
    ax.text(x + 1.2, y, f"{v:.0f}%", va="center", ha="left", fontsize=9, color=INK, **kw)


# Figure 1: who offers/uses, and the two sides' pay terms
fig = plt.figure(figsize=(11.2, 5.4))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.25], wspace=0.06)
axL, axR = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
heights = {k: len(ITEM[k]) for k in KEYS}
ytop, ypos = 0.0, {}
for k in KEYS:
    ypos[k] = ytop - heights[k] / 2
    ytop -= heights[k] + 0.35
for k in KEYS:
    y = ypos[k]
    s = tk[tk.arrangement == k].iloc[0]
    axL.barh(y + 0.22, off[k][0], height=0.36, color=LRED)
    axL.barh(y - 0.22, s.used, height=0.36, color=BLUE)
    lab_bar(axL, off[k][0], y + 0.22, off[k][0])
    lab_bar(axL, s.used, y - 0.22, s.used)
axL.set_yticks([ypos[k] for k in KEYS])
axL.set_yticklabels([LAB[k] for k in KEYS], fontsize=11)
axL.set_xlim(0, 105)
axL.set_xlabel("% of firms offering (red) / % of PMEs using (blue)", fontsize=9, color=MUTED)
axL.tick_params(length=0)
axL.spines["left"].set_visible(False)
yl = 0
for k in KEYS:
    for j, it in enumerate(ITEM[k]):
        y = ypos[k] + (len(ITEM[k]) - 1) / 2 - j
        pm, pl, pu, _ = g("pme", it)
        em, el, eu, _ = g("emp", it)
        axR.plot([pl, pu], [y + 0.13] * 2, color=BLUE, lw=1.6)
        axR.plot(pm, y + 0.13, "o", color=BLUE, ms=6)
        axR.plot([el, eu], [y - 0.13] * 2, color=RED, lw=1.6)
        axR.plot(em, y - 0.13, "D", color=RED, ms=6)
        axR.text(pu + 0.8, y + 0.13, f"{pm:.0f}", va="center", fontsize=8.5, color=BLUE)
        axR.text(eu + 0.8, y - 0.13, f"{em:.0f}", va="center", fontsize=8.5, color=RED)
        if SUB[it]:
            axR.text(-1.2, y, SUB[it], va="center", ha="right", fontsize=8.5, color=MUTED)
axR.axvline(0, color=MUTED, lw=0.8, ls="--")
axR.set_yticks([])
axR.set_ylim(ytop + 0.1, 0.45)
axL.set_ylim(ytop + 0.1, 0.45)
axR.set_xlim(-14, 62)
axR.set_xlabel("% of pay: PMEs would give up (blue) / employers would require (red)", fontsize=9, color=MUTED)
axR.tick_params(length=0)
axR.spines["left"].set_visible(False)
fig.savefig(OUT / "F_fwa_diag.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Figure 2: availability, use and take-up among PMEs
fig, ax = plt.subplots(figsize=(8.4, 4.4))
for i, k in enumerate(KEYS):
    y = -i
    s = tk[tk.arrangement == k].iloc[0]
    ax.barh(y + 0.2, s.avail, height=0.34, color=LBLUE)
    ax.barh(y - 0.2, s.used, height=0.34, color=BLUE)
    ax.text(s.avail + 1, y + 0.2, f"{s.avail:.0f}%", va="center", fontsize=9)
    ax.text(s.used + 1, y - 0.2, f"{s.used:.0f}%", va="center", fontsize=9)
    ax.text(104, y, f"{s.takeup:.0f}%", va="center", ha="left", fontsize=12, fontweight="bold", color=BLUE)
ax.text(104, 0.85, "Use, among\nthose with access", va="bottom", ha="left", fontsize=8.5, color=MUTED)
ax.set_yticks([-i for i in range(5)])
ax.set_yticklabels([LAB[k] for k in KEYS], fontsize=11)
ax.set_xlim(0, 100)
ax.set_xlabel("% of employed PMEs: with access (light) / using (dark)", fontsize=9, color=MUTED)
ax.set_ylim(-4.6, 1.4)
ax.tick_params(length=0)
ax.spines["left"].set_visible(False)
fig.savefig(OUT / "F_fwa_takeup.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Figure 3: employers' biggest challenge
fig, ax = plt.subplots(figsize=(8.4, 3.9))
c2 = ch.iloc[::-1]
for i, r in enumerate(c2.itertuples()):
    ax.barh(i, r.share, height=0.6, color=RED)
    ax.plot([r.lb, r.ub], [i, i], color=INK, lw=1.0)
    ax.text(r.ub + 0.8, i, f"{r.share:.0f}%", va="center", fontsize=9.5)
ax.set_yticks(range(len(c2)))
ax.set_yticklabels(c2.challenge, fontsize=9.5)
ax.set_xlim(0, 35)
ax.set_xlabel(f"% of employers naming it the biggest challenge in offering FWAs (n = {NO})", fontsize=9, color=MUTED)
ax.tick_params(length=0)
fig.savefig(OUT / "F_fwa_challenge.png", dpi=200, bbox_inches="tight")
plt.close(fig)
