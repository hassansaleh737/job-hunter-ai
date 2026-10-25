"""Fast demo reuses only date-bound, content-bound PUBLIC job requirements."""
import json
from job_hunter.models import CandidateProfile, Preferences, JobPosting, JobRequirementExtraction
from job_hunter.snapshots.loader import job_fingerprint, load_prepared_requirements
from job_hunter.agent.orchestrator import run_pipeline, shortlist, _ground_requirements


def job(source="Greenhouse", source_id="42"):
    return JobPosting(source=source, source_id=source_id, title="Python Engineer Intern", company="Example Company",
        description="Python is required. Remote - US.",location="Remote - US",
        url="https://job-boards.greenhouse.io/test/jobs/42")


def requirement():
    return JobRequirementExtraction(required_skills=["Python"],preferred_skills=[],mandatory_skills=[],
        experience_requirement="",geography="Remote - US",work_authorization="",remote_policy="Remote",
        employment_type="",pay_evidence="",evidence_quotes=["Python"])


class NeverCallGateway:
    def requirements(self, *a):
        raise AssertionError("The model must not be called for prepared public postings")


def test_prepared_snapshot_skips_llm_and_still_matches_cv(monkeypatch):
    import job_hunter.agent.orchestrator as orch
    sample = job()
    monkeypatch.setattr(orch,"load_snapshot",lambda:("2026-10-25T11:00Z",[sample]))
    monkeypatch.setattr(orch,"load_prepared_requirements",lambda date: {job_fingerprint(sample): requirement()})
    events=[]
    res,outcomes,date=run_pipeline(CandidateProfile(skills=["Python"],education=[],experience=[],projects=[],confirmed=True),
        Preferences(roles=["Python Engineer"],level="Both",country="Egypt"),
        "snapshot",lambda type,data:events.append((type,data)),lambda:False,gateway=NeverCallGateway())
    assert len(res)==1 and res[0].skills.label=="Strong"
    assert res[0].eligibility=="Not Eligible"
    assert outcomes["Greenhouse"]=="Snapshot"
    assert any(t=="stage" and v["status"]=="Skipped" for t,v in events)
    assert any(t=="info" and "Reused prepared" in v["message"] for t,v in events)


def test_prepared_entries_are_bound_to_specific_date_and_job_text(tmp_path):
    j=job()
    path=tmp_path/"prepared.json"
    path.write_text(json.dumps({"schema_version":1,"collected_at":"2026-10-25",
                                "requirements":{job_fingerprint(j):requirement().model_dump()}}))
    assert len(load_prepared_requirements("2026-10-25",path))==1
    assert load_prepared_requirements("2026-10-26",path)=={}
    j.description="Altered posting"
    assert job_fingerprint(j) not in load_prepared_requirements("2026-10-25",path)


def test_skills_are_recomputed_for_different_profiles(monkeypatch):
    import job_hunter.agent.orchestrator as orch
    sample=job()
    monkeypatch.setattr(orch,"load_snapshot",lambda:("2026-10-25T11:00Z",[sample]))
    monkeypatch.setattr(orch,"load_prepared_requirements",lambda date: {job_fingerprint(sample): requirement()})
    pref=Preferences(roles=["Python Engineer"],level="Both",country="Egypt")
    def run(skills):
        results,*_=run_pipeline(CandidateProfile(skills=skills,education=[],experience=[],projects=[],confirmed=True),
            pref,"snapshot",lambda *a:None,lambda:False,gateway=NeverCallGateway())
        return results[0].skills.label
    assert run(["Python"])=="Strong"
    assert run(["Java"])=="Weak"


def test_live_shortlist_has_maximum_six_with_source_balance():
    jobs=[job("Greenhouse",str(x)) for x in range(12)]
    jobs.extend(job("Remotive",str(x)) for x in range(12))
    pref=Preferences(roles=["Python Engineer"],level="Both",country="Egypt")
    chosen=shortlist(jobs,pref)
    assert len(chosen)==6
    assert sum(j.source=="Remotive" for j in chosen)>=2
    assert sum(j.source=="Greenhouse" for j in chosen)>=4
