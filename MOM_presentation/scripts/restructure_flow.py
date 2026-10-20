"""restructure_flow -- one-off edit of overleaf_upload/main.tex for the revised main-slide flow (19-20 Oct 2026).

Main flow after this edit: title, motivation, question, benchmark (new), data, design+estimation (merged), current use,
PMEs' value, career concern, employers' required cut, where employers differ, gap, arrangement diagnosis (new), PME barriers,
employer barriers (new), zones/policy, options, limits, conclusion, thanks.
Moved to the backups (not deleted): M-literature, M-framework, M-estimation, M-groups, M-robust, M-puzzle.
New backups: B-barriers-both (draft of a merged barriers slide), B-fwa-current, B-fwa-table.
usage: python3 restructure_flow.py main.tex      (edits in place; asserts every step)
"""
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")


def strip_comment(line):
    return re.sub(r"(?<!\\)%.*$", "", line)


def block(label):
    """(start, end) character offsets of a frame, its leading comment lines and its trailing comments/\\note{...}"""
    m = re.search(r"^\\begin\{frame\}\[[^\]]*label=%s[\],]" % re.escape(label), s, re.M)
    assert m, label
    start = m.start()
    # leading contiguous comment lines
    lines_before = s[:start].split("\n")
    i = len(lines_before) - 1            # last element is the (empty) text before the match on its line
    k = i
    while k - 1 >= 0 and lines_before[k - 1].startswith("%") and not lines_before[k - 1].startswith("% ====") \
            and not lines_before[k - 1].startswith("% ####"):
        k -= 1
    start = sum(len(x) + 1 for x in lines_before[:k])
    e = s.index("\\end{frame}", m.start()) + len("\\end{frame}")
    pos = e
    rest = s[pos:]
    # trailing: comment lines, then optional \note{...}
    out = pos
    mm = re.match(r"(?:[ \t]*\n)*", rest)
    j = pos + mm.end()
    while True:
        line_end = s.find("\n", j)
        line = s[j:line_end if line_end != -1 else len(s)]
        if line.startswith("%") and not line.startswith("% ====") and not line.startswith("% ####"):
            j = line_end + 1
            out = j
            continue
        break
    if s.startswith("\\note{", j):
        depth, q = 0, j
        while True:
            ch = s[q]
            if ch == "\\":
                q += 2
                continue
            if ch == "%":
                q = s.index("\n", q)
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    q += 1
                    break
            q += 1
        out = q
        nl = s.find("\n", out)
        out = nl + 1 if nl != -1 else out
    else:
        out = max(out, pos)
        out = s.find("\n", out) + 1 if not s[out:out + 1] == "\n" else out + 1
    return start, out


def take(label):
    global s
    a, b = block(label)
    txt = s[a:b]
    s = s[:a] + s[b:]
    return txt


# ---------------------------------------------------------------- 1. move six main frames to the backups
RENAME = {"M-literature": "B-literature", "M-framework": "B-framework", "M-estimation": "B-estimation",
          "M-groups": "B-groups", "M-robust": "B-robust", "M-puzzle": "B-puzzle-main"}
moved = {}
for old, new in RENAME.items():
    moved[new] = take(old).replace(f"label={old}", f"label={new}", 1)
for old, new in RENAME.items():
    s = s.replace("{%s}" % old, "{%s}" % new)            # every \hyperlink / \BL / \BackTo target
assert not re.search(r"label=M-(literature|framework|estimation|groups|robust|puzzle)[\],]|\{M-(literature|framework|estimation|groups|robust|puzzle)\}", s)

# ---------------------------------------------------------------- 2. merge estimation into the design slide

marker = "      at (7.31,-4.75) {Two attributes differ in each choice; which ones, and their levels, are randomized.};"
assert s.count(marker) == 1
s = s.replace(marker, marker.replace("-4.75", "-4.65"))
i = s.index(marker.replace("-4.75", "-4.65"))
j = s.index("  \\end{tikzpicture}\\par}", i)
STRIP = (
    "    % how values are calculated (was the separate estimation slide, now B-estimation)\n"
    "    \\foreach \\x/\\n/\\t in {0/1/{Each PME or employer makes six choices},\n"
    "                          5.00/2/{We estimate how pay and each arrangement shift the choices},\n"
    "                          10.00/3/{We convert this into the \\textbf{\\% of pay} each side would give up or require}} {\n"
    "      \\node[deckcard,anchor=north west,inner xsep=0.10cm,inner ysep=0.08cm,minimum width=4.76cm,text width=4.42cm,\n"
    "        text=Ink,font=\\FsSmall,align=left] (st\\n) at (\\x,-5.25) {{\\color{Navy}\\bfseries\\n}\\hspace{0.10cm}\\t};\n"
    "      \\fill[Navy] (st\\n.north west) rectangle ([xshift=0.06cm]st\\n.south west);}\n")
s = s[:j] + STRIP + s[j:]

# ---------------------------------------------------------------- 4. new main slides
M_DIAG = r"""
\begin{frame}[t,label=M-diag]{Offering, use and pay terms differ across arrangements}
  % F_fwa_diag_m (scripts/fig_fwa_m.py, 14.4 x 5.0 cm) from results_fwa/ (scripts/fwa_diagnosis.py): firms offering = ticked
  % in QID15 (as M-descriptive); PMEs using = current arrangement (QID31-33), employed PMEs n = 1,004; "use, if available" =
  % share using among PMEs with access (available = ticked or currently used); pay terms as M-meet (1--2 days WFH on the WFH row).
  \FrameTop
  \FigC{F_fwa_diag_m}
  \Interp{The compressed week is the one that both sides value alike, yet only 17\% of firms offer it.\\ For job sharing and part-time, employers ask for 24--36\% against 4--6\% from PMEs.}
  \SourceNote{Use, if available: share of PMEs using it among those who have access to it.}
  \Backups{\BL{B-fwa-table}{Numbers} \BL{B-fwa-current}{Users vs others}}
\end{frame}
\note{[Short path] This puts the five arrangements side by side. Left: the share of firms that offer each, and the share of PMEs who use it; then, among PMEs who have it available, the share who use it. Right: the pay PMEs would give up and the pay cut employers would require, as on the previous slide. % [D1, M16, E-series, R-series]
Three patterns. First, WFH: widely offered and used (78 per cent of firms, 66 per cent of PMEs, 87 per cent take-up where available), but employers require much more than PMEs give up. Second, the compressed week: both sides accept about 7 per cent, yet only 17 per cent of firms offer it and 6 per cent of PMEs use it, 31 per cent of those who have it. Third, job sharing and part-time: employers ask for 24 and 36 per cent against 6 and 4 per cent from PMEs; both cut hours, so much of the employers' number is simply pay for fewer hours. Staggered hours are offered by 37 per cent of firms and PMEs place little value on them. % [S1, S2]
Take-up among those with access is 31, 27 and 26 per cent for the compressed week, job sharing and part-time, against 69 per cent for staggered hours and 87 per cent for WFH. These are our samples, not national rates; we did not ask why PMEs who have an arrangement do not use it. [Backup: numbers; users against others.]}

"""
M_EMP_BARR = r"""
\begin{frame}[t,label=M-employer-barriers]{Employers name productivity, coordination and fairness}
  % F_fwa_challenge_m (scripts/fig_fwa_m.py): QID50 biggest challenge in offering FWAs, all 397 employers incl. Other
  \FrameTop
  \FigC{F_fwa_challenge_m}
  \Interp{Productivity, coordination and fairness are each named by about a quarter of employers.\\ Digital infrastructure and security matter much less (6\% each).}
  \Backups{\BL{B-barriers-both}{Both sides} \BL{B-org-view}{Employer view}}
\end{frame}
\note{[Short path] Asked for the biggest challenge in offering flexible arrangements, employers name productivity and output quality (24 per cent), team coordination (24) and fairness across roles (23). Managerial resistance or lack of trust follows (14). Digital infrastructure and security are named by 6 per cent each. % [B1, fwa_challenge]
The three leading items are statistically indistinguishable in this sample. The question asks for one challenge for FWAs in general, not for each arrangement, so it cannot say why a given arrangement, such as the compressed week, is offered by few firms. % [B1]
Next, how the evidence maps to the three zones.}

"""
B_BOTH = r"""
% Draft for review (19 Oct 2026): the two barrier slides on one page, to judge how busy it looks.
\begin{frame}[t,label=B-barriers-both]{Barriers on both sides (draft of a merged slide)}
  \FrameTop
  \FigC{F_barriers_both_m}
  \Interp{PMEs: career worries and little knowledge of the Guidelines.\\ Employers: productivity, coordination and fairness.}
  \BackToTwo{M-barriers}{PME barriers}{M-employer-barriers}{Employer concerns}
\end{frame}

\begin{frame}[t,label=B-fwa-current]{Current users value part-time and staggered hours more}
  % F_fwa_current_m (scripts/fig_fwa_m.py) from results_fwa/fwa_current.csv: current-arrangement interaction model of
  % code_final.do, employed PMEs with all three current-arrangement answers (n = 1,004)
  \FrameTop
  \FigC{F_fwa_current_m}
  \Interp{Users give up more for part-time (14 points) and staggered hours (6), but not for WFH.}
  \SourceNote{Users may differ from non-users in other ways; the gap is not an effect of using it.}
  \BackTo{M-diag}{Arrangements}
\end{frame}

\begin{frame}[t,label=B-fwa-table]{Offering, use and pay terms: numbers}
  \FrameTop % first body token (centring; never a frame subtitle)
  \Tab{T_fwa_diag}
  \BackTo{M-diag}{Arrangements}
\end{frame}

"""

# main slides: diag after M-meet, employer barriers after M-barriers
def insert_after(label, text):
    global s
    a, b = block(label)
    s = s[:b] + text + s[b:]


insert_after("M-meet", M_DIAG)
insert_after("M-barriers", M_EMP_BARR)

# ---------------------------------------------------------------- 5. backups: moved frames + new ones, before the first content backup
anchor = re.search(r"^% =+\n% Motivation and question\n% =+\n", s, re.M)
assert anchor
insert = ("% ==========================================================================\n"
          "% Slides moved out of the main flow (19-20 Oct 2026): kept as backups\n"
          "% ==========================================================================\n"
          + "".join(moved[k] + "\n" for k in ("B-literature", "B-framework", "B-estimation", "B-groups", "B-robust", "B-puzzle-main"))
          + B_BOTH)
s = s[:anchor.start()] + insert + s[anchor.start():]

# ---------------------------------------------------------------- 6. indexes and short-path lists
NEWB = ",".join(["B-literature", "B-framework", "B-estimation", "B-groups", "B-robust", "B-puzzle-main", "B-barriers-both",
                 "B-fwa-current", "B-fwa-table"])
s = s.replace("M-question,M-framework,M-design,M-pmes,M-why-pmes,M-employers,M-where,M-meet,M-puzzle,M-barriers,M-options",
              "M-question,M-benchmark,M-design,M-pmes,M-why-pmes,M-employers,M-where,M-meet,M-diag,M-barriers,M-employer-barriers,M-options")
s = s.replace("B-index,B-index-all,B-laboursupply", "B-index,B-index-all," + NEWB + ",B-laboursupply", 1)
OLD1 = r"""      \mbox{\BIi{B-intl}{Evidence elsewhere}}\enspace\textcolor{Muted}{$\cdot$}\enspace \mbox{\BIi{B-zones}{Zone rules}}\par"""
NEW1 = OLD1 + "\n" + r"""      \mbox{\BIi{B-literature}{Literature}}\enspace\textcolor{Muted}{$\cdot$}\enspace \mbox{\BIi{B-framework}{Framework}}\par"""
assert s.count(OLD1) == 1
s = s.replace(OLD1, NEW1)
OLD2 = r"""      \BI{B-methods}{Equations}"""
NEW2 = r"""      \mbox{\BIi{B-methods}{Equations}}\enspace\textcolor{Muted}{$\cdot$}\enspace \mbox{\BIi{B-estimation}{Estimation}}\par"""
assert s.count(OLD2) == 1
s = s.replace(OLD2, NEW2)
OLD3 = r"""      \mbox{\BIi{B-org-pct}{Employer \% of salary}}\enspace\textcolor{Muted}{$\cdot$}\enspace \mbox{\BIi{B-gap}{Gap}}\par"""
NEW3 = OLD3 + "\n" + r"""      \mbox{\BIi{B-fwa-table}{Numbers}}\enspace\textcolor{Muted}{$\cdot$}\enspace \mbox{\BIi{B-fwa-current}{Users vs others}}\par
      \BI{B-barriers-both}{Both sides}"""
assert s.count(OLD3) == 1
s = s.replace(OLD3, NEW3)
OLD4 = r"""      \mbox{\BIi{B-ra-sameside}{Same-side}}\enspace\textcolor{Muted}{$\cdot$}\enspace \mbox{\BIi{B-ra-trim}{Trim}}\par"""
NEW4 = OLD4 + "\n" + r"""      \mbox{\BIi{B-groups}{Subgroups}}\enspace\textcolor{Muted}{$\cdot$}\enspace \mbox{\BIi{B-robust}{Robustness}}\par
      \BI{B-puzzle-main}{Compressed week (main slide)}"""
assert s.count(OLD4) == 1
s = s.replace(OLD4, NEW4)
p.write_text(s, encoding="utf-8")
print("ok", len(s))
