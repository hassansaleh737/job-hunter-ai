---
doc: spec
status: approved
---

# Job Hunter AI — Technical Specification

## How This Works, in Plain Language

Job Hunter AI runs as one small Python web application. The user uploads a text-based PDF; PyMuPDF reads its text locally, and the application shows a clear disclosure before sending that extracted text to the configured Hugging Face Inference Provider. The model returns a structured candidate profile, which is validated before the user can review it.

When the user starts a search, a bounded agent creates a small search plan and requests only approved tools. Those tools retrieve real postings from Remotive and four public Greenhouse boards. The application verifies and normalizes the returned facts, then uses the model only where language interpretation is useful, such as extracting stated requirements and associating them with short evidence excerpts.

Deterministic code—not the language model—makes the final eligibility classification and skills-match label. Explicit restrictions win over model interpretation, and missing critical evidence remains `Unknown`. This division keeps the workflow agentic while preventing the model from inventing job facts or overriding source evidence.

Everything associated with a CV stays in the active Streamlit session. There is no application database, user account, analytics service, or permanent CV storage. A replacement CV creates a new profile version and immediately invalidates all prior profile-dependent results.

This single-process architecture is intentionally small enough for one developer and a hackathon demonstration.

## The Core Journey Through the System

1. **Upload CV:** Streamlit accepts one PDF in memory. The upload service checks the file type and size, and PyMuPDF extracts text locally. A blank or image-only document is rejected with guidance to upload a text-based PDF.
2. **External processing disclosure:** Before inference, the interface identifies Hugging Face routing, the configured provider, and the fact that extracted CV text will leave the application process. Processing begins only after the user continues.
3. **Extract and review:** `InferenceClient` requests a schema-constrained profile. Pydantic validates the response. The user reviews skills, education, experience, and relevant projects; edits are marked as user-provided.
4. **Set preferences:** The application validates the required target roles, experience level, and applying-from country, plus the optional employment types and paid-only preference.
5. **Run the agent:** A unique run starts in one background worker. The bounded orchestrator requests source tools, validates every tool name and argument, searches Remotive and the Greenhouse allowlist, and emits truthful stage events.
6. **Verify and evaluate:** Source adapters normalize jobs and attach provenance. Explicit restrictions are evaluated by deterministic rules. The model may extract requirements and evidence into validated structures, but cannot set or override eligibility.
7. **Present results:** Deterministic ranking groups `Eligible`, `Unknown`, then `Not Eligible`, and orders each group by skills match and trustworthy freshness. Cards and details show source evidence, unknowns, attribution, and original links.
8. **Cancel, retry, or replace:** Cancellation is cooperative between bounded operations; late output from a cancelled run is discarded. Retry creates a new run without overlap. Replacing the CV increments the profile version and clears dependent state before processing the new file.

PRD ref: `prd.md > The Core Journey`, `prd.md > States and Boundaries`.

## Stack

| Area | Choice | Why |
|---|---|---|
| Language | Python 3.12 | Matches the learner's experience and the selected libraries. |
| Environment | `uv` with a locked `pyproject.toml` and `uv.lock` | Fast, reproducible setup without a separate dependency layer. |
| Web UI | Streamlit 1.57 or a later compatible 1.x release | Supports the five-step Python UI, session state, fragments, forms, and application testing with little infrastructure. |
| Data validation | Pydantic 2.x | Defines JSON schemas for model output and rejects malformed tool arguments and responses. |
| PDF extraction | PyMuPDF 1.26+ | Extracts text locally without uploading the PDF itself. |
| Hosted inference | `huggingface_hub.InferenceClient` 1.25+ | Provides Hugging Face Inference Provider routing, chat completions, tools, and structured response formats. |
| HTTP | HTTPX 0.28+ | Supplies explicit timeouts, redirects, connection reuse, and testable adapters for job APIs and link checks. |
| HTML cleanup | Beautiful Soup 4 | Converts source descriptions to safe plain text for analysis and evidence excerpts. |
| Tests | pytest, pytest-cov, respx, and Streamlit AppTest | Covers pure rules, HTTP contracts, workflow integration, and visible application behavior. |

The verified inference default is `Qwen/Qwen3.5-9B` with `HF_PROVIDER=deepinfra`. On 2026-10-25, Hugging Face's compatibility table listed this pair as supporting both tools and structured outputs at approximately USD $0.10 per million input tokens and $0.15 per million output tokens. Authenticated synthetic smoke tests confirmed both capabilities through `InferenceClient`. The application still reads `HF_MODEL` and `HF_PROVIDER` from environment variables so the pair can be replaced without changing workflow code, but any replacement must pass the same compatibility and privacy gates.

Major documentation:

- [Streamlit documentation](https://docs.streamlit.io/)
- [PyMuPDF documentation](https://pymupdf.readthedocs.io/)
- [Hugging Face InferenceClient](https://huggingface.co/docs/huggingface_hub/guides/inference)
- [Hugging Face function calling](https://huggingface.co/docs/inference-providers/guides/function-calling)
- [Hugging Face structured outputs](https://huggingface.co/docs/inference-providers/guides/structured-output)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [HTTPX documentation](https://www.python-httpx.org/)

## Where It Runs and How Someone Tries It

The proof of concept runs locally as one Streamlit process and opens in a desktop browser. Local execution is the required demo path; public deployment is optional and is not part of this specification.

Required environment variables:

```text
HF_TOKEN=<Hugging Face user access token with inference permission>
HF_MODEL=Qwen/Qwen3.5-9B
HF_PROVIDER=deepinfra
```

`HF_TOKEN` must be supplied through the process environment or an ignored local `.env` file loaded at startup. It must never appear in source, committed configuration, logs, snapshots, exceptions shown to users, or tests. `.env.example` contains names and safe defaults only.

Planned setup and start commands:

```powershell
uv sync
uv run streamlit run streamlit_app.py
```

The user opens the local URL printed by Streamlit, normally `http://localhost:8501`. The public GitHub repository must include setup instructions and a dated snapshot for a repeatable recording, but never secrets or CV data.

## Look and Feel

The UI follows the approved light, modern SaaS direction: off-white background, dark navy or charcoal text, muted blue actions, rounded cards, clear typography, and generous spacing. Eligibility uses subtle green, amber, and red accents together with explicit text and icons, so color is never the only signal. The five-step indicator remains compact and persistent. Agent progress shows actual states and concise counts, not animation-based or estimated progress.

Streamlit's native components and theme configuration are preferred. Small, scoped CSS may refine spacing and card presentation, but the project will not introduce a frontend framework or custom JavaScript application.

PRD ref: `prd.md > Look and Feel`, `prd.md > Screens and Layout`.

## Components

### Streamlit Application Shell and Navigation

`streamlit_app.py` configures the theme-facing shell and uses `st.navigation` for the five guided pages. Navigation guards prevent skipping required steps. `st.session_state` holds only the active session's state. A polling fragment reads progress events without rerunning unrelated forms.

PRD ref: `prd.md > Screens and Layout`.

### Session and Invalidation Manager

The session manager owns `session_id`, `profile_version`, confirmed profile, preferences, active run, and results. Replacing a CV first increments `profile_version`, requests cancellation of any active run, and clears the old PDF bytes, extracted text, profile, preferences-derived analysis, and results. Every background result carries both `run_id` and `profile_version`; mismatches are discarded.

PRD ref: `prd.md > CV Upload and Extraction`, `prd.md > States and Boundaries`.

### CV Ingestion Service

The service receives PDF bytes in memory, validates the PDF signature and configurable upload limit, and extracts text with PyMuPDF. It rejects encrypted, unreadable, empty, or image-only PDFs. It normalizes whitespace but does not infer content. The PDF bytes are released after extraction and are never written to disk.

Only the extracted text is eligible to leave the process, and only after the external-provider disclosure is shown. CV text and model payloads are explicitly excluded from logs and analytics.

PRD ref: `prd.md > CV Upload and Extraction`.

### Hugging Face Inference Gateway

One adapter constructs `InferenceClient(provider=HF_PROVIDER, api_key=HF_TOKEN)` and sends requests using `HF_MODEL`. It exposes two narrow operations:

- `extract_candidate_profile(text) -> CandidateProfileExtraction`
- `extract_job_requirements(job_text, source_facts) -> JobRequirementExtraction`

Each operation passes a Pydantic-generated JSON Schema through `response_format`, parses the returned JSON, and validates it with Pydantic. Extra fields are forbidden. Evidence-bearing fields include a short source excerpt or source-field reference. A schema failure or unsupported response is rejected; the gateway may make one bounded validation retry but never silently accept malformed output. The restored first-version CV path sends the locally extracted text directly, capped only by the existing 18,000-character PDF extraction boundary, and uses `extra_body={"reasoning_effort": "none"}` with a 2,048-token output allowance. It does not set a custom inference-client timeout. The earlier compatibility smoke test established that 1,024 tokens was sufficient for its small synthetic profile, while 256 tokens could end before final JSON content was emitted.

The same gateway supports agent planning and function calls. Tool calls are treated as untrusted input: names must exist in the fixed registry, arguments must pass Pydantic validation, and values such as Greenhouse board tokens must belong to the configured allowlist.

PRD ref: `prd.md > CV Upload and Extraction`, `prd.md > Source Search and Agent Activity`.

### Bounded Agent Orchestrator

The orchestrator is a small application-owned state machine, not a general-purpose agent framework. Its maximum work per run is fixed: one planning response, approved source calls, one requirement-extraction batch per shortlisted job, and one final preparation pass. It does not execute arbitrary code, browse arbitrary domains, or call tools outside the registry.

The model receives the reviewed profile summary, preferences, source-tool schemas, and limits. It proposes keyword queries and requests tools such as:

- `search_remotive(query, category, limit)`
- `list_greenhouse_jobs(board_token)`
- `get_greenhouse_job(board_token, job_id)`

The orchestrator executes approved calls and records sanitized tool events. Source coverage is a deterministic invariant: a live run attempts Remotive and every configured Greenhouse board even if the model omits one. The model therefore helps plan meaningful queries and emits real function calls, while the orchestrator controls coverage, bounds, validation, retries, and safety.

No chain-of-thought, prompts, or raw model traces are displayed. The UI shows only factual stages, sources, counts, and failures. If planning fails, the run fails honestly rather than being presented as successful AI reasoning.

PRD ref: `prd.md > Step 4 — Find Jobs`, `prd.md > Source Search and Agent Activity`.

### Remotive Tool

The adapter calls `GET https://remotive.com/api/remote-jobs` using supported `category`, `search`, and `limit` parameters. It normalizes returned jobs, preserves the Remotive URL, and records `publication_date`, `candidate_required_location`, job type, description, and retrieval time.

Because Remotive advises no more than four fetches per day and blocks excessive traffic over two requests per minute, the single-process app uses an in-memory six-hour source cache. A tool invocation reports whether the response was fetched during the run or served from this temporary cache and retains the original retrieval time. No cache is written to disk. The UI always attributes Remotive and links to its supplied URL.

PRD ref: `prd.md > Source Search and Agent Activity`, `scope.md > In Scope`.

### Greenhouse Tools

The adapter uses unauthenticated public GET endpoints only:

- `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`
- `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}?questions=true&pay_transparency=true`

The allowlist is:

| Company | Board token | Verification on 2026-10-25 |
|---|---|---|
| Constructor TECH | `constructortech` | Endpoint active; 37 jobs; early-career technical postings present. |
| Ritual | `ritual` | Endpoint active; 15 jobs; one older software internship candidate. |
| Cadence Solutions | `solutions` | Endpoint active; 21 jobs; current software internship with a U.S.-remote restriction. |
| Orbis | `orbisoperations` | Endpoint active; 23 jobs; current entry-level AI posting with explicit U.S. eligibility evidence. |

All four tokens and list endpoints returned valid job data during the feasibility check, so no replacement is required. These are discovery sources, not guaranteed eligible employers. Detail calls are limited to shortlisted jobs so application questions can provide additional location or work-authorization evidence.

PRD ref: `prd.md > Source Search and Agent Activity`, `prd.md > Demo Acceptance Scenario`.

### Posting Verification and Normalization

Adapters convert source payloads into one canonical `JobPosting` without erasing the raw field provenance needed for evidence. A live posting is considered source-active only if it appears in the current source response or its Greenhouse detail endpoint succeeds. Original links are checked only when supplied by an approved source; HTTP requests use a short timeout, limited redirects, and block private-network destinations. Link-check failure marks link availability as unknown or unavailable and never creates eligibility evidence.

HTML is decoded and converted to plain text. Short evidence excerpts are retained with field paths, never detached from the original source URL. No job description is invented or rewritten as fact.

PRD ref: `prd.md > Job Cards and Details`, `prd.md > States and Boundaries`.

### Skills-Match Engine

The model extracts stated required and preferred skills into a validated structure, each tied to a source excerpt. Deterministic normalization handles case, punctuation, and a small reviewed alias map. Candidate evidence comes only from the confirmed profile; manually entered facts remain labeled user-provided.

The displayed label is deterministic:

- `Strong`: at least one stated required skill exists, at least 70% of stated required skills are supported, and no explicitly mandatory core skill is missing.
- `Partial`: some relevant evidence matches, but required-skill coverage is below the strong threshold or an explicit required skill is missing.
- `Weak`: no meaningful supported overlap, or required-skill coverage is below 30%.

If the posting states no usable skill requirements, the result cannot be `Strong`; it is `Partial` only when role/project evidence supports a meaningful connection, otherwise `Weak`. The UI displays labels and supporting skills, not the internal ratio as a false-precision percentage.

Skills match never changes eligibility.

PRD ref: `prd.md > Skills Match Assessment`.

### Deterministic Eligibility Engine

The engine evaluates separate critical conditions and stores the state and evidence for each:

- posting activity and link availability;
- geographic eligibility from the applying-from country;
- explicit residency, work-authorization, or hiring-region restrictions;
- experience-level requirements;
- selected employment type;
- compensation evidence when `Paid Only` is selected;
- remote-work evidence for the fixed Remote Only mode.

Each condition is `confirmed`, `conflict`, `unknown`, or `not_applicable`.

- Overall `Not Eligible` requires at least one explicit `conflict`.
- Overall `Eligible` requires every applicable critical condition to be `confirmed` and no conflict.
- Otherwise, overall eligibility is `Unknown`.

`Worldwide` confirms only the advertised geographic scope. It does not confirm unstated legal, residency, payroll, or work-authorization conditions. Missing pay information under `Paid Only` is `unknown`, not unpaid. Deterministic explicit facts always take precedence over model-extracted interpretation.

PRD ref: `prd.md > Eligibility Assessment`.

### Ranking and Presentation Service

The service groups results in the approved eligibility order and then sorts by skills label and trustworthy freshness. It never lets a strong match outrank the eligibility group. Filters operate on stored assessments without recomputation. Details separate confirmed evidence, restrictions, and unknowns and include attribution, retrieval/collection dates, and original links.

PRD ref: `prd.md > Step 5 — Results`, `prd.md > Job Cards and Details`.

### Run Controller, Progress, Cancellation, and Retry

Each search gets a unique `run_id`, immutable profile version, cancellation token, stage state, and event queue. One `ThreadPoolExecutor` worker is allowed per session. Network calls use connect/read timeouts. Cancellation is checked before and after every source and inference call; an in-flight HTTP request may finish, but its result is ignored after cancellation. Retry begins only after the prior run is terminal and creates a new ID.

The six visible stages update from real events. A failed source remains failed. One successful source permits partial results with a warning; two failed sources produce an error state with no success claim.

PRD ref: `prd.md > Step 4 — Find Jobs`, `prd.md > States and Boundaries`.

### Dated Snapshot Loader

A snapshot is a version-controlled JSON fixture containing only previously collected public job facts, evidence, source URLs, source identifiers, and `collected_at`. It contains no CV, profile, preference, or model prompt. Snapshot mode bypasses network search and is labeled throughout as `Dated Snapshot`; it is never selected automatically and is not described as reverified unless live checks actually run.

The same normalization, matching, and eligibility pipeline processes snapshot jobs so the demonstration exercises the real application behavior.

PRD ref: `prd.md > Step 4 — Find Jobs`, `prd.md > Demo Acceptance Scenario`.

### Safe Logging

Logs contain stage names, run IDs, source identifiers, counts, durations, sanitized error categories, model/provider names, and token/cost metadata when available. They exclude PDF bytes, extracted CV text, profile fields, job-description bodies, evidence excerpts, prompts, model responses, tool payloads, tokens, and user-entered personal data. No analytics service is included.

PRD ref: `prd.md > CV Upload and Extraction`, `scope.md > Privacy and Trust Boundary`.

## Data Model

All application models are Pydantic models. Profile-dependent objects carry `profile_version`; source-derived facts carry provenance.

| Model | Important fields | Lifetime |
|---|---|---|
| `CandidateProfile` | skills, education, experience, projects, provenance per field, confirmed flag, version | Active session only |
| `JobPreferences` | target roles, experience level, applying-from country, employment types, paid-only, fixed remote mode | Active session only |
| `SearchPlan` | normalized keywords, requested tools, source limits | One run |
| `JobPosting` | source/source ID, title, company, description text, source URL, location, employment type, dates, raw-field references | One run or public snapshot |
| `EvidenceItem` | fact type, normalized value, short excerpt/field path, source URL, confidence type (`explicit` or `interpreted`) | One result |
| `SkillAssessment` | label, matched skills, missing skills, evidence references, internal coverage values | One result |
| `EligibilityCondition` | condition, state, evidence references, explanation | One result |
| `JobAssessment` | posting, skill assessment, condition list, overall eligibility, freshness state | Active session only |
| `SearchRun` | run ID, profile version, mode, stages, source outcomes, cancellation state, timestamps | Active session only |
| `SnapshotManifest` | snapshot ID, collection date, source set, job records, schema version | Version-controlled public data only |

Session state holds current objects in memory. The application performs no serialization of personal state. Closing or expiring the Streamlit session loses the profile and results. Snapshot data is the sole planned application data committed to the repository, and it is public job data only.

## File Structure

```text
job-hunter-ai-hackathon/
├── streamlit_app.py                 # Application entry point and navigation
├── pyproject.toml                   # Python metadata, dependencies, and tool settings
├── uv.lock                          # Reproducible dependency lock
├── .env.example                     # Environment variable names; never secrets
├── .gitignore                       # Excludes .env, local CVs, caches, and test artifacts
├── .streamlit/
│   └── config.toml                  # Light theme and safe Streamlit settings
├── app_pages/
│   ├── upload_cv.py                 # Step 1
│   ├── review_profile.py            # Step 2
│   ├── preferences.py               # Step 3
│   ├── find_jobs.py                 # Step 4 and progress polling
│   └── results.py                   # Step 5, filters, cards, and details
├── job_hunter/
│   ├── config.py                    # Validated environment and allowlist settings
│   ├── models.py                    # Pydantic domain and response models
│   ├── session.py                   # State lifecycle and profile invalidation
│   ├── privacy.py                   # Disclosure text and log redaction helpers
│   ├── cv/
│   │   ├── pdf.py                   # Local PyMuPDF extraction
│   │   └── profile_extractor.py     # Validated Hugging Face profile extraction
│   ├── inference/
│   │   ├── client.py                # InferenceClient gateway
│   │   ├── schemas.py               # Structured-output and tool schemas
│   │   └── prompts.py               # Minimal versioned instructions
│   ├── agent/
│   │   ├── orchestrator.py          # Bounded state machine and tool loop
│   │   ├── registry.py              # Fixed tool registry and argument validation
│   │   ├── run_controller.py        # Worker, events, cancellation, retry
│   │   └── progress.py              # User-visible stage model
│   ├── sources/
│   │   ├── base.py                  # Source adapter contract
│   │   ├── remotive.py              # Remotive API and temporary cache
│   │   ├── greenhouse.py            # Greenhouse list/detail APIs
│   │   └── link_check.py             # Restricted source-link verification
│   ├── analysis/
│   │   ├── requirements.py          # Evidence-grounded requirement extraction
│   │   ├── skills.py                # Deterministic skill assessment
│   │   ├── eligibility.py           # Deterministic eligibility rules
│   │   └── ranking.py               # Stable grouping and ordering
│   └── snapshots/
│       └── loader.py                # Manifest validation and loading
├── data/
│   └── snapshots/
│       └── demo.json                 # Dated public job evidence; no personal data
├── tests/
│   ├── fixtures/                    # Sanitized source/provider response fixtures
│   ├── unit/                        # PDF, schemas, rules, ranking, invalidation
│   ├── contract/                    # Remotive, Greenhouse, and HF response contracts
│   ├── integration/                 # Bounded workflow with mocked external services
│   └── ui/                          # Streamlit AppTest and navigation/state checks
├── devpost/
│   ├── learner-profile.md
│   ├── scope.md
│   ├── prd.md
│   └── spec.md
└── README.md                         # English setup, privacy, attribution, and demo guide
```

## External Services and Dependencies

### Hugging Face Inference Providers and DeepInfra

- **Client:** `huggingface_hub.InferenceClient` with `HF_TOKEN`, `HF_MODEL`, and `HF_PROVIDER`.
- **Calls:** chat completions with either `tools`/`tool_choice="auto"` for planning or `response_format={"type": "json_schema", ...}` for typed extraction.
- **Validation:** Pydantic schemas forbid extra fields and reject malformed output. One bounded correction retry is allowed.
- **Verified default:** `Qwen/Qwen3.5-9B` through `deepinfra`.
- **Compatibility verified 2026-10-25:** a real `InferenceClient` call returned the requested synthetic `search_jobs` function call with Pydantic-valid arguments. A separate strict JSON Schema call returned a synthetic profile accepted by Pydantic, including two stated skills, no invented experience, and one stated project. The structured call required `reasoning_effort="none"` and a 1,024-token output allowance; no CV or personal data was used.
- **Pricing reviewed 2026-10-25:** Hugging Face routed requests use provider pass-through pricing with no HF markup. The model table showed about $0.10/M input tokens and $0.15/M output tokens for this pair. Hugging Face Free accounts include no monthly inference credit at the time of review; purchased credits or an eligible paid plan are required. Pricing can change and must be checked before the demo.
- **Privacy reviewed 2026-10-25:** Hugging Face states that routed request/response bodies are not stored and are not used for training; debugging logs may be kept for up to 30 days but exclude user data and tokens. DeepInfra's terms state zero retention for request/response customer data after processing, no training on it, and limited exceptions for non-content operational metadata, legal/security requirements, explicitly authorized support, and optional retained features. The user must still see the provider disclosure before CV text is sent.
- **Rate limits:** No fixed Inference Provider request quota for this routed model/account was published. The app treats HTTP 429 as an explicit provider failure, honors `Retry-After` when present, uses capped backoff, and never launches concurrent model calls for one session. The account billing/usage page must be checked before real-CV use.
- **Docs:** [Inference Providers](https://huggingface.co/docs/inference-providers/index), [pricing](https://huggingface.co/docs/inference-providers/pricing), [security](https://huggingface.co/docs/inference-providers/main/security), [supported models](https://huggingface.co/inference/models), [DeepInfra privacy](https://deepinfra.com/privacy), and [DeepInfra terms](https://deepinfra.com/terms).

The synthetic compatibility gate is complete. Before the first real CV is sent, the owner must still review the then-current policies and confirm billing/quota in the Hugging Face account.

### Remotive

- **Endpoint:** `GET https://remotive.com/api/remote-jobs`.
- **Parameters:** `category`, `search`, and `limit` only.
- **Response used:** ID, URL, title, company, category, job type, publication date, required candidate location, salary, and description.
- **Authentication/cost:** none documented for the public API.
- **Limits:** advised maximum four fetches per day; more than two requests per minute may be blocked. The in-memory six-hour cache enforces the POC's intended usage.
- **Terms:** every displayed job identifies Remotive as the source and links to the Remotive URL; the app does not collect signups to reveal listings or redistribute them to third-party job boards.
- **Docs:** [Remotive Remote Jobs Public API](https://github.com/remotive-com/remote-jobs-api).

### Greenhouse Job Board API

- **List:** `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`.
- **Detail:** `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}?questions=true&pay_transparency=true`.
- **Response used:** job/post IDs, title, company, location, content, departments/offices, publication/update/deadline fields when present, original URL, questions, metadata, and pay ranges when exposed.
- **Authentication/cost:** public GET endpoints require no authentication and have no documented fee.
- **Limits:** no public numeric GET rate limit is documented. The app fetches each allowlisted board once per run, retrieves details only for shortlisted jobs, uses timeouts, and handles 429/5xx responses as source failures.
- **Docs:** [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html).

## Privacy and Security Controls

- Keep PDF bytes, extracted text, profiles, preferences, and results in session memory only.
- Never use `st.cache_data`, disk files, snapshots, or global caches for CV-derived data.
- Release old objects and invalidate run outputs when the CV changes; do not merge profiles.
- Show the named external route—Hugging Face and the configured provider—before sending extracted text.
- Send only normalized extracted text needed for the four approved profile categories, not the PDF file or filename.
- Redact personal content from logs, error messages, test recordings, and screenshots.
- Validate upload type, PDF structure, input length, tool arguments, model JSON, source URLs, and external response sizes.
- Restrict outbound job tools to Remotive, Greenhouse allowlist endpoints, and source-provided public links.
- Keep `HF_TOKEN` environment-only and run secret scanning before commits.

PRD ref: `prd.md > CV Upload and Extraction`, `scope.md > Privacy and Trust Boundary`.

## Testing and Acceptance Verification

### Unit Tests

- Text-based, blank, scanned, encrypted, and malformed PDF behavior using synthetic fixtures.
- Pydantic rejection of extra fields, missing fields, wrong types, invented tool names, and non-allowlisted board tokens.
- Full eligibility truth table: explicit conflict, all confirmed, unknown critical condition, `Worldwide`, paid-only missing pay, and strong skills plus geographic conflict.
- Skill thresholds and separation from eligibility.
- Profile minimum-content rule and CV-replacement invalidation.
- Stable ranking and snapshot-date labeling.
- Log-redaction tests using synthetic PII canaries.

### Contract Tests

- Recorded, sanitized Remotive and Greenhouse fixtures validate adapter assumptions without live requests in the normal suite.
- Optional live contract tests confirm the four Greenhouse tokens and Remotive schema without asserting that any specific job remains available.
- A provider smoke test sends synthetic, non-personal text and must prove both: a valid tool call with schema-valid arguments and a valid structured JSON response accepted by Pydantic. The initial test passed on 2026-10-25 and remains a required regression check whenever the model, provider, SDK version, or response settings change.

### Integration Tests

- Mocked model and HTTP services exercise the complete live workflow, source partial failure, both-source failure, cancellation, retry, late-result discard, and one-worker rule.
- Snapshot mode runs the same downstream analysis while making zero source-network calls.
- Invalid or unsupported model output ends in an honest error and never produces confirmed assessments.

### UI and Manual Acceptance

- Streamlit AppTest checks guarded navigation, required preferences, provider disclosure, real stage states, filters, visible text labels, and CV replacement.
- A manual 60-second rehearsal uses the dated real-data snapshot to show both approved source types, `Strong` plus `Not Eligible`, an `Unknown` result, evidence, attribution, freshness, and original links.
- A separate live rehearsal confirms real source calls and clearly records which sources completed or failed.

The build is not accepted if the verified provider contract regresses, if a CV-derived value appears in logs or committed files, or if the eligibility engine can be overridden by model output.

## Important Failure Modes

- **Hugging Face/provider is unavailable, rate-limited, or returns malformed output** → stop the affected analysis, show a truthful retryable error, and never display partial model output as confirmed.
- **One or both job sources fail** → show partial results with the named failed source when one succeeds; show an error and Retry when both fail. Never switch silently to a snapshot.
- **Cancellation arrives during an external call** → allow the timed request to end, discard output using `run_id`/`profile_version`, and show the run as cancelled.
- **A posting disappears or its link fails** → label it `Stale` or `Unavailable`; do not present it as verified active, but retain already collected evidence in a dated snapshot when applicable.
- **A new CV replaces the active one** → cancel the old run and clear all profile-dependent state before displaying the new extraction.

## What Was Simplified and Why

- **One local Streamlit process** instead of separate frontend, API server, queue, and database—enough for one user and easier to inspect during a hackathon.
- **A custom bounded state machine** instead of a general agent framework—keeps tool behavior visible and limits dependencies and uncontrolled loops.
- **One model/provider pair at a time** instead of automatic provider failover—preserves predictable privacy disclosure, cost, and tested behavior. Configuration remains replaceable.
- **Local PDF text extraction plus hosted structured extraction** instead of OCR or document services—keeps the uploaded file local and honors the text-based-PDF boundary.
- **Deterministic labels from validated evidence** instead of model-generated scores—makes decisions reproducible and explainable.
- **An in-memory Remotive cache** instead of persistent job storage—respects source request guidance without creating a database or confusing live data with snapshots.
- **Cooperative cancellation** instead of distributed task termination—proportionate for a single local process; timeouts and stale-result rejection protect correctness.

## Decisions and Open Issues

### Recorded Decisions

- The learner selected Hugging Face Inference Providers, `huggingface_hub.InferenceClient`, and environment-only `HF_TOKEN` as the hosted-inference architecture.
- `HF_MODEL` and `HF_PROVIDER` remain configurable. `Qwen/Qwen3.5-9B` with `deepinfra` is the verified default; any replacement must pass both tool-call and structured-output smoke tests before use.
- PyMuPDF extracts text locally; only extracted text is sent externally after disclosure.
- Pydantic validation is mandatory for model output and tool arguments; invalid output is rejected.
- The bounded agent owns planning and real tool calls, while deterministic code owns restrictions, eligibility, skills labels, ranking, bounds, and retries.
- Session memory is the only store for personal data. Snapshots contain public job data only.
- All four proposed Greenhouse boards remain in the initial allowlist because their public endpoints, tokens, and current job availability were verified on 2026-10-25.

### Compatibility Uncertainty Resolved

The genuine uncertainty was whether the low-cost `Qwen/Qwen3.5-9B` and `deepinfra` pair would support both required interfaces through `huggingface_hub.InferenceClient`, rather than merely appearing compatible in a provider table. This was resolved on 2026-10-25 with authenticated calls containing synthetic data only:

1. **Tool calling passed:** the model returned exactly one requested `search_jobs` call, and its function name and arguments passed strict Pydantic validation.
2. **Structured JSON passed:** the model returned JSON matching a strict profile schema, and Pydantic validated the stated skills, empty experience list, and stated project.
3. **Compatibility detail:** the first structured attempt used a 256-token allowance and produced no final content. Repeating it with `reasoning_effort="none"` and a 1,024-token allowance returned valid JSON. These settings are therefore part of the verified provider contract.
4. **Security:** `.env` was loaded with `python-dotenv`; the token was used only for authentication and was never printed, committed, or included in output.

There are no unresolved model/provider compatibility decisions for this draft. A future model or provider change requires the same privacy review and synthetic smoke tests and must document the reason for the change.
