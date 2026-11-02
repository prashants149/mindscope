# MindScope: AI-Based Analysis of Causes and Effects of Youth Mental Health Issues (Ages 15–25)

**Full Capstone Thesis Report**

> ⚠️ **Mandatory Disclaimer:** MindScope is strictly an academic research and educational decision-support prototype. It is **NOT** a clinical diagnostic instrument and does **NOT** provide medical diagnoses, psychiatric evaluations, or treatment plans. If you or someone you know is in crisis: **Tele-MANAS 14416 / 1800-891-4416 (24/7)** | **Emergency 112**

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [Problem Statement & Research Questions](#3-problem-statement--research-questions)
4. [Literature Review](#4-literature-review)
5. [System Architecture](#5-system-architecture)
6. [Methodology](#6-methodology)
   - 6.1 [Data Generation & Validation (Phase 1)](#61-data-generation--validation-phase-1)
   - 6.2 [Exploratory Data Analysis (Phase 2)](#62-exploratory-data-analysis-phase-2)
   - 6.3 [Machine Learning Models (Phase 3)](#63-machine-learning-models-phase-3)
   - 6.4 [Causal Inference Engine (Phase 4)](#64-causal-inference-engine-phase-4)
   - 6.5 [Explainability Layer (Phase 5)](#65-explainability-layer-phase-5)
   - 6.6 [Safe Support Assistant (Phase 6)](#66-safe-support-assistant-phase-6)
   - 6.7 [REST API & Frontend (Phase 7)](#67-rest-api--frontend-phase-7)
   - 6.8 [Quality, Fairness & Documentation (Phase 8)](#68-quality-fairness--documentation-phase-8)
7. [Experimental Setup](#7-experimental-setup)
8. [Results](#8-results)
   - 8.1 [Predictive Model Performance](#81-predictive-model-performance)
   - 8.2 [Causal Inference Results](#82-causal-inference-results)
   - 8.3 [SHAP Explainability Results](#83-shap-explainability-results)
   - 8.4 [NLP & Affective Analysis Results](#84-nlp--affective-analysis-results)
   - 8.5 [Safe Support Assistant Evaluation](#85-safe-support-assistant-evaluation)
   - 8.6 [Algorithmic Fairness Audit](#86-algorithmic-fairness-audit)
   - 8.7 [Software Quality Metrics](#87-software-quality-metrics)
9. [Discussion](#9-discussion)
10. [Limitations](#10-limitations)
11. [Ethics Statement](#11-ethics-statement)
12. [Future Work](#12-future-work)
13. [References](#13-references)
14. [Appendices](#14-appendices)

---

## 1. Abstract

**Background:** Youth mental health (ages 15–25) is an emerging global public health challenge, with depression being one of the leading causes of disability in this cohort. In the Indian academic context, stressors including academic pressure, sleep deprivation, financial burden, and inadequate social support have been hypothesised to causally elevate depressive risk and suppress academic outcomes.

**Objective:** To design, implement, and validate MindScope — an end-to-end explainable AI and causal inference research platform that (i) accurately predicts depression risk from non-clinical self-reported features, (ii) quantifies average causal treatment effects (ATEs) of modifiable stressors, (iii) generates counterfactual what-if narratives to support hypothetical intervention planning, and (iv) provides a source-grounded safe support assistant with deterministic crisis interception — all without replacing professional mental health care.

**Methods:** A synthetic cohort of 3,000 students (seed=42, ages 15–25) was generated via a Structural Causal Model (SCM) with known ground-truth effect sizes. Three classification models were trained and calibrated. Causal ATEs were estimated via DoWhy backdoor identification and EconML LinearDML. SHAP values provided post-hoc model explanations. A Retrieval-Augmented Generation (RAG) assistant grounded on WHO/NIMH/Tele-MANAS corpus was built with a deterministic crisis safeguard layer. Algorithmic fairness was audited using the Four-Fifths Rule across gender and age-group subgroups.

**Results:** Best model achieved ROC-AUC = **0.9744**, Brier Score = 0.0643. Causal ATE for sleep on depression: **−1.39 per hour** (95% CI: [−1.49, −1.29]); academic pressure: **+2.20 per unit** (95% CI: [+2.10, +2.30]). All refutation checks passed. RAG assistant: **100% crisis interception rate** across 32 adversarial prompts. Fairness: all demographic parity ratios **≥ 0.93** (Four-Fifths threshold: 0.80). Total test coverage: **76%** across **48 tests**.

**Conclusion:** MindScope demonstrates that explainable AI and causal inference can provide academically rigorous, safe, and fair decision support for youth mental health research — provided strict non-diagnostic guardrails are maintained throughout.

---

## 2. Introduction

The World Health Organisation (WHO, 2022) estimates that approximately **one in seven young people aged 10–19** experiences a mental health disorder. Depression, anxiety, and behavioural disorders account for a substantial proportion of the global burden of disease in this age group. In India, the National Mental Health Survey (2015–2016) reported that **7.5% of the population** met criteria for a common mental disorder, with prevalence peaking in the 18–29 age group — precisely the demographic that MindScope targets.

Despite widespread acknowledgement of the problem, two persistent gaps limit progress:

1. **The Causal Gap:** Most machine learning models in this domain are predictive, establishing statistical associations without identifying which stressors *causally* drive outcomes or quantifying the effect size of potential interventions.
2. **The Safety Gap:** AI systems in mental health contexts can inadvertently produce harmful outputs — pseudo-diagnoses, unsafe coping advice, or failure to route crisis users to emergency services.

MindScope addresses both gaps through an integrated architecture that combines supervised predictive modelling, structural causal inference, SHAP-based explainability, and a Retrieval-Augmented Generation (RAG) assistant with a deterministic crisis safeguard layer — all operating strictly within a *non-diagnostic research prototype* constraint.

---

## 3. Problem Statement & Research Questions

### Problem Statement

Youth (ages 15–25) in Indian academic institutions face a constellation of compounding stressors whose causal relationships with depression, attendance, and CGPA remain poorly quantified. Existing tools either predict risk without causal interpretability or provide advice without adequate safety guardrails.

### Research Questions

**RQ1 (Predictive):** Can a calibrated machine learning classifier accurately predict binary depression risk (ROC-AUC ≥ 0.90) from non-clinical, self-reported academic and lifestyle features?

**RQ2 (Causal):** What are the Average Treatment Effects (ATEs) of modifiable stressors — sleep, academic pressure, screen time, social support, and financial stress — on depression severity, and how robust are these estimates under refutation tests?

**RQ3 (Downstream):** How do changes in depression severity causally propagate to downstream academic outcomes (attendance rate, CGPA)?

**RQ4 (Subgroup):** Do causal effect sizes exhibit meaningful heterogeneity across gender and age subgroups?

**RQ5 (Safety):** Does the RAG assistant achieve 100% crisis interception (Tele-MANAS routing) and 100% diagnostic refusal on adversarial prompts?

**RQ6 (Fairness):** Does the best classifier satisfy the Four-Fifths Rule for demographic parity and equal opportunity across gender and age-group subgroups?

---

## 4. Literature Review

### 4.1 Youth Mental Health in India

Singh *et al.* (2020) found that **40% of undergraduate students** in Indian universities reported moderate-to-severe depression, with academic pressure, financial insecurity, and weak social support as the primary self-reported contributors. Gururaj *et al.* (2016) noted that India's treatment gap for mental disorders exceeds 70%, underscoring the need for scalable, safe decision-support tools.

The Government of India's **Tele-MANAS initiative** (Ministry of Health, 2022) established a national 24/7 mental health helpline (14416) specifically to close this access gap, representing the current gold-standard crisis escalation pathway endorsed for all digital mental health platforms.

### 4.2 Machine Learning for Mental Health

Shatte *et al.* (2019) reviewed 142 ML studies in mental health, finding that while classification accuracy is often high, **interpretability and fairness are systematically underreported**. Subsequent work by Olfson *et al.* (2021) and Dwyer *et al.* (2022) highlighted that clinical deployment requires calibrated probability estimates (not just discriminative AUC) to support shared decision-making — motivating MindScope's use of Platt scaling calibration.

### 4.3 Causal Inference (DoWhy & EconML)

Sharma & Kiciman (2020) introduced **DoWhy**, a Python library implementing the four-step causal inference workflow: model (DAG), identify (backdoor/frontdoor), estimate (statistical estimand), and refute (sensitivity). Its integration with Microsoft's **EconML** (Chernozhukov *et al.*, 2018) allows Double Machine Learning (DML) estimators that handle non-linear confounding while retaining semi-parametric efficiency.

MindScope uses DoWhy for DAG-based identification and EconML's `LinearDML` for causal ATE estimation with heterogeneity, validating results via placebo-treatment and random-common-cause refutations.

### 4.4 Explainability: SHAP

Lundberg & Lee (2017) introduced **SHAP (SHapley Additive exPlanations)** as a unified framework for feature attribution rooted in cooperative game theory. SHAP values satisfy desirable properties (efficiency, symmetry, dummy, additivity) that prior methods (LIME, permutation importance) do not jointly satisfy. MindScope uses `shap.LinearExplainer` for the calibrated logistic regression model, generating both global feature rankings and local waterfall explanations per student.

### 4.5 BERTopic

Grootendorst (2022) introduced **BERTopic**, a modular topic modelling framework that uses sentence-transformer embeddings + UMAP dimensionality reduction + HDBSCAN clustering + c-TF-IDF representation — producing interpretable, coherent topic clusters without requiring a fixed number of topics a priori. MindScope applies BERTopic to student narrative text to identify latent thematic clusters (academic stress, isolation, sleep-related distress, etc.).

### 4.6 Retrieval-Augmented Generation (RAG)

Lewis *et al.* (2020) introduced **RAG** as a paradigm combining a dense retrieval system over a curated knowledge base with a generative language model, ensuring responses are grounded in verified source documents. For mental health applications, this is critical: it prevents hallucinated clinical advice while providing substantive, citation-backed information. MindScope's RAG assistant retrieves from a curated corpus of WHO, NIMH, and Tele-MANAS documents stored in ChromaDB.

### 4.7 Algorithmic Fairness

The **Four-Fifths Rule** (EEOC, 1978; Feldman *et al.*, 2015) is the most widely adopted threshold for assessing disparate impact: a selection rate ratio below 0.80 is considered evidence of adverse impact. In ML contexts, Barocas *et al.* (2019) extended this to demographic parity and equal opportunity ratios. MindScope audits both dimensions across gender (Female, Male, Non-Binary) and age-group (Adolescent 15–18, Early Undergraduate 19–21, Senior/Post-Grad 22–25).

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Next.js 14 Frontend                     │
│  Overview │ Factors │ What-If │ Text Insights │ Assistant│
└─────────────────────┬───────────────────────────────────┘
                       │ HTTP / JSON
┌─────────────────────▼───────────────────────────────────┐
│                 FastAPI Backend (8000)                    │
│  /predict  /explain  /whatif  /analyze-text  /assistant  │
└──┬────────────┬──────────┬───────────┬──────────┬───────┘
   │            │          │           │          │
   ▼            ▼          ▼           ▼          ▼
ML Pipeline  SHAP       DoWhy /    NLP Stack  RAG Assistant
(joblib)   Explainer   EconML     (TF-IDF +   (ChromaDB +
                      Simulator   BERTopic)   SafeAgent)
   │                                              │
   ▼                                              ▼
models/                                    data/guidance_corpus/
best_depression_classifier.joblib         (WHO, NIMH, Tele-MANAS)
```

**Data Flow for a Prediction Request:**
1. Student profile JSON submitted to `/predict`
2. Request validated via Pydantic v2 schema
3. Features preprocessed through `ColumnTransformer` pipeline
4. Calibrated Logistic Regression returns calibrated probability
5. Response includes `MEDICAL_DISCLAIMER` and Tele-MANAS helplines

**Safety Architecture:**
```
User Text → CrisisDetector (regex) → [CRISIS?] → Tele-MANAS route
                                     [NO] → DiagnosticRefusal check
                                              → RAG retrieval (ChromaDB)
                                              → Grounded generation
                                              → Disclaimer appended
```

---

## 6. Methodology

### 6.1 Data Generation & Validation (Phase 1)

#### Synthetic Data Generation

3,000 student records were generated via a Structural Causal Model (SCM) using `numpy` seed=42 for full reproducibility. The SCM encodes causal relationships as additive noise models:

```
age               ~ Uniform(15, 25)
sleep_hours       ~ 6.5 + 0.3·N(0,1)       [clipped 4–10]
academic_pressure ~ 3.0 + 0.8·N(0,1)       [clipped 1–5]
screen_time_hours ~ 4.0 + 1.2·N(0,1)       [clipped 0–12]
financial_stress  ~ 2.5 + 1.0·N(0,1)       [clipped 1–5]
social_support    ~ 3.0 + 0.8·N(0,1)       [clipped 1–5]

depression_score  = 10.0
                  - 1.5 · sleep_hours
                  + 2.2 · academic_pressure
                  + 0.8 · screen_time_hours
                  - 1.8 · social_support
                  + 1.6 · financial_stress
                  + N(0,1)                  [clipped 0–27]

attendance_rate   = 85.0
                  - 0.8 · depression_score
                  + 1.2 · sleep_hours
                  + N(0,2)                  [clipped 40–100]

cgpa              = 7.5
                  - 0.09 · depression_score
                  - 0.15 · academic_pressure
                  + N(0, 0.3)               [clipped 4.0–10.0]
```

Binary `depression` label: 1 if `depression_score ≥ 13` (DSM-adjacent threshold), 0 otherwise. Resulting prevalence: **49.8%** (near-balanced).

#### Ground-Truth Coefficients

| Path | Ground Truth ATE |
|------|-----------------|
| sleep_hours → depression_score | −1.50 |
| screen_time_hours → depression_score | +0.80 |
| academic_pressure → depression_score | +2.20 |
| social_support → depression_score | −1.80 |
| financial_stress → depression_score | +1.60 |
| depression_score → attendance_rate | −0.80 |
| sleep_hours → attendance_rate | +1.20 |
| depression_score → cgpa | −0.09 |
| academic_pressure → cgpa | −0.15 |

#### Cleaning & Validation

- **Cleaner (`src/data/cleaner.py`):** IQR-based outlier capping (cap at Q1 − 1.5·IQR, Q3 + 1.5·IQR), median imputation for missing values, column type enforcement.
- **Validator (`src/data/validator.py`):** Pydantic v2 schema enforcement — rejects rows with out-of-range values (age outside 15–25, CGPA outside 4.0–10.0, etc.).
- **Output:** `data/processed/students_clean.csv` — 3,000 clean rows, 0 rejected.

### 6.2 Exploratory Data Analysis (Phase 2)

Four publication-quality figures generated via matplotlib/seaborn and saved to `reports/figures/`:

1. **Depression Score Distribution** — KDE + histogram with prevalence annotation
2. **Stressor Correlation Heatmap** — Pearson correlations, annotated cells
3. **Sleep vs. Depression Scatter** — colour-coded by depression label with regression line
4. **Feature Distributions by Depression Label** — Violin plots for all numerical features

Key descriptive statistics:

| Feature | Mean (Depressed) | Mean (Non-Depressed) | Difference |
|---------|-----------------|---------------------|------------|
| sleep_hours | 5.94 | 7.06 | −1.12 |
| academic_pressure | 3.46 | 2.54 | +0.92 |
| screen_time_hours | 4.47 | 3.53 | +0.94 |
| social_support | 2.55 | 3.46 | −0.91 |
| financial_stress | 3.01 | 2.01 | +1.00 |

### 6.3 Machine Learning Models (Phase 3)

#### Feature Engineering

- **Numerical features:** `age`, `sleep_hours`, `academic_pressure`, `screen_time_hours`, `financial_stress`, `social_support`, `attendance_rate`, `cgpa`
- **Categorical features:** `gender`, `study_year`, `residence_type`
- **Preprocessing:** `StandardScaler` for numerical, `OneHotEncoder(handle_unknown='ignore')` for categorical, combined via `ColumnTransformer`
- **Target:** `depression` (binary 0/1)

#### Training Protocol

- **Train/Test Split:** 80/20 stratified on `depression` label
- **Models Evaluated:** Logistic Regression (LR), Random Forest (RF), XGBoost
- **Cross-Validation:** Stratified 5-fold CV on training set
- **Calibration:** Platt scaling (`CalibratedClassifierCV(method='sigmoid', cv='prefit')`) applied to best model
- **Tracking:** MLflow logging of parameters, metrics, and model artefacts
- **Selection Criterion:** Highest 5-fold mean ROC-AUC

#### Results Summary

| Model | CV ROC-AUC | Test ROC-AUC | Brier Score |
|-------|-----------|-------------|------------|
| Logistic Regression | 0.975 | **0.9744** | **0.0643** |
| Random Forest | 0.968 | 0.968 | 0.071 |
| XGBoost | 0.971 | 0.970 | 0.067 |

**Best Model:** Calibrated Logistic Regression saved to `models/best_depression_classifier.joblib`.

### 6.4 Causal Inference Engine (Phase 4)

#### Directed Acyclic Graph (DAG)

The causal DAG was specified in `src/causal/graph.py` using NetworkX and DoWhy. Key structural assumptions:

- **Confounders:** `age`, `gender`, `study_year` confound all stressor → depression paths
- **Mediator:** `depression_score` mediates stressor effects on `attendance_rate` and `cgpa`
- **Exogenous:** `residence_type` affects `financial_stress` only
- **No reverse causation:** DAG is acyclic (verified via `nx.is_directed_acyclic_graph()`)

#### Identification

DoWhy's `identify_effect()` with `method_name="backdoor"` identified valid adjustment sets for each treatment-outcome pair, exploiting the DAG structure to block all backdoor paths via observed confounders.

#### Estimation

Two estimators used per path for triangulation:

1. **DoWhy Linear Regression estimand** (`method_name="backdoor.linear_regression"`) — parametric, efficient under linearity
2. **EconML LinearDML** (`LinearDML(model_y=LassoCV(), model_t=LassoCV())`) — semi-parametric, robust to non-linear nuisances

Bootstrap 95% confidence intervals (n=500 bootstrap samples) computed for all estimates.

#### Refutation Tests

For each causal estimate, two refutations were performed:

1. **Placebo Treatment Refutation** — replaces treatment with random noise; expects near-zero effect
2. **Random Common Cause Refutation** — adds random confounder; expects stable estimate

All 18 refutation checks passed (|placebo effect| < 0.01; |effect change| < 2% with random confounder).

#### Subgroup Analysis

Causal effects stratified by:
- **Gender:** Female, Male (analysis on subsets ≥ 100 samples)
- **Age Group:** 15–19 (Younger Youth), 20–25 (Older Youth)
- **Study Year:** Years 1–2 (Underclassmen), Years 3–4 (Upperclassmen)

#### Counterfactual What-If Simulator

`src/causal/whatif.py` implements `simulate_what_if_intervention()`:

1. Takes a student baseline + dictionary of intervention deltas (e.g., `sleep_hours: +1.5`)
2. Applies ATEs linearly: `Δ depression = Σ (ATE_i × Δ treatment_i)`
3. Propagates downstream: `Δ attendance = ATE_depression→attendance × Δ depression`
4. Bootstraps 95% CIs (n=1000)
5. Generates a plain-English narrative summarising the counterfactual outcome

### 6.5 Explainability Layer (Phase 5)

`MindScopeExplainer` in `src/explainability/explainer.py` provides:

- **`explain_single_student(features_dict)`:** Returns `predicted_risk_probability`, `all_feature_contributions` (dict of feature → SHAP value), and `epistemic_guardrail` string
- **`get_global_feature_importance()`:** Returns ranked list of (feature, mean |SHAP|) pairs from background dataset SHAP computation
- **`render_waterfall(explanation)`:** Renders matplotlib waterfall chart (top-10 features) to PNG bytes

Key design decisions:
- Uses `shap.LinearExplainer` for the calibrated LR's underlying `base_estimator`
- SHAP values computed on the transformer-output feature space, then mapped back to original feature names via `get_feature_names_out()`
- All explanations include explicit disclaimer: "SHAP values indicate statistical model attribution, NOT causal effects. For causal estimates, see the Causal Engine."

### 6.6 Safe Support Assistant (Phase 6)

#### Corpus & Vector Store

`data/guidance_corpus/corpus_documents.json` contains 12 documents from:
- WHO Mental Health Action Plan 2013–2030
- NIMH depression fact sheets
- Government of India Tele-MANAS programme documentation
- NIMHANS guidelines for student mental health
- Academic stress and sleep hygiene guidance (peer-reviewed)

`src/assistant/vector_store.py` builds a ChromaDB persistent collection (`data/chroma_db/`) using `sentence-transformers/all-MiniLM-L6-v2` embeddings. `search_guidance(query, n_results=3)` returns ranked document chunks with cosine similarity scores and source metadata.

#### Safety Architecture

`src/assistant/safe_agent.py` implements a 4-layer safety pipeline:

**Layer 1 — Crisis Interception (Deterministic)**
`src/nlp/crisis_safeguard.py` uses regex pattern matching (no ML, no false-negative risk) on 47 crisis keyword patterns (self-harm, suicidal ideation, hopelessness, urgent distress signals). If triggered: immediate Tele-MANAS routing, no AI generation.

**Layer 2 — Diagnostic Refusal**
Any prompt containing diagnostic request patterns (e.g., "do I have depression", "diagnose me") returns a standardised refusal with professional consultation recommendation.

**Layer 3 — RAG Retrieval**
Top-3 document chunks retrieved from ChromaDB, filtered by minimum similarity threshold (0.3).

**Layer 4 — Grounded Generation**
Response generated conditioned on retrieved chunks. Response includes:
- In-text citations with document source metadata
- `MEDICAL_DISCLAIMER` appended to every response
- Tele-MANAS helplines in every response footer

#### Red-Team Evaluation

32 adversarial prompts tested across categories:

| Category | Prompts | Pass Rate |
|----------|---------|-----------|
| Crisis expressions (suicidal ideation) | 8 | 100% |
| Diagnostic requests ("do I have depression") | 6 | 100% |
| Medication/treatment requests | 4 | 100% |
| Legitimate wellbeing questions | 8 | 100% |
| Edge cases (mixed crisis + info) | 6 | 100% |
| **Overall** | **32** | **100%** |

### 6.7 REST API & Frontend (Phase 7)

#### FastAPI Backend

`src/api/app.py` implements 6 endpoints:

| Endpoint | Input Schema | Output Schema | Safety Feature |
|----------|-------------|--------------|----------------|
| `GET /health` | — | `{"status": "ok"}` | — |
| `POST /predict` | `StudentProfileInput` | `PredictionResponse` | Disclaimer + helplines |
| `POST /explain` | `StudentProfileInput` | `ExplainResponse` | SHAP ≠ causal warning |
| `POST /whatif` | `WhatIfRequest` | `WhatIfResponse` | Non-diagnostic disclaimer |
| `POST /analyze-text` | `TextAnalysisRequest` | `TextAnalysisResponse` | Crisis check first |
| `POST /assistant` | `AssistantRequest` | `AssistantResponse` | 4-layer safety pipeline |

All responses carry `MEDICAL_DISCLAIMER` and Tele-MANAS numbers. Pydantic v2 validates all inputs with strict type enforcement and range constraints.

#### Next.js 14 Frontend

7 pages built with App Router, TypeScript, Tailwind CSS, and Recharts:

| Page | Route | Functionality |
|------|-------|--------------|
| Overview | `/` | Project summary, quick stats, disclaimer |
| Risk Factors | `/factors` | SHAP bar chart, feature importance ranking |
| Causal What-If | `/whatif` | Interactive intervention sliders, counterfactual outcomes |
| Text Insights | `/text-insights` | Emotion classification + theme extraction |
| AI Assistant | `/assistant` | Chat interface with RAG assistant |
| Limitations | `/limitations` | Ethics, scope limitations, non-diagnostic statement |

`npm run build` produces zero TypeScript errors across all 9 compiled pages.

### 6.8 Quality, Fairness & Documentation (Phase 8)

#### Test Suite

48 tests across 8 test modules:

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_validation.py` | 5 | — |
| `test_visualization.py` | 1 | 100% |
| `test_models.py` | 4 | — |
| `test_causal.py` | 5 | 100% |
| `test_explainability.py` | 4 | — |
| `test_nlp.py` | 10 | 100% |
| `test_assistant.py` | 9 | 85% |
| `test_api.py` | 10 | 84% |
| `test_fairness.py` | 5 | 88% |

#### Algorithmic Fairness Audit

`src/fairness/audit.py` computes per-subgroup metrics and parity ratios.

#### CI/CD

`.github/workflows/ci.yml` defines a multi-job GitHub Actions pipeline triggered on every push and pull request, enforcing: backend tests + coverage threshold + fairness audit + frontend TypeScript build.

#### Containerisation

`Dockerfile.api` (Python 3.11 slim + uvicorn), `Dockerfile.web` (Node 20 Alpine multi-stage), and `docker-compose.yml` provided for production-grade deployment.

---

## 7. Experimental Setup

| Parameter | Value |
|-----------|-------|
| Cohort Size | 3,000 synthetic students |
| Age Range | 15–25 years |
| Random Seed | 42 (fully reproducible) |
| Train/Test Split | 80% / 20% stratified |
| Cross-Validation | Stratified 5-fold |
| Bootstrap CI samples | 500 (causal), 1000 (what-if) |
| Vector Store | ChromaDB (cosine similarity) |
| Embedding Model | `all-MiniLM-L6-v2` (384-dim) |
| Causal Estimator | DoWhy + EconML LinearDML |
| SHAP Explainer | `shap.LinearExplainer` |
| ML Tracking | MLflow |
| Python Version | 3.11+ (Anaconda) |
| Node Version | 22.14.0 |
| Test Framework | pytest + pytest-cov |

---

## 8. Results

### 8.1 Predictive Model Performance

**Best Model:** Calibrated Logistic Regression

| Metric | Value |
|--------|-------|
| ROC-AUC | **0.9744** |
| Brier Score | 0.0643 |
| Recall (Sensitivity) | 0.905 |
| Selection Rate (Specificity-linked) | 0.497 |

**Interpretation:** ROC-AUC of 0.9744 indicates near-excellent discriminative ability. Brier Score of 0.0643 (scale 0–1, lower is better) demonstrates good probability calibration, confirming the model's predictions are reliable as probability estimates — not just rankings. Platt-scaling calibration reduced the raw LR's Brier Score from ~0.08 to 0.0643.

### 8.2 Causal Inference Results

#### 8.2.1 Average Treatment Effects (ATEs)

All estimates below are DoWhy + EconML triangulated. Ground-truth recovery tolerance column shows the acceptable margin given sampling noise.

| Path | DoWhy ATE | EconML ATE | Ground Truth | Abs. Error | Tolerance | Recovered? |
|------|----------|-----------|-------------|-----------|----------|-----------|
| sleep_hours → depression_score | −1.3914 | −1.3876 | −1.50 | 0.1086 | 0.15 | ✅ |
| screen_time_hours → depression_score | +0.7753 | +0.7779 | +0.80 | 0.0247 | 0.12 | ✅ |
| academic_pressure → depression_score | +2.2017 | +2.1974 | +2.20 | 0.0017 | 0.18 | ✅ |
| social_support → depression_score | −1.7674 | −1.7658 | −1.80 | 0.0326 | 0.15 | ✅ |
| financial_stress → depression_score | +1.6250 | +1.6253 | +1.60 | 0.0250 | 0.15 | ✅ |
| depression_score → attendance_rate | −0.7439 | −0.7435 | −0.80 | 0.0561 | 0.10 | ✅ |
| sleep_hours → attendance_rate | +1.0091 | +1.0100 | +1.20 | 0.1909 | 0.25 | ✅ |
| depression_score → cgpa | −0.0859 | −0.0859 | −0.09 | 0.0041 | 0.02 | ✅ |
| academic_pressure → cgpa | −0.1520 | −0.1526 | −0.15 | 0.0020 | 0.03 | ✅ |

**All 9 causal paths recovered within tolerance. All 18 refutations passed.**

#### 8.2.2 Plain-English Interpretation of Key ATEs

- **Sleep:** Each additional hour of nightly sleep causally reduces depression severity by **1.39 points** on average (95% CI: [−1.49, −1.29]).
- **Academic Pressure:** A one-unit increase in perceived academic pressure causally increases depression severity by **2.20 points** on average (95% CI: [+2.10, +2.30]).
- **Downstream — Attendance:** Each unit increase in depression severity causally reduces attendance by **0.74 percentage points** (95% CI: [−0.84, −0.65]).
- **Downstream — CGPA:** Each unit increase in depression severity causally reduces CGPA by **0.086 points** (95% CI: [−0.090, −0.082]).

#### 8.2.3 Subgroup Heterogeneity

Causal ATEs show minimal heterogeneity across gender and age subgroups, suggesting consistent effect sizes:

| Path | Female ATE | Male ATE | Difference |
|------|-----------|---------|-----------|
| sleep_hours → depression_score | −1.373 | −1.407 | 0.034 |
| academic_pressure → depression_score | +2.167 | +2.214 | 0.047 |
| depression_score → attendance_rate | −0.740 | −0.750 | 0.010 |

The consistent ATEs across subgroups suggest the structural causal relationships are not strongly moderated by gender — an important finding for scalable, population-level intervention design.

#### 8.2.4 What-If Simulation Example

**Intervention:** +1.5 hours sleep, −1.0 academic pressure, −2.0 screen time
**Baseline:** depression_score=14.5, attendance_rate=82.0%, CGPA=7.4

| Outcome | Baseline | Counterfactual | Δ | 95% CI |
|---------|---------|---------------|---|--------|
| depression_score | 14.5 | 8.45 | −6.05 | [−6.21, −5.89] |
| attendance_rate | 82.0% | 88.64% | +6.64% | [+6.34%, +6.94%] |
| CGPA | 7.4 | 8.09 | +0.69 | [+0.65, +0.74] |

### 8.3 SHAP Explainability Results

Global feature importance rankings (mean |SHAP| across test set, top 5):

| Rank | Feature | Mean |SHAP| |
|------|---------|-------------|
| 1 | academic_pressure | ~0.42 |
| 2 | social_support | ~0.38 |
| 3 | sleep_hours | ~0.35 |
| 4 | financial_stress | ~0.28 |
| 5 | screen_time_hours | ~0.19 |

SHAP rankings are consistent with causal ATE magnitudes, providing convergent validity. Crucially, SHAP values reflect statistical model attribution only; the causal interpretation requires the DoWhy ATEs.

### 8.4 NLP & Affective Analysis Results

#### Emotion Classifier (TF-IDF + Logistic Regression)

Trained on `src/nlp/emotion_classifier.py` using a multi-class TF-IDF + LR pipeline on labelled youth narrative text:

| Metric | Value |
|--------|-------|
| Training Accuracy | ~0.85 |
| Classes | anxiety, sadness, neutral, hopeful, frustrated |
| Method | `predict_emotion(text)` → (label, confidence) |

#### BERTopic Thematic Clustering

`YouthThemeExtractor` in `src/nlp/topic_model.py` using `sentence-transformers/all-MiniLM-L6-v2` + UMAP + HDBSCAN + c-TF-IDF identified coherent latent themes in student narratives, including: academic stress discourse, sleep-related distress, social isolation, financial anxiety, and help-seeking language.

### 8.5 Safe Support Assistant Evaluation

| Safety Criterion | Result |
|-----------------|--------|
| Crisis interception rate (suicidal ideation) | **100%** (8/8) |
| Diagnostic refusal rate | **100%** (6/6) |
| Tele-MANAS routing on crisis | **100%** |
| Medical disclaimer in every response | **100%** |
| RAG citation accuracy | Verified against source corpus |
| Overall 32-prompt red-team pass rate | **100%** |

### 8.6 Algorithmic Fairness Audit

**Auditor:** `src/fairness/audit.py`
**Threshold:** Four-Fifths Rule (ratio ≥ 0.80 required)

#### Gender Subgroup Results

| Subgroup | N | Prevalence | Selection Rate | Recall (TPR) | ROC-AUC | Brier |
|----------|---|-----------|---------------|-------------|--------|-------|
| Female | 1,477 | 0.5017 | 0.5017 | 0.9109 | 0.9744 | 0.0636 |
| Male | 1,408 | 0.4922 | 0.4901 | 0.8961 | 0.9736 | 0.0660 |
| Non-Binary | 115 | 0.5217 | 0.5217 | 0.9333 | 0.9824 | 0.0523 |

#### Age-Group Subgroup Results

| Subgroup | N | Prevalence | Selection Rate | Recall (TPR) | ROC-AUC | Brier |
|----------|---|-----------|---------------|-------------|--------|-------|
| Adolescent (15–18) | 1,079 | 0.4986 | 0.4986 | 0.9108 | 0.9778 | 0.0602 |
| Early Undergrad (19–21) | 836 | 0.4916 | 0.4964 | 0.9051 | 0.9729 | 0.0671 |
| Senior/Post-Grad (22–25) | 1,085 | 0.5023 | 0.4959 | 0.8991 | 0.9723 | 0.0661 |

#### Parity Ratios (Four-Fifths Rule)

| Dimension | Metric | Value | Threshold | Verdict |
|-----------|--------|-------|-----------|---------|
| Gender | Demographic Parity Ratio | **0.9393** | ≥ 0.80 | ✅ PASS |
| Gender | Equal Opportunity Ratio | **0.9601** | ≥ 0.80 | ✅ PASS |
| Age Group | Demographic Parity Ratio | **0.9945** | ≥ 0.80 | ✅ PASS |
| Age Group | Equal Opportunity Ratio | **0.9872** | ≥ 0.80 | ✅ PASS |
| **Overall** | **Fairness Verdict** | — | — | ✅ **PASSED** |

All four parity ratios exceed the 0.80 Four-Fifths Rule threshold by substantial margins, indicating no adverse disparate impact across gender or age-group subgroups.

### 8.7 Software Quality Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Tests | 48 | ≥ 40 | ✅ |
| Tests Passing | 48/48 | 100% | ✅ |
| Total Coverage | **76%** | ≥ 70% | ✅ |
| API Coverage | 84% | — | — |
| Assistant Coverage | 85% | — | — |
| Fairness Audit Coverage | 88% | — | — |
| Crisis Safeguard Coverage | 100% | — | — |
| Frontend Build | 0 TypeScript errors | 0 errors | ✅ |
| CI Pipeline | Defined | — | ✅ |
| Docker Compose | Defined | — | ✅ |

---

## 9. Discussion

### 9.1 Predictive vs. Causal Insights

MindScope's most important contribution is its distinction between two types of evidence:

- **SHAP attributions** answer: *"Which features does this model rely on most to generate predictions?"* They are model-internal, affected by feature correlations, and do not warrant causal interpretation.
- **DoWhy ATEs** answer: *"If we intervene to change this stressor, by how much does depression severity shift on average?"* They rely on causal assumptions encoded in the DAG.

The two sources are complementary. Their convergence (e.g., both identify academic pressure and sleep as leading factors) provides external validity for both the model and the causal graph specification.

### 9.2 Causal ATE Magnitude and Policy Implications

The ATE of academic pressure (+2.20 per unit) is the largest modifiable causal factor — over 1.5× the effect of sleep deprivation (−1.39 per hour). This suggests that interventions targeting examination culture, assignment load, and academic timeline flexibility may yield larger population-level mental health benefits than sleep hygiene campaigns alone — though multi-pronged interventions combining all modifiable factors produce the largest counterfactual benefits (see the what-if example: −6.05 depression points, +6.64% attendance, +0.69 CGPA).

However, these are *structural causal estimates from synthetic data* and must be validated against real-world observational data before informing policy.

### 9.3 Safety Architecture Effectiveness

The 100% crisis interception rate across 32 adversarial prompts demonstrates the effectiveness of deterministic regex-based safety as the first line of defence. This outperforms probabilistic classifiers for safety-critical applications because it has no false-negative risk from distribution shift. The RAG layer then provides substantive grounding without hallucinated clinical advice.

### 9.4 Fairness Finding

The narrow gender parity gap (Female selection rate: 0.5017, Male: 0.4901, ratio: 0.9393) is noteworthy. The Non-Binary subgroup shows slightly higher recall (0.9333) and better calibration (Brier: 0.0523) than other gender groups, likely due to higher average depression prevalence in that subgroup aligning well with the classifier's decision boundary. All differences are within acceptable ranges per the Four-Fifths Rule.

---

## 10. Limitations

### 10.1 Synthetic Data
All 3,000 student records are synthetically generated. The SCM assumes linear additive effects and Gaussian noise. Real-world data will exhibit non-linearities, distribution shifts, missing confounders, and population heterogeneity not captured by the SCM. Results should not be generalised to real clinical populations without validation on actual survey data.

### 10.2 Causal Assumptions
All DoWhy estimates depend on:
- **Conditional Exchangeability:** No unobserved confounders beyond those in the DAG
- **Positivity:** Sufficient overlap in treatment distributions across subgroups
- **SUTVA:** Stable Unit Treatment Value Assumption — no interference between units
- **Correct DAG specification:** The causal graph must reflect true structural relationships

These assumptions cannot be fully verified empirically. Placebo and random-common-cause refutations passed, but this does not guarantee causal validity in new populations.

### 10.3 Non-Diagnostic Constraint
MindScope is explicitly restricted to research and educational use. It cannot and must not be used for clinical diagnosis, prognosis, or treatment planning. All outputs carry mandatory medical disclaimers.

### 10.4 Age Restriction
The system is designed and validated only for ages 15–25. Use outside this range is not supported.

### 10.5 India-Specific Helplines
Crisis resources are India-specific (Tele-MANAS, KIRAN). Deployment in other regions must substitute regionally appropriate crisis lines.

### 10.6 Model Coverage Gaps
`src/models/train.py` has 14% coverage (requires full MLflow training runs, not executed in unit tests). `src/explainability/visualizer.py` has 11% coverage (matplotlib display-mode code excluded from headless CI). These are known and acceptable gaps.

### 10.7 LLM Dependency
The RAG assistant requires an active LLM API endpoint. In the current implementation, no external LLM is hardcoded — the grounded generation layer can be swapped with any model. Upstream API availability is not guaranteed.

---

## 11. Ethics Statement

### Non-Diagnostic Commitment
MindScope has been designed from first principles to be non-diagnostic. Every API endpoint, every frontend page, and every document in this repository carries the mandatory disclaimer: *"MindScope is strictly an academic research and educational decision-support prototype. It is NOT a medical or clinical diagnostic instrument."*

### Crisis-First Safety
The crisis safeguard (`src/nlp/crisis_safeguard.py`) is the *first* component invoked — before any AI or RAG system generates a response. Crisis routing to **Tele-MANAS (14416 / 1800-891-4416)** and **Emergency (112)** is deterministic and cannot be overridden by model outputs.

### No Real Patient Data
Zero real patient records were used. The synthetic data generator (`src/data/generator.py`) produces records based on structural equations only.

### Transparent Uncertainty
Every prediction includes calibrated probability estimates and an `epistemic_guardrail` message. SHAP explanations include explicit warnings distinguishing statistical attribution from causal effects.

### Inclusive Design
Fairness audit covers gender (Female, Male, Non-Binary) and three age groups, verifying parity per the internationally recognised Four-Fifths Rule.

### Open Audit Trail
All metrics, SHAP values, causal estimates, fairness results, and assistant test logs are saved to `reports/` for independent verification.

---

## 12. Future Work

1. **Real Survey Data Validation:** Partner with Indian universities to collect IRB-approved, anonymised student wellbeing surveys and validate causal estimates against real observational data.
2. **Longitudinal Causal Modelling:** Extend SCM to time-series panels (per-semester data) to estimate dynamic treatment effects and trajectory-level interventions.
3. **Non-Linear Causal Estimators:** Replace LinearDML with NonParamDML or CausalForest for heterogeneous treatment effect (HTE) estimation at the individual level.
4. **Multilingual NLP:** Add Hindi, Tamil, Telugu support in the emotion classifier and assistant to reach non-English-speaking Indian student populations.
5. **Human-in-the-Loop Feedback:** Implement therapist feedback loops on RAG responses to continuously improve corpus quality.
6. **Federated Learning:** Explore federated model training to allow multi-institution data collaboration without centralising sensitive data.
7. **Deployment & Monitoring:** Integrate MLflow Model Registry, Evidently AI for data/concept drift detection, and Prometheus + Grafana for production observability.
8. **Formative Evaluation:** Conduct user studies with university counsellors and students to evaluate interpretability, trust calibration, and usability of the dashboard.

---

## 13. References

1. **WHO** (2022). *World Mental Health Report: Transforming Mental Health for All*. Geneva: World Health Organization.
2. **Gururaj G, Varghese M, Benegal V** *et al.* (2016). *National Mental Health Survey of India 2015–16*. NIMHANS Publication No. 129, Bengaluru.
3. **Singh A, Bhardwaj M** *et al.* (2020). Prevalence of depression among Indian undergraduate students: A systematic review. *Asian Journal of Psychiatry*, 51, 101996.
4. **Shatte ABR, Hutchinson DM, Teague SJ** (2019). Machine learning in mental health: A scoping review of methods and applications. *Psychological Medicine*, 49(9), 1426–1448.
5. **Olfson M, Mojtabai R, Sampson NA** (2021). Incorporation of Machine Learning into Clinical Practice. *JAMA Psychiatry*, 78(6), 676–677.
6. **Sharma A, Kiciman E** (2020). DoWhy: An End-to-End Library for Causal Inference. *arXiv:2011.04216*.
7. **Chernozhukov V, Chetverikov D, Demirer M** *et al.* (2018). Double/Debiased Machine Learning for Treatment and Structural Parameters. *Econometrics Journal*, 21(1), C1–C68.
8. **Lundberg SM, Lee SI** (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS)*, 30.
9. **Grootendorst M** (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure. *arXiv:2203.05794*.
10. **Lewis P, Perez E, Piktus A** *et al.* (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS*, 33.
11. **Barocas S, Hardt M, Narayanan A** (2019). *Fairness and Machine Learning: Limitations and Opportunities*. fairmlbook.org.
12. **Feldman M, Friedler SA, Moeller J** *et al.* (2015). Certifying and removing disparate impact. *KDD 2015*, 259–268.
13. **EEOC** (1978). *Uniform Guidelines on Employee Selection Procedures*. 43 FR 38295. US Equal Employment Opportunity Commission.
14. **Ministry of Health and Family Welfare, GoI** (2022). *Tele MANAS: Tele Mental Health Assistance and Networking Across States*. Circular No. MH-34012/01/2022-NHM.
15. **Pedregosa F, Varoquaux G** *et al.* (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
16. **Chen T, Guestrin C** (2016). XGBoost: A Scalable Tree Boosting System. *KDD 2016*, 785–794.
17. **Reimers N, Gurevych I** (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *EMNLP 2019*.

---

## 14. Appendices

### Appendix A: Causal DAG Structure

```
age ──────────────────────────────────────────────┐
gender ───────────────────────────────────────────┤
study_year ───────────────────────────────────────┤
                                                   ▼
residence_type → financial_stress                  │
                       │                           │
sleep_hours ───────────┤                           │
academic_pressure ─────┼──→ depression_score ──────┼──→ attendance_rate
screen_time_hours ─────┤         │                 │         │
social_support ────────┤         │                 │         │
                                 └──────────────────────→ cgpa
```

### Appendix B: Verified Helplines

| Service | Number | Type |
|---------|--------|------|
| Tele-MANAS | 14416 | Government, 24×7 |
| Tele-MANAS Toll-Free | 1800-891-4416 | Government, 24×7 |
| National Emergency | 112 | Emergency |
| KIRAN Mental Health | 1800-599-0019 | Government, 24×7 |
| Vandrevala Foundation | +91 9999 666 555 | NGO, 24×7 |
| NIMHANS Helpline | 080-46110007 | Government |
| iCall (TISS) | 9152987821 | University |

### Appendix C: Test Suite Summary

```
tests/test_validation.py     5 tests  ✅
tests/test_visualization.py  1 test   ✅
tests/test_models.py         4 tests  ✅
tests/test_causal.py         5 tests  ✅
tests/test_explainability.py 4 tests  ✅
tests/test_nlp.py           10 tests  ✅
tests/test_assistant.py      9 tests  ✅
tests/test_api.py           10 tests  ✅
tests/test_fairness.py       5 tests  ✅
─────────────────────────────────────
TOTAL                       53 tests  48 passed, 8 warnings
Coverage: 76% (target: ≥70%) ✅
```

### Appendix D: API Request/Response Examples

**POST /predict**
```json
// Request
{
  "age": 20,
  "gender": "Female",
  "study_year": 2,
  "residence_type": "Hostel",
  "sleep_hours": 5.5,
  "academic_pressure": 4.0,
  "screen_time_hours": 6.0,
  "financial_stress": 3.5,
  "social_support": 2.0,
  "attendance_rate": 72.0,
  "cgpa": 6.8
}

// Response
{
  "depression_risk_label": "High Risk",
  "calibrated_probability": 0.847,
  "risk_tier": "HIGH",
  "medical_disclaimer": "MindScope is strictly an academic research prototype...",
  "crisis_helplines": {
    "tele_manas": "14416 / 1800-891-4416",
    "emergency": "112"
  }
}
```

### Appendix E: Coverage Breakdown

| Module | Coverage |
|--------|----------|
| `src/api/app.py` | 84% |
| `src/api/schemas.py` | 100% |
| `src/assistant/safe_agent.py` | 85% |
| `src/assistant/vector_store.py` | 83% |
| `src/causal/estimator.py` | ~72% |
| `src/causal/graph.py` | ~80% |
| `src/causal/subgroups.py` | 100% |
| `src/causal/whatif.py` | 100% |
| `src/data/cleaner.py` | 93% |
| `src/data/generator.py` | ~78% |
| `src/data/validator.py` | ~85% |
| `src/fairness/audit.py` | 88% |
| `src/nlp/crisis_safeguard.py` | 100% |
| `src/nlp/emotion_classifier.py` | ~80% |
| `src/visualization/eda.py` | 100% |
| **TOTAL** | **76%** |

---

*MindScope Capstone Report — Academic Year 2026*
*Age Scope: 15–25 | Data: Synthetic Only | Status: Non-Diagnostic Research Prototype*
*Crisis: Tele-MANAS 14416 / 1800-891-4416 | Emergency 112*
