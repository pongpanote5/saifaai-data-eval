import json
import os

def log_metrics(output_path, url, mode, start, end, clean_score, complete_score, **extras):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data = {
        "url": url,
        "mode": mode,
        "elapsed_s": round(end - start, 2),
        "cleanliness": clean_score,
        "completeness": complete_score,
    }
    if extras:
        data.update(extras)
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")
