"""fig_wtp -- the deck's WTP figures, both sides in ONE convention (pay given up; positive = pay cut).

PMEs: % of monthly pay they would give up for an arrangement.  Employers: % pay cut they would require of a candidate
who wants it (= minus the employer model's WTP).  Gap = employers' required cut minus PMEs' accepted cut (positive =
friction).  All main figures use ALL respondents (no panel exclusion, no dagger ranges) and show no equal-pay shares.

Reads data/wtp_deck.csv (scripts/build_wtp_data.py) and a few aggregate CSVs of MOM_presentation/data and mechanisms.
Style helpers (figstyle / fig_main / fig_v2) come from the professor's deck_support/scripts, READ ONLY (a build tree
made by make_build_tree.sh): set BUILD to that tree.  Figures go to OUTDIR (PDF + PNG).

usage: BUILD=/path/to/build OUTDIR=/path/to/figures python3 fig_wtp.py [name ...]
"""
import math
import os
import sys
from pathlib import Path

import pandas as pd

sys.dont_write_bytecode = True
MOM = Path(__file__).resolve().parents[1]
BUILD = Path(os.environ["BUILD"]).resolve()
sys.path.insert(0, str(BUILD / "deck_support" / "scripts"))

import figstyle as S  # noqa: E402

S.FIGDIR = Path(os.environ.get("OUTDIR", MOM / "overleaf_upload" / "figures"))
import fig_main as M  # noqa: E402
import fig_v2 as V  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

V.EB_TEXT = V.EB_TEXT          # (unused: this script reads no evidence-book strings)
D = pd.read_csv(MOM / "data" / "wtp_deck.csv")
GREY_D = V.GREY_D
HALO = M.HALO
SIZE = (13.0, 5.0)
V.SIZE.update({k: SIZE for k in ("F_org_wtp", "F_gap_m", "F_why_pmes", "F_where_r5", "F_groups_m", "F_emp_wtp", "F_landscape_m",
                                 "F_puzzle_r5", "F_barriers_r5")})


def get(side, item, sample="main", split="all", group=0, col="giveup"):
    q = D[(D.side == side) & (D["sample"] == sample) & (D.split == split) & (D.group == group) & (D["item"] == item)]
    if len(q) != 1:
        raise KeyError((side, item, sample, split, group, len(q)))
    r = q.iloc[0]
    return r if col is None else float(r[col])


def tri(side, item, **kw):
    r = get(side, item, col=None, **kw)
    return float(r.giveup), float(r.lb), float(r.ub)


def r0(x):
    return int(math.floor(x + 0.5))


def txt0(x):
    v = r0(x)
    return ("−" if v < 0 else "") + str(abs(v))


SIZES1 = {"F_emp_wtp": (13.0, 5.3), "F_org_wtp": (13.0, 5.3), "F_gap_m": (13.0, 5.1), "F_barriers_r5": (13.0, 4.9)}   # single-panel figures without a subtitle: taller


def new_fig(name):
    return M.new_fig(*SIZES1.get(name, SIZE))


def done(fig, name):
    V.outside(fig, name)
    return M.finish(fig, name, SIZES1.get(name, SIZE))


ROWS = [  # label, item, y (data units), hours-change row?
    ("Fully remote", "p3", 7.0, False), ("3–4 WFH days", "p2", 5.95, False),
    ("1–2 WFH days", "p1", 5.05, False), ("Compressed week", "t2", 4.15, False),
    ("Staggered hours", "t1", 3.25, False), ("Job sharing", "l1", 1.95, True), ("Part-time", "l2", 1.05, True)]
YA, YB = 0.55, 7.5


def nohead(*args, **kw):
    """the figures carry no subtitle: slide title and summary say what is shown; tick labels end in %"""
    return None


def frame(fig, labels, xl, xr, ticks, val_w=1.05, head_h=0.36, pad=0.15, bottom=0.55):
    W, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, t, S.FS_ROW) for t in labels)
    X0 = LX + pad
    EX = W - val_w
    X1 = EX - 0.30
    AY, AT = bottom, H - head_h
    ax = M.axes_cm(fig, X0, AY, X1 - X0, AT - AY)
    ax.set_xlim(xl, xr)
    ax.set_ylim(YA, YB)
    S.ref_line(ax, 0, YA, YB)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(S.RULE)
    S.pct_ticks(ax, ticks)

    def fy(y):
        return AY + (y - YA) / (YB - YA) * (AT - AY)
    return dict(LX=LX, X0=X0, X1=X1, EX=EX, AY=AY, AT=AT, ax=ax, fy=fy)


def vlabel(ax, x, y, txt, col, bold=True):
    """value label right next to the marker's CI end (5 pt gap)"""
    ax.annotate(txt, (x, y), xytext=(5, 0), textcoords="offset points", ha="left", va="center", fontsize=S.FS_VAL,
                color=col, fontweight="bold" if bold else "normal", path_effects=HALO, zorder=5)


def hours_note(fig, F):
    """small grey label above the separator line: the two rows below also change hours"""
    M.ftext(fig, fig.W - 0.05, F["fy"](2.6) + 0.04, "These also cut hours", ha="right", va="bottom",
            fontsize=S.FS_CAP, color=S.MUTED)


def ci_dot(ax, y, est, lb, ub, col, **kw):
    ax.plot([lb, ub], [y, y], color=col, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
    ax.plot([est], [y], marker="o", ms=S.MS_CIRCLE, mfc=col, mec="white", mew=S.MEW, ls="none", zorder=3, **kw)


# ----------------------------------------------------------------------------------------------------------------
# F_org_wtp (M-employers): pay cut employers would require, 7 arrangements, 95% CIs
# ----------------------------------------------------------------------------------------------------------------
def fig_org_wtp():
    name = "F_org_wtp"
    fig = new_fig(name)
    labels = [r[0] for r in ROWS]
    F = frame(fig, labels, -8, 68, [0, 20, 40, 60], val_w=0.35, bottom=0.60)
    nohead(fig, name, "Pay cut employers would require for each arrangement, % of pay")
    V.hline_cm(fig, 0.05, fig.W - 0.05, F["fy"](2.6), **S.SEP)
    for lab, item, y, load in ROWS:
        est, lb, ub = tri("emp", item)
        col = S.EMPLOYER
        ci_dot(F["ax"], y, est, lb, ub, col)
        vlabel(F["ax"], max(ub, est), y, txt0(est), col)
        M.ftext(fig, F["LX"], F["fy"](y), lab, ha="right", va="center", fontsize=S.FS_ROW,
                color=S.INK)
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# gap numbers (shared by the figure and the tables): employers' required cut minus PMEs' accepted cut
# ----------------------------------------------------------------------------------------------------------------
def gap_row(item, pme_item=None):
    pe, pl, pu = tri("pme", pme_item or item)
    ps = float(get("pme", pme_item or item, col="se"))
    ee, el, eu = tri("emp", item)
    es = float(get("emp", item, col="se"))
    g = ee - pe
    se = math.hypot(ps, es)
    return dict(pme=(pe, pl, pu), emp=(ee, el, eu), gap=g, lo=g - 1.96 * se, hi=g + 1.96 * se,
                p=math.erfc(abs(g / se) / math.sqrt(2)))


# ----------------------------------------------------------------------------------------------------------------
# F_gap_m (M-meet): dumbbell, PMEs' pay given up vs employers' required cut, with the gap
# ----------------------------------------------------------------------------------------------------------------
def fig_emp_wtp():
    name = "F_emp_wtp"
    fig = new_fig(name)
    labels = [r[0] for r in ROWS]
    F = frame(fig, labels, -5, 24, [0, 5, 10, 15, 20], val_w=0.35, bottom=0.60)
    ax = F["ax"]
    # no 'abroad' band: the title compares remote work with the other arrangements; the abroad range is on slide 4 and B-emp-benchmarks
    nohead(fig, name, "Pay PMEs would give up for each arrangement, % of monthly pay")
    V.hline_cm(fig, 0.05, fig.W - 0.05, F["fy"](2.6), **S.SEP)
    for i, (lab, item, y, load) in enumerate(ROWS):
        est, lb, ub = tri("pme", item)
        col = S.EMPLOYEE
        ci_dot(ax, y, est, lb, ub, col)
        vlabel(ax, max(ub, est), y, txt0(est), col)
        M.ftext(fig, F["LX"], F["fy"](y), labels[i], ha="right", va="center", fontsize=S.FS_ROW,
                color=S.INK)
    return done(fig, name)


def fig_gap_m():
    name = "F_gap_m"
    fig = new_fig(name)
    labels = ["Fully remote", "3–4 WFH days", "1–2 WFH days", "Compressed week", "Staggered hours",
              "Job sharing / reduced load", "Part-time"]
    F = frame(fig, labels, -17, 52, [0, 20, 40], val_w=0.35, bottom=0.60)
    ax = F["ax"]
    ax.set_xticks([0, 20, 40])
    ax.set_xticklabels(["0", "20", "40"])      # points of pay, not %
    V.hline_cm(fig, 0.05, fig.W - 0.05, F["fy"](2.6), **S.SEP)
    for (lab0, item, y, load), lab in zip(ROWS, labels):
        g = gap_row(item)
        ci_dot(ax, y, g["gap"], g["lo"], g["hi"], S.AGREE)
        vlabel(ax, max(g["hi"], g["gap"]), y, txt0(g["gap"]), S.AGREE)
        M.ftext(fig, F["LX"], F["fy"](y), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# two-series row chart helper (career belief) ---------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
def fig_why_pmes():
    name = "F_why_pmes"
    levels = [("p1", "1–2 WFH days"), ("p2", "3–4 WFH days"), ("p3", "Fully remote"),
              ("t2", "Compressed week")]
    fig = new_fig(name)
    W, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, ln, S.FS_ROW) for lv in levels for ln in lv[1].split("\n"))
    X0 = LX + 0.15
    X1 = W - 0.35
    XL, XR = -9, 26
    YB0, YB1 = 1.15, H - 0.30
    ax = M.axes_cm(fig, X0, YB0, X1 - X0, YB1 - YB0)
    ax.set_xlim(XL, XR)
    ax.set_ylim(YB0, YB1)
    S.ref_line(ax, 0, YB0, YB1)
    top, bot = YB1 - 0.36, YB0 + 0.36
    pitch = (top - bot) / 3.2
    rows_y = [top, top - pitch, top - 2.1 * pitch, bot]
    cols = {1: GREY_D, 0: S.EMPLOYEE}
    DY = {1: 0.15, 0: -0.15}
    ns = {}
    for (it, lab), y in zip(levels, rows_y):
        M.ftext(fig, LX, y, lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK, linespacing=1.0)
        pts = []
        for g in (1, 0):
            q = D[(D.side == "pme") & (D.split == "career") & (D.group == g) & (D["item"] == it)].iloc[0]
            ns[g] = int(q.n)
            ax.plot([q.lb, q.ub], [y + DY[g]] * 2, color=cols[g], lw=S.CI_LW, solid_capstyle="butt", zorder=2)
            pts.append((q.giveup, q.lb, q.ub, g))
        for p, lb, ub, g in pts:
            other = [q for q in pts if q[3] != g][0]
            left = g == 1
            ax.plot([p], [y + DY[g]], marker="o", ms=S.MS_CIRCLE, mfc=cols[g], mec="white", mew=S.MEW, ls="none",
                    zorder=4 if g == 0 else 3)
            xt = (min(lb, other[1]) - 0.8) if left else (max(ub, other[2]) + 0.8)
            ax.text(xt, y + DY[g], txt0(p), ha="right" if left else "left", va="center", fontsize=S.FS_VAL,
                    color=cols[g], fontweight="bold", path_effects=HALO, zorder=5)
    keys = [("o", GREY_D, GREY_D, S.MS_CIRCLE, "Expect a penalty", GREY_D, "bold"),
            ("o", S.EMPLOYEE, S.EMPLOYEE, S.MS_CIRCLE, "Neutral or disagree", S.EMPLOYEE, "bold")]
    V.r5_key(fig, (W - V.key_width(fig, keys)) / 2, 0.16, keys)
    nohead(fig, name, "Pay PMEs would give up, % of monthly pay")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(S.RULE)
    S.pct_ticks(ax, [0, 10, 20])
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# F_where_r5 (M-where): employers' required cut, by role need and creativity concern
# ----------------------------------------------------------------------------------------------------------------
def fig_where_r5():
    name = "F_where_r5"
    fig = new_fig(name)
    W, H = fig.W, fig.H
    levels = [("p1", "1\u20132 WFH days"), ("p2", "3\u20134 WFH days"), ("p3", "Fully remote")]
    panels = [("On-site presence needed", "physical", "Most roles", "Some or few roles"),
              ("Creativity concern", "creat", "Concern", "No concern")]
    LX = 0.05 + max(V.tw_cm(fig, t, S.FS_ROW) for _, t in levels)
    GAP = 0.45
    PW = (W - 0.05 - LX - 0.15 - GAP) / 2
    AY, AT = 1.40, H - 0.62
    XL, XR = -15, 108
    YA_, YB_ = 0.0, 3.0

    def fy(v):
        return AY + (v - YA_) / (YB_ - YA_) * (AT - AY)
    nohead(fig, name, "Pay cut employers would require, % of pay")
    for j, (title, split, lab_f, lab_o) in enumerate(panels):
        x0 = LX + 0.15 + j * (PW + GAP)
        ax = M.axes_cm(fig, x0, AY, PW, AT - AY)
        ax.set_xlim(XL, XR)
        ax.set_ylim(YA_, YB_)
        S.ref_line(ax, 0, YA_, YB_)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(S.RULE)
        S.pct_ticks(ax, [0, 25, 50, 75])
        M.ftext(fig, x0 + PW / 2, AT + 0.10, title, ha="center", va="bottom", fontsize=S.FS_HEAD, color=S.INK,
                fontweight="bold")
        ns = {}
        for (it, _), yc in zip(levels, (2.5, 1.5, 0.5)):
            for g, focal, dy in ((0, True, 0.2), (1, False, -0.2)):
                q = D[(D.side == "emp") & (D.split == split) & (D.group == g) & (D["item"] == it)].iloc[0]
                ns[g] = int(q.n)
                y = yc + dy
                ax.plot([q.lb, q.ub], [y, y], color=S.EMPLOYER, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
                ax.plot([q.giveup], [y], marker="D", ms=S.MS_DIAMOND, mfc=S.EMPLOYER if focal else "white",
                        mec="white" if focal else S.EMPLOYER, mew=S.MEW if focal else S.MEW_HOLLOW, ls="none", zorder=3)
                vlabel(ax, max(q.ub, q.giveup), y, txt0(q.giveup), S.EMPLOYER)
        keys = [("D", S.EMPLOYER, S.EMPLOYER, S.MS_DIAMOND, f"{lab_f} (n = {ns[0]})", S.INK, "normal"),
                ("D", "white", S.EMPLOYER, S.MS_DIAMOND, f"{lab_o} (n = {ns[1]})", S.INK, "normal")]
        V.r5_key(fig, x0 - 0.1, 0.72, keys[:1])
        V.r5_key(fig, x0 - 0.1, 0.30, keys[1:])
    for (it, lab), yc in zip(levels, (2.5, 1.5, 0.5)):
        M.ftext(fig, LX, fy(yc), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# F_groups_m (M-groups): PME WTP by gender, age and caregiving
# ----------------------------------------------------------------------------------------------------------------
def fig_groups_m():
    name = "F_groups_m"
    levels = [("p1", "1–2 WFH days"), ("p2", "3–4 WFH days"), ("p3", "Fully remote")]
    splits = [("gender", "Men", "Women"), ("age", "Under 40", "Aged 40+"), ("care_any", "Not caregivers", "Caregivers")]
    rows = [("main", 0, "All PMEs (1,020)")]
    for sp, a, b in splits:
        rows += [(sp, 0, a), (sp, 1, b)]
    ys = [9.0, 7.6, 6.8, 5.4, 4.6, 3.2, 2.4]
    fig = new_fig(name)
    W, H = fig.W, fig.H
    lab_w = max(V.tw_cm(fig, r[2], S.FS_ROW, "bold" if r[0] == "main" else "normal") for r in rows)
    LX = 0.05 + lab_w
    PCW = 0.0   # no test column: the intervals carry the comparison
    PX0, GAP = LX + 0.15, 0.30
    PW = (W - 0.05 - PCW - 0.30 - PX0 - 2 * GAP) / 3
    AY, AT = 1.15, H - 0.62
    YA_, YB_ = 1.95, 9.50

    def fy(y):
        return AY + (y - YA_) / (YB_ - YA_) * (AT - AY)
    for j, (it, title) in enumerate(levels):
        ax = M.axes_cm(fig, PX0 + j * (PW + GAP), AY, PW, AT - AY)
        ax.set_xlim(-3, 30)
        ax.set_ylim(YA_, YB_)
        S.ref_line(ax, 0, YA_, YB_)
        for (sp, g, lab), y in zip(rows, ys):
            if sp == "main":
                est, lb, ub = tri("pme", it)
            else:
                q = D[(D.side == "pme") & (D.split == sp) & (D.group == g) & (D["item"] == it)].iloc[0]
                est, lb, ub = q.giveup, q.lb, q.ub
            filled = sp == "main" or g == 1
            ax.plot([lb, ub], [y, y], color=S.EMPLOYEE, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
            ax.plot([est], [y], marker="o", ms=S.MS_CIRCLE, mfc=S.EMPLOYEE if filled else "white",
                    mec="white" if filled else S.EMPLOYEE, mew=S.MEW if filled else S.MEW_HOLLOW, ls="none", zorder=3)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(S.RULE)
        S.pct_ticks(ax, [0, 10, 20, 30])
        M.ftext(fig, PX0 + j * (PW + GAP) + PW / 2, AT + 0.10, title, ha="center", va="bottom", fontsize=S.FS_HEAD,
                fontweight="bold", color=S.EMPLOYEE)
    for yy in (8.3, 6.1, 3.9):
        V.hline_cm(fig, 0.05, W - 0.05, fy(yy), **S.SEP)
    for (sp, g, lab), y in zip(rows, ys):
        M.ftext(fig, LX, fy(y), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK,
                fontweight="bold" if sp == "main" else "normal")
    nohead(fig, name, "Pay PMEs would give up, % of monthly pay")
    keys = [("o", "white", S.EMPLOYEE, S.MS_CIRCLE, "first group listed", S.INK, "normal"),
            ("o", S.EMPLOYEE, S.EMPLOYEE, S.MS_CIRCLE, "second", S.INK, "normal")]
    kw_ = V.key_width(fig, keys, gap=0.35)
    V.r5_key(fig, (W - kw_) / 2, 0.16, keys, gap=0.35)
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# F_landscape_m (M-descriptive): all respondents, no dagger ranges
# ----------------------------------------------------------------------------------------------------------------
def fig_landscape_m():
    name = "F_landscape_m"
    items = [("Remote work (WFH at least 1 day a week)", "WFH \u22651 day a week"), ("Staggered hours", "Staggered hours"),
             ("Compressed workweek", "Compressed week"), ("Job sharing", "Job sharing"),
             ("Part-time / reduced hours", "Part-time")]

    def u(block, item, grp="Employed"):
        r, _ = M.one("emp_fwa_use.csv", block=block, sample="all", group=grp, item=item)
        return float(r["share"]), int(r["n"])
    fig = new_fig(name)
    W, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, it[1], S.FS_ROW) for it in items)
    BX0, BW = LX + 0.15, 3.70
    _, n_a = u("use", "Any of the five FWAs")
    M.ftext(fig, 0.05, H - 0.04, f"Employed PMEs (n = {n_a:,})", ha="left", va="top", fontsize=S.FS_HEAD,
            color=S.EMPLOYEE, fontweight="bold")
    M.ftext(fig, 0.05, H - 0.47, "% using each arrangement", ha="left", va="top", fontsize=S.FS_AXIS, color=S.INK)
    top, bh = H - 1.30, 0.38
    pitch = (top - 0.40) / 4
    for i, (item, lab) in enumerate(items):
        y = top - i * pitch
        M.ftext(fig, LX, y, lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
        v, _ = u("use", item)
        fig.add_artist(Rectangle((BX0 / W, (y - bh / 2) / H), v / 100 * BW / W, bh / H, transform=fig.transFigure,
                                 fc=S.EMPLOYEE, ec="none", lw=0))
        M.ftext(fig, BX0 + v / 100 * BW + 0.14, y, f"{r0(v)}%", ha="left", va="center", fontsize=S.FS_VAL,
                color=S.EMPLOYEE, fontweight="bold")
    V.vline_cm(fig, BX0, top - 4 * pitch - bh / 2 - 0.06, top + bh / 2 + 0.06, color=S.RULE, lw=0.7)
    RX0 = 8.05
    M.ftext(fig, RX0, H - 0.04, "Employers (n = 465)", ha="left", va="top", fontsize=S.FS_HEAD, color=S.EMPLOYER,
            fontweight="bold")
    M.ftext(fig, RX0, H - 0.47, "% offering it to PMEs", ha="left", va="top", fontsize=S.FS_AXIS, color=S.INK)
    ritems = [("Remote work (ad hoc, scheduled or remote-first)", "WFH"), ("Staggered hours", "Staggered hours"),
              ("Compressed workweek", "Compressed week"), ("Job sharing", "Job sharing"),
              ("Part-time / reduced hours", "Part-time")]
    RL = RX0 + 0.05 + max(V.tw_cm(fig, t, S.FS_ROW) for _, t in ritems)
    RB0, RBW = RL + 0.15, 1.15
    for i, (item, lab) in enumerate(ritems):
        y = top - i * pitch
        v = float(M.one("org_fwa.csv", block="offered_ticked", sample="all", group="All employer respondents",
                       item=item)[0]["share"])
        M.ftext(fig, RL, y, lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
        fig.add_artist(Rectangle((RB0 / W, (y - bh / 2) / H), v / 100 * RBW / W, bh / H, transform=fig.transFigure,
                                 fc=S.EMPLOYER, ec="none", lw=0))
        M.ftext(fig, RB0 + v / 100 * RBW + 0.14, y, f"{r0(v)}%", ha="left", va="center", fontsize=S.FS_VAL,
                color=S.EMPLOYER, fontweight="bold")
    V.vline_cm(fig, RB0, top - 4 * pitch - bh / 2 - 0.06, top + bh / 2 + 0.06, color=S.RULE, lw=0.7)
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# F_puzzle_r5 (M-puzzle): four fact cards, no equal-pay share, no dagger
# ----------------------------------------------------------------------------------------------------------------
def fig_sample_m():
    name = "F_sample_m"
    SZ = (13.0, 6.0)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    oc = pd.read_csv(MOM / "data" / "org_composition.csv")

    def share(block, item):
        r = oc[(oc.block == block) & (oc["sample"] == "all") & (oc["item"] == item)].iloc[0]
        return float(r.share)
    PAD, BAR = S.CARD_PAD_CM, S.CARD_BAR_CM
    CY0, CY1 = 2.95, H - 0.04
    CWD = (Wd - 0.10 - 0.30) / 2
    cards = [(0.05, S.EMPLOYEE, "1,020", "PMEs", ["Singapore citizens and PRs", "in or seeking PME roles"],
              "Fielded 4\u201321 Aug 2026", "Online panels"),
             (0.05 + CWD + 0.30, S.EMPLOYER, "465", "employer respondents", ["People involved in PME hiring", "or manpower decisions"],
              "Fielded 12 Aug\u201321 Oct 2026", "Online panel")]
    for x, col, big, unit, who, when, pan in cards:
        fig.add_artist(Rectangle((x / Wd, CY0 / H), CWD / Wd, (CY1 - CY0) / H, transform=fig.transFigure, fc=S.CARD_FILL, ec="none", lw=0))
        fig.add_artist(Rectangle((x / Wd, (CY1 - BAR) / H), CWD / Wd, BAR / H, transform=fig.transFigure, fc=col, ec="none", lw=0))
        xt = x + PAD + 0.05
        tb = M.ftext(fig, xt, CY1 - BAR - PAD - 0.55, big, ha="left", va="baseline", fontsize=S.FS_BIG, color=col, fontweight="bold")
        xb_ = fig.transFigure.inverted().transform((tb.get_window_extent(renderer=fig.canvas.get_renderer()).x1, 0))[0] * Wd
        M.ftext(fig, xb_ + 0.12, CY1 - BAR - PAD - 0.55, unit, ha="left", va="baseline", fontsize=S.CARD_HEAD_FS, color=col, fontweight="bold")
        M.ftext(fig, xt, CY1 - BAR - PAD - 0.80, "\n".join(who), ha="left", va="top", fontsize=S.FS_ROW, color=S.INK, linespacing=1.2)
        M.ftext(fig, xt, CY0 + PAD + 0.45, f"{pan}, unweighted", ha="left", va="baseline", fontsize=S.FS_ROW, color=S.INK, fontweight="bold")
        M.ftext(fig, xt, CY0 + PAD, when, ha="left", va="baseline", fontsize=S.FS_ROW, color=S.MUTED)
    M.ftext(fig, 0.05, 1.95, "Employer respondents' firms, by staff size", ha="left", va="center", fontsize=S.FS_HEAD,
            color=S.EMPLOYER, fontweight="bold")
    BX0, BX1, BY, BH = 0.05, Wd - 0.05, 0.18, 0.70
    segs = [("\u2264200 staff", "200 or fewer", "firm_size3", S.EMPLOYER_LIGHT), ("201\u20131,000", "201-1,000", "firm_size3", S.GREY_MID),
            ("1,001+", "1,001 or more", "firm_size3", S.MUTED)]
    x = BX0
    for lab, it, blk, c in segs:
        v = share(blk, it)
        w = v / 100 * (BX1 - BX0)
        fig.add_artist(Rectangle((x / Wd, BY / H), w / Wd, BH / H, transform=fig.transFigure, fc=c, ec="white", lw=1.0))
        if lab.startswith("\u2264200"):
            yb = BY + BH + 0.16
            V.hline_cm(fig, x + 0.02, x + w - 0.02, yb, color=S.INK, lw=0.7)
            for xx in (x + 0.02, x + w - 0.02):
                V.vline_cm(fig, xx, yb - 0.10, yb, color=S.INK, lw=0.7)
            M.ftext(fig, x + w / 2, yb + 0.08, f"{lab}: {r0(v)}%", ha="center", va="bottom", fontsize=S.FS_TICK,
                    color=S.INK, fontweight="bold")
            w200 = (x, w)
        else:
            M.ftext(fig, x + w / 2, BY + BH / 2, f"{lab}: {r0(v)}%", ha="center", va="center", fontsize=S.FS_TICK,
                    color="white" if c == S.MUTED else S.INK, fontweight="bold")
        x += w
    v50 = share("firm_size3", "50 or fewer")
    w50 = v50 / 100 * (BX1 - BX0)
    fig.add_artist(Rectangle((BX0 / Wd, BY / H), w50 / Wd, BH / H, transform=fig.transFigure, fc=S.EMPLOYER, ec="white", lw=1.0))
    M.ftext(fig, BX0 + w50 / 2, BY + BH / 2, f"\u226450: {r0(v50)}%", ha="center", va="center", fontsize=S.FS_TICK, color="white", fontweight="bold")
    M.ftext(fig, BX0 + w50 + (w200[1] - w50) / 2, BY + BH / 2, "51\u2013200", ha="center", va="center", fontsize=S.FS_TICK, color=S.INK)
    V.outside(fig, name)
    return M.finish(fig, name, SZ)


def fig_puzzle_r5():
    import fig_r5 as F5
    name = "F_puzzle_r5"
    CP = "compressed_puzzle.csv"
    ov, _ = V.mone(CP, sec="A", analysis="Employers offering a compressed week", sample="all",
                   item="Offers (ticked QID15 or typical PME schedule QID61)")
    of = float(ov["est"])

    def pol(group):
        hits = [r for r in V.mrows(CP) if r["sec"] == "A" and r["analysis"].startswith("Share offering")
                and r["split"] == "policy" and r["group"] == group and r["metric"] == "share"]
        return float(hits[0]["est"])
    pw, pn = pol("Written FWA policy"), pol("No written FWA policy")
    ta, _ = V.mone(CP, sec="B", analysis="Compressed week: overall", sample="all",
                   group="Employed PMEs with access (adjusted)", item="Take-up: uses it")
    tk = float(ta["est"])
    pme, emp = tri("pme", "t2"), tri("emp", "t2")
    fig = M.new_fig(*SIZE)
    H, W = fig.H, fig.W
    PAD, BAR = S.CARD_PAD_CM, S.CARD_BAR_CM
    gx, gy = 0.20, 0.16
    cw = (W - 0.10 - gx) / 2
    FY0 = 0.04
    ch = (H - 0.04 - FY0 - gy) / 2
    cells = [(0.05, FY0 + ch + gy), (0.05 + cw + gx, FY0 + ch + gy), (0.05, FY0), (0.05 + cw + gx, FY0)]
    NB = 2.15

    def frame(i, head, col):
        x, y0 = cells[i]
        F5.card(fig, x, y0, cw, ch, col)
        M.ftext(fig, x + PAD, y0 + ch - BAR - 0.13, head, ha="left", va="top", fontsize=F5.FS_CARD, color=col,
                fontweight="bold")
        return x, x + PAD + NB + 0.15, x + cw - PAD, y0 + ch - 0.88, y0 + (ch - 0.58) / 2 + 0.02

    def number(x, yb, main, col, sub=None, sub_col=None):
        x += PAD
        if sub is None:
            M.ftext(fig, x + NB / 2, yb, main, ha="center", va="center", fontsize=S.FS_BIG, color=col, fontweight="bold")
            return
        M.ftext(fig, x + NB / 2, yb + 0.20, main, ha="center", va="center", fontsize=S.FS_BIG, color=col,
                fontweight="bold")
        M.ftext(fig, x + NB / 2, yb - 0.62, sub, ha="center", va="baseline", fontsize=S.FS_DAG_BIG, color=sub_col,
                fontweight="bold")

    def desc(xr0, ytop, s):
        M.ftext(fig, xr0, ytop, s, ha="left", va="top", fontsize=F5.FS_LAB, color=S.INK, linespacing=1.15)
    # card 1: both sides, pay (0-20% scale)
    x, xr0, xr1, yt, yb = frame(0, "Both sides: about the same", S.EMPLOYEE)
    number(x, yb, f"{r0(pme[0])}%", S.EMPLOYEE, f"vs {r0(emp[0])}%", S.EMPLOYER)
    for yy, v, col in ((yt + 0.12, pme[0], S.EMPLOYEE), (yt - 0.04, emp[0], S.EMPLOYER)):
        fx = F5.track(fig, xr0, yy, xr1 - xr0, h=0.13)
        F5.bar(fig, fx(0), fx(v * 5), yy, col, h=0.13)
    for p_, s_, ha in ((0, "0", "left"), (100, "20%", "right")):
        M.ftext(fig, xr0 + (xr1 - xr0) * p_ / 100, yt - 0.04 - 0.065 - 0.05, s_, ha=ha, va="top", fontsize=S.FS_NOTE,
                color=S.MUTED)
    desc(xr0, yt - 0.50, "of pay: PMEs give up\nvs employers require")
    # card 2
    x, xr0, xr1, yt, yb = frame(1, "Few firms offer it", S.EMPLOYER)
    number(x, yb, f"1 in {round(100 / of)}", S.EMPLOYER, f"{r0(of)}%", S.EMPLOYER)
    fx = F5.track(fig, xr0, yt, xr1 - xr0)
    F5.bar(fig, fx(0), fx(of), yt, S.EMPLOYER)
    F5.track_ends(fig, fx, yt)
    desc(xr0, yt - 0.50, "of surveyed firms offer\nit to PMEs")
    # card 3
    x, xr0, xr1, yt, yb = frame(2, "Goes with a written FWA policy", S.EMPLOYER)
    number(x, yb, f"{pw:.1f}%", S.EMPLOYER, f"vs {pn:.1f}%", GREY_D)
    fx = F5.track(fig, xr0, yt + 0.12, xr1 - xr0, h=0.13)
    F5.bar(fig, fx(0), fx(pw), yt + 0.12, S.EMPLOYER, h=0.13)
    fx2 = F5.track(fig, xr0, yt - 0.04, xr1 - xr0, h=0.13)
    F5.bar(fig, fx2(0), fx2(pn), yt - 0.04, GREY_D, h=0.13)
    F5.track_ends(fig, fx2, yt - 0.04, h=0.13)
    desc(xr0, yt - 0.50, "of firms with / without a\nwritten policy offer it")
    # card 4
    x, xr0, xr1, yt, yb = frame(3, "Take-up where available", S.EMPLOYEE)
    number(x, yb, "1 in 3", S.EMPLOYEE, f"{r0(tk)}%", S.EMPLOYEE)
    fx = F5.track(fig, xr0, yt, xr1 - xr0)
    F5.bar(fig, fx(0), fx(tk), yt, S.EMPLOYEE)
    F5.track_ends(fig, fx, yt)
    desc(xr0, yt - 0.50, "of PMEs with access\nuse it")
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# F_barriers_r5 (M-barriers): all respondents, single values
# ----------------------------------------------------------------------------------------------------------------
def fig_barriers_r5():
    """M-barriers: by job level, what PMEs give up for WFH (three levels) next to familiarity with the Guidelines."""
    import fig_r5 as F5
    name = "F_barriers_r5"
    fam = "Familiar (aware and understand key provisions)"
    LV = [("Junior professionals", "Junior professional", "Role: Junior professional / specialist"),
          ("Middle management", "Middle management", "Role: Middle management"),
          ("Senior management", "Senior management", "Role: Senior management")]
    aware = [float(M.one("emp_tgfwar.csv", block="by_role", sample="all", group=g, item=fam)[0]["share"]) for _, _, g in LV]
    import pandas as pd
    acc = pd.read_csv(MOM / "data" / "pme_level_access.csv").set_index("level")["avail_any"]
    avail = [float(acc[i]) for i in (1, 2, 3)]
    ITEMS = [("p12", "1\u20132 days", "#9DB4D0"), ("p34", "3\u20134 days", "#5C7FAE"), ("remote", "Fully remote", S.EMPLOYEE)]

    def wtp(level, item):
        # junior and middle from the junior-vs-middle pair; senior from the junior-vs-senior pair
        if level == 2:
            r = M.one("dce_emp_het.csv", block="pairwise", split="level", group_a="Junior professional", group_b="Senior management", item=item)[0]
            return float(r["wtp_b"])
        r = M.one("dce_emp_het.csv", block="pairwise", split="level", group_a="Junior professional", group_b="Middle management", item=item)[0]
        return float(r["wtp_a" if level == 0 else "wtp_b"])
    fig = M.new_fig(*SIZE)
    H, W = fig.H, fig.W
    gap = 0.30
    cw = (W - 0.10 - gap) / 2
    CY0, CY1 = 0.04, H - 0.05
    LW = max(V.tw_cm(fig, lab, F5.FS_ROW) for lab, _, _ in LV)
    LEFT = [("FWA available", "#9DB4D0"), ("Know the Guidelines", S.EMPLOYEE)]
    heads = [("Access and awareness", "Share of employed PMEs"),
             ("Pay given up for WFH", "% of monthly pay")]
    for k, (hd, sub) in enumerate(heads):
        x = 0.05 + k * (cw + gap)
        F5.card(fig, x, CY0, cw, CY1 - CY0, S.EMPLOYEE)
        M.ftext(fig, x + 0.25, CY1 - S.CARD_BAR_CM - 0.13, hd, ha="left", va="top", fontsize=F5.FS_CARD, color=S.EMPLOYEE,
                fontweight="bold")
        M.ftext(fig, x + 0.25, CY1 - S.CARD_BAR_CM - 0.62, sub, ha="left", va="top", fontsize=F5.FS_LAB, color=S.MUTED)
        for lv, (lab, _, _) in enumerate(LV):
            yc = CY1 - S.CARD_BAR_CM - 1.75 - lv * 0.95
            M.ftext(fig, x + 0.25, yc, lab, ha="left", va="center", fontsize=F5.FS_ROW, color=S.INK)
            tx0 = x + 0.25 + LW + 0.20
            if k == 0:
                tw = x + cw - 0.25 - 1.0 - tx0
                for m_, (v, col) in enumerate(((avail[lv], LEFT[0][1]), (aware[lv], LEFT[1][1]))):
                    yy = yc + 0.135 - m_ * 0.27
                    fx = F5.track(fig, tx0, yy, tw, h=0.17)
                    F5.bar(fig, fx(0), fx(v), yy, col, h=0.17)
                    M.ftext(fig, tx0 + tw + 0.12, yy, f"{r0(v)}%", ha="left", va="center", fontsize=S.FS_VAL - 1,
                            color=S.EMPLOYEE, fontweight="bold")
            else:
                tw = x + cw - 0.25 - 0.8 - tx0
                for m_, (it, il, col) in enumerate(ITEMS):
                    yy = yc + 0.27 - m_ * 0.27
                    v = wtp(lv, it)
                    fx = F5.track(fig, tx0, yy, tw, h=0.17)
                    F5.bar(fig, fx(0), fx(max(v, 0) / 25.0 * 100), yy, col, h=0.17)
                    M.ftext(fig, tx0 + tw + 0.12, yy, f"{r0(v)}", ha="left", va="center", fontsize=S.FS_VAL - 1, color=S.EMPLOYEE,
                            fontweight="bold")
    # legend of the right card, at the bottom of the figure
    for x, ky, items in ((0.05 + 0.25, CY0 + 0.30, [(None, il, col) for il, col in LEFT]),
                         (0.05 + cw + gap + 0.25, CY0 + 0.30, ITEMS)):
        for it, il, col in items:
            fig.add_artist(Rectangle((x / W, (ky - 0.07) / H), 0.22 / W, 0.14 / H, transform=fig.transFigure, facecolor=col,
                                     edgecolor="none"))
            M.ftext(fig, x + 0.32, ky, il, ha="left", va="center", fontsize=F5.FS_LAB, color=S.INK)
            x += 0.32 + V.tw_cm(fig, il, F5.FS_LAB) + 0.25
    return done(fig, name)


FIGS = {"F_emp_wtp": fig_emp_wtp, "F_org_wtp": fig_org_wtp, "F_gap_m": fig_gap_m, "F_why_pmes": fig_why_pmes, "F_where_r5": fig_where_r5,
        "F_groups_m": fig_groups_m,
        "F_landscape_m": fig_landscape_m, "F_sample_m": fig_sample_m, "F_puzzle_r5": fig_puzzle_r5, "F_barriers_r5": fig_barriers_r5}

if __name__ == "__main__":
    import warnings
    warnings.simplefilter("default")
    names = sys.argv[1:] or list(FIGS)
    for nm in names:
        print("wrote", FIGS[nm]())
    for fl in dict.fromkeys(M.FLAGS):
        print("FLAG:", fl)
