---
doc: prd
status: approved
---

# Job Hunter AI — Product Requirements

Job Hunter AI is a guided, evidence-based job discovery experience for Computer Science and Software Engineering students and recent graduates in Egypt seeking remote early-career technology roles.

Source: `scope.md > The Unique Kernel`, `scope.md > Who It's For`.

## Product Principle

**Evidence-Based Job Matching** is the product's unique kernel. Every assessment must be grounded in the user's reviewed profile, stated preferences, and evidence from the original job posting. The product must never invent CV information, job requirements, or eligibility.

Skills match and job eligibility are independent assessments. A job may be a strong skills match while being `Not Eligible` because of a verified restriction, or `Unknown` because critical eligibility evidence is missing.

Source: `scope.md > The Unique Kernel`, `scope.md > Success Criteria`.

## The Core Journey

1. The user opens a focused landing page and sees what the product does, the five-step journey, accepted file type, and session-only privacy notice.
2. The user uploads a text-based PDF CV. If an external AI provider will receive CV content, the product displays a clear disclosure before processing begins.
3. The product extracts only skills, education, experience, and relevant projects. The user reviews the extracted profile, corrects it, and confirms it.
4. The user selects required job preferences and any optional filters, then continues when the required inputs are complete.
5. The user starts either a live search or an explicitly selected dated snapshot. The product shows truthful progress for source searches, verification, skills matching, and eligibility evaluation.
6. The user receives a results dashboard containing separate skills-match and eligibility assessments, evidence, source attribution, freshness information, and original job links.
7. The user can inspect a result, edit preferences and run a new search, or replace the CV. Replacing the CV removes the prior profile and invalidates every profile-dependent result and analysis.

Source: `scope.md > The Core Loop`, `scope.md > What "Working" Looks Like`.

## Screens and Layout

The product uses five sequential steps rather than one crowded dashboard. A compact indicator communicates the current position: **Upload CV → Review Profile → Preferences → Find Jobs → Results**.

### Step 1 — Upload CV

- A simple header contains a small logo and the name **Job Hunter AI**.
- The centered hero contains:
  - Title: **Find jobs that actually fit you.**
  - Subtitle: **Upload your CV. Let AI discover real opportunities and explain why they match.**
- The primary control supports drag-and-drop and file selection.
- The accepted format is stated clearly as **Text-Based PDF only**.
- A concise notice states: **Your CV is processed for this session only and is not permanently stored.**
- If CV content will be sent to an external AI provider, that disclosure appears before processing.
- No jobs, login, sign-up, chatbot, or unrelated dashboard content appears before upload.

### Step 2 — Review Profile

- The page title is **Review Your Profile** and displays **Step 2 of 5** and the uploaded filename.
- The profile is divided into four editable sections:
  - **Skills:** editable tags that can be added, renamed, or removed.
  - **Education:** university, degree, field of study, and graduation year when available.
  - **Experience:** simple cards containing job title, company, duration, and description when available.
  - **Relevant Projects:** project name, short description, and technologies.
- Education, experience, and project entries can be added, edited, or removed.
- Missing values remain blank or display **Not provided**. The product does not infer a value merely to fill a field.
- Information added or changed manually is visibly distinguished from information extracted from the CV.
- The page provides **Back / Replace CV** and **Confirm & Continue** actions.
- The user is not required to complete every field that was absent from the CV.
- **Confirm & Continue** is enabled when the reviewed profile contains at least one skill, one experience entry with meaningful information, or one relevant project with meaningful information.
- Education by itself is insufficient because it does not provide enough evidence for reliable skills matching.
- If none of the three minimum conditions is met, the page displays a clear validation message requesting usable matching information.

### Step 3 — Job Preferences

- The page displays **Step 3 of 5**.
- Required inputs are:
  - **Target Roles:** at least one role; multiple roles are allowed.
  - **Experience Level:** Student/Intern, Entry-Level/Junior, or Both.
  - **Applying From:** a country value that defaults to Egypt and remains editable.
- Optional inputs are:
  - **Employment Types:** Internship, Part-time, Full-time, Contract, and Freelance; multiple selections are allowed. No selection means **No Preference**.
  - **Paid Only:** an optional preference. Missing compensation evidence remains `Unknown` and is never interpreted as paid.
- **Work Mode** is fixed to **Remote Only** for the MVP.
- Salary range is not shown.
- **Continue** is enabled only when all three required inputs are valid.

### Step 4 — Find Jobs

- The page displays **Step 4 of 5** and a clear sequence of actual agent activity:
  1. Preparing search based on your profile
  2. Searching Remotive
  3. Searching Greenhouse
  4. Verifying job details and restrictions
  5. Evaluating skills match and eligibility
  6. Preparing results
- Every stage displays its actual state: `Pending`, `Running`, `Completed`, or `Failed`.
- The product may display the source name and discovered or analyzed job count when known.
- It does not display prompts, internal reasoning, or overwhelming technical logs.
- It does not describe deterministic checks or orchestration as AI reasoning.
- The user can cancel an active search. Cancellation stops the current run and does not start a duplicate operation.
- After cancellation or failure, the user can retry explicitly.
- **Live Search** is the default search mode.
- **Dated Snapshot** is an explicit alternative that displays the data collection date before the search starts and throughout the results experience.
- Snapshot data is never described as live or reverified unless a direct verification actually occurs.
- A snapshot is never selected automatically to conceal a live-search failure.

### Step 5 — Results

- The page displays **Step 5 of 5** and uses readable job cards rather than a large table.
- Results are grouped and ordered by eligibility:
  1. `Eligible`
  2. `Unknown`
  3. `Not Eligible`
- Within each group, results are ordered by skills-match assessment and then by posting freshness when trustworthy freshness data is available.
- The user can filter by eligibility, skills match, and source.
- Available actions are **View Details**, **Open Original Job**, **New Search / Edit Preferences**, and **Replace CV**.
- If the run used a snapshot, the dashboard displays the snapshot label and collection date prominently.

Source: `scope.md > The Core Loop`, `scope.md > Inspiration & Identity`, `scope.md > Privacy and Trust Boundary`.

## Look and Feel

- The interface is entirely in English and should be responsive where practical.
- The visual direction is a clean, modern, professional SaaS dashboard.
- Use a light theme with an off-white or very light gray background, dark navy or charcoal text, and muted blue as the primary accent.
- Use subtle green, amber, and red treatments for eligibility states, while always displaying the status in text so meaning never depends on color alone.
- Use clear typography, generous spacing, rounded cards, and readable evidence sections.
- Avoid crowded dashboards, chatbot layouts, large tables, excessive animation, fake progress, unnecessary 3D effects, and overwhelming technical logs.

## Features and Behavior

### CV Upload and Extraction

- The product accepts one text-based PDF CV at a time.
- It extracts only skills, education, experience, and relevant projects.
- Extraction must remain grounded in text present in the uploaded CV. Unsupported claims are not added.
- A scanned PDF or a PDF whose text cannot be extracted produces a clear request for a text-based version.
- The uploaded file and extracted personal information exist only for the active session and are not intentionally persisted.
- CV content and personally identifiable information do not appear in logs or analytics.
- Uploading another CV fully replaces the current extracted profile; information from different CVs is never merged.
- Replacing the CV invalidates prior results, rankings, and analysis immediately.

Source: `scope.md > In Scope`, `scope.md > Privacy and Trust Boundary`.

#### Acceptance Criteria

- [ ] A readable text-based PDF advances to **Review Your Profile** and displays only the four approved information categories.
- [ ] Missing CV information remains blank or **Not provided**.
- [ ] A scanned or unreadable PDF does not create a profile and displays corrective guidance.
- [ ] A replacement CV removes the old profile and all profile-dependent results before the new profile is shown.
- [ ] External-provider disclosure appears before CV content is sent externally, when applicable.

### Profile Review

- The user can correct extracted information without being forced to supply information absent from the CV.
- Manual additions and changes are marked as user-provided so they are not represented as extracted evidence.
- Subsequent matching uses the reviewed profile, not the unconfirmed extraction.

Source: `scope.md > The Core Loop`, `scope.md > Success Criteria`.

#### Acceptance Criteria

- [ ] The user can add, edit, and remove supported profile information.
- [ ] Extracted and user-provided information are visibly distinguishable.
- [ ] **Confirm & Continue** is enabled when the profile contains at least one skill, one meaningful experience entry, or one meaningful relevant project.
- [ ] Education alone does not enable **Confirm & Continue**.
- [ ] A profile without usable matching information displays a clear validation message and does not advance.
- [ ] A valid reviewed profile advances to Job Preferences without requiring all four profile sections.
- [ ] Returning to replace the CV follows the replacement and invalidation rules.

### Preferences

- Required and optional fields behave as defined in **Step 3 — Job Preferences**.
- `Paid Only` does not transform missing pay information into a negative or positive claim; missing pay evidence remains `Unknown`.
- Remote-only is visible as a fixed MVP constraint.

#### Acceptance Criteria

- [ ] Continue remains unavailable until at least one target role, an experience level, and an applying-from country are present.
- [ ] No employment-type selection is interpreted as **No Preference**.
- [ ] The applying-from country initially displays Egypt and can be changed.
- [ ] Salary range is not requested.

### Source Search and Agent Activity

- A live run searches the Remotive source and the initial Greenhouse allowlist through real tool calls.
- The initial proposed Greenhouse boards are Constructor TECH (`constructortech`, EU), Ritual (`ritual`), Cadence Solutions (`solutions`), and Orbis (`orbisoperations`). They are source candidates, not guaranteed eligible employers.
- Before `4-spec`, each public endpoint, board token, current posting availability, and suitability for the demo must be verified. An unsuitable board may be replaced only when necessary, with the reason documented.
- Search progress reflects actual execution state and exposes understandable source-level activity.
- The product respects Remotive attribution and links each result to its original source.
- The user can cancel or retry without creating overlapping duplicate runs.

Source: `scope.md > The Core Loop`, `scope.md > In Scope`.

#### Acceptance Criteria

- [ ] The six progress stages update only when their underlying work changes state.
- [ ] A completed live run records which sources completed or failed.
- [ ] The Greenhouse search uses only boards whose public endpoints, tokens, current availability, and demo suitability were verified before `4-spec`.
- [ ] Cancel leaves the run visibly cancelled and permits one explicit retry.
- [ ] Live and snapshot modes remain clearly distinguishable before, during, and after a run.

### Skills Match Assessment

- Skills match is reported independently from eligibility using `Strong`, `Partial`, or `Weak`.
- The assessment identifies matching skills and missing skills with evidence from the reviewed profile and job posting.
- The product does not show an unexplained numerical percentage.
- Skills match cannot promote or override an eligibility classification.

Source: `scope.md > The Unique Kernel`, `scope.md > Success Criteria`.

#### Acceptance Criteria

- [ ] Each result displays one of the three match assessments.
- [ ] Job details show matched and missing skills.
- [ ] A result can visibly show `Strong` skills match together with `Not Eligible` or `Unknown` eligibility.

### Eligibility Assessment

- Eligibility is classified as `Eligible`, `Not Eligible`, or `Unknown` using source evidence and conservative rules.
- `Eligible` requires affirmative evidence for every critical eligibility condition evaluated by the MVP and no explicit conflict.
- `Not Eligible` requires an explicit conflict such as a geographic, experience, employment-type, or work-authorization restriction.
- `Unknown` means available evidence is insufficient to confirm or reject eligibility.
- A `Worldwide` label confirms only the advertised geographic scope. It does not confirm unstated legal, residency, employment, or work-authorization requirements.
- Explicit restrictions take precedence over semantic interpretation.

Source: `scope.md > The Unique Kernel`, `scope.md > Success Criteria`.

#### Acceptance Criteria

- [ ] Every classification displays its supporting evidence or unresolved requirement.
- [ ] Missing evidence never produces `Not Eligible`.
- [ ] An explicit conflict produces `Not Eligible` even when skills match is `Strong`.
- [ ] A critical unresolved requirement produces `Unknown` rather than `Eligible`.

### Job Cards and Details

Each job card displays:

- Job title and company
- Source
- Employment type when known
- Location and remote restrictions
- Skills-match assessment
- Eligibility status
- Key matching skills
- Main eligibility evidence or reason for uncertainty
- Source date or last-verified information when available

**View Details** reveals:

- Job-description summary
- Matched skills
- Missing skills
- Eligibility evidence
- Explicit restrictions
- Unknown requirements
- Short evidence references or excerpts from the posting
- Original job link
- Source attribution and freshness information

Evidence excerpts remain short and directly relevant. The original posting remains the authoritative source.

#### Acceptance Criteria

- [ ] Every card keeps skills match and eligibility visually separate.
- [ ] Details distinguish confirmed evidence, explicit restrictions, and unknown requirements.
- [ ] **Open Original Job** opens the source-provided posting link.
- [ ] Filters update the visible set without changing any underlying assessment.

## States and Boundaries

- **First use:** only the upload experience and explanatory content are shown; no jobs appear before a CV is processed.
- **Extracting CV:** the product shows an honest processing state and does not reveal internal prompts or CV contents in logs.
- **CV extraction failed:** the profile is not created; the user is asked to upload a text-based PDF.
- **External AI analysis failed:** the product reports the failure and offers retry without presenting incomplete analysis as confirmed.
- **Ready to search:** the reviewed profile and required preferences are complete.
- **Searching:** actual progress states and counts are shown when available.
- **Cancelled:** processing stops, no duplicate run begins, and retry is available.
- **No jobs found:** the product explains that no results were found and offers preference editing and a new search.
- **No eligible jobs:** `Unknown` results remain separate, and explicit reasons for `Not Eligible` results are available.
- **Unknown results only:** the product explains that evidence was insufficient to confirm or reject eligibility.
- **One source failed:** partial results from the successful source are shown with a warning naming the failed source.
- **Both sources failed:** no successful result state is shown; the product displays an error and offers retry.
- **Stale or unavailable posting:** the result is not presented as verified active. It is labeled `Stale` or `Unavailable`, with existing details accessible when available.
- **Live results:** labeled as live and accompanied by available freshness or verification information.
- **Dated snapshot:** labeled throughout with its collection date and never silently substituted for a failed live run.
- **CV replaced:** the prior profile, results, rankings, and analysis disappear before the new CV workflow proceeds.
- **Session ended:** CV data, reviewed profile, and results do not persist into a new session.

## Demo Acceptance Scenario

The approximately 60-second demonstration must be able to show:

1. Uploading a text-based PDF CV.
2. Reviewing extracted skills and confirming the profile.
3. Selecting target roles and required preferences.
4. Starting the agent and showing truthful tool activity for Remotive and Greenhouse.
5. Displaying real job results from both approved source types.
6. Opening a job with a `Strong` skills match that is `Not Eligible` because of verified geographic evidence.
7. Opening another job classified `Unknown` because critical eligibility evidence is missing.
8. Showing evidence, source attribution, freshness information, and original job links.

If a dated snapshot is used, its collection date must remain visible. The defining demonstration statement is: **Strong Skills Match does not mean Eligible.**

Source: `scope.md > What "Working" Looks Like`.

## Product Decisions

- Use a five-step guided experience instead of one crowded screen so the workflow remains understandable.
- Require profile review before matching so extracted information is never silently treated as correct.
- Permit profile confirmation with at least one skill, one meaningful experience entry, or one meaningful project; education alone is insufficient for matching.
- Keep work mode fixed to remote-only and omit salary-range search to protect the MVP boundary.
- Use `Strong`, `Partial`, and `Weak` instead of an unexplained numerical score.
- Keep skills match independent from eligibility so a technically relevant job is not misrepresented as applicable.
- Make live search the default and dated snapshots explicit so demo reliability never obscures data provenance.
- Show agent actions at a human-readable stage level without exposing prompts or pretending deterministic checks are AI reasoning.
- Permit partial results when one source fails, but never claim success when both sources fail.
- Store no personal data beyond the active session and invalidate dependent results whenever the CV changes.
- Start with the four named Greenhouse board candidates and verify them before `4-spec`, replacing a board only when necessary and documenting why.

## What We're Building

- The five-step journey from text-based CV upload through evidence-based results.
- Editable, grounded extraction of the four approved profile categories.
- Required and optional preferences defined in this PRD.
- Live Remotive and Greenhouse searches plus an explicitly dated real-data snapshot mode.
- Truthful agent progress, cancellation, retry, and partial-source behavior.
- Independent skills-match and eligibility assessments with inspectable evidence.
- Job cards, details, filters, source attribution, freshness information, and original links.
- Session-only privacy behavior and complete CV-replacement invalidation.

## Deferred From the POC

- **Cover letters and application messages:** deferred because they introduce a separate generation and grounding workflow.
- **Auto-apply and application tracking:** deferred because they require external authorization, consent, and additional safeguards.
- **OCR and scanned PDFs:** deferred to keep CV ingestion small and reliable.
- **Accounts, saved jobs, and persistence:** deferred to protect privacy and avoid account infrastructure.
- **Local Egyptian sources and additional platforms:** deferred to keep source integration limited to Remotive and the Greenhouse allowlist.

## Possible Later Enhancements

- OCR and additional CV formats.
- Privacy-controlled saved profiles, searches, and application tracking.
- Local Egyptian job sources and broader international coverage.
- Grounded application-message preparation after a user selects a job.

## Non-Goals

- The product is not a chatbot.
- It does not guarantee that suitable jobs exist or manufacture positive matches for a demo.
- It does not verify unstated legal facts or replace the employer's final eligibility decision.
- It does not scrape unrestricted job platforms.
- It does not store CVs or personal profiles permanently.
- It does not generate cover letters, rewrite CVs, submit applications, or apply automatically.
