"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Activity, Brain, Sparkles, MessageSquare, ShieldAlert, ArrowRight, CheckCircle2, PhoneCall } from "lucide-react";
import { checkHealth } from "@/lib/api";

export default function OverviewPage() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    checkHealth().then(setHealth);
  }, []);

  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-900 via-indigo-900 to-slate-900 rounded-3xl p-8 sm:p-12 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center space-x-2 bg-blue-500/20 text-blue-200 border border-blue-400/30 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
            Final-Year Capstone Project &bull; B.Tech CSE (AI)
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            AI-Based Analysis of Causes & Effects of Youth Mental Health Issues
          </h1>
          <p className="text-blue-100 text-base sm:text-lg leading-relaxed">
            MindScope is an explainable, causal AI research platform tailored for student cohorts aged 15–25. It links demographic and academic pressures to mental health outcomes, estimates counterfactual intervention effects on CGPA and attendance, and provides a safe, source-grounded support assistant.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              href="/factors"
              className="inline-flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white font-semibold px-5 py-2.5 rounded-xl transition shadow-md"
            >
              <span>Explore Factor Importance</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/whatif"
              className="inline-flex items-center space-x-2 bg-white/10 hover:bg-white/20 text-white font-semibold px-5 py-2.5 rounded-xl backdrop-blur-sm transition border border-white/20"
            >
              <span>Causal What-If Engine</span>
            </Link>
          </div>
        </div>
      </div>

      {/* System Status Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className={`w-3.5 h-3.5 rounded-full ${health?.status === "healthy" ? "bg-emerald-500 animate-pulse" : "bg-slate-400"}`} />
          <div>
            <h4 className="text-sm font-semibold text-slate-800">
              FastAPI Inference Engine & Safety Services:{" "}
              <span className={health?.status === "healthy" ? "text-emerald-600 font-bold" : "text-slate-500"}>
                {health?.status === "healthy" ? "Online & Ready" : "Initializing..."}
              </span>
            </h4>
            <p className="text-xs text-slate-500">
              Calibrated Classifier &bull; Linear SHAP &bull; DoWhy Causal DAG &bull; BERTopic &bull; ChromaDB RAG
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs bg-slate-100 text-slate-700 px-3 py-1.5 rounded-lg font-mono">
            v1.0.0 (Research Release)
          </span>
        </div>
      </div>

      {/* Core Research Pillars */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-5">Research Modules & Capabilities</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link
            href="/factors"
            className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-blue-400 hover:shadow-lg transition flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 group-hover:text-blue-600 transition">
                Factor Importance & SHAP
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Estimate calibrated depression risk probabilities and decompose individual risk factors via local SHAP waterfall attributions.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-100 flex items-center text-xs font-semibold text-blue-600">
              <span>View Explanations</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          <Link
            href="/whatif"
            className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-indigo-400 hover:shadow-lg transition flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition">
                <Brain className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 group-hover:text-indigo-600 transition">
                Causal What-If Simulation
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Structural Causal Model simulation estimating true counterfactual intervention effects on depression score, attendance rate, and CGPA with 95% CIs.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-100 flex items-center text-xs font-semibold text-indigo-600">
              <span>Simulate Counterfactuals</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          <Link
            href="/text-insights"
            className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-emerald-400 hover:shadow-lg transition flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:bg-emerald-600 group-hover:text-white transition">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 group-hover:text-emerald-600 transition">
                Text Insights & Affective NLP
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Analyze free-text student reflections for emotional distribution, distress intensity tier, and emergent themes, backed by automatic crisis interception.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-100 flex items-center text-xs font-semibold text-emerald-600">
              <span>Analyze Reflections</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          <Link
            href="/assistant"
            className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-violet-400 hover:shadow-lg transition flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center group-hover:bg-violet-600 group-hover:text-white transition">
                <MessageSquare className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 group-hover:text-violet-600 transition">
                Safe Support Assistant (RAG)
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Source-grounded guidance referencing WHO, NIMH, Tele-MANAS, and NIMHANS. Strictly non-diagnostic with 100% crisis interception sensitivity.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-100 flex items-center text-xs font-semibold text-violet-600">
              <span>Open Assistant</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          <Link
            href="/limitations"
            className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-amber-400 hover:shadow-lg transition flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center group-hover:bg-amber-600 group-hover:text-white transition">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 group-hover:text-amber-600 transition">
                Limitations, Ethics & Fairness
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Academic documentation of unobserved confounding, demographic constraints, algorithmic fairness audits across gender, and non-diagnostic boundaries.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-100 flex items-center text-xs font-semibold text-amber-600">
              <span>Review Limitations</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          <div className="bg-gradient-to-br from-red-50 to-orange-50 p-6 rounded-2xl border border-red-200 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-red-100 text-red-600 flex items-center justify-center">
                <PhoneCall className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-red-950">Immediate Crisis Resources</h3>
              <p className="text-xs text-red-800 leading-relaxed">
                Verified Indian emergency lines active 24x7. If experiencing acute emotional distress or self-harm thoughts:
              </p>
              <ul className="text-xs text-red-900 space-y-1.5 font-medium">
                <li>&bull; <strong>Tele-MANAS:</strong> 14416 or 1800-891-4416 (Toll-Free, 24x7)</li>
                <li>&bull; <strong>National Emergency:</strong> 112</li>
                <li>&bull; <strong>KIRAN:</strong> 1800-599-0019</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
