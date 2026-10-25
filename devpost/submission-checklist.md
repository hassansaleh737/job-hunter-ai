# Job Hunter AI — Final Submission Checklist

Status: **Open / not yet submitted**. Check boxes manually after verifying each item during `6-ship`.

## Build Review

- [ ] `uv run pytest` passes on the final source in Windows.
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

- [ ] `.env` remains excluded (`git check-ignore .env`).
- [ ] All real CV PDFs, private files, local snapshots, and credentials remain unstaged.
- [ ] README matches the final code and the repository has a license.
- [ ] Commit the required source, tests, documentation, and lockfile when appropriate.
- [ ] Push to a public GitHub repository only after a staged-file and secret review.

## Demo and Devpost

- [ ] Record an honest video under the official hackathon time limit.
- [ ] Show only prepared, dated snapshot job results when using Snapshot mode.
- [ ] Explain the difference between skills match and eligibility, with evidence.
- [ ] Upload the video and confirm reviewers can view it without signing in.
- [ ] Complete Devpost submission fields and team information.
- [ ] Confirm all links work and submit before the official deadline.

This checklist is a shipping work plan, not evidence that any item is complete.
