"use client";

import { useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, Legend } from "recharts";
import { Brain, Sliders, ArrowDownRight, ArrowUpRight, ShieldAlert, Sparkles, AlertCircle } from "lucide-react";
import { simulateWhatIf, WhatIfResult } from "@/lib/api";

export default function WhatIfPage() {
  const [baseline, setBaseline] = useState({
    depression_score: 14.0,
    attendance_rate: 82.0,
    cgpa: 7.4,
  });

  const [interventions, setInterventions] = useState({
    sleep_hours: 1.5,
    screen_time_hours: -2.0,
    academic_pressure: -1.0,
    social_support: 1.0,
    financial_stress: 0.0,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<WhatIfResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await simulateWhatIf(baseline, interventions);
      setResult(data);
    } catch (err: any) {
      setError("Failed to execute causal simulation. Ensure the FastAPI backend is running on http://localhost:8000.");
    } finally {
      setLoading(false);
    }
  };

  const chartData = result
    ? [
        {
          metric: "Depression (0-27)",
          Baseline: result.baseline.depression_score,
          Counterfactual: result.counterfactual_outcomes.depression_score,
          delta: result.predicted_deltas.depression_score,
          ci: result.confidence_intervals_95.depression_score,
        },
        {
          metric: "Attendance (%)",
          Baseline: result.baseline.attendance_rate,
          Counterfactual: result.counterfactual_outcomes.attendance_rate,
          delta: result.predicted_deltas.attendance_rate,
          ci: result.confidence_intervals_95.attendance_rate,
        },
        {
          metric: "CGPA (0-10)",
          Baseline: result.baseline.cgpa,
          Counterfactual: result.counterfactual_outcomes.cgpa,
          delta: result.predicted_deltas.cgpa,
          ci: result.confidence_intervals_95.cgpa,
        },
      ]
    : [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Causal Counterfactual &ldquo;What-If&rdquo; Simulator
        </h1>
        <p className="text-sm sm:text-base text-slate-600 mt-1">
          Estimate true causal downstream impacts of lifestyle and academic interventions on depression severity, attendance, and CGPA with 95% Confidence Intervals.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Intervention Controls */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center space-x-2 pb-3 border-b border-slate-100">
            <Sliders className="w-5 h-5 text-indigo-600" />
            <h2 className="font-bold text-slate-800 text-base">Hypothetical Interventions (&Delta; Shifts)</h2>
          </div>

          <div className="space-y-4 text-xs sm:text-sm">
            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>&Delta; Sleep Duration (hrs/night)</span>
                <span className="font-bold text-indigo-600">
                  {interventions.sleep_hours > 0 ? `+${interventions.sleep_hours}` : interventions.sleep_hours} hrs
                </span>
              </div>
              <input
                type="range"
                min="-3.0"
                max="3.0"
                step="0.5"
                value={interventions.sleep_hours}
                onChange={(e) => setInterventions({ ...interventions, sleep_hours: parseFloat(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>&Delta; Screen Time (hrs/day)</span>
                <span className="font-bold text-indigo-600">
                  {interventions.screen_time_hours > 0 ? `+${interventions.screen_time_hours}` : interventions.screen_time_hours} hrs
                </span>
              </div>
              <input
                type="range"
                min="-5.0"
                max="5.0"
                step="0.5"
                value={interventions.screen_time_hours}
                onChange={(e) => setInterventions({ ...interventions, screen_time_hours: parseFloat(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>&Delta; Academic Pressure (1-5 scale)</span>
                <span className="font-bold text-indigo-600">
                  {interventions.academic_pressure > 0 ? `+${interventions.academic_pressure}` : interventions.academic_pressure}
                </span>
              </div>
              <input
                type="range"
                min="-3.0"
                max="3.0"
                step="0.5"
                value={interventions.academic_pressure}
                onChange={(e) => setInterventions({ ...interventions, academic_pressure: parseFloat(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>&Delta; Social Support (1-5 scale)</span>
                <span className="font-bold text-indigo-600">
                  {interventions.social_support > 0 ? `+${interventions.social_support}` : interventions.social_support}
                </span>
              </div>
              <input
                type="range"
                min="-3.0"
                max="3.0"
                step="0.5"
                value={interventions.social_support}
                onChange={(e) => setInterventions({ ...interventions, social_support: parseFloat(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>&Delta; Financial Stress (1-5 scale)</span>
                <span className="font-bold text-indigo-600">
                  {interventions.financial_stress > 0 ? `+${interventions.financial_stress}` : interventions.financial_stress}
                </span>
              </div>
              <input
                type="range"
                min="-3.0"
                max="3.0"
                step="0.5"
                value={interventions.financial_stress}
                onChange={(e) => setInterventions({ ...interventions, financial_stress: parseFloat(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>
          </div>

          <button
            onClick={handleSimulate}
            disabled={loading}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl transition shadow flex items-center justify-center space-x-2 disabled:bg-indigo-300"
          >
            {loading ? (
              <span>Simulating Causal DAG...</span>
            ) : (
              <>
                <Brain className="w-4 h-4" />
                <span>Simulate Causal What-If</span>
              </>
            )}
          </button>
        </div>

        {/* Counterfactual Simulation Results */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-xl text-sm flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 shrink-0 text-red-500 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {!result && !loading && !error && (
            <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-white border border-dashed border-slate-300 rounded-2xl p-8 text-center text-slate-500 space-y-3">
              <Brain className="w-12 h-12 text-slate-400 stroke-[1.5]" />
              <h3 className="font-semibold text-slate-700 text-lg">Select Interventions to Simulate</h3>
              <p className="text-xs sm:text-sm max-w-sm">
                Adjust delta shifts on the left (e.g. +1.5 hrs sleep, -2 hrs screen time) to calculate downstream causal shifts on student attendance and academic performance.
              </p>
            </div>
          )}

          {result && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="font-bold text-slate-900 text-base">
                  Estimated Counterfactual Shifts with 95% CIs
                </h3>
                <span className="text-xs bg-indigo-50 text-indigo-700 border border-indigo-200 px-2.5 py-1 rounded-full font-semibold">
                  EconML LinearDML &bull; DoWhy SCM
                </span>
              </div>

              {/* Outcome Comparison Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-500 font-semibold uppercase">Depression Score</span>
                  <div className="flex items-baseline space-x-2 mt-1">
                    <span className="text-2xl font-bold text-slate-900">
                      {result.counterfactual_outcomes.depression_score.toFixed(1)}
                    </span>
                    <span className="text-xs text-slate-400">/ 27</span>
                  </div>
                  <div className="flex items-center mt-2 text-xs font-semibold text-emerald-600">
                    <ArrowDownRight className="w-4 h-4 mr-0.5" />
                    <span>{result.predicted_deltas.depression_score.toFixed(2)} pts</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    95% CI: [{result.confidence_intervals_95.depression_score[0]}, {result.confidence_intervals_95.depression_score[1]}]
                  </div>
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-500 font-semibold uppercase">Attendance Rate</span>
                  <div className="flex items-baseline space-x-2 mt-1">
                    <span className="text-2xl font-bold text-slate-900">
                      {result.counterfactual_outcomes.attendance_rate.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center mt-2 text-xs font-semibold text-emerald-600">
                    <ArrowUpRight className="w-4 h-4 mr-0.5" />
                    <span>+{result.predicted_deltas.attendance_rate.toFixed(2)}%</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    95% CI: [{result.confidence_intervals_95.attendance_rate[0]}%, {result.confidence_intervals_95.attendance_rate[1]}%]
                  </div>
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-500 font-semibold uppercase">Cumulative CGPA</span>
                  <div className="flex items-baseline space-x-2 mt-1">
                    <span className="text-2xl font-bold text-slate-900">
                      {result.counterfactual_outcomes.cgpa.toFixed(2)}
                    </span>
                    <span className="text-xs text-slate-400">/ 10</span>
                  </div>
                  <div className="flex items-center mt-2 text-xs font-semibold text-emerald-600">
                    <ArrowUpRight className="w-4 h-4 mr-0.5" />
                    <span>+{result.predicted_deltas.cgpa.toFixed(2)} pts</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    95% CI: [{result.confidence_intervals_95.cgpa[0]}, {result.confidence_intervals_95.cgpa[1]}]
                  </div>
                </div>
              </div>

              {/* Narrative Summary */}
              <div className="p-4 bg-indigo-50/60 border border-indigo-200 rounded-xl text-xs sm:text-sm text-indigo-950 leading-relaxed">
                <strong>Causal Narrative:</strong> {result.plain_english_summary}
              </div>

              {/* Assumptions & Methodology */}
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Identification Assumptions & Causal Graph
                </h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {result.causal_assumptions}. Direct causal effects identify unconfounded shifts by conditioning on baseline confounders (Age, Gender, Financial Stress) and blocking backdoor paths.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
