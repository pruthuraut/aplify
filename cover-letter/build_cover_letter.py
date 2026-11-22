"""Build a one-page cover letter PDF from a JSON content file.

Usage:  python cover-letter/build_cover_letter.py <applications/<job>/cover_letter.json>

cover_letter.json:
{
  "company": "Amazon",
  "company_address": ["Amazon.com Services LLC", "Seattle, WA"],   # optional lines
  "greeting": "Hiring Manager",                                     # or a verified name
  "paragraphs": ["...", "...", "..."]                               # plain text, 3-4 paragraphs
}

Header (name, email, phone, links) comes from profile/applicant_profile.json.
Writes <First>_<Last>_Cover_Letter.tex/.pdf next to the JSON. Fonts, size and margins are fixed by
the template and never shrunk: if the letter runs past one page the build fails and the text must
be shortened.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = Path(__file__).with_name("template.tex")
PROFILE = ROOT / "profile" / "applicant_profile.json"

LATEX_SPECIAL = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
                 "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\^{}"}


def esc(s: str) -> str:
    s = "".join(LATEX_SPECIAL.get(c, c) for c in s)
    return s.replace("\u2014", "---").replace("\u2013", "--").replace("\u2019", "'") \
            .replace("\u201c", "``").replace("\u201d", "''")


def find_pdflatex() -> str:
    exe = shutil.which("pdflatex")
    if exe:
        return exe
    for base in (Path.home() / "AppData/Local/Programs/MiKTeX", Path("C:/Program Files/MiKTeX")):
        cand = base / "miktex/bin/x64/pdflatex.exe"
        if cand.exists():
            return str(cand)
    sys.exit("pdflatex not found - install MiKTeX or TeX Live.")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    c = json.loads(src.read_text(encoding="utf-8"))
    p = json.loads(PROFILE.read_text(encoding="utf-8"))
    me, links = p["personal"], p["links"]

    name = f'{me["first_name"]} {me["last_name"]}'
    phone = me["phone"]
    m = re.fullmatch(r"\+?1?(\d{3})(\d{3})(\d{4})", re.sub(r"[^\d+]", "", phone))
    if m:
        phone = f"+1 ({m.group(1)}) {m.group(2)}-{m.group(3)}"
    contact = [rf'\href{{mailto:{me["email"]}}}{{{esc(me["email"])}}}', esc(phone)]
    for label, key in (("LinkedIn", "linkedin"), ("GitHub", "github"), ("Portfolio", "portfolio")):
        if links.get(key):
            contact.append(rf'\href{{{links[key]}}}{{{label}}}')

    company_lines = [esc(c["company"])] if not c.get("company_address") else [esc(x) for x in c["company_address"]]
    body = "\n\n".join(esc(par.strip()) for par in c["paragraphs"])

    tex = TEMPLATE.read_text(encoding="utf-8")
    for key, val in {
        "<<NAME>>": esc(name),
        "<<CONTACT_LINE>>": r" \quad ".join(contact),
        "<<DATE>>": date.today().strftime("%B %-d, %Y") if sys.platform != "win32" else date.today().strftime("%B %#d, %Y"),
        "<<COMPANY_BLOCK>>": r" \\ ".join(company_lines),
        "<<GREETING>>": esc(c.get("greeting", "Hiring Manager")),
        "<<BODY>>": body,
    }.items():
        tex = tex.replace(key, val)

    stem = f'{me["first_name"]}_{me["last_name"]}_Cover_Letter'
    pdflatex = find_pdflatex()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / f"{stem}.tex").write_text(tex, encoding="utf-8")
        r = subprocess.run([pdflatex, "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"],
                           cwd=work, capture_output=True, text=True, errors="replace")
        log = (work / f"{stem}.log").read_text(errors="replace") if (work / f"{stem}.log").exists() else r.stdout
        if r.returncode != 0:
            sys.exit("LaTeX failed:\n" + log[-2500:])
        pages = int(re.search(r"\((\d+) pages?", log).group(1))
        if pages != 1:
            sys.exit(f"Cover letter is {pages} pages - shorten the paragraphs (do not change fonts/margins).")
        shutil.copy(work / f"{stem}.pdf", src.parent / f"{stem}.pdf")
        (src.parent / f"{stem}.tex").write_text(tex, encoding="utf-8")
    print(f"OK  {src.parent / (stem + '.pdf')}  (1 page)")


if __name__ == "__main__":
    main()
