"use client";

import { useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ReferenceLine } from "recharts";
import { AlertCircle, Sliders, Info, ShieldAlert, Sparkles, CheckCircle2 } from "lucide-react";
import { predictRisk, explainProfile, StudentProfile, ExplainResult, PredictionResult } from "@/lib/api";

export default function FactorsPage() {
  const [profile, setProfile] = useState<StudentProfile>({
    age: 20,
    gender: "Female",
    study_year: 2,
    academic_pressure: 4.2,
    study_hours: 3.5,
    sleep_hours: 5.5,
    screen_time_hours: 6.5,
    social_support: 2.5,
    financial_stress: 3.5,
    physical_activity_hours: 1.5,
  });

  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [explanation, setExplanation] = useState<ExplainResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const [predRes, expRes] = await Promise.all([
        predictRisk(profile),
        explainProfile(profile),
      ]);
      setPrediction(predRes);
      setExplanation(expRes);
    } catch (err: any) {
      setError("Failed to connect to MindScope backend. Make sure the FastAPI service is running on http://localhost:8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Factor Importance & Calibrated Risk Assessment
        </h1>
        <p className="text-sm sm:text-base text-slate-600 mt-1">
          Estimate calibrated probability of depression risk and inspect individual feature contributions using Local SHAP (SHapley Additive exPlanations).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Profile Inputs Panel */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center space-x-2 pb-3 border-b border-slate-100">
            <Sliders className="w-5 h-5 text-blue-600" />
            <h2 className="font-bold text-slate-800 text-base">Student Risk Factor Inputs</h2>
          </div>

          <div className="space-y-4 text-xs sm:text-sm">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Age: {profile.age}</label>
                <input
                  type="range"
                  min="15"
                  max="25"
                  value={profile.age}
                  onChange={(e) => setProfile({ ...profile, age: parseInt(e.target.value) })}
                  className="w-full accent-blue-600"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Gender</label>
                <select
                  value={profile.gender}
                  onChange={(e) => setProfile({ ...profile, gender: e.target.value as any })}
                  className="w-full border border-slate-300 rounded-lg p-1.5 text-xs bg-white text-slate-800"
                >
                  <option value="Female">Female</option>
                  <option value="Male">Male</option>
                  <option value="Non-Binary">Non-Binary</option>
                </select>
              </div>
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Academic Pressure (1-5)</span>
                <span className="font-bold text-blue-600">{profile.academic_pressure.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="5.0"
                step="0.1"
                value={profile.academic_pressure}
                onChange={(e) => setProfile({ ...profile, academic_pressure: parseFloat(e.target.value) })}
                className="w-full accent-blue-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Sleep Duration (hrs/night)</span>
                <span className="font-bold text-blue-600">{profile.sleep_hours.toFixed(1)} hrs</span>
              </div>
              <input
                type="range"
                min="3.0"
                max="12.0"
                step="0.5"
                value={profile.sleep_hours}
                onChange={(e) => setProfile({ ...profile, sleep_hours: parseFloat(e.target.value) })}
                className="w-full accent-blue-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Daily Screen Time (hrs/day)</span>
                <span className="font-bold text-blue-600">{profile.screen_time_hours.toFixed(1)} hrs</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="14.0"
                step="0.5"
                value={profile.screen_time_hours}
                onChange={(e) => setProfile({ ...profile, screen_time_hours: parseFloat(e.target.value) })}
                className="w-full accent-blue-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Daily Study Hours</span>
                <span className="font-bold text-blue-600">{profile.study_hours.toFixed(1)} hrs</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="12.0"
                step="0.5"
                value={profile.study_hours}
                onChange={(e) => setProfile({ ...profile, study_hours: parseFloat(e.target.value) })}
                className="w-full accent-blue-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Social Support Rating (1-5)</span>
                <span className="font-bold text-blue-600">{profile.social_support.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="5.0"
                step="0.1"
                value={profile.social_support}
                onChange={(e) => setProfile({ ...profile, social_support: parseFloat(e.target.value) })}
                className="w-full accent-blue-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Financial Stress (1-5)</span>
                <span className="font-bold text-blue-600">{profile.financial_stress.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="5.0"
                step="0.1"
                value={profile.financial_stress}
                onChange={(e) => setProfile({ ...profile, financial_stress: parseFloat(e.target.value) })}
                className="w-full accent-blue-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Weekly Physical Activity (hrs/wk)</span>
                <span className="font-bold text-blue-600">{profile.physical_activity_hours.toFixed(1)} hrs</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="15.0"
                step="0.5"
                value={profile.physical_activity_hours}
                onChange={(e) => setProfile({ ...profile, physical_activity_hours: parseFloat(e.target.value) })}
                className="w-full accent-blue-600"
              />
            </div>
          </div>

          <button
            onClick={handleRunAnalysis}
            disabled={loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition shadow flex items-center justify-center space-x-2 disabled:bg-blue-300"
          >
            {loading ? (
              <span>Computing SHAP Attributions...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Estimate Risk & Explain</span>
              </>
            )}
          </button>
        </div>

        {/* Results & SHAP Panel */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-xl text-sm flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 shrink-0 text-red-500 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {!prediction && !loading && !error && (
            <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-white border border-dashed border-slate-300 rounded-2xl p-8 text-center text-slate-500 space-y-3">
              <Sliders className="w-12 h-12 text-slate-400 stroke-[1.5]" />
              <h3 className="font-semibold text-slate-700 text-lg">Adjust Parameters & Run Analysis</h3>
              <p className="text-xs sm:text-sm max-w-sm">
                Set student lifestyle attributes on the left and click &ldquo;Estimate Risk &amp; Explain&rdquo; to view model probability and feature-level attributions.
              </p>
            </div>
          )}

          {prediction && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
              {/* Risk Probability Score */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
                <div>
                  <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
                    Calibrated Predictive Model
                  </span>
                  <div className="flex items-baseline space-x-3 mt-1">
                    <span className="text-3xl font-extrabold text-slate-900">
                      {(prediction.depression_risk_probability * 100).toFixed(1)}%
                    </span>
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full font-bold uppercase ${
                        prediction.risk_category === "High Risk"
                          ? "bg-red-100 text-red-800"
                          : prediction.risk_category === "Moderate Risk"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-emerald-100 text-emerald-800"
                      }`}
                    >
                      {prediction.risk_category}
                    </span>
                  </div>
                </div>

                <div className="text-xs text-slate-500 max-w-xs text-left sm:text-right">
                  Logistic Regression calibrated via Stratified 5-Fold Cross Validation.
                </div>
              </div>

              {/* SHAP Feature Contribution Chart */}
              {explanation && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-slate-800 text-sm">
                      SHAP Local Feature Contributions (Impact on Log-Odds)
                    </h3>
                    <span className="text-xs text-slate-500">Base value: {explanation.base_value.toFixed(2)}</span>
                  </div>

                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={explanation.contributions}
                        layout="vertical"
                        margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                      >
                        <XAxis type="number" tick={{ fontSize: 11 }} />
                        <YAxis
                          type="category"
                          dataKey="display_name"
                          tick={{ fontSize: 11 }}
                          width={110}
                        />
                        <Tooltip
                          formatter={(val: any) => [`${Number(val).toFixed(3)} SHAP value`, "Impact"]}
                        />
                        <ReferenceLine x={0} stroke="#94a3b8" />
                        <Bar dataKey="shap_value" radius={[4, 4, 4, 4]}>
                          {explanation.contributions.map((entry, idx) => (
                            <Cell
                              key={`cell-${idx}`}
                              fill={entry.shap_value > 0 ? "#ef4444" : "#3b82f6"}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Summary Breakdown */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                    <div className="p-3 bg-red-50 border border-red-200 rounded-xl">
                      <h4 className="text-xs font-bold text-red-900 uppercase tracking-wider mb-1.5">
                        Top Risk Escalators
                      </h4>
                      <ul className="text-xs text-red-800 space-y-1">
                        {explanation.top_risk_escalators.map((item, idx) => (
                          <li key={idx} className="flex justify-between">
                            <span>{item.display_name}</span>
                            <span className="font-bold">+{item.shap_value.toFixed(3)}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl">
                      <h4 className="text-xs font-bold text-blue-900 uppercase tracking-wider mb-1.5">
                        Top Protective Factors
                      </h4>
                      <ul className="text-xs text-blue-800 space-y-1">
                        {explanation.top_protective_factors.map((item, idx) => (
                          <li key={idx} className="flex justify-between">
                            <span>{item.display_name}</span>
                            <span className="font-bold">{item.shap_value.toFixed(3)}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Plain English Summary */}
                  <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 leading-relaxed">
                    <strong>Interpretation:</strong> {explanation.plain_english_summary}
                  </div>

                  {/* Epistemic Guardrail Banner */}
                  <div className="p-3.5 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-start space-x-2">
                    <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                    <p className="leading-relaxed">
                      <strong>CAUSAL WARNING:</strong> {explanation.epistemic_warning}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
