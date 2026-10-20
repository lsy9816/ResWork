"""restructure_flow2 -- 20 Oct 2026: fold the arrangement-diagnosis slide (M-diag) into M-descriptive and keep M-diag as backup B-fwa-diag.
usage: python3 restructure_flow2.py main.tex   (edits in place)"""
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")

# 1. M-descriptive: new figure, summary, note
a = s.index("\\begin{frame}[t,label=M-descriptive]")
b = s.index("\\end{frame}", a) + len("\\end{frame}")
frame = s[a:b]
new_frame = """\\begin{frame}[t,label=M-descriptive]{WFH is the common FWA; the others are used far less}
  % F_use_m (scripts/fig_fwa_m.py, 13.0 x 4.9 cm) from results_fwa/: firms offering = ticked in QID15 (n = 397); PMEs using = current
  % arrangement (QID31-33), all employed PMEs (n = 1,004); third column = share using among PMEs who have access
  % (available = ticked in QID38 or currently used).
  \\FrameTop
  \\FigC{F_use_m}
  \\Interp{Two in three PMEs already work from home at least one day a week; the other arrangements are used far less.\\\\ Even where available, only about 3 in 10 PMEs use the compressed week, job sharing or part-time.}
  \\SourceNote{Use, if available: share using it among PMEs who have access to it.}
  \\Backups{\\BL{B-landscape}{Landscape}\\BL{B-setup}{Pathways}\\BL{B-fwa-diag}{With pay terms}}
\\end{frame}"""
s = s[:a] + new_frame + s[b:]

# 2. cut M-diag (frame + trailing note) and re-insert as backup B-fwa-diag
m = re.search(r"^\\begin\{frame\}\[t,label=M-diag\]", s, re.M)
a = m.start()
e = s.index("\\end{frame}", a) + len("\\end{frame}")
j = s.index("\\note{", e)
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
blk = s[a:q]
s = s[:a] + s[q:]
blk = blk.replace("label=M-diag", "label=B-fwa-diag", 1)
blk = re.sub(r"\\Backups\{[^\n]*\}\n", "\\\\Backups{\\\\BL{B-fwa-table}{Numbers} \\\\BL{B-fwa-current}{Users vs others}}\n", blk, count=1)
blk = blk.replace("[Short path] This puts", "[Backup] This puts")
anchor = "% Draft for review (19 Oct 2026): the two barrier slides on one page"
assert s.count(anchor) == 1
s = s.replace(anchor, blk + "\n\n" + anchor)
s = s.replace("\\BackTo{M-diag}{Arrangements}", "\\BackTo{B-fwa-diag}{Arrangements}")

# 3. lists and index
s = s.replace("M-meet,M-diag,M-barriers", "M-meet,M-barriers")
s = s.replace("B-fwa-current,B-fwa-table", "B-fwa-diag,B-fwa-current,B-fwa-table", 2)
old = "\\mbox{\\BIi{B-fwa-table}{Numbers}}\\enspace\\textcolor{Muted}{$\\cdot$}\\enspace \\mbox{\\BIi{B-fwa-current}{Users vs others}}\\par"
assert s.count(old) == 1
s = s.replace(old, "\\mbox{\\BIi{B-fwa-diag}{Arrangements}}\\enspace\\textcolor{Muted}{$\\cdot$}\\enspace \\mbox{\\BIi{B-fwa-table}{Numbers}}\\par\n      \\BI{B-fwa-current}{Users vs others}")
assert "{M-diag}" not in s
p.write_text(s, encoding="utf-8")
print("ok")
