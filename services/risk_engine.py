# from dataclasses import dataclass


# # ============================================================
# # PAYGUARD DECISION POLICY
# # ============================================================

# ALLOW_MAX = 0.60
# REVIEW_MAX = 0.80
# VERIFY_MAX = 0.90


# # ============================================================
# # RISK RESULT
# # ============================================================

# @dataclass
# class RiskDecision:
#     probability: float
#     risk_level: str
#     decision: str
#     reason: str


# # ============================================================
# # RISK ENGINE
# # ============================================================

# def evaluate_risk(probability: float) -> RiskDecision:
#     probability = float(probability)

#     probability = max(
#         0.0,
#         min(probability, 1.0)
#     )

#     # Risk level
#     if probability < 0.50:
#         risk_level = "LOW"

#     elif probability < 0.80:
#         risk_level = "MEDIUM"

#     elif probability < 0.90:
#         risk_level = "HIGH"

#     else:
#         risk_level = "CRITICAL"

#     # Decision
#     if probability < ALLOW_MAX:

#         decision = "ALLOW"

#         reason = (
#             "Fraud probability is below 60%. "
#             "Routine processing is appropriate."
#         )

#     elif probability < REVIEW_MAX:

#         decision = "REVIEW"

#         reason = (
#             "Fraud probability is between 60% and 80%. "
#             "Manual review or additional verification is recommended."
#         )

#     elif probability < VERIFY_MAX:

#         decision = "VERIFY"

#         reason = (
#             "Fraud probability is between 80% and 90%. "
#             "Strong customer verification is recommended."
#         )

#     else:

#         decision = "BLOCK"

#         reason = (
#             "Fraud probability is 90% or higher. "
#             "Blocking and investigation are recommended."
#         )

#     return RiskDecision(
#         probability=probability,
#         risk_level=risk_level,
#         decision=decision,
#         reason=reason,
#     )













from dataclasses import dataclass

ALLOW_MAX = 0.60
REVIEW_MAX = 0.80
VERIFY_MAX = 0.90


@dataclass
class RiskDecision:
    probability: float
    risk_level: str
    decision: str
    reason: str


def evaluate_risk(probability: float) -> RiskDecision:
    probability = float(probability)
    probability = max(0.0, min(probability, 1.0))

    if probability < 0.50:
        risk_level = "LOW"
    elif probability < 0.80:
        risk_level = "MEDIUM"
    elif probability < 0.90:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    if probability < ALLOW_MAX:
        decision = "ALLOW"
        reason = (
            "Fraud probability is below 60%. "
            "Routine processing is appropriate."
        )
    elif probability < REVIEW_MAX:
        decision = "REVIEW"
        reason = (
            "Fraud probability is between 60% and 80%. "
            "Manual review or additional verification is recommended."
        )
    elif probability < VERIFY_MAX:
        decision = "VERIFY"
        reason = (
            "Fraud probability is between 80% and 90%. "
            "Strong verification is recommended before proceeding."
        )
    else:
        decision = "BLOCK"
        reason = (
            "Fraud probability is 90% or higher. "
            "Blocking and investigation are recommended."
        )

    return RiskDecision(
        probability=probability,
        risk_level=risk_level,
        decision=decision,
        reason=reason,
    )