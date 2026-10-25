"""Eligibility first, skills second, recent publication dates third."""
from datetime import datetime, timezone
from job_hunter.models import JobAssessment


def _published_time(value: str) -> float:
    if not value:
        return 0
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    except (ValueError, OverflowError):
        return 0


def rank(items: list[JobAssessment]) -> list[JobAssessment]:
    order = {"Eligible": 0, "Unknown": 1, "Not Eligible": 2}
    match = {"Strong": 0, "Partial": 1, "Weak": 2}
    return sorted(items, key=lambda item: (
        order[item.eligibility], match[item.skills.label],
        -_published_time(item.job.posted_at), item.job.title.casefold(),
    ))
