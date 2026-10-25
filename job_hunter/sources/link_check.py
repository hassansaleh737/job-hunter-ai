"""Optional URL checks restricted to source-owned public HTTPS hosts."""
from urllib.parse import urlparse
import httpx

ALLOWED_HOSTS={"remotive.com","www.remotive.com","job-boards.greenhouse.io","job-boards.eu.greenhouse.io","boards.greenhouse.io","boards.eu.greenhouse.io"}

def check_link(url: str, client=None) -> str:
    p=urlparse(url)
    if p.scheme!="https" or p.hostname not in ALLOWED_HOSTS or p.port not in (None,443):
        return "unknown"
    try:
        c=client or httpx.Client(timeout=5.0,follow_redirects=False)
        try:
            r=c.head(url)
            if r.status_code in (405,403): return "unknown"
            if 200 <= r.status_code < 400: return "active"
            if r.status_code in (404,410): return "unavailable"
            return "unknown"
        finally:
            if client is None: c.close()
    except Exception:
        return "unknown"
