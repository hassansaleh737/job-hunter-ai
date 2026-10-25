# Job Hunter AI — Evidence-Based Job Matching

Job Hunter AI is a privacy-conscious Streamlit proof of concept for Computer Science and Software Engineering students and recent graduates in Egypt who are looking for remote early-career technology roles.

The application follows a five-step workflow:

**Upload CV → Review Profile → Preferences → Find Jobs → Results**

Its core idea is simple: a strong skills match does not automatically mean a candidate is eligible. Job Hunter AI keeps skills matching and job eligibility separate, cites the available evidence, and leaves missing or ambiguous requirements as `Unknown` instead of guessing.

## What the Proof of Concept Does

- Extracts text locally from a text-based PDF CV with PyMuPDF.
- Sends extracted text to the disclosed Hugging Face inference provider only after user consent.
- Validates structured skills, education, experience, and project data with Pydantic.
- Lets the user review and correct the extracted profile before any job search.
- Uses real tools to search the Remotive API and a fixed allowlist of public Greenhouse job boards.
- Extracts stated job requirements with `Qwen/Qwen3.5-9B` through Hugging Face Inference Providers and DeepInfra.
- Applies deterministic Python rules for skills matching and conservative eligibility classification.
- Shows evidence, explicit restrictions, unknown requirements, source attribution, freshness information, and original job links.
- Supports clearly separated Live Search and Dated Snapshot modes.

The MVP does not provide accounts, persistent profiles, OCR, cover-letter generation, saved jobs, or automatic applications.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A Hugging Face token with inference access
- Network access for hosted inference and live job-source requests

## Setup

1. Clone the repository and enter the project directory.
2. Copy `.env.example` to `.env`.
3. Set the following values in `.env`:

```env
HF_TOKEN=your_private_hugging_face_token
HF_MODEL=Qwen/Qwen3.5-9B
HF_PROVIDER=deepinfra
```

Never commit `.env` or paste a real token into source code, logs, screenshots, or issue reports.

4. Install the locked dependencies:

```powershell
uv sync
```

5. Run the application:

```powershell
uv run streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

## Tests

Run the complete automated suite:

```powershell
uv run pytest
```

Run the authenticated provider compatibility check with synthetic data only:

```powershell
uv run python scripts/provider_smoke_test.py
```

The provider smoke test consumes hosted inference and should not be used with a real CV for debugging.

## Demo Snapshot

Live Search is the default. For a repeatable local recording, collect a dated snapshot of real public job postings:

```powershell
uv run python scripts/collect_snapshot.py
uv run python scripts/prepare_demo.py
uv run streamlit run streamlit_app.py
```

Snapshot results are labeled with their collection date and as not live or reverified. Locally generated `demo.json` and `demo_requirements.json` files are intentionally excluded from Git to avoid republishing collected job text or accidentally mixing local demo data with source code.

## Architecture

- `streamlit_app.py` and `app_pages/`: the five-step Streamlit interface.
- `job_hunter/cv/`: local PDF text extraction.
- `job_hunter/inference/`: configurable Hugging Face inference and validated structured outputs.
- `job_hunter/sources/`: Remotive and Greenhouse source adapters and link checks.
- `job_hunter/agent/`: bounded tool orchestration, progress, cancellation, and retry behavior.
- `job_hunter/analysis/`: deterministic skills, experience, eligibility, and ranking rules.
- `job_hunter/snapshots/`: dated public-job snapshot validation and loading.
- `tests/`: unit and mocked source-contract regression tests.

The implementation deliberately separates probabilistic extraction from deterministic decisions. The model structures evidence from unstructured text; explicit restrictions and final eligibility labels remain controlled by testable rules.

## Privacy and Security

- CV PDF bytes and reviewed profile data remain in the active Streamlit session and are not intentionally persisted.
- A replacement CV invalidates the previous profile, results, rankings, and analysis.
- Extracted CV text is transmitted externally only after a visible disclosure and user consent.
- CV content, personal information, and tokens must not be written to application logs or analytics.
- `.gitignore` excludes `.env`, common private document formats, and local snapshot data.
- External provider privacy, retention, pricing, and rate-limit policies remain separate from the application's session-only storage guarantees and should be reviewed before using a personal CV.
- Job postings and original links are external, untrusted data; users should verify them with the employer before applying.

## Job Sources and Attribution

- [Remotive Public API](https://github.com/remotive-com/remote-jobs-api)
- [Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html)

Job Hunter AI preserves source attribution and links users to the original posting. Source availability, posting status, and employer requirements can change after retrieval.

## Known Limitations

- Only text-based PDF CVs are supported; scanned PDFs and OCR are outside the MVP.
- Live inference latency and cost depend on the configured Hugging Face provider and account.
- Cancellation discards late results but cannot interrupt an already executing provider or HTTP call.
- Location and work-authorization evidence is often incomplete, so many jobs correctly remain `Unknown`.
- The application cannot verify the truth of CV claims or make the employer's final eligibility decision.
- Locally generated snapshots are not included in the public repository and must never be presented as live results.
- Automated browser coverage is limited; the full five-step journey should be checked manually before recording.

## Planning and Build Artifacts

The public repository includes the Skill Pack planning and build artifacts under `devpost/`:

- `scope.md`
- `prd.md`
- `spec.md`
- `checklist.md`
- `app-map.html`

`devpost/learner-profile.md` is personal learning context and is intentionally ignored rather than published.

## License

This project is released under the [MIT License](LICENSE).
