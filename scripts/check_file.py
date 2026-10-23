import pandas as pd

# Read only first 5 rows to avoid loading the full 191 MB file
df = pd.read_csv("data/meajor_cleaned_preprocessed.csv", nrows=5)
print("Columns:", df.columns.tolist())
print("\nFirst 2 rows:")
print(df.head(2).to_string())