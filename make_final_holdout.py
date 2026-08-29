from pathlib import Path
import pandas as pd

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "train_transaction.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "final_holdout_1000.csv"
)


# ============================================================
# LOAD ORIGINAL DATA
# ============================================================

print("Loading original transaction dataset...")

df = pd.read_csv(INPUT_PATH)

print(f"Total rows loaded: {len(df):,}")


# ============================================================
# BASIC CHECKS
# ============================================================

required_columns = [
    "TransactionDT",
    "isFraud",
]

for col in required_columns:
    if col not in df.columns:
        raise ValueError(
            f"Required column missing: {col}"
        )


# ============================================================
# SAME CHRONOLOGICAL ORDER AS MODEL NOTEBOOK
# ============================================================

df = (
    df
    .sort_values(
        "TransactionDT",
        kind="mergesort",
    )
    .reset_index(drop=True)
)


# ============================================================
# SAME 80 / 20 SPLIT AS TRAINING NOTEBOOK
# ============================================================

split_index = int(
    len(df) * 0.80
)

train_df = (
    df.iloc[:split_index]
    .copy()
)

valid_df = (
    df.iloc[split_index:]
    .copy()
    .reset_index(drop=True)
)

print()
print("Chronological split:")
print(
    f"Training rows   : {len(train_df):,}"
)

print(
    f"Validation rows : {len(valid_df):,}"
)


# ============================================================
# SAME VALIDATION SPLIT AS NOTEBOOK
#
# First half:
# threshold calibration
#
# Second half:
# final holdout
# ============================================================

calibration_size = int(
    len(valid_df) * 0.50
)

calibration_df = (
    valid_df
    .iloc[:calibration_size]
    .copy()
)

final_holdout_df = (
    valid_df
    .iloc[calibration_size:]
    .copy()
    .reset_index(drop=True)
)


print()
print("Validation subdivision:")

print(
    f"Calibration rows : {len(calibration_df):,}"
)

print(
    f"Final holdout    : {len(final_holdout_df):,}"
)


# ============================================================
# CHECK HOLDOUT FRAUD DISTRIBUTION
# ============================================================

fraud_rows = (
    final_holdout_df[
        final_holdout_df["isFraud"] == 1
    ]
    .copy()
)

legit_rows = (
    final_holdout_df[
        final_holdout_df["isFraud"] == 0
    ]
    .copy()
)


print()
print(
    f"Available fraud rows      : {len(fraud_rows):,}"
)

print(
    f"Available legitimate rows : {len(legit_rows):,}"
)


# ============================================================
# CREATE BALANCED 1,000-ROW DEMO TEST
# ============================================================

N_FRAUD = 500
N_LEGIT = 500


if len(fraud_rows) < N_FRAUD:

    raise ValueError(
        f"Final holdout contains only "
        f"{len(fraud_rows):,} fraud rows. "
        f"Need {N_FRAUD:,}."
    )


if len(legit_rows) < N_LEGIT:

    raise ValueError(
        f"Final holdout contains only "
        f"{len(legit_rows):,} legitimate rows. "
        f"Need {N_LEGIT:,}."
    )


fraud_sample = fraud_rows.sample(
    n=N_FRAUD,
    random_state=2026,
)

legit_sample = legit_rows.sample(
    n=N_LEGIT,
    random_state=2026,
)


final_test = pd.concat(
    [
        fraud_sample,
        legit_sample,
    ],
    ignore_index=True,
)


# ============================================================
# SHUFFLE ONLY AFTER SELECTING
# ============================================================

final_test = (
    final_test
    .sample(
        frac=1,
        random_state=2026,
    )
    .reset_index(drop=True)
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

final_test.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 65)
print("FINAL HOLDOUT TEST FILE CREATED")
print("=" * 65)

print(
    f"Saved to: {OUTPUT_PATH}"
)

print(
    f"Rows: {len(final_test):,}"
)

print(
    f"Columns: {len(final_test.columns):,}"
)

print(
    f"Fraud: "
    f"{int((final_test['isFraud'] == 1).sum()):,}"
)

print(
    f"Legitimate: "
    f"{int((final_test['isFraud'] == 0).sum()):,}"
)

print()

print("TransactionDT range:")

print(
    "Minimum:",
    final_test["TransactionDT"].min()
)

print(
    "Maximum:",
    final_test["TransactionDT"].max()
)

print()

print("Fraud distribution:")

print(
    final_test[
        "isFraud"
    ].value_counts()
)

print()
print("✅ Done.")
print()
print(
    "IMPORTANT: This balanced file is for "
    "demonstration/testing."
)
print(
    "For official scientific metrics, use the "
    "complete final holdout distribution."
)