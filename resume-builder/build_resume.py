"""Compile a resume .tex into a single-page PDF whose height fits the content exactly.

Usage:  python build_resume.py <resume.tex> [--out DIR]

Everything in the .tex (class, packages, fonts, sizes, margins, width) is kept as-is.
Only `paperheight` in the geometry line is changed:
  pass 1 - compile on a very tall page and record where the last line ends
  pass 2 - recompile with paperheight = content height + bottom margin
So a long resume grows the page instead of spilling to page 2, and a short one
gets trimmed so there is no empty space under the last line.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TALL = "200in"            # pass-1 page height (TeX max is ~226in)
SAFETY_PT = 1.0           # tiny cushion so descenders never touch the edge
SP_PER_PT = 65536
PT_PER_IN = 72.27

GEOMETRY_RE = re.compile(r"(\\usepackage\[[^\]]*?paperheight=)([\d.]+\s*(?:in|cm|mm|pt))")
MARGIN_RE = re.compile(r"\\usepackage\[[^\]]*?(?:bottom|margin)=([\d.]+)\s*(in|cm|mm|pt)")

MARKER = r"""
\par
\newwrite\fitout\immediate\openout\fitout=\jobname.fit
\pdfsavepos\write\fitout{\the\pdflastypos}
"""
UNIT_TO_PT = {"in": PT_PER_IN, "pt": 1.0, "cm": PT_PER_IN / 2.54, "mm": PT_PER_IN / 25.4}


def find_pdflatex() -> str:
    exe = shutil.which("pdflatex")
    if exe:
        return exe
    for base in (Path.home() / "AppData/Local/Programs/MiKTeX", Path("C:/Program Files/MiKTeX")):
        cand = base / "miktex/bin/x64/pdflatex.exe"
        if cand.exists():
            return str(cand)
    sys.exit("pdflatex not found - install MiKTeX or TeX Live.")


def compile_tex(pdflatex: str, tex: str, workdir: Path, name: str) -> Path:
    src = workdir / f"{name}.tex"
    src.write_text(tex, encoding="utf-8")
    cmd = [pdflatex, "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"]
    r = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, errors="replace")
    pdf = workdir / f"{name}.pdf"
    if r.returncode != 0 or not pdf.exists():
        log = (workdir / f"{name}.log")
        tail = log.read_text(errors="replace")[-3000:] if log.exists() else r.stdout[-3000:]
        sys.exit(f"LaTeX failed:\n{tail}")
    return pdf


def page_count(log: Path) -> int:
    m = re.search(r"Output written on .*?\((\d+) pages?", log.read_text(errors="replace"), re.S)
    return int(m.group(1)) if m else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex")
    ap.add_argument("--out", help="output directory (default: next to the .tex)")
    args = ap.parse_args()

    src = Path(args.tex).resolve()
    out_dir = Path(args.out).resolve() if args.out else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    tex = src.read_text(encoding="utf-8")

    if not GEOMETRY_RE.search(tex):
        sys.exit("No paperheight= found in the geometry \\usepackage line.")
    m = MARGIN_RE.search(tex)
    bottom_pt = float(m.group(1)) * UNIT_TO_PT[m.group(2)] if m else 0.2 * PT_PER_IN

    pdflatex = find_pdflatex()
    name = src.stem
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)

        # Pass 1: tall page + position marker after the last line.
        probe = GEOMETRY_RE.sub(lambda g: g.group(1) + TALL, tex, count=1)
        probe = probe.replace(r"\end{document}", MARKER + r"\end{document}")
        compile_tex(pdflatex, probe, work, name)
        y_sp = int((work / f"{name}.fit").read_text().strip())
        tall_pt = float(TALL[:-2]) * PT_PER_IN
        content_bottom_pt = tall_pt - y_sp / SP_PER_PT     # distance from page top
        height_in = (content_bottom_pt + bottom_pt + SAFETY_PT) / PT_PER_IN

        # Pass 2: exact height; grow slightly if anything still spills to page 2.
        for _ in range(10):
            final = GEOMETRY_RE.sub(lambda g: g.group(1) + f"{height_in:.3f}in", tex, count=1)
            pdf = compile_tex(pdflatex, final, work, name)
            if page_count(work / f"{name}.log") == 1:
                break
            height_in += 0.05
        else:
            sys.exit("Could not fit on one page.")

        shutil.copy(pdf, out_dir / f"{name}.pdf")
        # Save the .tex with the fitted height so it reproduces the same PDF (e.g. on Overleaf).
        (out_dir / f"{name}.tex").write_text(final, encoding="utf-8")

    print(f"OK  {out_dir / (name + '.pdf')}  (1 page, height {height_in:.3f}in)")


if __name__ == "__main__":
    main()
