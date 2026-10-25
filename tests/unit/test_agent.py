from job_hunter.models import CandidateProfile,Preferences,JobPosting,JobRequirementExtraction
from job_hunter.agent.orchestrator import run_pipeline
from job_hunter.agent.run_controller import RunController

def sample():
    return JobPosting(source="Greenhouse",source_id="42",title="Software Engineering Intern",company="Test",
        description="Python. Remote - US.",location="Remote - US",url="https://job-boards.greenhouse.io/test/jobs/42",link_status="active")
class FakeGateway:
    def plan_tool_calls(self, roles):return [("search_remotive",{"query":"python","category":"software-dev","limit":15})]
    def requirements(self,title,description,location,questions):
        return JobRequirementExtraction(required_skills=["Python"],preferred_skills=[],mandatory_skills=[],
            experience_requirement="",geography="Remote - US",work_authorization="",remote_policy="Remote",
            employment_type="",pay_evidence="",evidence_quotes=["Python"])

def test_snapshot_same_pipeline_no_search(monkeypatch):
    import job_hunter.agent.orchestrator as orch
    monkeypatch.setattr(orch,"load_snapshot",lambda:("2026-10-25T00:00:00+00:00",[sample()]))
    events=[]
    results,outcomes,date=run_pipeline(
       CandidateProfile(skills=["Python"],education=[],experience=[],projects=[],confirmed=True),
       Preferences(roles=["Python"],level="Both",country="Egypt"),
       "snapshot",lambda kind,value:events.append((kind,value)),lambda:False,gateway=FakeGateway())
    assert len(results)==1
    assert results[0].skills.label=="Strong"
    assert results[0].eligibility=="Not Eligible"
    assert outcomes["Greenhouse"]=="Snapshot"
    assert date.startswith("2026")
