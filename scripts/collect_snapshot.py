"""Capture REAL public jobs at the moment of execution; never fabricate job fixtures.

Run on your Internet-connected laptop:
    uv run python scripts/collect_snapshot.py

Uses approved public sources only; does not read your .env or process CVs.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

# Allow direct execution: uv run python scripts/collect_snapshot.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from job_hunter.sources.remotive import search_remotive, SourceError
from job_hunter.sources.greenhouse import list_greenhouse_jobs
from job_hunter.config import GREENHOUSE_BOARDS
from job_hunter.sources.base import now_utc

DEST=Path(__file__).resolve().parents[1]/"data"/"snapshots"/"demo.json"

def main():
    jobs=[]
    try:
        rem,_=search_remotive(query="software",limit=12)
        jobs.extend(rem)
    except SourceError:
        print("Remotive unavailable; continuing with Greenhouse.")
    for token in GREENHOUSE_BOARDS:
        try:
            group=list_greenhouse_jobs(token)
            relevant=[j for j in group if any(k in j.title.casefold() for k in
                      ["intern","engineer","developer","graduate","data","python","ai ","research"])]
            jobs.extend(relevant[:10])
            print(f"{token}: collected {len(relevant[:10])} actual published postings")
        except SourceError:
            print(f"{token}: unavailable")
    if not jobs:
        raise SystemExit("No real source data available. No snapshot file was created.")
    # A snapshot is historical data. Each job stays attributed to its public source.
    manifest={"schema_version":1,"collected_at":now_utc(),
              "provenance":"Remotive and public Greenhouse GET APIs at collection time",
              "jobs":[j.model_dump() for j in jobs]}
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Saved {len(jobs)} real postings to {DEST}")
    print("Snapshot is historical; it must NEVER be presented as a live search.")

if __name__=="__main__":main()
