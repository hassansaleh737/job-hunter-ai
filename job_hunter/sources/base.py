"""Safe source normalization helpers."""
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import html

def clean_html(value: str) -> str:
    soup = BeautifulSoup(html.unescape(value or ""), "html.parser")
    for item in soup(["script", "style", "iframe", "form"]):
        item.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())[:16000]

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
