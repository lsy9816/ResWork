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
V.SIZE.update({k: SIZE for k in ("F_org_wtp", "F_gap_m", "F_why_pmes", "F_where_r5", "F_groups_m", "F_landscape_m",
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


def new_fig(name):
    return M.new_fig(*SIZE)


def done(fig, name):
    V.outside(fig, name)
    return M.finish(fig, name, SIZE)


ROWS = [  # label, item, y (data units), hours-change row?
    ("Fully remote", "p3", 7.0, False), ("3–4 WFH days", "p2", 5.95, False),
    ("1–2 WFH days", "p1", 5.05, False), ("Compressed week", "t2", 4.15, False),
    ("Staggered hours", "t1", 3.25, False), ("Job sharing*", "l1", 1.95, True), ("Part-time*", "l2", 1.05, True)]
YA, YB = 0.55, 7.5


def frame(fig, labels, xl, xr, ticks, val_w=1.05, head_h=0.86, pad=0.15):
    W, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, t, S.FS_ROW) for t in labels)
    X0 = LX + pad
    EX = W - val_w
    X1 = EX - 0.30
    AY, AT = 0.55, H - head_h
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
    F = frame(fig, labels, -8, 64, [0, 20, 40, 60])
    V.head(fig, name, "Pay cut employers would require for each arrangement, % of pay")
    V.hline_cm(fig, 0.05, fig.W - 0.05, F["fy"](2.6), **S.SEP)
    for lab, item, y, load in ROWS:
        est, lb, ub = tri("emp", item)
        col = S.MUTED if load else S.EMPLOYER
        ci_dot(F["ax"], y, est, lb, ub, col)
        M.ftext(fig, F["EX"], F["fy"](y), txt0(est), ha="left", va="center", fontsize=S.FS_VAL, color=col,
                fontweight="normal" if load else "bold")
        M.ftext(fig, F["LX"], F["fy"](y), lab, ha="right", va="center", fontsize=S.FS_ROW,
                color=S.MUTED if load else S.INK)
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
def fig_gap_m():
    name = "F_gap_m"
    fig = new_fig(name)
    labels = ["Fully remote", "3–4 WFH days", "1–2 WFH days", "Compressed week", "Staggered hours",
              "Job sharing / reduced load*", "Part-time*"]
    F = frame(fig, labels, -4, 62, [0, 20, 40, 60], val_w=1.35)
    ax = F["ax"]
    keys = [("o", S.EMPLOYEE, S.EMPLOYEE, S.MS_CIRCLE, "PMEs would give up", S.EMPLOYEE, "bold"),
            ("o", S.EMPLOYER, S.EMPLOYER, S.MS_CIRCLE, "Employers would require", S.EMPLOYER, "bold")]
    V.r5_key(fig, F["EX"] - 0.25 - V.key_width(fig, keys), fig.H - 0.64, keys)
    V.head(fig, name, "Pay given up vs pay cut required, % of pay")
    V.hline_cm(fig, 0.05, fig.W - 0.05, F["fy"](2.6), **S.SEP)
    M.ftext(fig, F["EX"], F["AT"] + 0.10, "Gap", ha="left", va="bottom", fontsize=S.FS_HEAD, color=S.INK,
            fontweight="bold")
    for (lab0, item, y, load), lab in zip(ROWS, labels):
        g = gap_row(item, "p3own" if item == "p3" else None)
        pe, ee = g["pme"][0], g["emp"][0]
        ax.plot([pe, ee], [y, y], color=S.RULE, lw=2.4, solid_capstyle="butt", zorder=1)
        ax.plot([pe], [y], marker="o", ms=S.MS_CIRCLE, mfc=S.EMPLOYEE, mec="white", mew=S.MEW, ls="none", zorder=3)
        ax.plot([ee], [y], marker="o", ms=S.MS_CIRCLE, mfc=S.EMPLOYER, mec="white", mew=S.MEW, ls="none", zorder=3)
        overlap = g["lo"] <= 0 <= g["hi"]
        M.ftext(fig, F["EX"], F["fy"](y), "overlap" if overlap else txt0(g["gap"]), ha="left", va="center",
                fontsize=S.FS_VAL if not overlap else S.FS_ROW, color=S.MUTED if overlap else S.INK,
                fontweight="normal" if overlap else "bold")
        M.ftext(fig, F["LX"], F["fy"](y), lab, ha="right", va="center", fontsize=S.FS_ROW,
                color=S.MUTED if load else S.INK)
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# two-series row chart helper (career belief) ---------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
def fig_why_pmes():
    name = "F_why_pmes"
    levels = [("p1", "1–2 WFH days"), ("p2", "3–4 WFH days"), ("p3m", "Fully remote\n(vs 15–45 min commute)"),
              ("t2", "Compressed week")]
    fig = new_fig(name)
    W, H = fig.W, fig.H
    LX = 0.05 + max(V.tw_cm(fig, ln, S.FS_ROW) for lv in levels for ln in lv[1].split("\n"))
    ANN = ("Groups differ", "p = .002", "No difference", "detected, p = .15")
    PW_ = max(V.tw_cm(fig, t_, S.FS_TICK) for t_ in ANN)
    X0 = LX + 0.15
    X1 = W - 0.05 - PW_ - 0.30
    XL, XR = -9, 26
    YB0, YB1 = 0.55, H - 1.24
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
    xb = X1 + 0.10
    V.vline_cm(fig, xb, rows_y[2] - 0.20, rows_y[0] + 0.20, color=S.INK, lw=0.7)
    for yy in (rows_y[0] + 0.20, rows_y[2] - 0.20):
        V.hline_cm(fig, xb - 0.08, xb, yy, color=S.INK, lw=0.7)
    M.ftext(fig, xb + 0.15, rows_y[1], "Groups differ\np = .002", ha="left", va="center", fontsize=S.FS_TICK,
            color=S.INK, linespacing=1.1)
    M.ftext(fig, xb + 0.15, rows_y[3], "No difference\ndetected, p = .15", ha="left", va="center", fontsize=S.FS_TICK,
            color=S.INK, linespacing=1.1)
    keys = [("o", S.EMPLOYEE, S.EMPLOYEE, S.MS_CIRCLE, f"No expected penalty (n = {ns[0]})", S.EMPLOYEE, "bold"),
            ("o", GREY_D, GREY_D, S.MS_CIRCLE, f"Expected penalty (n = {ns[1]})", GREY_D, "bold")]
    V.r5_key(fig, W - 0.05 - V.key_width(fig, keys), H - 0.64, keys)
    V.head(fig, name, "Pay PMEs would give up, % of monthly pay")
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
    blocks = [("1–2 WFH days a week", "p1", "physical", [(0, "Most roles need presence", True),
                                                             (1, "Some or few roles do", False)]),
              ("Fully remote", "p3", "creat", [(0, "Creativity concern", True), (1, "No creativity concern", False)])]
    LX, X0, X1, VX = 5.20, 5.40, 11.75, W - 0.05
    XL, XR = -40, 90
    AY, AT = 0.55, H - 0.55
    ax = M.axes_cm(fig, X0, AY, X1 - X0, AT - AY)
    ax.set_xlim(XL, XR)
    YA_, YB_ = 0.0, 6.0
    ax.set_ylim(YA_, YB_)
    S.ref_line(ax, 0, YA_, YB_)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(S.RULE)
    S.pct_ticks(ax, [0, 25, 50, 75])

    def fy(y):
        return AY + (y - YA_) / (YB_ - YA_) * (AT - AY)
    ys = [(5.2, [4.35, 3.55]), (2.45, [1.6, 0.8])]
    for (title, item, split, grps), (yh, yr) in zip(blocks, ys):
        M.ftext(fig, 0.05, fy(yh), title, ha="left", va="center", fontsize=S.FS_HEAD, color=S.INK, fontweight="bold")
        for (g, lab, focal), y in zip(grps, yr):
            q = D[(D.side == "emp") & (D.split == split) & (D.group == g) & (D["item"] == item)].iloc[0]
            ax.plot([q.lb, q.ub], [y, y], color=S.EMPLOYER, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
            ax.plot([q.giveup], [y], marker="D", ms=S.MS_DIAMOND, mfc=S.EMPLOYER if focal else "white",
                    mec="white" if focal else S.EMPLOYER, mew=S.MEW if focal else S.MEW_HOLLOW, ls="none", zorder=3)
            M.ftext(fig, LX, fy(y), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
            M.ftext(fig, LX + 0.08, fy(y), f"n = {int(q.n)}", ha="left", va="center", fontsize=S.FS_CAP, color=S.MUTED)
            M.ftext(fig, VX, fy(y), txt0(q.giveup), ha="right", va="center", fontsize=S.FS_VAL, color=S.EMPLOYER,
                    fontweight="bold")
    V.hline_cm(fig, 0.05, W - 0.05, fy(3.1), **S.SEP)
    V.head(fig, name, "Pay cut employers would require, % of pay")
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
    P_HEAD = ("Joint", "test p")
    PCW = max([V.tw_cm(fig, ".43", S.FS_ROW)] + [V.tw_cm(fig, s_, S.FS_HEAD, "bold") for s_ in P_HEAD]) + 0.10
    PX0, GAP = LX + 0.15, 0.30
    PW = (W - 0.05 - PCW - 0.30 - PX0 - 2 * GAP) / 3
    AY, AT = 0.55, H - 0.98
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
                est, lb, ub = tri("pme", "p3own" if it == "p3" else it)
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
    xp = W - 0.05 - PCW
    M.ftext(fig, xp, AT + 0.10, P_HEAD[0], ha="left", va="bottom", fontsize=S.FS_HEAD, color=S.INK, fontweight="bold")
    M.ftext(fig, xp, AT + 0.06, P_HEAD[1], ha="left", va="top", fontsize=S.FS_HEAD, color=S.INK, fontweight="bold")
    for (sp, a, b), (ya, yb_) in zip(splits, ((7.6, 6.8), (5.4, 4.6), (3.2, 2.4))):
        pv = get("pme", "joint_p", split=sp, group=-1)
        M.ftext(fig, xp, (fy(ya) + fy(yb_)) / 2, ("%.2f" % pv).lstrip("0"), ha="left", va="center",
                fontsize=S.FS_ROW, color=S.INK)
    V.head(fig, name, "Pay PMEs would give up, % of monthly pay")
    keys = [("o", "white", S.EMPLOYEE, S.MS_CIRCLE, "first group listed", S.INK, "normal"),
            ("o", S.EMPLOYEE, S.EMPLOYEE, S.MS_CIRCLE, "second", S.INK, "normal")]
    kw_ = V.key_width(fig, keys, gap=0.35)
    V.r5_key(fig, W - 0.05 - kw_, H - 0.23, keys, gap=0.35)
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
    cats = [("0 days (fully onsite)", "0"), ("1-2 days a week", "1\u20132"), ("3-4 days a week", "3\u20134"),
            ("5 days (remote-first)", "5")]
    vals = []
    for it, short in cats:
        v, _ = M.one("org_fwa.csv", block="typical_wfh_days", sample="all", group="All employer respondents", item=it)
        vals.append((float(v["share"]), short, int(v["n"])))
    n_o = vals[0][2]
    M.ftext(fig, RX0, H - 0.04, f"Employers (n = {n_o})", ha="left", va="top", fontsize=S.FS_HEAD,
            color=S.EMPLOYER, fontweight="bold")
    M.ftext(fig, RX0, H - 0.47, "Typical PME WFH days a week", ha="left", va="top", fontsize=S.FS_AXIS, color=S.INK)
    CB, CT = 0.46, H - 1.40
    CW, CP = 0.78, 1.18
    scale = (CT - CB) / max(v for v, _, _ in vals)
    for k, (v, short, _) in enumerate(vals):
        x = RX0 + 0.25 + k * CP
        hi_ = short == "1\u20132"
        fig.add_artist(Rectangle((x / W, CB / H), CW / W, v * scale / H, transform=fig.transFigure,
                                 fc=S.EMPLOYER if hi_ else S.EMPLOYER_LIGHT, ec="none", lw=0))
        M.ftext(fig, x + CW / 2, CB + v * scale + 0.08, f"{r0(v)}%", ha="center", va="bottom", fontsize=S.FS_VAL,
                color=S.EMPLOYER if hi_ else S.INK, fontweight="bold")
        M.ftext(fig, x + CW / 2, CB - 0.08, short, ha="center", va="top", fontsize=S.FS_ROW, color=S.INK)
    V.hline_cm(fig, RX0 + 0.10, RX0 + 0.40 + 3 * CP + CW, CB, color=S.RULE, lw=0.7)
    return done(fig, name)


# ----------------------------------------------------------------------------------------------------------------
# F_puzzle_r5 (M-puzzle): four fact cards, no equal-pay share, no dagger
# ----------------------------------------------------------------------------------------------------------------
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
    import fig_r5 as F5
    name = "F_barriers_r5"
    fam = "Familiar (aware and understand key provisions)"
    c = float(M.one("emp_career.csv", block="career_penalty", sample="all", group="All respondents",
                    item="Agree (4-5)")[0]["share"])
    j = float(M.one("emp_tgfwar.csv", block="by_role", sample="all", group="Role: Junior professional / specialist",
                    item=fam)[0]["share"])
    a = float(M.one("emp_tgfwar.csv", block="overall", sample="all", group="All employed", item=fam)[0]["share"])
    d_ = M.one("emp_requests.csv", block="outcome", sample="all", group="Employed who say they made a formal request",
               item="Yes, but declined")[0]
    d = float(d_["share"])
    assert int(d_["k"]) >= 5
    fig = M.new_fig(*SIZE)
    H, W = fig.H, fig.W
    gap, sep = 0.18, 0.50
    cw = (W - 0.10 - gap - sep) / 3
    CY0, CY1 = 0.04, H - 0.52
    xs = [0.05, 0.05 + cw + gap, 0.05 + 2 * cw + gap + sep]
    for x0, x1, s in ((xs[0], xs[1] + cw, "Not conditional on asking"), (xs[2], xs[2] + cw, "Reported requesters")):
        M.ftext(fig, (x0 + x1) / 2, H - 0.21, s, ha="center", va="center", fontsize=S.FS_HEAD, color=S.INK,
                fontweight="bold")
        V.hline_cm(fig, x0, x1, H - 0.42, color=S.INK, lw=0.8)
    V.vline_cm(fig, xs[2] - sep / 2, CY0, H - 0.05, **S.SEP)
    cards = [("Career concern", c, "of PMEs agree shorter or\nmore flexible hours would\nhurt their career"),
             ("Know the Guidelines", j, f"of junior PMEs are familiar\nwith the Guidelines\n(all levels: {r0(a)}%)"),
             ("Outright refusal", d, "of PMEs who report a\nformal request: a\nselected lower bound")]
    YH = CY1 - S.CARD_BAR_CM - 0.13
    YN, YT = CY1 - 1.48, CY1 - 2.08
    YD = YT - 0.62
    for x, (hd, v, ds) in zip(xs, cards):
        F5.card(fig, x, CY0, cw, CY1 - CY0, S.EMPLOYEE)
        M.ftext(fig, x + cw / 2, YH, hd, ha="center", va="top", fontsize=F5.FS_CARD, color=S.EMPLOYEE, fontweight="bold")
        M.ftext(fig, x + cw / 2, YN, f"{r0(v)}%", ha="center", va="baseline", fontsize=S.FS_BIG, color=S.EMPLOYEE,
                fontweight="bold")
        fx = F5.track(fig, x + 0.30, YT, cw - 0.60)
        F5.bar(fig, fx(0), fx(v), YT, S.EMPLOYEE)
        F5.track_ends(fig, fx, YT)
        M.ftext(fig, x + cw / 2, YD - 0.06, ds, ha="center", va="top", fontsize=F5.FS_LAB, color=S.INK,
                linespacing=1.2, multialignment="center")
    return done(fig, name)


FIGS = {"F_org_wtp": fig_org_wtp, "F_gap_m": fig_gap_m, "F_why_pmes": fig_why_pmes, "F_where_r5": fig_where_r5,
        "F_groups_m": fig_groups_m,
        "F_landscape_m": fig_landscape_m, "F_puzzle_r5": fig_puzzle_r5, "F_barriers_r5": fig_barriers_r5}

if __name__ == "__main__":
    import warnings
    warnings.simplefilter("default")
    names = sys.argv[1:] or list(FIGS)
    for nm in names:
        print("wrote", FIGS[nm]())
    for fl in dict.fromkeys(M.FLAGS):
        print("FLAG:", fl)
