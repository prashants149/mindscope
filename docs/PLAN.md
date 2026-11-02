# MindScope: AI-Based Analysis of Causes and Effects of Youth Mental Health Issues
## Comprehensive System Architecture, Research Plan, and 10-Week Implementation Roadmap

> **MANDATORY ETHICAL & MEDICAL DISCLAIMER**  
> MindScope is strictly an academic research and educational decision-support software system for youth aged 15–25. It is **NOT** a medical diagnostic instrument, psychiatric diagnostic tool, or clinical decision system. It does **NOT** diagnose mental disorders or prescribe medical treatments. All analytical outputs represent statistical associations and causal estimates under specified econometric assumptions. If a user expresses self-harm or suicidal intent, the system immediately ceases analytical processing and surfaces verified national crisis helplines (Tele-MANAS: **14416** or **1800-891-4416**, Emergency: **112**).

---

## 1. Executive Summary & Project Statement
Youth mental health (ages 15–25) is impacted by complex, interacting factors spanning academic workloads, sleep disruption, digital media saturation, financial precarity, and social isolation. Existing tools either offer black-box predictions that confuse correlation with causation or rely on unconstrained chatbots prone to clinical hallucinations.

**MindScope** bridges this gap as an explainable, causal-aware, source-grounded research platform:
1. **Predictive Modeling:** Quantifies associations with depression and anxiety using calibrated, class-balanced machine learning.
2. **Explainable AI (XAI):** Unpacks global and local model behaviors using SHAP (SHapley Additive exPlanations) while explicitly communicating that predictive feature importance does not equate to causal impact.
3. **Causal Inference Engine:** Implements formal Structural Causal Models (SCMs) in DoWhy and EconML to estimate Average Treatment Effects (ATE) of modifiable lifestyle and academic factors on depression and downstream academic outcomes (attendance rate and CGPA), backed by refutation tests.
4. **Affective & Thematic NLP:** Extracts multi-label emotion distributions and discovers latent discussion themes from student narratives using fine-tuned DistilBERT and BERTopic.
5. **Safe, Source-Grounded Support Assistant:** Employs Retrieval-Augmented Generation (RAG) over verified public guidance (WHO, NIMH, Tele-MANAS) via Claude/Anthropic API, equipped with deterministic crisis safeguards and non-diagnostic guardrails.

---

## 2. Research Questions (RQs)

* **RQ1 (Predictive Associations & Risk Indicators):**  
  Which lifestyle, academic, and socio-demographic indicators are most strongly predictive of depression and anxiety among youth aged 15–25 across modern classification architectures (Logistic Regression, Random Forest, XGBoost)?
* **RQ2 (Causal Attribution & Counterfactual Outcomes):**  
  What are the identifiable causal effects of modifiable factors (sleep duration, recreational screen time, academic pressure, social support, and financial stress) on depression severity, and how does depression causally mediate downstream educational impacts (class attendance rate and CGPA)?
* **RQ3 (Affective & Thematic Text Mining):**  
  Can lightweight transformer models running on CPU environments reliably detect nuanced emotion distributions and extract emergent thematic stressors from youth narratives without confusing metaphorical angst with acute distress?
* **RQ4 (Safe, Grounded Conversational Support):**  
  How can a retrieval-augmented conversational assistant deliver source-attributed emotional support and evidence-backed coping strategies while strictly enforcing non-diagnostic boundaries and infallible crisis detection?

---

## 3. High-Level System Architecture

```
                                  +---------------------------------------+
                                  |         Next.js Web Frontend          |
                                  |  (TypeScript, Tailwind CSS, Recharts) |
                                  +-------------------+-------------------+
                                                      |
                                             REST API / JSON
                                                      |
                                  +-------------------v-------------------+
                                  |           FastAPI Backend             |
                                  |     (Python 3.11, Pydantic, CORS)     |
                                  +----+-------------+--------------+-----+
                                       |             |              |
                +----------------------+             |              +-----------------------+
                |                                    |                                      |
+---------------v---------------+   +----------------v----------------+   +-----------------v----------------+
|     Predictive & XAI Engine   |   |     Causal Inference Engine     |   |    Safe NLP & Support Engine     |
| - Preprocessing Pipeline      |   | - DoWhy Structural Causal Graph |   | - DistilBERT Emotion Classifier  |
| - Logistic Regression/XGBoost |   | - EconML DML / Causal Forest    |   | - BERTopic Theme Extractor       |
| - TreeSHAP / KernelSHAP       |   | - Refutation & Sensitivity      |   | - ChromaDB Vector Store (RAG)    |
| - MLflow Experiment Tracking  |   | - Counterfactual "What-If" API  |   | - Anthropic API (Claude 3.5)     |
+-------------------------------+   +---------------------------------+   | - Deterministic Crisis Safeguard |
                                                                          +----------------------------------+
                                                     |
                                  +------------------v--------------------+
                                  |       Storage & Artifact Layer        |
                                  | - SQLite (Logs, Sessions)             |
                                  | - ChromaDB (WHO/NIMH/Tele-MANAS docs) |
                                  | - Serialized Models (ONNX / Joblib)   |
                                  +---------------------------------------+
```

---

## 4. Structural Causal Model (SCM) Specification

The synthetic benchmark data and causal analysis are structured according to the following Directed Acyclic Graph (DAG):

```
       [Financial Stress] --------+
               |                  |
               v                  v
     [Academic Pressure] ---> [Depression Severity] <--- [Social Support]
          |       |           ^       ^        |
          |       v          /        |        |
          |  [Screen Time] -+         |        |
          v       |                   |        |
       [Sleep Duration] --------------+        |
          |                                    |
          |           +------------------------+
          |           |                        |
          v           v                        v
    [Attendance Rate (%)]                   [CGPA (10.0)]
```

### Structural Equations & Ground-Truth Parameter Table

Let $S$ = Sleep hours, $T$ = Screen time hours, $P$ = Academic pressure (1–5), $U$ = Social support (1–5), $F$ = Financial stress (1–5).

1. **Depression Severity ($D \in [0, 27]$, PHQ-9 scale):**
   $$D = 12.0 - 1.50(S - 7.0) + 0.80(T - 5.5) + 2.20(P - 3.0) - 1.80(U - 3.0) + 1.60(F - 3.0) + \epsilon_D$$
   where $\epsilon_D \sim \mathcal{N}(0, 1.5^2)$. Binary depression indicator: $\mathbb{I}(D \ge 10.0)$.

2. **Attendance Rate ($Att \in [40, 100]\%$):**
   $$Att = 92.0 - 0.80(D - 10.0) + 1.20(S - 7.0) + \epsilon_{Att}$$
   where $\epsilon_{Att} \sim \mathcal{N}(0, 3.0^2)$.

3. **CGPA ($CGPA \in [2.0, 10.0]$):**
   $$CGPA = 8.80 - 0.09(D - 10.0) - 0.15(P - 3.0) + \epsilon_{CGPA}$$
   where $\epsilon_{CGPA} \sim \mathcal{N}(0, 0.4^2)$.

| Relationship / Causal Path | Causal Type | True Coefficient ($\beta$) | Expected Estimation Tolerance |
|:---|:---|:---:|:---:|
| `sleep_hours -> depression_score` | Direct Effect | **-1.50** | $\pm 0.15$ |
| `screen_time_hours -> depression_score` | Direct Effect | **+0.80** | $\pm 0.12$ |
| `academic_pressure -> depression_score` | Direct Effect | **+2.20** | $\pm 0.18$ |
| `social_support -> depression_score` | Direct Effect | **-1.80** | $\pm 0.15$ |
| `financial_stress -> depression_score` | Direct Effect | **+1.60** | $\pm 0.15$ |
| `depression_score -> attendance_rate` | Direct Effect | **-0.80** | $\pm 0.10$ |
| `sleep_hours -> attendance_rate` | Direct Effect | **+1.20** | $\pm 0.15$ |
| `depression_score -> cgpa` | Direct Effect | **-0.09** | $\pm 0.02$ |
| `academic_pressure -> cgpa` | Direct Effect | **-0.15** | $\pm 0.03$ |
| `sleep_hours -> attendance_rate` | Total Effect | **+2.40** | $\pm 0.25$ |
| `academic_pressure -> cgpa` | Total Effect | **-0.348** | $\pm 0.05$ |

---

## 5. Public Datasets Documentation & Licensing Matrix

| Dataset Name | Domain / Primary Features | Source / Citation | License | Privacy & Legal Compliance |
|:---|:---|:---|:---:|:---|
| **Student Mental Health** | University student survey on CGPA, age, gender, marital status, depression, anxiety, panic attacks. (N=101) | Shariful Islam, IIUM Malaysia / Kaggle [ADD CITATION] | **CC0: Public Domain** | Fully de-identified, no PII, public domain dedication. |
| **Student Depression Dataset** | Indian students across multiple cities; academic pressure, study satisfaction, sleep duration, dietary habits, suicidal ideation, depression status. (N>27,000) | Kaggle / Open Academic Data [ADD CITATION] | **Apache 2.0 / CC0** | Anonymized city & student IDs. Complies with India Digital Personal Data Protection (DPDP) Act 2023. |
| **GoEmotions** | 58,000 curated Reddit comments manually annotated across 27 emotion categories and neutral. | Google Research (Demszky et al., ACL 2020) [ADD CITATION] | **Apache 2.0 / CC BY 4.0** | Public Reddit comments stripped of user handles and subreddit metadata. |
| **Dreaddit** | 3,553 social media posts across 5 domains (anxiety, PTSD, financial, relationship, domestic abuse) labeled for psychological stress. | Columbia University (Turcan & McKeown, EMNLP 2019) [ADD CITATION] | **CC BY 4.0** | Post IDs anonymized, research use approved under institutional IRB protocols. |

---

## 6. Ten-Week Phase Roadmap

```
Week 1: Phase 1 - Architecture, Research Questions, Synthetic SCM Generator & Cleaning Pipeline
Week 2: Phase 2 - Exploratory Data Analysis & Calibrated Predictive Models (MLflow)
Week 3: Phase 3 - Explainability via SHAP (Global/Local) & Plain-English Association Summaries
Week 4-5: Phase 4 - Causal Graph Inference, Refutations, Subgroup Effects & "What-If" API
Week 6: Phase 5 - Fine-Tuned Emotion Classifier (DistilBERT) & BERTopic Thematic Discovery
Week 7: Phase 6 - Safe RAG Assistant (Anthropic API, ChromaDB) & 30+ Red-Team Guardrail Tests
Week 8: Phase 7 - FastAPI REST Endpoints & Next.js Full-Stack Application
Week 9-10: Phase 8 - Dockerization, Pytest (>70% Coverage), GitHub CI, Fairness Audits & Thesis Report
```

---

## 7. Safety Protocols & Red-Teaming Safeguards

### 7.1 Deterministic Crisis Interception
If user input or processed narrative matches self-harm or suicidal ideation patterns:
1. Immediately halt all analytical and inference pipelines.
2. Return a high-priority supportive response.
3. Provide prominent display of verified 24/7 toll-free crisis lines:
   - **Tele-MANAS:** `14416` or `1800-891-4416` (National Tele Mental Health Programme of India)
   - **Emergency Services:** `112`
   - **KIRAN Helpline:** `1800-599-0019`
4. Strongly advise connecting with trusted family, faculty mentors, or professional care.

### 7.2 Non-Diagnostic Framing
Under no circumstances will the system output diagnostic categorizations (e.g., "You are diagnosed with Major Depressive Disorder"). The system strictly reports:
- Factor risk scores and empirical percentiles.
- Estimated counterfactual shifts under hypothetical lifestyle changes.
- Emotion intensity vectors and thematic clusters.
