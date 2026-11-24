from datasets import load_dataset

ds = load_dataset("arag0rn/SecVulEval")
df = ds["train"].to_pandas()

print("Total rows:", len(df))
print("Columns:", list(df.columns))
print(df["project"].value_counts().head(5))