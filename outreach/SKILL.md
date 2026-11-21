---
name: linkedin-outreach
description: After contacts are found for a job, draft personalised LinkedIn connection notes (<=300 chars) for 5-6 contacts, get the user's approval of the exact notes, then send the invites automatically (paced, capped). Logs every invite in applications/outreach.csv.
---

# LinkedIn outreach (auto-send after approval)

Input: `applications/<job>/contacts.md` (from the Hiring Contact Finder skill), the JD and the tailored resume.

## 1. Pick contacts
- 5-6 contacts from `contacts.md` with High/Medium confidence, as the Hiring Contact Finder ranks them
  (recruiter for the role/campus, team members, likely manager). Fewer if evidence is thin - never pad with Low. Skip anyone already in `applications/outreach.csv` for this company.
- Only people with a verified LinkedIn profile URL.

## 2. Draft notes
One note per person, <= 300 characters (LinkedIn's limit; count them), plain text, no emojis, no links:
- Greeting with first name.
- The exact role (and that you applied, if you did).
- One specific, true connection to them (their team, a post, their practice area) - from the evidence in contacts.md, never invented.
- Your single most relevant proof point for that role (from the resume, with a number).
- A light ask ("would love to connect" / "happy to share more") - never ask for a referral in the first note.
Do not repeat the same note verbatim across people. Save drafts to `applications/<job>/outreach.md`.

## 3. Approval
Show the user: name, title, profile URL, why them, and the exact note with its character count.
Proceed only with the notes the user approves (apply their edits exactly).

## 4. Send on LinkedIn (only the approved notes)
The user approves the batch of exact notes in chat; that approval covers sending exactly those notes to exactly
those people, once. Anything else (a new person, an edited note) needs a new approval.
For each approved contact, one at a time:
1. Open the profile URL. Confirm name + current company match contacts.md; if not, skip and report it.
2. If the profile shows **Pending** or **Message** only (already invited/connected), skip it.
3. Click **Connect** (may be under **More**) -> **Add a note**, type the approved note exactly, verify the
   character counter and text, then click **Send** and confirm LinkedIn shows "Invitation sent".
4. Wait a random 60-150 seconds before the next profile.
Limits (protect the account): max 15 invites per day and 80 per rolling 7 days across all companies
(count from outreach.csv). Stop immediately and tell the user if LinkedIn shows a weekly-limit notice, asks for an
email address, shows a CAPTCHA/verification, or warns about unusual activity. Never message, follow, endorse,
or withdraw invites.

## 5. Log
After each send, append to `applications/outreach.csv`
(columns: `date,company,role,name,title,profile_url,channel,note,status`) with status `sent`
(or `skipped` with the reason). Update the job's `contacts` column in `applications/tracker.csv` with the names.
