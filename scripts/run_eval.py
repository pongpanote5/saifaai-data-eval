from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from evaluation.eval_logger import log_metrics
from evaluation.metrics import compute_cleanliness, compute_completeness
from pipelines.raw_text_pipeline import run_raw_text_pipeline
from pipelines.llm_markdown_pipeline import run_llm_markdown_pipeline


def _read_urls(path: Path, max_urls: int | None) -> list[str]:
    if not path.exists():
        return []
    urls: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            url = row[0].strip()
            if not url:
                continue
            urls.append(url)
            if max_urls is not None and len(urls) >= max_urls:
                break
    return urls


def _write_results(output_path: Path, results: list[dict], baselines: dict[str, dict]) -> None:
    for result in results:
        url = result.get("url", "")
        mode = result.get("mode", "")
        baseline_text = baselines.get(url, {}).get("text", "")
        candidate_text = result.get("text") or result.get("markdown_text", "")
        cleanliness = compute_cleanliness(candidate_text)
        completeness = compute_completeness(baseline_text, candidate_text)
        elapsed_s = result.get("elapsed_s", 0.0)

        extras = {
            "chunk_count": result.get("chunk_count", 0),
            "error": result.get("error"),
        }
        log_metrics(
            str(output_path),
            url,
            mode,
            0.0,
            float(elapsed_s),
            cleanliness,
            completeness,
            **{k: v for k, v in extras.items() if v is not None},
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run extraction evaluation pipelines.")
    parser.add_argument("--input", default="data/test_urls.csv", help="CSV file with URLs")
    parser.add_argument("--output", default="outputs/eval_results.jsonl", help="JSONL output path")
    parser.add_argument(
        "--mode",
        choices=["raw_text", "llm_markdown", "both"],
        default="both",
        help="Which pipeline to run",
    )
    parser.add_argument("--max_urls", type=int, default=None, help="Limit number of URLs")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    urls = _read_urls(input_path, args.max_urls)
    if not urls:
        return 0

    baselines: dict[str, dict] = {}
    if args.mode in {"raw_text", "both"}:
        raw_results = run_raw_text_pipeline(urls)
        baselines = {item["url"]: item for item in raw_results}
        _write_results(output_path, raw_results, baselines)

    if args.mode in {"llm_markdown", "both"}:
        if not baselines:
            baselines = {item["url"]: item for item in run_raw_text_pipeline(urls)}
        markdown_results = run_llm_markdown_pipeline(urls)
        _write_results(output_path, markdown_results, baselines)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
