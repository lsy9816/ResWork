# =============================================================================================================
# fig_r5_appended.py -- COPY of deck_support/scripts/fig_r5.py (professor's script; the original is not modified)
# with the employer values switched to the appended employer sample (n = 397). Run it through
# make_figs_appended.py, which writes the figures into MOM_presentation/figures/ and reads the appended data
# from MOM_presentation/data/. Changes vs the original: fig_org_eqpay, fig_where_r5 and fig_meet_r5 expected
# values (and the 303-firm EVIDENCE_BOOK string checks switched off for the employer numbers).
# =============================================================================================================
"""Round-5 main-slide figures (redesign/ROUND5_SPEC.md sections 3-4; reviews/claude_round5/MANDATE.md).

New figure names, so nothing collides with fig_v2.py / fig_main.py / fig_backup.py (none of those is edited):

  F_org_eqpay    M-employers  employer equal-pay shares with 95% CIs only, ranked; grey >20%-turnover benchmark;
                              50% reference; NO % discounts                          EB Q1-Q5, Q8 (R10, R12)
  F_where_r5     M-where      two within-employer contrasts: 1-2 WFH days by presence need (29 vs 49%);
                              fully remote by creativity concern (19 vs 39%); 50% reference; n labels   EB M10, Q10, Q11
  F_meet_r5      M-meet       two visibly separate panels (PMEs | employers), each with its own axis and 50% line,
                              same row order, zone labels A/B/C; header 'Compare each side with its own 50%; do not
                              compare distances across sides'                         EB Q1, Q2, Q5, Q3, M1
  F_puzzle_r5    M-puzzle     2 x 2 fact cards: PMEs' equal-pay share 58%; about 1 in 5 firms offer it (21%);
                              offering goes with a written policy, 26.5% vs 9.7% (association); take-up about 1 in 3
                              where available (31-33%+)                               EB Q5, M16, M17, M22, D2x
  F_barriers_r5  M-barriers   three fact cards under two headers, 'Not conditional on asking' | 'Reported
                              requesters': 37-45%+ expect a career penalty; junior PMEs 25-29%+ familiar with the
                              Guidelines (all levels, employed: 44-55%+); 4-7%+ of reported requesters report an
                              outright refusal, a selected lower bound               EB M23 (B5), D6, D7, D7b
                              (fixer pass 7 Oct 2026: header was 'All surveyed PMEs', the wrong base for the
                              junior-PME card, fact_audit WRONG 3; all-level familiarity added, mom_ps-05)
  (+ = dagger: two-sample range, all respondents / excluding one online panel; on a 0-100% track the bar is solid to
  the lower value and mid grey from the lower to the upper value.)

Every figure is drawn at TRUE size 13.0 x 5.0 cm, except F_meet_r5 at 14.0 x 4.7 cm (SIZE_CM; integrator pass, see
below) (fig_main.new_fig pins the canvas; the PDF size is measured with PyMuPDF after saving), so \\FigC{<name>} prints
it at scale 1. Text is never below 8 pt; row labels, tick labels and
other labels are at least 9 pt (checked after drawing; any breach stops the run). No mathtext anywhere: the dagger of a
two-sample range is a plain 'dagger' glyph drawn as its own artist at >= 8 pt. Madrid palette from figstyle.py
(PMEs myblue #003366, employers myred #990000, everything else neutral grey), white canvas, no alpha blending (checked).

Every number drawn is read from an aggregate CSV row (data/*.csv, mechanisms/*.csv) and checked against the
EVIDENCE_BOOK value with fig_main.record (the script stops on any mismatch); the expected value strings are also searched
for in the fact's own evidence-book line or table row, so a later edit of the book stops the build. CI ends that are
drawn but not printed are checked the same way where the book states them, and logged otherwise. Inputs are aggregates
only (no row-level data, no cell with n < 5).

Polish pass (7 Oct 2026; reviews/claude_round5/DESIGN_PLAN.md s1.3 and s2 fig_r5; lead decision G5; log:
reviews/claude_round5/log_polish_FIGmain.md): every size, weight and line style is a figstyle token (check() stops on
any other size); bold FS_HEAD headers top-left; "50% = no preference" as an FS_CAP label on top of the REF line
(S.ref_line replaces ref50); FS_VAL values; CI_LW, MS_*, MEW; no footnote lines (each moved, verbatim, to its slide's
\\SourceNote Note); cards in the deck's card style (Soft, square, CARD_BAR_CM top accent bar, CARD_PAD_CM, CARD_HEAD_FS
headings) with white tracks; F_meet_r5 without panel boxes (bottom spines, a RULE divider), a right-aligned value
column and Ink zone discs.

Run:   python3 fig_r5.py               (all five figures + manifest)
       python3 fig_r5.py F_meet_r5     (one figure, no manifest)
Output: ../../overleaf/figures/<name>.{pdf,png}; manifest reviews/claude_round5/figs_r5_manifest.md
"""
import sys
import warnings

from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.text import Text

import figstyle as S
import fig_main as M
import fig_v2 as V

W_CM, H_CM = 13.0, 5.0
# Polish-integrator pass (7 Oct 2026; log reviews/claude_round5/log_polish_integrate.md): F_meet_r5 is 14.0 wide so its
# mandated reading-rule header fits on ONE line (13.3 cm at 10 pt bold) and the two panels get a wider gap ("80%" and
# "10" no longer touch); the freed header line makes it 0.30 cm shorter with a slightly taller plot area. M-meet had
# 0.01 cm of vertical slack under its 2-line Interp and 2-line note block; this gives it about 0.30 cm, like the other
# figure slides. Same adaptation as F_motivation (14.0 wide), logged in ADJUDICATION.md.
SIZE_CM = {"F_meet_r5": (14.0, 4.7)}
OUT_MD = S.ROOT / "deck_support" / "reviews" / "claude_round5" / "figs_r5_manifest.md"
EB_TEXT = V.EB_TEXT

# Polish pass (7 Oct 2026; DESIGN_PLAN s1.3 and s2 fig_r5; lead decision G5): every size, weight and line style is a
# figstyle token; check() stops on any other size. FS_DAG = FS_VAL (a dagger after a value label is the size of the
# value); FS_DAG_BIG (11 pt) is the dagger next to a headline number. Cards take the deck's card style (G7).
FS_MIN = S.FS_NOTE          # 8 pt floor for any text (ROUND5_SPEC section 2)
FS_LAB = S.FS_TICK          # 9 pt floor for row, axis and other labels
FS_ROW = S.FS_ROW           # 9.5 row labels
FS_TICK = S.FS_TICK         # 9 tick labels (MUTED)
FS_VAL = S.FS_VAL           # 10 bold value labels in the side colour
FS_HEAD = S.FS_HEAD         # 10 bold figure header (top-left) and panel heads
FS_CAP = S.FS_CAP           # 8.5 direct labels ("50% = no preference"), n labels
FS_NOTE = S.FS_NOTE         # 8 track ends
FS_BIG = S.FS_BIG           # 20 headline numbers on the fact cards
FS_DAG = S.FS_DAG           # = FS_VAL
FS_DAG_BIG = S.FS_DAG_BIG   # 11: dagger next to a headline number; also the second line of a number block
FS_CARD = S.CARD_HEAD_FS    # 10.5 card headings (= LaTeX \FsHead x 0.92)
FS_OK = set(S.FS_TOKENS) | {S.CARD_HEAD_FS}
GREY_D = V.GREY_D   # dark neutral grey (#4D4D4D) for comparison / benchmark series
WHITE = "#FFFFFF"
LABELS = {}         # name -> artists that must be >= FS_LAB


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def eb_row(fid):
    """The evidence-book table row '| Qn | ... |' of fact fid (section 3b table)."""
    for line in EB_TEXT.splitlines():
        if line.startswith(f"| {fid} |"):
            return line
    sys.exit(f"STOP: EVIDENCE_BOOK has no table row for {fid}")


def eb_row_has(fid, *subs):
    line = eb_row(fid)
    for s in subs:
        if s not in line:
            sys.exit(f"STOP: EVIDENCE_BOOK {fid} table row no longer contains {s!r}")


def new_fig(name=None):
    fig = M.new_fig(*SIZE_CM.get(name, (W_CM, H_CM)))
    fig.patch.set_facecolor(WHITE)
    return fig


def lab(name, artist):
    """Register a label artist (must be >= FS_LAB)."""
    LABELS.setdefault(name, []).append(artist)
    return artist


def ltext(fig, name, x, y, s, **kw):
    """Figure text in cm that counts as a label (>= 9 pt)."""
    return lab(name, M.ftext(fig, x, y, s, **kw))


def width_cm(fig, s, fs, weight="normal"):
    return V.tw_cm(fig, s, fs, weight)


def text_dag(fig, x, y, s, fs, color, weight="bold", ha="center", va="baseline", dag_fs=None, name=None):
    """Draw s and a plain dagger glyph raised to the top of s (no mathtext), as one unit aligned by ha.
    Returns (main artist, dagger artist)."""
    dag_fs = dag_fs or (fs if fs <= FS_DAG_BIG else FS_DAG_BIG)   # polish pass: a token size, never below 8 pt
    w_main = width_cm(fig, s, fs, weight)
    w_dag = width_cm(fig, "†", dag_fs, "normal")
    gap = 0.02
    total = w_main + gap + w_dag
    x0 = {"left": x, "center": x - total / 2, "right": x - total}[ha]
    t = M.ftext(fig, x0, y, s, ha="left", va=va, fontsize=fs, color=color, fontweight=weight)
    r = fig.canvas.get_renderer()
    bb = t.get_window_extent(renderer=r)
    _, fy1 = fig.transFigure.inverted().transform((bb.x1, bb.y1))
    d = M.ftext(fig, x0 + w_main + gap, fy1 * fig.H - 0.02 * fs / 10, "†", ha="left", va="top", fontsize=dag_fs,
                color=color, fontweight="normal")
    if name:
        lab(name, t)
    return t, d


def style_xaxis(ax, ticks):
    """Bottom spine only (RULE); percentage ticks via figstyle.pct_ticks (FS_TICK, MUTED, '%' on the last)."""
    ax.set_yticks([])
    for s_ in ("left", "right", "top"):
        ax.spines[s_].set_visible(False)
    ax.spines["bottom"].set_color(S.RULE)
    S.pct_ticks(ax, ticks)


def check(fig, name):
    """Stop on any text below 8 pt, any size that is not a figstyle token (polish pass, G5), any registered label or
    tick label below 9 pt, any mathtext, any alpha < 1, or a non-white canvas (ROUND5_SPEC section 2; figstyle
    round-3 rule: no alpha-blended myred/myblue)."""
    fig.canvas.draw()
    errs = []
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        if "$" in t.get_text():
            errs.append(f"mathtext in {t.get_text()!r}")
        if t.get_fontsize() < FS_MIN - 1e-9:
            errs.append(f"text below {FS_MIN} pt ({t.get_fontsize()}): {t.get_text()!r}")
        if not any(abs(t.get_fontsize() - k) < 1e-6 for k in FS_OK):
            errs.append(f"size {t.get_fontsize()} pt is not a figstyle token: {t.get_text()!r}")
    for ax in fig.axes:
        for t in ax.get_xticklabels() + ax.get_yticklabels():
            if t.get_visible() and t.get_text().strip() and t.get_fontsize() < FS_LAB - 1e-9:
                errs.append(f"tick label below {FS_LAB} pt: {t.get_text()!r}")
        fc = ax.get_facecolor()
        if fc[3] > 0 and tuple(round(c, 3) for c in fc[:3]) != (1.0, 1.0, 1.0):
            errs.append(f"axes facecolor {fc}")
    for t in LABELS.get(name, []):
        if t.get_fontsize() < FS_LAB - 1e-9:
            errs.append(f"label below {FS_LAB} pt ({t.get_fontsize()}): {t.get_text()!r}")
    for a in fig.findobj(lambda o: hasattr(o, "get_alpha")):
        al = a.get_alpha()
        if al is not None and al < 1.0:
            errs.append(f"alpha {al} on {type(a).__name__}")
    if tuple(round(c, 3) for c in fig.get_facecolor()[:3]) != (1.0, 1.0, 1.0):
        errs.append("figure facecolor not white")
    if errs:
        sys.exit(f"STOP: {name}: " + "; ".join(errs))


def done(fig, name):
    check(fig, name)
    V.outside(fig, name)
    return M.finish(fig, name, SIZE_CM.get(name, (W_CM, H_CM)))


def fit(fig, name, s, fs, max_w, weight="normal"):
    """Stop if any line of s is wider than max_w cm at fs (keeps labels inside their columns and cards)."""
    for line in s.split("\n"):
        w = width_cm(fig, line, fs, weight)
        if w > max_w + 1e-9:
            sys.exit(f"STOP: {name}: {line!r} is {w:.2f} cm at {fs} pt; the space is {max_w:.2f} cm")
    return s


HEAD_EQPAY = "Hiring choices for the flexible candidate at equal pay, %"
LAB50 = "50% = no preference"


# ---------------------------------------------------------------------------
# F_org_eqpay (M-employers): employer equal-pay shares with 95% CIs only, ranked; grey benchmark (Q1-Q5, Q8)
# ---------------------------------------------------------------------------
def fig_org_eqpay():
    name = "F_org_eqpay"
    # EB section 3b table (employer column) and R12; checked as strings, then each drawn value against the CSV
    # Employer update (14 Oct 2026): appended employer sample (n = 397), appended_clogit.xlsx sheet main,
    # invlogit(b) with delta-method 95% CIs. The EVIDENCE_BOOK Q1-Q8/R12 rows still hold the 303-firm values,
    # so the string checks against them are switched off here; the expected values below are the appended ones.
    exp = {  # level: (label, Q id, share, CI)
        "2.timeflex": ("Compressed week", "Q5", 47, (41, 53)),
        "1.timeflex": ("Staggered hours", "Q4", 45, (40, 50)),
        "1.place": ("1–2 WFH days", "Q1", 40, (35, 45)),
        "2.place": ("3–4 WFH days", "Q2", 31, (26, 36)),
        "3.place": ("Fully remote", "Q3", 23, (18, 28)),
    }
    V.eb_has("R10", "fully remote penalised most")
    # ranking from the CSV (the order drawn is the order of the estimates, never typed)
    vals = {lev: M.eqpay("employer", lev) for lev in exp}
    order = sorted(exp, key=lambda k: -vals[k][0])
    if order != list(exp):
        sys.exit(f"STOP: {name}: CSV ranking {order} differs from the expected EB ranking {list(exp)}")
    bv, blb, bub, _, bd = M.eqpay("employer", "2.retention")

    fig = new_fig()
    H, W = fig.H, fig.W
    # Polish pass (7 Oct 2026; DESIGN_PLAN s2 fig_r5; G5): FS_HEAD header on the top row; "50% = no preference" as an
    # FS_CAP label on top of the REF line (row 2: header and label do not fit on one row at 10 pt); FS_VAL values,
    # FS_ROW labels; CI_LW, MS_DIAMOND / MS_SQUARE, MEW; SEP rule; pct_ticks; no footnote line (its text, "Lines: 95%
    # CIs. Model-based shares: no pair in the survey had equal pay.", is the M-employers \SourceNote Note).
    LX, X0, X1, VX = 3.80, 4.00, 11.70, W - 0.05      # label right edge | plot | value column (right edge)
    XL, XR = 10, 60
    AY, AT = 0.55, H - 0.88
    YA, YB = 0.30, 6.55
    ys = [6.05, 5.15, 4.25, 3.35, 2.45]
    yb = 0.95
    ax = M.axes_cm(fig, X0, AY, X1 - X0, AT - AY)
    ax.set_xlim(XL, XR)
    ax.set_ylim(YA, YB)

    def fy(y):
        return AY + (y - YA) / (YB - YA) * (AT - AY)

    S.ref_line(ax, 50, YA, YB)
    x50 = X0 + (50 - XL) / (XR - XL) * (X1 - X0)
    ltext(fig, name, 0.05, H - 0.04, fit(fig, name, HEAD_EQPAY, FS_HEAD, W - 0.10, "bold"), ha="left",
          va="top", fontsize=FS_HEAD, color=S.INK, fontweight="bold")
    fit(fig, name, LAB50, FS_CAP, 2 * (W - 0.05 - x50))
    V.cap50(fig, x50, AT + 0.05)
    for lev, y in zip(order, ys):
        lab_, qid, v_eb, ci_eb = exp[lev]
        v, lb, ub, _, d = vals[lev]
        txt = M.record(name, f"{M.pint(v)}%", v, d, qid, v_eb, f"employers, {lab_}: equal-pay share")
        M.record(name, "(CI end, unlabelled)", lb, d + " (lb)", qid, ci_eb[0], f"employers, {lab_}: 95% CI lower")
        M.record(name, "(CI end, unlabelled)", ub, d + " (ub)", qid, ci_eb[1], f"employers, {lab_}: 95% CI upper")
        ax.plot([lb, ub], [y, y], color=S.EMPLOYER, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
        ax.plot([v], [y], marker="D", ms=S.MS_DIAMOND, mfc=S.EMPLOYER, mec=WHITE, mew=S.MEW, ls="none", zorder=3)
        ltext(fig, name, VX, fy(y), txt, ha="right", va="center", fontsize=FS_VAL, color=S.EMPLOYER,
              fontweight="bold")
        bold = lev == "3.place"
        ltext(fig, name, LX, fy(y), fit(fig, name, lab_, FS_ROW, LX - 0.05, "bold" if bold else "normal"),
              ha="right", va="center", fontsize=FS_ROW, color=S.INK, fontweight="bold" if bold else "normal")
    # benchmark row, set apart by a rule and drawn in neutral grey (EB Q8; R11 'yardstick')
    V.hline_cm(fig, 0.05, W - 0.05, fy((ys[-1] + yb) / 2), **S.SEP)
    bt = M.record(name, "33.6%", bv, bd, "Q8", 33.6, "benchmark: candidate with >20% turnover risk: equal-pay share")
    M.record(name, "(CI end, unlabelled)", blb, bd + " (lb)", "Q8", 28, "benchmark: 95% CI lower")
    M.record(name, "(CI end, unlabelled)", bub, bd + " (ub)", "Q8", 39, "benchmark: 95% CI upper")
    ax.plot([blb, bub], [yb, yb], color=GREY_D, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
    ax.plot([bv], [yb], marker="s", ms=S.MS_SQUARE, mfc=GREY_D, mec=WHITE, mew=S.MEW, ls="none", zorder=3)
    ltext(fig, name, VX, fy(yb), bt, ha="right", va="center", fontsize=FS_VAL, color=GREY_D, fontweight="bold")
    blab = fit(fig, name, "Benchmark: candidate\nwith >20% turnover risk", FS_ROW, LX - 0.05)
    ltext(fig, name, LX, fy(yb), blab, ha="right", va="center", fontsize=FS_ROW, color=GREY_D, linespacing=1.0)
    style_xaxis(ax, [10, 20, 30, 40, 50, 60])
    return done(fig, name)


# ---------------------------------------------------------------------------
# F_where_r5 (M-where): two within-employer contrasts (M10, Q10, Q11)
# ---------------------------------------------------------------------------
def fig_where_r5():
    name = "F_where_r5"
    # Employer update (14 Oct 2026): appended employer sample; rows from ../data/employer_channels_appended.csv
    # (appended_clogit.xlsx physical_1/2 and creative_concern_1/0, invlogit with delta-method CIs). The 303-firm
    # EVIDENCE_BOOK M10/Q10/Q11 strings are not checked here.
    CI_EB = {("physical", "0"): (41.7, 54.7), ("physical", "1"): (19.3, 33.7),
             ("creative", "0"): (20.8, 37.3), ("creative", "1"): (11.3, 24.6)}
    blocks = [  # header, item, rows: (split, group, label, share, n, focal?)
        ("1–2 WFH days a week", "1.place",
         [("physical", "1", "Most roles need presence", 27, 137, True),
          ("physical", "0", "Some or few roles do", 48, 260, False)]),
        ("Fully remote", "3.place",
         [("creative", "1", "Creativity concern", 18, 201, True),
          ("creative", "0", "No creativity concern", 29, 196, False)]),
    ]
    fig = new_fig()
    H, W = fig.H, fig.W
    # Polish pass (7 Oct 2026; DESIGN_PLAN s2 fig_r5; G5): FS_HEAD header on the top row; "50% = no preference" as an
    # FS_CAP label on top of the REF line (row 2); group heads 9.5 pt bold INK; FS_VAL values, FS_ROW labels, FS_CAP
    # n labels; CI_LW; filled diamonds MS_DIAMOND with a white MEW edge, hollow ones a MEW_HOLLOW edge; SEP rule;
    # pct_ticks; no footnote line (the marker key, "Filled: firms with the need or concern; hollow: other firms.
    # Lines: 95% CIs.", is the M-where \SourceNote Note).
    # appended: three-digit n labels ("n = 137") need 0.10 cm more label room than "n = 98"
    LX, X0, X1, VX = 5.20, 5.40, 11.75, W - 0.05
    XL, XR = 0, 60
    AY, AT = 0.55, H - 0.88
    YA, YB = 0.30, 6.30
    yhead = [5.75, 2.80]
    yrows = [[4.95, 4.10], [2.00, 1.15]]
    ax = M.axes_cm(fig, X0, AY, X1 - X0, AT - AY)
    ax.set_xlim(XL, XR)
    ax.set_ylim(YA, YB)

    def fy(y):
        return AY + (y - YA) / (YB - YA) * (AT - AY)

    S.ref_line(ax, 50, YA, YB)
    x50 = X0 + (50 - XL) / (XR - XL) * (X1 - X0)
    ltext(fig, name, 0.05, H - 0.04, fit(fig, name, HEAD_EQPAY, FS_HEAD, W - 0.10, "bold"), ha="left",
          va="top", fontsize=FS_HEAD, color=S.INK, fontweight="bold")
    fit(fig, name, LAB50, FS_CAP, 2 * (W - 0.05 - x50))
    V.cap50(fig, x50, AT + 0.05)
    for (head, item, rows), ys, yh in zip(blocks, yrows, yhead):
        ltext(fig, name, 0.05, fy(yh), head, ha="left", va="center", fontsize=FS_ROW, color=S.INK,
              fontweight="bold")
        for (split, grp, glab, v_eb, n_eb, focal), y in zip(rows, ys):
            r, d = V.mone("employer_channels.csv", block="eqpay", split=split, group=grp, item=item)
            v, lb, ub = (100 * float(r[k]) for k in ("est", "lb", "ub"))
            n = float(r["n_resp"])
            txt = M.record(name, f"{M.pint(v)}%", v, d + " (est)", "M10", v_eb, f"{glab}, {head}: equal-pay share")
            nt = M.record(name, f"n = {int(n)}", n, d + " (n_resp)", "M10", n_eb, f"{glab}: firms")
            M.record(name, "(CI end, unlabelled)", lb, d + " (lb)", "M10", CI_EB[(split, grp)][0],
                     f"{glab}, {head}: 95% CI lower (separate clogit)")
            M.record(name, "(CI end, unlabelled)", ub, d + " (ub)", "M10", CI_EB[(split, grp)][1],
                     f"{glab}, {head}: 95% CI upper (separate clogit)")
            ax.plot([lb, ub], [y, y], color=S.EMPLOYER, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
            if focal:
                ax.plot([v], [y], marker="D", ms=S.MS_DIAMOND, mfc=S.EMPLOYER, mec=WHITE, mew=S.MEW, ls="none",
                        zorder=3)
            else:
                ax.plot([v], [y], marker="D", ms=S.MS_DIAMOND, mfc=WHITE, mec=S.EMPLOYER, mew=S.MEW_HOLLOW,
                        ls="none", zorder=3)
            ltext(fig, name, VX, fy(y), txt, ha="right", va="center", fontsize=FS_VAL, color=S.EMPLOYER,
                  fontweight="bold")
            wn = width_cm(fig, nt, FS_CAP)
            ltext(fig, name, LX - wn - 0.14, fy(y), fit(fig, name, glab, FS_ROW, LX - wn - 0.25), ha="right",
                  va="center", fontsize=FS_ROW, color=S.INK)
            M.ftext(fig, LX, fy(y), nt, ha="right", va="center", fontsize=FS_CAP, color=S.MUTED)
    V.hline_cm(fig, 0.05, W - 0.05, fy((yrows[0][1] + yhead[1]) / 2), **S.SEP)
    style_xaxis(ax, [0, 10, 20, 30, 40, 50, 60])
    return done(fig, name)


# ---------------------------------------------------------------------------
# F_meet_r5 (M-meet): two separate panels, each read against its own 50% (Q1, Q2, Q3, Q5, M1)
# ---------------------------------------------------------------------------
def fig_meet_r5():
    name = "F_meet_r5"
    # Employer update (14 Oct 2026): employer panel = appended sample (n = 397); EB employer strings not checked
    eb_row_has("Q5", "**58%** (55–62)")
    eb_row_has("Q1", "**58%** (55–62)")
    eb_row_has("Q2", "**61%** (57–64)")
    V.eb_has("M1", "the remote job wins **64% [61, 68]** of choices at equal pay")
    rows = [  # label, PME level, employer level, (PME id, share, CI), (employer id, share, CI), zone
        ("Compressed week", "2.timeflex", "2.timeflex", ("Q5", 58, (55, 62)), ("Q5", 47, (41, 53)),
         "A  Common ground"),
        ("1–2 WFH days", "1.place", "1.place", ("Q1", 58, (55, 62)), ("Q1", 40, (35, 45)),
         "B  Depends on the role"),
        ("3–4 WFH days", "2.place", "2.place", ("Q2", 61, (57, 64)), ("Q2", 31, (26, 36)), "C  Far apart"),
        ("Fully remote", "p3own", "3.place", ("M1", 64, (61, 68)), ("Q3", 23, (18, 28)), "C  Far apart"),
    ]
    fig = new_fig(name)
    H, W = fig.H, fig.W
    # Polish pass (7 Oct 2026; DESIGN_PLAN s2 fig_meet_r5; G5): the mandated reading rule stays as the FS_HEAD header,
    # top-left, on ONE line (integrator pass: 13.3 cm at 10 pt bold on the 14.0 cm canvas); panel titles FS_HEAD bold in
    # the side colour; value labels in a right-aligned column at XR - 0.5 in each panel, clear of the 50% line;
    # pct_ticks every 10 points; bottom spines only plus a RULE divider between the panels (no boxes); zones as Ink
    # disc badges (white letter) with Ink names; SEP zone rules; no footnote line (its text is the M-meet
    # \SourceNote Note, verbatim).
    DISC = 0.34                                      # zone disc diameter (cm)
    LX = 0.07 + max(max(width_cm(fig, r[0], FS_ROW) for r in rows),
                    max(width_cm(fig, r[5].split("  ", 1)[1], FS_LAB, "bold") for r in rows) + DISC + 0.10)
    # tick labels are centred on their ticks: the gap holds the PME "80%" and the employer "10" side by side, and the
    # employer panel stops short of the canvas edge by half its "70%"
    gap = 1.00                                       # integrator pass: 0.66 -> 1.00 cm, "80%" | "10" clear
    RIN = 0.34
    # the employer panel is as wide as its 10 pt title needs (4.52 cm); the panels share no ruler anyway (below)
    pw_r = width_cm(fig, "Employers: hiring choices", FS_HEAD, "bold") + 0.10
    pw = W - 0.05 - RIN - (LX + 0.18) - gap - pw_r
    P = [(LX + 0.18, LX + 0.18 + pw), (LX + 0.18 + pw + gap, W - 0.05 - RIN)]
    # fixer pass 7 Oct 2026 (mom_ps-09; fact_audit s3 item 10): one x-range PER PANEL, so the two panels share no
    # ruler. Employers 10-70 keeps the compressed-week CI inside its panel.
    RNG = [(40, 80), (10, 70)]                       # PMEs | employers
    AY, AT = 0.52, H - 0.88                          # integrator pass: one header line (was H - 1.28, two lines)
    YA, YB = 0.45, 4.55
    ys = [4.0, 3.0, 2.0, 1.0]

    def fy(y):
        return AY + (y - YA) / (YB - YA) * (AT - AY)

    # header: the reading rule (EB Lead decision 3; COMMENTS slide 14; ROUND5_SPEC M-meet)
    hd = "Compare each side with its own 50%; do not compare distances across sides"
    ltext(fig, name, 0.05, H - 0.04, fit(fig, name, hd, FS_HEAD, W - 0.1, "bold"), ha="left", va="top",
          fontsize=FS_HEAD, color=S.INK, fontweight="bold", linespacing=1.1)
    titles = [("PMEs: job choices", S.EMPLOYEE), ("Employers: hiring choices", S.EMPLOYER)]
    axes = []
    for (x0, x1), (tt, col), (XL, XR) in zip(P, titles, RNG):
        ax = M.axes_cm(fig, x0, AY, x1 - x0, AT - AY)
        ax.set_xlim(XL, XR)
        ax.set_ylim(YA, YB)
        S.ref_line(ax, 50, YA, YB)
        style_xaxis(ax, list(range(XL, XR + 1, 10)))
        ltext(fig, name, (x0 + x1) / 2, AT + 0.08, fit(fig, name, tt, FS_HEAD, x1 - x0, "bold"), ha="center",
              va="bottom", fontsize=FS_HEAD, color=col, fontweight="bold")
        axes.append(ax)
    # divider between the two panels (RULE), and the zone rules across labels and panels (SEP): A | B | C
    V.vline_cm(fig, P[0][1] + gap / 2, AY - 0.02, AT + 0.42, **S.SEP)
    for yy in ((ys[0] + ys[1]) / 2, (ys[1] + ys[2]) / 2):
        for (x0, x1) in ((0.05, P[0][1]), (P[1][0], P[1][1])):
            V.hline_cm(fig, x0, x1, fy(yy), **S.SEP)
    for lab_, pl, rl, (pid, pv_eb, pci), (rid, rv_eb, rci), zone in rows:
        y = ys[[r[0] for r in rows].index(lab_)]
        ltext(fig, name, LX, fy(y) + 0.18, fit(fig, name, lab_, FS_ROW, LX - 0.05), ha="right", va="center",
              fontsize=FS_ROW, color=S.INK)
        letter, zname = zone.split("  ", 1)
        zt = ltext(fig, name, LX, fy(y) - 0.20, fit(fig, name, zname, FS_LAB, LX - 0.05 - DISC - 0.10, "bold"),
                   ha="right", va="center", fontsize=FS_LAB, color=S.INK, fontweight="bold")
        xd = LX - width_cm(fig, zname, FS_LAB, "bold") - 0.08 - DISC / 2
        M.fmarker(fig, xd, fy(y) - 0.20, "o", S.INK, S.INK, size=DISC / 2.54 * 72, lw=0)
        M.ftext(fig, xd, fy(y) - 0.20, letter, ha="center", va="center_baseline", fontsize=FS_NOTE, color=WHITE,
                fontweight="bold")
        # PMEs
        if pl == "p3own":
            r, d = V.mone("pme_channels.csv", block="eqpay", sample="all", split="all", item="p3own")
            pv, plb, pub = float(r["est"]), float(r["lb"]), float(r["ub"])
            what = "PMEs, fully remote (vs own commute)"
        else:
            pv, plb, pub, _, d = M.eqpay("employee", pl)
            what = f"PMEs, {lab_}"
        pt = M.record(name, f"{M.pint(pv)}%", pv, d, pid, pv_eb, what + ": equal-pay share")
        M.record(name, "(CI end, unlabelled)", plb, d + " (lb)", pid, pci[0], what + ": 95% CI lower")
        M.record(name, "(CI end, unlabelled)", pub, d + " (ub)", pid, pci[1], what + ": 95% CI upper")
        # employers
        rv, rlb, rub, _, rd = M.eqpay("employer", rl)
        rt = M.record(name, f"{M.pint(rv)}%", rv, rd, rid, rv_eb, f"employers, {lab_}: equal-pay share")
        M.record(name, "(CI end, unlabelled)", rlb, rd + " (lb)", rid, rci[0], f"employers, {lab_}: 95% CI lower")
        M.record(name, "(CI end, unlabelled)", rub, rd + " (ub)", rid, rci[1], f"employers, {lab_}: 95% CI upper")
        for (ax, v, lb, ub, t, col, mk), (x0p, x1p), (XL, XR) in zip(
                ((axes[0], pv, plb, pub, pt, S.EMPLOYEE, "o"), (axes[1], rv, rlb, rub, rt, S.EMPLOYER, "D")), P, RNG):
            # value labels: a right-aligned column at XR - 0.5 in each panel; it must clear the CI and the 50% line
            xv = x0p + (XR - 0.5 - XL) / (XR - XL) * (x1p - x0p)
            xs = xv - width_cm(fig, t, FS_VAL, "bold")
            xu = x0p + (max(ub, 50) - XL) / (XR - XL) * (x1p - x0p)
            if xs < xu + 0.10:
                sys.exit(f"STOP: {name}: label {t!r} starts at {xs:.2f} cm, within 0.10 cm of its CI or 50% line")
            ax.plot([lb, ub], [y, y], color=col, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
            if mk == "o":
                ax.plot([v], [y], marker=mk, ms=S.MS_CIRCLE, mfc=col, mec=WHITE, mew=S.MEW, ls="none", zorder=3)
            else:
                ax.plot([v], [y], marker=mk, ms=S.MS_DIAMOND, mfc=col, mec=WHITE, mew=S.MEW, ls="none", zorder=3)
            ltext(fig, name, xv, fy(y), t, ha="right", va="center", fontsize=FS_VAL, color=col, fontweight="bold")
    # fixer pass 7 Oct 2026 (editor-01): the zones are descriptive labels [Q16]; remote vs own commute [M1]. Polish
    # pass: both now sit in the M-meet \SourceNote Note ("Zones A-C: descriptive labels. PMEs' remote vs own commute.")
    V.eb_has("Q16", "So the A/B/C zones are **descriptive labels**")
    return done(fig, name)


# ---------------------------------------------------------------------------
# fact cards (F_puzzle_r5, F_barriers_r5)
# ---------------------------------------------------------------------------
def card(fig, x, y, w, h, color):
    """The deck's card (polish pass, G7; = LaTeX \\DeckCard): CARD_FILL, square corners, no outline, and a
    CARD_BAR_CM top accent bar in the card's side colour (myblue PMEs, myred employers)."""
    fig.add_artist(Rectangle((x / fig.W, y / fig.H), w / fig.W, h / fig.H, transform=fig.transFigure,
                             facecolor=S.CARD_FILL, edgecolor="none", linewidth=0, zorder=0))
    fig.add_artist(Rectangle((x / fig.W, (y + h - S.CARD_BAR_CM) / fig.H), w / fig.W, S.CARD_BAR_CM / fig.H,
                             transform=fig.transFigure, facecolor=color, edgecolor="none", linewidth=0, zorder=0.5))


def track(fig, x, y, w, h=0.20):
    """A 0-100% track of width w cm, drawn white on the Soft card; returns a function % -> x in cm."""
    fig.add_artist(Rectangle((x / fig.W, (y - h / 2) / fig.H), w / fig.W, h / fig.H, transform=fig.transFigure,
                             facecolor=WHITE, edgecolor="none", zorder=1))
    return lambda p: x + w * p / 100.0


def bar(fig, x0, x1, y, color, h=0.20):
    fig.add_artist(Rectangle((x0 / fig.W, (y - h / 2) / fig.H), max(x1 - x0, 0.0) / fig.W, h / fig.H,
                             transform=fig.transFigure, facecolor=color, edgecolor="none", zorder=2))


def range_bar(fig, fx, lo, hi, y, color, h=0.20):
    """Two-sample range on a track: solid to the lower value, mid grey from the lower to the upper value."""
    bar(fig, fx(0), fx(lo), y, color, h)
    bar(fig, fx(lo), fx(hi), y, S.GREY_MID, h)


def track_ends(fig, fx, y, h=0.20):
    """'0' and '100%' under the ends of a track (8 pt)."""
    for p, s, ha in ((0, "0", "left"), (100, "100%", "right")):
        M.ftext(fig, fx(p), y - h / 2 - 0.05, s, ha=ha, va="top", fontsize=FS_NOTE, color=S.MUTED)


def pair_range(name, a, b):
    """'lo–hi%' from two samples via fig_main.span (records both; the dagger is drawn by text_dag)."""
    s = M.span(name, a, b)
    if not s.endswith(M.DAG):
        sys.exit(f"STOP: {name}: span() changed format: {s!r}")
    return s[: -len(M.DAG)]


# ---------------------------------------------------------------------------
# F_puzzle_r5 (M-puzzle): valued, rarely offered, written-policy association, take-up (Q5, M16, M17, M22, D2x)
# ---------------------------------------------------------------------------
def fig_puzzle_r5():
    name = "F_puzzle_r5"
    eb_row_has("Q5", "**58%** (55–62)")
    V.eb_has("M16", "About one firm in five offers it", "**63 of 303 firms (20.8%**")
    V.eb_has("M17", "**26.5%** of firms with a written FWA policy offer it (53/200) vs **9.7%** without (10/103)")
    V.eb_has("M22", "Take-up where available is about one in three", "(**31.0%** [25.1, 37.5]); excl. Lucid 30 of 91 "
             "(33.0%)")
    V.eb_has("D2x", "compressed 31 [33]")
    CP = "compressed_puzzle.csv"
    # (1) PMEs: equal-pay choice share (Q5)
    qv, qlb, qub, _, qd = M.eqpay("employee", "2.timeflex")
    q_t = M.record(name, f"{M.pint(qv)}%", qv, qd, "Q5", 58, "PMEs choose the compressed-week job at equal pay")
    M.record(name, "(CI end, unlabelled)", qlb, qd + " (lb)", "Q5", 55, "Q5 PMEs: 95% CI lower")
    M.record(name, "(CI end, unlabelled)", qub, qd + " (ub)", "Q5", 62, "Q5 PMEs: 95% CI upper")
    # (2) firms offering it (M16)
    ov, ovd = V.mone(CP, sec="A", analysis="Employers offering a compressed week", sample="all",
                     item="Offers (ticked QID15 or typical PME schedule QID61)")
    of = float(ov["est"])
    of_t = M.record(name, f"{M.pint(of)}%", of, ovd + " (est)", "M16", 20.8, "surveyed firms offering it to PMEs")
    if not 19.5 <= of <= 21.5:   # 'about 1 in 5' (M16 heading) must still describe the share
        sys.exit(f"STOP: {name}: offering share {of:.1f}% no longer reads 'about 1 in 5'")
    M.LEDGER.append(dict(fig=name, shown="1 in 5", what="'about 1 in 5' firms offer it (M16 heading wording)", raw=of,
                         row=ovd, eb="M16 = About one firm in five offers it (20.8%)"))

    # (3) written policy association (M17)
    def pol(group):
        hits = [r for r in V.mrows(CP) if r["sec"] == "A" and r["analysis"].startswith("Share offering")
                and r["split"] == "policy" and r["group"] == group and r["metric"] == "share"]
        if len(hits) != 1:
            sys.exit(f"STOP: {CP} policy/{group}: {len(hits)} rows")
        r = hits[0]
        return float(r["est"]), f"`mechanisms/{CP}` l.{r['_line']}: sec A, split=policy, group={group}"

    pw, pwd = pol("Written FWA policy")
    pn, pnd = pol("No written FWA policy")
    pw_t = M.record(name, f"{pw:.1f}%", pw, pwd, "M17", 26.5, "firms with a written FWA policy offering it")
    pn_t = M.record(name, f"{pn:.1f}%", pn, pnd, "M17", 9.7, "firms without a written FWA policy offering it")
    # (4) take-up where available, two samples (M22; cross-checked with D2x in emp_fwa_use.csv)
    ta, tad = V.mone(CP, sec="B", analysis="Compressed week: overall", sample="all",
                     group="Employed PMEs with access (adjusted)", item="Take-up: uses it")
    tx, txd = V.mone(CP, sec="B", analysis="Compressed week: overall", sample="excl_lucid",
                     group="Employed PMEs with access (adjusted)", item="Take-up: uses it")
    for smp, val in (("all", float(ta["est"])), ("excl_lucid", float(tx["est"]))):
        r, d = M.one("emp_fwa_use.csv", block="takeup_adjusted", sample=smp, item="Compressed workweek")
        if abs(float(r["share"]) - val) > 0.01:
            sys.exit(f"STOP: {name}: take-up {smp}: compressed_puzzle {val} vs emp_fwa_use {r['share']}")
    tk_raw = sorted((float(ta["est"]), float(tx["est"])))
    tk = pair_range(name, (float(ta["est"]), tad + " (est)", "M22", 31.0, "take-up where available, all"),
                    (float(tx["est"]), txd + " (est)", "M22", 33.0, "take-up where available, excl. one panel"))
    if not (30.0 <= tk_raw[0] and tk_raw[1] <= 36.7):
        sys.exit(f"STOP: {name}: take-up no longer reads 'about 1 in 3'")
    M.LEDGER.append(dict(fig=name, shown="1 in 3", what="'about 1 in 3' take-up where available (M22 heading wording)",
                         raw=float(ta["est"]), row=tad, eb="M22 = about one in three (31.0%; excl. one panel 33.0%)"))

    fig = new_fig()
    H, W = fig.H, fig.W
    # Polish pass (7 Oct 2026; DESIGN_PLAN s2 fig_puzzle_r5; G5, G7): cards in the deck's card style (Soft, square,
    # top accent bar, CARD_PAD_CM), headings CARD_HEAD_FS, numbers FS_BIG with an FS_DAG_BIG second line, white
    # tracks on the cards. Card 1: a 0.20 cm track with the CI as a CI_LW line and the point as a white-edged dot;
    # "50% = no preference" (FS_CAP) centred on the top of the 50% tick (final fixer). No footnote line: the
    # dagger and "Surveyed samples, unweighted." are the M-puzzle \SourceNote Note. Numbers unchanged.
    PAD, BAR = S.CARD_PAD_CM, S.CARD_BAR_CM
    gx, gy = 0.20, 0.16
    cw = (W - 0.10 - gx) / 2
    FY0 = 0.04
    ch = (H - 0.04 - FY0 - gy) / 2
    cells = [(0.05, FY0 + ch + gy), (0.05 + cw + gx, FY0 + ch + gy), (0.05, FY0), (0.05 + cw + gx, FY0)]
    NB = 2.15                                    # width of the big-number block (cm)
    FS_SUB = FS_DAG_BIG                          # second line of the number block (11 pt)

    def frame(i, head, col):
        """Card i: heading; returns x, the right block (track and descriptor) and the body centre."""
        x, y0 = cells[i]
        card(fig, x, y0, cw, ch, col)
        ltext(fig, name, x + PAD, y0 + ch - BAR - 0.13, fit(fig, name, head, FS_CARD, cw - 2 * PAD, "bold"),
              ha="left", va="top", fontsize=FS_CARD, color=col, fontweight="bold")
        xr0, xr1 = x + PAD + NB + 0.15, x + cw - PAD
        yt = y0 + ch - 0.88                      # track centre
        yb = y0 + (ch - 0.58) / 2 + 0.02         # body centre (number block)
        return x, xr0, xr1, yt, yb

    def number(x, yb, main, col, sub=None, sub_col=None, dag=False):
        x = x + PAD                              # the number block starts at the card padding
        if sub is None:
            lab(name, M.ftext(fig, x + NB / 2, yb, fit(fig, name, main, FS_BIG, NB, "bold"), ha="center",
                              va="center", fontsize=FS_BIG, color=col, fontweight="bold"))
            return
        lab(name, M.ftext(fig, x + NB / 2, yb + 0.20, fit(fig, name, main, FS_BIG, NB, "bold"), ha="center",
                          va="center", fontsize=FS_BIG, color=col, fontweight="bold"))
        fit(fig, name, sub, FS_SUB, NB - 0.3, "bold")
        if dag:
            text_dag(fig, x + NB / 2, yb - 0.62, sub, FS_SUB, sub_col, weight="bold", ha="center", va="baseline",
                     dag_fs=FS_DAG_BIG, name=name)
        else:
            lab(name, M.ftext(fig, x + NB / 2, yb - 0.62, sub, ha="center", va="baseline", fontsize=FS_SUB,
                              color=sub_col, fontweight="bold"))

    def desc(xr0, xr1, ytop, s):
        lab(name, M.ftext(fig, xr0, ytop, fit(fig, name, s, FS_LAB, xr1 - xr0), ha="left", va="top",
                          fontsize=FS_LAB, color=S.INK, linespacing=1.15))

    # card 1: PMEs value it: 58% of choices at equal pay; the CI as a line on a 0-100 track, the 50% mark.
    # Final fixer (7 Oct 2026, visual QA p16): one grammar with slides 10-12 and with cards 2-4. The 95% CI is a
    # CI_LW line with the MS_CIRCLE white-edged dot (it had been a bar as tall as the track, read as "[o]"); the
    # 50% REF tick runs through the full track height, with "50% = no preference" (FS_CAP) centred on its top, as
    # cap50() places it on the charts; the label sits right of the card heading (checked below); the 0 / 100%
    # ends hang under the track as on cards 2-4.
    x, xr0, xr1, yt, yb = frame(0, "PMEs value it", S.EMPLOYEE)
    number(x, yb, q_t, S.EMPLOYEE)
    fx = track(fig, xr0, yt, xr1 - xr0)
    V.vline_cm(fig, fx(50), yt - 0.10, yt + 0.15, **dict(S.REF, zorder=3))
    fig.add_artist(Line2D([fx(qlb) / W, fx(qub) / W], [yt / H] * 2, transform=fig.transFigure, color=S.EMPLOYEE,
                          lw=S.CI_LW, solid_capstyle="butt", zorder=4))
    fig.add_artist(Line2D([fx(qv) / W], [yt / H], transform=fig.transFigure, marker="o", ms=S.MS_CIRCLE,
                          mfc=S.EMPLOYEE, mec=WHITE, mew=S.MEW, ls="none", zorder=5))   # the estimate
    l50 = fit(fig, name, LAB50, FS_CAP, xr1 - xr0)
    w50 = width_cm(fig, l50, FS_CAP)
    w_head = width_cm(fig, "PMEs value it", FS_CARD, "bold")
    if fx(50) - w50 / 2 < x + PAD + w_head + 0.15:
        sys.exit(f"STOP: {name}: '{LAB50}' runs into the card 1 heading")
    if fx(50) + w50 / 2 > xr1 + 1e-9:
        sys.exit(f"STOP: {name}: '{LAB50}' runs past the card 1 track")
    M.ftext(fig, fx(50), yt + 0.16, l50, ha="center", va="bottom", fontsize=FS_CAP, color=S.MUTED)
    track_ends(fig, fx, yt)
    desc(xr0, xr1, yt - 0.50, "of PMEs' job choices\nat equal pay")
    # card 2: few firms offer it: about 1 in 5 (21%)
    x, xr0, xr1, yt, yb = frame(1, "Few firms offer it", S.EMPLOYER)
    number(x, yb, "1 in 5", S.EMPLOYER, of_t, S.EMPLOYER)
    fx = track(fig, xr0, yt, xr1 - xr0)
    bar(fig, fx(0), fx(of), yt, S.EMPLOYER)
    track_ends(fig, fx, yt)
    desc(xr0, xr1, yt - 0.50, "of surveyed firms offer\nit to PMEs")
    # card 3: offering goes with a written FWA policy: 26.5% vs 9.7% (an association)
    x, xr0, xr1, yt, yb = frame(2, "Goes with a written FWA policy", S.EMPLOYER)
    number(x, yb, pw_t, S.EMPLOYER, f"vs {pn_t}", GREY_D)
    # integrator pass: the pair of tracks sits 0.04 cm higher and the '0 / 100%' ends hang under the lower track
    # (they touched its grey bar); the ends now sit where they do on the single-track cards
    fx = track(fig, xr0, yt + 0.12, xr1 - xr0, h=0.13)
    bar(fig, fx(0), fx(pw), yt + 0.12, S.EMPLOYER, h=0.13)
    fx2 = track(fig, xr0, yt - 0.04, xr1 - xr0, h=0.13)
    bar(fig, fx2(0), fx2(pn), yt - 0.04, GREY_D, h=0.13)
    track_ends(fig, fx2, yt - 0.04, h=0.13)
    desc(xr0, xr1, yt - 0.50, "of firms with / without a\nwritten policy offer it")
    # card 4: take-up where available: about 1 in 3 (31-33%+). Fixer pass 7 Oct 2026 (editor-15, worker-11): the
    # title is neutral (ROUND5_SPEC row 16); 'modest' implied a shortfall that EB M22 / D2 say is partly true by
    # construction (access includes users)
    x, xr0, xr1, yt, yb = frame(3, "Take-up where available", S.EMPLOYEE)
    number(x, yb, "1 in 3", S.EMPLOYEE, tk, S.EMPLOYEE, dag=True)
    fx = track(fig, xr0, yt, xr1 - xr0)
    range_bar(fig, fx, tk_raw[0], tk_raw[1], yt, S.EMPLOYEE)
    track_ends(fig, fx, yt)
    desc(xr0, xr1, yt - 0.50, "of PMEs with access\nuse it")
    return done(fig, name)


# ---------------------------------------------------------------------------
# F_barriers_r5 (M-barriers): career concern, junior familiarity, refusals among reported requesters
# ---------------------------------------------------------------------------
def fig_barriers_r5():
    name = "F_barriers_r5"
    V.eb_has("M23", "**44.6%** [41.6, 47.7] of PMEs agree", "**37.1%** [33.7, 40.8] excluding Lucid",
             "Display \"37–45%†\"")
    V.eb_has("B5", "agree **45%** [**37%** excl. Lucid]")
    V.eb_has("D6", "**Junior PMEs: only 29% [25%] familiar.**")
    V.eb_has("D6", "familiar 55% [**44%**]")
    V.eb_has("D7", "**declined 4.4% [7.2%]**")
    V.eb_has("D7b", "likely **lower bound on refusals**", "22/317 = **6.9%** [19/182 = **10.4%**]")
    cr_a, cra = M.one("emp_career.csv", block="career_penalty", sample="all", group="All respondents",
                      item="Agree (4-5)")
    cr_x, crx = M.one("emp_career.csv", block="career_penalty", sample="excl_lucid", group="All respondents",
                      item="Agree (4-5)")
    fam = "Familiar (aware and understand key provisions)"
    jr_a, jra = M.one("emp_tgfwar.csv", block="by_role", sample="all", group="Role: Junior professional / specialist",
                      item=fam)
    jr_x, jrx = M.one("emp_tgfwar.csv", block="by_role", sample="excl_lucid",
                      group="Role: Junior professional / specialist", item=fam)
    dc = {}
    for smp in ("all", "excl_lucid"):
        dc[smp] = M.one("emp_requests.csv", block="outcome", sample=smp,
                        group="Employed who say they made a formal request", item="Yes, but declined")
    for smp, (r, _) in dc.items():   # privacy: no cell below 5
        if int(r["k"]) < 5 or int(r["n"]) < 5:
            sys.exit(f"STOP: {name}: refusal cell {smp} has n < 5")
    raw = {"c": sorted((float(cr_a["share"]), float(cr_x["share"]))),
           "j": sorted((float(jr_a["share"]), float(jr_x["share"]))),
           "d": sorted((float(dc["all"][0]["share"]), float(dc["excl_lucid"][0]["share"])))}
    c_t = pair_range(name, (float(cr_a["share"]), cra, "M23", 44.6, "expect a career penalty, all respondents"),
                     (float(cr_x["share"]), crx, "M23", 37.1, "expect a career penalty, excl. one panel"))
    M.record(name, "(B5 cross-check)", float(cr_a["share"]), cra, "B5", 45, "B5 = M23, all respondents")
    M.record(name, "(B5 cross-check)", float(cr_x["share"]), crx, "B5", 37, "B5 = M23, excl. one panel")
    j_t = pair_range(name, (float(jr_a["share"]), jra, "D6", 29, "junior PMEs familiar, all respondents"),
                     (float(jr_x["share"]), jrx, "D6", 25, "junior PMEs familiar, excl. one panel"))
    # fixer pass 7 Oct 2026 (mom_ps-05 b): all employed PMEs, same base as the junior card (D6, N = 1,004)
    al_a, ala = M.one("emp_tgfwar.csv", block="overall", sample="all", group="All employed", item=fam)
    al_x, alx = M.one("emp_tgfwar.csv", block="overall", sample="excl_lucid", group="All employed", item=fam)
    a_t = pair_range(name, (float(al_a["share"]), ala, "D6", 55, "employed PMEs familiar, all levels, all respondents"),
                     (float(al_x["share"]), alx, "D6", 44, "employed PMEs familiar, all levels, excl. one panel"))
    d_t = pair_range(name, (float(dc["all"][0]["share"]), dc["all"][1], "D7", 4.4,
                            "reported requesters: declined, all respondents"),
                     (float(dc["excl_lucid"][0]["share"]), dc["excl_lucid"][1], "D7", 7.2,
                      "reported requesters: declined, excl. one panel"))
    # D7b: the stricter rate (excl. automatic company-policy FWAs) is higher, which is why 4-7% is a lower bound;
    # recomputed here from the aggregate rows, not drawn
    for smp, eb_v in (("all", 6.9), ("excl_lucid", 10.4)):
        dr, dd = dc[smp]
        pr, _ = M.one("emp_requests.csv", block="request_by_setup", sample=smp,
                      group="Setup: Company-wide policy (applied automatically)", item="Says made a formal FWA request")
        pdc, _ = M.one("emp_requests.csv", block="request_by_setup", sample=smp,
                       group="Setup: Company-wide policy (applied automatically)",
                       item="Declined (among those who say they requested)")
        strict = 100 * (int(dr["k"]) - int(pdc["k"])) / (int(dr["n"]) - int(pr["k"]))
        M.record(name, "(not drawn: supports 'a lower bound')", strict, dd + " minus company-policy setups", "D7b",
                 eb_v, f"declined excl. automatic FWAs, {smp}")
        if strict <= float(dr["share"]):
            sys.exit(f"STOP: {name}: stricter refusal rate is not above the headline rate ({smp})")

    fig = new_fig()
    H, W = fig.H, fig.W
    # Polish pass (7 Oct 2026; DESIGN_PLAN s2 fig_r5; G5, G7): cards in the deck's card style (Soft, square, a PME
    # accent bar, CARD_PAD_CM), headings CARD_HEAD_FS, numbers FS_BIG with an FS_DAG_BIG dagger, white tracks, track
    # ends FS_NOTE, descriptors 9 pt (the longest line, "of junior PMEs are familiar", is 3.98 cm at 9.5 pt in a
    # 4.04 cm card); group headers FS_HEAD over an INK rule; a SEP divider between the two bases. No footnote line:
    # the dagger and "Grey: the gap between the two." are the M-barriers \SourceNote Note.
    gap, sep = 0.18, 0.50
    cw = (W - 0.10 - gap - sep) / 3
    CY0, CY1 = 0.04, H - 0.52
    xs = [0.05, 0.05 + cw + gap, 0.05 + 2 * cw + gap + sep]
    # group headers: not conditional on asking | reported requesters only (conditional on asking)
    # fixer pass 7 Oct 2026 (fact_audit WRONG 3; mom_ps-05 a, worker-10): the junior-PME card's base is employed
    # junior PMEs (D6), so the left header names what the two cards share: neither is conditional on asking
    for x0, x1, s in ((xs[0], xs[1] + cw, "Not conditional on asking"), (xs[2], xs[2] + cw, "Reported requesters")):
        ltext(fig, name, (x0 + x1) / 2, H - 0.21, fit(fig, name, s, FS_HEAD, x1 - x0, "bold"), ha="center",
              va="center", fontsize=FS_HEAD, color=S.INK, fontweight="bold")
        V.hline_cm(fig, x0, x1, H - 0.42, color=S.INK, lw=0.8)
    V.vline_cm(fig, xs[2] - sep / 2, CY0, H - 0.05, **S.SEP)
    cards = [
        ("Career concern", c_t, raw["c"], "of PMEs agree shorter or\nmore flexible hours would\nhurt their career"),
        ("Know the Guidelines", j_t, raw["j"], f"of junior PMEs are familiar\nwith the Guidelines\n(all levels: {a_t}†)"),
        ("Outright refusal", d_t, raw["d"], "of PMEs who report a\nformal request: a\nselected lower bound"),
    ]
    YH = CY1 - S.CARD_BAR_CM - 0.13
    YN = CY1 - 1.48                              # number baseline; the card's content is spread over its height
    YT = CY1 - 2.08
    YD = YT - 0.62
    for x, (hd, rng, (lo, hi), ds) in zip(xs, cards):
        card(fig, x, CY0, cw, CY1 - CY0, S.EMPLOYEE)
        ltext(fig, name, x + cw / 2, YH, fit(fig, name, hd, FS_CARD, cw - 2 * S.CARD_PAD_CM, "bold"), ha="center",
              va="top", fontsize=FS_CARD, color=S.EMPLOYEE, fontweight="bold")
        text_dag(fig, x + cw / 2, YN, rng, FS_BIG, S.EMPLOYEE, weight="bold", ha="center", va="baseline",
                 dag_fs=FS_DAG_BIG, name=name)
        fx = track(fig, x + 0.30, YT, cw - 0.60)
        range_bar(fig, fx, lo, hi, YT, S.EMPLOYEE)
        track_ends(fig, fx, YT)
        lab(name, M.ftext(fig, x + cw / 2, YD - 0.06, fit(fig, name, ds, FS_LAB, cw - 0.2), ha="center", va="top",
                          fontsize=FS_LAB, color=S.INK, linespacing=1.2, multialignment="center"))
    return done(fig, name)


FIGS = {
    "F_org_eqpay": fig_org_eqpay,
    "F_where_r5": fig_where_r5,
    "F_meet_r5": fig_meet_r5,
    "F_puzzle_r5": fig_puzzle_r5,
    "F_barriers_r5": fig_barriers_r5,
}
SLIDE = {
    "F_org_eqpay": "M-employers",
    "F_where_r5": "M-where",
    "F_meet_r5": "M-meet",
    "F_puzzle_r5": "M-puzzle",
    "F_barriers_r5": "M-barriers",
}


def write_manifest(sizes):
    L = ["# Round-5 figures: manifest (written by `deck_support/scripts/fig_r5.py`; do not edit by hand)", "",
         "Re-run: `python3 fig_r5.py` in `deck_support/scripts/`. Output: `final/overleaf/figures/<name>.pdf` (vector, "
         "Arial embedded as TrueType) + `.png` (300 dpi review copy). Each figure is 13.0 x 5.0 cm (F_meet_r5: 14.0 x 4.7 cm, "
         "integrator pass 7 Oct 2026), so `\\FigC{<name>}` prints it at scale 1. Every number drawn is checked against the EVIDENCE_BOOK value "
         "(integers: half-up rounding must match; one-decimal values within 0.05); CI ends drawn but not printed are "
         "listed as '(CI end, unlabelled)'.", ""]
    if M.FLAGS:
        L += ["## Flags", ""] + [f"- {f}" for f in dict.fromkeys(M.FLAGS)] + [""]
    L += ["## Summary", "", "| Figure | Slide | Size (cm, measured) | Every drawn number | Fact IDs |",
          "|---|---|---|---|---|"]
    for name in FIGS:
        if name not in sizes:
            continue
        w, h, _ = sizes[name]
        ents = [e for e in M.LEDGER if e["fig"] == name]
        shown = list(dict.fromkeys(e["shown"] for e in ents if not (e["shown"].startswith("(")
                                                                     and e["shown"].endswith(")"))))
        ids = list(dict.fromkeys(V._fid(e) for e in ents))
        L.append(f"| `{name}` | {SLIDE[name]} | {w:.2f} x {h:.2f} | {'; '.join(shown)} | {', '.join(ids)} |")
    L.append("")
    for name in FIGS:
        if name not in sizes:
            continue
        w, h, _ = sizes[name]
        L += [f"## {name}", "", f"- `\\FigC{{{name}}}` on {SLIDE[name]}; **{w:.2f} x {h:.2f} cm**.", "",
              "| Shown | What | Fact ID (EB value) | Source value | Source row |", "|---|---|---|---|---|"]
        for e in M.LEDGER:
            if e["fig"] != name:
                continue
            raw = "" if e["raw"] is None else f"{e['raw']:.4g}"
            L.append(f"| {e['shown'].replace('|', '/')} | {e['what'].replace('|', '/')} | "
                     f"{e['eb'].replace('|', '/')} | {raw} | {e['row'].replace('|', '/')} |")
        L.append("")
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    return OUT_MD


if __name__ == "__main__":
    warnings.simplefilter("error", UserWarning)
    names = sys.argv[1:] or list(FIGS)
    for nm in names:
        print("wrote", FIGS[nm]())
    sizes = M.measure()
    bad = False
    for nm, (w, h, t) in sizes.items():
        print(f"{nm}: {w:.3f} x {h:.3f} cm (target {t[0]} x {t[1]})")
        bad |= abs(w - t[0]) > 0.02 or abs(h - t[1]) > 0.02
    if not sys.argv[1:]:
        print("manifest:", write_manifest(sizes))
    for fl in dict.fromkeys(M.FLAGS):
        print("FLAG:", fl)
    if bad or M.FLAGS:
        sys.exit(1)


