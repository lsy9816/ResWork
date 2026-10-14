"""zonetests -- port of deck_zonetests.do (employer Wald tests behind the A/B/C zones; EVIDENCE_BOOK Q16, Q10c)."""
import sys
sys.path.insert(0, "/home/user/ResWork/MOM_presentation/scripts/port")
from stata_core import clogit, wald
from employer_data import load, dce_frame, dummies, XR


def run(dta, appended):
    d = dummies(dce_frame(load(dta, appended)))
    X = ["log_salary"] + XR
    f = clogit(d, "chosen", X, "choice_set", "id")
    out = []

    def T(fit, label, a, b=None):
        row = {a: 1, **({b: -1} if b else {})}
        chi, df, p = wald(fit, [row])
        out.append((label, chi, p))
    T(f, "ALL: compressed vs 1-2 days", "2.timeflex", "1.place")
    T(f, "ALL: 1-2 vs 3-4 days", "1.place", "2.place")
    T(f, "ALL: 3-4 days vs remote", "2.place", "3.place")
    T(f, "ALL: staggered vs compressed", "1.timeflex", "2.timeflex")
    sub = d[d["physical_presence"] == 1]
    g = clogit(sub, "chosen", X, "choice_set", "id")
    T(g, "MOST ROLES NEED PRESENCE: compressed vs 1-2 days", "2.timeflex", "1.place")
    T(g, "MOST ROLES NEED PRESENCE: compressed = 0", "2.timeflex")
    T(g, "MOST ROLES NEED PRESENCE: staggered = 0", "1.timeflex")
    return out, f.G, g.G


if __name__ == "__main__":
    SP = "/tmp/claude-0/-home-user-ResWork/ddc3d860-5d1b-54ab-bc5b-0b5766ecc715/scratchpad/dl"
    for nm, p, app in (("303", f"{SP}/src/employer.dta", False), ("397", f"{SP}/appended.dta", True)):
        out, n1, n2 = run(p, app)
        print(nm, "clusters", n1, n2)
        for l, c, pv in out:
            print(f"  {l:55s} chi2={c:7.3f} p={pv:.4f}")
