# Job Hunter AI — Final Submission Checklist

Status: **Open / not yet submitted**. Check boxes manually after verifying each item during `6-ship`.

Official deadline: **October 26, 2026 at 5:00 PM Eastern Time**. This corresponds to **October 27, 2026 at 12:00 AM in Cairo** while Cairo is UTC+3.

## Build Review

- [x] The approved `5-build` checklist and app map are present.
- [x] The complete pytest suite passes on the publication candidate in Windows (`40 passed`).
- [ ] Review extraction, edits, role preferences, Live Search, and Dated Snapshot in the UI.
- [ ] Confirm a three-year CV is not automatically rejected from a role requiring two or more years.
- [ ] Confirm no experience information maps to `Unknown`, not an invented conflict.
- [ ] Verify evidence from reviewed experience and projects contributes to skills match.
- [ ] Test Cancel followed by immediate retry; no overlapping agent worker.
- [ ] Replace a PDF with a different PDF of the same name; no stale results survive.
- [ ] Confirm snapshots show the date and `NOT live` labeling everywhere.
- [ ] Check no-eligible, unknown-only, unavailable, and filter states.
- [ ] Check original employer links before applying.

## Git and Privacy

- [x] `.env` remains excluded (`git check-ignore .env`).
- [x] All real CV PDFs, private files, local snapshots, and credentials remain unstaged and absent from Git history.
- [x] README matches the final code and the repository has a visible open-source license.
- [x] `devpost/scope.md`, `devpost/prd.md`, and `devpost/spec.md` are present in the intended public repository set.
- [x] `devpost/learner-profile.md` remains ignored and absent from Git history.
- [x] Local Skill Pack or tooling folders and patch instructions are excluded from the intended publication set.
- [x] The required source, tests, documentation, and lockfile are committed.
- [ ] Push to a public GitHub repository only after a staged-file and secret review.

## Demo Video

- [ ] Record an English working demo between one minute and less than three minutes.
- [ ] Follow `devpost/demo-runbook.md` without exposing credentials or private CV content.
- [ ] Show only prepared, dated snapshot job results when using Snapshot mode.
- [ ] Explain the difference between skills match and eligibility, with evidence.
- [ ] Upload the video to YouTube or Vimeo and make it publicly visible.
- [ ] Confirm the video opens without authentication and remains under three minutes.

## Devpost Submission

- [ ] Use the project name **Job Hunter AI**.
- [ ] Add the public repository URL to the **Try it out** field.
- [ ] Add learner-written English text explaining what the project does, who it is for, and what was learned.
- [ ] Complete the required explanation of how the Devpost Learn Skill Pack was used.
- [ ] Complete the required age-of-majority checkbox.
- [ ] Complete every additional required field and exit-survey question shown in the authenticated form.
- [ ] Confirm the submission describes only demonstrated behavior and does not invent URLs or results.
- [ ] Confirm all links work and submit before the official deadline.

This checklist is a shipping work plan, not evidence that any item is complete.
