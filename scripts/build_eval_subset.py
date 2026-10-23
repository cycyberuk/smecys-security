import pandas as pd

# Load only necessary columns
df = pd.read_csv(
    "data/meajor_cleaned_preprocessed.csv",
    usecols=["body", "label", "source", "urls", "url_count", "subject"]
)

# Remove empty bodies and very short samples
df = df.dropna(subset=["body"])
df = df[df["body"].str.len() > 50]

# Stratified sampling: 250 phishing + 250 benign
phishing = df[df["label"] == 1.0]
benign = df[df["label"] == 0.0]

phishing_sample = phishing.groupby("source", group_keys=False).apply(
    lambda x: x.sample(min(len(x), int(250 * len(x) / len(phishing))), random_state=42)
)
benign_sample = benign.groupby("source", group_keys=False).apply(
    lambda x: x.sample(min(len(x), int(250 * len(x) / len(benign))), random_state=42)
)

# Top up if under 250 per class
if len(phishing_sample) < 250:
    extra = phishing.drop(phishing_sample.index).sample(250 - len(phishing_sample), random_state=42)
    phishing_sample = pd.concat([phishing_sample, extra])
if len(benign_sample) < 250:
    extra = benign.drop(benign_sample.index).sample(250 - len(benign_sample), random_state=42)
    benign_sample = pd.concat([benign_sample, extra])

subset = pd.concat([phishing_sample, benign_sample]).sample(frac=1, random_state=42).reset_index(drop=True)
subset["index"] = subset.index
subset.to_csv("data/eval_subset.csv", index=False)

print(f"Eval subset saved: {len(subset)} samples")
print("Label distribution:\n", subset["label"].value_counts())
print("Source distribution:\n", subset["source"].value_counts())
print(f"Samples with URLs: {(subset['url_count'] > 0).sum()}")