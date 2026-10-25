"""Acceptance regressions for matching, provenance, life cycle and source failures."""
from __future__ import annotations

import threading
from datetime import datetime, timezone
import pytest

from job_hunter.analysis.eligibility import evaluate_eligibility
from job_hunter.analysis.skills import assess_skills
from job_hunter.analysis.ranking import rank
from job_hunter.models import (
    CandidateProfile, Experience, Project, JobPosting, JobRequirementExtraction,
    JobAssessment, SkillsAssessment, Preferences,
)
from job_hunter.agent.run_controller import RunController, RunBusyError, is_running
from job_hunter.sources.remotive import SourceError


def profile(skills=None, duration="", description="", project=""):
    return CandidateProfile(
        skills=skills or [], education=[],
        experience=[Experience(title="Software Engineer", duration=duration,
                               description=description)] if duration or description else [],
        projects=[Project(name="App", description=project)] if project else [],
        confirmed=True,
    )


def req(skills=None, years=""):
    return JobRequirementExtraction(
        required_skills=skills or [], preferred_skills=[], mandatory_skills=[],
        experience_requirement=years, geography="", work_authorization="",
        remote_policy="", employment_type="", pay_evidence="", evidence_quotes=[],
    )


def job(description="", date="2026-10-25T00:00:00Z"):
    return JobPosting(source="Remotive", source_id="44", title="Python Developer",
        company="Example", description=description,
        url="https://remotive.com/remote-jobs/software-dev/test", location="Worldwide",
        posted_at=date)


def pref():
    return Preferences(roles=["Python Developer"], level="Both", country="Egypt")


def condition(conditions, name):
    return next(c for c in conditions if c.name == name)


def test_three_documented_years_can_satisfy_two_year_requirement():
    years = "At least 2 years of professional experience"
    _, checks = evaluate_eligibility(job(years), req(years=years), pref(),
                                     profile(duration="3 years"))
    assert condition(checks, "Experience level").state == "confirmed"


def test_missing_exp_evidence_is_unknown_not_a_rejection():
    years = "At least 2 years of professional experience"
    state, checks = evaluate_eligibility(job(years), req(years=years), pref(), profile())
    assert state == "Unknown"
    assert condition(checks, "Experience level").state == "unknown"


def test_earlier_year_range_is_conservative_but_not_summed():
    years = "2+ years of experience"
    p = profile(duration="2021-2025")
    p.experience.append(Experience(title="Overlapping", duration="2022-2025"))
    _, checks = evaluate_eligibility(job(years), req(years=years), pref(), p)
    assert condition(checks, "Experience level").state == "confirmed"


def test_experience_and_projects_can_supply_exact_skill_evidence():
    r = req(["Python", "FastAPI"])
    p = profile(description="Developed Python services.", project="Built APIs using FastAPI.")
    result = assess_skills(p, r)
    assert result.label == "Strong"
    assert result.matched == ["Python", "FastAPI"]


def test_java_does_not_match_only_javascript_description():
    p = profile(description="Built services using JavaScript and React.")
    result = assess_skills(p, req(["Java", "JavaScript"]))
    assert result.label == "Partial"
    assert result.matched == ["JavaScript"]


def test_rank_prefers_freshness_when_eligibility_and_match_equal():
    old = job(date="2026-01-01T09:00:00Z")
    new = job(date="2026-10-25T09:00:00Z")
    def assess(j):
        return JobAssessment(job=j, skills=SkillsAssessment(label="Strong"),
                             eligibility="Unknown", conditions=[])
    assert rank([assess(old), assess(new)])[0].job.posted_at == new.posted_at


def test_run_cancellation_cannot_overlap_same_session():
    started = threading.Event()
    finish = threading.Event()
    def blocked(p, prefs, mode, emit, cancelled):
        started.set()
        finish.wait(3)
        return [], {}, ""
    controller = RunController(profile(skills=["Python"]), pref(), "snapshot", 1,
                               pipeline=blocked, session_key="same-test-session")
    try:
        assert started.wait(2)
        controller.cancel()
        assert is_running("same-test-session")
        with pytest.raises(RunBusyError):
            RunController(profile(skills=["Python"]), pref(), "snapshot", 2,
                          pipeline=blocked, session_key="same-test-session")
    finally:
        finish.set()
        controller.future.result(timeout=3)
    assert not is_running("same-test-session")
    second = RunController(profile(skills=["Python"]), pref(), "snapshot", 2,
                           pipeline=lambda *args: ([], {}, ""),
                           session_key="same-test-session")
    second.future.result(timeout=3)


def test_cv_reset_clears_outputs_but_keeps_session_guard(monkeypatch):
    import importlib
    import sys
    import types
    if "streamlit" not in sys.modules:
        monkeypatch.setitem(sys.modules, "streamlit", types.SimpleNamespace(session_state={}))
    session = importlib.import_module("job_hunter.session")
    class State(dict):
        def __getattr__(self, key): return self[key]
        def __setattr__(self, key, value): self[key] = value
    state = State()
    monkeypatch.setattr(session.st, "session_state", state)
    session.init_session()
    existing = state.run_session_key
    state.profile = profile(skills=["Python"])
    state.cv_name = "same.pdf"
    state.cv_sha256 = "oldhash"
    state.results = ["old"]
    state.result_mode = "live"
    session.replace_cv(preserve_upload=True)
    assert state.profile is None and state.cv_sha256 == ""
    assert state.results == [] and state.result_mode == ""
    assert state.run_session_key == existing
    assert state.upload_epoch == 0
    session.replace_cv()
    assert state.upload_epoch == 1


def test_one_source_failure_keeps_partial_real_results(monkeypatch):
    import job_hunter.agent.orchestrator as orch
    j = job(description="Python developer role")
    j.link_status = "active"
    class FakeGateway:
        def plan_tool_calls(self, roles):
            return [("search_remotive", {"query": "python", "limit": 15, "category": "software-dev"})]
        def requirements(self, *args): return req(["Python"])
    monkeypatch.setattr(orch, "search_remotive", lambda **kw: ([_j for _j in [j]], "live fetch"))
    monkeypatch.setattr(orch, "list_greenhouse_jobs", lambda token: (_ for _ in ()).throw(SourceError("offline")))
    monkeypatch.setattr(orch, "check_link", lambda url: "active")
    results, outcomes, _ = orch.run_pipeline(profile(skills=["Python"]), pref(), "live",
        lambda *args: None, lambda: False, gateway=FakeGateway())
    assert len(results) == 1
    assert outcomes["Greenhouse"] == "Failed" and outcomes["Remotive"] == "Completed"


def test_both_source_failures_are_clearly_fatal(monkeypatch):
    import job_hunter.agent.orchestrator as orch
    class FakeGateway:
        def plan_tool_calls(self, roles):
            return [("search_remotive", {"query": "python", "limit": 15, "category": "software-dev"})]
    monkeypatch.setattr(orch, "search_remotive", lambda **kw: (_ for _ in ()).throw(SourceError("offline")))
    monkeypatch.setattr(orch, "list_greenhouse_jobs", lambda token: (_ for _ in ()).throw(SourceError("offline")))
    with pytest.raises(SourceError, match="Both job sources failed"):
        orch.run_pipeline(profile(skills=["Python"]), pref(), "live",
            lambda *args: None, lambda: False, gateway=FakeGateway())
