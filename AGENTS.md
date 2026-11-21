# aplify - job application workflow

Shared instructions for every coding agent (Claude Code reads them via `CLAUDE.md`, Codex reads
`AGENTS.md` directly, Gemini CLI via `.gemini/settings.json` -> `contextFileName`).

Given a job posting (text or URL):
0. **Eligibility + duplicates first** - check `applications/tracker.csv` for the company/role. Read the JD and
   skip (log as `skipped_ineligible`) roles that require US citizenship, a security clearance, or that the
   profile otherwise rules out. Tell the user why.
1. **Resume** - follow `resume-builder/SKILL.md`. Start from `resume-builder/base_resume.tex`, tailor content only,
   save to `applications/<company>-<role>/Pruthu_Raut_Resume.tex`, then ALWAYS build with
   `python resume-builder/build_resume.py <that .tex>` (single page, height fitted to content, same fonts/sizes).
1b. **Cover letter** - follow `cover-letter/SKILL.md`: write `applications/<company>-<role>/cover_letter.json`
   from the JD + tailored resume, then `python cover-letter/build_cover_letter.py <that .json>` (must be 1 page).
2. **Contacts** - follow `Hiring Contact Finder/skills/find-hiring-contacts/SKILL.md`. Save the brief to
   `applications/<company>-<role>/contacts.md`.
2b. **Outreach** - follow `outreach/SKILL.md`: draft <=300-char LinkedIn connection notes for 5-6 contacts,
   get the user's approval of the exact notes, then send them (paced, <=15/day, <=80/week); log in `applications/outreach.csv`.
3. **Application forms** - Simplify first, then memory, then ask (browser: see "Browser tools" below):
   a. Open the application page. Use the Simplify Copilot extension panel to autofill
      (click "Autofill" / "Autofill This Page" in the Simplify sidebar) and wait for it to finish.
      Then REPLACE whatever resume/cover letter Simplify attached with this job's tailored files
      (`Pruthu_Raut_Resume.pdf`, `Pruthu_Raut_Cover_Letter.pdf`) using the browser's file-upload tool, and confirm
      the form shows the new filenames. If the form has a cover-letter text box instead of an upload, paste the letter text.
   b2. Open-ended questions ("Why this company/role?", "Describe a project...", "Anything else?"):
      draft answers from the JD + resume per `cover-letter/SKILL.md`, save to `applications/<job>/answers.md`.
   b. Read the form and list every field that is still empty or wrong.
   c. For each one, check `profile/applicant_profile.json`, then
      `python profile/answers.py lookup "<exact question text>" --company "<Company>"`.
      Use a lookup result only if its `matched` question truly means the same thing (e.g. "US citizen"
      is NOT the same as "US citizen or permanent resident") - otherwise treat it as unknown.
   d. Ask the user for all remaining unknowns in ONE message. Never guess, and never guess a `TODO` field.
   e. Save every new answer the user gives:
      `python profile/answers.py add "<question>" "<answer>" [--company X if company-specific] [--type yes_no|select|text]`
      (company-specific = mentions the company, e.g. "Why do you want to work at X?").
      Never save passwords, SSNs, IDs, or financial details - the script refuses these.
   f. If the user corrects an autofilled answer, save the correction the same way (it overwrites).
   g. Before submitting, show the user: the filled form summary, the attached file names, and every drafted
      open-ended answer. Submit only after explicit approval; then save approved open-ended answers to memory.
4. **Approval gates** - never submit an application, send a message/connection request, or email anyone
   without explicit approval of the exact content. Show the filled form / draft first. Never type passwords,
   create accounts, or accept terms/consent checkboxes without asking; the user signs in themselves.
5. Log every application in `applications/tracker.csv` (date, company, role, url, status, contacts, notes);
   check it first to avoid duplicates.

## Browser tools
The agent must drive the user's own Chrome (their logins + the Simplify extension live there).
- **Claude Code**: Claude in Chrome (`mcp__claude-in-chrome__*`).
- **Codex CLI / Gemini CLI**: Playwright MCP in extension mode (`@playwright/mcp --extension`), connected to the
  user's Chrome through the "Playwright MCP Bridge" extension (setup: `python setup/agent_setup.py`).
  Useful tools: `browser_navigate`, `browser_snapshot` (read the page + element refs), `browser_click`,
  `browser_type`, `browser_select_option`, `browser_file_upload`, `browser_tabs`, `browser_take_screenshot`.
  - Use `browser_snapshot` to read forms; prefer it over screenshots.
  - The Simplify panel is drawn by another extension and may not be clickable from Playwright. If clicking
    "Autofill" fails, ask the user to click it, wait for them to say it finished, then continue from step 3b.
  - `browser_file_upload` needs absolute paths, e.g. the PDFs in `applications/<job>/`.
- LinkedIn: read profiles/jobs, and send ONLY user-approved connection invites (step 2b, within its limits).
  Never apply, message, follow, endorse or do anything else there.
