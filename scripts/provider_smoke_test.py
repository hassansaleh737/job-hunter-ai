"""HF tests using only synthetic text, no real CV or user-identifiable data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from job_hunter.inference.client import HFGateway

def main():
    model=HFGateway()
    cv="""Synthetic CV with fictional facts only.
    Skills
    Python, FastAPI, SQL
    Education
    University: Example University
    Degree: Bachelor of Science
    Field: Computer Science
    Graduation Year: 2025
    Experience
    Job Title: Software Engineering Intern
    Company: Example Labs
    Duration: June 2025 - August 2025
    Description: Built a Python API.
    Relevant Projects
    Project Name: Demo API Project
    Description: Built a FastAPI application for a toy database.
    Technologies: Python, FastAPI"""
    extracted=model.extract_profile(cv)
    assert "Python" in extracted.skills
    assert extracted.education
    assert extracted.experience
    assert extracted.projects
    calls=model.plan_tool_calls(["Python Developer"])
    assert calls
    print("Structured extraction and tool-call tests passed with fictional data.")
    print("Model/provider:",model.cfg.model,"/",model.cfg.provider)

if __name__=="__main__":main()
