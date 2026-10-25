---
doc: checklist
status: draft
---

# Job Hunter AI Build Checklist

Build mode: fast (retrospective verification of an existing implementation)

## Slices

- [x] **1. Upload a CV and review a grounded candidate profile**
  Becomes usable: A user can upload a text-based PDF, consent to external inference, receive a validated profile, and review or replace the extracted skills, education, experience, and projects.
  Why now: This establishes the privacy boundary and the trusted candidate data used by every later assessment.
  PRD ref: `prd.md > CV Upload and Extraction`, `prd.md > Profile Review`
  Spec ref: `spec.md > CV Ingestion Service`, `spec.md > Hugging Face Inference Gateway`, `spec.md > Session and Invalidation Manager`
  Build: Use PyMuPDF for local text extraction, send extracted text to the configured Hugging Face provider only after disclosure and consent, validate the response with Pydantic, support review edits, and invalidate profile-dependent state when the CV is replaced.
  Verify (mechanical): `tests/unit/test_cv_inference.py`, `tests/unit/test_rules.py`, and `tests/unit/test_final_fixes.py` pass; the entrypoint AppTest renders the upload page without exceptions; source inspection confirms one `Analyze CV` action.
  Learner check: Upload a text-based PDF, review all four profile sections, edit one value, and replace the CV; confirm the old profile and results do not survive.
  Commit: `Complete verified Job Hunter AI build` (retrospective baseline; see Revisions)

- [x] **2. Configure preferences and run the bounded job-search workflow**
  Becomes usable: A reviewed profile can be paired with required preferences and used in either Live Search or an explicitly selected Dated Snapshot run.
  Why now: This delivers real source tool use while preserving truthful provenance and controlled failure behavior.
  PRD ref: `prd.md > Preferences`, `prd.md > Source Search and Agent Activity`
  Spec ref: `spec.md > Bounded Agent Orchestrator`, `spec.md > Remotive Tool`, `spec.md > Greenhouse Tools`, `spec.md > Run Controller, Progress, Cancellation, and Retry`
  Build: Validate required preferences, orchestrate Remotive and the fixed Greenhouse allowlist, expose actual stage states, support cancellation and retry without overlapping runs, and keep snapshot mode explicit.
  Verify (mechanical): `tests/unit/test_agent.py`, `tests/unit/test_lifecycle.py`, `tests/unit/test_demo_speed.py`, `tests/unit/test_final_fixes.py`, and `tests/contract/test_sources.py` pass with mocked network boundaries.
  Learner check: Run Live Search, then cancel and retry once; separately select Dated Snapshot and confirm it is never presented as live.
  Commit: `Complete verified Job Hunter AI build` (retrospective baseline; see Revisions)

- [x] **3. Inspect independent skills-match and eligibility evidence**
  Becomes usable: Results show `Strong`, `Partial`, or `Weak` skills match separately from `Eligible`, `Unknown`, or `Not Eligible`, with source evidence and original job links.
  Why now: This is the product's unique kernel and prevents a strong technical match from being misrepresented as geographic or legal eligibility.
  PRD ref: `prd.md > Skills Match Assessment`, `prd.md > Eligibility Assessment`, `prd.md > Job Cards and Details`
  Spec ref: `spec.md > Skills-Match Engine`, `spec.md > Deterministic Eligibility Engine`, `spec.md > Ranking and Presentation Service`
  Build: Ground requirement extraction in job text, calculate skills labels deterministically, classify explicit restrictions conservatively, rank without mixing eligibility and skills, and expose evidence and source links.
  Verify (mechanical): `tests/unit/test_rules.py`, `tests/unit/test_skills_compound.py`, `tests/unit/test_final_fixes.py`, and `tests/unit/test_demo_speed.py` pass, including strong-match/location-conflict and missing-evidence cases.
  Learner check: Open one strong skills match with a verified conflict and one `Unknown` result; confirm the evidence explains both without treating missing information as rejection.
  Commit: `Complete verified Job Hunter AI build` (retrospective baseline; see Revisions)

- [x] **4. Handle privacy, replacement, source failures, and repeatable demo data safely**
  Becomes usable: The app fails honestly, can show partial-source outcomes, invalidates old-CV results, and labels dated data throughout the workflow.
  Why now: These boundaries make the proof of concept dependable enough for final review without expanding its feature set.
  PRD ref: `prd.md > States and Boundaries`, `prd.md > Demo Acceptance Scenario`
  Spec ref: `spec.md > Important Failure Modes`, `spec.md > Dated Snapshot Loader`, `spec.md > Safe Logging`, `spec.md > Testing and Acceptance Verification`
  Build: Preserve session-only CV data, exclude credentials and local snapshots from Git, distinguish partial and total source failure, reject stale dependent state, and display collection dates and non-live notices.
  Verify (mechanical): The complete test suite passes (`40 passed`); `.env`, PDF files, and local prepared snapshots are ignored; no token literal is found in trackable project files; Python compilation and the Streamlit entrypoint AppTest pass.
  Learner check: Exercise no-results or source-failure messaging where practical, replace the CV, and confirm snapshot date and `NOT live` labeling on search and results pages.
  Commit: `Complete verified Job Hunter AI build` (retrospective baseline; see Revisions)

## Hands-on Checkpoints

- [x] Early usable behavior explored — the learner implemented and manually tested the main journey before requesting formal completion.
- [x] Final kick-the-tires exploration and feedback completed — the learner reported that the implemented application had been manually tested; no feature changes were made during this completion audit.

## Final Review

- [ ] Final review complete — mechanical verification is complete; learner confirmation that the current audited build is ready to ship is still required.

## Code Tour and App Map

- [x] Learning activity complete — focused recap connected the evidence-based eligibility requirement to deterministic rules and regression tests.
- [x] Optional edit and transfer reflection addressed — not applicable; this completion pass intentionally made no application-code or UI changes.
- [x] `devpost/app-map.html` generated from finished code and checked offline, including a project-grounded practice to reuse; the map is a reference route rather than a claimed live tour.

Activity and evidence: Focused recap of the product principle that skills match must remain independent from eligibility. The requirement appears in `devpost/prd.md > Product Principle`; deterministic enforcement is in `job_hunter/analysis/eligibility.py > evaluate_eligibility` and `job_hunter/analysis/skills.py > assess_skills`; regression evidence is in `tests/unit/test_rules.py > test_strong_skill_match_cannot_override_location_conflict`. The full suite passed with 40 tests.
Route and stops: Reference-only route: `app_pages/upload_cv.py` (`Analyze CV`) → `job_hunter/agent/orchestrator.py` (`run_pipeline`) and `job_hunter/analysis/eligibility.py` (`evaluate_eligibility`) → `app_pages/results.py` (`Evidence-Based Job Matches`).
Edit outcome: Not applicable; the learner requested verification and documentation without rebuilding or changing working features.
Reflection: Already covered through the learner's stated goal of building reliable, tool-using agents and repeated evidence/uncertainty decisions in the approved planning documents.
Activity mode: Focused evidence-based recap with a reference-only code route and offline app map.

## Revisions

- Retrospective checklist adoption — the application was implemented before the official checklist artifact was created, so the verified current build is recorded as one audited baseline rather than fabricating historical per-slice commits.
- Submission tasks separated — the prior submission-oriented checklist was preserved as `devpost/submission-checklist.md`; it is not evidence of `5-build` completion.
