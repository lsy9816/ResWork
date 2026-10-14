"""compressed_employer -- Python port of the EMPLOYER sections (A, D, and employer part of F) of
deck_mech_compressed.do.  run(dta_path, appended, outdir) writes compressed_puzzle.csv: the professor's
employee rows (sections B, C, E) copied unchanged from the professor's CSV plus recomputed employer rows.
"""
import csv, io, os, sys, re
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stata_core as sc
import employer_data as ed

import os
PROF_CSV = os.path.join(os.environ.get("DECK_SUPPORT", os.path.expanduser("~/Dropbox/ResWork_SY/SNEF_survey/final/deck_support")),
                        "mechanisms", "compressed_puzzle.csv")
Z = stats.norm.ppf(0.975)
LOG = []          # diagnostics (collinearity, perfect prediction, small cells ...)
COLS = ["sec", "analysis", "sample", "split", "group", "item", "metric", "n", "k", "est", "lb", "ub", "p",
        "family", "q", "note"]
nan = np.nan


def ncdf(x):
    return stats.norm.cdf(x)


# ---------------------------------------------------------------- labels (from the do-file)
LAB = {
    "size3": {0: "200 or fewer staff", 1: "201-1,000 staff", 2: "1,001+ staff"},
    "wfh3": {0: "No WFH today", 1: "1-2 days WFH typical", 2: "3+ days WFH typical"},
    "nowfh": {0: "Some WFH today", 1: "No WFH today"},
    "policy": {0: "No written FWA policy", 1: "Written FWA policy"},
    "nopolicy": {0: "Written FWA policy", 1: "No written FWA policy"},
    "tech_readiness": {1: "Not ready", 2: "Partially ready (significant gaps)", 3: "Fully ready"},
    "techfull": {0: "Not fully tech-ready", 1: "Fully tech-ready"},
    "notready": {0: "Fully tech-ready", 1: "Not fully tech-ready"},
    "physical_presence": {1: "Most roles require physical presence", 2: "Some roles require presence",
                          3: "Few or no roles require presence"},
    "mostphys": {0: "Some or few PME roles need presence", 1: "Most PME roles need presence"},
    "ag_productivity": {0: "Not worried about productivity", 1: "Worried about productivity"},
    "ag_coordination": {0: "Not worried about coordination", 1: "Worried about coordination"},
    "ag_creativity": {0: "Not worried about creativity", 1: "Worried creativity suffers"},
    "ag_fairness": {0: "Not worried about fairness", 1: "Unfair to frontline staff (agree)"},
    "ag_talent": {0: "Disagree/neutral: FWAs help attract talent", 1: "Agree: FWAs help attract talent"},
    "ag_offset": {0: "Disagree/neutral: salary offset", 1: "Agree: FWAs reduce salary needed"},
    "concern": {0: "Low overall concern", 1: "High overall concern"},
    "hiredif": {0: "No PME hiring difficulty", 1: "Some or significant hiring difficulty"},
    "turn_hi": {0: "Low PME turnover (<10%)", 1: "Moderate or high PME turnover (10%+)"},
    "expand": {0: "Not planning to expand FWAs", 1: "Plans to expand FWAs"},
    "offer_stag": {0: "Does not offer staggered hours", 1: "Offers staggered hours"},
    "offer_pt": {0: "Does not offer part-time", 1: "Offers part-time"},
    "offer_js": {0: "Does not offer job sharing", 1: "Offers job sharing"},
    "offer_rem": {0: "No remote work", 1: "Offers some remote work"},
    "offer_cmp": {0: "Does not offer a compressed week", 1: "Offers a compressed week"},
    "n_oth": {0: "No other time/load FWA", 1: "One other", 2: "Two other", 3: "Three other"},
    "indg": {3: "Information and communications", 7: "Construction", 10: "Financial and insurance services",
             12: "Manufacturing", 15: "Professional services", 16: "Public administration and education",
             20: "Transportation and storage", 99: "Other industries (each <20 firms)"},
    "chal": {1: "Productivity and output quality", 2: "Coordination and communication",
             3: "Fairness (not all roles can be flexible)", 4: "Lack of digital infrastructure",
             5: "Managerial resistance or lack of trust", 7: "Security/compliance or other"},
    "pmesh": {1: "PMEs <25% of staff", 2: "PMEs 25-49%", 3: "PMEs 50%+"},
    "foreignhq": {0: "Headquartered in Singapore", 1: "Foreign/regional HQ"},
}
VLAB = {"size3": "Firm size", "wfh3": "Typical PME WFH", "policy": "Written FWA policy",
        "techfull": "Fully tech-ready", "mostphys": "Most PME roles need presence", "indg": "Industry",
        "ag_productivity": "Worried about productivity", "ag_coordination": "Worried about coordination",
        "ag_creativity": "Worried creativity suffers", "ag_fairness": "Unfair to frontline staff",
        "ag_talent": "FWAs help attract talent", "hiredif": "PME hiring difficulty",
        "offer_stag": "Offers staggered hours", "offer_pt": "Offers part-time", "turn_hi": "Moderate/high PME turnover"}


def lab(v, l):
    return LAB[v].get(int(l), str(int(l)))


# ---------------------------------------------------------------- data preparation (employer block of the do-file)
def prepare(path, appended):
    d = ed.load(path, appended)
    c = lambda s: d[s]
    ind = lambda cond, base=None: cond.astype(float)
    # size6 / size3
    o = c("orgsize")
    s6 = pd.Series(nan, index=d.index)
    s6[(o >= 0) & (o < 10)] = 1
    s6[(o >= 10) & (o <= 50)] = 2
    s6[(o >= 51) & (o <= 200)] = 3
    s6[(o >= 201) & (o <= 500)] = 4
    s6[(o >= 501) & (o <= 1000)] = 5
    s6[(o >= 1001)] = 6
    oc = c("orgsize_cat")
    m = s6.isna() & (oc >= 1) & (oc <= 6)
    s6[m] = oc[m]
    d["size6"] = s6
    d["size3"] = np.where(s6.isna(), nan, np.where(s6 <= 3, 0, np.where(s6.isin([4, 5]), 1, 2)))

    def b(cond, src=None):
        r = cond.astype(float)
        if src is not None:
            r = r.where(src.notna())
        return r
    d["offer_cmp"] = b((c("fwa_compressed") == 1) | (c("schedule") == 3))
    d["tick_cmp"] = b(c("fwa_compressed") == 1)
    d["typ_cmp"] = b(c("schedule") == 3)
    d["offer_stag"] = b((c("fwa_staggered") == 1) | (c("schedule") == 2))
    d["offer_pt"] = b((c("fwa_parttime") == 1) | (c("workload") == 3))
    d["offer_js"] = b((c("fwa_jobshare") == 1) | (c("workload") == 2))
    d["offer_rem"] = b((c("fwa_adhoc") == 1) | (c("fwa_schedremote") == 1) | (c("fwa_fullremote") == 1)
                       | c("remote").isin([2, 3, 4]))
    d["n_oth"] = d.offer_stag + d.offer_pt + d.offer_js
    r = c("remote")
    d["wfh3"] = np.where(r.isna(), nan, np.where(r == 1, 0, np.where(r == 2, 1, 2)))
    d["nowfh"] = b(r == 1, r)
    d["policy"] = b(c("fwa_policy") == 1, c("fwa_policy"))
    d["nopolicy"] = b(c("fwa_policy") == 2, c("fwa_policy"))
    d["techfull"] = b(c("tech_readiness") == 3, c("tech_readiness"))
    d["notready"] = b(c("tech_readiness") <= 2, c("tech_readiness"))
    d["mostphys"] = b(c("physical_presence") == 1, c("physical_presence"))
    for v in ["productivity", "coordination", "creativity", "fairness"]:
        d["ag_" + v] = b(c(v + "_concern") >= 4, c(v + "_concern"))
    d["ag_talent"] = b(c("talent_benefit") >= 4, c("talent_benefit"))
    d["ag_offset"] = b(c("salary_offset") >= 4, c("salary_offset"))
    cm = d[["productivity_concern", "coordination_concern", "creativity_concern"]].mean(axis=1, skipna=True)
    d["concern"] = b(cm > 3, cm)
    d["hiredif"] = b(c("hiring_difficulty").isin([1, 2]), c("hiring_difficulty"))
    t = c("turnover")
    d["turn_hi"] = b(t.isin([2, 3]), t).where((t >= 1) & (t <= 3))
    d["expand"] = b(c("fwa_plan").isin([1, 2]), c("fwa_plan"))
    ig = c("industry").copy()
    ig[~ig.isin([3, 7, 10, 12, 15, 16, 20])] = 99
    d["indg"] = ig
    ch = c("fwa_challenge").copy()
    ch[ch.isin([6, 7])] = 7
    d["chal"] = ch
    pm = c("pme_share").copy()
    pm[pm == 4] = 3
    d["pmesh"] = pm
    d["foreignhq"] = b(c("sg_status") == 4, c("sg_status"))
    return d


# ---------------------------------------------------------------- posting helpers
class Post:
    def __init__(self):
        self.rows = []

    def add(self, sec, an, smp, spl, grp, itm, metric, n=nan, k=nan, est=nan, lb=nan, ub=nan, p=nan, fam="", note=""):
        self.rows.append(dict(sec=sec, analysis=an, sample=smp, split=spl, group=grp, item=itm, metric=metric,
                              n=n, k=k, est=est, lb=lb, ub=ub, p=p, family=fam, q=nan, note=note))


def shpost(P, d, y, mask, sec, an, smp, spl, grp, itm, minn=5, note=""):
    sub = d.loc[mask & d[y].notna(), y]
    n = len(sub)
    k = int((sub == 1).sum())
    if n < minn:
        nshow = n if n >= 5 else nan
        P.add(sec, an, smp, spl, grp, itm, "share", nshow, nan, nan, nan, nan, nan, "",
              f"suppressed: base n<{minn} (n itself withheld when <5). {note}")
        LOG.append(f"suppressed share: {spl} / {grp} n={n} (minn={minn})")
    else:
        lb, ub = sc.wilson(k, n)
        P.add(sec, an, smp, spl, grp, itm, "share", n, k, 100 * k / n, max(0, lb), min(100, ub), nan, "", note)


def shsplit(P, d, y, g, sec, an, smp, spl, itm, minn=5, note=""):
    ok = d[y].notna() & d[g].notna()
    for l in sorted(d.loc[ok, g].unique()):
        shpost(P, d, y, ok & (d[g] == l), sec, an, smp, spl, lab(g, l), itm, minn, note)
    sub = d.loc[ok]
    tab = pd.crosstab(sub[y], sub[g])
    r, c = tab.shape
    if r >= 2 and c >= 2:
        chi2, p, dof, _ = stats.chi2_contingency(tab.values, correction=False)
        P.add(sec, an, smp, spl, "All groups", itm, "chi2_p", len(sub), (r - 1) * (c - 1), chi2, nan, nan, p, "",
              "Pearson chi2 test of equal shares across all groups (est = chi2, k = df)")
    else:
        LOG.append(f"chi2 not computable for {spl}: table {r}x{c}")


# ---------------------------------------------------------------- logit with robust SE and AME
def factor_cols(terms):
    """term like '1.size3' -> (level, var)"""
    out = []
    for t in terms:
        m = re.match(r"^(\d+)\.(.+)$", t)
        out.append((int(m.group(1)), m.group(2)))
    return out


def logit_robust(d, y, factors):
    """factors: list of (var, base).  Returns dict with fit pieces.  Mimics Stata logit, vce(robust):
    drops perfectly predicted dummy + its observations, omitted (collinear) dummies."""
    vars_ = [v for v, _ in factors]
    dd = d.dropna(subset=[y] + vars_).copy()
    cols, meta = [], []
    for v, base in factors:
        for l in sorted(dd[v].unique()):
            if l == base:
                continue
            nm = f"{int(l)}.{v}"
            dd[nm] = (dd[v] == l).astype(float)
            cols.append(nm)
            meta.append((v, l))
    omitted = []
    while True:  # perfect prediction check (dummy == 1 -> y constant)
        drop = None
        for nm in cols:
            if nm in omitted:
                continue
            s = dd.loc[dd[nm] == 1, y]
            if len(s) and s.nunique() == 1:
                drop = nm
                break
            if len(s) == 0:
                omitted.append(nm)
                LOG.append(f"logit {y}: {nm} has no observations (omitted)")
        if drop is None:
            break
        LOG.append(f"logit {y}: {drop} predicts {'success' if s.iloc[0]==1 else 'failure'} perfectly; omitted, "
                   f"{int((dd[drop]==1).sum())} obs dropped")
        dd = dd.loc[dd[drop] != 1]
        omitted.append(drop)
    use = [nm for nm in cols if nm not in omitted]
    X = np.column_stack([dd[use].to_numpy(float), np.ones(len(dd))])
    yv = dd[y].to_numpy(float)
    if np.linalg.matrix_rank(X) < X.shape[1]:
        LOG.append(f"logit {y}: collinear columns (rank {np.linalg.matrix_rank(X)} < {X.shape[1]})")
    b = np.zeros(X.shape[1])
    for it in range(100):
        p = 1 / (1 + np.exp(-X @ b))
        g = X.T @ (yv - p)
        H = (X * (p * (1 - p))[:, None]).T @ X
        step = np.linalg.solve(H, g)
        b = b + step
        if np.max(np.abs(step)) < 1e-12:
            break
    p = 1 / (1 + np.exp(-X @ b))
    H = (X * (p * (1 - p))[:, None]).T @ X
    Hinv = np.linalg.inv(H)
    S = X * (yv - p)[:, None]
    N = len(yv)
    V = N / (N - 1) * Hinv @ (S.T @ S) @ Hinv
    kk = X.shape[1] - 1
    chi2 = float(b[:kk] @ np.linalg.solve(V[:kk, :kk], b[:kk]))
    pmodel = float(stats.chi2.sf(chi2, kk))
    # AME (margins, dydx(*), discrete change from base level)
    names = use
    ame, ame_se = {}, {}
    for j, nm in enumerate(use):
        v = nm.split(".", 1)[1]
        same = [i for i, n2 in enumerate(use) if n2.split(".", 1)[1] == v]
        X1 = X.copy()
        X1[:, same] = 0
        X0 = X1.copy()
        X1[:, j] = 1
        p1 = 1 / (1 + np.exp(-X1 @ b))
        p0 = 1 / (1 + np.exp(-X0 @ b))
        a = np.mean(p1 - p0)
        J = np.mean((p1 * (1 - p1))[:, None] * X1 - (p0 * (1 - p0))[:, None] * X0, axis=0)
        ame[nm] = a
        ame_se[nm] = float(np.sqrt(J @ V @ J))
    return dict(N=N, events=int(yv.sum()), ybar=100 * yv.mean(), p_model=pmodel, names=names, b=b, V=V,
                ame=ame, ame_se=ame_se, omitted=omitted)


def lgres(P, fit, sec, an, smp, note=""):
    P.add(sec, an, smp, "model", "All", "N; k = events; est = outcome mean (%); p = model Wald test", "model",
          fit["N"], fit["events"], fit["ybar"], nan, nan, fit["p_model"], "", note)
    for t in fit["omitted"]:
        pass

    def tl(t):
        lv, v = re.match(r"^(\d+)\.(.+)$", t).groups()
        return f"{VLAB.get(v, v)}: {lab(v, lv)}"
    for i, t in enumerate(fit["names"]):
        b, se = fit["b"][i], np.sqrt(fit["V"][i, i])
        P.add(sec, an, smp, "covariate", tl(t), t, "OR", fit["N"], nan, np.exp(b), np.exp(b - Z * se),
              np.exp(b + Z * se), 2 * ncdf(-abs(b / se)), "", "")
    for t in fit["names"]:
        b, se = fit["ame"][t], fit["ame_se"][t]
        if se == 0 or np.isnan(se):
            continue
        P.add(sec, an, smp, "covariate", tl(t), t, "AME_pp", fit["N"], nan, 100 * b, 100 * (b - Z * se),
              100 * (b + Z * se), 2 * ncdf(-abs(b / se)), "", "")


# ---------------------------------------------------------------- DCE pieces
XR = ["1.place", "2.place", "3.place", "1.timeflex", "2.timeflex", "1.load", "2.load", "1.retention",
      "2.retention", "0.collaborative"]
XR_ORDER = ["1.place", "2.place", "3.place", "1.timeflex", "2.timeflex", "1.load", "2.load", "1.retention",
            "2.retention", "0.collaborative"]


def add_dummies(d):
    d = d.copy()
    for v, lv in [("place", (1, 2, 3)), ("timeflex", (1, 2)), ("load", (1, 2)), ("retention", (1, 2))]:
        for l in lv:
            d[f"{l}.{v}"] = (d[v] == l).astype(float)
    d["0.collaborative"] = (d["collaborative"] == 0).astype(float)
    return d


def fit_clogit(d, X, tag):
    f = sc.clogit(d, "chosen", X, "choice_set", "id")
    # rank check on the first-differenced design (Stata would omit collinear regressors)
    d2 = d.sort_values("choice_set", kind="mergesort").reset_index(drop=True)
    first = d2.index[d2.choice_set.ne(d2.choice_set.shift())].to_numpy()
    dX = d2[X].to_numpy(float)[first] - d2[X].to_numpy(float)[first + 1]
    rk = np.linalg.matrix_rank(dX)
    if rk < len(X):
        LOG.append(f"clogit {tag}: design rank {rk} < {len(X)} regressors (Stata would omit collinear terms)")
    if np.any(~np.isfinite(f.se)) or np.any(f.se == 0):
        LOG.append(f"clogit {tag}: zero/non-finite SE")
    return f


def dcegrp(P, d, side, smp, spl, grp, note=""):
    dd = d  # already subset
    nr = dd["id"].nunique()
    f = fit_clogit(dd, ["log_salary"] + XR, f"group {spl}/{grp}")
    sec, an = "D", "Employer valuation by group (separate clogit)"
    b, se = f.b[f.idx["log_salary"]], f.se[f.idx["log_salary"]]
    P.add(sec, an, smp, spl, grp, "Log-salary coefficient", "bsal", nr, nan, b, b - 1.96 * se, b + 1.96 * se,
          2 * ncdf(-abs(b / se)), "", note)
    for t, lb in [("2.timeflex", "Compressed 4-day week"), ("1.timeflex", "Staggered hours"),
                  ("1.place", "1-2 days WFH"), ("2.place", "3-4 days WFH"), ("3.place", "Fully remote")]:
        bb, ss = f.b[f.idx[t]], f.se[f.idx[t]]
        pb = 2 * ncdf(-abs(bb / ss))
        e, es, _ = sc.nlcom(f, lambda B, t=t: 100 * sc.invlogit(B[t]))
        P.add(sec, an, smp, spl, grp, lb, "eqpay", nr, nan, e[0], e[0] - 1.96 * es[0], e[0] + 1.96 * es[0], pb, "", note)
        w, ws, _ = sc.nlcom(f, lambda B, t=t: 100 * (np.exp(-B[t] / B["log_salary"]) - 1))
        P.add(sec, an, smp, spl, grp, lb, "wtp", nr, nan, w[0], w[0] - 1.96 * ws[0], w[0] + 1.96 * ws[0],
              2 * ncdf(-abs(w[0] / ws[0])), "", note)


def dcesplit(P, D, gvar, smp, spl, note="", fam="R"):
    d = D[D[gvar].notna()].copy()
    levs = sorted(d[gvar].unique())
    Lc, Ls, Lp, Lo, Lsal = [], [], [], [], []
    for g in levs:
        if g == 0:
            continue
        g = int(g)
        for k in (1, 2, 3):
            d[f"gxp{k}_{g}"] = (d[gvar] == g) * (d["place"] == k) * 1.0
            Lp.append(f"gxp{k}_{g}")
        for k in (1, 2):
            d[f"gxt{k}_{g}"] = (d[gvar] == g) * (d["timeflex"] == k) * 1.0
            d[f"gxl{k}_{g}"] = (d[gvar] == g) * (d["load"] == k) * 1.0
            d[f"gxr{k}_{g}"] = (d[gvar] == g) * (d["retention"] == k) * 1.0
            Ls.append(f"gxt{k}_{g}")
            Lo += [f"gxl{k}_{g}", f"gxr{k}_{g}"]
        Lc.append(f"gxt2_{g}")
    La = Lp + Ls + Lo
    nr = d["id"].nunique()
    sec = "D"
    f = fit_clogit(d, ["log_salary"] + XR + La, f"pooled {spl}")
    an = "Pooled split test (common salary slope)"

    def wt(fit, names):
        for nm in names:
            if np.sqrt(fit.V[fit.idx[nm], fit.idx[nm]]) == 0:
                LOG.append(f"test includes zero-variance term {nm} in {spl}")
        return sc.wald(fit, [{n: 1.0} for n in names])
    for lbl, names, suf in [("Compressed-week interaction(s)", Lc, "cmp"),
                            ("Schedule interactions (staggered, compressed)", Ls, "sch"),
                            ("Location interactions (1-2d, 3-4d, remote)", Lp, "loc"),
                            ("All interactions", La, "all")]:
        chi2, df, p = wt(f, names)
        P.add(sec, an, smp, spl, "All groups", lbl, "wald_p", nr, df, chi2, nan, nan, p, f"{fam}_{suf}", note)
    for g in levs:
        if g == 0:
            continue
        d[f"gxs_{int(g)}"] = (d[gvar] == g) * d["log_salary"]
        Lsal.append(f"gxs_{int(g)}")
    f2 = fit_clogit(d, ["log_salary"] + XR + La + Lsal, f"pooled-F {spl}")
    an = "Pooled split test (group-specific salary slopes)"
    chi2, df, p = wt(f2, Lc)
    P.add(sec, an, smp, spl, "All groups", "Compressed-week interaction(s)", "wald_p", nr, df, chi2, nan, nan, p,
          f"{fam}_cmpF", note)
    chi2, df, p = wt(f2, Lsal)
    P.add(sec, an, smp, spl, "All groups", "Log-salary slope interaction(s)", "wald_p", nr, df, chi2, nan, nan, p,
          f"{fam}_sal", note)
    g0l = lab(gvar, 0)
    for g in levs:
        if g == 0:
            continue
        g = int(g)
        gl = lab(gvar, g)
        est, se, _ = sc.nlcom(f2, lambda B: 100 * (sc.invlogit(B["2.timeflex"] + B[f"gxt2_{g}"]) - sc.invlogit(B["2.timeflex"])))
        P.add(sec, an, smp, spl, f"{gl} minus {g0l}", "Compressed 4-day week", "eqp_diff", nr, nan, est[0],
              est[0] - 1.96 * se[0], est[0] + 1.96 * se[0], 2 * ncdf(-abs(est[0] / se[0])), "",
              "percentage points; delta method")
        est, se, _ = sc.nlcom(f2, lambda B: 100 * (np.exp(-(B["2.timeflex"] + B[f"gxt2_{g}"]) / (B["log_salary"] + B[f"gxs_{g}"]))
                                                   - np.exp(-B["2.timeflex"] / B["log_salary"])))
        P.add(sec, an, smp, spl, f"{gl} minus {g0l}", "Compressed 4-day week", "wtp_diff", nr, nan, est[0],
              est[0] - 1.96 * se[0], est[0] + 1.96 * se[0], 2 * ncdf(-abs(est[0] / se[0])), "", "% of pay; delta method")
    for g in levs:
        dcegrp(P, d[d[gvar] == g], "R", smp, spl, lab(gvar, g), note)


# ---------------------------------------------------------------- sections
def section_A(P, F):
    N = len(F)
    an = "Employers offering a compressed week"
    allm = pd.Series(True, index=F.index)
    for y, itm, note in [("offer_cmp", "Offers (ticked QID15 or typical PME schedule QID61)", "adjusted, as org_fwa.csv"),
                         ("tick_cmp", "Ticked as offered to PMEs (QID15)", ""),
                         ("typ_cmp", "Compressed week is the typical PME schedule (QID61)", ""),
                         ("offer_stag", "Comparator: offers staggered hours (adjusted)", ""),
                         ("offer_rem", "Comparator: offers some remote work (adjusted)", "")]:
        shpost(P, F, y, allm, "A", an, "all", "overall", "All employers", itm, note=note)
    for g in ["size3", "wfh3", "policy", "tech_readiness", "physical_presence", "ag_productivity", "ag_coordination",
              "ag_creativity", "ag_fairness", "ag_talent", "hiredif", "turn_hi", "expand", "offer_stag", "offer_pt",
              "offer_js", "offer_rem", "n_oth", "chal", "pmesh", "foreignhq"]:
        shsplit(P, F, "offer_cmp", g, "A", "Share offering a compressed week, by group", "all", g,
                "Offers a compressed week")
    # industry: label text from indg labels, split name 'industry'
    shsplit(P, F, "offer_cmp", "indg", "A", "Share offering a compressed week, by group", "all", "industry",
            "Offers a compressed week", minn=20, note="industry cells need n>=20; smaller industries pooled")
    S1 = [("size3", 0), ("wfh3", 1), ("policy", 0), ("techfull", 0), ("mostphys", 0)]
    ntxt = "robust SEs; base = <=200 staff, 1-2 days WFH typical, no written policy, not fully ready, some/few roles need presence"
    f = logit_robust(F, "offer_cmp", S1)
    lgres(P, f, "A", "Logit: offers a compressed week (S1)", "all", ntxt)
    f = logit_robust(F, "offer_cmp", S1 + [("indg", 99)])
    lgres(P, f, "A", "Logit: S1 + industry (S2)", "all", "robust SEs; industry base = other industries")
    nturn = int(F["turn_hi"].isna().sum())
    f = logit_robust(F, "offer_cmp", S1 + [(v, 0) for v in ["ag_productivity", "ag_coordination", "ag_creativity",
                                                            "ag_fairness", "ag_talent", "hiredif", "turn_hi"]])
    lgres(P, f, "A", "Logit: S1 + beliefs and business conditions (S3)", "all",
          f"robust SEs; turnover 'not sure' (n={nturn}) dropped")
    f = logit_robust(F, "offer_cmp", S1 + [("offer_stag", 0), ("offer_pt", 0)])
    lgres(P, f, "A", "Logit: S1 + other time/load FWAs offered (S4)", "all", "robust SEs; bundling")


def section_D(P, d, nfirms):
    D = add_dummies(d)
    D["_maxs"] = D.groupby("choice_set")["log_salary"].transform("max")
    D["_cheap"] = (D["log_salary"] < D["_maxs"]).astype(int)
    nsets = D["choice_set"].nunique()
    gl_design = f"Employer DCE ({nsets:,} choice sets)"
    an1 = "Design check: the option with this level is the lower-paid one"
    an2 = "Model-free: share choosing the option with this level"
    for a in ["place", "timeflex", "load"]:
        for k in (1, 2, 3):
            if a != "place" and k == 3:
                continue
            D["_nk"] = D.groupby("choice_set")[a].transform(lambda s: (s == k).sum())
            m = (D[a] == k) & (D["_nk"] == 1)
            nn = int(m.sum())
            kk = int((m & (D._cheap == 1)).sum())
            lb, ub = sc.wilson(kk, nn)
            P.add("D", an1, "all", "design", gl_design, f"{k}.{a}", "share", nn, kk, 100 * kk / nn, lb, ub, nan, "",
                  "n = choice sets where exactly one option has this level")
            for c in (1, 0):
                mm = m & (D._cheap == c)
                nn = int(mm.sum())
                kk = int((mm & (D.chosen == 1)).sum())
                gg = "This option is the lower-paid one" if c == 1 else "This option is the higher-paid one"
                if nn >= 5:
                    lb, ub = sc.wilson(kk, nn)
                    P.add("D", an2, "all", "design", gg, f"{k}.{a}", "share", nn, kk, 100 * kk / nn, lb, ub, nan, "",
                          "n = choice sets; Wilson CI ignores clustering by respondent")
                else:
                    LOG.append(f"design model-free row skipped: {k}.{a} cheap={c} n={nn}")
    D["_nc"] = D.groupby("choice_set")["timeflex"].transform(lambda s: (s == 2).sum())
    for grp, m in [("Benchmark: lower-paid option, sets without a compressed week", (D._cheap == 1) & (D._nc == 0)),
                   ("Benchmark: lower-paid option, all sets", D._cheap == 1)]:
        nn = int(m.sum())
        kk = int((m & (D.chosen == 1)).sum())
        lb, ub = sc.wilson(kk, nn)
        P.add("D", an2, "all", "design", grp, "lower pay", "share", nn, kk, 100 * kk / nn, lb, ub, nan, "",
              "n = choice sets; Wilson CI ignores clustering by respondent")
    dcegrp(P, D, "R", "all", "main", "All employers")
    nturn = int(d.loc[d["turn_hi"].isna(), "id"].nunique())
    for gv, spl, note in [("offer_cmp", "offer_cmp", ""), ("size3", "size3", ""), ("mostphys", "physical", ""),
                          ("concern", "concern", ""), ("ag_creativity", "creative", ""),
                          ("ag_coordination", "coord", ""), ("ag_productivity", "product", ""),
                          ("ag_fairness", "fairness", ""), ("nowfh", "nowfh", ""), ("nopolicy", "nopolicy", ""),
                          ("notready", "notready", ""), ("hiredif", "hiredif", ""),
                          ("turn_hi", "turnover", f"turnover 'not sure' (n={nturn}) dropped"),
                          ("ag_offset", "belief", "")]:
        dcesplit(P, D, gv, "all", spl, note)


def bh(rows):
    fams = ["R_cmp", "R_sch", "R_loc", "R_all", "R_cmpF", "R_sal"]
    for fam in fams:
        idx = [i for i, r in enumerate(rows) if r["family"] == fam and not np.isnan(r["p"])]
        m = len(idx)
        if m == 0:
            continue
        order = sorted(idx, key=lambda i: (rows[i]["p"], i))
        qq = [min(1.0, rows[i]["p"] * m / (r + 1)) for r, i in enumerate(order)]
        for j in range(m - 2, -1, -1):
            qq[j] = min(qq[j], qq[j + 1])
        for i, q in zip(order, qq):
            rows[i]["q"] = q


def fmt(v, dec):
    return "" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.{dec}f}"


def to_line(r):
    f = [r["sec"], r["analysis"][:60], r["sample"], r["split"][:32], r["group"][:80], r["item"][:80], r["metric"],
         fmt(r["n"], 0), fmt(r["k"], 0), fmt(r["est"], 3), fmt(r["lb"], 3), fmt(r["ub"], 3), fmt(r["p"], 4),
         r["family"], fmt(r["q"], 4), r["note"][:244]]
    buf = io.StringIO()
    csv.writer(buf, lineterminator="").writerow(f)
    return buf.getvalue()


def employer_rows(dta_path, appended):
    LOG.clear()
    d = prepare(dta_path, appended)
    nf = d["id"].nunique()
    F = d[(d["task"] == 1) & (d["option"] == 1)].copy()
    assert F["id"].is_unique and len(F) == nf
    P = Post()
    section_A(P, F)
    section_D(P, d, nf)
    secA = [r for r in P.rows if r["sec"] == "A"]
    secD = [r for r in P.rows if r["sec"] == "D"]
    rows = secA + secD
    bh(rows)
    return rows, nf


def run(dta_path, appended, outdir):
    rows, nf = employer_rows(dta_path, appended)
    with open(PROF_CSV, newline="") as fh:
        raw = fh.read().split("\n")
    header, body = raw[0], [l for l in raw[1:] if l != ""]
    emp = [l for l in body if l.split(",", 1)[0] in ("B", "C", "E")]
    # professor's order: blocks B, E, C (positions 0-1299), A, D
    last_emp = max(i for i, l in enumerate(body) if l.split(",", 1)[0] in ("B", "C", "E"))
    out = body[:last_emp + 1] + [to_line(r) for r in rows if r["sec"] == "A"] + [to_line(r) for r in rows if r["sec"] == "D"]
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "compressed_puzzle.csv")
    with open(path, "w", newline="") as fh:
        fh.write(header + "\n" + "\n".join(out) + "\n")
    return path, rows, nf


if __name__ == "__main__":
    pass
