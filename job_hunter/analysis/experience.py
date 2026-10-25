"""Conservative years-of-experience evidence from user-reviewed CV entries.

We report only a documented lower bound; missing CV experience is NOT proof of
ineligibility, and overlapping entries are not summed.
"""
from __future__ import annotations

import re
from job_hunter.models import CandidateProfile

# Numeric, explicit statements made in a reviewed experience record.
_DURATION = re.compile(r"\b(\d{1,2}(?:\.\d+)?)\s*(?:\+\s*)?(years?|yrs?|months?|mos?)\b", re.I)
_YEAR_RANGE = re.compile(r"\b((?:19|20)\d{2})\s*(?:[-–—]|to)\s*((?:19|20)\d{2})\b", re.I)


def documented_experience_years(profile: CandidateProfile) -> float | None:
    """At least this many years are explicitly supported by one reviewed role.

    We deliberately do not sum durations: internships, overlapping periods and
    duplicated CV experience could otherwise inflate the estimate.
    """
    supported: list[float] = []
    for experience in profile.experience:
        duration = (experience.duration or "").strip()
        for match in _DURATION.finditer(duration):
            number = float(match.group(1))
            if number <= 40:
                supported.append(number / 12 if match.group(2).lower().startswith(("mo",)) else number)
        for match in _YEAR_RANGE.finditer(duration):
            start, end = map(int, match.groups())
            if 1950 <= start < end <= 2100 and end - start <= 40:
                # Year-only ranges are ambiguous by almost a year. Be conservative.
                supported.append(float(max(0, end - start - 1)))
    return max(supported) if supported else None
