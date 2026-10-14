"""fig_r5_appended -- the professor's deck_support/scripts/fig_r5.py, patched IN MEMORY for the appended employer
sample (n = 397). The original file is only read, never written. Each replacement must match the original exactly
once, so the run stops if fig_r5.py changes. Changes: expected values of F_org_eqpay, F_where_r5 and F_meet_r5
(appended_clogit.xlsx; 303-firm EVIDENCE_BOOK employer strings not checked) and 0.10 cm more label room on
F_where_r5 for three-digit n labels. Imported by make_figs_appended.py.
"""
import sys
from pathlib import Path

import figstyle as _S

_SRC = Path(_S.__file__).with_name("fig_r5.py")

REPLACEMENTS = [
    ('    exp = {  # level: (label, Q id, EB share, EB CI)',
     '    # Employer update (14 Oct 2026): appended employer sample (n = 397), appended_clogit.xlsx sheet main,\n    # invlogit(b) with delta-method 95% CIs. The EVIDENCE_BOOK Q1-Q8/R12 rows still hold the 303-firm values,\n    # so the string checks against them are switched off here; the expected values below are the appended ones.\n    exp = {  # level: (label, Q id, share, CI)'),
    ('        "2.timeflex": ("Compressed week", "Q5", 48, (41, 55)),',
     '        "2.timeflex": ("Compressed week", "Q5", 47, (41, 53)),'),
    ('        "1.timeflex": ("Staggered hours", "Q4", 44, (38, 50)),',
     '        "1.timeflex": ("Staggered hours", "Q4", 45, (40, 50)),'),
    ('        "1.place": ("1–2 WFH days", "Q1", 42, (37, 48)),',
     '        "1.place": ("1–2 WFH days", "Q1", 40, (35, 45)),'),
    ('        "2.place": ("3–4 WFH days", "Q2", 37, (31, 43)),',
     '        "2.place": ("3–4 WFH days", "Q2", 31, (26, 36)),'),
    ('        "3.place": ("Fully remote", "Q3", 28, (21, 34)),',
     '        "3.place": ("Fully remote", "Q3", 23, (18, 28)),'),
    ('    }\n    for lev, (_, qid, v, (lo, hi)) in exp.items():\n        eb_row_has(qid, f"**{v}%** ({lo}–{hi})")\n    eb_row_has("Q8", "**37.5%** (31–44)")\n    V.eb_has("R12", "compressed 48%, 1–2 days 42%, 3–4 days 37%, fully remote **28%**")',
     '    }'),
    ('    bt = M.record(name, "37.5%", bv, bd, "Q8", 37.5, "benchmark: candidate with >20% turnover risk: equal-pay share")',
     '    bt = M.record(name, "33.6%", bv, bd, "Q8", 33.6, "benchmark: candidate with >20% turnover risk: equal-pay share")'),
    ('    M.record(name, "(CI end, unlabelled)", blb, bd + " (lb)", "Q8", 31, "benchmark: 95% CI lower")',
     '    M.record(name, "(CI end, unlabelled)", blb, bd + " (lb)", "Q8", 28, "benchmark: 95% CI lower")'),
    ('    M.record(name, "(CI end, unlabelled)", bub, bd + " (ub)", "Q8", 44, "benchmark: 95% CI upper")',
     '    M.record(name, "(CI end, unlabelled)", bub, bd + " (ub)", "Q8", 39, "benchmark: 95% CI upper")'),
    ('    V.eb_has("M10", "Most PME roles need on-site presence (n = 98): **29 / 28 / 22 / 54%**",\n             "only some or few roles (n = 205): **49 / 41 / 30 / 46%**",\n             "(agree 4–5, n = 162): **40 / 31 / 19 / 42%**", "not worried (n = 141): **46 / 44 / 39 / 54%**")\n    V.eb_has("Q10", "Most PME roles need presence (n=98): 1–2 days 29%",\n             "Only some or few roles do (n=205): 1–2 days **49% (≈ indifferent)**")\n    V.eb_has("Q11", "(n=162): 1–2 days 40%, 3–4 days 31%, remote **19%**", "Not worried (n=141): 46%, 44%, 39%")\n    # drawn 95% CIs: EB M10 \'Drawn 95% CIs on F_where_r5\' (separate per-group clogits; fixer pass 7 Oct 2026)',
     '    # Employer update (14 Oct 2026): appended employer sample; rows from ../data/employer_channels_appended.csv'),
    ('    V.eb_has("M10", "**49.2 [41.9, 56.4]**", "**29.2 [20.3, 38.1]**", "**39.1 [28.4, 49.9]**", "**19.5 [11.8, 27.2]**")',
     '    # (appended_clogit.xlsx physical_1/2 and creative_concern_1/0, invlogit with delta-method CIs). The 303-firm\n    # EVIDENCE_BOOK M10/Q10/Q11 strings are not checked here.'),
    ('    CI_EB = {("physical", "0"): (41.9, 56.4), ("physical", "1"): (20.3, 38.1),',
     '    CI_EB = {("physical", "0"): (41.7, 54.7), ("physical", "1"): (19.3, 33.7),'),
    ('             ("creative", "0"): (28.4, 49.9), ("creative", "1"): (11.8, 27.2)}',
     '             ("creative", "0"): (20.8, 37.3), ("creative", "1"): (11.3, 24.6)}'),
    ('    blocks = [  # header, item, rows: (split, group, label, EB share, EB n, focal?)',
     '    blocks = [  # header, item, rows: (split, group, label, share, n, focal?)'),
    ('         [("physical", "1", "Most roles need presence", 29, 98, True),',
     '         [("physical", "1", "Most roles need presence", 27, 137, True),'),
    ('          ("physical", "0", "Some or few roles do", 49, 205, False)]),',
     '          ("physical", "0", "Some or few roles do", 48, 260, False)]),'),
    ('         [("creative", "1", "Creativity concern", 19, 162, True),',
     '         [("creative", "1", "Creativity concern", 18, 201, True),'),
    ('          ("creative", "0", "No creativity concern", 39, 141, False)]),',
     '          ("creative", "0", "No creativity concern", 29, 196, False)]),'),
    ('    LX, X0, X1, VX = 5.10, 5.30, 11.75, W - 0.05',
     '    # appended: three-digit n labels ("n = 137") need 0.10 cm more label room than "n = 98"\n    LX, X0, X1, VX = 5.20, 5.40, 11.75, W - 0.05'),
    ('    eb_row_has("Q5", "**58%** (55–62)", "**48%** (41–55)")',
     '    # Employer update (14 Oct 2026): employer panel = appended sample (n = 397); EB employer strings not checked\n    eb_row_has("Q5", "**58%** (55–62)")'),
    ('    eb_row_has("Q1", "**58%** (55–62)", "**42%** (37–48)")',
     '    eb_row_has("Q1", "**58%** (55–62)")'),
    ('    eb_row_has("Q2", "**61%** (57–64)", "**37%** (31–43)")\n    eb_row_has("Q3", "**28%** (21–34)")',
     '    eb_row_has("Q2", "**61%** (57–64)")'),
    ('        ("Compressed week", "2.timeflex", "2.timeflex", ("Q5", 58, (55, 62)), ("Q5", 48, (41, 55)),',
     '        ("Compressed week", "2.timeflex", "2.timeflex", ("Q5", 58, (55, 62)), ("Q5", 47, (41, 53)),'),
    ('        ("1–2 WFH days", "1.place", "1.place", ("Q1", 58, (55, 62)), ("Q1", 42, (37, 48)),',
     '        ("1–2 WFH days", "1.place", "1.place", ("Q1", 58, (55, 62)), ("Q1", 40, (35, 45)),'),
    ('        ("3–4 WFH days", "2.place", "2.place", ("Q2", 61, (57, 64)), ("Q2", 37, (31, 43)), "C  Far apart"),',
     '        ("3–4 WFH days", "2.place", "2.place", ("Q2", 61, (57, 64)), ("Q2", 31, (26, 36)), "C  Far apart"),'),
    ('        ("Fully remote", "p3own", "3.place", ("M1", 64, (61, 68)), ("Q3", 28, (21, 34)), "C  Far apart"),',
     '        ("Fully remote", "p3own", "3.place", ("M1", 64, (61, 68)), ("Q3", 23, (18, 28)), "C  Far apart"),'),
]

_code = _SRC.read_text(encoding="utf-8")
for _old, _new in REPLACEMENTS:
    if _code.count(_old) != 1:
        sys.exit(f"STOP: fig_r5.py changed; patch text not found exactly once: {_old[:70]!r}")
    _code = _code.replace(_old, _new)
exec(compile(_code, str(_SRC) + " [appended patch]", "exec"), globals())
