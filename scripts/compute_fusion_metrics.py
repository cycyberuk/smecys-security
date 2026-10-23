import pandas as pd
import numpy as np

# Load results
ds = pd.read_csv("results/deepseek_results.csv")
vt = pd.read_csv("results/virustotal_results.csv")

# Merge on index
merged = ds.merge(vt, on="index", suffixes=("_ds", "_vt"))
merged = merged[merged["verdict"] != "ERROR"]
merged = merged.dropna(subset=["malicious", "total"])
merged = merged[merged["total"] > 0]  # remove samples with no VT data

print(f"Merged samples with both DeepSeek and VirusTotal: {len(merged)}")

# Map DeepSeek verdict to score (0-100)
def ds_score(v):
    return {"malicious": 90, "suspicious": 60, "benign": 10}.get(v, 50)

merged["ds_score"] = merged["verdict"].apply(ds_score)

# VirusTotal score: percentage of engines flagging as malicious
merged["vt_score"] = (merged["malicious"] / merged["total"]) * 100

# Fusion: 60% DeepSeek + 40% VirusTotal (as per paper)
merged["fused_score"] = 0.6 * merged["ds_score"] + 0.4 * merged["vt_score"]

# Classification thresholds
def fused_verdict(score):
    if score > 70:
        return "malicious"
    elif score > 40:
        return "suspicious"
    else:
        return "benign"

merged["fused_verdict"] = merged["fused_score"].apply(fused_verdict)

# Binarize for metrics
merged["label"] = merged["label_ds"].astype(int)
merged["pred_fused"] = merged["fused_verdict"].apply(lambda v: 0 if v == "benign" else 1)
merged["pred_ds"] = merged["verdict"].apply(lambda v: 0 if v == "benign" else 1)
merged["pred_vt"] = merged["vt_score"].apply(lambda s: 1 if s > 0 else 0)

def metrics(df, pred_col, name):
    tp = ((df[pred_col] == 1) & (df["label"] == 1)).sum()
    tn = ((df[pred_col] == 0) & (df["label"] == 0)).sum()
    fp = ((df[pred_col] == 1) & (df["label"] == 0)).sum()
    fn = ((df[pred_col] == 0) & (df["label"] == 1)).sum()
    acc = (tp + tn) / len(df)
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    print(f"\n{name}")
    print(f"  Samples: {len(df)}")
    print(f"  TP={tp}, TN={tn}, FP={fp}, FN={fn}")
    print(f"  Accuracy:  {acc:.3f}")
    print(f"  Precision: {prec:.3f}")
    print(f"  Recall:    {rec:.3f}")
    print(f"  F1:        {f1:.3f}")
    print(f"  FPR:       {fpr:.3f}")
    return {"name": name, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "fpr": fpr, "n": len(df)}

# Compare three configurations on the merged subset
results = []
results.append(metrics(merged, "pred_ds", "DeepSeek Only"))
results.append(metrics(merged, "pred_vt", "VirusTotal Only"))
results.append(metrics(merged, "pred_fused", "Proposed Fusion"))

# Cross-tab for the paper
print("\nFusion verdict distribution:")
print(pd.crosstab(merged["label"], merged["fused_verdict"]))

# Save merged results
merged.to_csv("results/fusion_results.csv", index=False)
print("\nSaved to results/fusion_results.csv")