"""Strict domain contracts for personal session data and public job evidence."""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Education(StrictModel):
    university: str = ""
    degree: str = ""
    field: str = ""
    graduation_year: str = ""
    provenance: Literal["cv", "user"] = "cv"

class Experience(StrictModel):
    title: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""
    provenance: Literal["cv", "user"] = "cv"

class Project(StrictModel):
    name: str = ""
    description: str = ""
    technologies: str = ""
    provenance: Literal["cv", "user"] = "cv"

class ProfileExtraction(StrictModel):
    skills: list[str]
    education: list[Education]
    experience: list[Experience]
    projects: list[Project]

class CandidateProfile(ProfileExtraction):
    confirmed: bool = False
    profile_version: int = 0
    user_added_skills: list[str] = Field(default_factory=list)

    def usable(self) -> bool:
        return bool(any(s.strip() for s in self.skills) or
            any((x.title or x.description).strip() for x in self.experience) or
            any((x.name or x.description or x.technologies).strip() for x in self.projects))

class Preferences(StrictModel):
    roles: list[str]
    level: Literal["Student / Intern", "Entry-Level / Junior", "Both"]
    country: str = "Egypt"
    employment_types: list[str] = Field(default_factory=list)
    paid_only: bool = False

    @field_validator("roles")
    @classmethod
    def roles_required(cls, values):
        if not any(x.strip() for x in values):
            raise ValueError("At least one target role is required")
        return values

class Evidence(StrictModel):
    field: str
    excerpt: str
    source_url: str
    kind: Literal["explicit", "interpreted", "unknown"] = "explicit"

class JobPosting(StrictModel):
    source: Literal["Remotive", "Greenhouse"]
    source_id: str
    title: str
    company: str
    description: str
    url: str
    location: str = ""
    employment_type: str = ""
    salary: str = ""
    posted_at: str = ""
    retrieved_at: str = ""
    active: bool = True
    link_status: Literal["unchecked", "active", "unknown", "unavailable"] = "unchecked"
    questions: list[str] = Field(default_factory=list)
    board: str = ""
    source_fields: dict[str, str] = Field(default_factory=dict)

class JobRequirementExtraction(StrictModel):
    required_skills: list[str]
    preferred_skills: list[str]
    mandatory_skills: list[str]
    experience_requirement: str
    geography: str
    work_authorization: str
    remote_policy: str
    employment_type: str
    pay_evidence: str
    evidence_quotes: list[str]

class EligibilityCondition(StrictModel):
    name: str
    state: Literal["confirmed", "conflict", "unknown", "not_applicable"]
    explanation: str
    evidence: list[Evidence] = Field(default_factory=list)

class SkillsAssessment(StrictModel):
    label: Literal["Strong", "Partial", "Weak"]
    matched: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    core_missing: list[str] = Field(default_factory=list)
    explanation: str = ""

class JobAssessment(StrictModel):
    job: JobPosting
    skills: SkillsAssessment
    eligibility: Literal["Eligible", "Not Eligible", "Unknown"]
    conditions: list[EligibilityCondition]
    evidence: list[Evidence] = Field(default_factory=list)
    freshness: str = ""

class SearchArguments(StrictModel):
    query: str = Field(min_length=1, max_length=100)
    category: str = "software-dev"
    limit: int = Field(default=15, ge=1, le=30)

class BoardArguments(StrictModel):
    board_token: Literal["constructortech", "ritual", "solutions", "orbisoperations"]

class DetailArguments(BoardArguments):
    job_id: int = Field(ge=1)
