"""Port of deck_aggregates.do section 2 (EMPLOYER SURVEY): org_composition.csv, org_fwa.csv, org_attitudes.csv."""
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stata_core import wilson as _wilson  # noqa: E402

MINCELL = 5
COLS = ["block", "sample", "group", "item", "qid", "n", "k", "share", "lb", "ub", "value", "note"]

LABELS = {
    "likert": {1: "1 Strongly disagree", 2: "2", 3: "3 Neither agree nor disagree", 4: "4", 5: "5 Strongly agree"},
    "size6": {1: "Fewer than 10", 2: "10-50", 3: "51-200", 4: "201-500", 5: "501-1,000", 6: "1,001 or more"},
    "size3": {1: "200 or fewer", 2: "201-1,000", 3: "1,001 or more"},
    "sg_status": {1: "Headquartered in Singapore", 4: "Foreign/regional HQ with Singapore operations"},
    "hiring_role": {1: "Makes executive decisions on manpower planning", 2: "Makes or approves PME hiring decisions",
                    3: "Provides input into PME hiring, no final decision"},
    "role": {1: "Senior executive (owner, CEO or C-suite)", 2: "HR director or HR manager",
             3: "Manager with hiring responsibilities (line or hiring manager)", 4: "Other"},
    "industry": {1: "Accommodation", 3: "Information and communications", 4: "Administrative and support services",
                 6: "Arts, entertainment and recreation", 7: "Construction",
                 9: "Other community, social and personal services", 10: "Financial and insurance services",
                 11: "Health and social services", 12: "Manufacturing", 13: "Retail trade", 15: "Professional services",
                 16: "Public administration and education", 18: "Real estate services", 20: "Transportation and storage",
                 22: "Wholesale trade", 23: "Other", 24: "Food and beverage services"},
    "pme_share": {1: "Less than 25%", 2: "25%-49%", 3: "50%-74%", 4: "75% or more"},
    "role_level": {1: "Individual contributor", 2: "Team lead / supervisor", 3: "Middle management",
                   4: "Senior management or above"},
    "role_function": {1: "Finance / accounting / procurement", 2: "HR / administration", 3: "Sales / business development",
                      4: "Marketing / communications", 5: "IT / digital", 6: "R&D / engineering",
                      7: "Operations / supply chain / logistics", 8: "Strategy / corporate planning / governance",
                      9: "General management", 10: "Legal / compliance", 11: "Other"},
    "turnover": {1: "Low (<10% left voluntarily)", 2: "Moderate (10%-20%)", 3: "High (>20%)", 4: "Not sure"},
    "culture": {1: "Hierarchical", 2: "Collaborative", 3: "Autonomous / results-oriented",
                4: "Mixed / difficult to characterise"},
    "remote": {1: "0 days (fully onsite)", 2: "1-2 days a week", 3: "3-4 days a week", 4: "5 days (remote-first)"},
    "schedule": {1: "Fixed hours", 2: "Staggered hours", 3: "Compressed workweek"},
    "workload": {1: "Full-time only", 2: "Job sharing available", 3: "Part-time available"},
    "tgfwar": {1: "Aware and familiar", 2: "Heard of, not familiar with details", 3: "Not aware"},
    "fwa_request": {1: "Yes, received formal requests", 2: "No", 3: "Don't know / not sure"},
    "fwa_approval": {1: "All or nearly all (90-100%)", 2: "Most (60-89%)", 3: "About half (40-59%)", 4: "Some (10-39%)",
                     5: "Few or none (0-9%)", 6: "Don't know the approval rate"},
    "fwa_plan": {1: "Expand significantly", 2: "Expand somewhat", 3: "Maintain current offerings",
                 4: "Reduce somewhat", 5: "Reduce significantly", 6: "Don't know / not sure"},
    "physical_presence": {1: "Most roles require physical presence",
                          2: "Some roles require presence; others can be remote",
                          3: "Few or no roles require physical presence"},
    "tech_readiness": {1: "Not ready", 2: "Partially ready (significant gaps)", 3: "Fully ready"},
    "hiring_difficulty": {1: "Yes, significant difficulty", 2: "Yes, some difficulty",
                          3: "No, not particularly difficult", 4: "Not applicable (no PME vacancies)"},
    "fwa_challenge": {1: "Maintaining productivity and output quality", 2: "Coordination and communication across teams",
                      3: "Fairness concerns (not all roles can be flexible)", 4: "Lack of digital infrastructure",
                      5: "Managerial resistance or lack of trust", 6: "Security, confidentiality or compliance",
                      7: "Other"},
}
LIKERTS = ["productivity_concern", "coordination_concern", "creativity_concern", "fairness_concern", "talent_benefit",
           "salary_offset"]
for _v in LIKERTS:
    LABELS[_v] = LABELS["likert"]

NEEDED = ["id", "task", "option", "sg_status", "hiring_role", "role", "industry", "orgsize_resp", "orgsize", "orgsize_cat",
          "pme_share", "fwa_adhoc", "fwa_schedremote", "fwa_fullremote", "fwa_staggered", "fwa_compressed",
          "fwa_parttime", "fwa_jobshare", "fwa_homework", "fwa_other", "fwa_none", "fwa_any", "remote", "schedule",
          "workload", "culture", "turnover", "salary_resp", "salary", "base_salary", "role_level", "role_function",
          "fwa_policy", "tgfwar", "fwa_request", "fwa_approval", "fwa_plan", "physical_presence", "tech_readiness",
          "productivity_concern", "coordination_concern", "creativity_concern", "fairness_concern", "talent_benefit",
          "salary_offset", "hiring_difficulty", "fwa_challenge"]


def _p50(x):
    """Stata summarize, detail: p50 (average of two middle obs when n*p/100 is an integer)."""
    x = np.sort(np.asarray(x, float))
    n = len(x)
    f = n * 50 / 100
    i = int(math.floor(f + 1e-9))
    if abs(f - i) < 1e-9:
        return (x[i - 1] + x[i]) / 2
    return x[int(math.ceil(f)) - 1]


class Poster:
    def __init__(self):
        self.rows = []

    def spost(self, blk, smp, grp, itm, qid="", nn=None, kk=None, val=None, note=""):
        n = np.nan if nn is None else nn
        k = np.nan if kk is None else kk
        v = np.nan if val is None else val
        sh = lb = ub = np.nan
        if not np.isnan(n) and n < MINCELL:
            k = np.nan
            v = np.nan
            note = ("suppressed: base n<%d. %s" % (MINCELL, note)).strip()
        elif not np.isnan(n) and not np.isnan(k) and n > 0:
            sh = 100 * k / n
            lb, ub = _wilson(k, n)
        self.rows.append([blk, smp, grp, itm, qid, n, k, sh, lb, ub, v, note])

    def ctab(self, s, mask, blk, grp, qid, levels, note=""):
        x = s[mask & s.notna()]
        n = len(x)
        for l in levels:
            self.spost(blk, "all", grp, LABELS[s.name][l], qid, n, int((x == l).sum()), note=note)

    def bpost(self, s, mask, blk, grp, itm, qid, note=""):
        x = s[mask & s.notna()]
        self.spost(blk, "all", grp, itm, qid, len(x), int((x == 1).sum()), note=note)

    def mpost(self, s, mask, blk, grp, itm, qid, stat="mean", note=""):
        x = s[mask & s.notna()]
        n = len(x)
        v = np.nan
        if n > 0:
            v = x.mean() if stat == "mean" else _p50(x)
        self.spost(blk, "all", grp, itm, qid, n, None, None if np.isnan(v) else v, note)

    def frame(self):
        return pd.DataFrame(self.rows, columns=COLS)


def _fmt(df):
    out = df.copy()
    out["n"] = out["n"].map(lambda v: "" if pd.isna(v) else "%d" % v)
    out["k"] = out["k"].map(lambda v: "" if pd.isna(v) else "%d" % v)
    for c in ("share", "lb", "ub"):
        out[c] = out[c].map(lambda v: "" if pd.isna(v) else "%.4f" % v)
    out["value"] = out["value"].map(lambda v: "" if pd.isna(v) else "%.4f" % v)
    return out


def prepare(dta_path, appended, id_col=None):
    raw = pd.read_stata(dta_path, convert_categoricals=False)
    if id_col is None:
        id_col = "id_new" if appended else "id"
    d = raw[[c for c in NEEDED if c != "id"]].copy()
    d["id"] = raw[id_col]
    d = d[(d["task"] == 1) & (d["option"] == 1)].drop(columns=["task", "option"]).reset_index(drop=True)
    assert d["id"].is_unique
    for c in d.columns:
        if str(d[c].dtype) in ("string", "str", "object"):
            continue
        d[c] = pd.to_numeric(d[c], errors="coerce")

    os_ = d["orgsize"]
    s6 = pd.Series(np.nan, index=d.index)
    s6[(os_ >= 0) & (os_ < 10)] = 1
    s6[(os_ >= 10) & (os_ <= 50)] = 2
    s6[(os_ >= 51) & (os_ <= 200)] = 3
    s6[(os_ >= 201) & (os_ <= 500)] = 4
    s6[(os_ >= 501) & (os_ <= 1000)] = 5
    s6[os_ >= 1001] = 6
    oc = d["orgsize_cat"]
    fill = s6.isna() & (oc >= 1) & (oc <= 6)
    s6[fill] = oc[fill]
    d["size6"] = s6
    d["size3"] = np.where(s6.isna(), np.nan, np.where(s6 <= 3, 1, np.where(s6.isin([4, 5]), 2, 3)))
    d["size_le50"] = np.where(s6.isna(), np.nan, (s6 <= 2).astype(float))

    def ind(cond, src=None):
        r = cond.astype(float)
        if src is not None:
            r[src.isna()] = np.nan
        return r

    one = lambda c: d[c] == 1  # noqa: E731
    d["offered_remote"] = (one("fwa_adhoc") | one("fwa_schedremote") | one("fwa_fullremote")).astype(float)
    d["typical_remote"] = d["remote"].isin([2, 3, 4]).astype(float)
    d["oadj_remote"] = ((d["offered_remote"] == 1) | (d["typical_remote"] == 1)).astype(float)
    d["oadj_staggered"] = (one("fwa_staggered") | (d["schedule"] == 2)).astype(float)
    d["oadj_compressed"] = (one("fwa_compressed") | (d["schedule"] == 3)).astype(float)
    d["oadj_jobshare"] = (one("fwa_jobshare") | (d["workload"] == 2)).astype(float)
    d["oadj_parttime"] = (one("fwa_parttime") | (d["workload"] == 3)).astype(float)
    d["policy"] = ind(d["fwa_policy"] == 1, d["fwa_policy"])
    d["aware"] = ind(d["tgfwar"].isin([1, 2]), d["tgfwar"])
    d["familiar"] = ind(d["tgfwar"] == 1, d["tgfwar"])
    d["received"] = ind(d["fwa_request"] == 1, d["fwa_request"])
    d["expand"] = ind(d["fwa_plan"].isin([1, 2]), d["fwa_plan"])
    d["reduce"] = ind(d["fwa_plan"].isin([4, 5]), d["fwa_plan"])
    d["hiredif"] = ind(d["hiring_difficulty"].isin([1, 2]), d["hiring_difficulty"])
    d["techfull"] = ind(d["tech_readiness"] == 3, d["tech_readiness"])
    d["mostphys"] = ind(d["physical_presence"] == 1, d["physical_presence"])
    for v in LIKERTS:
        d["ag_" + v] = ind(d[v].isin([4, 5]), d[v])
    d["anyconcern"] = ((d["ag_productivity_concern"] == 1) | (d["ag_coordination_concern"] == 1)
                       | (d["ag_creativity_concern"] == 1)).astype(float)
    ap = pd.Series(np.nan, index=d.index)
    for lv, val in {1: 0.95, 2: 0.745, 3: 0.495, 4: 0.245, 5: 0.045}.items():
        ap[d["fwa_approval"] == lv] = val
    d["apprate"] = 100 * ap
    return d


def build(d):
    """Return the three DataFrames (org_composition, org_fwa, org_attitudes)."""
    N = len(d)
    T = pd.Series(True, index=d.index)
    G = "All employer respondents"
    S = lambda c: d[c].rename(c)  # noqa: E731

    # ---- 2.1 composition
    P = Poster()
    P.ctab(S("size6"), T, "firm_size", G, "QID9/QID11", range(1, 7), "S3; numeric headcount or band for 17 unsure")
    P.ctab(S("size3"), T, "firm_size3", G, "QID9/QID11", range(1, 4), "S3")
    P.bpost(S("size_le50"), T, "firm_size3", G, "50 or fewer", "QID9/QID11", "S3")
    P.mpost(S("orgsize"), T, "firm_size_numeric", "Firms giving a numeric headcount", "Median headcount", "QID9", "p50")
    P.ctab(S("role"), T, "designation", G, "QID7", range(1, 5), "S2")
    P.ctab(S("hiring_role"), T, "hiring_involvement", G, "QID5", range(1, 4))
    P.ctab(S("sg_status"), T, "hq_status", G, "QID4", [1, 4])
    P.ctab(S("industry"), T, "industry", G, "QID8", [1, 3, 4, 6, 7, 9, 10, 11, 12, 13, 15, 16, 18, 20, 22, 23, 24],
           "composition only; industry-level DCE estimates are not reportable")
    P.ctab(S("pme_share"), T, "pme_share", G, "QID12", range(1, 5))
    P.ctab(S("role_level"), T, "role_in_mind_level", G, "QID32", range(1, 5))
    P.ctab(S("role_function"), T, "role_in_mind_function", G, "QID33", range(1, 12))
    P.ctab(S("turnover"), T, "pme_turnover", G, "QID19", range(1, 5))
    P.ctab(S("culture"), T, "culture", G, "QID18", range(1, 5))
    P.mpost(S("salary"), d["salary_resp"] == 7, "salary_anchor", "Firms giving an exact salary",
            "Median monthly salary of most recent PME hire (SGD)", "QID63", "p50")
    P.mpost(S("base_salary"), T, "salary_anchor", G, "Median DCE reference salary (SGD)", "QID63/QID64", "p50")
    comp = P.frame()

    # ---- 2.2 fwa
    P = Poster()
    ot = "offered_ticked"
    P.bpost(S("offered_remote"), T, ot, G, "Remote work (ad hoc, scheduled or remote-first)", "QID15")
    P.bpost(S("fwa_staggered"), T, ot, G, "Staggered hours", "QID15")
    P.bpost(S("fwa_compressed"), T, ot, G, "Compressed workweek", "QID15")
    P.bpost(S("fwa_jobshare"), T, ot, G, "Job sharing", "QID15")
    P.bpost(S("fwa_parttime"), T, ot, G, "Part-time / reduced hours", "QID15")
    P.bpost(S("fwa_homework"), T, ot, G, "Home-working (physical work)", "QID15")
    P.bpost(S("fwa_none"), T, ot, G, "None of the above", "QID15")
    oa = "offered_adjusted"
    P.bpost(S("oadj_remote"), T, oa, G, "Remote work", "QID15+QID16", "ticked OR typical practice; RA slide definition")
    P.bpost(S("oadj_staggered"), T, oa, G, "Staggered hours", "QID15+QID61")
    P.bpost(S("oadj_compressed"), T, oa, G, "Compressed workweek", "QID15+QID61")
    P.bpost(S("oadj_jobshare"), T, oa, G, "Job sharing", "QID15+QID17")
    P.bpost(S("oadj_parttime"), T, oa, G, "Part-time / reduced hours", "QID15+QID17")
    P.ctab(S("remote"), T, "typical_wfh_days", G, "QID16", range(1, 5), "D3; modal PME practice, not use")
    P.ctab(S("schedule"), T, "typical_schedule", G, "QID61", range(1, 4))
    P.ctab(S("workload"), T, "typical_workload", G, "QID17", range(1, 4), "single choice")
    P.bpost(S("policy"), T, "written_policy", G, "Has a formal written FWA policy", "QID21", "D4")
    for z in (1, 2, 3):
        P.bpost(S("policy"), d["size3"] == z, "written_policy_by_size", "Firm size: " + LABELS["size3"][z],
                "Has a formal written FWA policy", "QID21", "D4")
    ok = d["size3"].notna() & d["policy"].notna()
    tab = pd.crosstab(d.loc[ok, "size3"], d.loc[ok, "policy"])
    chi, chip = stats.chi2_contingency(tab.values, correction=False)[:2]
    P.spost("written_policy_by_size", "all", "Size x policy", "Pearson chi2 p-value", "QID21 x QID9/11", N, None, chip,
            "D4; Pearson chi2(2) = %5.2f" % chi)
    P.ctab(S("tgfwar"), T, "awareness", G, "QID23", range(1, 4), "D6")
    P.bpost(S("aware"), T, "awareness", G, "Aware (familiar or heard of)", "QID23", "D6")
    for z in (1, 2, 3):
        P.bpost(S("familiar"), d["size3"] == z, "awareness_by_size", "Firm size: " + LABELS["size3"][z],
                "Aware and familiar", "QID23")
    aware1, rec1, pol1 = d["aware"] == 1, d["received"] == 1, d["policy"] == 1
    P.ctab(S("fwa_request"), aware1, "requests_received", "Firms aware of TG-FWAR", "QID24", range(1, 4))
    P.ctab(S("fwa_approval"), rec1, "approval", "Firms that received formal requests", "QID25", range(1, 7), "D8")
    P.mpost(S("apprate"), rec1, "approval", "Firms that received formal requests",
            "Mean approval share (midpoint-imputed, %)", "QID25",
            note="INFERENCE: category midpoints 95/74.5/49.5/24.5/4.5; excludes don't know")
    P.bpost(S("received"), aware1 & pol1, "requests_by_policy", "Aware firms with a written policy",
            "Received formal requests", "QID24 x QID21", "D10")
    P.bpost(S("received"), aware1 & (d["policy"] == 0), "requests_by_policy", "Aware firms without a written policy",
            "Received formal requests", "QID24 x QID21", "D10")
    P.bpost(S("received"), d["tgfwar"] == 1, "requests_by_familiarity", "Familiar firms", "Received formal requests",
            "QID24 x QID23")
    P.bpost(S("received"), d["tgfwar"] == 2, "requests_by_familiarity", "Heard-of-only firms",
            "Received formal requests", "QID24 x QID23")
    P.ctab(S("fwa_approval"), rec1 & pol1, "approval_by_policy", "Received requests; written policy", "QID25 x QID21",
           range(1, 7))
    P.ctab(S("fwa_approval"), rec1 & (d["policy"] == 0), "approval_by_policy", "Received requests; no written policy",
           "QID25 x QID21", range(1, 7))
    fwa = P.frame()

    # ---- 2.3 attitudes
    Q = {"productivity_concern": "I worry that employees are less productive when working from home",
         "coordination_concern": "Hybrid work creates coordination and communication problems",
         "creativity_concern": "Creativity and innovation suffer when people are not physically together",
         "fairness_concern": "It is unfair to offer FWAs to PMEs when frontline staff cannot have them",
         "talent_benefit": "FWAs help us attract and retain talent in a competitive market",
         "salary_offset": "Offering FWAs reduces the salary we need to offer to attract and retain PME talent"}
    I = {v: "QID22_%d" % (i + 1) for i, v in enumerate(LIKERTS)}  # noqa: E741
    P = Poster()
    for v in LIKERTS:
        P.ctab(S(v), T, "statement_distribution", Q[v], I[v], range(1, 6))
        P.bpost(S("ag_" + v), T, "statement_agree", G, Q[v], I[v], "B2; agree = 4-5 on 1-5")
        P.mpost(S(v), T, "statement_mean", G, Q[v], I[v], note="mean on 1-5")
    P.bpost(S("anyconcern"), T, "statement_agree", G,
            "Agree with at least one of the productivity/coordination/creativity statements", "QID22_1-3", "B2")
    P.ctab(S("fwa_challenge"), T, "biggest_challenge", G, "QID50", range(1, 8), "B1")
    for z in (1, 2, 3):
        P.ctab(S("fwa_challenge"), d["size3"] == z, "biggest_challenge_by_size", "Firm size: " + LABELS["size3"][z],
               "QID50", range(1, 8), "B1")
    P.ctab(S("fwa_plan"), T, "plan_12m", G, "QID26", range(1, 7), "B3")
    P.bpost(S("expand"), T, "plan_12m", G, "Expand (significantly or somewhat)", "QID26", "B3")
    P.bpost(S("reduce"), T, "plan_12m", G, "Reduce (somewhat or significantly)", "QID26", "B3")
    P.bpost(S("expand"), pol1, "plan_12m_by_policy", "Written FWA policy", "Expand (significantly or somewhat)",
            "QID26 x QID21")
    P.bpost(S("expand"), d["policy"] == 0, "plan_12m_by_policy", "No written FWA policy",
            "Expand (significantly or somewhat)", "QID26 x QID21")
    P.ctab(S("hiring_difficulty"), T, "hiring_difficulty", G, "QID49", range(1, 5), "B3")
    P.bpost(S("hiredif"), T, "hiring_difficulty", G, "Any difficulty (significant or some)", "QID49", "B3")
    P.ctab(S("tech_readiness"), T, "tech_readiness", G, "QID28", range(1, 4), "B4")
    for z in (1, 2, 3):
        P.bpost(S("techfull"), d["size3"] == z, "tech_readiness_by_size", "Firm size: " + LABELS["size3"][z],
                "Fully ready", "QID28")
    P.ctab(S("physical_presence"), T, "physical_presence", G, "QID27", range(1, 4), "R14a split variable")
    att = P.frame()
    return comp, fwa, att


def run(dta_path, appended, outdir, expected_firms=None, id_col=None):
    d = prepare(dta_path, appended, id_col)
    if expected_firms is not None:
        assert len(d) == expected_firms, (len(d), expected_firms)
    frames = build(d)
    os.makedirs(outdir, exist_ok=True)
    for name, f in zip(("org_composition.csv", "org_fwa.csv", "org_attitudes.csv"), frames):
        _fmt(f).to_csv(os.path.join(outdir, name), index=False, lineterminator="\n")
    return frames


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2] == "1", sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else None)
