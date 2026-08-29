from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "train_transaction.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "final_holdout_full.csv"

print("Loading dataset...")

df = pd.read_csv(INPUT_PATH)

df = (
    df.sort_values(
        "TransactionDT",
        kind="mergesort"
    )
    .reset_index(drop=True)
)

# Same 80/20 chronological split used by your training notebook
split_index = int(len(df) * 0.80)

valid_df = (
    df.iloc[split_index:]
    .copy()
    .reset_index(drop=True)
)

# Same calibration/final-holdout split
calibration_size = int(len(valid_df) * 0.50)

final_holdout_full = (
    valid_df.iloc[calibration_size:]
    .copy()
    .reset_index(drop=True)
)

final_holdout_full.to_csv(
    OUTPUT_PATH,
    index=False
)

fraud_count = int(
    (final_holdout_full["isFraud"] == 1).sum()
)

legit_count = int(
    (final_holdout_full["isFraud"] == 0).sum()
)

fraud_rate = (
    fraud_count / len(final_holdout_full) * 100
)

print()
print("=" * 60)
print("FINAL FULL HOLDOUT CREATED")
print("=" * 60)

print(f"Saved to: {OUTPUT_PATH}")
print(f"Total rows: {len(final_holdout_full):,}")
print(f"Fraud rows: {fraud_count:,}")
print(f"Legitimate rows: {legit_count:,}")
print(f"Natural fraud prevalence: {fraud_rate:.2f}%")

print()
print("✅ Done")