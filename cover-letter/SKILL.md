---
name: cover-letter
description: Write a one-page, job-specific cover letter (PDF) and draft answers to open-ended application questions ("Why this company?", "Why this role?", "Describe a project...") grounded in the job description and the tailored resume.
---

# Cover letter + open-ended answers

Inputs: the job description (`applications/<job>/job_description.txt` or the posting) and the tailored
resume (`applications/<job>/Pruthu_Raut_Resume.tex`). Research the company briefly (official site,
product/security blog, recent news) only for facts you can cite; never invent them.

## Cover letter
Write `applications/<job>/cover_letter.json`:
```json
{"company": "...", "company_address": ["Company", "City, ST"], "greeting": "Hiring Manager", "paragraphs": ["..."]}
```
- 3-4 paragraphs, 250-380 words total. Plain text (no LaTeX); the build script escapes it.
- P1: the exact role title, and a hook connecting your strongest relevant achievement to the team's mission.
- P2-P3: 2-3 concrete, quantified accomplishments from the resume mapped to the JD's top requirements
  (use the JD's own keywords). Show, don't list.
- Last: why this company specifically (one real, specific detail about its product, team or security work),
  availability (start June 2027), and a confident close.
- Greeting: a hiring manager's name only if verified (e.g. from the contact-finder brief); otherwise "Hiring Manager".
- Every claim must be supported by the resume or profile. No clichés ("I am writing to express my interest...",
  "team player", "passionate"), no repeating the resume line by line.

Build (must be ONE page; if it fails, shorten the text - never change fonts or margins):
`python cover-letter/build_cover_letter.py applications/<job>/cover_letter.json`

## Open-ended application questions
For questions such as "Why do you want to work here?", "Why this role?", "Tell us about a challenging
project", "What interests you about our mission?":
- First `python profile/answers.py lookup "<question>" --company "<Company>"`. Reuse a generic saved answer
  (e.g. a project story) only after re-tailoring it to this JD.
- Otherwise draft one from the JD + resume: specific to the company and role, first person, 80-150 words
  (or within the form's character limit), one concrete example with a number, no clichés.
- Save to `applications/<job>/answers.md` (question -> answer) and show them to the user with the filled form.
- After the user approves (or edits) them, store each with `answers.py add ... --company "<Company>"` for
  company-specific questions, or without `--company` for reusable generic ones (e.g. "Describe a project you're proud of").
