# aplify

An agent-driven job application workflow for [Claude Code](https://claude.com/claude-code), [Codex CLI](https://github.com/openai/codex) and [Gemini CLI](https://github.com/google-gemini/gemini-cli). All three follow the same instructions in `AGENTS.md`.

Give it a job posting and it will:

1. **Tailor your LaTeX resume** to the job description (ATS keywords, JD-driven ordering of experience and projects).
2. **Build a single-page PDF whose height fits the content exactly**: same fonts, sizes, margins and width as your base resume; the page grows if content overflows and shrinks so there is no blank space under the last line.
3. **Write a one-page cover letter** tailored to the job (same font as the resume; the build fails rather than spill onto page 2) and draft answers to open-ended questions like "Why this company?" from the job description.
4. **Find hiring contacts** (recruiters, team members) with evidence and profile links.
5. **Fill application forms**: Simplify Copilot autofills first, the tailored resume and cover letter replace whatever Simplify attached, the agent fills the rest from your profile and a learned-answers memory, and asks you only for questions it has never seen. Your answers are saved (`profile/answers.py`) so they're autofilled next time. It stops for your approval before anything is submitted or sent.
6. **Track every application** in a CSV to avoid duplicates (with importers for Simplify, LinkedIn and Jobright history).

## Layout

| Path | What it is |
|---|---|
| `AGENTS.md` | The workflow and approval rules every agent follows |
| `CLAUDE.md`, `GEMINI.md` | Thin pointers that import `AGENTS.md` for Claude Code / Gemini CLI |
| `.gemini/settings.json` | Gemini CLI: Playwright MCP browser server for this project |
| `setup/agent_setup.py` | Registers Playwright MCP with Codex and checks prerequisites |
| `resume-builder/SKILL.md` | Resume-tailoring skill (prompt + build step) |
| `resume-builder/build_resume.py` | Fit-to-content LaTeX build script |
| `cover-letter/` | Cover-letter skill, LaTeX template and one-page build script |
| `Hiring Contact Finder/` | Plugin/skill for finding evidence-backed hiring contacts |
| `profile/applicant_profile.example.json` | Template for your application-form answers |
| `profile/answers.py` | Learned-answers memory: fuzzy lookup / add / list / forget for form questions |

Personal files are git-ignored: `profile/applicant_profile.json`, `profile/learned_answers.json`, `resume-builder/base_resume.tex`, `applications/` and all PDFs.

## Setup

1. Install a LaTeX distribution with `pdflatex` ([MiKTeX](https://miktex.org/) on Windows, TeX Live on macOS/Linux) and Python 3.
2. Put your resume at `resume-builder/base_resume.tex`. Its `\usepackage[...]{geometry}` line must include a `paperheight=`.
3. Copy `profile/applicant_profile.example.json` to `profile/applicant_profile.json` and fill it in.
4. Open the folder in Claude Code and paste a job posting or URL.

## Using Codex CLI or Gemini CLI

Claude Code drives the browser with Claude in Chrome. Codex and Gemini use
[Playwright MCP](https://github.com/microsoft/playwright-mcp) (free, open source) in **extension mode**, so they
control your everyday Chrome where you're signed in and Simplify is installed.

1. Install Node.js, plus `codex` (`npm i -g @openai/codex`) and/or `gemini` (`npm i -g @google/gemini-cli`).
2. Run `python setup/agent_setup.py`. It adds the `playwright` MCP server to Codex; Gemini picks it up from
   `.gemini/settings.json` automatically.
3. In Chrome, install the **Playwright MCP Bridge** extension (Chrome Web Store, by Microsoft). When the agent first
   opens the browser, the extension asks which tab to share.
4. Run `codex` or `gemini` from this folder and paste a job posting.

### Antigravity CLI (agy): use `/browser` (faster)

agy has a built-in browser subagent that drives your own running Chrome through Chrome DevTools MCP, which is
quicker than Playwright on long forms like Workday. One-time setup:

1. Use Chrome 144 or newer and install Node.js (`npx` launches the DevTools MCP server).
2. Open `chrome://inspect/#remote-debugging` and turn on **Allow remote debugging for this browser instance**.
3. Run `agy` from this folder and paste a job posting. When Chrome asks to allow remote debugging, click **Allow**.

While remote debugging is on, any program on your computer can control that Chrome, so turn it off when you're
done. The Playwright MCP server stays configured as a fallback.

If the agent can't click the Simplify panel (it belongs to another extension), it asks you to click
**Autofill**, then continues filling the rest of the form.

## Building a resume manually

```bash
python resume-builder/build_resume.py path/to/resume.tex [--out DIR]
```

How it works: pass 1 compiles on a 200in-tall page and records the vertical position of the last line using `\pdfsavepos`. Pass 2 recompiles with `paperheight` set to that height plus the bottom margin, then confirms the result is exactly one page. Nothing else in the `.tex` is changed, and the fitted `.tex` is saved next to the PDF so it reproduces identically (e.g. on Overleaf).

## Safety

The agent never submits an application, sends a message or connection request, or emails anyone without explicit approval of the exact content. Avoid automating LinkedIn actions, which LinkedIn's terms prohibit.
