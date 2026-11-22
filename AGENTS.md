# aplify - job application workflow

Shared instructions for every coding agent (Claude Code reads them via `CLAUDE.md`, Codex reads
`AGENTS.md` directly, Gemini CLI via `.gemini/settings.json` -> `contextFileName`).

Given a job posting (text or URL):
0. **Eligibility + duplicates first** - check `applications/tracker.csv` for the company/role. Read the JD and
   skip (log as `skipped_ineligible`) roles that require US citizenship, a security clearance, or that the
   profile otherwise rules out. Tell the user why.
1. **Resume** - follow `resume-builder/SKILL.md`. Start from `resume-builder/base_resume.tex`, tailor content only,
   save to `applications/<company>-<role>/<First>_<Last>_Resume.tex` (name from `profile/applicant_profile.json`), then ALWAYS build with
   `python resume-builder/build_resume.py <that .tex>` (single page, height fitted to content, same fonts/sizes).
1b. **Cover letter** - follow `cover-letter/SKILL.md`: write `applications/<company>-<role>/cover_letter.json`
   from the JD + tailored resume, then `python cover-letter/build_cover_letter.py <that .json>` (must be 1 page).
2. **Contacts** - follow `Hiring Contact Finder/skills/find-hiring-contacts/SKILL.md`. Save the brief to
   `applications/<company>-<role>/contacts.md`.
2b. **Outreach** - follow `outreach/SKILL.md`: draft <=300-char LinkedIn connection notes for 5-6 contacts,
   get the user's approval of the exact notes, then send them (paced, <=15/day, <=80/week); log in `applications/outreach.csv`.
3. **Application forms** - Simplify first, then memory, then ask (browser: see "Browser tools" below):
   a. **Simplify FIRST - mandatory, before typing anything yourself.** Simplify fills most fields in seconds, so
      never fill a field by hand until Simplify has run on that page:
      1. Open the application page and wait for it to load. Do not read the whole form yet.
      2. Click Simplify's **Autofill This Page** button (in the Simplify sidebar on the right; open the sidebar
         via the Simplify icon if it's collapsed). The sidebar lives inside a shadow root, so normal locators,
         `find` and `snapshot` usually can't see it - click it with JavaScript instead (verified working):
         Browser MCP: `eval "() => { const h=[...document.querySelectorAll('*')].find(e=>e.shadowRoot&&/Autofill This Page/.test(e.shadowRoot.textContent)); const b=h&&[...h.shadowRoot.querySelectorAll('button')].find(b=>/Autofill This Page/.test(b.textContent)); if(!b) return 'not found'; b.click(); return 'clicked'; }"`
         (Claude in Chrome: the same code in `javascript_tool`, or click the button by screen coordinates.)
      3. Wait until Simplify says **"Autofill complete!"** (up to ~30 s). It's also in the shadow root, so check with
         `eval "() => [...document.querySelectorAll('*')].some(e=>e.shadowRoot&&/Autofill complete/.test(e.shadowRoot.textContent))"`
         every few seconds until it returns true.
      4. If the button can't be found or clicked after 2 tries, ask the user once: "Please click Autofill This
         Page in Simplify and tell me when it's done", and wait. Don't fill fields manually meanwhile.
      5. Multi-page forms (Workday, iCIMS, etc.): repeat steps 2-3 on EVERY new page/step before filling it.
      Only after that, read the form (step b) and fill just the gaps.
      Then REPLACE whatever resume/cover letter Simplify attached with this job's tailored files
      (`<First>_<Last>_Resume.pdf`, `<First>_<Last>_Cover_Letter.pdf`) using the browser's file-upload tool, and confirm
      the form shows the new filenames. If the form has a cover-letter text box instead of an upload, paste the letter text.
   b2. Open-ended questions ("Why this company/role?", "Describe a project...", "Anything else?"):
      draft answers from the JD + resume per `cover-letter/SKILL.md`, save to `applications/<job>/answers.md`.
   b. Read the form and list every field that is still empty or wrong.
   c. For each one, check `profile/applicant_profile.json`, then
      `python profile/answers.py lookup "<exact question text>" --company "<Company>"`.
      Use a lookup result only if its `matched` question truly means the same thing (e.g. "US citizen"
      is NOT the same as "US citizen or permanent resident") - otherwise treat it as unknown.
   c2. **Standing answers (user-confirmed, apply to every company - don't ask again):**
      - In-office / hybrid / onsite days requirement ("able to work in the office N days a week?"): **Yes**.
      - Salary expectations: if the posting (or form) shows a pay range, enter the **top of the range**;
        only if no range is shown, use the learned-answers value.
      - Outside projects / side engagements / other business activities that would continue if hired: **No**.
      - Application privacy notice / data-processing consent acknowledgments ("I Acknowledge"): **tick/accept**.
        This covers application privacy acknowledgments only - still ask before creating accounts or accepting
        anything else (site terms of service, arbitration agreements, background-check authorizations).
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
   create accounts, or accept terms/consent checkboxes without asking (except the application privacy
   acknowledgments pre-approved in step 3c2); the user signs in themselves.
4b. **Portal sign-in screens** (Oracle "You don't need an account - just use your email", iCIMS, Workday, Taleo, etc.):
   - Email-only entry (no password field): type the `email` from `profile/applicant_profile.json` and continue. Ask
     before ticking any terms box on that screen, as in step 4.
   - A verification / one-time code is sent: stop and ask the user once - "<Company> sent a code to your email; enter
     it in the open tab and tell me when done" - then continue. Never open the user's mailbox to read codes.
   - A password or account creation is required: stop and ask the user to sign in or create the account themselves
     (their password manager can fill it). Never type, store or log passwords.
   - Meanwhile, continue with other work (e.g. build the next job's resume) instead of idling.
4c. **Login queue** - a portal that needs sign-in, account creation or a code never blocks a run:
   1. Do everything that needs no login first: eligibility, tailored resume + cover letter, draft answers for any
      questions visible on the public posting.
   2. Add the job to `applications/login_queue.md` (one row: date, company, role, portal type, apply URL, what the
      user must do, prep status) and set its tracker status to `queued_login`. Then move on to the next job.
   3. At the end of the run (or when asked), show the queue grouped by portal - one login per portal usually covers
      all its jobs - and ask the user to sign in to them in one sitting (tick "Keep me signed in"; a saved password
      makes it one click).
   4. When the user says "done" (or names portals), work through the queued jobs on those portals: Simplify first,
      fill, upload, show the summary for approval (step 3g), then remove the row from the queue and update the tracker.
   Same for portals that are temporarily down (note "retry") and CAPTCHAs that appear mid-form (note "captcha").
5. Log every application in `applications/tracker.csv` (date, company, role, url, status, contacts, notes);
   check it first to avoid duplicates.

## Browser tools
The agent must drive the user's own Chrome (their logins + the Simplify extension live there).
- **Claude Code**: Claude in Chrome (`mcp__claude-in-chrome__*`).
- **Antigravity CLI (agy)**: [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
  (server `chrome-devtools`, `chrome-devtools-mcp --autoConnect`), attached to the user's running Chrome - never a
  browser it launches itself (that profile has no logins and no Simplify). Setup: `python setup/agent_setup.py --agy`;
  the user enables chrome://inspect/#remote-debugging once and clicks Allow when agy connects.
  - Read: `take_snapshot` (a11y tree with uids; much smaller than screenshots - prefer it), `list_pages` / `select_page`.
    Act: `navigate_page`, `new_page`, `click`, `fill`, `fill_form` (many fields in one call), `hover`, `press_key`,
    `upload_file` (uid of the file input + absolute path to the PDF in `applications/<job>/`), `wait_for` (text),
    `handle_dialog` (never accept a submit/confirm dialog without approval).
  - Simplify (step 3a): `evaluate_script` with the same function as the Browser MCP `eval` below, then poll the
    "Autofill complete" check the same way. Elements inside shadow roots or custom dropdowns that `click`/`fill` can't
    reach: use `evaluate_script` to click the option, or `take_snapshot` again and use the new uid.
  - Re-uploading a resume can make some ATS (Lever, Workday) re-parse it and overwrite fields you already set -
    always re-read the form after an upload and fix them.
  - Fallback: Browser MCP (below), then Playwright MCP.
- **Codex CLI / Gemini CLI** (and agy's fallback): [Browser MCP](https://browsermcp.io/) (`@browsermcp/mcp@latest`,
  server name `browsermcp`) with the Browser MCP Chrome extension (setup: `python setup/agent_setup.py`).
  It works in its own tab group in the user's Chrome, signed in where they are.
  - One `browser` tool that takes command lines; put several lines in one call when you can predict the steps
    (e.g. `goto <url>`, then `snapshot -i`, then `fill ... / select ... / check ...`). Each action answers with one line.
  - Read: `snapshot -i` (interactive elements + refs), `find "<text>"`, `get text <target> --max N`.
    Act: `click`, `fill <target> "<text>"`, `select <target> "<value>"`, `check`, `press <key>`,
    `upload <target> <absolute path>` (the PDFs in `applications/<job>/`). Wait: `wait --text "..."`, `wait <target>`.
    Targets: refs from a snapshot (`e34`), Playwright locators (`getByLabel('Email')`) or CSS selectors.
  - First use: the tool returns a six-digit code; ask the user to check it matches the extension popup and click Allow.
  - To work on a page the user already has open (e.g. a form they started), use `tab list` / `tab select <tabId>`,
    or ask them to drag the tab into the agent's tab group.
  - Simplify autofill always runs first on every form page - follow step 3a exactly (find + click
    "Autofill This Page", wait for "Autofill complete!", ask the user to click it if you can't).
  - Never run `dialog accept` on a submit/confirm dialog without the user's approval (step 4).
  - Fallback: Playwright MCP (`playwright` server, `browser_*` tools) if Browser MCP is unavailable or fails twice.
- LinkedIn: read profiles/jobs, and send ONLY user-approved connection invites (step 2b, within its limits).
  Never apply, message, follow, endorse or do anything else there.
