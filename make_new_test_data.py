from pathlib import Path
import pandas as pd

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "train_transaction.csv"

OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "new_holdout_1000.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("Loading transaction data...")

df = pd.read_csv(TRAIN_PATH)

print(f"Total rows loaded: {len(df):,}")


# ============================================================
# CHECK LABEL
# ============================================================

if "isFraud" not in df.columns:
    raise ValueError("Column 'isFraud' was not found.")


# ============================================================
# IMPORTANT:
# Use the LAST part of the dataset as a time-style holdout.
#
# This is safer than randomly sampling from the full dataset
# because fraud data is time-dependent.
# ============================================================

df = df.sort_values("TransactionDT").reset_index(drop=True)

holdout_fraction = 0.20

split_index = int(
    len(df) * (1 - holdout_fraction)
)

holdout = df.iloc[split_index:].copy()

print(
    f"Holdout pool rows: {len(holdout):,}"
)


# ============================================================
# SEPARATE FRAUD / LEGIT
# ============================================================

fraud_rows = holdout[
    holdout["isFraud"] == 1
].copy()

legit_rows = holdout[
    holdout["isFraud"] == 0
].copy()

print(
    f"Fraud rows available: {len(fraud_rows):,}"
)

print(
    f"Legitimate rows available: {len(legit_rows):,}"
)


# ============================================================
# CREATE BALANCED 1000-ROW TEST SET
# ============================================================

N_FRAUD = 500
N_LEGIT = 500

if len(fraud_rows) < N_FRAUD:
    raise ValueError(
        f"Only {len(fraud_rows)} fraud rows are available."
    )

if len(legit_rows) < N_LEGIT:
    raise ValueError(
        f"Only {len(legit_rows)} legitimate rows are available."
    )


fraud_sample = fraud_rows.sample(
    n=N_FRAUD,
    random_state=2026,
)

legit_sample = legit_rows.sample(
    n=N_LEGIT,
    random_state=2026,
)


new_test = pd.concat(
    [
        fraud_sample,
        legit_sample,
    ],
    ignore_index=True,
)


# Shuffle rows after selecting them
new_test = new_test.sample(
    frac=1,
    random_state=2026,
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

new_test.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("NEW TEST DATA CREATED")
print("=" * 60)

print(
    f"Output file: {OUTPUT_PATH}"
)

print(
    f"Total rows: {len(new_test):,}"
)

print(
    f"Fraud rows: {(new_test['isFraud'] == 1).sum():,}"
)

print(
    f"Legitimate rows: {(new_test['isFraud'] == 0).sum():,}"
)

print()
print("Fraud distribution:")

print(
    new_test["isFraud"].value_counts()
)

print()
print("Done.")
