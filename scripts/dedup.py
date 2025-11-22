import pandas as pd

df = pd.read_csv("data/hit5_clean_manual.csv")
df = df.drop_duplicates()
df.to_csv("data/hit5_clean_deduped.csv", index=False)
print(f"Deduplicated draws: {len(df)}")
