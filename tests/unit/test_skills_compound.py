from job_hunter.analysis.skills import assess_skills
from job_hunter.models import CandidateProfile, JobRequirementExtraction


def req(items, mandatory=None):
    return JobRequirementExtraction(required_skills=items, preferred_skills=[],
        mandatory_skills=mandatory or [], experience_requirement="", geography="",
        work_authorization="", remote_policy="", employment_type="",
        pay_evidence="", evidence_quotes=[])


def profile(skills):
    return CandidateProfile(skills=skills, education=[], experience=[], projects=[])


def test_any_one_of_languages_satisfies_or():
    r = req(["Strong in at least one of Python, TypeScript, Go, Rust, Java or C++"])
    result = assess_skills(profile(["Python"]), r)
    assert result.label == "Strong"
    assert len(result.matched) == 1


def test_and_technology_group_needs_every_tech():
    result = assess_skills(profile(["Docker", "Git"]),
        req(["Solid with Docker, Linux, Git and automated testing"]))
    assert "Linux" in result.missing
    assert result.label != "Strong"


def test_experience_sentence_not_skill():
    result = assess_skills(profile(["Python"]),
        req(["2+ years of professional software engineering", "Python"]))
    assert result.label == "Strong"
    assert result.matched == ["Python"]
