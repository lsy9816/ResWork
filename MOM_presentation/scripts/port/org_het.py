"""org_het -- Python port of deck_aggregates.do section 8b (employer heterogeneity) -> dce_org_het.csv.

run(dta_path, appended, outdir) writes <outdir>/dce_org_het.csv and returns the DataFrame.
"""
import os, sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, '/home/user/ResWork/MOM_presentation/scripts/port')
import stata_core as sc
import employer_data as ed

COLS = ["block", "split", "group_a", "group_b", "item", "label", "n_a", "n_b", "wtp_a", "wtp_b", "diff", "se",
        "stat", "df", "p", "q_all", "q_split", "note"]
XR = ed.XR
ATT = ["p1", "p2", "p3", "s1", "s2", "j1", "j2", "t1", "t2"]
ATT_SRC = {"p1": ("place", 1), "p2": ("place", 2), "p3": ("place", 3), "s1": ("timeflex", 1), "s2": ("timeflex", 2),
           "j1": ("load", 1), "j2": ("load", 2), "t1": ("retention", 1), "t2": ("retention", 2)}
ALAB = {"p1": "1-2 days WFH a week", "p2": "3-4 days WFH a week", "p3": "Fully remote", "s1": "Staggered hours",
        "s2": "Compressed 4-day week", "j1": "Reduced load (4 days/week)", "j2": "Part-time", "t1": "Moderate turnover risk",
        "t2": "High turnover risk"}
GLAB = {
    "physical": {1: "Most PME roles need on-site presence", 2: "Some or few PME roles need presence"},
    "curwfh": {0: "No WFH today (typical 0 days)", 1: "Some WFH today (typical 1+ days)"},
    "concern": {1: "High concern index (mean of 3 items > 3)", 0: "Low concern index (mean <= 3)"},
    "prod": {1: "Agree: WFH lowers productivity (4-5)", 0: "Not agree (1-3)"},
    "coord": {1: "Agree: hybrid creates coordination problems (4-5)", 0: "Not agree (1-3)"},
    "creat": {1: "Agree: creativity suffers apart (4-5)", 0: "Not agree (1-3)"},
    "belief": {1: "Agree: FWAs reduce the salary needed (4-5)", 0: "Not agree (1-3)"},
    "size": {1: "200 or fewer staff", 2: "201-1,000 staff", 3: "1,001+ staff"},
    "tech": {1: "Tech not ready", 2: "Tech partially ready", 3: "Tech fully ready"},
    "role": {1: "Senior executive / owner", 2: "HR director or manager", 3: "Line or hiring manager"},
    "policy": {1: "Written FWA policy", 0: "No written FWA policy"},
}
OBS = float("nan")


def fit_clogit(df, X):
    """clogit with Stata-style omission of collinear terms (later terms dropped). Returns fit expanded to all X
    (omitted: b=0, V=0) plus the list of omitted names."""
    d = df.sort_values("choice_set", kind="mergesort")
    # use differences within sets to detect collinearity
    d2, first, dX, y1 = sc._prep(d, "chosen", X, "choice_set")
    keep = []
    Q = np.zeros((dX.shape[0], 0))
    for j, n in enumerate(X):
        v = dX[:, j].copy()
        nv = np.linalg.norm(v)
        if nv < 1e-12:
            continue
        r = v - Q @ (Q.T @ v) if Q.shape[1] else v
        if np.linalg.norm(r) > 1e-8 * max(1.0, nv):
            Q = np.column_stack([Q, r / np.linalg.norm(r)])
            keep.append(n)
    f = sc.clogit(df, "chosen", keep, "choice_set", "id")
    full = sc.Fit()
    k = len(X)
    full.names = list(X)
    full.idx = {n: i for i, n in enumerate(X)}
    full.b = np.zeros(k)
    full.V = np.zeros((k, k))
    ki = [full.idx[n] for n in keep]
    full.b[ki] = f.b
    full.V[np.ix_(ki, ki)] = f.V
    full.se = np.sqrt(np.diag(full.V))
    full.G, full.N, full.ll = f.G, f.N, f.ll
    full.omitted = [n for n in X if n not in keep]
    return full


def wald_terms(fit, terms):
    """Stata `test t1 t2 ...`: omitted terms are dropped from the test (df reduced)."""
    t = [x for x in terms if x not in fit.omitted]
    if not t:
        return float("nan"), 0, float("nan")
    return sc.wald(fit, [{x: 1.0} for x in t])


def testnl(fit, funcs, h=1e-6):
    """Delta-method Wald test of nonlinear restrictions g(b)=0 (as Stata testnl)."""
    def ev(bb):
        dd = {n: bb[i] for n, i in fit.idx.items()}
        return np.array([f(dd) for f in funcs], float)
    b = fit.b
    g = ev(b)
    J = np.zeros((len(g), len(b)))
    for j in range(len(b)):
        if fit.names[j] in fit.omitted:
            continue
        st = h * max(1.0, abs(b[j]))
        bp, bm = b.copy(), b.copy()
        bp[j] += st
        bm[j] -= st
        J[:, j] = (ev(bp) - ev(bm)) / (2 * st)
    Vg = J @ fit.V @ J.T
    chi2 = float(g @ np.linalg.solve(Vg, g))
    df = len(g)
    return chi2, df, float(stats.chi2.sf(chi2, df))


def fmt(df):
    for c in ("n_a", "n_b", "df"):
        df[c] = df[c].round(0)
    for c in ("wtp_a", "wtp_b", "diff", "se", "stat"):
        df[c] = df[c].round(4)
    for c in ("p", "q_all", "q_split"):
        df[c] = df[c].round(6)
    return df


def run(dta_path, appended, outdir):
    raw = ed.load(dta_path, appended)
    d = ed.dce_frame(raw)
    d = ed.dummies(d)
    d["tagid"] = (~d["id"].duplicated()).astype(int)
    d["log_salary"] = d["log_salary"].astype(float)
    nan = np.nan
    d["physical"] = d["physical_presence"].where(d["physical_presence"] != 3, 2)
    d["curwfh"] = np.where(d["remote"] == 1, 0.0, np.where(d["remote"].isin([2, 3, 4]), 1.0, nan))
    fc = (d["productivity_concern"] + d["coordination_concern"] + d["creativity_concern"]) / 3
    d["fwa_concern"] = fc
    def ind(c): return np.where(c.isna(), nan, (c).astype(float))
    d["concern"] = np.where(fc.isna(), nan, (fc > 3).astype(float))
    for nm, v in (("prod", "productivity_concern"), ("coord", "coordination_concern"), ("creat", "creativity_concern")):
        d[nm] = np.where(d[v].isna(), nan, (d[v] > 3).astype(float))
    d["belief"] = np.where(d["salary_offset"].isna(), nan, d["salary_offset"].isin([4, 5]).astype(float))
    o = d["orgsize"]
    d["size"] = np.where(o.between(0, 200), 1.0, np.where(o.between(201, 1000), 2.0, np.where(o >= 1001, 3.0, nan)))
    d["tech"] = d["tech_readiness"]
    d["policy"] = 2 - d["fwa_policy"]
    d["ind4"] = d["industry"]
    d["grp_physical"] = (d["physical"] == 1).astype(float)
    for nm in ("curwfh", "concern", "prod", "coord", "creat", "belief"):
        d["grp_" + nm] = d[nm]
    d["grp_policy"] = np.where(d["fwa_policy"].isna(), nan, (d["fwa_policy"] == 1).astype(float))
    d["grp_large"] = np.where(o.isna(), nan, (o >= 1001).astype(float))
    d["grp_techfull"] = np.where(d["tech_readiness"].isna(), nan, (d["tech_readiness"] == 3).astype(float))
    inr = d["role"].isin([1, 2, 3])
    d["grp_hr"] = np.where(inr, (d["role"] == 2).astype(float), nan)
    d["grp_exec"] = np.where(inr, (d["role"] == 1).astype(float), nan)

    rows = []
    def post(**k):
        r = {c: (nan if c not in ("block", "split", "group_a", "group_b", "item", "label", "note") else "") for c in COLS}
        r.update(k)
        rows.append(r)

    def orglin(name, ga, gb):
        g = d["grp_" + name]
        s = d[g.notna()].copy()
        names = []
        for a in ATT:
            v, l = ATT_SRC[a]
            s[a + "X"] = (s[v] == l).astype(float) * s["grp_" + name]
            names.append(a + "X")
        # drop rows with missing regressors (Stata)
        X = ["log_salary"] + XR + names
        s = s.dropna(subset=X)
        f = fit_clogit(s, X)
        n1 = int(((s["tagid"] == 1) & (s["grp_" + name] == 1)).sum())
        n0 = int(((s["tagid"] == 1) & (s["grp_" + name] == 0)).sum())
        c, df_, p = wald_terms(f, ["p1X", "p2X", "p3X"])
        post(block="linear_test", split=name, group_a=ga, group_b=gb, item="place",
             label="Location x group interactions = 0 (3 df)", n_a=n1, n_b=n0, stat=c, df=df_, p=p,
             note=f"R14/R15 p-value; common salary slope; clusters = {f.G}")
        c, df_, p = wald_terms(f, names)
        post(block="linear_test", split=name, group_a=ga, group_b=gb, item="all9",
             label="All 9 attribute x group interactions = 0", n_a=n1, n_b=n0, stat=c, df=df_, p=p,
             note="common salary slope")

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

    def orgsplit(var, levels, name, note=""):
        s = d[d[var].isin(levels)].copy()
        rhs = interacted(s, levels, var)
        s = s.dropna(subset=rhs)
        f = fit_clogit(s, rhs)
        n = {l: int(((s[var] == l) & (s["tagid"] == 1)).sum()) for l in levels}
        for l in levels:
            for a in ATT:
                est, se, _ = sc.nlcom(f, lambda B, a=a, l=l: 100 * (np.exp(-B["%s_%d" % (a, l)] / B["ls_%d" % l]) - 1))
                z = est[0] / se[0]
                p = 2 * stats.norm.sf(abs(z))
                post(block="group_wtp", split=name, group_a=GLAB[name][l], item=a, label=ALAB[a], n_a=n[l],
                     wtp_a=est[0], se=se[0], stat=z, p=p,
                     note=f"employer % salary change (negative = discount required), fully interacted model; {note}")
        nl = len(levels)
        def rf(a, l1, l2):
            return lambda B: B[f"{a}_{l1}"] / B[f"ls_{l1}"] - B[f"{a}_{l2}"] / B[f"ls_{l2}"]
        for i in range(nl):
            for j in range(i + 1, nl):
                a1, b1 = levels[i], levels[j]
                c, df_, p = testnl(f, [rf(a, a1, b1) for a in ("p1", "p2", "p3")])
                post(block="ratio_test_place", split=name, group_a=GLAB[name][a1], group_b=GLAB[name][b1], item="place",
                     label="Equal location WTPs (3 ratio restrictions)", n_a=n[a1], n_b=n[b1], stat=c, df=df_, p=p,
                     note="testnl after fully interacted model")
        if nl > 2:
            base = levels[0]
            fs = [rf(a, base, l) for l in levels[1:] for a in ("p1", "p2", "p3")]
            c, df_, p = testnl(f, fs)
            post(block="ratio_test_place", split=name, group_a="all groups", item="place",
                 label="Equal location WTPs across all groups", stat=c, df=df_, p=p,
                 note="testnl after fully interacted model")

    orglin("physical", "Most PME roles need on-site presence", "Some or few PME roles need presence")
    orglin("curwfh", "Some WFH today (typical 1+ days)", "No WFH today (typical 0 days)")
    orglin("concern", "High concern index (mean of 3 items > 3)", "Low concern index (mean <= 3)")
    orglin("prod", "Agree: WFH lowers productivity (4-5)", "Not agree (1-3)")
    orglin("coord", "Agree: hybrid creates coordination problems (4-5)", "Not agree (1-3)")
    orglin("creat", "Agree: creativity suffers apart (4-5)", "Not agree (1-3)")
    orglin("belief", "Agree: FWAs reduce the salary needed (4-5)", "Not agree (1-3)")
    orglin("policy", "Written FWA policy", "No written FWA policy")
    orglin("large", "1,001+ staff (numeric headcount)", "1,000 or fewer staff (numeric headcount)")
    orglin("techfull", "Tech fully ready", "Tech not or partially ready")
    orglin("exec", "Senior executive / owner", "HR or line manager")
    orglin("hr", "HR director or manager", "Senior executive or line manager")
    for i, a in enumerate((1, 2, 3)):
        d["cp%d" % a] = (d["place"] == a).astype(float) * d["fwa_concern"]
    s = d.dropna(subset=["fwa_concern"])
    f = fit_clogit(s, ["log_salary"] + XR + ["cp1", "cp2", "cp3"])
    c, df_, p = wald_terms(f, ["cp1", "cp2", "cp3"])
    post(block="linear_test", split="concern_continuous", item="place",
         label="Location x continuous concern index = 0 (3 df)", stat=c, df=df_, p=p,
         note="R14 overall concern index, continuous")

    orgsplit("physical", [1, 2], "physical", "R14a")
    orgsplit("curwfh", [0, 1], "curwfh", "R14c")
    orgsplit("concern", [0, 1], "concern")
    orgsplit("prod", [0, 1], "prod")
    orgsplit("coord", [0, 1], "coord")
    orgsplit("creat", [0, 1], "creat", "R14b")
    orgsplit("belief", [0, 1], "belief")
    nsz = int(((d["tagid"] == 1) & d["size"].isna()).sum())
    orgsplit("size", [1, 2, 3], "size", f"numeric headcount only; {nsz} firms without a number excluded")
    orgsplit("tech", [1, 2, 3], "tech")
    nother = int(((d["tagid"] == 1) & ~d["role"].isin([1, 2, 3])).sum())
    orgsplit("role", [1, 2, 3], "role", f"Other designation (n={nother}) excluded")
    orgsplit("policy", [0, 1], "policy")

    # industry: the do-file hard-codes the four industry codes 3, 10, 12, 15 (ICT, Finance, Manufacturing, Prof. services)
    inds = [3, 10, 12, 15]
    s = d[d["ind4"].isin(inds)].copy()
    rhs = interacted(s, inds, "ind4")
    s = s.dropna(subset=rhs)
    f = fit_clogit(s, rhs)
    fs = [(lambda B, a=a, l=l: B[f"{a}_3"] / B["ls_3"] - B[f"{a}_{l}"] / B[f"ls_{l}"]) for l in (10, 12, 15) for a in ("p1", "p2", "p3")]
    c, df_, p = testnl(f, fs)
    cells = (s[s["tagid"] == 1]["ind4"].value_counts())
    post(block="ratio_test_place", split="ind4", group_a="all groups", item="place",
         label="Equal location WTPs across the 4 largest industries", stat=c, df=df_, p=p,
         note="R15; industry-level WTPs not reported (cells of %d-%d firms)" % (cells.min(), cells.max()))

    out = fmt(pd.DataFrame(rows, columns=COLS))
    os.makedirs(outdir, exist_ok=True)
    out.to_csv(os.path.join(outdir, "dce_org_het.csv"), index=False)
    run.industry_counts = d[d["tagid"] == 1]["industry"].value_counts()
    return out
