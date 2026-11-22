# aplify

Paste a job link into your AI coding agent and aplify does the busywork of applying:

1. **Checks** the job against your tracker (no duplicates) and skips roles you're not eligible for (citizenship, clearance).
2. **Tailors your LaTeX resume** to the job description and builds a one-page PDF whose height fits the content exactly.
3. **Writes a one-page cover letter** and drafts answers to open-ended questions ("Why this company?").
4. **Fills the application form** in your own Chrome: Simplify autofills first, then the agent fills the gaps from your
   profile and a learned-answers memory, and asks you only for questions it has never seen (and remembers your answers).
5. **Finds hiring contacts** and drafts short LinkedIn connection notes.
6. **Logs everything** in `applications/tracker.csv`.

It always stops for your approval before submitting an application or sending any message.

Works with **Claude Code**, **Codex CLI**, **Antigravity CLI (`agy`)** and **Gemini CLI**. Every agent follows the same
instructions in [`AGENTS.md`](AGENTS.md).

---

## Contents

- [Requirements](#requirements)
- [Setup (about 15 minutes)](#setup-about-15-minutes)
  - [1. Get the code](#1-get-the-code)
  - [2. Install Python and LaTeX](#2-install-python-and-latex)
  - [3. Add your profile](#3-add-your-profile)
  - [4. Add your base resume](#4-add-your-base-resume)
  - [5. Describe your background to the resume skill](#5-describe-your-background-to-the-resume-skill)
  - [6. Set up your agent and browser](#6-set-up-your-agent-and-browser)
  - [7. Check that everything works](#7-check-that-everything-works)
- [Using it](#using-it)
- [Learned answers](#learned-answers)
- [What's in the repo](#whats-in-the-repo)
- [Privacy](#privacy)
- [Troubleshooting](#troubleshooting)
- [Safety rules](#safety-rules)

---

## Requirements

| What | Why | Get it |
|---|---|---|
| Python 3.10+ | build scripts, answer memory | [python.org](https://www.python.org/downloads/) (Windows: tick "Add to PATH") |
| A LaTeX distribution with `pdflatex` | builds the resume and cover-letter PDFs | Windows: [MiKTeX](https://miktex.org/download) · macOS: [MacTeX](https://www.tug.org/mactex/) · Linux: `sudo apt install texlive-latex-extra` |
| Google Chrome | the agent fills forms in your own browser, where you're signed in | [google.com/chrome](https://www.google.com/chrome/) |
| [Simplify Copilot](https://simplify.jobs/copilot) extension (recommended) | autofills most fields in seconds | Chrome Web Store |
| One AI agent | runs the workflow | Claude Code, Codex CLI, Antigravity CLI or Gemini CLI |
| Node.js 20+ (Codex, agy, Gemini only) | runs the browser MCP servers | [nodejs.org](https://nodejs.org/) |

## Setup (about 15 minutes)

### 1. Get the code

```bash
git clone https://github.com/pruthuraut/aplify.git
cd aplify
```

### 2. Install Python and LaTeX

Install both from the table above. Then check:

```bash
python --version          # 3.10 or newer
pdflatex --version        # any recent version
```

On Windows, MiKTeX installed "for me only" is often not on PATH. That's fine: the build scripts look in the usual
MiKTeX folders automatically. The first build may pop up MiKTeX asking to install missing packages; allow it (or set
MiKTeX Console → Settings → "Always install missing packages").

### 3. Add your profile

The profile holds the answers to standard form questions (contact details, links, work authorization, EEO answers).

```bash
cp profile/applicant_profile.example.json profile/applicant_profile.json
cp profile/learned_answers.example.json   profile/learned_answers.json
```

Open `profile/applicant_profile.json` and replace every `TODO`. Notes:

- `first_name` / `last_name` also name your output files (`First_Last_Resume.pdf`, `First_Last_Cover_Letter.pdf`)
  and the cover-letter header.
- Leave a field as `TODO` if you don't want it filled automatically; the agent will ask you instead of guessing.
- Be precise in `work_authorization`. It decides which jobs are skipped and how sponsorship questions are answered.
- Never put passwords, SSNs, ID numbers or bank details here. The answer memory refuses to store them too.

### 4. Add your base resume

Save your resume as LaTeX at `resume-builder/base_resume.tex`. Every tailored resume starts from it, and the build keeps
your fonts, sizes, margins and layout exactly.

One requirement: the `\usepackage[...]{geometry}` line must include a `paperheight=` value, for example:

```latex
\usepackage[paperwidth=8.5in, paperheight=11in, margin=0.2in]{geometry}
```

The build script replaces that height so the single page ends right after your last line.

Test it:

```bash
python resume-builder/build_resume.py resume-builder/base_resume.tex --out /tmp/aplify-test
```

You should see `OK ... (1 page, height ...in)`.

### 5. Describe your background to the resume skill

`resume-builder/SKILL.md` is the prompt the agent uses to tailor your resume. Its **Context** section currently
describes the author's own jobs and projects. Rewrite that paragraph (and the "classify the JD" hints under
**Experience & Project Selection**) to describe **your** experience and which projects to lead with for which kinds of
roles. Keep the rules about not changing LaTeX formatting.

Optionally skim `cover-letter/SKILL.md` and `outreach/SKILL.md` and adjust the tone to taste.

### 6. Set up your agent and browser

Every agent drives **your everyday Chrome**, where you're signed in to job sites and Simplify is installed, never a
blank browser profile.

| Agent | Browser connection | Fallbacks |
|---|---|---|
| Claude Code | [Claude in Chrome](https://claude.com/chrome) extension | - |
| Antigravity CLI (`agy`) | [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp), attached to your running Chrome | Browser MCP, Playwright MCP |
| Codex CLI, Gemini CLI | [Browser MCP](https://browsermcp.io/) extension | Playwright MCP |

<details open>
<summary><b>Claude Code</b></summary>

1. Install [Claude Code](https://claude.com/claude-code) and the **Claude in Chrome** extension, then sign in.
2. Run `claude` in the `aplify` folder. `CLAUDE.md` loads the workflow automatically.
3. When the agent first opens a job site, allow it in the extension prompt.

</details>

<details>
<summary><b>Antigravity CLI (agy)</b></summary>

1. Install Antigravity CLI and Node.js 20+.
2. Register the browser servers:
   ```bash
   python setup/agent_setup.py --agy
   ```
   This adds `chrome-devtools` (in attach mode), plus `browsermcp` and `playwright` as fallbacks. If you already had a
   `chrome-devtools` entry that launches its own browser, it is switched to attach mode.
3. In Chrome (version 144+), open `chrome://inspect/#remote-debugging` and turn on remote debugging. You do this once.
4. Run `agy` in the `aplify` folder. The first time it connects, Chrome asks for permission: click **Allow**.
5. Optional, fewer prompts: agy asks before every new tool and every new website. Choose "always allow" for the
   browser tools and job sites as they come up, or add them to `permissions.allow` in
   `~/.gemini/antigravity-cli/settings.json`. Consider keeping `handle_dialog` (confirm/submit pop-ups) on "ask".

</details>

<details>
<summary><b>Codex CLI</b></summary>

1. Install Codex CLI and Node.js 20+.
2. Install the **Browser MCP** extension from [browsermcp.io](https://browsermcp.io/) and pin it.
3. Register the servers:
   ```bash
   python setup/agent_setup.py --codex
   ```
4. Run `codex` in the `aplify` folder. The first time, a six-digit code appears: check that the extension popup shows
   the same code and click **Allow**. **Stop** in the popup pauses the agent at any time.
5. **Windows:** if Codex says `python` or `pdflatex` isn't installed when they are, set
   `[windows] sandbox = "unelevated"` in `~/.codex/config.toml` and restart Codex. The default "elevated" sandbox runs
   commands as a separate account that can't see per-user installs.

</details>

<details>
<summary><b>Gemini CLI</b></summary>

1. Install Gemini CLI and Node.js 20+.
2. Install the **Browser MCP** extension from [browsermcp.io](https://browsermcp.io/) and pin it.
3. Run `gemini` in the `aplify` folder. `.gemini/settings.json` already adds the browser servers and `GEMINI.md` loads
   the workflow.

</details>

### 7. Check that everything works

```bash
python setup/agent_setup.py                     # prerequisites + MCP registration report
python profile/answers.py list                  # should print your saved answers (or nothing yet)
python profile/answers.py lookup "Are you authorized to work in the US?"
```

Then start your agent and try: `Apply to <job URL>`. It should check the tracker, build a resume and cover letter,
open the form, run Simplify, and stop to show you everything before submitting.

## Using it

Run your agent from the `aplify` folder and talk to it normally. Examples:

| You say | What happens |
|---|---|
| `Apply to https://jobs.lever.co/...` | eligibility check → tailored resume + cover letter → form filled → summary for your approval |
| `Find contacts and reach out` | ranked hiring contacts in `contacts.md`, draft notes in `outreach.md`; nothing is sent until you approve the exact notes |
| `Approved` | sends exactly the approved invites, spaced out, within daily/weekly limits |
| `Open https://jobright.ai/jobs/recommend and apply one by one` | works through your recommendations, skips anything it's unsure about, and lists what needs you |
| `Submit` | submits the form it just showed you |

Each job gets a folder `applications/<company>-<role>/` with the job description, tailored `.tex`/`.pdf` resume,
cover letter, contacts and outreach drafts. `applications/tracker.csv` lists every application and its status.

**Login queue:** portals that need a sign-in, account or email code (Workday, Oracle, Taleo, iCIMS, amazon.jobs)
never block a run. The agent prepares the resume and cover letter, adds the job to `applications/login_queue.md`, and
moves on. At the end you sign in once per portal (tick "Keep me signed in"), say `done`, and it fills those forms.

**When the agent needs you:**
- signing in or creating accounts on job portals (Workday, iCIMS, Taleo, Oracle, amazon.jobs) and one-time codes;
- CAPTCHAs;
- questions it has never seen (asked all at once, then remembered);
- final approval before anything is submitted or sent.

## Learned answers

Every new answer you give is saved to `profile/learned_answers.json` and reused on later forms through fuzzy matching
of the question text.

```bash
python profile/answers.py add "Are you open to relocation?" "Yes" --type yes_no
python profile/answers.py add "Why do you want to work at Acme?" "..." --company Acme
python profile/answers.py lookup "Willing to relocate?"
python profile/answers.py list
python profile/answers.py forget "Are you open to relocation?"
```

Standing rules that apply to every company (for example "always answer the in-office question Yes" or "use the top of
the posted salary range") live in `AGENTS.md` step 3c2. Edit them to match your own preferences.

## What's in the repo

| Path | What it is |
|---|---|
| `AGENTS.md` | The workflow and approval rules every agent follows |
| `CLAUDE.md`, `GEMINI.md` | Short files that load `AGENTS.md` for Claude Code / Gemini CLI / agy |
| `resume-builder/` | Resume-tailoring prompt (`SKILL.md`) and the fit-to-one-page build script |
| `cover-letter/` | Cover-letter prompt, LaTeX template and one-page build script |
| `Hiring Contact Finder/` | Skill for finding evidence-backed recruiters and team members |
| `outreach/SKILL.md` | LinkedIn connection-note rules (≤300 chars, approval, rate limits) |
| `profile/` | Profile template and the learned-answers tool (`answers.py`) |
| `setup/agent_setup.py` | Registers browser MCP servers for Codex / agy and checks prerequisites |
| `.gemini/settings.json` | Browser MCP servers for Gemini CLI |

## Privacy

Your personal data never leaves your machine through git. These are git-ignored:

- `profile/applicant_profile.json` and `profile/learned_answers.json`
- `resume-builder/base_resume.tex` and all PDFs
- `applications/` (tracker, tailored resumes, cover letters, contacts, outreach)
- `scratch/` and browser-tool output

Before you push changes to a fork, run `git status` and make sure none of these appear.

## Troubleshooting

| Problem | Fix |
|---|---|
| `pdflatex not found` | Install MiKTeX/TeX Live. On Windows the scripts also search `%LOCALAPPDATA%\Programs\MiKTeX`. In Codex, see the sandbox note above. |
| `paperheight` error from `build_resume.py` | Add `paperheight=` to the `geometry` line in `base_resume.tex`. |
| Cover letter build fails "more than 1 page" | Intended: shorten `cover_letter.json`. Fonts are never shrunk. |
| Agent can't click Simplify's **Autofill This Page** | Simplify's panel is inside a shadow root. `AGENTS.md` step 3a clicks it with JavaScript; if that fails, the agent asks you to click it once. |
| Uploading a resume overwrote fields (Lever, Workday) | Some forms re-parse the resume after upload. The agent re-checks the form after every upload, and you should still glance at name, phone and education. |
| agy: "Could not connect to Chrome" | Turn on `chrome://inspect/#remote-debugging` in Chrome 144+, keep Chrome open, click **Allow**. |
| agy asks for permission constantly | See Antigravity step 5 above. |
| Browser MCP not connecting | Open the extension popup, click **Connect**, and approve the six-digit code. |
| LinkedIn shows a limit or verification warning | The agent stops by itself. Wait a day; limits are ≤15 invites/day, ≤80/week. |

## Safety rules

Built into `AGENTS.md` and enforced by every agent:

- Never submits an application, or sends a connection request, message or email, without your explicit approval of
  the exact content.
- Never types passwords, creates accounts, or solves CAPTCHAs; you sign in yourself.
- Never guesses unknown answers or stores sensitive data (SSN, IDs, financial details).
- On LinkedIn it only reads profiles and jobs and sends invites you approved, with pacing and limits. It never uses
  Easy Apply, messages, follows or endorses. Automating LinkedIn can conflict with its terms; use it at your own risk.

---

Questions or ideas? Open an issue on [GitHub](https://github.com/pruthuraut/aplify/issues).
