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


SPL8 = [("physical", "Most roles need presence", 0), ("curwfh", "No WFH today", 1), ("policy", "No written policy", 1),
        ("belief", "Salary offset belief", 0), ("concern", "High overall concern", 0), ("creat", "Creativity suffers apart", 0),
        ("prod", "Productivity worry", 0), ("coord", "Coordination worry", 0)]
SPL5 = [("plan", "Plans to expand FWAs"), ("hire", "Difficulty filling vacancies"), ("talent", "FWAs help attract talent"),
        ("turn", "Turnover 10% or more"), ("tech", "Technology fully ready")]


def deck_emp(split, group, item):
    q = W.D[(W.D.side == "emp") & (W.D["sample"] == "main") & (W.D.split == split) & (W.D.group == group) & (W.D["item"] == item)].iloc[0]
    return float(q.giveup), float(q.lb), float(q.ub)


def diamond(ax, y, e, lb, ub, filled):
    ax.plot([lb, ub], [y, y], color=S.EMPLOYER, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
    ax.plot([e], [y], marker="D", ms=S.MS_DIAMOND, mfc=S.EMPLOYER if filled else "white", mec="white" if filled else S.EMPLOYER,
            mew=S.MEW if filled else S.MEW_HOLLOW, ls="none", zorder=3, clip_on=False)


def yes_no_key(fig):
    keys = [("D", S.EMPLOYER, S.EMPLOYER, S.MS_DIAMOND, "Yes", S.INK, "normal"),
            ("D", "white", S.EMPLOYER, S.MS_DIAMOND, "No", S.INK, "normal")]
    V.r5_key(fig, (fig.W - V.key_width(fig, keys)) / 2, 0.16, keys)


def fig_org_overview(name="F_org_splits", which="roles"):
    """Employer splits, WFH options only: pay cut required, yes vs no."""
    o = pd.read_csv(MOM / "results_fwa" / "employer_other.csv")
    items = [("p1", "1–2 days"), ("p2", "3–4 days"), ("p3", "Remote")]
    rows = []
    if which == "roles":
        for sp, lab, g in SPL8:
            rows.append((lab, {it: (deck_emp(sp, g, it), deck_emp(sp, 1 - g, it)) for it, _ in items}))
    else:
        for sp, lab in SPL5:
            d = {}
            for it, _ in items:
                q = o[(o.split == sp) & (o["item"] == it)].iloc[0]
                d[it] = ((q.cut1, q.lb1, q.ub1), (q.cut0, q.lb0, q.ub0))
            rows.append((lab, d))
    SZ = (14.5, 5.4 if which == "roles" else 4.6)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, r[0], S.FS_ROW) for r in rows)
    PX0, GAP = LX + 0.15, 0.25
    PW = (Wd - 0.65 - PX0 - 2 * GAP) / 3
    AY, AT = 1.15, H - 0.55
    n = len(rows)
    YA_, YB_ = 0.4, n + 0.6
    ys = [n - i for i in range(n)]

    def fy(v):
        return AY + (v - YA_) / (YB_ - YA_) * (AT - AY)
    for j, (it, title) in enumerate(items):
        ax = M.axes_cm(fig, PX0 + j * (PW + GAP), AY, PW, AT - AY)
        ax.set_xlim(-35, 100)
        ax.set_ylim(YA_, YB_)
        S.ref_line(ax, 0, YA_, YB_)
        for (lab, d), yy in zip(rows, ys):
            (e1, l1, u1), (e0, l0, u0) = d[it]
            diamond(ax, yy + 0.17, e1, l1, u1, True)
            diamond(ax, yy - 0.17, e0, l0, u0, False)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(S.RULE)
        S.pct_ticks(ax, [0, 50, 100])
        M.ftext(fig, PX0 + j * (PW + GAP) + PW / 2, AT + 0.08, title, ha="center", va="bottom", fontsize=S.FS_HEAD,
                fontweight="bold", color=S.EMPLOYER)
    for (lab, d), yy in zip(rows, ys):
        M.ftext(fig, LX, fy(yy), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    if which == "roles":
        V.hline_cm(fig, 0.05, Wd - 0.05, fy(4.5), **S.SEP)
    yes_no_key(fig)
    V.outside(fig, name)
    return M.finish(fig, name, SZ)


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
    # key at the bottom, centred: dot = observed share, line = model prediction
    t1, t2 = "Observed share, 95% CI", "Model prediction"
    w1 = 0.33 + V.tw_cm(fig, t1, S.FS_TICK)
    w2 = 0.55 + V.tw_cm(fig, t2, S.FS_TICK)
    gap = 0.42
    x = (Wd - (w1 + gap + w2)) / 2
    M.fmarker(fig, x + 0.11, 0.16, "o", S.EMPLOYEE, "white", size=S.MS_CIRCLE, lw=S.MEW)
    M.ftext(fig, x + 0.33, 0.16, t1, ha="left", va="center", fontsize=S.FS_TICK, color=S.INK)
    x += w1 + gap
    V.hline_cm(fig, x, x + 0.45, 0.16, color=S.MUTED, lw=1.6)
    M.ftext(fig, x + 0.55, 0.16, t2, ha="left", va="center", fontsize=S.FS_TICK, color=S.INK)
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


GROUP_MARK = [("o", "white"), ("o", "half"), ("o", "full")]   # smallest group hollow, middle half-tone, largest filled


def draw3(ax, y, vals, color, light):
    """vals: three (est, lb, ub) tuples top to bottom."""
    for (e, lb, ub), dy, st in zip(vals, (0.32, 0.0, -0.32), ("white", "half", "full")):
        ax.plot([lb, ub], [y + dy] * 2, color=color, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
        mfc = {"white": "white", "half": light, "full": color}[st]
        ax.plot([e], [y + dy], marker="o", ms=S.MS_CIRCLE, mfc=mfc, mec=color if st != "full" else "white",
                mew=S.MEW_HOLLOW if st != "full" else S.MEW, ls="none", zorder=3)


def key3(fig, labels, color, light):
    items = []
    for lab, st in zip(labels, ("white", "half", "full")):
        mfc = {"white": "white", "half": light, "full": color}[st]
        items.append(("o", mfc, color, S.MS_CIRCLE, lab, S.INK, "normal"))
    V.r5_key(fig, (fig.W - V.key_width(fig, items, gap=0.35)) / 2, 0.16, items, gap=0.35)


ARR = [("1–2 WFH days", "p1"), ("3–4 WFH days", "p2"), ("Fully remote", "p3"), ("Compressed week", "t2"),
       ("Staggered hours", "t1"), ("Job sharing", "l1"), ("Part-time", "l2")]
YS7 = [8.0, 7.0, 6.0, 4.4, 3.4, 1.8, 0.8]


def fig_size():
    """Pay by organisation size, PMEs (own organisation) and employers (firm): three size groups, seven arrangements."""
    name = "F_size"
    pm = pd.read_csv(MOM / "data" / "pme_by_size.csv")
    em = W.D[(W.D.side == "emp") & (W.D["sample"] == "main") & (W.D.split == "size")]
    SZ = (14.5, 6.4)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, a, S.FS_ROW) for a, _ in ARR)
    PX0, GAP = LX + 0.15, 0.7
    PW = (Wd - 0.5 - PX0 - GAP) / 2
    AY, AT = 1.35, H - 0.65
    YA_, YB_ = 0.1, 8.7

    def fy(v):
        return AY + (v - YA_) / (YB_ - YA_) * (AT - AY)
    for j, (title, color, light, xlim, ticks) in enumerate([("PMEs: own organisation", S.EMPLOYEE, S.EMPLOYEE_LIGHT, (-8, 30), [0, 10, 20, 30]),
                                                            ("Employers: firm", S.EMPLOYER, S.EMPLOYER_LIGHT, (-30, 80), [0, 25, 50, 75])]):
        ax = M.axes_cm(fig, PX0 + j * (PW + GAP), AY, PW, AT - AY)
        ax.set_xlim(*xlim)
        ax.set_ylim(YA_, YB_)
        S.ref_line(ax, 0, YA_, YB_)
        for (lab, it), y in zip(ARR, YS7):
            if j == 0:
                vals = [tuple(pm[(pm.group == g) & (pm["item"] == it)][["giveup", "lb", "ub"]].iloc[0]) for g in (1, 2, 3)]
            else:
                vals = [tuple(em[(em.group == g) & (em["item"] == it)][["giveup", "lb", "ub"]].iloc[0]) for g in (0, 1, 2)]
            draw3(ax, y, vals, color, light)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(S.RULE)
        ax.set_xticks(ticks)
        ax.set_xticklabels([str(t) for t in ticks[:-1]] + [f"{ticks[-1]}%"])
        ax.tick_params(axis="x", length=2.5, width=0.6, colors=S.RULE, labelcolor=S.MUTED, labelsize=S.FS_TICK)
        M.ftext(fig, PX0 + j * (PW + GAP) + PW / 2, AT + 0.08, title, ha="center", va="bottom", fontsize=S.FS_HEAD,
                fontweight="bold", color=color)
    for (lab, it), y in zip(ARR, YS7):
        M.ftext(fig, LX, fy(y), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    V.hline_cm(fig, 0.05, Wd - 0.05, fy(5.2), **S.SEP)
    V.hline_cm(fig, 0.05, Wd - 0.05, fy(2.6), **S.SEP)
    key3(fig, ["≤200 staff", "201–1,000", "1,001+"], S.MUTED, S.GREY_MID)
    V.outside(fig, name)
    return M.finish(fig, name, SZ)


def fig_role():
    """Employer pay cut by who answered the survey (owner / HR / line or hiring manager), seven arrangements."""
    name = "F_org_role"
    em = W.D[(W.D.side == "emp") & (W.D["sample"] == "main") & (W.D.split == "role")]
    SZ = (13.0, 5.8)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, a, S.FS_ROW) for a, _ in ARR)
    PX0 = LX + 0.15
    AY, AT = 1.35, H - 0.3
    YA_, YB_ = 0.1, 8.7

    def fy(v):
        return AY + (v - YA_) / (YB_ - YA_) * (AT - AY)
    ax = M.axes_cm(fig, PX0, AY, Wd - PX0 - 0.5, AT - AY)
    ax.set_xlim(-30, 85)
    ax.set_ylim(YA_, YB_)
    S.ref_line(ax, 0, YA_, YB_)
    for (lab, it), y in zip(ARR, YS7):
        vals = [tuple(em[(em.group == g) & (em["item"] == it)][["giveup", "lb", "ub"]].iloc[0]) for g in (0, 1, 2)]
        draw3(ax, y, vals, S.EMPLOYER, S.EMPLOYER_LIGHT)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(S.RULE)
    ax.set_xticks([0, 25, 50, 75])
    ax.set_xticklabels(["0", "25", "50", "75%"])
    ax.tick_params(axis="x", length=2.5, width=0.6, colors=S.RULE, labelcolor=S.MUTED, labelsize=S.FS_TICK)
    for (lab, it), y in zip(ARR, YS7):
        M.ftext(fig, LX, fy(y), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    V.hline_cm(fig, 0.05, Wd - 0.05, fy(5.2), **S.SEP)
    V.hline_cm(fig, 0.05, Wd - 0.05, fy(2.6), **S.SEP)
    key3(fig, ["Owner / C-suite", "HR", "Hiring manager"], S.EMPLOYER, S.EMPLOYER_LIGHT)
    V.outside(fig, name)
    return M.finish(fig, name, SZ)


if __name__ == "__main__":
    figs = {"F_use_att": fig_use_att, "F_wtp_att": fig_wtp_att, "F_org_splits": fig_org_overview, "F_org_other": lambda: fig_org_overview("F_org_other", "hiring"), "F_dominance": fig_dominance, "F_size": fig_size, "F_org_role": fig_role, "F_groups_diff": fig_groups_diff}
    for nm in sys.argv[1:] or list(figs):
        print("wrote", figs[nm]())
    for fl in dict.fromkeys(M.FLAGS):
        print("FLAG:", fl)
