# 🛡️ PayGuard AI

### AI-Powered Payment Fraud Detection & Risk Operations Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://payguard-ai-eqnjmsd9mjxz8ggmdw5uc9.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![CatBoost](https://img.shields.io/badge/ML-CatBoost-yellow)](https://catboost.ai/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-blue)](https://ai.google.dev/)

**PayGuard AI** is an AI-powered payment risk operations platform designed to detect suspicious transactions, prioritize investigations, uncover fraud relationships, support human analysts with AI, and maintain an auditable risk-decision workflow.

Built for the **Razorpay AI Buildathon 2026 — Track 02: AI Risk Manager**.

## 🚀 Live Demo

### 👉 [Launch PayGuard AI](https://payguard-ai-eqnjmsd9mjxz8ggmdw5uc9.streamlit.app/)

The application is deployed on **Streamlit Community Cloud** directly from this GitHub repository.

> The deployed application uses authentication. First-time environments may require initial administrator setup.

---

## 🖥️ PayGuard AI Dashboard

![PayGuard AI Dashboard](docs/screenshots/01-dashboard.png)

PayGuard AI brings transaction scoring, fraud investigation, operational prioritization, network intelligence, risk economics, monitoring, AI-assisted analysis, and auditability into one interface.

---

## 🎯 The Problem

Payment fraud detection is not only a classification problem.

A fraud model can generate a probability, but a risk team still needs to answer:

- How risky is this transaction?
- Should it be allowed, reviewed, verified, or blocked?
- Which transactions should analysts investigate first?
- Are suspicious transactions connected?
- What is the operational cost of false positives?
- Why did a transaction receive a high-risk score?
- What decision did the human analyst ultimately make?
- Can investigation decisions be reviewed later?

**PayGuard AI turns fraud predictions into an operational risk-management workflow.**

---

## 💡 Solution

PayGuard combines machine learning, deterministic risk policies, analytics, fraud-network intelligence, human investigation workflows, and Gemini-powered assistance.

The core workflow is:

```text
Transaction
    ↓
Fraud Probability
    ↓
Risk Classification
    ↓
Operational Decision
    ↓
Investigation Prioritization
    ↓
Human + AI Investigation
    ↓
Analyst Outcome
    ↓
Audit Trail