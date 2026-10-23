import pandas as pd

# Load CSV (if memory is insufficient, use the Parquet version)
df = pd.read_csv("data/meajor_cleaned_preprocessed.csv")

print("Total samples:", len(df))
print("Columns:", df.columns.tolist())
print("\nLabel distribution:")
print(df["label"].value_counts())

# Check source dataset distribution (column name may be "source_dataset" or similar)
if "source_dataset" in df.columns:
    print("\nSource dataset distribution:")
    print(df["source_dataset"].value_counts())

# Focus on Nigerian Fraud samples
nigerian = df[df["source_dataset"].str.contains("Nigerian", case=False, na=False)]
print(f"\nNigerian Fraud samples: {len(nigerian)}")
print(nigerian.head(3)[["label", "source_dataset"]].to_string())