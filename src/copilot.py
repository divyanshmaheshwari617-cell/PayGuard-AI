"""
PayGuard AI Copilot
-------------------

Gemini-powered AI assistant for PayGuard.

This module is intentionally independent of Streamlit so that it can be
imported safely by FastAPI/Uvicorn.

Secrets are loaded from:

    .streamlit/secrets.toml

Expected secrets.toml:

    GEMINI_API_KEY = "your-api-key"
    GEMINI_MODEL = "gemini-2.5-flash"

Environment variables can also be used as a fallback.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

# D:\PayGuard-AI\src\copilot.py
# parents[0] = D:\PayGuard-AI\src
# parents[1] = D:\PayGuard-AI
PROJECT_ROOT = Path(__file__).resolve().parents[1]

SECRETS_FILE = PROJECT_ROOT / ".streamlit" / "secrets.toml"


# ============================================================
# LOAD SECRETS
# ============================================================

def _load_secrets() -> dict[str, Any]:
    """
    Load secrets from .streamlit/secrets.toml.

    Environment variables take priority over secrets.toml.
    """

    secrets: dict[str, Any] = {}

    # Load secrets.toml if it exists
    if SECRETS_FILE.exists():
        try:
            with SECRETS_FILE.open("rb") as file:
                secrets = tomllib.load(file)
        except Exception as exc:
            raise RuntimeError(
                f"Could not read secrets file:\n"
                f"{SECRETS_FILE}\n\n"
                f"Error: {exc}"
            ) from exc

    return secrets


_SECRETS = _load_secrets()


def _get_secret(name: str, default: str | None = None) -> str | None:
    """
    Get a configuration value.

    Priority:
        1. Environment variable
        2. secrets.toml
        3. default
    """

    value = os.getenv(name)

    if value:
        return value

    value = _SECRETS.get(name)

    if value is not None:
        return str(value)

    return default


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")

GEMINI_MODEL = _get_secret(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)


# ============================================================
# VALIDATE API KEY
# ============================================================

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found.\n\n"
        f"Please add it to:\n"
        f"{SECRETS_FILE}\n\n"
        "Example:\n"
        'GEMINI_API_KEY = "your-api-key"\n'
        'GEMINI_MODEL = "gemini-2.5-flash"\n'
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

try:
    from google import genai
except ImportError as exc:
    raise RuntimeError(
        "The Google GenAI SDK is not installed.\n\n"
        "Install it with:\n"
        "pip install google-genai"
    ) from exc


try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as exc:
    raise RuntimeError(
        f"Failed to initialize Gemini client: {exc}"
    ) from exc


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are PayGuard AI Copilot, an intelligent assistant for a payment
fraud detection and transaction-risk analysis platform.

Your job is to help investigators, analysts, and developers understand
fraud-risk predictions and transaction behavior.

Important rules:

1. A high-risk prediction does NOT automatically mean a transaction is
   fraudulent.

2. Explain risk as a probability or model assessment, not as a definitive
   accusation.

3. When transaction information is provided, explain the important risk
   factors clearly.

4. Consider factors such as:
   - transaction amount
   - transaction frequency / velocity
   - customer history
   - location
   - IP information
   - device information
   - payment information
   - shipping/billing information
   - unusual behavioral patterns
   - model risk score
   - model threshold

5. If the user asks about a specific transaction but does not provide
   transaction data, clearly say that the transaction data is missing.

6. Do not invent transaction values, model scores, customer information,
   fraud evidence, or investigation results.

7. Give practical investigation recommendations when appropriate.

8. Use clear, professional language suitable for a fraud analyst.

9. If the user asks a general question about PayGuard, explain it simply.

10. Never claim that the machine-learning model is 100% accurate.

11. If information is unavailable, explicitly say that it is unavailable
    rather than guessing.

You are the Copilot layer of PayGuard AI. The CatBoost model performs
the actual machine-learning risk prediction; you explain and contextualize
the results for the user.
""".strip()


# ============================================================
# HELPER: CONVERT INPUT TO TEXT
# ============================================================

def _build_prompt(
    user_message: str,
    transaction: dict[str, Any] | None = None,
    model_result: dict[str, Any] | None = None,
) -> str:
    """
    Build the prompt sent to Gemini.
    """

    parts: list[str] = []

    parts.append(
        "You are assisting with the PayGuard AI fraud detection system."
    )

    parts.append(
        f"\nUser request:\n{user_message.strip()}"
    )

    if transaction:
        parts.append(
            "\nTransaction data:\n"
            + _safe_stringify(transaction)
        )

    if model_result:
        parts.append(
            "\nMachine-learning model result:\n"
            + _safe_stringify(model_result)
        )

    return "\n".join(parts)


def _safe_stringify(value: Any) -> str:
    """
    Convert Python objects into readable text without exposing secrets.
    """

    try:
        import json

        return json.dumps(
            value,
            indent=2,
            default=str,
        )
    except Exception:
        return str(value)


# ============================================================
# MAIN COPILOT FUNCTION
# ============================================================

def ask_copilot(
    message: str,
    transaction: dict[str, Any] | None = None,
    model_result: dict[str, Any] | None = None,
) -> str:
    """
    Send a question to Gemini and return the Copilot response.

    Parameters
    ----------
    message:
        User's question.

    transaction:
        Optional transaction dictionary.

    model_result:
        Optional CatBoost prediction/result dictionary.

    Returns
    -------
    str
        Gemini's response.
    """

    if not message or not message.strip():
        return "Please provide a question or message."

    prompt = _build_prompt(
        message,
        transaction=transaction,
        model_result=model_result,
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                SYSTEM_PROMPT
                                + "\n\n"
                                + prompt
                            )
                        }
                    ],
                }
            ],
        )

        # Gemini response normally exposes .text
        answer = getattr(response, "text", None)

        if answer:
            return answer.strip()

        # Defensive fallback
        if hasattr(response, "candidates"):
            try:
                candidate = response.candidates[0]

                if hasattr(candidate, "content"):
                    content = candidate.content

                    if hasattr(content, "parts"):
                        texts = []

                        for part in content.parts:
                            text = getattr(part, "text", None)

                            if text:
                                texts.append(text)

                        if texts:
                            return "\n".join(texts).strip()

            except Exception:
                pass

        return (
            "I received a response from Gemini, but I could not extract "
            "the response text."
        )

    except Exception as exc:
        error_message = str(exc)

        # Avoid exposing the API key if something unexpectedly includes it.
        if GEMINI_API_KEY:
            error_message = error_message.replace(
                GEMINI_API_KEY,
                "[REDACTED]",
            )

        return (
            "I couldn't generate a Copilot response right now.\n\n"
            f"Gemini error: {error_message}"
        )


# ============================================================
# TRANSACTION ANALYSIS HELPER
# ============================================================

def analyze_transaction(
    transaction: dict[str, Any],
    model_result: dict[str, Any] | None = None,
) -> str:
    """
    Generate an investigator-friendly explanation for a transaction.
    """

    return ask_copilot(
        message=(
            "Analyze this transaction from a fraud-investigation "
            "perspective. Explain the risk level, important risk factors, "
            "what the investigator should verify, and what additional "
            "information would be useful."
        ),
        transaction=transaction,
        model_result=model_result,
    )


# ============================================================
# HEALTH CHECK
# ============================================================

def copilot_health() -> dict[str, Any]:
    """
    Return basic Copilot configuration status.

    Does NOT expose the API key.
    """

    return {
        "status": "ok",
        "provider": "Google Gemini",
        "model": GEMINI_MODEL,
        "secrets_file": str(SECRETS_FILE),
        "secrets_file_exists": SECRETS_FILE.exists(),
        "api_key_configured": bool(GEMINI_API_KEY),
    }


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PayGuard AI Copilot")
    print("=" * 60)

    print("\nConfiguration:")
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Secrets file : {SECRETS_FILE}")
    print(f"Secrets OK   : {SECRETS_FILE.exists()}")
    print(f"Gemini model : {GEMINI_MODEL}")
    print(
        f"API key      : "
        f"{'configured' if GEMINI_API_KEY else 'missing'}"
    )

    print("\nTesting Copilot...\n")

    result = ask_copilot(
        "Hello PayGuard, explain what a high risk transaction means."
    )

    print(result)