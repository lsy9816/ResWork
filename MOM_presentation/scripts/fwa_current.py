"""fwa_current -- do PMEs who already use an arrangement value it more than those who do not?

Re-estimates, from employee.dta (read only), the do-file model "Current arrangement (interaction with own current FWA)"
of code_final.do: conditional logit on the six choice tasks, pay and each FWA level plus its interaction with the
respondent's OWN current arrangement (remote QID31, schedule QID32, workload QID33), clustered by respondent.
Pay given up = 100 * (1 - exp(-(b_x + g * b_current_x) / b_pay)),  g = 0 non-users, g = 1 users  (delta method).
Sample: employed respondents with all three current-arrangement answers.

Writes results_fwa/fwa_current.csv and results_fwa/F_fwa_current.png.
usage: python3 fwa_current.py DIR_WITH_employee.dta
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MOM = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOM / "scripts" / "port"))
import stata_core as sc

OUT = MOM / "results_fwa"
e = pd.read_stata(Path(sys.argv[1]) / "employee.dta", convert_categoricals=False)
e = e[e.empstat.isin([1, 2])].copy()

TERMS = ["place12", "place34", "remote", "stagger", "compress", "jobshare", "parttime"]
CUR = {"place12": e.remote == 2, "place34": e.remote == 3, "remote": e.remote == 4, "stagger": e.schedule == 2,
       "compress": e.schedule == 3, "jobshare": e.workload == 2, "parttime": e.workload == 3}
for t in TERMS:
    e["ac_" + t] = np.where(e[["remote", "schedule", "workload"]].notna().all(axis=1),
                            CUR[t].astype(float) * e["mx_" + t], np.nan)
BASE = ["log_salary"] + ["mx_" + t for t in TERMS] + ["mx_lowrisk", "mx_modrisk", "mx_collab", "mx_autonomy", "mx_mixed",
                                                      "commute_short", "commute_mod"]
d = e[e[["remote", "schedule", "workload"]].notna().all(axis=1)].copy()
assert d["choice_set"].value_counts().eq(2).all()

# check: the main model (no interactions) reproduces the deck's PME values (1-2 days 7.4, 3-4 days 9.5, fully remote 15.1)
f0 = sc.clogit(d, "chosen", BASE, "choice_set", "id")
for t, want in [("remote", 15.1), ("place12", 7.4), ("place34", 9.5), ("compress", 7.4)]:
    est, se, _ = sc.nlcom(f0, lambda b: 100 * (1 - np.exp(-b["mx_" + t] / b["log_salary"])))
    print(f"check main model {t}: {est[0]:.2f}   (deck {want})")

X = BASE + ["ac_" + t for t in TERMS]
f = sc.clogit(d, "chosen", X, "choice_set", "id")
print("N respondents", f.G, " tasks-sets", f.nsets)
LAB = {"place12": "1–2 days WFH", "place34": "3–4 days WFH", "remote": "Fully remote",
       "stagger": "Staggered hours", "compress": "Compressed week", "jobshare": "Job sharing", "parttime": "Part-time"}
first_rows = d.drop_duplicates("id")
rows = []
for t in TERMS:
    n_use = int(CUR[t].loc[first_rows.index].sum())
    r = dict(arrangement=LAB[t], term=t, n_users=n_use, n_nonusers=int(f.G) - n_use)
    for gname, g in (("nonusers", 0), ("users", 1)):
        est, se, _ = sc.nlcom(f, lambda b: 100 * (1 - np.exp(-(b["mx_" + t] + g * b["ac_" + t]) / b["log_salary"])))
        r[f"giveup_{gname}"], r[f"se_{gname}"] = est[0], se[0]
        r[f"lb_{gname}"], r[f"ub_{gname}"] = est[0] - 1.96 * se[0], est[0] + 1.96 * se[0]
    # users minus non-users in pay-given-up terms, and a Wald test that the log-odds interaction is zero
    est, se, _ = sc.nlcom(f, lambda b: 100 * (1 - np.exp(-(b["mx_" + t] + b["ac_" + t]) / b["log_salary"]))
                          - 100 * (1 - np.exp(-b["mx_" + t] / b["log_salary"])))
    r["diff"], r["diff_se"] = est[0], se[0]
    r["diff_lb"], r["diff_ub"] = est[0] - 1.96 * se[0], est[0] + 1.96 * se[0]
    # test that users and non-users have the same pay-equivalent value (WTP ratio test, group-specific pay slopes not allowed here:
    # pay slope is common, so this equals the interaction test)
    r["p_interaction"] = sc.wald(f, [{"ac_" + t: 1}])[2]
    rows.append(r)
cur = pd.DataFrame(rows)
for nm, grp in (("location", ["ac_place12", "ac_place34", "ac_remote"]), ("schedule", ["ac_stagger", "ac_compress"]),
                ("workload", ["ac_jobshare", "ac_parttime"]), ("all", ["ac_" + t for t in TERMS])):
    p = sc.wald(f, [{g: 1} for g in grp])[2]
    print(f"joint test {nm}: p = {p:.4f}")
    cur.loc[cur.index[0], "joint_" + nm] = p
cur.round(4).to_csv(OUT / "fwa_current.csv", index=False)
print(cur[["arrangement", "n_users", "giveup_nonusers", "giveup_users", "diff", "p_interaction"]].round(2).to_string())

# ------------------------------------------------------------------ figure
BLUE, MUTED, GREY, INK = "#003366", "#555555", "#8FA3BA", "#1A1A1A"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(8.8, 5.2))
order = ["place12", "place34", "remote", None, "stagger", "compress", None, "jobshare", "parttime"]
y, ys, labs = 0, [], []
for t in order:
    if t is None:
        y -= 0.5
        continue
    r = cur[cur.term == t].iloc[0]
    ax.plot([r.lb_nonusers, r.ub_nonusers], [y + 0.14] * 2, color=GREY, lw=1.8)
    ax.plot(r.giveup_nonusers, y + 0.14, "o", color=GREY, ms=6.5)
    ax.plot([r.lb_users, r.ub_users], [y - 0.14] * 2, color=BLUE, lw=1.8)
    ax.plot(r.giveup_users, y - 0.14, "D", color=BLUE, ms=6.5)
    ax.text(r.ub_nonusers + 0.7, y + 0.14, f"{r.giveup_nonusers:.0f}", va="center", fontsize=9, color=MUTED)
    ax.text(r.ub_users + 0.7, y - 0.14, f"{r.giveup_users:.0f}", va="center", fontsize=9, color=BLUE, fontweight="bold")
    ys.append(y)
    labs.append(f"{LAB[t]}\n(n = {int(r.n_users)} use it)")
    y -= 1
ax.axvline(0, color=MUTED, lw=0.8, ls="--")
ax.set_yticks(ys)
ax.set_yticklabels(labs, fontsize=9.5)
ax.set_ylim(y + 0.2, 0.7)
ax.set_xlabel("% of pay PMEs would give up for the arrangement", fontsize=9, color=MUTED)
ax.plot([], [], "o", color=GREY, label="PMEs not in this arrangement now")
ax.plot([], [], "D", color=BLUE, label="PMEs already in this arrangement")
ax.legend(loc="upper right", frameon=False, fontsize=9)
ax.tick_params(length=0)
ax.spines["left"].set_visible(False)
fig.savefig(OUT / "F_fwa_current.png", dpi=200, bbox_inches="tight")
plt.close(fig)
