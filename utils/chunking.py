from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

_DEFAULT_CHUNK_SIZE = 300
_DEFAULT_CHUNK_OVERLAP = 30
_DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " "]


@dataclass(frozen=True)
class ChunkingConfig:
    chunk_size: int
    chunk_overlap: int
    separators: list[str]


def _parse_chunking_notes(path: Path) -> ChunkingConfig:
    chunk_size = _DEFAULT_CHUNK_SIZE
    chunk_overlap = _DEFAULT_CHUNK_OVERLAP
    separators = list(_DEFAULT_SEPARATORS)

    if not path.exists():
        return ChunkingConfig(chunk_size, chunk_overlap, separators)

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("chunk_size:"):
            try:
                chunk_size = int(line.split(":", 1)[1].strip())
            except ValueError:
                continue
        elif line.startswith("chunk_overlap:"):
            try:
                chunk_overlap = int(line.split(":", 1)[1].strip())
            except ValueError:
                continue
        elif line.startswith("separators:"):
            raw = line.split(":", 1)[1].strip()
            if raw.startswith("[") and raw.endswith("]"):
                trimmed = raw[1:-1]
                parts = [part.strip().strip("'\"") for part in trimmed.split(",")]
                separators = [part for part in parts if part]

    if not separators:
        separators = list(_DEFAULT_SEPARATORS)

    return ChunkingConfig(chunk_size, chunk_overlap, separators)


def _split_units(text: str, separators: Iterable[str]) -> list[str]:
    separators = [sep for sep in separators if sep != ""]
    if not separators:
        return [text]

    sep = separators[0]
    if sep not in text:
        return _split_units(text, separators[1:])

    parts = text.split(sep)
    units = []
    for index, part in enumerate(parts):
        if not part:
            continue
        if index < len(parts) - 1:
            units.append(part + sep)
        else:
            units.append(part)
    return units


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks based on chunking notes or defaults."""
    config = _parse_chunking_notes(Path("config/chunking_notes.md"))
    if not text:
        return []

    units = _split_units(text, config.separators)
    chunks: list[str] = []
    current = ""

    for unit in units:
        if not current:
            current = unit
            continue

        if len(current) + len(unit) <= config.chunk_size:
            current += unit
            continue

        chunks.append(current.strip())
        overlap_text = current[-config.chunk_overlap :] if config.chunk_overlap > 0 else ""
        current = overlap_text + unit

    if current.strip():
        chunks.append(current.strip())

    return [chunk for chunk in chunks if chunk]
