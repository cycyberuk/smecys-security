import pandas as pd

df = pd.read_csv(
    "data/meajor_cleaned_preprocessed.csv",
    usecols=["body", "label", "source", "urls", "url_count"]
)
print("Total samples:", len(df))
print("\nLabel distribution:\n", df["label"].value_counts())
print("\nSource distribution:\n", df["source"].value_counts())

# Nigerian Fraud subset
ng = df[df["source"].str.contains("nigerian", case=False, na=False)]
print(f"\nNigerian Fraud samples: {len(ng)}")
print("Nigerian label distribution:\n", ng["label"].value_counts())
print(f"Nigerian samples with URLs: {(ng['url_count'] > 0).sum()}")