"""Public Greenhouse board list/details. Board tokens are immutable allowlist."""
import httpx
from job_hunter.config import GREENHOUSE_BOARDS
from job_hunter.models import JobPosting
from job_hunter.sources.base import clean_html, now_utc
from job_hunter.sources.remotive import SourceError

HOST = "https://boards-api.greenhouse.io"

def list_greenhouse_jobs(board_token: str, client=None) -> list[JobPosting]:
    if board_token not in GREENHOUSE_BOARDS:
        raise SourceError("Unknown board")
    url = f"{HOST}/v1/boards/{board_token}/jobs"
    try:
        c = client or httpx.Client(timeout=httpx.Timeout(12.0), follow_redirects=False)
        try:
            r = c.get(url, params={"content":"true"}); r.raise_for_status()
            payload = r.json()
            if not isinstance(payload.get("jobs"),list): raise ValueError("Invalid response")
        finally:
            if client is None: c.close()
    except Exception:
        raise SourceError(f"Greenhouse board {board_token} is unavailable.") from None
    retrieval = now_utc()
    output = []
    for j in payload["jobs"]:
        title = str(j.get("title") or "")
        loc = str((j.get("location") or {}).get("name") or "")
        output.append(JobPosting(
            source="Greenhouse", source_id=str(j.get("id")), title=title,
            company=GREENHOUSE_BOARDS[board_token], description=clean_html(j.get("content") or ""),
            url=str(j.get("absolute_url") or ""), location=loc,
            posted_at=str(j.get("first_published") or j.get("updated_at") or ""),
            retrieved_at=retrieval, board=board_token,
            source_fields={"location.name":loc, "updated_at":str(j.get("updated_at") or "")}
        ))
    return output

def get_greenhouse_job(board_token: str, job_id: int, client=None) -> dict:
    if board_token not in GREENHOUSE_BOARDS or job_id <= 0:
        raise SourceError("Unauthorized board or job")
    try:
        c = client or httpx.Client(timeout=httpx.Timeout(12.0), follow_redirects=False)
        try:
            r=c.get(f"{HOST}/v1/boards/{board_token}/jobs/{job_id}",params={"questions":"true","pay_transparency":"true"})
            r.raise_for_status(); payload=r.json()
        finally:
            if client is None: c.close()
    except Exception:
        raise SourceError("Greenhouse job detail was unavailable.") from None
    questions=[]
    for q in payload.get("questions") or []:
        label=clean_html(str(q.get("label") or ""))
        if label: questions.append(label)
    for q in payload.get("location_questions") or []:
        label=clean_html(str(q.get("label") or ""))
        if label: questions.append(label)
    pay=payload.get("pay_input_ranges") or []
    return {"questions":questions[:20],"pay":str(pay)[:700] if pay else "",
            "description":clean_html(payload.get("content") or "")}
