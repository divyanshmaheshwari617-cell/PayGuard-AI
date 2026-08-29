import pandas as pd
import numpy as np

# ==========================================
# PAYGUARD AI - TRANSACTION DATA GENERATOR
# ==========================================

# Make results reproducible
np.random.seed(42)

# Number of transactions
N = 100_000

print("Generating PayGuard AI transaction data...")

# ==========================================
# 1. BASIC INFORMATION
# ==========================================

transactions = pd.DataFrame({
    "transaction_id": [
        f"TXN{i:07d}" for i in range(1, N + 1)
    ],

    "user_id": [
        f"USR{np.random.randint(1, 20_001):05d}"
        for _ in range(N)
    ],

    "merchant_id": [
        f"MER{np.random.randint(1, 1_001):04d}"
        for _ in range(N)
    ]
})


# ==========================================
# 2. TRANSACTION FEATURES
# ==========================================

# Transaction amount in INR
transactions["amount"] = np.round(
    np.random.lognormal(
        mean=7.0,
        sigma=1.0,
        size=N
    ),
    2
)

# Payment method
transactions["payment_method"] = np.random.choice(
    ["UPI", "CARD", "NETBANKING", "WALLET"],
    size=N,
    p=[0.55, 0.25, 0.15, 0.05]
)

# Bank
transactions["bank"] = np.random.choice(
    ["Bank_A", "Bank_B", "Bank_C", "Bank_D", "Bank_E"],
    size=N
)

# Device
transactions["device_type"] = np.random.choice(
    ["Android", "iOS", "Web"],
    size=N,
    p=[0.50, 0.30, 0.20]
)

# User location
transactions["location"] = np.random.choice(
    [
        "Mumbai",
        "Delhi",
        "Bangalore",
        "Hyderabad",
        "Chennai",
        "Pune",
        "Kolkata",
        "Other"
    ],
    size=N
)

# Hour of transaction
transactions["transaction_hour"] = np.random.randint(
    0,
    24,
    size=N
)

# Number of previous transactions
transactions["previous_transactions"] = np.random.poisson(
    lam=15,
    size=N
)

# Previous failed attempts
transactions["failed_attempts"] = np.random.poisson(
    lam=0.5,
    size=N
)

# Age of account
transactions["account_age_days"] = np.random.randint(
    1,
    2000,
    size=N
)

# Whether user is using a new device
transactions["is_new_device"] = np.random.choice(
    [0, 1],
    size=N,
    p=[0.85, 0.15]
)

# Payment gateway
transactions["gateway"] = np.random.choice(
    ["Gateway_A", "Gateway_B", "Gateway_C"],
    size=N,
    p=[0.40, 0.35, 0.25]
)

# Gateway latency
transactions["latency_ms"] = np.round(
    np.random.lognormal(
        mean=5.5,
        sigma=0.45,
        size=N
    ),
    0
)


# ==========================================
# 3. FRAUD GENERATION
# ==========================================

fraud_score = (
    0.02
    + 0.12 * transactions["is_new_device"]
    + 0.10 * (transactions["failed_attempts"] >= 3)
    + 0.08 * (transactions["amount"] > 50_000)
    + 0.08 * (
        transactions["transaction_hour"].between(0, 5)
    )
    + 0.07 * (
        transactions["account_age_days"] < 30
    )
)

# Keep probability between 0 and 90%
fraud_score = np.clip(
    fraud_score,
    0,
    0.90
)

# Generate fraud label
transactions["is_fraud"] = (
    np.random.random(N) < fraud_score
).astype(int)


# ==========================================
# 4. PAYMENT FAILURE GENERATION
# ==========================================

failure_score = (
    0.03
    + 0.08 * (
        transactions["failed_attempts"] >= 2
    )
    + 0.06 * (
        transactions["latency_ms"] > 400
    )
    + 0.05 * (
        transactions["bank"] == "Bank_E"
    )
    + 0.04 * (
        transactions["gateway"] == "Gateway_B"
    )
)

# Keep probability between 0 and 80%
failure_score = np.clip(
    failure_score,
    0,
    0.80
)

# Generate payment failure label
transactions["payment_failed"] = (
    np.random.random(N) < failure_score
).astype(int)


# ==========================================
# 5. TRANSACTION STATUS
# ==========================================

transactions["transaction_status"] = np.where(
    transactions["payment_failed"] == 1,
    "FAILED",
    "SUCCESS"
)


# ==========================================
# 6. SAVE DATASET
# ==========================================

output_path = "data/raw/transactions.csv"

transactions.to_csv(
    output_path,
    index=False
)


# ==========================================
# 7. DISPLAY RESULTS
# ==========================================

print()
print("==========================================")
print("DATASET GENERATED SUCCESSFULLY")
print("==========================================")

print(f"Rows       : {len(transactions):,}")
print(f"Columns    : {len(transactions.columns)}")
print(f"Saved to   : {output_path}")

print()
print(
    f"Fraud rate : "
    f"{transactions['is_fraud'].mean() * 100:.2f}%"
)

print(
    f"Failure rate: "
    f"{transactions['payment_failed'].mean() * 100:.2f}%"
)

print()
print("Columns:")
print(list(transactions.columns))

print()
print("First 5 transactions:")
print(transactions.head())

print()
print("==========================================")
print("DONE")
print("==========================================")