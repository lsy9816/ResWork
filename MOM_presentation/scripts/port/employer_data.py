"""Load the employer choice data as the do-files do: employer.dta (303 firms) or snef_employer_appended.dta (397)."""
import numpy as np
import pandas as pd

COLS = ["id", "task", "option", "chosen", "choice_set", "offer_salary", "salary_ratio", "log_salary", "place",
        "timeflex", "load", "retention", "jobculture", "collaborative", "design_block", "same_side", "salary_out",
        "physical_presence", "remote", "productivity_concern", "coordination_concern", "creativity_concern",
        "fairness_concern", "talent_benefit", "salary_offset", "hiring_difficulty", "turnover", "pme_share",
        "hiring_role", "role", "fwa_plan", "tgfwar", "tech_readiness", "fwa_policy", "orgsize", "orgsize_cat",
        "fwa_challenge", "industry", "sg_status", "orgsize_resp", "fwa_adhoc", "fwa_schedremote", "fwa_fullremote",
        "fwa_staggered", "fwa_compressed", "fwa_parttime", "fwa_jobshare", "fwa_homework", "fwa_other", "fwa_none",
        "fwa_any", "schedule", "workload", "culture", "salary_resp", "salary", "base_salary", "role_level",
        "role_function", "fwa_request", "fwa_approval", "vendor"]


def load(path, appended):
    raw = pd.read_stata(path, convert_categoricals=False)
    cols = [c for c in COLS if c in raw.columns] + (["id_new", "choice_set_new", "source"] if appended else [])
    d = raw[cols].copy()
    if appended:
        d["id"] = d["id_new"].astype(int)
        d["choice_set"] = d["choice_set_new"].astype(int)
    for c in ("design_block", "salary_out"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["collaborative"] = np.where(d["jobculture"].notna(), (d["jobculture"] == 2).astype(float), np.nan)
    return d.reset_index(drop=True)


def dce_frame(d):
    """Derived choice-level variables of deck_aggregates.do section 4."""
    d = d.copy()
    d["left"] = (d["option"] == 1).astype(float)
    d["ss"] = d.groupby("id")["same_side"].transform("max")
    g = d.groupby("choice_set")
    d["smax"] = g["offer_salary"].transform("max")
    d["smin"] = g["offer_salary"].transform("min")
    d["rmax"] = g["salary_ratio"].transform("max")
    d["rmin"] = g["salary_ratio"].transform("min")
    assert (d["smax"] > d["smin"]).all()
    d["hi"] = (d["offer_salary"] == d["smax"]).astype(float)
    d["lo"] = (d["offer_salary"] == d["smin"]).astype(float)
    d["lgap"] = np.log(d["smax"] / d["smin"])
    d["lgap_design"] = np.log(d["rmax"] / d["rmin"])
    d["gkey"] = np.round(1000 * d["lgap_design"]).astype(int)
    d["mins"] = g["log_salary"].transform("min")
    return d


def dummies(d, spec="R"):
    """Indicator columns named like Stata factor terms: '1.place' ... ; base levels dropped."""
    out = d.copy()
    for v, lv in [("place", (1, 2, 3)), ("timeflex", (1, 2)), ("load", (1, 2)), ("retention", (1, 2))]:
        for l in lv:
            out[f"{l}.{v}"] = (out[v] == l).astype(float)
    out["1.collaborative_base"] = np.nan
    # ib1.collaborative: base = collaborative==1 -> coefficient on 0.collaborative
    out["0.collaborative"] = (out["collaborative"] == 0).astype(float)
    return out


XR = ["1.place", "2.place", "3.place", "1.timeflex", "2.timeflex", "1.load", "2.load", "1.retention",
      "2.retention", "0.collaborative"]
TR = XR  # $TR in the do-file lists the same terms
