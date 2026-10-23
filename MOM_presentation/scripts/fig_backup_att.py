"""fig_backup_att -- appendix figures on attitudes and further firm characteristics (all respondents, 95% intervals, no joint tests).

F_use_att   : use among PMEs with the arrangement available, by agreement that flexible work hurts one's career / that users are
              seen as less committed (data/emp_access_use_attitudes.csv; attitude 1 = career, 2 = stigma; group 0 disagree, 1 neutral, 2 agree).
F_wtp_att   : pay PMEs would give up, by the same two attitudes (data/emp_career_impact.csv, data/emp_fwa_stigma.csv).
F_org_other : pay cut employers would require for the WFH options, by five further firm characteristics (results_fwa/employer_other.csv).
usage: BUILD=... OUTDIR=... python3 fig_backup_att.py [name ...]
"""
import sys
from pathlib import Path

import pandas as pd

sys.dont_write_bytecode = True
MOM = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOM / "scripts"))
import fig_wtp as W  # noqa: E402

S, M, V = W.S, W.M, W.V
GRP = [(0, "Disagree", "o", "white"), (1, "Neutral", "^", "#8A8F98"), (2, "Agree", "s", None)]   # filled colour None = side colour


def three_panel(name, panels, rows, getter, xlim, ticks, xlabel, SZ, color):
    """panels: list of (title, key); rows: list of (label, key); getter(panel_key, row_key, group) -> (est, lb, ub)."""
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, r[0], S.FS_ROW) for r in rows)
    PX0, GAP = LX + 0.15, 0.9
    k = len(panels)
    PW = (Wd - 0.65 - PX0 - (k - 1) * GAP) / k
    AY, AT = 1.35, H - 0.55
    n = len(rows)
    YA_, YB_ = 0.4, n + 0.6
    ys = [n - i for i in range(n)]

    def fy(v):
        return AY + (v - YA_) / (YB_ - YA_) * (AT - AY)
    for j, (title, pk) in enumerate(panels):
        ax = M.axes_cm(fig, PX0 + j * (PW + GAP), AY, PW, AT - AY)
        ax.set_xlim(*xlim)
        ax.set_ylim(YA_, YB_)
        S.ref_line(ax, xlim[0] if xlim[0] == 0 else 0, YA_, YB_)
        for (lab, rk), yy in zip(rows, ys):
            for g, _, mk, fc in GRP:
                e, lb, ub = getter(pk, rk, g)
                dy = (1 - g) * 0.24
                c = color if fc is None or fc == "white" else fc
                ax.plot([lb, ub], [yy + dy] * 2, color=c, lw=1.0, solid_capstyle="butt", zorder=2)
                ax.plot([e], [yy + dy], marker=mk, ms=4.6, mfc=(color if fc is None else fc), mec=c if fc == "white" else "white",
                        mew=S.MEW_HOLLOW if fc == "white" else S.MEW, ls="none", zorder=3)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(S.RULE)
        S.pct_ticks(ax, ticks)
        M.ftext(fig, PX0 + j * (PW + GAP) + PW / 2, AT + 0.08, title, ha="center", va="bottom", fontsize=S.FS_HEAD,
                fontweight="bold", color=color)
    for (lab, rk), yy in zip(rows, ys):
        M.ftext(fig, LX, fy(yy), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    W.nohead(fig, name, xlabel)
    keys = [(mk, (color if fc is None else fc), (color if fc == "white" else fc or color), 4.6, lab, S.INK, "normal")
            for g, lab, mk, fc in GRP]
    keys = [(mk, color if fc is None else fc, color if fc == "white" else "white", 4.6, lab, S.INK, "normal") for g, lab, mk, fc in GRP]
    V.r5_key(fig, (Wd - V.key_width(fig, keys, gap=0.35)) / 2, 0.16, keys, gap=0.35)
    V.outside(fig, name)
    return M.finish(fig, name, SZ)


def fig_use_att():
    d = pd.read_csv(MOM / "data" / "emp_access_use_attitudes.csv")
    rows = [("Scheduled remote work", 1), ("Fully remote work", 2), ("Staggered hours", 3), ("Compressed week", 4),
            ("Job sharing", 5), ("Part-time", 6)]

    def get(pk, rk, g):
        q = d[(d.attitude == pk) & (d.fwa == rk) & (d.group == g)].iloc[0]
        return q.rate, q.lb, q.ub
    return three_panel("F_use_att", [("Career will suffer", 1), ("Users seen as less committed", 2)], rows, get,
                       (0, 100), [0, 50, 100], "Using, among PMEs with the arrangement available (%)", (14.5, 6.0), S.EMPLOYEE)


def fig_wtp_att():
    a = pd.read_csv(MOM / "data" / "emp_career_impact.csv")
    b = pd.read_csv(MOM / "data" / "emp_fwa_stigma.csv")
    src = {"career": a, "stigma": b}
    rows = [("1–2 WFH days", "1.place"), ("3–4 WFH days", "2.place"), ("Fully remote", "3.place"), ("Compressed week", "2.timeflex"),
            ("Staggered hours", "1.timeflex"), ("Job sharing", "1.load"), ("Part-time", "2.load")]

    def get(pk, rk, g):
        q = src[pk]
        q = q[(q.group == g) & (q.term == rk)].iloc[0]
        return q.wtp, q.lb, q.ub
    return three_panel("F_wtp_att", [("Career will suffer", "career"), ("Users seen as less committed", "stigma")], rows, get,
                       (-8, 32), [0, 10, 20, 30], "Pay PMEs would give up, % of monthly pay", (14.5, 6.4), S.EMPLOYEE)


def fig_org_other():
    d = pd.read_csv(MOM / "results_fwa" / "employer_other.csv")
    # each split as a row; panels = the three WFH options; group 1 filled, group 0 hollow (two groups)
    SPL = [("plan", "Plans to expand FWAs"), ("hire", "Difficulty filling vacancies"), ("talent", "FWAs help attract talent"),
           ("turn", "Turnover 10% or more"), ("tech", "Technology fully ready")]
    items = [("p1", "1–2 days"), ("p2", "3–4 days"), ("p3", "Remote")]
    SZ = (14.5, 5.0)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    labs, nn = [], []
    for s, lab in SPL:
        q = d[(d.split == s) & (d.item == "p1")].iloc[0]
        labs.append(lab)
        nn.append((int(q.n1), int(q.n0)))
    LX = 0.05 + max(V.tw_cm(fig, t, S.FS_ROW) for t in labs)
    PX0, GAP = LX + 0.15, 0.25
    PW = (Wd - 0.65 - PX0 - 2 * GAP) / 3
    AY, AT = 1.20, H - 0.55
    n = len(SPL)
    YA_, YB_ = 0.4, n + 0.6
    ys = [n - i for i in range(n)]

    def fy(v):
        return AY + (v - YA_) / (YB_ - YA_) * (AT - AY)
    for j, (it, title) in enumerate(items):
        ax = M.axes_cm(fig, PX0 + j * (PW + GAP), AY, PW, AT - AY)
        ax.set_xlim(-35, 100)
        ax.set_ylim(YA_, YB_)
        S.ref_line(ax, 0, YA_, YB_)
        for (s, lab), yy in zip(SPL, ys):
            q = d[(d.split == s) & (d.item == it)].iloc[0]
            for filled, e, lb, ub, dy in ((True, q.cut1, q.lb1, q.ub1, 0.17), (False, q.cut0, q.lb0, q.ub0, -0.17)):
                ax.plot([lb, ub], [yy + dy] * 2, color=S.EMPLOYER, lw=1.0, solid_capstyle="butt", zorder=2)
                ax.plot([e], [yy + dy], marker="D", ms=4.6, mfc=S.EMPLOYER if filled else "white",
                        mec="white" if filled else S.EMPLOYER, mew=S.MEW if filled else S.MEW_HOLLOW, ls="none", zorder=3)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(S.RULE)
        S.pct_ticks(ax, [0, 50, 100])
        M.ftext(fig, PX0 + j * (PW + GAP) + PW / 2, AT + 0.08, title, ha="center", va="bottom", fontsize=S.FS_HEAD,
                fontweight="bold", color=S.EMPLOYER)
    for t, yy in zip(labs, ys):
        M.ftext(fig, LX, fy(yy), t, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    W.nohead(fig, "F_org_other", "Pay cut employers would require, % of pay")
    keys = [("D", S.EMPLOYER, S.EMPLOYER, 4.6, "Yes", S.INK, "normal"),
            ("D", "white", S.EMPLOYER, 4.6, "No", S.INK, "normal")]
    V.r5_key(fig, (Wd - V.key_width(fig, keys, gap=0.35)) / 2, 0.16, keys, gap=0.35)
    V.outside(fig, "F_org_other")
    return M.finish(fig, "F_org_other", SZ)


def fig_dominance():
    """Share choosing the dominant job by its salary gap (data/pme_dominance.csv from scripts/pme_dominance.py)."""
    d = pd.read_csv(MOM / "data" / "pme_dominance.csv")
    SZ = (12.0, 5.2)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    ax = M.axes_cm(fig, 1.4, 1.35, Wd - 1.9, H - 1.55)
    ax.set_xlim(-0.44, 0.34)
    ax.set_ylim(0, 1.02)
    S.ref_line(ax, 0, 0, 1.02)
    c = d.dropna(subset=["pred"])
    ax.plot(c.bin, c.pred, color=S.MUTED, lw=1.6, zorder=2)
    p = d.dropna(subset=["frac"])
    for _, q in p.iterrows():
        ax.plot([q.bin] * 2, [q.frac - 1.96 * q.se, q.frac + 1.96 * q.se], color=S.EMPLOYEE, lw=S.CI_LW, zorder=2)
    ax.plot(p.bin, p.frac, ls="none", marker="o", ms=S.MS_CIRCLE, mfc=S.EMPLOYEE, mec="white", mew=S.MEW, zorder=3)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0", "25", "50", "75", "100%"])
    ax.set_xticks([-0.4, -0.3, -0.2, 0, 0.2, 0.3])
    ax.set_xticklabels(["-0.4", "-0.3", "-0.2", "0", "0.2", "0.3"])
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(S.RULE)
    ax.spines["left"].set_color(S.RULE)
    W.nohead(fig, "F_dominance", "Salary of the dominant job minus the other (log points)")
    keys = [("o", S.EMPLOYEE, "white", S.MS_CIRCLE, "Observed share, 95% CI", S.INK, "normal"),
            ("s", S.MUTED, "white", S.MS_CIRCLE, "Model prediction", S.INK, "normal")]
    V.r5_key(fig, (Wd - V.key_width(fig, keys, gap=0.35)) / 2, 0.16, keys, gap=0.35)
    V.outside(fig, "F_dominance")
    return M.finish(fig, "F_dominance", SZ)


def fig_groups_diff():
    """Difference in pay PMEs would give up between groups, all seven arrangements (dce_emp_het.csv pairwise rows; diff, se -> 95% CI)."""
    h = pd.read_csv(Path(W.BUILD) / "deck_support" / "data" / "dce_emp_het.csv")
    h = h[h.block == "pairwise"]
    items = [("p12", "1–2 WFH days"), ("p34", "3–4 WFH days"), ("remote", "Fully remote"), ("compress", "Compressed week"),
             ("stagger", "Staggered hours"), ("jobshare", "Job sharing"), ("parttime", "Part-time")]
    panels = [("female", "Women − men"), ("age40", "40+ − under 40"), ("care_any", "Caregiving − none")]
    SZ = (14.5, 5.0)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, t, S.FS_ROW) for _, t in items)
    PX0, GAP = LX + 0.15, 0.55
    PW = (Wd - 0.65 - PX0 - 2 * GAP) / 3
    AY, AT = 1.15, H - 0.65
    n = len(items)
    YA_, YB_ = 0.4, n + 0.6
    ys = [n - i for i in range(n)]

    def fy(v):
        return AY + (v - YA_) / (YB_ - YA_) * (AT - AY)
    for j, (sp, title) in enumerate(panels):
        ax = M.axes_cm(fig, PX0 + j * (PW + GAP), AY, PW, AT - AY)
        ax.set_xlim(-20, 20)
        ax.set_ylim(YA_, YB_)
        S.ref_line(ax, 0, YA_, YB_)
        for (it, lab), yy in zip(items, ys):
            q = h[(h.split == sp) & (h["item"] == it)].iloc[0]
            lb, ub = q["diff"] - 1.96 * q.se, q["diff"] + 1.96 * q.se
            filled = lb > 0 or ub < 0
            ax.plot([lb, ub], [yy, yy], color=S.EMPLOYEE, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
            ax.plot([q["diff"]], [yy], marker="o", ms=S.MS_CIRCLE, mfc=S.EMPLOYEE if filled else "white",
                    mec="white" if filled else S.EMPLOYEE, mew=S.MEW if filled else S.MEW_HOLLOW, ls="none", zorder=3)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(S.RULE)
        ax.set_xticks([-15, 0, 15])
        ax.set_xticklabels(["-15", "0", "15"])
        M.ftext(fig, PX0 + j * (PW + GAP) + PW / 2, AT + 0.08, title, ha="center", va="bottom", fontsize=S.FS_HEAD,
                fontweight="bold", color=S.EMPLOYEE)
    for (it, lab), yy in zip(items, ys):
        M.ftext(fig, LX, fy(yy), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    keys = [("o", S.EMPLOYEE, "white", S.MS_CIRCLE, "Interval excludes 0", S.INK, "normal"),
            ("o", "white", S.EMPLOYEE, S.MS_CIRCLE, "Includes 0", S.INK, "normal")]
    V.r5_key(fig, (Wd - V.key_width(fig, keys, gap=0.35)) / 2, 0.16, keys, gap=0.35)
    V.outside(fig, "F_groups_diff")
    return M.finish(fig, "F_groups_diff", SZ)


if __name__ == "__main__":
    figs = {"F_use_att": fig_use_att, "F_wtp_att": fig_wtp_att, "F_org_other": fig_org_other, "F_dominance": fig_dominance, "F_groups_diff": fig_groups_diff}
    for nm in sys.argv[1:] or list(figs):
        print("wrote", figs[nm]())
    for fl in dict.fromkeys(M.FLAGS):
        print("FLAG:", fl)
