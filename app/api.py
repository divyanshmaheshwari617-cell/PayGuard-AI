# from pathlib import Path
# import sys
# from typing import Any

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field

# # ============================================================
# # PROJECT PATH
# # ============================================================

# # api.py is located directly inside D:\PayGuard-AI
# PROJECT_ROOT = Path(__file__).resolve().parent

# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))


# # ============================================================
# # PAYGUARD IMPORTS
# # ============================================================

# try:
#     from src.predict import PayGuardModel
# except Exception as exc:
#     raise RuntimeError(
#         f"Could not import PayGuardModel: "
#         f"{type(exc).__name__}: {exc}"
#     ) from exc


# try:
#     from src.copilot import ask_copilot
# except Exception:
#     ask_copilot = None


# try:
#     from services.risk_engine import (
#         evaluate_risk,
#         ALLOW_MAX,
#         REVIEW_MAX,
#         VERIFY_MAX,
#     )
# except Exception:
#     # Fallback policy so the API can still start
#     ALLOW_MAX = 0.60
#     REVIEW_MAX = 0.80
#     VERIFY_MAX = 0.90

#     class FallbackRisk:
#         def __init__(
#             self,
#             probability,
#             risk_level,
#             decision,
#             reason,
#         ):
#             self.probability = probability
#             self.risk_level = risk_level
#             self.decision = decision
#             self.reason = reason

#     def evaluate_risk(probability):

#         probability = float(probability)
#         probability = max(
#             0.0,
#             min(
#                 probability,
#                 1.0,
#             ),
#         )

#         if probability < 0.50:
#             risk_level = "LOW"
#         elif probability < 0.80:
#             risk_level = "MEDIUM"
#         elif probability < 0.90:
#             risk_level = "HIGH"
#         else:
#             risk_level = "CRITICAL"

#         if probability < 0.60:
#             decision = "ALLOW"
#             reason = (
#                 "Fraud probability is below 60%. "
#                 "Routine processing is appropriate."
#             )

#         elif probability < 0.80:
#             decision = "REVIEW"
#             reason = (
#                 "Fraud probability is between 60% and 80%. "
#                 "Manual review is recommended."
#             )

#         elif probability < 0.90:
#             decision = "VERIFY"
#             reason = (
#                 "Fraud probability is between 80% and 90%. "
#                 "Strong verification is recommended."
#             )

#         else:
#             decision = "BLOCK"
#             reason = (
#                 "Fraud probability is 90% or higher. "
#                 "Blocking and investigation are recommended."
#             )

#         return FallbackRisk(
#             probability=probability,
#             risk_level=risk_level,
#             decision=decision,
#             reason=reason,
#         )


# # ============================================================
# # FASTAPI APPLICATION
# # ============================================================

# app = FastAPI(
#     title="PayGuard AI Risk API",
#     description=(
#         "Defense-only payment fraud risk detection and "
#         "decision API for PayGuard test environments."
#     ),
#     version="2.0.0",
# )


# # ============================================================
# # LOAD MODEL ONCE
# # ============================================================

# try:
#     model = PayGuardModel()
# except Exception as exc:
#     raise RuntimeError(
#         f"PayGuard model could not be loaded: "
#         f"{type(exc).__name__}: {exc}"
#     ) from exc


# # ============================================================
# # TRANSACTION SCHEMA
# # ============================================================

# class Transaction(BaseModel):

#     TransactionID: int = 0

#     TransactionDT: int = 0

#     TransactionAmt: float = 0.0

#     ProductCD: str = "W"

#     card1: float | None = None
#     card2: float | None = None
#     card3: float | None = None

#     card4: str | None = None

#     card5: float | None = None
#     card6: float | None = None

#     addr1: float | None = None
#     addr2: float | None = None

#     dist1: float | None = None
#     dist2: float | None = None

#     P_emaildomain: str | None = None
#     R_emaildomain: str | None = None

#     DeviceType: str | None = None
#     DeviceInfo: str | None = None


# # ============================================================
# # FLEXIBLE FULL TRANSACTION REQUEST
# # ============================================================

# class FullTransaction(BaseModel):
#     """
#     Flexible request for a full real transaction row.

#     This allows the API to receive the large feature set
#     available in your real IEEE-CIS transaction data.
#     """

#     data: dict[str, Any] = Field(
#         default_factory=dict
#     )


# # ============================================================
# # COPILOT REQUEST
# # ============================================================

# class CopilotRequest(BaseModel):

#     question: str

#     context: str = ""


# # ============================================================
# # HOME
# # ============================================================

# @app.get("/")
# def home():

#     return {
#         "application": "PayGuard AI",
#         "status": "online",
#         "model": "CatBoost",
#         "purpose": "Payment Fraud Detection",
#         "api_version": "2.0.0",
#         "decision_policy": {
#             "below_60_percent": "ALLOW",
#             "60_to_below_80_percent": "REVIEW",
#             "80_to_below_90_percent": "VERIFY",
#             "90_percent_or_higher": "BLOCK",
#         },
#     }


# # ============================================================
# # HEALTH
# # ============================================================

# @app.get("/health")
# def health():

#     return {
#         "status": "healthy",
#         "model_loaded": True,
#         "model": "CatBoost",
#         "features": len(
#             getattr(
#                 model,
#                 "features",
#                 []
#             )
#         ),
#         "categorical_features": len(
#             getattr(
#                 model,
#                 "categorical_features",
#                 []
#             )
#         ),
#         "decision_policy": {
#             "ALLOW_MAX": ALLOW_MAX,
#             "REVIEW_MAX": REVIEW_MAX,
#             "VERIFY_MAX": VERIFY_MAX,
#         },
#     }


# # ============================================================
# # MODEL INFORMATION
# # ============================================================

# @app.get("/model-info")
# def model_info():

#     return {
#         "model": "CatBoost",

#         "features": len(
#             getattr(
#                 model,
#                 "features",
#                 []
#             )
#         ),

#         "categorical_features": len(
#             getattr(
#                 model,
#                 "categorical_features",
#                 []
#             )
#         ),

#         "stored_training_threshold": getattr(
#             model,
#             "threshold",
#             None,
#         ),

#         "decision_policy": {
#             "below_60_percent": "ALLOW",
#             "60_to_below_80_percent": "REVIEW",
#             "80_to_below_90_percent": "VERIFY",
#             "90_percent_or_higher": "BLOCK",
#         },

#         "risk_policy": {
#             "below_50_percent": "LOW",
#             "50_to_below_80_percent": "MEDIUM",
#             "80_to_below_90_percent": "HIGH",
#             "90_percent_or_higher": "CRITICAL",
#         },
#     }


# # ============================================================
# # COMMON PREDICTION FUNCTION
# # ============================================================

# def run_prediction(
#     transaction_data: dict[str, Any]
# ):

#     try:

#         # ------------------------------------------------------
#         # Get model probability
#         # ------------------------------------------------------

#         probabilities = (
#             model.predict_probability(
#                 transaction_data
#             )
#         )

#         if len(probabilities) == 0:
#             raise RuntimeError(
#                 "The model returned no probability."
#             )

#         probability = float(
#             probabilities[0]
#         )

#         # ------------------------------------------------------
#         # Apply Risk Engine
#         # ------------------------------------------------------

#         risk = evaluate_risk(
#             probability
#         )

#         # ------------------------------------------------------
#         # Return unified result
#         # ------------------------------------------------------

#         return {
#             "transaction_id":
#                 transaction_data.get(
#                     "TransactionID"
#                 ),

#             "fraud_probability":
#                 probability,

#             "fraud_probability_percent":
#                 probability * 100.0,

#             "risk_score":
#                 probability * 100.0,

#             "risk_level":
#                 risk.risk_level,

#             "decision":
#                 risk.decision,

#             "reason":
#                 risk.reason,

#             "model":
#                 "CatBoost",
#         }

#     except Exception as exc:

#         raise HTTPException(
#             status_code=400,
#             detail=(
#                 f"Prediction failed: "
#                 f"{type(exc).__name__}: {exc}"
#             ),
#         ) from exc


# # ============================================================
# # ORIGINAL PREDICT ENDPOINT
# # ============================================================

# @app.post("/predict")
# def predict(
#     transaction: Transaction
# ):

#     transaction_data = (
#         transaction.model_dump()
#     )

#     result = run_prediction(
#         transaction_data
#     )

#     return {
#         "transaction_id":
#             transaction.TransactionID,

#         "prediction":
#             result,
#     }


# # ============================================================
# # FULL FEATURE / RISK ENDPOINT
# # ============================================================

# @app.post("/risk")
# def risk_prediction(
#     request: FullTransaction
# ):

#     if not request.data:

#         raise HTTPException(
#             status_code=400,
#             detail="Transaction data cannot be empty.",
#         )

#     return run_prediction(
#         request.data
#     )


# # ============================================================
# # BATCH ENDPOINT
# # ============================================================

# @app.post("/batch")
# def batch_predict(
#     transactions: list[dict[str, Any]]
# ):

#     if not transactions:

#         raise HTTPException(
#             status_code=400,
#             detail="Transaction list cannot be empty.",
#         )

#     results = []

#     for transaction in transactions:

#         try:

#             results.append(
#                 run_prediction(
#                     transaction
#                 )
#             )

#         except HTTPException as exc:

#             results.append(
#                 {
#                     "transaction_id":
#                         transaction.get(
#                             "TransactionID"
#                         ),

#                     "error":
#                         exc.detail,
#                 }
#             )

#         except Exception as exc:

#             results.append(
#                 {
#                     "transaction_id":
#                         transaction.get(
#                             "TransactionID"
#                         ),

#                     "error":
#                         (
#                             f"{type(exc).__name__}: "
#                             f"{exc}"
#                         ),
#                 }
#             )

#     return {
#         "count": len(results),
#         "results": results,
#     }


# # ============================================================
# # COPILOT CHAT
# # ============================================================

# @app.post("/copilot/chat")
# def copilot_chat(
#     request: CopilotRequest
# ):

#     if ask_copilot is None:

#         raise HTTPException(
#             status_code=503,
#             detail=(
#                 "PayGuard Copilot is unavailable because "
#                 "src.copilot could not be imported."
#             ),
#         )

#     try:

#         answer = ask_copilot(
#             question=request.question,
#             context=request.context,
#         )

#         return {
#             "answer": answer
#         }

#     except Exception as exc:

#         raise HTTPException(
#             status_code=500,
#             detail=(
#                 f"Copilot request failed: "
#                 f"{type(exc).__name__}: {exc}"
#             ),
#         ) from exc





from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ============================================================
# PROJECT ROOT
# ============================================================

# This file is:
# D:\PayGuard-AI\app\api.py
#
# Therefore:
# parent      = D:\PayGuard-AI\app
# parent.parent = D:\PayGuard-AI

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PAYGUARD IMPORTS
# ============================================================

try:
    from src.predict import PayGuardModel
except Exception as exc:
    raise RuntimeError(
        f"Could not import PayGuardModel: "
        f"{type(exc).__name__}: {exc}"
    ) from exc


try:
    from src.copilot import ask_copilot
except Exception:
    ask_copilot = None


try:
    from services.risk_engine import (
        evaluate_risk,
        ALLOW_MAX,
        REVIEW_MAX,
        VERIFY_MAX,
    )
except Exception:

    ALLOW_MAX = 0.60
    REVIEW_MAX = 0.80
    VERIFY_MAX = 0.90

    class FallbackRisk:
        def __init__(
            self,
            probability,
            risk_level,
            decision,
            reason,
        ):
            self.probability = probability
            self.risk_level = risk_level
            self.decision = decision
            self.reason = reason

    def evaluate_risk(probability):

        probability = float(probability)

        probability = max(
            0.0,
            min(probability, 1.0)
        )

        if probability < 0.50:
            risk_level = "LOW"
        elif probability < 0.80:
            risk_level = "MEDIUM"
        elif probability < 0.90:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        if probability < 0.60:

            decision = "ALLOW"

            reason = (
                "Fraud probability is below 60%. "
                "Routine processing is appropriate."
            )

        elif probability < 0.80:

            decision = "REVIEW"

            reason = (
                "Fraud probability is between 60% and 80%. "
                "Manual review is recommended."
            )

        elif probability < 0.90:

            decision = "VERIFY"

            reason = (
                "Fraud probability is between 80% and 90%. "
                "Strong verification is recommended."
            )

        else:

            decision = "BLOCK"

            reason = (
                "Fraud probability is 90% or higher. "
                "Blocking and investigation are recommended."
            )

        return FallbackRisk(
            probability,
            risk_level,
            decision,
            reason,
        )


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="PayGuard AI Risk API",
    description=(
        "PayGuard AI payment fraud detection "
        "and risk assessment API."
    ),
    version="2.0.0",
)


# ============================================================
# MODEL
# ============================================================

try:

    model = PayGuardModel()

except Exception as exc:

    raise RuntimeError(
        f"PayGuard model could not be loaded: "
        f"{type(exc).__name__}: {exc}"
    ) from exc


# ============================================================
# TRANSACTION MODEL
# ============================================================

class Transaction(BaseModel):

    TransactionID: int = 0

    TransactionDT: int = 0

    TransactionAmt: float = 0.0

    ProductCD: str = "W"

    card1: float | None = None
    card2: float | None = None
    card3: float | None = None
    card4: str | None = None
    card5: float | None = None
    card6: float | None = None

    addr1: float | None = None
    addr2: float | None = None

    dist1: float | None = None
    dist2: float | None = None

    P_emaildomain: str | None = None
    R_emaildomain: str | None = None

    DeviceType: str | None = None
    DeviceInfo: str | None = None


class FullTransaction(BaseModel):

    data: dict = {}


class CopilotRequest(BaseModel):

    question: str

    context: str = ""


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "application": "PayGuard AI",
        "status": "online",
        "model": "CatBoost",
        "purpose": "Payment Fraud Detection",
        "api_version": "2.0.0",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": True,
        "model": "CatBoost",
        "features": len(
            getattr(
                model,
                "features",
                []
            )
        ),
        "categorical_features": len(
            getattr(
                model,
                "categorical_features",
                []
            )
        ),
    }


# ============================================================
# MODEL INFO
# ============================================================

@app.get("/model-info")
def model_info():

    return {
        "model": "CatBoost",

        "features": len(
            getattr(
                model,
                "features",
                []
            )
        ),

        "categorical_features": len(
            getattr(
                model,
                "categorical_features",
                []
            )
        ),

        "stored_training_threshold": getattr(
            model,
            "threshold",
            None
        ),

        "decision_policy": {
            "below_60_percent": "ALLOW",
            "60_to_below_80_percent": "REVIEW",
            "80_to_below_90_percent": "VERIFY",
            "90_percent_or_higher": "BLOCK",
        },

        "risk_policy": {
            "below_50_percent": "LOW",
            "50_to_below_80_percent": "MEDIUM",
            "80_to_below_90_percent": "HIGH",
            "90_percent_or_higher": "CRITICAL",
        },
    }


# ============================================================
# PREDICTION HELPER
# ============================================================

def run_prediction(
    transaction_data: dict
):

    try:

        probability_result = (
            model.predict_probability(
                transaction_data
            )
        )

        if probability_result is None:
            raise RuntimeError(
                "Model returned no probability."
            )

        probability = float(
            probability_result[0]
        )

        risk = evaluate_risk(
            probability
        )

        return {
            "transaction_id":
                transaction_data.get(
                    "TransactionID"
                ),

            "fraud_probability":
                probability,

            "fraud_probability_percent":
                probability * 100.0,

            "risk_score":
                probability * 100.0,

            "risk_level":
                risk.risk_level,

            "decision":
                risk.decision,

            "reason":
                risk.reason,

            "model":
                "CatBoost",
        }

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Prediction failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        ) from exc


# ============================================================
# PREDICT
# ============================================================

@app.post("/predict")
def predict(
    transaction: Transaction
):

    transaction_data = (
        transaction.model_dump()
    )

    result = run_prediction(
        transaction_data
    )

    return {
        "transaction_id":
            transaction.TransactionID,

        "prediction":
            result,
    }


# ============================================================
# FULL RISK
# ============================================================

@app.post("/risk")
def risk_prediction(
    request: FullTransaction
):

    if not request.data:

        raise HTTPException(
            status_code=400,
            detail="Transaction data cannot be empty.",
        )

    return run_prediction(
        request.data
    )


# ============================================================
# BATCH
# ============================================================

@app.post("/batch")
def batch_prediction(
    transactions: list[dict]
):

    if not transactions:

        raise HTTPException(
            status_code=400,
            detail="Transaction list cannot be empty.",
        )

    results = []

    for transaction in transactions:

        try:

            result = run_prediction(
                transaction
            )

            results.append(
                result
            )

        except Exception as exc:

            results.append(
                {
                    "transaction_id":
                        transaction.get(
                            "TransactionID"
                        ),

                    "error":
                        str(exc),
                }
            )

    return {
        "count": len(results),
        "results": results,
    }


# ============================================================
# COPILOT
# ============================================================

@app.post("/copilot/chat")
def copilot_chat(
    request: CopilotRequest
):

    if ask_copilot is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "PayGuard Copilot is unavailable."
            ),
        )

    try:

        answer = ask_copilot(
            question=request.question,
            context=request.context,
        )

        return {
            "answer": answer
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Copilot request failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        ) from exc