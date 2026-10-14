"""org_channels -- Python port of deck_mech_org.do (mechanisms key: employer_channels) for the employer sample.

Writes mechanisms/employer_channels.csv. The 'pme' rows (employee comparator) are copied from the professor's CSV.
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, "/home/user/ResWork/MOM_presentation/scripts/port")
from stata_core import clogit, nlcom, wald, invlogit, normal_cdf
from employer_data import load, dce_frame, dummies, XR

Z = 1.96   # the do-file writes 1.96*se in this file
COLS = ["block", "split", "channel", "group", "glabel", "n_resp", "item", "label", "est", "lb", "ub", "se", "stat", "df", "p", "q", "note"]
ALAB = {"1.place": "1-2 days WFH", "2.place": "3-4 days WFH", "3.place": "Fully remote", "1.timeflex": "Staggered hours",
        "2.timeflex": "Compressed 4-day week", "1.load": "Reduced load (4 days/week)", "2.load": "Part-time",
        "1.retention": "Moderate turnover risk", "2.retention": "High turnover risk (>20%)"}
NAN = np.nan


def row(block, split, channel, group, glabel, n_resp, item, label, est=NAN, lb=NAN, ub=NAN, se=NAN, stat=NAN, df=NAN, p=NAN, q=NAN, note=""):
    return dict(block=block, split=split, channel=channel, group=group, glabel=str(glabel)[:90], n_resp=n_resp, item=item,
                label=str(label)[:80], est=est, lb=lb, ub=ub, se=se, stat=stat, df=df, p=p, q=q, note=str(note)[:200])


def prep(d):
    d = d.copy()
    d["tagid"] = (d.groupby("id").cumcount() == 0)
    d["mins"] = d.groupby("choice_set")["log_salary"].transform("min")
    d["lo"] = (d["log_salary"] == d["mins"]).astype(float)
    nm = lambda c: d[c].notna()
    g = {}
    def ind(cond, ok):
        return pd.Series(np.where(ok, cond.astype(float), np.nan), index=d.index)
    d["g_physical"] = ind(d["physical_presence"] == 1, nm("physical_presence"))
    d["g_creative"] = ind(d["creativity_concern"] >= 4, nm("creativity_concern"))
    d["g_product"] = ind(d["productivity_concern"] >= 4, nm("productivity_concern"))
    d["g_coord"] = ind(d["coordination_concern"] >= 4, nm("coordination_concern"))
    cm = d[["productivity_concern", "coordination_concern", "creativity_concern"]].mean(axis=1, skipna=True)
    d["g_concern"] = ind(cm > 3, cm.notna())
    d["g_nowfh"] = ind(d["remote"] == 1, nm("remote"))
    d["g_notready"] = ind(d["tech_readiness"] <= 2, nm("tech_readiness"))
    d["g_nopolicy"] = ind(d["fwa_policy"] == 2, nm("fwa_policy"))
    d["g_belief"] = ind(d["salary_offset"] >= 4, nm("salary_offset"))
    large = pd.Series(np.nan, index=d.index)
    large = large.mask(d["orgsize"].notna(), (d["orgsize"] > 1000).astype(float))
    large = large.mask(d["orgsize"].isna() & d["orgsize_cat"].notna(), (d["orgsize_cat"] == 6).astype(float))
    d["g_large"] = large
    sme = pd.Series(np.nan, index=d.index)
    sme = sme.mask(d["orgsize"].notna(), (d["orgsize"] <= 200).astype(float))
    sme = sme.mask(d["orgsize"].isna() & d["orgsize_cat"].notna(), d["orgsize_cat"].isin([1, 2, 3]).astype(float))
    d["g_sme"] = sme
    d["g_hiredif"] = ind(d["hiring_difficulty"].isin([1, 2]), d["hiring_difficulty"].isin([1, 2, 3]))
    d["g_talent"] = ind(d["talent_benefit"] >= 4, nm("talent_benefit"))
    d["g_fair"] = ind(d["fairness_concern"] >= 4, nm("fairness_concern"))
    d["g_turn"] = ind(d["turnover"].isin([2, 3]), d["turnover"].isin([1, 2, 3]))
    d["g_pme50"] = ind(d["pme_share"].isin([3, 4]), nm("pme_share"))
    d["g_hrole"] = d["hiring_role"].where(d["hiring_role"].isin([1, 2, 3]))
    d["g_desig"] = d["role"].where(d["role"].isin([1, 2, 3]))
    d["g_expand"] = ind(d["fwa_plan"].isin([1, 2]), d["fwa_plan"].between(1, 5))
    d["g_familiar"] = ind(d["tgfwar"] == 1, nm("tgfwar"))
    ch = d["fwa_challenge"].copy()
    ch = ch.mask(ch.isin([4, 6, 7]), 4)
    d["g_chal"] = ch
    return d


def interactions(d, g, pre, levels=None, base_first=True, vars_=("place", "timeflex", "load", "retention")):
    """Columns {pre}p1..p3, t1,t2, l1,l2, r1,r2 for indicator/level g (value passed as boolean/0-1 series)."""
    out = {}
    for a in (1, 2, 3):
        out[f"{pre}_p{a}"] = g * (d["place"] == a)
    for a in (1, 2):
        out[f"{pre}_t{a}"] = g * (d["timeflex"] == a)
        out[f"{pre}_l{a}"] = g * (d["load"] == a)
        out[f"{pre}_r{a}"] = g * (d["retention"] == a)
    return pd.DataFrame(out, index=d.index).astype(float)


def fit_check(f, name):
    if f.rank < len(f.b):
        raise RuntimeError(f"rank-deficient design in {name}: rank {f.rank} < {len(f.b)}")
    return f


def runsplit(d, var, name, channel, levels, labels, R, T, tblock="splittest"):
    s = d[d[var].notna()].copy()
    k = len(levels)
    cols, plist = [], []
    nlist, glist = [], []
    for j, l in enumerate(levels):
        n_j = int(((s["tagid"]) & (s[var] == l)).sum())
        nlist.append(n_j); glist.append(labels[j])
        if j >= 1:
            ia = interactions(s, (s[var] == l).astype(float), f"zz{j + 1}")
            for c in ia.columns:
                s[c] = ia[c]
            cols += list(ia.columns); plist += [c for c in ia.columns if "_p" in c]
    # NB: Stata names zz{j}p{a}: place interactions are the zz{j}p* variables
    f = fit_check(clogit(s, "chosen", ["log_salary"] + XR + cols, "choice_set", "id"), name)
    nc = f.G
    chi, df, p = wald(f, [{c: 1} for c in plist])
    T.append(row(tblock, name, channel, k, " | ".join(glist), nc, "place", "Location x group interactions = 0", stat=chi, df=df, p=p,
                 note="n by group = " + "/".join(map(str, nlist)) + "; pooled clogit, common salary slope, cluster id"))
    chi2, df2, p2 = wald(f, [{c: 1} for c in cols])
    T.append(row(tblock, name, channel, k, " | ".join(glist), nc, "all", "All attribute x group interactions = 0", stat=chi2, df=df2, p=p2,
                 note="n by group = " + "/".join(map(str, nlist)) + "; 9 interactions per non-base group"))
    for j, l in enumerate(levels):
        sub = s[s[var] == l]
        fj = fit_check(clogit(sub, "chosen", ["log_salary"] + XR, "choice_set", "id"), f"{name}/{l}")
        nr = fj.G
        for t in ["1.place", "2.place", "3.place", "1.timeflex", "2.timeflex", "1.load", "2.load", "2.retention"]:
            pz = 2 * normal_cdf(-abs(fj.b[fj.idx[t]] / fj.se[fj.idx[t]]))
            e, se, _ = nlcom(fj, lambda b: invlogit(b[t]))
            R.append(row("eqpay", name, channel, l, labels[j], nr, t, ALAB[t], e[0], e[0] - Z * se[0], e[0] + Z * se[0], se[0], p=pz,
                         note="separate clogit; p tests 50%"))
            e, se, _ = nlcom(fj, lambda b: 100 * (1 - np.exp(-b[t] / b["log_salary"])))
            R.append(row("wtp", name, channel, l, labels[j], nr, t, ALAB[t], e[0], e[0] - Z * se[0], e[0] + Z * se[0], se[0], p=pz,
                         note="required salary discount %, separate clogit (indicative)"))


def run(dta, appended, outdir, prof_mech):
    d = prep(dummies(dce_frame(load(dta, appended))))
    R, T = [], []
    # ---- pme comparator (copied)
    prof = pd.read_csv(prof_mech)
    pme = prof[prof.block == "pme"].copy()
    PME = {r["item"]: (r["est"], r["se"]) for _, r in pme.iterrows()}
    for _, r in pme.iterrows():
        R.append({c: r[c] for c in COLS})
    # ---- main
    fm = fit_check(clogit(d, "chosen", ["log_salary"] + XR, "choice_set", "id"), "main")
    for t in ["1.place", "2.place", "3.place", "1.timeflex", "2.timeflex", "1.load", "2.load", "2.retention"]:
        e, s, _ = nlcom(fm, lambda b: invlogit(b[t]))
        R.append(row("main", "main", "", 0, "All employers", fm.G, t, ALAB[t], e[0], e[0] - Z * s[0], e[0] + Z * s[0], s[0],
                     p=2 * normal_cdf(-abs(fm.b[fm.idx[t]] / fm.se[fm.idx[t]])), note="equal-pay share; p tests 50%"))
        e, s, _ = nlcom(fm, lambda b: 100 * (1 - np.exp(-b[t] / b["log_salary"])))
        R.append(row("main_wtp", "main", "", 0, "All employers", fm.G, t, ALAB[t], e[0], e[0] - Z * s[0], e[0] + Z * s[0], s[0],
                     note="required salary discount, % (indicative)"))
    # ---- splits
    S = [("g_physical", "physical", "Role requirements", [0, 1], ["Some or few PME roles need presence", "Most PME roles need presence"]),
         ("g_creative", "creative", "Beliefs: costs", [0, 1], ["Not worried about creativity", "Worried creativity suffers apart"]),
         ("g_product", "product", "Beliefs: costs", [0, 1], ["Not worried about productivity", "Worried WFH lowers productivity"]),
         ("g_coord", "coord", "Beliefs: costs", [0, 1], ["Not worried about coordination", "Worried about coordination"]),
         ("g_concern", "concern", "Beliefs: costs", [0, 1], ["Low overall concern", "High overall concern"]),
         ("g_nowfh", "nowfh", "Practice", [0, 1], ["Some WFH today", "No WFH today"]),
         ("g_notready", "notready", "Business conditions", [0, 1], ["Fully tech-ready", "Not fully tech-ready"]),
         ("g_nopolicy", "nopolicy", "Practice", [0, 1], ["Written FWA policy", "No written FWA policy"]),
         ("g_belief", "belief", "Beliefs: benefits", [0, 1], ["Not agree: FWAs offset salary", "Agree: FWAs offset salary"]),
         ("g_large", "large", "Business conditions", [0, 1], ["Up to 1000 staff", "Over 1000 staff"]),
         ("g_sme", "sme", "Business conditions", [0, 1], ["201+ staff", "Up to 200 staff"]),
         ("g_hiredif", "hiredif", "Business conditions", [0, 1], ["PME hiring not difficult", "Some or significant hiring difficulty"]),
         ("g_talent", "talent", "Beliefs: benefits", [0, 1], ["Not agree: FWAs help attract/retain talent", "Agree: FWAs help attract/retain talent"]),
         ("g_fair", "fair", "Internal equity", [0, 1], ["Not worried about fairness to frontline", "Worried about fairness to frontline"]),
         ("g_turn", "turnover", "Business conditions", [0, 1], ["Low PME turnover (<10%)", "Moderate or high PME turnover (10%+)"]),
         ("g_pme50", "pmeshare", "Role requirements", [0, 1], ["PMEs under half of workforce", "PMEs half or more of workforce"]),
         ("g_hrole", "hrole", "Respondent", [1, 2, 3], ["Executive manpower decisions", "Makes or approves PME hires", "Input only"]),
         ("g_desig", "desig", "Respondent", [1, 2, 3], ["C-suite or owner", "HR director or manager", "Line or hiring manager"]),
         ("g_expand", "plan", "Practice", [0, 1], ["Plan to maintain or reduce FWAs", "Plan to expand FWAs"]),
         ("g_familiar", "familiar", "Information", [0, 1], ["Not familiar with the Guidelines", "Familiar with the Guidelines"])]
    for var, name, ch, lv, lb in S:
        runsplit(d, var, name, ch, lv, lb, R, T)
    runsplit(d, "g_chal", "challenge", "Stated top challenge", [1, 2, 3, 5, 4],
             ["Productivity/quality", "Coordination", "Fairness to non-eligible staff", "Managerial resistance or trust",
              "Infrastructure/security/other"], R, T, tblock="explore")
    # ---- controb
    spec = XR
    for v in ["creativity_concern", "productivity_concern", "coordination_concern", "fairness_concern", "talent_benefit", "salary_offset"]:
        s = d.copy()
        ia = interactions(s, s[v], "zc")
        for c in ia.columns:
            s[c] = ia[c]
        f = fit_check(clogit(s[s[v].notna()], "chosen", ["log_salary"] + spec + list(ia.columns), "choice_set", "id"), v)
        chi, df, p = wald(f, [{"zc_p1": 1}, {"zc_p2": 1}, {"zc_p3": 1}])
        for a in (1, 2, 3):
            lab = {1: "1-2 days WFH", 2: "3-4 days WFH", 3: "Fully remote"}[a]
            c = f"zc_p{a}"
            R.append(row("controb", v, "", 0, "1-5 score, linear", f.G, f"zcp{a}", f"Score x {lab} (per point)", f.b[f.idx[c]],
                         f.b[f.idx[c]] - Z * f.se[f.idx[c]], f.b[f.idx[c]] + Z * f.se[f.idx[c]], f.se[f.idx[c]], chi, df, p,
                         note="coef on score x location; stat/df/p = joint location test"))
    # ---- mutual
    d["g_pc"] = d["g_physical"] * d["g_creative"]
    blocks = {}
    for pre, g in [("P", "g_physical"), ("C", "g_creative"), ("W", "g_nowfh"), ("D", "g_product"), ("F", "g_fair"), ("H", "g_hiredif"), ("PC", "g_pc")]:
        ia = interactions(d, d[g], pre)
        for c in ia.columns:
            d[c] = ia[c]
        blocks[pre] = list(ia.columns)

    def mut(model, blks, desc, sub=None):
        s = d if sub is None else d[sub]
        cols = sum((blocks[b] for b in blks), [])
        f = fit_check(clogit(s[s[cols].notna().all(axis=1)], "chosen", ["log_salary"] + spec + cols, "choice_set", "id"), model)
        for b in blks:
            chi, df, p = wald(f, [{f"{b}_p{a}": 1} for a in (1, 2, 3)])
            ca, da, pa = wald(f, [{c: 1} for c in blocks[b]])
            R.append(row("mutual", model, "", 0, desc, f.G, f"{b}_place", f"{b} x location = 0, given the other blocks", stat=chi, df=df, p=p,
                         note=f"all {b} interactions: chi2={ca:6.2f} df={da} p={pa:6.4f}"))
            for a in (1, 2, 3):
                lab = {1: "1-2 days WFH", 2: "3-4 days WFH", 3: "Fully remote"}[a]
                c = f"{b}_p{a}"
                R.append(row("mutual_b", model, "", 0, desc, f.G, c, f"{b} x {lab} (logit coef)", f.b[f.idx[c]],
                             f.b[f.idx[c]] - Z * f.se[f.idx[c]], f.b[f.idx[c]] + Z * f.se[f.idx[c]], f.se[f.idx[c]],
                             p=2 * normal_cdf(-abs(f.b[f.idx[c]] / f.se[f.idx[c]]))))
        return f
    fPC = mut("PC", ["P", "C"], "Presence + creativity worry")
    mut("PCW", ["P", "C", "W"], "Presence + creativity + no WFH today")
    mut("PCD", ["P", "C", "D"], "Presence + creativity + productivity worry")
    mut("PCFH", ["P", "C", "F", "H"], "Presence + creativity + fairness + hiring difficulty", sub=d["g_hiredif"].notna())
    fsat = mut("PCx", ["PC"], "Presence x creativity (saturated 2x2)") if False else None
    # the do-file's M5 model has P_* C_* PC_* but tests only the PC block
    cols = blocks["P"] + blocks["C"] + blocks["PC"]
    s5 = d[d[cols].notna().all(axis=1)]
    f5 = fit_check(clogit(s5, "chosen", ["log_salary"] + spec + cols, "choice_set", "id"), "PCx")
    for b in ["PC"]:
        chi, df, p = wald(f5, [{f"{b}_p{a}": 1} for a in (1, 2, 3)])
        ca, da, pa = wald(f5, [{c: 1} for c in blocks[b]])
        R.append(row("mutual", "PCx", "", 0, "Presence x creativity (saturated 2x2)", f5.G, f"{b}_place", f"{b} x location = 0, given the other blocks",
                     stat=chi, df=df, p=p, note=f"all {b} interactions: chi2={ca:6.2f} df={da} p={pa:6.4f}"))
        for a in (1, 2, 3):
            lab = {1: "1-2 days WFH", 2: "3-4 days WFH", 3: "Fully remote"}[a]
            c = f"{b}_p{a}"
            R.append(row("mutual_b", "PCx", "", 0, "Presence x creativity (saturated 2x2)", f5.G, c, f"{b} x {lab} (logit coef)", f5.b[f5.idx[c]],
                         f5.b[f5.idx[c]] - Z * f5.se[f5.idx[c]], f5.b[f5.idx[c]] + Z * f5.se[f5.idx[c]], f5.se[f5.idx[c]],
                         p=2 * normal_cdf(-abs(f5.b[f5.idx[c]] / f5.se[f5.idx[c]]))))
    # ---- cells
    firms = d[d["tagid"]]
    NF = len(firms)
    cnt = {}
    for pc in ("00", "10", "01", "11"):
        pp, cc = int(pc[0]), int(pc[1])
        cnt[pc] = int(((firms["g_physical"] == pp) & (firms["g_creative"] == cc)).sum())
        lab = ("Most roles need presence" if pp else "Some/few roles need presence") + "; " + ("worried about creativity" if cc else "not worried about creativity")
        R.append(row("cells", "PxC", "", 0, lab, cnt[pc], f"cell{pc}", "Firm share of cell", est=cnt[pc] / NF, note="2x2 firm composition (P,C)"))
    ok = firms[firms["g_physical"].notna() & firms["g_creative"].notna()]
    tab = pd.crosstab(ok["g_physical"], ok["g_creative"])
    chip = float(stats.chi2_contingency(tab, correction=False)[1])
    cw1 = float(firms.loc[firms["g_physical"] == 1, "g_creative"].mean())
    cw0 = float(firms.loc[firms["g_physical"] == 0, "g_creative"].mean())
    R.append(row("cells", "PxC", "", 0, "Share worried about creativity: most-presence firms", cnt["10"] + cnt["11"], "cw1",
                 "Share worried, most roles need presence", est=cw1, p=chip, note="Pearson chi2 p for P x C"))
    R.append(row("cells", "PxC", "", 0, "Share worried about creativity: other firms", cnt["00"] + cnt["01"], "cw0",
                 "Share worried, some/few roles need presence", est=cw0, p=chip, note="Pearson chi2 p for P x C"))
    s = {k: cnt[k] / NF for k in cnt}
    # ---- decomposition
    KT = {"p1": ("1.place", "p1", "1-2 days WFH"), "p2": ("2.place", "p2", "3-4 days WFH"), "p3": ("3.place", "p3", "Fully remote"),
          "s2": ("2.timeflex", "t2", "Compressed 4-day week")}

    def decomp(blk, note, f):
        for k, (t, ik, lab) in KT.items():
            Q, Qs = PME[k]
            def S(b, name):
                bb, dP, dC = b[t], b[f"P_{ik}"], b[f"C_{ik}"]
                S00, S10, S01, S11 = invlogit(bb), invlogit(bb + dP), invlogit(bb + dC), invlogit(bb + dP + dC)
                Sobs = s["00"] * S00 + s["10"] * S10 + s["01"] * S01 + s["11"] * S11
                SnoC = (s["00"] + s["01"]) * S00 + (s["10"] + s["11"]) * S10
                SnoP = (s["00"] + s["10"]) * S00 + (s["01"] + s["11"]) * S01
                cP = 0.5 * ((SnoP - Sobs) + (S00 - SnoC))
                cC = 0.5 * ((SnoC - Sobs) + (S00 - SnoP))
                return dict(Sobs=Sobs, S00=S00, S10=S10, S01=S01, S11=S11, SnoC=SnoC, SnoP=SnoP, cP=cP, cC=cC)[name]
            SL = {"Sobs": "(i) All firms as observed", "S00": "(ii) Some/few roles need presence; not worried",
                  "S11": "(iii) Most roles need presence; worried", "S10": "Most roles need presence; not worried",
                  "S01": "Some/few roles need presence; worried", "SnoC": "Counterfactual: no firm worried, presence as observed",
                  "SnoP": "Counterfactual: no presence-heavy firm, worry as observed"}
            for sc in ["Sobs", "S00", "S10", "S01", "S11", "SnoC", "SnoP"]:
                e, se, _ = nlcom(f, lambda b: S(b, sc))
                e, se = e[0], se[0]
                R.append(row(blk, k, "", 0, SL[sc], NAN, sc, f"{lab}: employer equal-pay share", e, e - Z * se, e + Z * se, se,
                             p=2 * normal_cdf(-abs((e - 0.5) / se)), note=f"{note}; p tests 50% (delta method)"))
                gs = np.sqrt(se ** 2 + Qs ** 2)
                R.append(row(blk, k, "", 0, SL[sc], NAN, f"gap_{sc}", f"{lab}: PME share minus employer share", Q - e, Q - e - Z * gs, Q - e + Z * gs, gs,
                             p=2 * normal_cdf(-abs((Q - e) / gs)), note=f"{note}; PME share {Q:5.3f}"))
            for cmp_, cl in (("cP", "Component associated with role requirements (presence)"), ("cC", "Component associated with beliefs (creativity worry)")):
                e, se, _ = nlcom(f, lambda b: S(b, cmp_))
                e, se = e[0], se[0]
                R.append(row(blk, k, "", 0, cl, NAN, cmp_, f"{lab}: rise in employer share (pp/100)", e, e - Z * se, e + Z * se, se,
                             p=2 * normal_cdf(-abs(e / se)), note=f"{note}; Shapley average of both orders"))
                est3, _, V3 = nlcom(f, lambda b: [S(b, cmp_) / (Q - S(b, "Sobs")), Q - S(b, "Sobs"), S(b, cmp_)])
                fr, gg, cc = est3
                fs = np.sqrt(V3[0, 0] + (cc / gg ** 2) ** 2 * Qs ** 2)
                R.append(row(blk, k, "", 0, cl, NAN, f"f_{cmp_}", f"{lab}: share of observed PME-employer gap", fr, fr - Z * fs, fr + Z * fs, fs, note=note))
            est3, _, V3 = nlcom(f, lambda b: [(Q - S(b, "S00")) / (Q - S(b, "Sobs")), Q - S(b, "Sobs"), Q - S(b, "S00")])
            fr, gg, rr = est3
            fs = np.sqrt(V3[0, 0] + ((gg - rr) / gg ** 2) ** 2 * Qs ** 2)
            R.append(row(blk, k, "", 0, "Residual: gap remaining in the most favourable cell (ii)", NAN, "f_resid",
                         f"{lab}: share of observed PME-employer gap", fr, fr - Z * fs, fr + Z * fs, fs, note=note))
            for cmp_ in ("cP", "cC"):
                e, se, _ = nlcom(f, lambda b: S(b, cmp_) / (0.5 - S(b, "Sobs")))
                e, se = e[0], se[0]
                R.append(row(blk, k, "", 0, f"{cmp_} as share of employer shortfall below 50%", NAN, f"h_{cmp_}",
                             f"{lab}: share of shortfall below indifference", e, e - Z * se, e + Z * se, se,
                             note=f"{note}; unstable when shortfall is near 0"))
            e, se, _ = nlcom(f, lambda b: (0.5 - S(b, "S00")) / (0.5 - S(b, "Sobs")))
            e, se = e[0], se[0]
            R.append(row(blk, k, "", 0, "Residual share of employer shortfall below 50%", NAN, "h_resid",
                         f"{lab}: share of shortfall below indifference", e, e - Z * se, e + Z * se, se,
                         note=f"{note}; unstable when shortfall is near 0"))
    decomp("decomp", "log salary; additive P + C model (M_PC)", fPC)
    pc_cols = blocks["P"] + blocks["C"]
    frank = fit_check(clogit(d[d[pc_cols].notna().all(axis=1)], "chosen", ["lo"] + spec + pc_cols, "choice_set", "id"), "rank PC")
    decomp("decomp_rank", "rank salary (cheaper dummy); additive P + C", frank)
    for k, (t, ik, lab) in KT.items():
        for sc, desc, expr in (("S00", "(ii) Some/few roles need presence; not worried", lambda b: invlogit(b[t])),
                               ("S11", "(iii) Most roles need presence; worried", lambda b: invlogit(b[t] + b[f"P_{ik}"] + b[f"C_{ik}"] + b[f"PC_{ik}"])),
                               ("S10", "Most roles need presence; not worried", lambda b: invlogit(b[t] + b[f"P_{ik}"])),
                               ("S01", "Some/few roles need presence; worried", lambda b: invlogit(b[t] + b[f"C_{ik}"]))):
            e, se, _ = nlcom(f5, expr)
            nn = {"S00": cnt["00"], "S11": cnt["11"], "S10": cnt["10"], "S01": cnt["01"]}[sc]
            R.append(row("decomp_sat", k, "", 0, desc, nn, sc, f"{lab}: employer equal-pay share", e[0], e[0] - Z * se[0], e[0] + Z * se[0], se[0],
                         note="saturated 2x2"))
    # ---- survey correlates
    R += survey(d)
    # ---- BH
    Tdf = pd.DataFrame(T)
    for it in ("place", "all"):
        m = Tdf[(Tdf["block"] == "splittest") & (Tdf["item"] == it)].sort_values("p", kind="mergesort")
        mm = len(m)
        raw = np.minimum(1, m["p"].to_numpy() * mm / np.arange(1, mm + 1))
        qq = np.minimum.accumulate(raw[::-1])[::-1]
        Tdf.loc[m.index, "q"] = qq
    Tdf = Tdf.sort_values(["item", "p"], kind="mergesort")
    out = pd.concat([Tdf[COLS], pd.DataFrame(R)[COLS]], ignore_index=True)
    return out


def logit_robust(X, y):
    X = np.column_stack([X, np.ones(len(y))])
    b = np.zeros(X.shape[1])
    for _ in range(100):
        p = invlogit(X @ b)
        g = X.T @ (y - p)
        H = (X * (p * (1 - p))[:, None]).T @ X
        step = np.linalg.solve(H, g)
        b = b + step
        if np.max(np.abs(step)) < 1e-12:
            break
    p = invlogit(X @ b)
    H = (X * (p * (1 - p))[:, None]).T @ X
    Hi = np.linalg.inv(H)
    S = X * (y - p)[:, None]
    n = len(y)
    V = (n / (n - 1)) * Hi @ (S.T @ S) @ Hi
    return b, V, X, p


def survey(d):
    f = d[d["tagid"]].copy()
    f["sz_sme"] = f["g_sme"]; f["sz_large"] = f["g_large"]
    f["d_exec"] = (f["role"] == 1).astype(float); f["d_hr"] = (f["role"] == 2).astype(float)
    f["techfull"] = (f["tech_readiness"] == 3).astype(float); f["policy"] = (f["fwa_policy"] == 1).astype(float)
    rows = []

    def svpost(model, dv, xs, desc):
        s = f[f[[dv] + xs].notna().all(axis=1)]
        y = s[dv].to_numpy(float)
        b, V, X, p = logit_robust(s[xs].to_numpy(float), y)
        nobs = len(s)
        base = y.mean()
        se = np.sqrt(np.diag(V))
        for i, x in enumerate(xs):
            rows.append(row("survey", model, "", 0, desc, nobs, f"OR_{x}", f"Odds ratio: {x}", np.exp(b[i]), np.exp(b[i] - Z * se[i]),
                            np.exp(b[i] + Z * se[i]), se[i], p=2 * normal_cdf(-abs(b[i] / se[i])), note=f"logit, robust SE; DV mean {base:5.3f}"))
        w = p * (1 - p)
        ame = np.array([np.mean(b[i] * w) for i in range(len(xs))])
        Jm = np.zeros((len(xs), len(b)))
        for i in range(len(xs)):
            for j in range(len(b)):
                Jm[i, j] = np.mean((1.0 if i == j else 0.0) * w + b[i] * w * (1 - 2 * p) * X[:, j])
        Va = Jm @ V @ Jm.T
        sa = np.sqrt(np.diag(Va))
        for i, x in enumerate(xs):
            rows.append(row("survey", model, "", 0, desc, nobs, f"AME_{x}", f"AME (pp/100): {x}", ame[i], ame[i] - Z * sa[i], ame[i] + Z * sa[i], sa[i],
                            p=2 * normal_cdf(-abs(ame[i] / sa[i])), note="average marginal effect, delta method"))
    svpost("S1", "g_creative", "g_physical g_nowfh sz_sme sz_large policy techfull g_pme50 d_exec d_hr".split(),
           "DV: worried creativity suffers apart (4-5)")
    for a, b_ in [("creativity_concern", "productivity_concern"), ("creativity_concern", "coordination_concern"),
                  ("productivity_concern", "coordination_concern"), ("creativity_concern", "fairness_concern"),
                  ("creativity_concern", "talent_benefit")]:
        s = f[[a, b_]].dropna()
        rho = stats.spearmanr(s[a], s[b_])[0]
        n = len(s)
        t = rho * np.sqrt((n - 2) / (1 - rho ** 2))
        pv = 2 * stats.t.sf(abs(t), n - 2)
        rows.append(row("survey", "S2", "", 0, "Spearman rho", n, "rho", f"{a} x {b_}", est=rho, p=pv, note="1-5 items"))
    svpost("S3", "g_expand", "g_hiredif g_turn g_talent g_fair g_creative g_physical g_nowfh policy g_familiar sz_sme sz_large".split(),
           "DV: plans to expand PME FWAs (excl. don't know; n/a and not-sure categories excluded)")
    ok = f[f["g_physical"].notna() & f["g_nowfh"].notna()]
    chip = float(stats.chi2_contingency(pd.crosstab(ok["g_physical"], ok["g_nowfh"]), correction=False)[1])
    for grp, lab in ((1, "Most roles need presence"), (0, "Some or few roles need presence")):
        sub = f[f["g_physical"] == grp]["g_nowfh"].dropna()
        rows.append(row("survey", "S4", "", grp, lab, len(sub), "nowfh", "Share with no WFH today", est=float(sub.mean()), p=chip,
                        note="Pearson chi2 p, P x no-WFH"))
    return rows


if __name__ == "__main__":
    SP = "/tmp/claude-0/-home-user-ResWork/ddc3d860-5d1b-54ab-bc5b-0b5766ecc715/scratchpad/dl"
    which = sys.argv[1] if len(sys.argv) > 1 else "val"
    if which == "val":
        out = run(f"{SP}/src/employer.dta", False, None, f"{SP}/ds/mechanisms/employer_channels.csv")
        out.to_csv(f"{SP}/val/employer_channels_303.csv", index=False)
    else:
        out = run(f"{SP}/appended.dta", True, None, f"{SP}/ds/mechanisms/employer_channels.csv")
        import pathlib
        pathlib.Path("/home/user/ResWork/MOM_presentation/mechanisms").mkdir(exist_ok=True)
        out.to_csv("/home/user/ResWork/MOM_presentation/mechanisms/employer_channels.csv", index=False, float_format="%.6f")
    print(out.shape)
