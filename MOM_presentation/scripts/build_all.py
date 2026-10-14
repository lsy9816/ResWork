"""build_all -- regenerate the deck's figures and tables for the appended employer sample from a build tree.

Usage: python3 build_all.py BUILD_DIR   (BUILD_DIR mirrors final/: deck_support/{data,mechanisms,scripts}, table/, overleaf/)

It imports the professor's figure/table scripts from BUILD_DIR/deck_support/scripts (copies; the originals are never touched)
and runs every figure/table function. Their hard-coded EVIDENCE_BOOK expectations describe the 303-firm sample, so "STOP"
data checks are logged as CHECK lines instead of ending the run; layout checks (text overflow) still stop the figure.
"""
import re
import sys
import traceback
import warnings
from pathlib import Path

sys.dont_write_bytecode = True
B = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(B / "deck_support" / "scripts"))

LAYOUT = re.compile(r"runs past|runs into|the space is|reaches the first separator|starts at .* within|text size\(s\)")
CHECKS = []
_orig_exit = sys.exit


def soft_exit(msg=0):
    if isinstance(msg, str) and msg.startswith("STOP") and not LAYOUT.search(msg):
        CHECKS.append(msg)
        print("CHECK (303-sample expectation, not enforced):", msg[:300])
        return None
    return _orig_exit(msg)


sys.exit = soft_exit
warnings.simplefilter("default")

import figstyle as S  # noqa: E402
import fig_main as FM  # noqa: E402
import fig_v2 as V  # noqa: E402
import fig_backup as FB  # noqa: E402
import fig_r5 as F5  # noqa: E402
import make_tables as MT  # noqa: E402

assert Path(S.ROOT).resolve() == B, (S.ROOT, B)
results = {}


def attempt(name, fn):
    n0 = len(CHECKS)
    try:
        out = fn()
        results[name] = ("ok", len(CHECKS) - n0, str(out)[:120])
        print("OK  ", name)
    except BaseException as e:  # noqa: BLE001
        results[name] = ("FAIL", len(CHECKS) - n0, f"{type(e).__name__}: {str(e)[:300]}")
        print("FAIL", name, type(e).__name__, str(e)[:300])
        traceback.print_exc(limit=3)


if __name__ == "__main__":
    only = set(sys.argv[2:])
    jobs = []
    for nm, fn in V.FIGS.items():
        jobs.append(("v2." + nm, fn))
    for nm, fn in F5.FIGS.items():
        jobs.append(("r5." + nm, fn))
    for fn in (FM.fig_mirror, FM.fig_employee_value, FM.fig_employer_eqpay, FM.fig_employer_where, FM.fig_practice, FM.fig_requests):
        jobs.append(("main." + fn.__name__, fn))
    for fn in (FB.fig_paygaps, FB.fig_emp_groups, FB.fig_benchmarks, FB.fig_org_splits, FB.fig_org_view, FB.fig_landscape,
               FB.fig_awareness, FB.fig_career, FB.fig_approvals_two, FB.fig_sample, FB.fig_industry):
        jobs.append(("backup." + fn.__name__, fn))
    for sh, grp, nm, rb in FB.RA_FIGS:
        jobs.append(("backup.ra_" + nm, (lambda sh=sh, grp=grp, nm=nm, rb=rb: FB.fig_ra(sh, grp, nm, robustness=rb))))
    for nm, fn in jobs:
        if only and not any(o in nm for o in only):
            continue
        attempt(nm, fn)
    if not only or "tables" in only:
        attempt("make_tables", lambda: [p.name for _, p in MT.build()])
    print("\nSUMMARY")
    for k, v in results.items():
        print(f"{v[0]:5s} checks={v[1]:3d} {k} {v[2] if v[0] == 'FAIL' else ''}")
