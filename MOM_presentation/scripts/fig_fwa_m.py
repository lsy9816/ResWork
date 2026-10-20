"""fig_fwa_m -- main-slide figures for "why are the other FWAs used so little?" (deck style, same helpers as fig_wtp.py).

Reads results_fwa/*.csv (scripts/fwa_diagnosis.py, scripts/fwa_current.py), data/org_fwa.csv, data/org_attitudes.csv and
the PME barrier aggregates of the build tree.  Figures: F_use_m, F_fwa_challenge_m, F_fwa_current_m.

usage: BUILD=/path/to/build OUTDIR=/path/to/figures python3 fig_fwa_m.py [name ...]
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fig_wtp as W  # noqa: E402  (helpers; running it as a module draws nothing)
from fig_wtp import M, S, V, Rectangle, r0, txt0, vlabel, ci_dot, frame, new_fig, done, MOM  # noqa: E402

RES = MOM / "results_fwa"
V.SIZE.update({k: W.SIZE for k in ("F_use_m", "F_fwa_challenge_m", "F_fwa_current_m")})


def bar(fig, x0, y, w, h, col):
    fig.add_artist(Rectangle((x0 / fig.W, (y - h / 2) / fig.H), w / fig.W, h / fig.H, transform=fig.transFigure,
                             fc=col, ec="none", lw=0))


# ----------------------------------------------------------------------------------------------------------------
# F_fwa_diag_m: for each arrangement, who offers it, who uses it, and the two sides' pay terms
# ----------------------------------------------------------------------------------------------------------------
def fig_fwa_diag_m():
    name = "F_fwa_diag_m"
    dg = pd.read_csv(RES / "fwa_diagnosis.csv")
    tk = pd.read_csv(RES / "fwa_takeup.csv").set_index("arrangement")
    rows = [("WFH 1\u20132 days", "p1", "remote"), ("Staggered hours", "t1", "staggered"),
            ("Compressed week", "t2", "compressed"), ("Job sharing", "l1", "jobshare"), ("Part-time", "l2", "parttime")]
    SZ = (13.0, 4.9)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, r[0], S.FS_ROW) for r in rows)
    pitch = 0.70
    top = H - 1.72
    bh = 0.34
    A0, AW = LX + 0.30, 1.25
    B0 = A0 + 2.45
    C0 = B0 + 2.45
    D0 = C0 + 2.45

    def head(x, s, col):
        M.ftext(fig, x, H - 0.04, s, ha="left", va="top", fontsize=S.FS_CAP, color=col, fontweight="bold",
                linespacing=1.1, multialignment="left")
    head(A0, "Firms\noffering", S.EMPLOYER)
    head(B0, "PMEs\nusing", S.EMPLOYEE)
    head(C0, "Use, if\navailable", S.EMPLOYEE)
    head(D0, "Employers' cut\nminus PMEs'\ngive-up, points", S.INK)
    V.hline_cm(fig, 0.05, Wd - 0.05, H - 1.24, **S.SEP)
    for i, (lab, item, key) in enumerate(rows):
        y = top - i * pitch
        r = dg[dg["item"] == item].iloc[0]
        M.ftext(fig, LX, y, lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
        off = float(r.firms_ticked)
        used = float(tk.loc[key, "used"])
        bar(fig, A0, y, max(off / 100 * AW, 0.03), bh, S.EMPLOYER)
        M.ftext(fig, A0 + off / 100 * AW + 0.12, y, f"{r0(off)}%", ha="left", va="center", fontsize=S.FS_VAL,
                color=S.EMPLOYER, fontweight="bold")
        bar(fig, B0, y, max(used / 100 * AW, 0.03), bh, S.EMPLOYEE)
        M.ftext(fig, B0 + used / 100 * AW + 0.12, y, f"{r0(used)}%", ha="left", va="center", fontsize=S.FS_VAL,
                color=S.EMPLOYEE, fontweight="bold")
        M.ftext(fig, C0, y, f"{r0(float(tk.loc[key, 'takeup']))}%", ha="left", va="center",
                fontsize=S.FS_VAL, color=S.EMPLOYEE, fontweight="bold")
        overlap = r.gap_lb <= 0 <= r.gap_ub
        M.ftext(fig, D0, y, txt0(r.gap), ha="left", va="center", fontsize=S.FS_VAL,
                color=S.MUTED if overlap else S.INK, fontweight="bold")
    for x in (A0 - 0.14, B0 - 0.14, C0 - 0.14, D0 - 0.14):
        V.vline_cm(fig, x, top - 4 * pitch - bh / 2 - 0.06, top + bh / 2 + 0.06, color=S.RULE, lw=0.7)
    V.outside(fig, name)
    return M.finish(fig, name, SZ)


# ----------------------------------------------------------------------------------------------------------------
# F_use_m (M-descriptive): offering, use, and use among PMEs who have access -- the three columns of F_fwa_diag_m
# ----------------------------------------------------------------------------------------------------------------
def fig_use_m():
    name = "F_use_m"
    dg = pd.read_csv(RES / "fwa_diagnosis.csv")
    tk = pd.read_csv(RES / "fwa_takeup.csv").set_index("arrangement")
    rows = [("Work from home", "p1", "remote"), ("Staggered hours", "t1", "staggered"),
            ("Compressed week", "t2", "compressed"), ("Job sharing", "l1", "jobshare"), ("Part-time", "l2", "parttime")]
    SZ = (13.0, 4.9)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, r[0], S.FS_ROW) for r in rows)
    pitch, top, bh = 0.80, H - 1.35, 0.36
    A0, AW = LX + 0.40, 1.80
    B0 = A0 + 3.10
    C0 = B0 + 3.10

    def head(x, s, col):
        M.ftext(fig, x, H - 0.04, s, ha="left", va="top", fontsize=S.FS_CAP, color=col, fontweight="bold",
                linespacing=1.1, multialignment="left")
    head(A0, "Firms offering it\nto PMEs", S.EMPLOYER)
    head(B0, "PMEs with access\nto it", S.EMPLOYEE)
    head(C0, "Of those, share\nusing it", S.EMPLOYEE)
    V.hline_cm(fig, 0.05, Wd - 0.05, H - 0.80, **S.SEP)
    for i, (lab, item, key) in enumerate(rows):
        y = top - i * pitch
        r = dg[dg["item"] == item].iloc[0]
        M.ftext(fig, LX, y, lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
        off, used = float(r.firms_ticked), float(tk.loc[key, "avail"])
        bar(fig, A0, y, max(off / 100 * AW, 0.03), bh, S.EMPLOYER)
        M.ftext(fig, A0 + off / 100 * AW + 0.12, y, f"{r0(off)}%", ha="left", va="center", fontsize=S.FS_VAL,
                color=S.EMPLOYER, fontweight="bold")
        bar(fig, B0, y, max(used / 100 * AW, 0.03), bh, S.EMPLOYEE)
        M.ftext(fig, B0 + used / 100 * AW + 0.12, y, f"{r0(used)}%", ha="left", va="center", fontsize=S.FS_VAL,
                color=S.EMPLOYEE, fontweight="bold")
        tku = float(tk.loc[key, "takeup"])
        bar(fig, C0, y, max(tku / 100 * AW, 0.03), bh, S.EMPLOYEE)
        M.ftext(fig, C0 + tku / 100 * AW + 0.12, y, f"{r0(tku)}%", ha="left", va="center", fontsize=S.FS_VAL,
                color=S.EMPLOYEE, fontweight="bold")
    for x in (A0 - 0.14, B0 - 0.14, C0 - 0.14):
        V.vline_cm(fig, x, top - 4 * pitch - bh / 2 - 0.06, top + bh / 2 + 0.06, color=S.RULE, lw=0.7)
    V.outside(fig, name)
    return M.finish(fig, name, SZ)


# ----------------------------------------------------------------------------------------------------------------
# F_fwa_challenge_m: employers' biggest challenge in offering FWAs (all 397, including "Other")
# ----------------------------------------------------------------------------------------------------------------
def fig_fwa_challenge_m():
    name = "F_fwa_challenge_m"
    ch = pd.read_csv(RES / "fwa_employer_challenge.csv")
    short = {"Productivity and output quality": "Productivity and output quality",
             "Team coordination and communication": "Team coordination",
             "Fairness across roles (not every role can be flexible)": "Fairness across roles",
             "Managerial resistance or lack of trust": "Managerial resistance or trust",
             "Lack of digital infrastructure": "Digital infrastructure",
             "Security, confidentiality or compliance": "Security or compliance", "Other": "Other"}
    fig = new_fig(name)
    Wd, H = fig.W, fig.H
    labs = [short[c] for c in ch.challenge]
    LX = 0.05 + max(V.tw_cm(fig, t, S.FS_ROW) for t in labs)
    M.ftext(fig, 0.05, H - 0.04, f"Employers' biggest challenge in offering FWAs, % of employers (n = {int(ch.n.iloc[0])})",
            ha="left", va="top", fontsize=S.FS_HEAD, color=S.EMPLOYER, fontweight="bold")
    top = H - 0.95
    pitch = (top - 0.30) / (len(ch) - 1)
    B0, BW = LX + 0.18, Wd - LX - 1.4
    for i, (r, lab) in enumerate(zip(ch.itertuples(), labs)):
        y = top - i * pitch
        M.ftext(fig, LX, y, lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
        bar(fig, B0, y, r.share / 30 * BW, 0.38, S.EMPLOYER)
        M.ftext(fig, B0 + r.share / 30 * BW + 0.14, y, f"{r0(r.share)}%", ha="left", va="center", fontsize=S.FS_VAL,
                color=S.EMPLOYER, fontweight="bold")
    V.vline_cm(fig, B0, top - (len(ch) - 1) * pitch - 0.25, top + 0.25, color=S.RULE, lw=0.7)
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# F_fwa_current_m (backup): pay PMEs would give up, by whether they already use the arrangement
# ----------------------------------------------------------------------------------------------------------------
def fig_fwa_current_m():
    name = "F_fwa_current_m"
    cu = pd.read_csv(RES / "fwa_current.csv").set_index("term")
    order = [("Fully remote", "remote", 7.0), ("3\u20134 WFH days", "place34", 5.95), ("1\u20132 WFH days", "place12", 5.05),
             ("Compressed week", "compress", 4.15), ("Staggered hours", "stagger", 3.25),
             ("Job sharing", "jobshare", 1.95), ("Part-time", "parttime", 1.05)]
    fig = new_fig(name)
    labels = [f"{a} ({int(cu.loc[t, 'n_users'])} use it)" for a, t, _ in order]
    F = frame(fig, labels, -14, 34, [-10, 0, 10, 20, 30], val_w=0.35, bottom=0.60)
    W.nohead(fig, name, "Extra pay given up by PMEs already in the arrangement, points of % of pay")
    V.hline_cm(fig, 0.05, fig.W - 0.05, F["fy"](2.6), **S.SEP)
    for (a, t, y), lab in zip(order, labels):
        r = cu.loc[t]
        ci_dot(F["ax"], y, r["diff"], r.diff_lb, r.diff_ub, S.EMPLOYEE)
        v = r["diff"]
        vlabel(F["ax"], max(r.diff_ub, v), y, ("+" if v >= 0.5 else "") + txt0(v), S.EMPLOYEE)
        M.ftext(fig, F["LX"], F["fy"](y), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    return done(fig, name)


FIGS = {"F_use_m": fig_use_m, "F_fwa_challenge_m": fig_fwa_challenge_m, "F_fwa_current_m": fig_fwa_current_m}

if __name__ == "__main__":
    import warnings
    warnings.simplefilter("default")
    for nm in sys.argv[1:] or list(FIGS):
        print("wrote", FIGS[nm]())
    for fl in dict.fromkeys(M.FLAGS):
        print("FLAG:", fl)
