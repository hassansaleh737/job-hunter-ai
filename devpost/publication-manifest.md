# Job Hunter AI — Intended Public Repository Files

This manifest defines the files intended for the first public GitHub publication. It does not authorize a push or repository creation.

## Required Skill Pack Evidence

The official hackathon requires these generated planning documents in the public repository:

- `devpost/scope.md`
- `devpost/prd.md`
- `devpost/spec.md`

The following safe build artifacts are also included to document the completed workflow:

- `devpost/checklist.md`
- `devpost/app-map.html`
- `devpost/demo-runbook.md`
- `devpost/publication-manifest.md`
- `devpost/submission-checklist.md`

The installed Skill Pack source folders themselves are optional and are not included in the intended publication set.

## Exact Intended File Set

### Root and Configuration

- `.env.example`
- `.gitignore`
- `.streamlit/config.toml`
- `LICENSE`
- `README.md`
- `START_WINDOWS.bat`
- `pyproject.toml`
- `streamlit_app.py`
- `uv.lock`

### Streamlit Pages

- `app_pages/__init__.py`
- `app_pages/find_jobs.py`
- `app_pages/preferences.py`
- `app_pages/results.py`
- `app_pages/review_profile.py`
- `app_pages/upload_cv.py`

### Snapshot Documentation

- `data/snapshots/README.md`

### Devpost Artifacts

- `devpost/app-map.html`
- `devpost/checklist.md`
- `devpost/demo-runbook.md`
- `devpost/prd.md`
- `devpost/publication-manifest.md`
- `devpost/scope.md`
- `devpost/spec.md`
- `devpost/submission-checklist.md`

### Application Package

- `job_hunter/__init__.py`
- `job_hunter/config.py`
- `job_hunter/models.py`
- `job_hunter/session.py`
- `job_hunter/agent/__init__.py`
- `job_hunter/agent/orchestrator.py`
- `job_hunter/agent/run_controller.py`
- `job_hunter/analysis/__init__.py`
- `job_hunter/analysis/eligibility.py`
- `job_hunter/analysis/experience.py`
- `job_hunter/analysis/ranking.py`
- `job_hunter/analysis/skills.py`
- `job_hunter/cv/__init__.py`
- `job_hunter/cv/pdf.py`
- `job_hunter/inference/__init__.py`
- `job_hunter/inference/client.py`
- `job_hunter/snapshots/__init__.py`
- `job_hunter/snapshots/loader.py`
- `job_hunter/sources/__init__.py`
- `job_hunter/sources/base.py`
- `job_hunter/sources/greenhouse.py`
- `job_hunter/sources/link_check.py`
- `job_hunter/sources/remotive.py`

### Scripts

- `scripts/collect_snapshot.py`
- `scripts/prepare_demo.py`
- `scripts/provider_smoke_test.py`

### Tests

- `tests/contract/test_sources.py`
- `tests/unit/test_agent.py`
- `tests/unit/test_cv_inference.py`
- `tests/unit/test_demo_speed.py`
- `tests/unit/test_final_fixes.py`
- `tests/unit/test_lifecycle.py`
- `tests/unit/test_rules.py`
- `tests/unit/test_skills_compound.py`

## Explicitly Excluded

- `.env` and any real credential file
- `.venv/`, caches, logs, and editor configuration
- `devpost/learner-profile.md`
- Real or private CV files
- `data/snapshots/demo.json`
- `data/snapshots/demo_requirements.json`
- `.agents/`
- `.claude/`
- `agent/`
- `skills-lock.json`
- `DEMO_SPEED_INSTRUCTIONS.txt`
- `FINAL_FIX_PATCH_INSTRUCTIONS.txt`
- `PATCH_INSTRUCTIONS.txt`

Before publication, compare this manifest with `git ls-files`, inspect the complete Git history, and verify the staged diff. Public repository creation and pushing require explicit learner approval.
