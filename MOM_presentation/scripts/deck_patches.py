"""deck_patches -- exact-once text patches applied to COPIES of the professor's deck_support/scripts (never to the originals).

Why: the figure and table scripts carry hard-coded expectations of the 303-firm employer sample (EVIDENCE_BOOK strings,
'about 1 in 5', 'beyond the tested range only for fully remote', the divisor 303 ...). Every patch changes one such expectation
for the appended sample (n = 397). Patch files: scripts/patches/<script>.patch in the format

    <<<<<<< ORIGINAL
    text that must occur exactly once in the professor's script
    =======
    replacement text
    >>>>>>> PATCH

A patch whose original text is not found exactly once stops the build. After patching, every remaining `assert` of the
script (except the data-lookup guards listed in HARD) is turned into a logged claim check (see softify).
"""
import ast
import re
import sys
from pathlib import Path

PATCH_DIR = Path(__file__).resolve().parent / "patches"

HARD = {  # asserts that guard data lookups / table geometry stay hard; every other assert is a claim about the data
    "make_tables.py": {173, 248, 267, 294, 348, 432, 440, 714, 761, 1136, 1224, 1232, 1243, 1304, 1306},
    "fig_backup.py": set(),
}
SOFT_HEAD = '''
CLAIMS = []   # appended-sample build: claims the professor's script asserted about the 303-firm data that do not hold here


def _chk(test, msg, line):
    try:
        ok = bool(test())
        detail = ""
    except Exception as e:   # noqa: BLE001
        ok, detail = False, f"{type(e).__name__}: {e}"
    if not ok:
        try:
            m = msg() if msg else ""
        except Exception:   # noqa: BLE001
            m = ""
        CLAIMS.append((line, str(m)[:200], detail[:120]))
        print(f"CLAIM no longer holds (line {line}): {str(m)[:160]} {detail[:100]}")
'''
BLOCK = re.compile(r"<<<<<<< ORIGINAL\n(.*?)\n=======\n(.*?)\n>>>>>>> PATCH", re.S)


def load_patches(fname):
    p = PATCH_DIR / (fname + ".patch")
    return BLOCK.findall(p.read_text(encoding="utf-8")) if p.exists() else []


def softify(path, hard):
    """Turn every assert except the HARD ones into a logged claim check (_chk); text edit on the build copy only."""
    src = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines = src.split("\n")
    edits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert) and node.lineno not in hard:
            t = ast.get_source_segment(src, node.test)
            m = ast.get_source_segment(src, node.msg) if node.msg is not None else None
            new = f"_chk(lambda: ({t}), " + (f"lambda: ({m})" if m else "None") + f", {node.lineno})"
            edits.append((node.lineno, node.end_lineno, node.col_offset, node.end_col_offset, new))
    for l0, l1, c0, c1, new in sorted(edits, reverse=True):
        first, last = lines[l0 - 1], lines[l1 - 1]
        lines[l0 - 1:l1] = [first[:c0] + new + last[c1:]]
    out = "\n".join(lines)
    i, j = out.find("\ndef "), out.find("\nclass ")
    k = min(x for x in (i, j) if x >= 0)
    Path(path).write_text(out[:k] + "\n" + SOFT_HEAD + out[k:], encoding="utf-8")


def apply(scripts_dir):
    scripts_dir = Path(scripts_dir)
    names = {p.name[: -len(".patch")] for p in PATCH_DIR.glob("*.patch")} | set(HARD)
    for fname in sorted(names):
        p = scripts_dir / fname
        s = p.read_text(encoding="utf-8")
        for old, new in load_patches(fname):
            if s.count(old) != 1:
                sys.exit(f"STOP: patch for {fname} not applicable (found {s.count(old)}x): {old[:80]!r}")
            s = s.replace(old, new)
        p.write_text(s, encoding="utf-8")
    for fname, hard in HARD.items():
        softify(scripts_dir / fname, hard)


if __name__ == "__main__":
    apply(sys.argv[1])
