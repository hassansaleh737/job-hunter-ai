"""Pre-analyze real public snapshot jobs ONCE, before recording a demo.

Only employer job postings are sent to Hugging Face. No CV or user-profile data
are read, sent, cached or written by this script. The demo still computes every
candidate-specific skills and eligibility assessment at playback time.

Usage:
    uv run python scripts/collect_snapshot.py
    uv run python scripts/prepare_demo.py

To analyze only a smaller set selected for specific demo roles:
    uv run python scripts/prepare_demo.py --limit 6 --roles "AI Engineer" "Python Developer"
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Allow direct execution: uv run python scripts/prepare_demo.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# A previously exported shell HF_TOKEN must not silently override the owner's
# explicitly configured project .env file. Never print or log the token.
load_dotenv(dotenv_path=".env", override=True)

from job_hunter.agent.orchestrator import _ground_requirements, shortlist
from job_hunter.inference.client import HFGateway
from job_hunter.models import Preferences
from job_hunter.snapshots.loader import (
    DEFAULT_PREPARED, job_fingerprint, load_prepared_requirements, load_snapshot,
)


def prepare_snapshot(limit: int = 0, roles: list[str] | None = None) -> tuple[int, int]:
    collected, jobs = load_snapshot()
    if limit:
        demo_roles = roles or ["AI Engineer", "Python Developer", "Software Engineer"]
        pref = Preferences(roles=demo_roles, level="Both", country="Egypt")
        selected = shortlist(jobs, pref)[:limit]
        print("Preparing the shortlisted roles:", ", ".join(demo_roles))
    else:
        selected = jobs

    # Resume from a successful previous preparation for this SAME snapshot.
    prepared = load_prepared_requirements(collected)
    gateway = HFGateway()
    completed = 0
    print(f"Snapshot contains {len(jobs)} public job postings. Preparing {len(selected)} postings.")
    for job in selected:
        fingerprint = job_fingerprint(job)
        if fingerprint in prepared:
            completed += 1
            print(f"[{completed}/{len(selected)}] Reused: {job.source} {job.source_id}")
            continue
        try:
            req = gateway.requirements(job.title, job.description, job.location, job.questions)
            req = _ground_requirements(job, req)
        except Exception as exc:
            # Never echo provider exception strings: they may include request bodies.
            print(f"Could not analyze a public posting ({type(exc).__name__}); resumable preparation stopped.")
            break
        prepared[fingerprint] = req
        completed += 1
        # Save after each item. A rate limit or timeout won't lose prior work.
        manifest = {
            "schema_version": 1,
            "collected_at": collected,
            "provenance": "Public job requirements extracted before the demo; NOT live verification",
            "requirements": {key: value.model_dump() for key, value in prepared.items()},
        }
        DEFAULT_PREPARED.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PREPARED.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{completed}/{len(selected)}] Prepared: {job.source} {job.source_id}")

    print(f"Ready: {completed}/{len(selected)} selected public postings, without any CV data.")
    if completed != len(selected):
        print("WARNING: unprepared job postings may still require Hugging Face during snapshot playback.")
    return completed, len(selected)


def main():
    parser = argparse.ArgumentParser(description="Prepare CV-free public job evidence for a faster dated snapshot demo")
    parser.add_argument("--limit", type=int, default=0, help="Pre-analyze at most N shortlisted postings; default: all")
    parser.add_argument("--roles", nargs="*", help="Used only with --limit; must match the demo's Job Preferences")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must not be negative")
    prepare_snapshot(args.limit, args.roles)


if __name__ == "__main__":
    main()
