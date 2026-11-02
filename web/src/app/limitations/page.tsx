"use client";

import { ShieldAlert, AlertTriangle, Scale, BookOpen, HeartPulse, CheckCircle2 } from "lucide-react";

export default function LimitationsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Limitations, Causal Assumptions &amp; Ethical Guardrails
        </h1>
        <p className="text-sm sm:text-base text-slate-600 mt-1">
          Formal academic documentation of structural causal assumptions, demographic constraints, non-diagnostic boundaries, and algorithmic fairness audits.
        </p>
      </div>

      {/* Non-Diagnostic Boundary Card */}
      <div className="bg-amber-50 border border-amber-300 rounded-2xl p-6 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-amber-900 font-bold text-base">
          <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0" />
          <span>Strict Non-Diagnostic Research Boundary</span>
        </div>
        <p className="text-xs sm:text-sm text-amber-950 leading-relaxed">
          MindScope is built exclusively as an <strong>academic research and decision-support tool</strong> for higher education research. It is <strong>NOT a clinical diagnostic instrument</strong>, psychiatric evaluation tool, or medical device. Under no circumstances should MindScope risk scores, SHAP values, or causal estimates be interpreted as clinical diagnoses or medical advice.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Causal Assumptions */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-slate-100">
            <BookOpen className="w-5 h-5 text-indigo-600" />
            <h3 className="font-bold text-slate-900 text-sm">Structural Causal Assumptions</h3>
          </div>
          <ul className="text-xs text-slate-600 space-y-2.5 leading-relaxed">
            <li>
              <strong>1. Conditional Exchangeability:</strong> We assume no unobserved confounders along backdoor paths given the conditioning set (Age, Gender, Financial Stress). In real-world youth mental health, unmeasured factors (genetic predisposition, acute trauma, neurodiversity) may introduce residual confounding.
            </li>
            <li>
              <strong>2. Positivity / Overlap:</strong> Every student profile within the covariate space has a non-zero probability of receiving any level of the lifestyle intervention.
            </li>
            <li>
              <strong>3. SUTVA:</strong> One student&rsquo;s lifestyle intervention (e.g. better sleep) is assumed not to directly alter another student&rsquo;s attendance or CGPA, except through modeled social support channels.
            </li>
            <li>
              <strong>4. DAG Correctness:</strong> Causal estimates rely on the directed acyclic graph specification validated against the synthetic ground truth in Phase 4.
            </li>
          </ul>
        </div>

        {/* Dataset & Demographic Constraints */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-slate-100">
            <AlertTriangle className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-slate-900 text-sm">Data Scope &amp; Demographic Generalizability</h3>
          </div>
          <ul className="text-xs text-slate-600 space-y-2.5 leading-relaxed">
            <li>
              <strong>Age Cohort (15–25 Years):</strong> The models and synthetic generator are calibrated exclusively to secondary and collegiate youth. Findings cannot be generalized to pediatric populations (&lt;15) or working adult cohorts (&gt;25).
            </li>
            <li>
              <strong>Self-Report Bias:</strong> Feature inputs (academic pressure, screen time, social support) rely on self-reported ordinal ratings, which can exhibit subjective scale compression and recall bias.
            </li>
            <li>
              <strong>Cross-Sectional Bounds:</strong> Observational cross-sectional surveys reflect static snapshots; longitudinal causal dynamics require recurring panel tracking over multiple semesters.
            </li>
          </ul>
        </div>

        {/* Algorithmic Fairness Audit */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-slate-100">
            <Scale className="w-5 h-5 text-emerald-600" />
            <h3 className="font-bold text-slate-900 text-sm">Algorithmic Fairness &amp; Parity</h3>
          </div>
          <ul className="text-xs text-slate-600 space-y-2.5 leading-relaxed">
            <li>
              <strong>Subgroup Parity:</strong> In Phase 4 and Phase 8 fairness audits, model calibration and recall are monitored across gender identities (Female, Male, Non-Binary) and study years.
            </li>
            <li>
              <strong>Balanced Calibration:</strong> Probability thresholds are calibrated to prevent disproportionate false-negative rates in historically under-reported demographics.
            </li>
            <li>
              <strong>Transparency:</strong> All model weights, SHAP explanations, and causal estimates are open-source and auditable without black-box proprietary barriers.
            </li>
          </ul>
        </div>

        {/* Crisis Escalation Protocols */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-slate-100">
            <HeartPulse className="w-5 h-5 text-red-600" />
            <h3 className="font-bold text-slate-900 text-sm">Crisis Escalation Safeguards</h3>
          </div>
          <ul className="text-xs text-slate-600 space-y-2.5 leading-relaxed">
            <li>
              <strong>Deterministic Interception:</strong> Any user text indicating self-harm, suicidal ideation, or acute crisis immediately halts predictive and thematic processing.
            </li>
            <li>
              <strong>Verified Tele-MANAS Lines:</strong> Immediate redirection to India&rsquo;s 24x7 toll-free mental health support helpline at <strong>14416 / 1800-891-4416</strong> and National Emergency <strong>112</strong>.
            </li>
            <li>
              <strong>Zero Diagnostic Prescriptions:</strong> The support assistant strictly refuses pharmaceutical inquiries, dosage guidance, or sickness certifications.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
