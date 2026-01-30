from __future__ import annotations

import math
import re
from collections import Counter

_STOPWORDS = {
    "the",
    "and",
    "a",
    "an",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "is",
    "it",
    "this",
    "that",
    "by",
    "be",
    "as",
    "are",
    "at",
    "from",
    "or",
    "we",
    "you",
    "your",
    "our",
    "us",
    "their",
    "they",
    "i",
    "me",
    "my",
    "was",
    "were",
    "can",
    "will",
    "may",
}

_BOILERPLATE_KEYWORDS = ("cookie", "privacy", "terms", "newsletter", "accept")


def _clamp(score: float) -> float:
    return max(0.0, min(1.0, score))


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def compute_cleanliness(text: str) -> float:
    """Compute a heuristic cleanliness score in [0, 1]."""
    if not text or not text.strip():
        return 0.0
    total_chars = len(text)
    alnum_ratio = sum(ch.isalnum() for ch in text) / total_chars if total_chars else 0.0

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return 0.0
    unique_ratio = len(set(lines)) / len(lines)
    short_ratio = sum(1 for line in lines if len(line) < 30) / len(lines)

    lowered = text.lower()
    boilerplate_hits = sum(1 for kw in _BOILERPLATE_KEYWORDS if kw in lowered)
    boilerplate_penalty = min(0.3, 0.05 * boilerplate_hits)

    score = (
        0.4 * alnum_ratio
        + 0.4 * unique_ratio
        + 0.2 * (1.0 - short_ratio)
        - boilerplate_penalty
    )
    if math.isnan(score):
        return 0.0
    return _clamp(score)


def compute_completeness(baseline_text: str, candidate_text: str) -> float:
    """Compute a heuristic completeness score in [0, 1] vs. baseline."""
    baseline_tokens = _tokenize(baseline_text)
    candidate_tokens = _tokenize(candidate_text)

    if not baseline_tokens:
        return 1.0 if candidate_tokens else 0.0

    length_ratio = min(1.0, len(candidate_tokens) / len(baseline_tokens))

    baseline_words = [word for word in baseline_tokens if word not in _STOPWORDS]
    if not baseline_words:
        return length_ratio

    freq = Counter(baseline_words)
    top_words = {word for word, _ in freq.most_common(50)}
    if not top_words:
        return length_ratio

    candidate_set = {word for word in candidate_tokens if word not in _STOPWORDS}
    coverage_ratio = len(top_words & candidate_set) / len(top_words)

    score = 0.6 * length_ratio + 0.4 * coverage_ratio
    if math.isnan(score):
        return 0.0
    return _clamp(score)
