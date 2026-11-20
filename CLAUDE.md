# aplify - job application workflow

Given a job posting (text or URL):
1. **Resume** - follow `resume-builder/SKILL.md`. Start from `resume-builder/base_resume.tex`, tailor content only,
   save to `applications/<company>-<role>/Pruthu_Raut_Resume.tex`, then ALWAYS build with
   `python resume-builder/build_resume.py <that .tex>` (single page, height fitted to content, same fonts/sizes).
2. **Contacts** - follow `Hiring Contact Finder/skills/find-hiring-contacts/SKILL.md`. Save the brief to
   `applications/<company>-<role>/contacts.md`.
3. **Application forms** - answer from `profile/applicant_profile.json`. Never guess a `TODO` field; ask.
4. **Approval gates** - never submit an application, send a message/connection request, or email anyone
   without explicit approval of the exact content. Show the filled form / draft first.
5. Log every application in `applications/tracker.csv` (date, company, role, url, status, contacts, notes);
   check it first to avoid duplicates.
