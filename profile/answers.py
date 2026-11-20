"""Learned application answers - a memory of form questions and how the user answered them.

Simplify autofills what it knows; the agent fills the rest from applicant_profile.json and this
store. Any question neither covers gets asked once, and the user's answer is saved here so it is
autofilled next time.

Usage:
  python profile/answers.py lookup "Question text as shown on the form" [--company X]
  python profile/answers.py add "Question text" "Answer" [--company X] [--type text|select|yes_no]
  python profile/answers.py list
  python profile/answers.py forget "Question text"

Matching is fuzzy: wording/punctuation/case differences ("Are you legally authorized to work in
the US?" vs "Authorized to work in the United States?") still match. Company-specific answers
(e.g. "Why do you want to work at X?") are stored with --company and only match that company.
"""
import argparse
import difflib
import json
import re
import sys
from datetime import date
from pathlib import Path

STORE = Path(__file__).with_name("learned_answers.json")
THRESHOLD = 0.75

# Never store these - they must come from the user or a password manager every time.
SENSITIVE = re.compile(
    r"password|passcode|\bpin\b|social security|\bssn\b|passport|driver'?s licen[cs]e|"
    r"bank|routing|account number|credit card|card number|cvv|tax id|\bitin\b|\bein\b",
    re.I,
)

SYNONYMS = [
    (r"\bunited states( of america)?\b|\bu\.?s\.?a?\b", " us "),
    (r"\blegally\b|\bcurrently\b|\bplease\b|\bkindly\b", " "),
    (r"\bauthori[sz]ed\b|\bauthori[sz]ation\b|\beligible\b|\beligibility\b", " authorized "),
    (r"\bsponsorship\b|\bsponsor\b|\bvisa support\b", " sponsor "),
    (r"\bdo you\b|\bare you\b|\bwill you\b|\bhave you\b|\bcan you\b", " "),
    (r"\bdesired\b|\bexpected\b|\bexpectations?\b|\bcompensation\b|\bpay\b|\bwages?\b", " salary "),
    (r"\bavailab\w*\b|\bearliest\b|\bwhen can\b", " start "),
    (r"\breferred\b|\bsource\b|\bfind out\b|\blearn about\b|\bhear about\b", " hear "),
    (r"\bimmigration\b|\bwork permit\b", " visa "),
    (r"\b(at least |over |older than )?18( years)?( of age| old)?( or older)?\b", " adult18 "),
    (r"\btop secret\b|\bts sci\b|\bts\b|\bsecret\b|\bsecurity clearance\b", " clearance "),
]
STOP = set("a an the to for of in at on by this that with your you what which is be or and are am "
           "do does did have has will would can could how i my we our please position role job "
           "company opportunity status employment if any when date current currently active about".split())


def tokens(q: str) -> set:
    return {t for t in norm(q).split() if t not in STOP}


def similarity(a: str, b: str) -> float:
    seq = difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return seq
    inter = len(ta & tb)
    jacc = inter / len(ta | tb)
    # containment only counts when the shorter question has 2+ meaningful words
    cont = inter / min(len(ta), len(tb)) if min(len(ta), len(tb)) >= 2 else jacc
    tok = 0.5 * jacc + 0.5 * cont
    # character similarity alone is misleading ("travel" vs "relocate"), so only trust it when near-identical
    return max(seq, tok) if seq >= 0.9 else tok


def norm(q: str) -> str:
    q = q.lower()
    q = re.sub(r"\*|\(required\)|\(optional\)", " ", q)
    for pat, rep in SYNONYMS:
        q = re.sub(pat, rep, q)
    q = re.sub(r"[^a-z0-9 ]", " ", q)
    return " ".join(q.split())


def load() -> list:
    if not STORE.exists():
        return []
    return json.loads(STORE.read_text(encoding="utf-8"))


def save(items: list) -> None:
    STORE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def best_match(items, question, company=None):
    best, score = None, 0.0
    for it in items:
        if it.get("company") and (not company or it["company"].lower() != company.lower()):
            continue
        for variant in [it["question"], *it.get("aliases", [])]:
            s = similarity(question, variant)
            # company-specific answers win ties over general ones
            s += 0.01 if it.get("company") else 0
            if s > score:
                best, score = it, s
    return (best, score) if score >= THRESHOLD else (None, score)


def cmd_lookup(a):
    item, score = best_match(load(), a.question, a.company)
    if item:
        print(json.dumps({"answer": item["answer"], "matched": item["question"],
                          "score": round(score, 2), "type": item.get("type", "text")}))
    else:
        print(json.dumps({"answer": None, "best_score": round(score, 2)}))
        sys.exit(1)


def cmd_add(a):
    if SENSITIVE.search(a.question):
        sys.exit("Refusing to store an answer to a sensitive question (credentials/financial/ID).")
    items = load()
    item, _ = best_match(items, a.question, a.company)
    if item and (item.get("company") or None) == (a.company or None):
        if norm(a.question) != norm(item["question"]) and a.question not in item.setdefault("aliases", []):
            item["aliases"].append(a.question)
        item.update(answer=a.answer, type=a.type, updated=date.today().isoformat())
        msg = "updated"
    else:
        items.append({"question": a.question, "answer": a.answer, "type": a.type,
                      "company": a.company, "aliases": [], "added": date.today().isoformat()})
        msg = "added"
    save(items)
    print(f"{msg}: {a.question!r} -> {a.answer!r}" + (f" [{a.company}]" if a.company else ""))


def cmd_list(_):
    for it in load():
        scope = f" [{it['company']}]" if it.get("company") else ""
        print(f"- {it['question']}{scope}: {it['answer']}")


def cmd_forget(a):
    items = load()
    item, _ = best_match(items, a.question)
    if not item:
        sys.exit("No matching answer.")
    items.remove(item)
    save(items)
    print(f"forgot: {item['question']!r}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lookup"); p.add_argument("question"); p.add_argument("--company")
    p = sub.add_parser("add"); p.add_argument("question"); p.add_argument("answer")
    p.add_argument("--company"); p.add_argument("--type", default="text", choices=["text", "select", "yes_no"])
    sub.add_parser("list")
    p = sub.add_parser("forget"); p.add_argument("question")
    a = ap.parse_args()
    {"lookup": cmd_lookup, "add": cmd_add, "list": cmd_list, "forget": cmd_forget}[a.cmd](a)


if __name__ == "__main__":
    main()
