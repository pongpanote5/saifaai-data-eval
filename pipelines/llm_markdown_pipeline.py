from __future__ import annotations

import os
import time
from dataclasses import dataclass, asdict
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from utils.chunking import chunk_text


@dataclass
class LlmMarkdownResult:
    url: str
    mode: str
    elapsed_s: float
    markdown_text: str
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


def _normalize_lines(lines: list[str]) -> str:
    cleaned = []
    seen = set()
    for line in lines:
        normalized = " ".join(line.split())
        if not normalized:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(normalized)
    return "\n".join(cleaned)


def _html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form", "svg", "canvas"]):
        tag.decompose()

    lines: list[str] = []
    for element in soup.find_all(["h1", "h2", "h3", "p", "li", "pre", "code"]):
        if element.name == "code" and element.parent and element.parent.name == "pre":
            continue
        text = element.get_text("\n").strip()
        if not text:
            continue
        if element.name == "h1":
            lines.append(f"# {text}")
        elif element.name == "h2":
            lines.append(f"## {text}")
        elif element.name == "h3":
            lines.append(f"### {text}")
        elif element.name == "li":
            lines.append(f"- {text}")
        elif element.name == "pre":
            lines.append("```")
            lines.append(text)
            lines.append("```")
        elif element.name == "code":
            lines.append(f"`{text}`")
        else:
            lines.append(text)
    return _normalize_lines(lines)


def _llm_markdown(html: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)
    prompt = (
        "Convert the following HTML into clean, readable Markdown for retrieval usage. "
        "Remove navigation, ads, and boilerplate. Return Markdown only.\n\n"
        f"HTML:\n{html}"
    )
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()


def run_llm_markdown_pipeline(urls: Iterable[str]) -> list[dict]:
    results: list[dict] = []
    for url in urls:
        start = time.time()
        error = None
        markdown = ""
        try:
            html = _fetch_html(url)
            if os.getenv("OPENAI_API_KEY"):
                try:
                    markdown = _llm_markdown(html)
                except Exception as exc:
                    error = f"llm_failed: {exc}"
                    markdown = _html_to_markdown(html)
            else:
                markdown = _html_to_markdown(html)
            chunks = chunk_text(markdown)
            elapsed = time.time() - start
            result = LlmMarkdownResult(
                url=url,
                mode="llm_markdown",
                elapsed_s=round(elapsed, 2),
                markdown_text=markdown,
                chunk_count=len(chunks),
                error=error,
            )
        except Exception as exc:
            elapsed = time.time() - start
            result = LlmMarkdownResult(
                url=url,
                mode="llm_markdown",
                elapsed_s=round(elapsed, 2),
                markdown_text="",
                chunk_count=0,
                error=str(exc),
            )
        results.append(result.to_dict())
    return results
