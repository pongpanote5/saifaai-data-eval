import json

from evaluation.eval_logger import log_metrics


def test_eval_logger_writes_jsonl(tmp_path):
    output_path = tmp_path / "out.jsonl"
    log_metrics(
        str(output_path),
        "https://example.com",
        "raw_text",
        0.0,
        1.23,
        0.5,
        0.6,
        chunk_count=2,
    )
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["url"] == "https://example.com"
    assert payload["mode"] == "raw_text"
    assert "elapsed_s" in payload
    assert payload["chunk_count"] == 2
