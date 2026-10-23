import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import time
import requests
import base64
from dotenv import load_dotenv

load_dotenv()
VT_KEY = os.environ.get("VIRUSTOTAL_API_KEY")
VT_BASE = "https://www.virustotal.com/api/v3"

df = pd.read_csv("data/eval_subset.csv")
df = df[df["url_count"] > 0].copy()

results_file = "results/virustotal_results.csv"
if os.path.exists(results_file):
    done = pd.read_csv(results_file)
    done_indices = set(done["index"].tolist())
    print(f"Resuming: {len(done_indices)} samples already checked")
else:
    done = pd.DataFrame()
    done_indices = set()

pending = df[~df.index.isin(done_indices)]
print(f"Pending URL samples: {len(pending)}")

for i, (idx, row) in enumerate(pending.iterrows(), 1):
    urls = str(row["urls"]).split("\n")
    url = urls[0].strip()
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

    try:
        resp = requests.get(f"{VT_BASE}/urls/{url_id}",
                            headers={"x-apikey": VT_KEY}, timeout=30)
        if resp.status_code == 404:
            malicious, total = 0, 0
        elif resp.status_code == 429:
            print(f"  Rate limited at sample {idx}, sleeping 60s")
            time.sleep(60)
            continue
        else:
            resp.raise_for_status()
            stats = resp.json()["data"]["attributes"]["last_analysis_stats"]
            malicious = stats.get("malicious", 0)
            total = sum(stats.values())
    except Exception as e:
        print(f"  Sample {idx} failed: {e}")
        malicious, total = None, None

    row_df = pd.DataFrame([{
        "index": idx, "label": row["label"],
        "malicious": malicious, "total": total
    }])
    if done.empty:
        row_df.to_csv(results_file, index=False)
        done = row_df
    else:
        row_df.to_csv(results_file, mode="a", header=False, index=False)
        done = pd.concat([done, row_df], ignore_index=True)

    print(f"Checked {len(done)} / {len(pending)} (sample index {idx})")
    time.sleep(16)  # safe margin below 4/min

print("VirusTotal checks complete.")