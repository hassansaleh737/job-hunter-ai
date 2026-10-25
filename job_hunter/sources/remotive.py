"""Remotive public API, one app-wide in-memory cache, no personal content."""
import threading
import time
import httpx
from job_hunter.models import JobPosting
from job_hunter.sources.base import clean_html, now_utc

_URL = "https://remotive.com/api/remote-jobs"
_cache: dict[str, object] = {"at":0.0, "payload":None, "retrieved_at":""}
_lock = threading.Lock()

class SourceError(RuntimeError):
    pass

def search_remotive(query: str, category: str = "software-dev", limit: int = 15, client=None) -> tuple[list[JobPosting], str]:
    # One full-feed request per six hours; query filtering is done locally to avoid
    # Remotive's recommended max of four network fetches per day.
    with _lock:
        if _cache["payload"] is not None and time.monotonic() - _cache["at"] < 6 * 3600:
            payload = _cache["payload"]
            retrieval = _cache["retrieved_at"]
            origin = "cached feed"
        else:
            try:
                c = client or httpx.Client(timeout=httpx.Timeout(14.0), follow_redirects=False)
                try:
                    response = c.get(_URL, params={"limit":100})
                    response.raise_for_status()
                    payload = response.json()
                    if not isinstance(payload.get("jobs"), list):
                        raise ValueError("Invalid jobs data")
                finally:
                    if client is None: c.close()
            except Exception:
                raise SourceError("Remotive is unavailable.") from None
            _cache.update({"payload": payload, "at":time.monotonic(), "retrieved_at":now_utc()})
            retrieval = _cache["retrieved_at"]
            origin = "live fetch"
    terms = [x for x in query.casefold().replace("/"," ").split() if len(x)>2]
    ranked = []
    for j in payload.get("jobs", []):
        title = str(j.get("title", ""))
        body = clean_html(j.get("description") or "")
        blob = f"{title} {j.get('category','')} {body[:1200]}".casefold()
        overlap = sum(t in blob for t in terms)
        if terms and overlap == 0: continue
        ranked.append((overlap, JobPosting(
            source="Remotive", source_id=str(j.get("id", "")), title=title,
            company=str(j.get("company_name", "")), description=body,
            url=str(j.get("url", "")), location=str(j.get("candidate_required_location") or ""),
            employment_type=str(j.get("job_type") or ""), salary=str(j.get("salary") or ""),
            posted_at=str(j.get("publication_date") or ""), retrieved_at=retrieval,
            link_status="unchecked", source_fields={"candidate_required_location":str(j.get("candidate_required_location") or ""),"category":str(j.get("category") or "")}
        )))
    ranked.sort(key=lambda item:item[0],reverse=True)
    return [j for _,j in ranked[:limit]], origin
