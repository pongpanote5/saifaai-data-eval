# SaifaAI Data Eval

## Usage

1. Populate `data/test_urls.csv` with one URL per row. Blank rows are ignored.
2. Run the evaluation:

```bash
python scripts/run_eval.py --mode both
```

### Output JSONL fields
Each line in the JSONL output includes:

- `url`: the source URL.
- `mode`: `raw_text` or `llm_markdown`.
- `elapsed_s`: pipeline elapsed time in seconds.
- `cleanliness`: heuristic noise score in `[0, 1]`.
- `completeness`: heuristic coverage vs. raw text baseline in `[0, 1]`.
- `chunk_count` (optional): number of chunks produced.
- `error` (optional): error message if the pipeline encountered a failure.
