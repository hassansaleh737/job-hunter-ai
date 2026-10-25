"""Deterministic, evidence-aware skill labels independent of job eligibility."""
from __future__ import annotations

import re
from job_hunter.models import CandidateProfile, JobRequirementExtraction, SkillsAssessment

ALIASES = {
    "py": "python", "js": "javascript", "nodejs": "node.js",
    "reactjs": "react", "postgres": "postgresql", "restful api": "rest api",
    "llm": "llms",
}

# Only explicit technology names visible in the posting TITLE can be considered
# title-specific. General role words ("developer", "engineer", "AI") are excluded.
TITLE_TECHNOLOGIES = (
    "C#", "C++", ".NET", "Python", "JavaScript", "TypeScript", "Java",
    "FastAPI", "React", "Kotlin", "Swift", "Rust", "Ruby", "PHP", "SQL",
)


def norm(value: str) -> str:
    key = value.strip().casefold()
    key = ALIASES.get(key, key)
    return re.sub(r"[^a-z0-9+#.]", "", key)


def _title_mentions(title: str, skill: str) -> bool:
    # Prevent `Java` matching `JavaScript`, `C++` matching plain `C`, etc.
    return re.search(r"(?<![\w#+])" + re.escape(skill) + r"(?![\w#+])", title, re.I) is not None



# A model may return entire job-requirement sentences as "skills". Only
# recognize alternatives explicitly separated by a supported OR construction.
# AND-groups retain each explicitly named technology as a separate requirement.
TECH_TERMS = (
    "JavaScript", "TypeScript", "Python", "Docker", "Linux", "Git", "C++", "C#",
    "Java", "Rust", "Go", "HTML5", "CSS3", "HTML", "CSS", "React", "Vue.js",
    "Angular", ".NET", "FastAPI", "PostgreSQL", "MySQL", "SQL", "AWS",
    "GitHub", "PyTorch", "TensorFlow", "Kubernetes", "Node.js", "MLOps",
)


def _mentioned_tech(text: str) -> list[str]:
    found = [term for term in TECH_TERMS if _title_mentions(text, term)]
    # Prefer the more specific variant over its substring component.
    return [term for term in found if not any(
        term != other and term.casefold() in other.casefold()
        and _title_mentions(other, term) for other in found
    )]


def _skill_groups(items: list[str]):
    """Return (label, acceptable alternatives), excluding non-skill sentences."""
    groups = []
    for entry in items:
        s = entry.strip()
        if not s:
            continue
        terms = _mentioned_tech(s)
        if len(terms) > 1:
            # A single explicit list with OR means ANY of the technologies.
            or_group = bool(re.search(r"\b(?:or|and/or)\b", s, re.I))
            if or_group:
                groups.append((s, terms))
            else:
                groups.extend((term, [term]) for term in terms)
        elif len(terms) == 1:
            # "2+ years Python" is not a standalone skill: require Python only.
            groups.append((terms[0], terms))
        elif len(s.split()) <= 3 and not re.search(r"\d+\s*\+?\s*years?", s, re.I):
            groups.append((s, [s]))
    seen = set()
    unique = []
    for label, alternatives in groups:
        key = tuple(sorted(norm(x) for x in alternatives))
        if key not in seen:
            seen.add(key)
            unique.append((label, alternatives))
    return unique

def assess_skills(
    profile: CandidateProfile,
    req: JobRequirementExtraction,
    job_title: str = "",
) -> SkillsAssessment:
    groups = _skill_groups(req.required_skills)
    stated = [label for label, _ in groups]
    known = {norm(s) for s in profile.skills if s.strip()}
    # Match exact skill mentions in reviewed experience and project narratives,
    # not arbitrary substring overlap ("Java" must not match "JavaScript").
    narratives = [part for entry in profile.experience
                  for part in (entry.title, entry.description) if part.strip()]
    for project in profile.projects:
        narratives.extend(x for x in (project.name, project.description, project.technologies) if x.strip())
        known.update(norm(s) for s in re.split(r"[,;/]", project.technologies) if s.strip())

    relevant = [term for _, alternatives in groups for term in alternatives]
    relevant += [term for _, alternatives in _skill_groups(req.mandatory_skills + req.preferred_skills) for term in alternatives]
    relevant += list(TITLE_TECHNOLOGIES)
    for skill in relevant:
        skill = skill.strip()
        if not skill or norm(skill) in known: continue
        if any(_title_mentions(text, skill) for text in narratives):
            known.add(norm(skill))

    matched = [label for label, alternatives in groups if any(norm(s) in known for s in alternatives)]
    missing = [label for label, alternatives in groups if not any(norm(s) in known for s in alternatives)]

    # Mandatory skills come from the posting extraction and must be grounded in
    # source text by the orchestrator before reaching this function.
    mandatory_missing = [label for label, alternatives in _skill_groups(req.mandatory_skills)
                         if not any(norm(s) in known for s in alternatives)]
    title_missing = [skill for skill in TITLE_TECHNOLOGIES
                     if _title_mentions(job_title, skill) and norm(skill) not in known]
    # Title-specific tech is an important role focus, but NOT proof the employer
    # explicitly made it a mandatory requirement.
    core_missing = list(dict.fromkeys(mandatory_missing + title_missing))
    for skill in core_missing:
        if norm(skill) not in {norm(value) for value in missing}:
            missing.append(skill)

    if stated:
        coverage = len(matched) / len(stated)
        if coverage >= 0.7 and not core_missing:
            label = "Strong"
        elif coverage < 0.3:
            label = "Weak"
        else:
            label = "Partial"
        explanation = f"{len(matched)} of {len(stated)} stated required skills supported by the reviewed profile."
    else:
        preferred_match = any(norm(skill) in known for skill in req.preferred_skills)
        label = "Partial" if preferred_match else "Weak"
        explanation = "No verifiable required-skill list; a strong match cannot be confirmed."

    if mandatory_missing:
        explanation += " Explicitly mandatory skill(s) not confirmed: " + ", ".join(mandatory_missing) + "."
    if title_missing:
        explanation += " Important technology in job title not confirmed: " + ", ".join(title_missing) + "."
    if core_missing:
        explanation += " A Strong match is not possible until these skill gaps are resolved."

    return SkillsAssessment(label=label, matched=matched, missing=missing,
                            core_missing=core_missing, explanation=explanation)
