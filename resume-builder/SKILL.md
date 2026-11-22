---
name: resume-builder
description: Tailor the user's LaTeX resume to a job description (ATS-optimized) and build it into a fitted single-page PDF. Use whenever a job posting/URL is given and a resume is needed.
---
Here's the standalone prompt, updated to fold in the Nightcrawler project and to explicitly instruct picking/emphasizing experience and projects based on the JD:
📄 Prompt to Optimize Resume for ATS
Context:
I am providing two things:

My current resume (LaTeX format). It includes four work experiences — Product Security Intern at Illumio, Security Researcher at Bugcrowd, Windows Internals Security Researcher Intern at CoE-CNDS Labs — and two projects: Nightcrawler (AI-driven SAST/DAST/SCA scanner for MCP servers — Python, FastAPI, React, TypeScript, SQLite, Docker, Claude/AWS Bedrock, asyncio) and Obsedian Guard (two-tier white-box/black-box security testing framework on AWS Lambda/S3).
A target job description (JD) for the role I'm applying to.
Revise my resume so it's optimized for ATS and tailored to the target job. Output must be in the same LaTeX structure and formatting I provided — do not touch the document class, packages, custom commands (\project, \datedentry), spacing, or section styling. Only the content changes.
🔑 Instructions

Keyword Optimization
Extract the most important hard skills, tools, certifications, and role-specific keywords from the JD.
Naturally weave them into Summary, Skills, Experience, and Projects — no keyword stuffing, must still read naturally.
Experience & Project Selection (JD-driven)
Read the JD first and classify it as leaning toward: (a) classic offensive security/pentesting/VAPT, (b) AI/LLM security & AppSec tooling (SAST/DAST/SCA, secure agentic systems), or (c) a mix of both.
Based on that classification, decide which experiences and which project (Nightcrawler vs. Obsedian Guard, or both) to lead with and expand, and which to compress or move lower.
Rewrite bullets under the chosen entries to foreground the achievements, tools, and outcomes most relevant to the JD; de-emphasize (but don't delete) the less relevant ones.
Reorder sections/entries so the most JD-aligned experience and project surface first.
ATS-Friendly Formatting
Keep the existing LaTeX formatting exactly as-is — no tables, text boxes, or graphics.
Keep the same section headers (SUMMARY, EDUCATION, SKILLS, WORK EXPERIENCE, PROJECTS, ACHIEVEMENTS) and consistent bullet formatting.
Place JD keywords in both Skills and Experience/Projects sections for redundant ATS parsing.
Professional Voice & Impact
Strong action verbs (engineered, architected, orchestrated, delivered, drove, validated).
Lead with measurable outcomes (%, counts, time saved).
Avoid vague phrases ("responsible for," "worked on").
Balance
No keyword stuffing; must stay human-readable.
Keep to 1 page.
Final Output
Deliver the complete revised resume as valid, compilable LaTeX, ready to paste into a .tex file.
Preserve the exact formatting/macros.
Tailored Summary at the top, comprehensive Skills section aligned to the JD.
📌 Deliverable
Output the final revised LaTeX resume. It must:

Lead with whichever experience(s) and project(s) — Nightcrawler, Obsedian Guard, or both — best match the JD, per the classification step above.
Pass ATS keyword scans.
Appeal to recruiters and hiring managers.
Keep formatting identical to the structure provided — only content, wording, ordering, and emphasis change.  

## Base resume
The master resume is `base_resume.tex` (in this folder). Always start from it. Never change the
document class, packages, fonts, font sizes, margins, page width, macros or spacing - only content.

## Build (required every time)
1. Save the tailored resume to `../applications/<company>-<role>/<First>_<Last>_Resume.tex`.
2. Run: `python build_resume.py ../applications/<company>-<role>/<First>_<Last>_Resume.tex`
3. The script keeps everything identical and only sets `paperheight` so the PDF is exactly
   ONE page whose height ends right after the last line (+ the 0.2in margin):
   too long -> page grows to fit; too short -> page shrinks so there is no blank space.
4. Report the PDF path and fitted height. Fix any LaTeX error before finishing.

