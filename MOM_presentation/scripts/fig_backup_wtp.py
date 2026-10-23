"""fig_backup_wtp -- backup figures without the Lucid-excluded values and without equal-pay shares.

The professor's fig_backup.py / fig_v2.py are patched IN MEMORY (text replacements that must match exactly once; the
originals are only read). F_emp_groups and F_org_splits are drawn from data/wtp_deck.csv (pay given up / pay cut required).
usage: BUILD=... OUTDIR=... python3 fig_backup_wtp.py [name ...]   (run after fig_wtp.py's import path setup)
"""
import math
import os
import sys
import types
from pathlib import Path

sys.dont_write_bytecode = True
MOM = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOM / "scripts"))
import fig_wtp as W  # noqa: E402  (sets sys.path, S.FIGDIR; imports fig_main, fig_v2)

S, M, V, D = W.S, W.M, W.V, W.D


def load_patched(modname, reps):
    src = Path(V.__file__).with_name(modname + ".py") if modname == "fig_v2" else Path(M.__file__).with_name(modname + ".py")
    code = src.read_text(encoding="utf-8")
    for old, new in reps:
        if code.count(old) != 1:
            sys.exit(f"STOP: {modname}: patch text not found exactly once: {old[:80]!r}")
        code = code.replace(old, new)
    mod = types.ModuleType(modname + "_wtp")
    mod.__file__ = str(src)
    exec(compile(code, str(src) + " [wtp patch]", "exec"), mod.__dict__)
    return mod


# ---------------------------------------------------------------------------------------------------------------
FB_REPS = [
    # F_landscape: no [excl. one panel] anywhere
    ('f"% of employed PMEs [{EXCL}]"', '"% of employed PMEs"'),
    ('        xw = text_width_cm(fig, f"{fmt_share(a)}%", FS, "bold") / w_l * 100\n'
     '        axl.text(a + 1.5 + xw + 1.5, y, f"[{fmt_share(x)}]", ha="left", va="center", fontsize=FS_SMALL,\n'
     '                 color=S.MUTED)\n', ''),
    ('f"{lab} {fmt(v)}% [{fmt(x)}]"', 'f"{lab} {fmt(v)}%"'),
    # F_awareness: drop the excl. row, the bracket column and its note
    ('        (EXCL[0].upper() + EXCL[1:], *emp_row("overall", "excl_lucid", "All employed"), "emp", None),\n', ''),
    ('        vx, _ = emp_row("by_role", "excl_lucid", g)\n', '        vx = None\n'),
    ('rows.append((lab, v, n, "emp", vx[0]))', 'rows.append((lab, v, n, "emp", None))'),
    ('    ys = [6.0, 5.0, 3.3, 2.4, 1.5, 0.2]\n    for (lab, v, n, side, vx), y in zip(rows, ys):',
     '    ys = [6.0, 3.9, 3.0, 2.1, 0.2]\n    for (lab, v, n, side, vx), y in zip(rows, ys):'),
    ('    ax.text(-0.15 * upc, 4.12, "By role:"', '    ax.text(-0.15 * upc, 4.62, "By role:"'),
    ('    ax.text(100 + 0.15 * upc, 4.12, f"[{EXCL}]", ha="left", va="center", fontsize=FS_SMALL, color=S.MUTED)\n', ''),
    ('"PMEs: employed (n). [ ] = % familiar, excl. one panel. Unweighted."', '"PMEs: employed (n). Unweighted."'),
    ('    w_br = text_width_cm(fig, f"[{EXCL}]", FS_SMALL) + 0.20\n', '    w_br = 0.05\n'),
    # F_career: one series, adjusted gaps from the full sample
    ('                                       (mk(S.EMPLOYEE, filled=False), f"[{EXCL}, N = {ex[1]}]", S.MUTED),\n', ''),
    ('            b, _ = get(block, item, g, "excl_lucid")\n', '            b = a\n'),
    ('            ax.plot([min(a, b), max(a, b)], [y, y], color=S.RULE, lw=1.0, zorder=2)   # v3: neutral, no tint\n'
     '            point(ax, b, y, mk(S.EMPLOYEE, filled=False), z=3)\n', ''),
    ('            xb = xa + (text_width_cm(fig, f"{fmt(a)}%", FS, "bold") + 0.08) * upc\n'
     '            ax.text(xb, y, f"[{fmt(b)}]", ha="left", va="center", fontsize=FS_SMALL, color=S.MUTED, clip_on=False)\n', ''),
    ('vw = text_width_cm(fig, "45%", FS, "bold") + text_width_cm(fig, "[37]", FS_SMALL) + 0.40',
     'vw = text_width_cm(fig, "45%", FS, "bold") + 0.30'),
    ('return one(crk, analysis="A1b_care", sample="excl",', 'return one(crk, analysis="A1b_care", sample="all",'),
    ('f"Career item, adjusted, excl. one panel: child 0–6 +{fmt(kid_ame)} pp (10% level), any caregiving"\n'
     '                     f" +{fmt(any_ame)} pp (n.s.).",',
     'f"Career item, adjusted: child 0–6 +{fmt(kid_ame)} pp (p = .001), any caregiving"\n'
     '                     f" +{fmt(any_ame)} pp (p = .01).",'),
    # F_approvals_two: one sample
    ('    samples = [("all", "Full sample"), ("excl_lucid", EXCL[0].upper() + EXCL[1:])]', '    samples = [("all", "All PMEs")]'),
    ('    for smp, exp, n_exp in (("all", (64, 32, 4.4), 547), ("excl_lucid", (51, 42, 7.2), 278)):',
     '    for smp, exp, n_exp in (("all", (64, 32, 4.4), 547),):'),
    ('    note_lines(fig, ["Excl.: drops one lower-quality panel. Unweighted."])', '    note_lines(fig, ["Unweighted."])'),
    # F_sample: no bracket
    ('                if (b, it) == ("role_level", "Senior management"):   # [excl. one panel], as on F_career\n'
     '                    xv = xb + v / XMAX * BL + 0.07 + text_width_cm(fig, f"{fmt(v)}%", FS_SMALL, "bold") + 0.08\n'
     '                    text_cm(fig, xv, y, f"[{fmt(sen_ex)}]", ha="left", va="center", fontsize=FS_SMALL, color=S.MUTED)\n', ''),
    ('f"{pnts[2]} PMEs ({fmt(pnts[0], 1)}%) gave no gender. [ ] = {EXCL}."', 'f"{pnts[2]} PMEs ({fmt(pnts[0], 1)}%) gave no gender."'),
    # figures carry no subtitle (the slide title and caption say what is shown); no in-figure notes
    ('    head(fig, 0.05, H - 0.22, "Share of pairs, %")\n', ''),
    ('    head(fig, 0.05, H - 0.22, "% of pay workers would give up for WFH")\n', ''),
    ('    note_lines(fig, pl)\n', ''),
    ('    ay = 1.18\n    ax = axes_cm(fig, x_ax, ay, axw, H - ay - 0.44)', '    ay = 0.60\n    ax = axes_cm(fig, x_ax, ay, axw, H - ay - 0.30)'),
    ('    head(fig, 0.05, H - 0.22, "% of PMEs (n)")\n', ''),
    # F_sample: "prefer not to say" is a gender row (no note); the two headers are centred over their columns
    ('[("Gender", [("Men", "gender", "Male"), ("Women", "gender", "Female")]),',
     '[("Gender", [("Men", "gender", "Male"), ("Women", "gender", "Female"),\n'
     '                      ("Prefer not to say", "gender", "Prefer not to say")]),'),
    ('+ (pnts[2] if title == "Gender" else 0)', '+ 0'),
    ('text_cm(fig, xb + v / XMAX * BL + 0.07, y, f"{fmt(v)}%", ha="left", va="center", fontsize=FS_SMALL,',
     'text_cm(fig, xb + v / XMAX * BL + 0.07, y, f"{fmt(v, 1) if v < 1 else fmt(v)}%", ha="left", va="center", fontsize=FS_SMALL,'),
    ('    note_lines(fig, [f"{pnts[2]} PMEs ({fmt(pnts[0], 1)}%) gave no gender."])\n', ''),
    ('    fig = canvas(W_BK, 4.8)                        # polish pass: 14.5 cm wide (was 14.0); still scale 1',
     '    fig = canvas(W_BK, 5.2)'),
    ('    text_cm(fig, 0.08, H - 0.24, f"PMEs (n = {n_pme:,})", ha="left", va="center", fontsize=FS_HEAD,',
     '    text_cm(fig, (0.08 + cols[1][0] + cols[1][1] + BL + VAL_W) / 2, H - 0.24, f"PMEs (n = {n_pme:,})", ha="center", va="center", fontsize=FS_HEAD,'),
    ('    text_cm(fig, split + 0.25, H - 0.24, f"Employers (n = {n_org:,})", ha="left", va="center", fontsize=FS_HEAD,',
     '    text_cm(fig, split + 0.25 + (lw_o[0] + BL + VAL_W) / 2, H - 0.24, f"Employers (n = {n_org:,})", ha="center", va="center", fontsize=FS_HEAD,'),
    # F_landscape: the take-up line is in B-fwa-table; no in-figure footnote
    ('    text_cm(fig, 0.05, 0.50, tk, ha="left", va="center", fontsize=FS_SMALL)\n', ''),
    ('    text_cm(fig, 0.05, 0.21, "Take-up = % using it among those with access (available or used).", ha="left",\n'
     '            va="center", fontsize=FS_SMALL, color=S.MUTED)\n', ''),
    # F_career: no in-figure footnotes; one key (dashed line) at the bottom, centred
    ('    key_row(fig, W - 0.05, H - 0.22, [(mk(S.EMPLOYEE), "full sample", S.MUTED),\n'
     '                                       (None, "dashed: one third", S.MUTED)], ha="right")\n',
     '    key_row(fig, (W - text_width_cm(fig, "dashed line: one third", FS_SMALL)) / 2, 0.30,\n'
     '            [(None, "dashed line: one third", S.MUTED)])\n'),
    ('    note_lines(fig, [f"Career item, adjusted: child 0–6 +{fmt(kid_ame)} pp (p = .001), any caregiving"\n'
     '                     f" +{fmt(any_ame)} pp (p = .01).",\n'
     '                     f"Other gaps not tested. PAP–NTUC survey ({ntuc_when}): {ntuc_stigma}% named stigma their primary"\n'
     '                     " concern."])\n', ''),
    # F_ra_*: no head, no footnote markers or note, no n in the key; key at the bottom, centred
    ('("3.place", "Fully remote¹"),   # polish', '("3.place", "Fully remote"),   # polish'),
    ('("1.load", "Job sharing²"), ("2.load", "Part-time²")]', '("1.load", "Job sharing"), ("2.load", "Part-time")]'),
    ('    AY = 0.98                                         # declutter: one footnote line (was two)\n'
     '    AW, AH = W - X0 - 0.40, H - AY - 0.86\n', '    AY = 1.25\n    AW, AH = W - X0 - 0.40, H - AY - 0.20\n'),
    ('    head(fig, 0.05, H - 0.22, "% of monthly pay given up (indicative)")\n', ''),
    ('    key_row(fig, 0.05, H - 0.58, [(RA_STYLE[style], f"{lab} ({ns[int(g)]:,})", S.INK) for g, lab, style in groups]\n'
     '            + [(None, "lines: 95% CI", S.MUTED)], fs=FS, gap=0.40)\n',
     '    _it = [(RA_STYLE[style], lab, S.INK) for g, lab, style in groups]\n'
     '    _tw = sum(0.34 + text_width_cm(fig, t, FS) for _, t, _ in _it) + 0.40 * (len(_it) - 1)\n'
     '    key_row(fig, (W - _tw) / 2, 0.30, _it, fs=FS, gap=0.40)\n'),
    ('    note_lines(fig, ["¹ vs onsite, >45 min commute. ² Fewer hours, same monthly pay. Base: onsite, fixed hours,"\n'
     '                     " full-time."])\n', ''),
]

V2_REPS = [
    ('    a_ex, da_ex, _ = sh("excl", "All respondents")\n    all_t = range_text(name, (a_all, da_all, "M23", 44.6, "all PMEs agree, all respondents (dotted line)"),\n'
     '                       (a_ex, da_ex, "M23", 37.1, "all PMEs agree, excl. one panel (dotted line)"))\n',
     '    a_ex = a_all\n    all_t = f"{int(M.half_up(a_all))}%"\n'),
    ('            vx, dx_, rx = sh("excl", grp)\n', '            vx, dx_, rx = va_, da, ra\n'),
    ('            txt = range_text(name, (va_, da, eid, ebv[0], f"agree, {lab}, all respondents"),\n'
     '                             (vx, dx_, eid, ebv[1], f"agree, {lab}, excl. one panel"))\n',
     '            txt = f"{int(M.half_up(va_))}%"\n'),
    ('            # dumbbell: grey connector; filled = all respondents, hollow = excluding one panel\n'
     '            ax.plot([min(va_, vx), max(va_, vx)], [y, y], color=S.GREY_MID, lw=S.CI_LW, solid_capstyle="butt",\n'
     '                    zorder=2)\n'
     '            ax.plot([vx], [y], marker="o", ms=S.MS_CIRCLE, mfc="white", mec=S.EMPLOYEE, mew=S.MEW_HOLLOW, ls="none",\n'
     '                    zorder=3)\n', ''),
    ('ax.text(max(va_, vx) + 2.2, y, nodag(txt) + DAGGER,', 'ax.text(max(va_, vx) + 2.2, y, txt,'),
    ('f"% agreeing (dotted: all PMEs, {nodag(all_t)}{DAGGER})"', 'f"% agreeing (dotted: all PMEs, {all_t})"'),
    ('    rx, dx_ = mone(CR, analysis="A3_request", sample="excl", outcome="req", model="logit_ctrl",\n'
     '                   term="1.impact_agree", metric="AME_pp")\n', ''),
    ('    axl = M.record(name, f"+{M.pint(float(rx[\'est\']))} pp", float(rx["est"]), dx_ + " (est)", "M27", 15.8,\n'
     '                   "AME excl. one panel (pp)")\n', ''),
    ('               ("after controls (excl. one panel: " + axl + ").", S.FS_NOTE, S.INK, "normal", 0.42),',
     '               ("after controls.", S.FS_NOTE, S.INK, "normal", 0.42),'),
    ('    keys = [("o", S.EMPLOYEE, S.EMPLOYEE, S.MS_CIRCLE, "all", S.MUTED, "normal"),\n'
     '            ("o", "white", S.EMPLOYEE, S.MS_CIRCLE, "excl. one panel (†)", S.MUTED, "normal")]\n', '    keys = []\n'),
    ('    xk = r5_key(fig, 0.05, 0.40 + 0.09, keys, fs=S.FS_NOTE, gap=0.30) + 0.35', '    xk = 0.05'),
    ('    head(fig, name, "Establishments (25+ staff, incl. public sector) offering a scheduled FWA, %")\n', ''),
    # F_motivation: key at the bottom, centred (not inside the plot)
    ('    X0, X1, Y0, Y1 = 1.12, W - 0.10, 0.55, H - 0.78', '    X0, X1, Y0, Y1 = 1.12, W - 0.10, 1.05, H - 0.30'),
    ('    r5_key(fig, X0 + (2008.3 - XA) / (XB - XA) * (X1 - X0), Y0 + 0.10 * (Y1 - Y0),\n'
     '           [("o", FIRM, FIRM, S.MS_CIRCLE, "CoE Survey", S.INK, "normal"),\n'
     '            ("o", "white", FIRM, S.MS_CIRCLE, "Supplementary Survey", S.INK, "normal")])\n',
     '    _k = [("o", FIRM, FIRM, S.MS_CIRCLE, "CoE Survey", S.INK, "normal"),\n'
     '          ("o", "white", FIRM, S.MS_CIRCLE, "Supplementary Survey", S.INK, "normal")]\n'
     '    r5_key(fig, (W - key_width(fig, _k)) / 2, 0.16, _k)\n'),
]


def run_patched():
    fb = load_patched("fig_backup", FB_REPS)
    fb.S.FIGDIR = S.FIGDIR
    v2 = load_patched("fig_v2", V2_REPS)
    out = {}
    for n in ("fig_landscape", "fig_awareness", "fig_career", "fig_approvals_two", "fig_sample", "fig_benchmarks", "fig_paygaps"):
        out["F_" + n[4:]] = getattr(fb, n)
    out["F_career_who"] = v2.fig_career_who
    out["F_motivation"] = v2.fig_motivation
    for sheet, groups, nm, rob in fb.RA_FIGS[:5]:
        out[nm] = (lambda sheet=sheet, groups=groups, nm=nm, rob=rob: fb.fig_ra(sheet, groups, nm, rob))
    return out


# ---------------------------------------------------------------------------------------------------------------
def fig_emp_groups():
    name = "F_emp_groups"
    SZ = (14.5, 5.2)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    levels = [("p1", "1–2 days"), ("p2", "3–4 days"), ("p3", "Remote"), ("t2", "Compressed")]
    rows = [("main", 0, "All PMEs (1,020)")]
    for sp, labs in (("gender", ("Men", "Women")), ("age", ("Aged 19–39", "Aged 40+")),
                     ("care_type", ("No caregiving", "Other caregiving", "Child aged 0–6"))):
        for g, lab in enumerate(labs):
            n = int(D[(D.side == "pme") & (D.split == sp) & (D.group == g) & (D["item"] == "p1")].n.iloc[0])
            if sp == "care_type":
                n = (360, 402, 258)[g]
            rows.append((sp, g, f"{lab} ({n})"))
    ys, y = [], 9.6
    for i, r in enumerate(rows):
        ys.append(y)
        y -= 0.85
        if i < len(rows) - 1 and rows[i + 1][0] != r[0]:
            y -= 0.45
    LX = 0.05 + max(V.tw_cm(fig, r[2], S.FS_ROW) for r in rows)
    PCW = 0.0   # no test column: the intervals carry the comparison
    PX0, GAP = LX + 0.15, 0.30
    PW = (Wd - 0.05 - PCW - 0.20 - PX0 - 3 * GAP) / 4
    AY, AT = 1.20, H - 0.55
    YA_, YB_ = min(ys) - 0.6, 10.2

    def fy(v):
        return AY + (v - YA_) / (YB_ - YA_) * (AT - AY)
    for j, (it, title) in enumerate(levels):
        ax = M.axes_cm(fig, PX0 + j * (PW + GAP), AY, PW, AT - AY)
        ax.set_xlim(-3, 31)
        ax.set_ylim(YA_, YB_)
        S.ref_line(ax, 0, YA_, YB_)
        for (sp, g, lab), yy in zip(rows, ys):
            if sp == "main":
                e, lb, ub = W.tri("pme", it)
            else:
                q = D[(D.side == "pme") & (D.split == sp) & (D.group == g) & (D["item"] == it)].iloc[0]
                e, lb, ub = q.giveup, q.lb, q.ub
            ax.plot([lb, ub], [yy, yy], color=S.EMPLOYEE, lw=S.CI_LW, solid_capstyle="butt", zorder=2)
            filled = sp == "main" or g >= 1
            ax.plot([e], [yy], marker="o", ms=S.MS_CIRCLE, mfc=S.EMPLOYEE if filled else "white",
                    mec="white" if filled else S.EMPLOYEE, mew=S.MEW if filled else S.MEW_HOLLOW, ls="none", zorder=3)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(S.RULE)
        S.pct_ticks(ax, [0, 10, 20, 30])
        M.ftext(fig, PX0 + j * (PW + GAP) + PW / 2, AT + 0.08, title, ha="center", va="bottom", fontsize=S.FS_HEAD,
                fontweight="bold", color=S.EMPLOYEE)
    for (sp, g, lab), yy in zip(rows, ys):
        M.ftext(fig, LX, fy(yy), lab, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK,
                fontweight="bold" if sp == "main" else "normal")
    for i in range(1, len(rows)):
        if rows[i][0] != rows[i - 1][0]:
            V.hline_cm(fig, 0.05, Wd - 0.05, fy((ys[i] + ys[i - 1]) / 2), **S.SEP)
    W.nohead(fig, name, "Pay PMEs would give up, % of monthly pay")
    keys = [("o", "white", S.EMPLOYEE, S.MS_CIRCLE, "first group listed", S.INK, "normal"),
            ("o", S.EMPLOYEE, S.EMPLOYEE, S.MS_CIRCLE, "No", S.INK, "normal")]
    V.r5_key(fig, (Wd - V.key_width(fig, keys, gap=0.35)) / 2, 0.16, keys, gap=0.35)
    V.outside(fig, name)
    return M.finish(fig, name, SZ)


def bh(ps):
    n = len(ps)
    order = sorted(range(n), key=lambda i: ps[i])
    q = [0.0] * n
    prev = 1.0
    for rank in range(n, 0, -1):
        i = order[rank - 1]
        prev = min(prev, ps[i] * n / rank)
        q[i] = prev
    return q


SPL_ROWS = [  # split, label, feature group (0 = first listed in the data), n label groups
    ("physical", "Most roles need presence", 0), ("curwfh", "No WFH today", 1), ("creat", "Creativity suffers apart", 0),
    ("concern", "High overall concern", 0), ("prod", "Productivity worry", 0), ("coord", "Coordination worry", 0),
    ("belief", "Salary offset belief", 0), ("policy", "No written policy", 1)]


def split_tests():
    """p (location WTPs equal, free pay slope) per split; q = Benjamini-Hochberg over the 11 joint tests."""
    names = [s for s, _, _ in SPL_ROWS] + ["size", "tech", "role"]
    ps = [W.get("emp", "ratio_p", split=s, group=-1) for s in names]
    q = bh(ps)
    return dict(zip(names, zip(ps, q)))


def fig_org_splits():
    name = "F_org_splits"
    SZ = (14.5, 5.4)
    fig = M.new_fig(*SZ)
    Wd, H = fig.W, fig.H
    levels = [("p1", "1–2 days"), ("p2", "3–4 days"), ("p3", "Remote")]
    tests = split_tests()
    labs = []
    for s, lab, g in SPL_ROWS:
        n1 = int(D[(D.side == "emp") & (D.split == s) & (D.group == g) & (D["item"] == "p1")].n.iloc[0])
        n0 = int(D[(D.side == "emp") & (D.split == s) & (D.group == 1 - g) & (D["item"] == "p1")].n.iloc[0])
        labs.append(f"{lab}  {n1} / {n0}")
    LX = 0.05 + max(V.tw_cm(fig, t, S.FS_ROW) for t in labs)
    PX0, GAP = LX + 0.15, 0.25
    PW_, QW_ = 0.45, 0.0   # no p and q columns: the intervals carry the comparison
    PW = (Wd - 0.05 - PW_ - QW_ - PX0 - 3 * GAP) / 3
    AY, AT = 1.20, H - 0.55
    n = len(SPL_ROWS)
    ys = [n - i for i in range(n)]
    YA_, YB_ = 0.4, n + 0.6

    def fy(v):
        return AY + (v - YA_) / (YB_ - YA_) * (AT - AY)
    for j, (it, title) in enumerate(levels):
        ax = M.axes_cm(fig, PX0 + j * (PW + GAP), AY, PW, AT - AY)
        ax.set_xlim(-35, 100)
        ax.set_ylim(YA_, YB_)
        S.ref_line(ax, 0, YA_, YB_)
        for (s, lab, g), yy in zip(SPL_ROWS, ys):
            for gi, filled in ((g, True), (1 - g, False)):
                q = D[(D.side == "emp") & (D.split == s) & (D.group == gi) & (D["item"] == it)].iloc[0]
                dy = 0.17 if filled else -0.17
                ax.plot([q.lb, q.ub], [yy + dy] * 2, color=S.EMPLOYER, lw=1.0, solid_capstyle="butt", zorder=2)
                ax.plot([q.giveup], [yy + dy], marker="D", ms=4.6, mfc=S.EMPLOYER if filled else "white",
                        mec="white" if filled else S.EMPLOYER, mew=S.MEW if filled else S.MEW_HOLLOW, ls="none", zorder=3)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(S.RULE)
        S.pct_ticks(ax, [0, 50, 100])
        M.ftext(fig, PX0 + j * (PW + GAP) + PW / 2, AT + 0.08, title, ha="center", va="bottom", fontsize=S.FS_HEAD,
                fontweight="bold", color=S.EMPLOYER)
    for (s, lab, g), yy, t in zip(SPL_ROWS, ys, labs):
        M.ftext(fig, LX, fy(yy), t, ha="right", va="center", fontsize=S.FS_ROW, color=S.INK)
    M.ftext(fig, 0.05, AT + 0.08, "n: yes / no", ha="left", va="bottom", fontsize=S.FS_CAP, color=S.MUTED)
    W.nohead(fig, name, "Pay cut employers would require, % of pay")
    keys = [("D", S.EMPLOYER, S.EMPLOYER, 4.6, "Yes", S.INK, "normal"),
            ("D", "white", S.EMPLOYER, 4.6, "No", S.INK, "normal")]
    V.r5_key(fig, (Wd - V.key_width(fig, keys, gap=0.35)) / 2, 0.16, keys, gap=0.35)
    V.outside(fig, name)
    return M.finish(fig, name, SZ)


if __name__ == "__main__":
    import warnings
    warnings.simplefilter("default")
    patched = run_patched()
    figs = {**patched, "F_emp_groups": fig_emp_groups, "F_org_splits": fig_org_splits}
    for nm in sys.argv[1:] or list(figs):
        print("wrote", figs[nm]())
    for fl in dict.fromkeys(M.FLAGS):
        print("FLAG:", fl)
