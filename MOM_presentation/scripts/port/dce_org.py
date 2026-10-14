"""dce_org -- Python port of the employer DCE parts of deck_aggregates.do (sections 4, 5, 6, 7) and deck_eqpay.do.

Writes dce_org_wtp.csv, dce_modelfree.csv, dce_rank_vs_log.csv, dce_design.csv, dce_eqpay.csv. The employee rows of the
files that hold both sides are copied unchanged from the professor's CSVs (EMP_DIR), the employer rows are recomputed.
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, "/home/user/ResWork/MOM_presentation/scripts/port")
from stata_core import clogit, nlcom, wald, invlogit, normal_cdf, wilson
from employer_data import load, dce_frame, dummies, XR, TR

Z = stats.norm.ppf(0.975)
MINCELL = 5

LAB_R = {
    "log_salary": ("Log monthly salary (candidate expectation)", ""),
    "left": ("Shown on the left (position constant)", "Shown on the right"),
    "lo": ("Cheaper candidate (rank dummy)", "Dearer candidate"),
    "1.place": ("1-2 days WFH a week", "Fully onsite"),
    "2.place": ("3-4 days WFH a week", "Fully onsite"),
    "3.place": ("Fully remote", "Fully onsite"),
    "1.timeflex": ("Staggered hours", "Fixed hours (9am-6pm)"),
    "2.timeflex": ("Compressed 4-day week", "Fixed hours (9am-6pm)"),
    "1.load": ("Reduced load, 4 days/week (shown to employers; RA outputs label it job sharing)", "Full-time (35-44 h/week)"),
    "2.load": ("Part-time (<35 h/week)", "Full-time (35-44 h/week)"),
    "1.retention": ("Moderate turnover risk (10-20%)", "Low turnover risk (<10%)"),
    "2.retention": ("High turnover risk (>20%)", "Low turnover risk (<10%)"),
    "0.collaborative": ("Independent / autonomous culture", "Collaborative culture"),
}


def stata_pctile(x, p):
    """Percentile as Stata's summarize, detail / _pctile (default definition)."""
    x = np.sort(np.asarray(x, float))
    n = len(x)
    P = n * p / 100.0
    if abs(P - round(P)) < 1e-9:
        i = int(round(P))
        return (x[i - 1] + x[i]) / 2 if i < n else x[n - 1]
    return x[int(np.floor(P))]


def xtile3(x):
    """Stata xtile nq(3): category by cut points at the 33.3 and 66.7 percentiles (x <= cut)."""
    c1 = stata_pctile(x, 100 / 3.0)
    c2 = stata_pctile(x, 200 / 3.0)
    x = np.asarray(x, float)
    return np.where(x <= c1, 1, np.where(x <= c2, 2, 3)), (c1, c2)


def drow(blk, smp, model, itm, resp=None, obs=None, clus=None, est=None, se=None, lb=None, ub=None, p=None, note=""):
    lab, base = LAB_R.get(itm, (itm, ""))
    E = np.nan if est is None else est
    S = np.nan if se is None else se
    return dict(block=blk, sample=smp, model=model, item=itm, label=lab, base=base, n_resp=resp, n_obs=obs, n_clust=clus,
                est=E, se=S, lb=(E - Z * S) if lb is None else lb, ub=(E + Z * S) if ub is None else ub,
                p=(2 * normal_cdf(-abs(E / S)) if S == S and S > 0 else np.nan) if p is None else p, note=note)


def nresp(d):
    return d["id"].nunique()


def org_run(d, smp, model, rows, cond=None, extra=(), vce="id", note="", ow=None):
    dd = d if cond is None else d[cond(d)]
    X = ["log_salary"] + list(extra) + XR
    f = clogit(dd, "chosen", X, "choice_set", vce)
    no, nc, nr = f.N, f.G, nresp(dd)
    for t in ["log_salary"] + list(extra) + TR:
        rows.append(drow("coef", smp, model, t, nr, no, nc, f.b[f.idx[t]], f.se[f.idx[t]], note=note))
    for t in TR:
        e, s, _ = nlcom(f, lambda b: 100 * (np.exp(-b[t] / b["log_salary"]) - 1))
        rows.append(drow("wtp", smp, model, t, nr, no, nc, e[0], s[0],
                         note="% salary change at indifference (negative = discount required); weakly identified (R1-R9); " + note))
        if smp == "main" and ow is not None:
            ow[t] = (e[0], s[0])
    for t in ["1.place", "2.place", "3.place", "1.timeflex", "2.timeflex", "1.load", "2.load", "1.retention", "0.collaborative"]:
        e, s, _ = nlcom(f, lambda b: b[t] / b["2.retention"])
        pp = wald(f, [{t: 1, "2.retention": -1}])[2]
        rows.append(drow("ratio_to_highturnover", smp, model, t, nr, no, nc, e[0], s[0], p=pp,
                         note="R11 salary-free: coefficient / high-turnover coefficient; p tests equality (ratio=1); " + note))
    for t in TR:
        pp = 2 * normal_cdf(-abs(f.b[f.idx[t]] / f.se[f.idx[t]]))
        e, s, _ = nlcom(f, lambda b: 100 * invlogit(b[t]))
        rows.append(drow("eqpay", smp, model, t, nr, no, nc, e[0], s[0], p=pp,
                         note="R12/Q table: % of employers picking this candidate over the base candidate at equal salary; p tests b=0 (50%); " + note))
    return f


def run_dce_wtp(d, emp_wtp_csv):
    rows, ow = [], {}
    M = "clogit: log salary + attributes; SE clustered by firm respondent"
    org_run(d, "main", M, rows, note="R1-R9 main model", ow=ow)
    org_run(d, "left_asc", "clogit: main + displayed-left ASC; SE by respondent", rows, extra=["left"])
    org_run(d, "block_cluster", "clogit: main; SE clustered by design block (10 clusters)", rows, vce="design_block",
            note="R4: 10 clusters; SEs unreliable")
    org_run(d, "excl_same_side", M, rows, cond=lambda x: x["ss"] == 0, note="drops respondents who always chose the same side")
    org_run(d, "excl_salary_out", M, rows, cond=lambda x: x["salary_out"] == 0,
            note="drops firms with reference salary outside SGD 2000-50000")
    ew = pd.read_csv(emp_wtp_csv)
    ew = ew[(ew["block"] == "wtp") & (ew["sample"] == "main")].set_index("item")
    for t in ["1.place", "2.place", "3.place", "1.timeflex", "2.timeflex", "1.load", "2.load"]:
        e = -ow[t][0] - ew.loc[t, "est"]
        s = np.sqrt(ow[t][1] ** 2 + ew.loc[t, "se"] ** 2)
        nt = "INDICATIVE backup only (G1-G6): difference of two functional-form-dependent numbers; independent-sample delta SE"
        if t == "3.place":
            nt += "; employee comparator is onsite with a long commute; employer magnitude beyond tested range"
        if t == "1.load":
            nt += "; employers saw Reduced-load (4 days/week), employees saw Job sharing (4 days/week); hours change"
        if t == "2.load":
            nt += "; hours change: mostly pro-rata pay, not a flexibility price"
        rows.append(drow("gap_indicative", "main", "gap = -(employer WTP) - (employee WTP); main models", t, est=e, se=s, note=nt))
    # rank model
    f = clogit(d, "chosen", ["lo"] + XR, "choice_set", "id")
    no, nc, nr = f.N, f.G, nresp(d)
    MR = "clogit: cheaper-candidate dummy (rank) + attributes; SE by respondent"
    for t in ["lo"] + TR:
        rows.append(drow("coef", "rank_model", MR, t, nr, no, nc, f.b[f.idx[t]], f.se[f.idx[t]]))
    for t in TR:
        pp = 2 * normal_cdf(-abs(f.b[f.idx[t]] / f.se[f.idx[t]]))
        e, s, _ = nlcom(f, lambda b: 100 * invlogit(b[t]))
        rows.append(drow("eqpay", "rank_model", MR, t, nr, no, nc, e[0], s[0], p=pp,
                         note="Q table [rank model]; p tests b=0 i.e. 50%"))
        e, s, _ = nlcom(f, lambda b: b[t] / b["lo"])
        rows.append(drow("ratio_to_rank", "rank_model", MR, t, nr, no, nc, e[0], s[0], note="coefficient / cheaper-candidate coefficient"))
    for t in ["1.place", "2.place", "3.place", "1.timeflex", "2.timeflex", "1.load", "2.load", "1.retention"]:
        e, s, _ = nlcom(f, lambda b: b[t] / b["2.retention"])
        pp = wald(f, [{t: 1, "2.retention": -1}])[2]
        rows.append(drow("ratio_to_highturnover", "rank_model", MR, t, nr, no, nc, e[0], s[0], p=pp,
                         note="R11 [rank model]; p tests equality with the high-turnover coefficient"))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ model-free (section 5, employers)
def mfrow(d, mask, blk, grp, itm, val=None, note="", invert=False):
    sub = d[mask]
    n = len(sub)
    k = int((sub["chosen"] == 1).sum())
    if invert:
        k = n - k
    nr = sub["id"].nunique()
    sh = lb = ub = np.nan
    kk = float(k)
    v = np.nan if val is None else val
    if n == 0:
        kk = np.nan
        note = ("no such choices in the design. " + note).strip()
    elif n < MINCELL:
        kk = np.nan
        v = np.nan
        note = ("suppressed: n<%d choices. " % MINCELL + note).strip()
    else:
        sh = 100 * k / n
        lb, ub = wilson(k, n)
    return dict(block=blk, sample="all", side="employer", group=grp, item=itm, n=n, n_resp=nr, k=kk, share=sh, lb=lb, ub=ub,
                value=v, note=note)


def run_modelfree(d):
    rows = []
    d = d.copy()
    d["dl"] = np.log(d["smax"]) - np.log(d["smin"])
    tag = d.groupby("choice_set").cumcount() == 0
    d["tagcs"] = tag
    cs = d[tag & True].copy()
    q, cuts = xtile3(cs["dl"].to_numpy())
    cs["gq3"] = q
    d["gq"] = d["choice_set"].map(cs.set_index("choice_set")["gq3"])
    gt = {}
    for q_ in (1, 2, 3):
        s = cs.loc[cs["gq3"] == q_, "dl"]
        gt[q_] = (f"{s.min():5.3f}", f"{s.max():5.3f}", s.mean())
    lo1 = d["lo"] == 1
    rows.append(mfrow(d, lo1, "cheaper_chosen", "All choice sets", "Chose the cheaper candidate", note="R13"))
    for t in range(1, 7):
        rows.append(mfrow(d, lo1 & (d["task"] == t), "cheaper_by_task", f"Task {t}", "Chose the cheaper candidate"))
    for q_ in (1, 2, 3):
        a, b, m = gt[q_]
        rows.append(mfrow(d, lo1 & (d["gq"] == q_), "cheaper_by_gap_tercile", f"Gap tercile {q_}", "Chose the cheaper candidate",
                          val=m, note=f"displayed log pay gap {a.strip()}-{b.strip()}; value = mean log gap"))
    GK = sorted(d.loc[tag, "gkey"].unique())
    for g in GK:
        cut = f"{100 * (1 - np.exp(-g / 1000)):4.1f}"
        rows.append(mfrow(d, lo1 & (d["gkey"] == g), "cheaper_by_design_gap", f"Design log gap 0.{g}", "Chose the cheaper candidate",
                          val=g / 1000, note=f"cheaper candidate {cut}% below the dearer one"))
    for v in ("place", "timeflex", "load"):
        dd = d.copy()
        dd["vmax"] = dd.groupby("choice_set")[v].transform("max")
        dd["vmin"] = dd.groupby("choice_set")[v].transform("min")
        if v == "place":
            dd = dd[(dd["vmin"] == 0) & (dd["vmax"] > 0)]
        else:
            dd = dd[(dd["vmin"] == 0) & (dd["vmax"] > 0) & (dd["vmax"] < 3)]
        dd = dd[dd[v] > 0].copy()
        dd["flexcheap"] = (dd["hi"] == 0).astype(int)
        for l in sorted(dd[v].unique()):
            if v == "place":
                ll = {1: "1-2 days WFH vs fully onsite", 2: "3-4 days WFH vs fully onsite"}.get(int(l), "Fully remote vs fully onsite")
            elif v == "timeflex":
                ll = "Staggered vs fixed hours" if l == 1 else "Compressed 4-day week vs fixed hours"
            else:
                ll = "Reduced load (4 days) vs full-time" if l == 1 else "Part-time vs full-time"
            rows.append(mfrow(dd, (dd[v] == l) & (dd["flexcheap"] == 1), "flexible_vs_base", "Flexible candidate cheaper", ll,
                              note="share choosing the flexible candidate"))
            rows.append(mfrow(dd, (dd[v] == l) & (dd["flexcheap"] == 0), "flexible_vs_base", "Flexible candidate dearer", ll,
                              note="share choosing the flexible candidate"))
        if v == "place":
            rows.append(mfrow(dd, (dd["place"] == 3) & (dd["flexcheap"] == 1), "remote_vs_onsite", "Fully remote candidate cheaper",
                              "Chose the on-site candidate", note="R13: complement of the flexible share", invert=True))
            for t in range(1, 7):
                rows.append(mfrow(dd, (dd["place"] == 3) & (dd["flexcheap"] == 1) & (dd["task"] == t), "remote_vs_onsite_by_task",
                                  f"Remote candidate cheaper; task {t}", "Chose the fully remote candidate"))
                rows.append(mfrow(dd, (dd["place"] == 3) & (dd["flexcheap"] == 0) & (dd["task"] == t), "remote_vs_onsite_by_task",
                                  f"Remote candidate dearer; task {t}", "Chose the fully remote candidate"))
            GR = sorted(dd.loc[(dd["place"] == 3) & (dd["flexcheap"] == 1), "gkey"].unique())
            for g in GR:
                cut = f"{100 * (1 - np.exp(-g / 1000)):4.1f}"
                rows.append(mfrow(dd, (dd["place"] == 3) & (dd["flexcheap"] == 1) & (dd["gkey"] == g), "remote_cheaper_by_gap",
                                  f"Design log gap 0.{g}", "Chose the fully remote candidate (remote cheaper)", val=g / 1000,
                                  note=f"remote candidate {cut}% cheaper"))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ rank vs log (section 7, employers)
def run_rank(d):
    rows = []
    X = XR
    R = "lo"
    cs = d[d["lo"] == 1]

    def rp(model, spec, f, note=""):
        k = len(f.b)
        ll = f.ll
        def g(c):
            return (f.b[f.idx[c]], f.se[f.idx[c]]) if c in f.idx else (np.nan, np.nan)
        bl, sl = g("log_salary"); br, sr = g("lo"); bf, sf = g("left")
        rows.append(dict(side="employer", model=model, spec=spec, n_obs=f.N, n_resp=nresp(d), ll=ll, k=k, aic=-2 * ll + 2 * k,
                         bic=-2 * ll + k * np.log(f.N), b_logsal=bl, se_logsal=sl, b_rank=br, se_rank=sr, b_left=bf, se_left=sf,
                         lr=np.nan, lr_df=np.nan, lr_p=np.nan, note=note))
    f0 = clogit(d, "chosen", ["log_salary"] + X, "choice_set", "id"); rp("M0", "log salary (published main model)", f0)
    f1 = clogit(d, "chosen", ["lo"] + X, "choice_set", "id"); rp("M1", "rank only (cheaper-candidate dummy)", f1)
    f2 = clogit(d, "chosen", ["log_salary", "lo"] + X, "choice_set", "id"); rp("M2", "log salary + rank", f2)
    q, _ = xtile3(cs["lgap_design"].to_numpy())
    g3 = pd.Series(q, index=cs["choice_set"].to_numpy())
    g3s = d["choice_set"].map(g3)
    dd = d.copy()
    for k_ in (1, 2, 3):
        dd[f"lo_g{k_}"] = (dd["lo"] * (g3s == k_)).astype(float)
    f3 = clogit(dd, "chosen", ["lo_g1", "lo_g2", "lo_g3"] + X, "choice_set", "id")
    p3 = wald(f3, [{"lo_g1": 1, "lo_g2": -1}, {"lo_g2": 1, "lo_g3": -1}])[2]
    rp("M3", "rank x design-gap tercile", f3,
       note=f"tercile coefs {f3.b[0]:.3f} / {f3.b[1]:.3f} / {f3.b[2]:.3f}; equality p = {p3:.4f}")
    f4 = clogit(d, "chosen", ["log_salary", "left"] + X, "choice_set", "id"); rp("M4", "log salary + left ASC", f4)
    f5 = clogit(d, "chosen", ["lo", "left"] + X, "choice_set", "id"); rp("M5", "rank + left ASC", f5)
    f6 = clogit(d, "chosen", ["log_salary", "lo", "left"] + X, "choice_set", "id"); rp("M6", "log salary + rank + left ASC", f6)
    for spec, lr, note in (("M2 vs M0: does rank add to log salary?", 2 * (f2.ll - f0.ll), "LL identical with or without clustering"),
                           ("M2 vs M1: does log salary add to rank?", 2 * (f2.ll - f1.ll), "")):
        rows.append(dict(side="employer", model="LR", spec=spec, n_obs=np.nan, n_resp=np.nan, ll=np.nan, k=np.nan, aic=np.nan,
                         bic=np.nan, b_logsal=np.nan, se_logsal=np.nan, b_rank=np.nan, se_rank=np.nan, b_left=np.nan,
                         se_left=np.nan, lr=lr, lr_df=1, lr_p=float(stats.chi2.sf(lr, 1)), note=note))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ design (section 6, employers)
def run_design(d):
    rows = []
    def post(block, item, value, note=""):
        rows.append(dict(side="employer", block=block, item=item, value=value, note=note))
    d = d.copy()
    for v in ("place", "timeflex", "load", "jobculture"):
        h = d[v].where(d["hi"] == 1)
        l = d[v].where(d["hi"] == 0)
        H = h.groupby(d["choice_set"]).transform("max")
        L = l.groupby(d["choice_set"]).transform("max")
        d[f"V_h_{v}"] = np.where(H != L, H, -1)
        d[f"V_l_{v}"] = np.where(H != L, L, -1)
    h = d["retention"].where(d["hi"] == 1); l = d["retention"].where(d["hi"] == 0)
    H = h.groupby(d["choice_set"]).transform("max"); L = l.groupby(d["choice_set"]).transform("max")
    d["V_h_r"] = np.where(H != L, H, -1); d["V_l_r"] = np.where(H != L, L, -1)
    d["V_h_c"] = -1; d["V_l_c"] = -1   # h_c = l_c = 0 for employers -> H == L
    tagid = d.groupby("id").cumcount() == 0
    nresp_ = int(tagid.sum())
    nleft = int(((d["left"] == 1) & (d["chosen"] == 1)).sum())
    tagcs = d.groupby("choice_set").cumcount() == 0
    nsets = int(tagcs.sum())
    post("counts", "Respondents", nresp_)
    post("counts", "Choice sets (6 per respondent)", nsets, "S1/S2")
    post("position", "Share of choices for the displayed-left option (%)", 100 * nleft / nsets)
    cs = d[tagcs].copy()
    post("salary_grid", "Sets pairing a below-1 with an above-1 multiplier (%)", 100 * ((cs["rmin"] < 1) & (cs["rmax"] > 1)).sum() / len(cs), "S6")
    lg = cs["lgap_design"].to_numpy()
    mn, p5, p50, mx = lg.min(), stata_pctile(lg, 5), stata_pctile(lg, 50), lg.max()
    post("salary_grid", "Design log gap ln(rmax/rmin): min", mn, "S6")
    post("salary_grid", "Design log gap: p5", p5)
    post("salary_grid", "Design log gap: median", p50)
    post("salary_grid", "Design log gap: max", mx, "S6")
    post("salary_grid", "Design % cut of lower vs higher offer: min", 100 * (1 - np.exp(-mn)), "S6: 17%")
    post("salary_grid", "Design % cut of lower vs higher offer: median", 100 * (1 - np.exp(-p50)))
    post("salary_grid", "Design % cut of lower vs higher offer: max", 100 * (1 - np.exp(-mx)), "S6: 33%")
    lg2 = cs["lgap"].to_numpy()
    post("salary_displayed", "Displayed log gap ln(smax/smin): min", lg2.min(), "after rounding to SGD 50 and clamping")
    for lab, p in (("p1", 1), ("p5", 5), ("median", 50)):
        post("salary_displayed", f"Displayed log gap: {lab}", stata_pctile(lg2, p))
    post("salary_displayed", "Displayed log gap: max", lg2.max())
    pc = (100 * (1 - cs["smin"] / cs["smax"])).to_numpy()
    post("salary_displayed", "Displayed % cut of lower vs higher offer: min", pc.min())
    post("salary_displayed", "Displayed % cut: p5", stata_pctile(pc, 5))
    post("salary_displayed", "Displayed % cut: median", stata_pctile(pc, 50))
    post("salary_displayed", "Displayed % cut: max", pc.max())
    pr = (100 * (cs["smax"] / cs["smin"] - 1)).to_numpy()
    post("salary_displayed", "Displayed % premium of higher vs lower offer: min", pr.min())
    post("salary_displayed", "Displayed % premium: median", stata_pctile(pr, 50))
    post("salary_displayed", "Displayed % premium: max", pr.max())
    GK = sorted(cs["gkey"].unique())
    post("salary_grid", "Distinct design log-gap values", len(GK), " ".join(str(int(g)) for g in GK) + " (x1000)")
    post("blocks", "Design blocks (fixed survey versions)", cs["design_block"].nunique())
    post("blocks", "Distinct block x task choice situations", cs.groupby(["design_block", "task"]).ngroups, "section 9: 60 distinct choice situations")
    key = ["task", "rmin", "rmax", "V_h_place", "V_l_place", "V_h_timeflex", "V_l_timeflex", "V_h_load", "V_l_load",
           "V_h_jobculture", "V_l_jobculture", "V_h_r", "V_l_r", "V_h_c", "V_l_c"]
    post("blocks", "Distinct varied-attribute configurations (task, salary pair, varied levels by pay side)",
         d.groupby(key, dropna=False).ngroups, "")
    t1 = d[d["task"] == 1].groupby("design_block")["id"].nunique()
    # contract design_block on the task==1 rows: rows (choice sets x 2 options) per block, as in the do-file
    t1r = cs[cs["task"] == 1].groupby("design_block").size()
    post("blocks", "Respondents per block: min", t1r.min())
    post("blocks", "Respondents per block: max", t1r.max())
    return pd.DataFrame(rows), t1


# ------------------------------------------------------------------ eqpay (deck_eqpay.do, employers)
def run_eqpay(d0):
    d = d0.copy()
    rows = []
    d["mins"] = d.groupby("choice_set")["log_salary"].transform("min")
    d["lo"] = (d["log_salary"] == d["mins"]).astype(float)
    LV = [("1.place", "1-2 days WFH"), ("2.place", "3-4 days WFH"), ("3.place", "Fully remote"), ("1.timeflex", "Staggered hours"),
          ("2.timeflex", "Compressed 4-day week"), ("1.load", "Reduced load (4 days/week)"), ("2.load", "Part-time"),
          ("1.retention", "Moderate turnover risk"), ("2.retention", "High turnover risk (>20%)")]

    def post(split, grp, glab, nres, f, term, label, model, jp):
        e, s, _ = nlcom(f, lambda b: invlogit(b[term]))
        rows.append(dict(side="employer", split=split, group=grp, glabel=glab, n_resp=nres, level=term, label=label, model=model,
                         prob=e[0], lb=e[0] - 1.96 * s[0], ub=e[0] + 1.96 * s[0], joint_p=jp))
    for m in ("log", "rank"):
        sal = "log_salary" if m == "log" else "lo"
        f = clogit(d, "chosen", [sal] + XR, "choice_set", "id")
        for term, label in LV:
            post("main", 0, "All employers", f.G, f, term, label, m, np.nan)
    g = {}
    g["physical"] = d["physical_presence"].eq(1).where(d["physical_presence"].notna())
    g["creative"] = (d["creativity_concern"] >= 4).where(d["creativity_concern"].notna())
    g["product"] = (d["productivity_concern"] >= 4).where(d["productivity_concern"].notna())
    g["coord"] = (d["coordination_concern"] >= 4).where(d["coordination_concern"].notna())
    cm = d[["productivity_concern", "coordination_concern", "creativity_concern"]].mean(axis=1, skipna=True)
    g["concern"] = (cm > 3).where(cm.notna())
    g["nowfh"] = (d["remote"] == 1).where(d["remote"].notna())
    g["notready"] = (d["tech_readiness"] <= 2).where(d["tech_readiness"].notna())
    g["nopolicy"] = (d["fwa_policy"] == 2).where(d["fwa_policy"].notna())
    g["belief"] = (d["salary_offset"] >= 4).where(d["salary_offset"].notna())
    large = pd.Series(np.nan, index=d.index)
    large = large.mask(d["orgsize"].notna(), (d["orgsize"] > 1000).astype(float))
    large = large.mask(d["orgsize"].isna() & d["orgsize_cat"].notna(), (d["orgsize_cat"] == 6).astype(float))
    g["large"] = large
    sme = pd.Series(np.nan, index=d.index)
    sme = sme.mask(d["orgsize"].notna(), (d["orgsize"] <= 200).astype(float))
    sme = sme.mask(d["orgsize"].isna() & d["orgsize_cat"].notna(), d["orgsize_cat"].isin([1, 2, 3]).astype(float))
    g["sme"] = sme
    labs = {"physical": ("Some or few PME roles need presence", "Most PME roles need presence"),
            "creative": ("Not worried about creativity", "Worried creativity suffers"),
            "product": ("Not worried about productivity", "Worried about productivity"),
            "coord": ("Not worried about coordination", "Worried about coordination"),
            "concern": ("Low overall concern", "High overall concern"),
            "nowfh": ("Some WFH today", "No WFH today"),
            "notready": ("Fully tech-ready", "Not fully tech-ready"),
            "nopolicy": ("Written FWA policy", "No written FWA policy"),
            "belief": ("Disagree/neutral: FWAs let us pay less", "Agree: FWAs let us pay less"),
            "large": ("Up to 1,000 staff", "1,001+ staff"), "sme": ("201+ staff", "Up to 200 staff")}
    for split in ("physical", "creative", "product", "coord", "concern", "nowfh", "notready", "nopolicy", "belief", "large", "sme"):
        gv = g[split]
        s = d[gv.notna()].copy()
        gg = gv[gv.notna()].astype(float)
        gx = []
        for k in (1, 2, 3):
            s[f"gx_p{k}"] = gg * (s["place"] == k); gx.append(f"gx_p{k}")
        for k in (1, 2):
            s[f"gx_t{k}"] = gg * (s["timeflex"] == k); gx.append(f"gx_t{k}")
            s[f"gx_l{k}"] = gg * (s["load"] == k); gx.append(f"gx_l{k}")
            s[f"gx_r{k}"] = gg * (s["retention"] == k); gx.append(f"gx_r{k}")
        fp = clogit(s, "chosen", ["log_salary"] + XR + gx, "choice_set", "id")
        jp = wald(fp, [{"gx_p1": 1}, {"gx_p2": 1}, {"gx_p3": 1}])[2]
        for grp in (0, 1):
            glab = labs[split][grp]
            sub = s[gg == grp]
            f = clogit(sub, "chosen", ["log_salary"] + XR, "choice_set", "id")
            for term, label in (("1.place", "1-2 days WFH"), ("2.place", "3-4 days WFH"), ("3.place", "Fully remote"),
                                ("2.timeflex", "Compressed 4-day week"), ("1.timeflex", "Staggered hours"), ("2.load", "Part-time")):
                post(split, grp, glab, f.G, f, term, label, "log", jp)
    return pd.DataFrame(rows)
