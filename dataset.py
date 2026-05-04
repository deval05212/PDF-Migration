import pandas as pd
from pathlib import Path

# Load the local dataset
df = pd.read_csv("Dataset.csv")

# Basic cleaning of the dataframe
total_initial = len(df)
df = df.dropna(subset=["Text"])
df["Text"] = df["Text"].astype(str)

# Deduplication
df = df.drop_duplicates(subset=["Text"])
total_after_dedup = len(df)

# Length filter: keep only resumes with > 500 characters
df = df[df["Text"].str.len() > 500]
total_after_len_filter = len(df)

# Select the head 400 after filtering
Resume = df["Text"].head(400)

output_dir = Path("Assets/resumes")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Initial rows: {total_initial}")
print(f"After deduplication: {total_after_dedup}")
print(f"After length filtering (>500 chars): {total_after_len_filter}")
print(f"Extracting {len(Resume)} resumes to {output_dir}...")

for idx, text in enumerate(Resume, 1):
    file_path = output_dir / f"{idx}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text.strip())
        f.write("\n")

print(f"Successfully saved {len(Resume)} resume files to {output_dir}")
