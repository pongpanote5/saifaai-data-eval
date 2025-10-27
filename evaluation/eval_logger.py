import time, json, os

def log_metrics(output_path, url, mode, start, end, clean_score, complete_score):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data = {
        "url": url,
        "mode": mode,
        "time_sec": round(end - start, 2),
        "cleanliness": clean_score,
        "completeness": complete_score
    }
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")
