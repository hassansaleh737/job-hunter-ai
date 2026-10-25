---
doc: scope
status: approved
---

# Job Hunter AI

Job Hunter AI is a small proof of concept for finding and evaluating real early-career technology jobs using evidence-based agent actions rather than chatbot-style recommendations.

## The Unique Kernel

The product's distinctive feature is **Evidence-Based Job Matching**. The agent must connect every eligibility and skills-match decision to evidence from the candidate's reviewed CV profile, stated preferences, and the original job posting. Skills match and job eligibility are separate assessments: a role may match the candidate's skills while remaining ineligible because of location or work-authorization restrictions. Missing or ambiguous evidence is never guessed or treated as a confirmed rejection.

## Who It's For

The first user is a Computer Science or Software Engineering student or recent graduate in Egypt seeking a first technology role or paid internship. They have project-level skills such as Python, APIs, FastAPI, LLMs, or AI agents and want remote opportunities that genuinely accept applicants from Egypt.

Today, this person searches several job sites, reads long descriptions, and repeatedly discovers that a supposedly remote role requires more experience, is restricted to another country, is unpaid, or is no longer available.

## The Core Loop

1. The user uploads a text-based PDF CV. A new upload replaces the previous extracted profile and invalidates all results and analysis produced from the previous CV.
2. The application extracts only skills, education, experience, and relevant projects.
3. The user reviews and corrects the extracted profile, then selects role, work-mode, location, and employment-type preferences.
4. The agent plans and runs searches against Remotive and a fixed Greenhouse allowlist of three to five companies.
5. The agent checks posting status and source evidence, evaluates skills match separately from eligibility, and classifies eligibility as `Eligible`, `Not Eligible`, or `Unknown`.
6. The user reviews ranked results, separate skills and eligibility assessments, evidence-grounded reasoning, confirmed conditions, unknown information, exclusion reasons, source attribution, and original job links.

The agent demonstrates meaningful tool use by planning source queries, calling real job tools, collecting evidence, and grounding its analysis in that evidence. Explicit restrictions such as location exclusions, experience thresholds, or work-authorization requirements use deterministic rules whenever possible. AI interpretation supports extraction and semantic comparison but does not override explicit source facts.

The value is not the number of jobs returned. It is the user's ability to distinguish supported matches, explicit conflicts, and unresolved opportunities without misleading certainty.

## Inspiration & Identity

The experience should feel simple, low-friction, and trustworthy: a focused decision dashboard rather than a conversational assistant. It should make evidence, uncertainty, source, and data freshness easy to inspect.

The MVP uses the official [Remotive Public API](https://github.com/remotive-com/remote-jobs-api) and public `GET` endpoints from the official [Greenhouse Job Board API](https://docs.greenhouse.io/job-board).

## Why This Matters to the Learner

The learner wants to practice building a practical, reliable AI agent with real tool calling and an organized agentic workflow. The project should demonstrate search, verification, matching, explicit uncertainty, and safe failure behavior rather than depending only on generated LLM answers.

## What "Working" Looks Like

In a short demo, a user uploads a readable PDF CV, reviews the grounded extracted profile, selects preferences for an early-career remote technology opportunity, and starts the search. The agent calls the approved job sources, verifies available evidence, and presents real postings with separate skills-match analysis and three clearly separated eligibility states.

The compelling moment is seeing the agent reject a role that merely says "Remote" when its original evidence restricts applicants to another country, while keeping an ambiguous role under `Unknown` instead of rejecting it or inventing eligibility.

The demo supports both live results and a repeatable snapshot made from previously collected real results. A snapshot must display its collection date and must never be presented as live data.

## Success Criteria

- A text-based PDF CV produces an editable profile containing only supported skills, education, experience, and relevant projects, with no invented claims.
- Replacing a CV completely replaces the prior extracted profile and invalidates every search result, ranking, and analysis derived from the old CV.
- The agent performs real tool calls against no more than two source types: Remotive and the configured Greenhouse allowlist.
- Every displayed job includes its source, original link, freshness information when available, a skills-match assessment, a separate eligibility classification, and evidence-based reasoning for both.
- A strong skills match can coexist with `Not Eligible` or `Unknown` eligibility and must not change the eligibility decision.
- `Eligible` is conservative: all critical eligibility conditions evaluated by the MVP must have affirmative supporting evidence and no explicit conflicts. A `Worldwide` label confirms only the stated geographic scope; it does not verify unstated legal, employment, residency, or work-authorization requirements. Any unresolved critical eligibility condition keeps the classification `Unknown`.
- `Not Eligible` requires an explicit conflict. Missing or ambiguous evidence is classified as `Unknown`, not as rejection.
- Explicit restrictions are evaluated with deterministic rules whenever possible; AI-generated interpretation must remain grounded in collected evidence and cannot override those rules.
- The system can truthfully return no verified eligible jobs while still explaining exclusions and presenting unresolved `Unknown` opportunities separately.
- A dated real-data snapshot makes the demo repeatable without being labeled or implied to be live.
- Uploaded CV files and extracted personal data remain temporary to the active session and do not appear in application logs or analytics.

## In Scope

- One solo-user workflow for students and recent graduates in Egypt seeking junior technology roles or paid internships.
- Text-based PDF CV upload, lightweight extraction, user review, and correction.
- Preferences covering target roles, remote work, location eligibility, and employment type such as part-time or internship.
- Real job discovery through Remotive and a fixed Greenhouse allowlist of three to five companies.
- Posting verification using available source fields, job descriptions, original links, and relevant application questions.
- Separate evidence-based skills matching and eligibility classification, followed by ranking and explanations that preserve both assessments.
- Real agent orchestration for source selection, tool calling, evidence collection, and grounded analysis, combined with deterministic checks for explicit restrictions.
- Clear handling of empty searches, explicit conflicts, insufficient evidence, source failures, and stale or unavailable postings.
- Remotive attribution and links in accordance with its public API terms.
- Clear disclosure if an external AI provider receives CV content.

## Out of Scope

- Local Egyptian job-board coverage or unrestricted search across all job platforms.
- More than Remotive and the small Greenhouse allowlist.
- Scanned PDFs, images, OCR, or non-PDF CV formats.
- User accounts, persistent profiles, CV storage, databases of personal information, analytics containing personal data, or cross-session history.
- Cover letters, application messages, CV rewriting, or application-document generation.
- Auto-apply, employer-account connections, application submission, or application tracking.
- A general-purpose chatbot experience.

## Privacy and Trust Boundary

Uploaded CVs and extracted personal information exist only for the active session and are not intentionally persisted. CV contents and personally identifiable information must not be written to logs or analytics. Uploading a new CV replaces the prior extracted profile instead of merging profiles and immediately invalidates all results and analysis associated with the previous CV. If CV content is sent to an external AI provider, that fact must be disclosed clearly to the user.

## Later

- OCR and scanned-PDF support.
- Local Egyptian job sources and broader international coverage.
- Additional verified source integrations and dynamic company discovery.
- Cover-letter and application-message preparation grounded in reviewed user data.
- Optional accounts, saved searches, application tracking, and privacy-controlled persistence.

## Explicitly Cut

- **Application preparation and cover letters:** cut to keep the proof of concept centered on evidence-based discovery and matching and to avoid a second hallucination-sensitive workflow.
- **Auto-apply:** cut because it requires platform authorization, user consent, and safeguards beyond this proof of concept.
- **OCR and scanned CVs:** cut to keep CV extraction lightweight and reliable.
- **Broad scraping:** cut because access may be unreliable or conflict with platform terms; only approved public APIs and original public job data are used.
- **Guaranteed positive matches:** cut because reliable behavior must reflect current evidence. A truthful empty result is preferable to presenting an unsuitable job as eligible.
