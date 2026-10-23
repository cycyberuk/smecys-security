import sys
import os

# Add project root to Python path so "src" package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import time
import json
from src.deepseek_client import analyze_email

# ============================================================
# Configuration
# ============================================================
EVAL_FILE = "data/eval_subset.csv"
RESULTS_DIR = "results"
RESULTS_FILE = os.path.join(RESULTS_DIR, "deepseek_results.csv")
BATCH_SIZE = 5          # <-- Set to 5 for testing, 50 for full run
SLEEP_PER_SAMPLE = 1    # seconds between API calls
SLEEP_PER_BATCH = 5     # seconds between batches

# ============================================================
# Setup
# ============================================================
os.makedirs(RESULTS_DIR, exist_ok=True)

df = pd.read_csv(EVAL_FILE)
print(f"Total samples in eval set: {len(df)}")

# Resume from checkpoint if results already exist
if os.path.exists(RESULTS_FILE):
    done = pd.read_csv(RESULTS_FILE)
    done_indices = set(done["index"].tolist())
    print(f"Resuming: {len(done_indices)} samples already processed")
else:
    done = pd.DataFrame()
    done_indices = set()

# Filter out already-processed samples
pending = df[~df.index.isin(done_indices)]
print(f"Pending samples: {len(pending)}")

if len(pending) == 0:
    print("All samples already processed. Delete results file to rerun.")
    sys.exit(0)

# ============================================================
# Batch loop
# ============================================================
for start in range(0, len(pending), BATCH_SIZE):
    batch = pending.iloc[start:start + BATCH_SIZE]
    batch_results = []

    for idx, row in batch.iterrows():
        try:
            # Build input with URL context prepended
            raw_urls = row.get("urls", "")
            if pd.notna(raw_urls) and str(raw_urls).strip() != "":
                urls_text = str(raw_urls)
            else:
                urls_text = "none"

            input_text = (
                f"URLs found in this email: {urls_text}\n\n"
                f"Email body:\n{row['body']}"
            )

            # Call DeepSeek API
            result_json = analyze_email(input_text)
            parsed = json.loads(result_json)

            batch_results.append({
                "index": idx,
                "label": row["label"],
                "verdict": parsed.get("verdict"),
                "confidence": parsed.get("confidence"),
                "source_dataset": row.get("source", "")
            })

        except Exception as e:
            print(f"  Sample {idx} failed: {e}")
            batch_results.append({
                "index": idx,
                "label": row["label"],
                "verdict": "ERROR",
                "confidence": None,
                "source_dataset": row.get("source", "")
            })

        time.sleep(SLEEP_PER_SAMPLE)

    # Append this batch to the results file
    batch_df = pd.DataFrame(batch_results)
    if done.empty or not os.path.exists(RESULTS_FILE):
        batch_df.to_csv(RESULTS_FILE, index=False)
        done = batch_df
    else:
        batch_df.to_csv(RESULTS_FILE, mode="a", header=False, index=False)
        done = pd.concat([done, batch_df], ignore_index=True)

    print(f"Completed {len(done)} / {len(df)} samples")
    time.sleep(SLEEP_PER_BATCH)

print(f"\nAll done. Results saved to: {RESULTS_FILE}")