from job_hunter.models import CandidateProfile,Preferences,JobPosting,JobRequirementExtraction
from job_hunter.analysis.eligibility import evaluate_eligibility
from job_hunter.analysis.skills import assess_skills
from job_hunter.analysis.ranking import rank
from job_hunter.cv.pdf import extract_pdf_text,CVError
import fitz,pytest

def job(location="Remote - US", salary="", title="Software Intern"):
    return JobPosting(source="Greenhouse",source_id="1",title=title,company="Example",
        description="Remote software role. Python and FastAPI.",url="https://job-boards.greenhouse.io/example/jobs/1",location=location,salary=salary,link_status="active")
def req():
    return JobRequirementExtraction(required_skills=["Python","FastAPI"],preferred_skills=[],mandatory_skills=[],
     experience_requirement="",geography="",work_authorization="",remote_policy="remote",
     employment_type="internship",pay_evidence="",evidence_quotes=["Python"])
def pref():return Preferences(roles=["Python Developer"],level="Both",country="Egypt")
def profile():return CandidateProfile(skills=["Python","FastAPI"],education=[],experience=[],projects=[],confirmed=True)

def test_strong_skill_match_cannot_override_location_conflict():
    sk=assess_skills(profile(),req())
    eligibility,conditions=evaluate_eligibility(job(),req(),pref())
    assert sk.label=="Strong"
    assert eligibility=="Not Eligible"
    assert any(x.name=="Geography" and x.state=="conflict" for x in conditions)

def test_worldwide_does_not_mean_legal_eligible():
    eligible,conditions=evaluate_eligibility(job(location="Worldwide"),req(),pref())
    assert eligible=="Unknown"
    assert next(x.state for x in conditions if x.name=="Geography")=="confirmed"
    assert next(x.state for x in conditions if x.name=="Work authorization")=="unknown"

def test_unknown_not_conflict():
    eligible,_=evaluate_eligibility(job(location="Remote"),req(),pref())
    assert eligible=="Unknown"

def test_unpaid_is_conflict_when_paid_only():
    p=pref().model_copy(update={"paid_only":True})
    eligible,conditions=evaluate_eligibility(job(location="Worldwide",salary="Unpaid"),req(),p)
    assert eligible=="Not Eligible"
    assert next(x.state for x in conditions if x.name=="Paid only")=="conflict"

def test_profile_minimum():
    assert profile().usable()
    assert not CandidateProfile(skills=[],education=[],experience=[],projects=[]).usable()

def test_pdf_text_and_scanned():
    doc=fitz.open();page=doc.new_page()
    page.insert_text((70,70),"Python developer. Studied Computer Science. Example API project in FastAPI and SQL.")
    assert "Python" in extract_pdf_text(doc.tobytes())
    blank=fitz.open();blank.new_page()
    with pytest.raises(CVError):extract_pdf_text(blank.tobytes())


def test_title_specific_tech_is_visible_without_claiming_it_was_mandatory():
    r = JobRequirementExtraction(required_skills=["Java", "Python", "C++", "C#", "JavaScript"],
        preferred_skills=[], mandatory_skills=[], experience_requirement="",
        geography="", work_authorization="", remote_policy="", employment_type="",
        pay_evidence="", evidence_quotes=[])
    p = CandidateProfile(skills=["Java", "Python", "C++"],
        education=[], experience=[], projects=[], confirmed=True)
    result = assess_skills(p, r, "Software Engineer (Intern, C#)")
    assert result.label == "Partial"
    assert result.core_missing == ["C#"]
    assert "Important technology in job title not confirmed: C#" in result.explanation
    assert "C#" in result.missing


def test_title_tech_prevents_strong_even_with_high_overlap():
    r = JobRequirementExtraction(required_skills=["Java", "Python", "C++", "JavaScript"],
        preferred_skills=[], mandatory_skills=[], experience_requirement="",
        geography="", work_authorization="", remote_policy="", employment_type="",
        pay_evidence="", evidence_quotes=[])
    p = CandidateProfile(skills=["Java", "Python", "C++", "JavaScript"],
        education=[], experience=[], projects=[], confirmed=True)
    result = assess_skills(p, r, "Software Engineer (Intern, C#)")
    assert result.label == "Partial"
    assert result.core_missing == ["C#"]


def test_java_not_mistaken_for_javascript_title_requirement():
    r = JobRequirementExtraction(required_skills=["Java"], preferred_skills=[],
        mandatory_skills=[], experience_requirement="", geography="", work_authorization="",
        remote_policy="", employment_type="", pay_evidence="", evidence_quotes=[])
    p = CandidateProfile(skills=["Java"], education=[], experience=[], projects=[], confirmed=True)
    result = assess_skills(p, r, "Junior JavaScript Engineer")
    assert result.label == "Partial"
    assert result.core_missing == ["JavaScript"]
    assert "Java" in result.matched
