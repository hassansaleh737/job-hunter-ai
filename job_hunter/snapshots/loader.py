"""Public job snapshots and reusable, CV-free pre-extracted posting facts."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from job_hunter.models import JobPosting, JobRequirementExtraction

DEFAULT_SNAPSHOT = Path(__file__).resolve().parents[2] / "data" / "snapshots" / "demo.json"
DEFAULT_PREPARED = DEFAULT_SNAPSHOT.with_name("demo_requirements.json")

class SnapshotError(ValueError):
    pass


def load_snapshot(path: Path = DEFAULT_SNAPSHOT) -> tuple[str, list[JobPosting]]:
    if not path.exists():
        raise SnapshotError("No dated real-data snapshot exists yet. Run: uv run python scripts/collect_snapshot.py")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        date = payload["collected_at"]
        if not isinstance(date, str) or not date or payload.get("schema_version") != 1:
            raise ValueError("Invalid snapshot manifest")
        jobs = [JobPosting.model_validate(j) for j in payload["jobs"]]
        if not jobs:
            raise ValueError("Empty snapshot")
        return date, jobs
    except Exception:
        raise SnapshotError("The dated snapshot is invalid and cannot be loaded.") from None


def job_fingerprint(job: JobPosting) -> str:
    """Identifies public posting text only; never includes any CV/profile data."""
    public_parts = {
        "source": job.source,
        "source_id": job.source_id,
        "board": job.board,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "questions": job.questions,
    }
    data = json.dumps(public_parts, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def load_prepared_requirements(
    collected_at: str, path: Path = DEFAULT_PREPARED,
) -> dict[str, JobRequirementExtraction]:
    """Reject prepared evidence if it belongs to a different dated snapshot.

    Missing prepared evidence is fine: the agent can still use live inference.
    Invalid prepared evidence is ignored, never silently taken as verified.
    """
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1 or data.get("collected_at") != collected_at:
            return {}
        return {
            fingerprint: JobRequirementExtraction.model_validate(record)
            for fingerprint, record in data["requirements"].items()
        }
    except (ValueError, KeyError, TypeError, OSError):
        return {}
