from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Iterable

import requests
from bs4 import BeautifulSoup

from utils.chunking import chunk_text


@dataclass
class RawTextResult:
    url: str
    mode: str
    elapsed_s: float
    text: str
    chunk_count: int
    error: str | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        if self.error is None:
            data.pop("error")
        return data


def _fetch_html(url: str, timeout_s: int = 10, retries: int = 2) -> str:
    headers = {"User-Agent": "saifaai-eval/0.1"}
    last_error = None
    for _ in range(retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout_s)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def _clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form", "svg", "canvas"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = []
    seen = set()
    for line in text.splitlines():
        normalized = " ".join(line.split())
        if not normalized:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        lines.append(normalized)
    return "\n".join(lines)


def run_raw_text_pipeline(urls: Iterable[str]) -> list[dict]:
    results: list[dict] = []
    for url in urls:
        start = time.time()
        try:
            html = _fetch_html(url)
            cleaned = _clean_text(html)
            chunks = chunk_text(cleaned)
            elapsed = time.time() - start
            result = RawTextResult(
                url=url,
                mode="raw_text",
                elapsed_s=round(elapsed, 2),
                text=cleaned,
                chunk_count=len(chunks),
            )
        except Exception as exc:
            elapsed = time.time() - start
            result = RawTextResult(
                url=url,
                mode="raw_text",
                elapsed_s=round(elapsed, 2),
                text="",
                chunk_count=0,
                error=str(exc),
            )
        results.append(result.to_dict())
    return results
