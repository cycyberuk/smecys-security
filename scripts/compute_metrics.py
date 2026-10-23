import pandas as pd

df = pd.read_csv("results/deepseek_results.csv")
df = df[df["verdict"] != "ERROR"]

# Binarize: benign=0, suspicious/malicious=1
df["pred"] = df["verdict"].apply(lambda v: 0 if v == "benign" else 1)
df["label"] = df["label"].astype(int)

tp = ((df["pred"] == 1) & (df["label"] == 1)).sum()
tn = ((df["pred"] == 0) & (df["label"] == 0)).sum()
fp = ((df["pred"] == 1) & (df["label"] == 0)).sum()
fn = ((df["pred"] == 0) & (df["label"] == 1)).sum()

accuracy = (tp + tn) / len(df)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

print(f"Samples evaluated: {len(df)}")
print(f"TP={tp}, TN={tn}, FP={fp}, FN={fn}")
print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1:        {f1:.3f}")
print(f"FPR:       {fpr:.3f}")

# Per-source breakdown
print("\nPer-source accuracy:")
for src in df["source_dataset"].dropna().unique():
    sub = df[df["source_dataset"] == src]
    acc = (sub["pred"] == sub["label"]).mean()
    print(f"  {src}: {acc:.3f} ({len(sub)} samples)")