"use client";

import { useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";
import { Sparkles, PhoneCall, AlertTriangle, ShieldCheck, HeartHandshake, AlertCircle } from "lucide-react";
import { analyzeText, TextAnalysisResult } from "@/lib/api";

const SAMPLES = [
  {
    title: "Exam Overwhelm",
    text: "I feel completely overwhelmed by back-to-back semester midterms and project submissions. I haven't slept more than 4 hours in three days.",
  },
  {
    title: "Hostel Isolation",
    text: "Ever since shifting to the campus hostel, I feel disconnected from everyone and lonely. I miss home and find it hard to concentrate in class.",
  },
  {
    title: "Positive Coping",
    text: "Studying with my lab partner today made a huge difference. We broke the assignment into chunks and I felt much calmer afterwards.",
  },
  {
    title: "Crisis Safety Check",
    text: "I can't take this anymore and want to end it all tonight.",
  },
];

export default function TextInsightsPage() {
  const [text, setText] = useState(SAMPLES[0].text);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TextAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeText(text);
      setResult(data);
    } catch (err: any) {
      setError("Analysis request failed. Make sure the FastAPI service is running on http://localhost:8000.");
    } finally {
      setLoading(false);
    }
  };

  const emotionData = result?.emotion_probabilities
    ? Object.entries(result.emotion_probabilities).map(([key, val]) => ({
        emotion: key.replace("_", " & ").toUpperCase(),
        probability: Math.round(val * 100),
      }))
    : [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Affective Text Insights &amp; Crisis Guardrail
        </h1>
        <p className="text-sm sm:text-base text-slate-600 mt-1">
          Analyze youth reflection narratives for emotional valence, distress intensity, and emergent themes, backed by automatic crisis interception.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Text Input Panel */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="font-bold text-slate-800 text-base">Student Narrative Reflection</h2>
            <span className="text-xs text-slate-400">Non-Diagnostic NLP</span>
          </div>

          <div>
            <textarea
              rows={6}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste or write student reflection text here..."
              className="w-full border border-slate-300 rounded-xl p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-slate-800 bg-slate-50/50"
            />
          </div>

          <div>
            <span className="text-xs font-semibold text-slate-500 block mb-2">Try Sample Reflections:</span>
            <div className="flex flex-wrap gap-1.5">
              {SAMPLES.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => setText(s.text)}
                  className={`text-xs px-2.5 py-1 rounded-lg border transition ${
                    s.title.includes("Crisis")
                      ? "border-red-300 bg-red-50 text-red-700 hover:bg-red-100"
                      : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  {s.title}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading || !text.trim()}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition shadow flex items-center justify-center space-x-2 disabled:bg-blue-300"
          >
            {loading ? (
              <span>Evaluating Reflection...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Analyze Emotional Valence</span>
              </>
            )}
          </button>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-xl text-sm flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 shrink-0 text-red-500 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {!result && !loading && !error && (
            <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-white border border-dashed border-slate-300 rounded-2xl p-8 text-center text-slate-500 space-y-3">
              <Sparkles className="w-12 h-12 text-slate-400 stroke-[1.5]" />
              <h3 className="font-semibold text-slate-700 text-lg">Enter Text to Analyze</h3>
              <p className="text-xs sm:text-sm max-w-sm">
                Submit a student reflection on the left to view emotional distributions and distress severity markers.
              </p>
            </div>
          )}

          {/* Crisis Interception Screen */}
          {result?.is_crisis && (
            <div className="bg-red-50 border-2 border-red-500 rounded-2xl p-6 shadow-md space-y-5 animate-pulse-once">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-7 h-7 text-red-600 shrink-0" />
                <div>
                  <h3 className="text-lg font-extrabold text-red-950">
                    CRISIS SAFEGUARD ACTIVATED
                  </h3>
                  <p className="text-xs sm:text-sm text-red-900 mt-1 leading-relaxed">
                    {result.message}
                  </p>
                </div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-red-200 space-y-3">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-1.5">
                  <PhoneCall className="w-4 h-4 text-red-600" />
                  <span>Immediate Indian Helplines (24x7, Toll-Free)</span>
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                    <span className="font-bold text-red-950 block">Tele-MANAS (MoHFW India)</span>
                    <span className="text-lg font-black text-red-700 block mt-0.5">14416 / 1800-891-4416</span>
                    <span className="text-[10px] text-red-800">24x7 Multilingual Psychological Support</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="font-bold text-slate-900 block">National Emergency</span>
                    <span className="text-lg font-black text-slate-900 block mt-0.5">112</span>
                    <span className="text-[10px] text-slate-600">Police, Ambulance, Emergency</span>
                  </div>
                </div>
              </div>

              {result.immediate_actions && (
                <div className="text-xs text-red-900 space-y-1 bg-red-100/50 p-3 rounded-lg border border-red-200">
                  <strong className="block text-red-950">Recommended Immediate Actions:</strong>
                  {result.immediate_actions.map((act, i) => (
                    <div key={i} className="flex items-center space-x-1.5">
                      <span>&bull;</span>
                      <span>{act}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Benign Text Analysis */}
          {result && !result.is_crisis && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Primary Affective Valence
                  </span>
                  <div className="flex items-baseline space-x-3 mt-1">
                    <span className="text-2xl font-extrabold text-slate-900">
                      {result.primary_emotion}
                    </span>
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full font-bold uppercase ${
                        result.distress_tier?.includes("High")
                          ? "bg-red-100 text-red-800"
                          : result.distress_tier?.includes("Moderate")
                          ? "bg-amber-100 text-amber-800"
                          : "bg-emerald-100 text-emerald-800"
                      }`}
                    >
                      {result.distress_tier}
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-1 text-xs text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>No Crisis Indicators Detected</span>
                </div>
              </div>

              {/* Emotion Probability Distribution */}
              {emotionData.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-bold text-slate-800 text-sm">
                    Calibrated Emotion Class Probabilities (%)
                  </h3>
                  <div className="h-56 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={emotionData} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
                        <XAxis
                          dataKey="emotion"
                          tick={{ fontSize: 10 }}
                          angle={-15}
                          textAnchor="end"
                          interval={0}
                        />
                        <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                        <Tooltip formatter={(val: any) => [`${val}%`, "Confidence"]} />
                        <Bar dataKey="probability" radius={[4, 4, 0, 0]}>
                          {emotionData.map((_, idx) => (
                            <Cell
                              key={`cell-${idx}`}
                              fill={idx % 2 === 0 ? "#3b82f6" : "#6366f1"}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Extracted Topical Cue Keywords */}
              {result.topics_extracted && result.topics_extracted.length > 0 && (
                <div className="pt-2">
                  <span className="text-xs font-semibold text-slate-500 block mb-2">
                    Discovered Topical Cues:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {result.topics_extracted.map((t, idx) => (
                      <span
                        key={idx}
                        className="text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-lg font-mono"
                      >
                        #{t}
                      </span>
                    ))}
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
