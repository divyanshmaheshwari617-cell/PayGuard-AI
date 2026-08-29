from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier


class PayGuardModel:
    """
    PayGuard AI prediction wrapper.

    IMPORTANT:
    This reproduces the preprocessing used in
    notebooks/02_fraud_model.ipynb.

    Model:
        models/payguard_fraud_catboost.cbm

    Config:
        models/payguard_model_config.json

    Preprocessing:
        models/payguard_preprocessing.joblib
    """

    BASE_DIR = Path(__file__).resolve().parent.parent

    MODEL_PATH = BASE_DIR / "models" / "payguard_fraud_catboost.cbm"
    CONFIG_PATH = BASE_DIR / "models" / "payguard_model_config.json"
    ARTIFACT_PATH = BASE_DIR / "models" / "payguard_preprocessing.joblib"

    MISSING_VALUE = "__MISSING__"

    def __init__(self):

        # ---------------------------------------------------------
        # Check files
        # ---------------------------------------------------------

        if not self.MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found:\n{self.MODEL_PATH}"
            )

        if not self.ARTIFACT_PATH.exists():
            raise FileNotFoundError(
                f"""
Preprocessing artifact not found:

{self.ARTIFACT_PATH}

This file was created by the training notebook.

Please make sure:
D:\\PayGuard-AI\\models\\payguard_preprocessing.joblib

exists.
"""
            )

        # ---------------------------------------------------------
        # Load CatBoost model
        # ---------------------------------------------------------

        self.model = CatBoostClassifier()

        try:
            self.model.load_model(str(self.MODEL_PATH))
        except Exception as exc:
            raise RuntimeError(
                f"""
Could not load CatBoost model:

{self.MODEL_PATH}

Original error:
{type(exc).__name__}: {exc}
"""
            ) from exc

        # ---------------------------------------------------------
        # Load preprocessing artifacts
        # ---------------------------------------------------------

        try:
            self.preprocessing = joblib.load(
                self.ARTIFACT_PATH
            )
        except Exception as exc:
            raise RuntimeError(
                f"""
Could not load preprocessing artifact:

{self.ARTIFACT_PATH}

Original error:
{type(exc).__name__}: {exc}
"""
            ) from exc

        # ---------------------------------------------------------
        # Load model configuration
        # ---------------------------------------------------------

        self.config = {}

        if self.CONFIG_PATH.exists():
            try:
                with open(
                    self.CONFIG_PATH,
                    "r",
                    encoding="utf-8"
                ) as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}

        # ---------------------------------------------------------
        # IMPORTANT:
        # These values come from the ORIGINAL TRAINING NOTEBOOK.
        # ---------------------------------------------------------

        self.features = list(
            self.preprocessing.get(
                "feature_columns",
                []
            )
        )

        self.categorical_features = list(
            self.preprocessing.get(
                "categorical_features",
                []
            )
        )

        self.frequency_maps = self.preprocessing.get(
            "frequency_maps",
            {}
        )

        self.amount_stats = self.preprocessing.get(
            "amount_stats",
            None
        )

        self.threshold = float(
            self.preprocessing.get(
                "threshold",
                self.config.get(
                    "threshold",
                    0.864575
                )
            )
        )

        # ---------------------------------------------------------
        # Safety check
        # ---------------------------------------------------------

        if not self.features:
            try:
                self.features = list(
                    self.model.feature_names_
                )
            except Exception:
                pass

        if not self.features:
            raise RuntimeError(
                "No model feature list was found."
            )

        # CatBoost's own feature names are the final authority
        # for column order if available.
        try:
            model_features = list(
                self.model.feature_names_
            )

            if model_features:
                self.features = model_features

        except Exception:
            pass

        # ---------------------------------------------------------
        # Information
        # ---------------------------------------------------------

        print("MODEL LOADED SUCCESSFULLY")
        print("Model:", self.MODEL_PATH)
        print("Threshold:", self.threshold)
        print("Features:", len(self.features))
        print(
            "Categorical:",
            len(self.categorical_features)
        )

    # =============================================================
    # HELPER
    # =============================================================

    @staticmethod
    def _safe_string(series):
        """
        Same logic as safe_str() in the notebook.
        """

        return (
            series
            .fillna("__MISSING__")
            .astype(str)
        )

    # =============================================================
    # PREPROCESSING
    # =============================================================

    def _prepare_dataframe(self, data):

        # ---------------------------------------------------------
        # Convert input to DataFrame
        # ---------------------------------------------------------

        if isinstance(data, dict):

            df = pd.DataFrame([data])

        elif isinstance(data, pd.Series):

            df = data.to_frame().T

        elif isinstance(data, pd.DataFrame):

            df = data.copy()

        else:

            raise TypeError(
                "Input must be a dictionary, pandas Series, "
                "or pandas DataFrame."
            )

        # ---------------------------------------------------------
        # Make sure original columns exist
        # ---------------------------------------------------------

        original_columns = [
            "TransactionID",
            "TransactionDT",
            "TransactionAmt",
            "ProductCD",

            "card1",
            "card2",
            "card3",
            "card4",
            "card5",
            "card6",

            "addr1",
            "addr2",

            "P_emaildomain",
            "R_emaildomain",

            "DeviceType",
            "DeviceInfo",
        ]

        for column in original_columns:

            if column not in df.columns:

                df[column] = np.nan

        # =========================================================
        # SAME FEATURE ENGINEERING AS NOTEBOOK
        # =========================================================

        # ---------------------------------------------------------
        # Transaction time
        # ---------------------------------------------------------

        SECONDS_PER_DAY = 86400

        transaction_dt = pd.to_numeric(
            df["TransactionDT"],
            errors="coerce"
        )

        df["transaction_day"] = (
            transaction_dt // SECONDS_PER_DAY
        )

        df["transaction_hour"] = (
            (transaction_dt % SECONDS_PER_DAY)
            // 3600
        )

        df["transaction_dow"] = (
            df["transaction_day"] % 7
        )

        # ---------------------------------------------------------
        # Amount features
        # ---------------------------------------------------------

        transaction_amount = pd.to_numeric(
            df["TransactionAmt"],
            errors="coerce"
        )

        df["amount_log"] = np.log1p(
            transaction_amount
        )

        df["amount_cents"] = (
            np.round(
                transaction_amount * 100
            )
            .astype("Int64")
            % 100
        )

        df["amount_is_round"] = (
            df["amount_cents"] == 0
        ).astype("int8")

        # ---------------------------------------------------------
        # Identity missing
        # ---------------------------------------------------------

        df["identity_missing"] = (
            df["DeviceType"].isna()
        ).astype("int8")

        # ---------------------------------------------------------
        # Email match
        # ---------------------------------------------------------

        p_email = (
            df["P_emaildomain"]
            .fillna("__MISSING__")
        )

        r_email = (
            df["R_emaildomain"]
            .fillna("__MISSING__")
        )

        df["email_match"] = (
            p_email == r_email
        ).astype("int8")

        # ---------------------------------------------------------
        # Card key
        # ---------------------------------------------------------

        df["card_key"] = (
            self._safe_string(df["card1"])
            + "_"
            + self._safe_string(df["card2"])
            + "_"
            + self._safe_string(df["card3"])
            + "_"
            + self._safe_string(df["card4"])
            + "_"
            + self._safe_string(df["card5"])
            + "_"
            + self._safe_string(df["card6"])
        )

        # ---------------------------------------------------------
        # Card + address key
        # ---------------------------------------------------------

        df["card_addr_key"] = (
            self._safe_string(df["card1"])
            + "_"
            + self._safe_string(df["addr1"])
        )

        # ---------------------------------------------------------
        # Card + device key
        # ---------------------------------------------------------

        df["card_device_key"] = (
            self._safe_string(df["card1"])
            + "_"
            + self._safe_string(df["DeviceInfo"])
        )

        # ---------------------------------------------------------
        # User key
        # ---------------------------------------------------------

        df["user_key"] = (
            self._safe_string(df["card1"])
            + "_"
            + self._safe_string(df["card2"])
            + "_"
            + self._safe_string(df["addr1"])
            + "_"
            + self._safe_string(df["P_emaildomain"])
        )

        # =========================================================
        # FREQUENCY FEATURES
        # SAME AS NOTEBOOK
        # =========================================================

        frequency_columns = [
            "card1",
            "card2",
            "card_addr_key",
            "card_device_key",
            "user_key",
            "P_emaildomain",
            "DeviceInfo",
        ]

        for column in frequency_columns:

            feature_name = f"{column}_freq"

            frequency_map = (
                self.frequency_maps.get(column)
            )

            if frequency_map is None:

                df[feature_name] = 0.0

            else:

                df[feature_name] = (
                    df[column]
                    .map(frequency_map)
                    .fillna(0)
                    .astype("float32")
                )

        # =========================================================
        # AMOUNT STATISTICS
        # SAME AS NOTEBOOK
        # =========================================================

        df["card_amount_mean"] = np.nan
        df["card_amount_std"] = np.nan

        if self.amount_stats is not None:

            try:

                amount_stats = self.amount_stats.copy()

                # amount_stats is indexed by card1
                if "card1" in amount_stats.index.names:

                    mean_map = (
                        amount_stats[
                            "card_amount_mean"
                        ]
                    )

                    std_map = (
                        amount_stats[
                            "card_amount_std"
                        ]
                    )

                    df["card_amount_mean"] = (
                        df["card1"]
                        .map(mean_map)
                    )

                    df["card_amount_std"] = (
                        df["card1"]
                        .map(std_map)
                    )

                else:

                    # Fallback if index name was not preserved
                    amount_stats = (
                        amount_stats.reset_index()
                    )

                    if "card1" in amount_stats.columns:

                        df["card_amount_mean"] = (
                            df["card1"]
                            .map(
                                amount_stats.set_index(
                                    "card1"
                                )[
                                    "card_amount_mean"
                                ]
                            )
                        )

                        df["card_amount_std"] = (
                            df["card1"]
                            .map(
                                amount_stats.set_index(
                                    "card1"
                                )[
                                    "card_amount_std"
                                ]
                            )
                        )

            except Exception:
                pass

        # ---------------------------------------------------------
        # Amount vs card mean
        # ---------------------------------------------------------

        df["amount_vs_card_mean"] = (
            transaction_amount
            /
            df["card_amount_mean"].replace(
                0,
                np.nan
            )
        )

        # =========================================================
        # MAKE ALL MODEL FEATURES AVAILABLE
        # =========================================================

        for column in self.features:

            if column not in df.columns:

                df[column] = np.nan

        # ---------------------------------------------------------
        # Exact feature order from trained model
        # ---------------------------------------------------------

        df = df[
            self.features
        ].copy()

        # =========================================================
        # CATEGORICAL PREPROCESSING
        #
        # THIS FIXES YOUR CURRENT CATBOOST ERROR:
        #
        # "cat_features ... nan ... must be converted to string"
        # =========================================================

        for column in self.categorical_features:

            if column not in df.columns:
                continue

            df[column] = (
                df[column]
                .fillna("__MISSING__")
                .astype(str)
            )

        # =========================================================
        # NUMERIC PREPROCESSING
        # =========================================================

        for column in self.features:

            if column in self.categorical_features:
                continue

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        return df

    # =============================================================
    # PREDICT PROBABILITY
    # =============================================================

    def predict_probability(self, data):

        df = self._prepare_dataframe(data)

        probabilities = self.model.predict_proba(
            df
        )

        # CatBoost binary classifier:
        # column 0 = legitimate
        # column 1 = fraud

        return probabilities[:, 1]

    # =============================================================
    # SINGLE PREDICTION
    # =============================================================

    def predict(self, data):

        probability = float(
            self.predict_probability(data)[0]
        )

        risk_score = (
            probability * 100.0
        )

        # ---------------------------------------------------------
        # IMPORTANT:
        # Risk levels reproduce the notebook:
        #
        # >= 80  HIGH
        # >= 50  MEDIUM
        # < 50   LOW
        # ---------------------------------------------------------

        if risk_score >= 80:

            risk_level = "HIGH"

        elif risk_score >= 50:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        # ---------------------------------------------------------
        # Fraud decision uses the ORIGINAL BEST THRESHOLD
        # 0.864575
        # ---------------------------------------------------------

        if probability >= self.threshold:

            decision = "BLOCK"

        else:

            decision = "ALLOW"

        return {
            "fraud_probability": probability,

            "fraud_probability_percent":
                probability * 100.0,

            "risk_score":
                round(risk_score, 2),

            "risk_level":
                risk_level,

            "decision":
                decision,

            "threshold":
                self.threshold,
        }

    # =============================================================
    # BATCH PREDICTION
    # =============================================================

    def predict_batch(self, data):

        if not isinstance(data, pd.DataFrame):

            raise TypeError(
                "predict_batch() requires a pandas DataFrame."
            )

        probabilities = (
            self.predict_probability(data)
        )

        output = data.copy()

        output[
            "fraud_probability"
        ] = probabilities

        output[
            "fraud_probability_percent"
        ] = probabilities * 100.0

        output[
            "risk_score"
        ] = (
            probabilities * 100.0
        ).round(2)

        output[
            "risk_level"
        ] = np.select(
            [
                output["risk_score"] >= 80,
                output["risk_score"] >= 50,
            ],
            [
                "HIGH",
                "MEDIUM",
            ],
            default="LOW"
        )

        output[
            "decision"
        ] = np.where(
            probabilities >= self.threshold,
            "BLOCK",
            "ALLOW"
        )

        return output