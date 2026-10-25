"""Regression tests for the restored PyMuPDF-to-Hugging-Face CV workflow."""
from __future__ import annotations

import ast
import json
from pathlib import Path
from types import SimpleNamespace

import httpx

import job_hunter.inference.client as inference
from job_hunter.inference.client import HFGateway, InferenceFailure
from job_hunter.models import Education, Experience, ProfileExtraction, Project


class FakeCompletions:
    def __init__(self, payloads: list[str] | None = None, *, error=None):
        self.payloads = payloads or [""]
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        payload = self.payloads[min(len(self.calls) - 1, len(self.payloads) - 1)]
        message = SimpleNamespace(content=payload, tool_calls=[])
        return SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason="stop")])


def fake_client(payload: str = "", *, payloads=None, error=None):
    completions = FakeCompletions(payloads or [payload], error=error)
    return SimpleNamespace(
        chat=SimpleNamespace(completions=completions),
        completions_spy=completions,
    )


def synthetic_cv(project_count: int = 10) -> str:
    projects = []
    for index in range(1, project_count + 1):
        projects.extend([
            f"Project {index}: Application {index}",
            f"Built application {index} with a grounded project description.",
            "Technologies: Python and FastAPI",
        ])
    return (
        "Skills\nPython\nFastAPI\n" + "Complete skill context.\n" * 80
        + "Education\nExample University\nComputer Science\n2025\n"
        + "Complete education context.\n" * 50
        + "Experience\nSoftware Intern\nExample Labs\nJune 2025 - August 2025\n"
        + "Complete experience context.\n" * 70
        + "Projects\n" + "\n".join(projects)
    )


def empty_profile(**updates) -> ProfileExtraction:
    values = {"skills": [], "education": [], "experience": [], "projects": []}
    values.update(updates)
    return ProfileExtraction(**values)


def test_restored_original_settings_and_field_level_grounding():
    cv_text = (
        "Skills: Python. Education: Example University, 2025. "
        "Experience: Software Engineering Intern. Projects: Job Matcher."
    )
    response = ProfileExtraction(
        skills=["Python", "Kubernetes"],
        education=[Education(
            university="Example University",
            degree="Invented PhD",
            graduation_year="2025",
        )],
        experience=[Experience(
            title="Software Engineering Intern",
            company="Invented Company",
            description="Invented responsibility",
        )],
        projects=[Project(
            name="Job Matcher",
            description="Invented project details",
            technologies="Invented Framework",
        )],
    )
    client = fake_client(response.model_dump_json())

    extracted = HFGateway(client=client).extract_profile(cv_text)
    request = client.completions_spy.calls[0]

    assert extracted.skills == ["Python"]
    assert extracted.education[0].university == "Example University"
    assert extracted.education[0].degree == ""
    assert extracted.education[0].graduation_year == "2025"
    assert extracted.experience[0].title == "Software Engineering Intern"
    assert extracted.experience[0].company == ""
    assert extracted.projects[0].name == "Job Matcher"
    assert extracted.projects[0].description == ""
    assert request["max_tokens"] == 2048
    assert request["extra_body"] == {"reasoning_effort": "none"}
    assert "temperature" not in request
    assert request["messages"][1]["content"] == cv_text
    assert request["messages"][0]["content"].startswith(
        "Extract ONLY facts explicitly present in the supplied CV."
    )


def test_restored_behavior_sends_same_full_synthetic_cv_and_keeps_multiple_projects():
    cv_text = synthetic_cv(10)
    assert 4000 < len(cv_text) < 18000
    response = empty_profile(
        skills=["Python", "FastAPI"],
        education=[Education(university="Example University", field="Computer Science")],
        experience=[Experience(title="Software Intern", company="Example Labs")],
        projects=[Project(name=f"Project {index}: Application {index}")
                  for index in range(1, 11)],
    )
    client = fake_client(response.model_dump_json())

    extracted = HFGateway(client=client).extract_profile(cv_text)
    request = client.completions_spy.calls[0]
    original_expected_payload = cv_text[:18000]

    assert request["messages"][1]["content"] == original_expected_payload
    assert len(extracted.projects) == 10
    assert [project.name for project in extracted.projects] == [
        f"Project {index}: Application {index}" for index in range(1, 11)
    ]
    assert len(client.completions_spy.calls) == 1


def test_restored_schema_has_no_artificial_array_caps():
    schema = ProfileExtraction.model_json_schema()["properties"]

    assert all("maxItems" not in schema[field]
               for field in ("skills", "education", "experience", "projects"))


def test_restored_original_input_ceiling_is_18000_characters():
    cv_text = "Skills\nPython\n" + "X" * 19000
    client = fake_client(empty_profile(skills=["Python"]).model_dump_json())

    HFGateway(client=client).extract_profile(cv_text)

    payload = client.completions_spy.calls[0]["messages"][1]["content"]
    assert payload == cv_text[:18000]
    assert len(payload) == 18000


def test_restored_schema_validation_retries_once_then_accepts_valid_output():
    valid = empty_profile(skills=["Python"]).model_dump_json()
    client = fake_client(payloads=[json.dumps({"skills": ["Python"]}), valid])

    extracted = HFGateway(client=client).extract_profile("Skills: Python")

    assert extracted.skills == ["Python"]
    assert len(client.completions_spy.calls) == 2


def test_invalid_provider_profile_fails_after_original_two_attempts():
    client = fake_client(json.dumps({"skills": ["Python"]}))

    try:
        HFGateway(client=client).extract_profile("Skills: Python")
    except InferenceFailure as error:
        assert error.kind == "schema_validation"
        assert "validation" in str(error)
        assert len(client.completions_spy.calls) == 2
    else:
        raise AssertionError("Malformed provider output must be rejected")


def test_timeout_is_reported_without_exposing_request_content():
    client = fake_client(error=httpx.ReadTimeout("synthetic timeout"))

    try:
        HFGateway(client=client).extract_profile("Skills: Python")
    except InferenceFailure as error:
        assert error.kind == "timeout"
        assert "timed out" in str(error)
        assert "Skills: Python" not in str(error)
    else:
        raise AssertionError("Provider timeout must be classified")


def test_default_client_uses_original_provider_configuration_without_timeout_override(monkeypatch):
    captured = {}

    def build_client(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(
        inference,
        "settings",
        lambda: SimpleNamespace(
            token="synthetic-token",
            model="Qwen/Qwen3.5-9B",
            provider="deepinfra",
        ),
    )
    monkeypatch.setattr(inference, "InferenceClient", build_client)

    HFGateway()

    assert captured == {"provider": "deepinfra", "api_key": "synthetic-token"}


def test_upload_page_keeps_one_original_analyze_action_and_no_experimental_paths():
    page = Path(__file__).resolve().parents[2] / "app_pages" / "upload_cv.py"
    source = page.read_text(encoding="utf-8")
    gateway_source = (page.parents[0] / "../job_hunter/inference/client.py").resolve().read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    analyze_buttons = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "button"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "Analyze CV"
    ]

    assert len(analyze_buttons) == 1
    assert "extract_pdf_text" in source
    assert "HFGateway" in source
    assert "hybrid_profile" not in source
    assert "local_profile" not in source
    assert "DeepSeek" not in source
    assert "CV_PROVIDER_CHAR_LIMIT" not in gateway_source
    assert "_prepare_cv_payload" not in gateway_source
    assert "_CV_SECTION_WEIGHTS" not in gateway_source
