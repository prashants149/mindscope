# MindScope: AI-Based Analysis of Causes and Effects of Youth Mental Health Issues

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)](#)
[![Tests: 48 Passed](https://img.shields.io/badge/Tests-48%20Passed-success.svg)](#)
[![Coverage: 76%](https://img.shields.io/badge/Coverage-76%25-brightgreen.svg)](#)
[![Phases: 8/8 Complete](https://img.shields.io/badge/Phases-8%2F8%20Complete-blue.svg)](#phases-overview)
[![ROC-AUC: 0.9744](https://img.shields.io/badge/ROC--AUC-0.9744-orange.svg)](#ml-results)
[![Fairness: PASSED](https://img.shields.io/badge/Fairness%20Audit-PASSED-brightgreen.svg)](#fairness)

> ### ⚠️ Mandatory Ethical & Medical Disclaimer
> **MindScope is strictly an academic research and educational decision-support prototype for youth aged 15–25.**
> It is **NOT** a clinical diagnostic instrument and does **NOT** provide medical diagnoses, psychiatric evaluations, or treatment plans.
> If you or someone you know is in emotional crisis or experiencing thoughts of self-harm:
> - **India Tele-MANAS:** Call **14416** or **1800-891-4416** (24/7 Toll-Free, Government of India)
> - **National Emergency Services:** Call **112**
> - **KIRAN Mental Health Helpline:** Call **1800-599-0019**
> - **Vandrevala Foundation:** **+91 9999 666 555**

---

## 🎓 Academic Capstone Project Details

| Field | Details |
|---|---|
| **Project Title** | **MindScope: Youth Mental Health XAI System** |
| **Domain** | Affective Computing, Explainable AI (XAI), & Causal Inference |
| **Target Cohort** | Youth & College Students (Ages 15–25) |
| **Tech Stack** | Python 3.13, FastAPI, Scikit-learn, DoWhy, EconML, SHAP, ChromaDB, Next.js 14, TypeScript |
| **Interview & Thesis Guide** | [MindScope_Project_Interview_Preparation.pdf](MindScope_Project_Interview_Preparation.pdf) |
| **Comprehensive Thesis Report** | [docs/REPORT.md](docs/REPORT.md) (841 lines) |

---

## Overview

MindScope is an explainable AI and causal inference research platform investigating the causes and downstream effects of mental health stressors (academic pressure, sleep deprivation, screen time, financial burden, social support) on youth depression, anxiety, attendance rates, and CGPA across ages 15–25.

All 8 project phases are complete, validated with **48 passing tests** and **76% code coverage**.

### Core Capabilities

| # | Capability | Technology |
|---|---|---|
| 1 | **Predictive Analytics** | Logistic Regression, Random Forest, XGBoost — MLflow tracked |
| 2 | **Explainable AI** | SHAP global attributions + local waterfall explanations |
| 3 | **Causal Inference Engine** | DoWhy / EconML Structural Causal Models, ATE estimation, refutation |
| 4 | **Affective NLP** | TF-IDF Emotion Classifier + BERTopic thematic clustering |
| 5 | **Safe Support Assistant** | RAG assistant (WHO/NIMH/Tele-MANAS corpus) with crisis safeguard filters |
| 6 | **REST API** | FastAPI backend with 6 endpoints |
| 7 | **Interactive Frontend** | Next.js 14 App Router, TypeScript, Tailwind CSS, Recharts |
| 8 | **Algorithmic Fairness Audit** | Four-Fifths Rule — gender & age demographic parity verified |

---

## Phases Overview

| Phase | Name | Status | Key Artifact |
|-------|------|--------|-------------|
| 1 | Data Generation & Validation | ✅ Complete | `data/processed/students_clean.csv` (3,000 rows) |
| 2 | Exploratory Data Analysis | ✅ Complete | `reports/figures/` (4 publication-quality plots) |
| 3 | ML Model Training | ✅ Complete | `models/best_depression_classifier.joblib` |
| 4 | Causal Inference | ✅ Complete | `reports/causal_results.json` |
| 5 | Explainability (SHAP) | ✅ Complete | `reports/shap_summary.json` |
| 6 | Safe Support Assistant | ✅ Complete | `src/assistant/safe_agent.py` |
| 7 | FastAPI Backend + Next.js Frontend | ✅ Complete | `src/api/app.py`, `web/` |
| 8 | Quality, Fairness & Docs | ✅ Complete | `reports/fairness_audit_results.json`, `docs/REPORT.md` |

---

## ML Results

| Metric | Value |
|--------|-------|
| ROC-AUC | **0.9744** |
| Brier Score | 0.0643 |
| Recall (TPR) | 0.905 |
| Best Model | Calibrated Logistic Regression |

## Fairness

| Dimension | Metric | Value | Threshold | Status |
|-----------|--------|-------|-----------|--------|
| Gender | Demographic Parity Ratio | 0.9393 | ≥ 0.80 | ✅ PASS |
| Gender | Equal Opportunity Ratio | 0.9601 | ≥ 0.80 | ✅ PASS |
| Age Group | Demographic Parity Ratio | 0.9945 | ≥ 0.80 | ✅ PASS |
| Age Group | Equal Opportunity Ratio | 0.9872 | ≥ 0.80 | ✅ PASS |
| **Overall** | **Fairness Verdict** | — | — | ✅ **PASSED** |

---

## Quickstart

### Prerequisites
- Python 3.11+ (Anaconda recommended)
- Node.js 18+ / npm
- Git

### Backend Setup

```bash
# 1. Clone and enter project
git clone https://github.com/example/mindscope.git
cd mindscope

# 2. Create and activate Python virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install core dependencies
pip install -r requirements.txt

# 4. Generate synthetic benchmark data and validate
python scripts/generate_and_validate.py

# 5. Train models (saves best model to models/)
python src/models/train.py

# 6. Build ChromaDB vector store for the assistant
python -c "from src.assistant.vector_store import MindScopeVectorStore; MindScopeVectorStore().build_store()"

# 7. Start FastAPI backend
uvicorn src.api.app:app --reload --port 8000
```

### Frontend Setup

```bash
# From project root
cd web
npm install
npm run dev
# Open http://localhost:3000
```

### Run Full Test Suite

```bash
# From project root (activate venv first)
pytest tests/ -v --cov=src --cov-report=term-missing
```

Expected: **48 passed**, coverage ≥ 70%.

---

## Docker Compose (Optional)

```bash
docker compose up --build
# API:      http://localhost:8000
# Frontend: http://localhost:3000
# Docs:     http://localhost:8000/docs
```

> **Note:** Docker Compose configuration is provided in `docker-compose.yml`. Requires Docker Desktop ≥ 24.

---

## CI/CD

GitHub Actions workflow at [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and pull request:

1. **Backend Tests** — `pytest tests/ --cov=src` (fails if coverage < 70%)
2. **Fairness Audit** — `python src/fairness/audit.py`
3. **Frontend Build** — `npm run build` (verifies TypeScript compilation)

---

## API Reference

FastAPI auto-docs available at `http://localhost:8000/docs` (Swagger UI) and `/redoc`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/predict` | POST | Depression risk prediction (returns probability + label) |
| `/explain` | POST | SHAP feature attributions for a student profile |
| `/whatif` | POST | Causal counterfactual simulation |
| `/analyze-text` | POST | Emotion + theme NLP analysis |
| `/assistant` | POST | RAG-based safe support assistant |

---

## Repository Structure

```
mindscope/
├── .github/
│   └── workflows/
│       └── ci.yml                   # GitHub Actions CI pipeline
├── data/
│   ├── guidance_corpus/             # WHO/NIMH/Tele-MANAS documents for RAG
│   ├── processed/                   # Cleaned, validated dataset (3,000 rows)
│   └── chroma_db/                   # ChromaDB persistent vector store
├── docs/
│   ├── PLAN.md                      # Research architecture & roadmap
│   └── REPORT.md                    # Full capstone thesis report
├── models/
│   └── best_depression_classifier.joblib  # Calibrated Logistic Regression
├── reports/
│   ├── figures/                     # EDA plots (4 publication-quality)
│   ├── causal_results.json          # Causal ATE estimates
│   ├── fairness_audit_results.json  # Algorithmic fairness audit
│   ├── shap_summary.json            # SHAP global feature rankings
│   └── assistant_test_results.json  # 32-prompt red-team audit (100% pass)
├── src/
│   ├── api/
│   │   ├── app.py                   # FastAPI application (6 endpoints)
│   │   └── schemas.py               # Pydantic v2 request/response models
│   ├── assistant/
│   │   ├── safe_agent.py            # RAG assistant with crisis interception
│   │   └── vector_store.py          # ChromaDB search interface
│   ├── causal/
│   │   ├── graph.py                 # DoWhy DAG definition
│   │   ├── estimator.py             # ATE estimation + refutation
│   │   ├── subgroups.py             # Subgroup heterogeneity analysis
│   │   └── whatif.py               # Counterfactual simulator
│   ├── data/
│   │   ├── generator.py             # SCM-informed synthetic data generator
│   │   ├── cleaner.py               # Imputation & outlier capping
│   │   └── validator.py             # Pydantic schema enforcement
│   ├── explainability/
│   │   ├── explainer.py             # MindScopeExplainer (SHAP)
│   │   └── visualizer.py            # SHAP waterfall renderer
│   ├── fairness/
│   │   └── audit.py                 # Algorithmic fairness audit (Four-Fifths)
│   ├── models/
│   │   ├── pipeline.py              # Sklearn ColumnTransformer pipeline
│   │   └── train.py                 # 3-model training with MLflow tracking
│   ├── nlp/
│   │   ├── crisis_safeguard.py      # Deterministic crisis keyword detector
│   │   ├── emotion_classifier.py    # TF-IDF + LR emotion classifier
│   │   └── topic_model.py           # BERTopic thematic extractor
│   ├── utils/
│   │   └── constants.py             # Helplines, seed, safety disclaimers
│   └── visualization/
│       └── eda.py                   # EDA figures (matplotlib/seaborn)
├── tests/                           # 48 tests across 8 modules
├── web/                             # Next.js 14 frontend
│   └── src/
│       ├── app/                     # App Router pages (7 pages)
│       ├── components/              # Navbar, DisclaimerBanner
│       └── lib/
│           └── api.ts               # Typed API client
├── Dockerfile.api                   # Python 3.11 slim + uvicorn
├── Dockerfile.web                   # Node 20 Alpine multi-stage
├── docker-compose.yml               # Orchestrates api + web services
└── requirements.txt
```

---

## Verified Helplines (India)

> These helplines are embedded in every API response, assistant interaction, and frontend page.

| Service | Number | Hours |
|---------|--------|-------|
| **Tele-MANAS** | `14416` / `1800-891-4416` | 24×7 Toll-Free |
| **National Emergency** | `112` | 24×7 |
| **KIRAN Helpline** | `1800-599-0019` | 24×7 Toll-Free |
| **Vandrevala Foundation** | `+91 9999 666 555` | 24×7 |
| **NIMHANS** | `080-46110007` | Mon–Sat |

---

## Ethical Commitments

1. **Non-Diagnostic:** The system never produces clinical diagnoses or treatment prescriptions.
2. **Crisis-First Safety:** All crisis keywords trigger immediate deterministic redirection to Tele-MANAS before any AI response.
3. **Synthetic Data Only:** No real patient records; all 3,000 students are synthetically generated via a Structural Causal Model.
4. **Age-Scoped:** Restricted to ages 15–25 per project mandate.
5. **Transparent Uncertainty:** Every prediction surface includes calibration confidence and epistemic guardrails.
6. **Algorithmic Fairness:** Gender and age-group parity verified via Four-Fifths Rule (all ratios ≥ 0.80).
7. **Open Audit Trail:** All test results, SHAP values, causal estimates, and fairness metrics saved in `reports/`.

---

## License

Apache 2.0 — See [LICENSE](LICENSE).

---

## Citation

```bibtex
@misc{mindscope2026,
  title  = {MindScope: AI-Based Analysis of Causes and Effects of Youth Mental Health Issues (Ages 15–25)},
  year   = {2026},
  note   = {Academic capstone research prototype. NOT a clinical tool.}
}
```
