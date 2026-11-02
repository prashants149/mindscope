"use client";

import { useState } from "react";
import { MessageSquare, Send, ShieldAlert, AlertTriangle, ExternalLink, Bot, User, PhoneCall, Sparkles } from "lucide-react";
import { askAssistant, AssistantResult } from "@/lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  isCrisis?: boolean;
  isDiagnosticRefusal?: boolean;
  sourcesCited?: { title: string; organization: string; url: string }[];
  emergencyHelplines?: Record<string, string>;
}

const PRESET_QUERIES = [
  "What evidence-based strategies help manage exam anxiety according to WHO?",
  "How does sleep deprivation impair memory and cognitive function?",
  "Can you diagnose whether I have clinical depression?",
  "I want to end my life tonight, I can't take this anymore.",
];

export default function AssistantPage() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hello! I am MindScope Assistant, an academic research and student support assistant. I can answer questions grounded in public mental health guidance from WHO, NIMH, Tele-MANAS, and NIMHANS. Please note that I am strictly non-diagnostic and cannot provide clinical diagnoses or prescriptions.",
    },
  ]);

  const handleSend = async (queryText?: string) => {
    const q = (queryText || input).trim();
    if (!q || loading) return;

    setInput("");
    const userMsg: ChatMessage = { role: "user", content: q };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res: AssistantResult = await askAssistant(q);
      const botMsg: ChatMessage = {
        role: "assistant",
        content: res.response_text,
        isCrisis: res.is_crisis,
        isDiagnosticRefusal: res.is_diagnostic_refusal,
        sourcesCited: res.sources_cited,
        emergencyHelplines: res.emergency_helplines,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error connecting to the guidance server. Please ensure the FastAPI backend is running on http://localhost:8000.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Safe Source-Grounded Support Assistant
        </h1>
        <p className="text-sm sm:text-base text-slate-600 mt-1">
          Evidence-based psychological well-being guidance with mandatory citations to WHO, NIMH, and Tele-MANAS. Strictly non-diagnostic.
        </p>
      </div>

      {/* Preset Buttons */}
      <div className="flex flex-wrap gap-2">
        {PRESET_QUERIES.map((preset, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(preset)}
            className="text-xs bg-white hover:bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full text-slate-700 transition shadow-sm flex items-center space-x-1"
          >
            <Sparkles className="w-3 h-3 text-blue-500" />
            <span className="truncate max-w-[280px]">{preset}</span>
          </button>
        ))}
      </div>

      {/* Chat Container */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col h-[520px] overflow-hidden">
        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
          {messages.map((m, idx) => {
            const isUser = m.role === "user";
            return (
              <div
                key={idx}
                className={`flex items-start space-x-3 ${isUser ? "flex-row-reverse space-x-reverse" : ""}`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white ${
                    isUser
                      ? "bg-blue-600"
                      : m.isCrisis
                      ? "bg-red-600"
                      : "bg-slate-700"
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                <div
                  className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 text-sm leading-relaxed ${
                    isUser
                      ? "bg-blue-600 text-white rounded-tr-none"
                      : m.isCrisis
                      ? "bg-red-50 text-red-950 border border-red-300 rounded-tl-none shadow-sm"
                      : m.isDiagnosticRefusal
                      ? "bg-amber-50 text-amber-950 border border-amber-200 rounded-tl-none"
                      : "bg-slate-100 text-slate-800 rounded-tl-none"
                  }`}
                >
                  {m.isCrisis && (
                    <div className="flex items-center space-x-1.5 font-bold text-red-700 mb-2 pb-1.5 border-b border-red-200 text-xs">
                      <AlertTriangle className="w-4 h-4 text-red-600" />
                      <span>CRISIS SAFEGUARD ACTIVATED</span>
                    </div>
                  )}

                  {m.isDiagnosticRefusal && (
                    <div className="flex items-center space-x-1.5 font-bold text-amber-800 mb-2 pb-1.5 border-b border-amber-200 text-xs">
                      <ShieldAlert className="w-4 h-4 text-amber-600" />
                      <span>NON-DIAGNOSTIC RESEARCH BOUNDARY</span>
                    </div>
                  )}

                  <div className="whitespace-pre-line">{m.content}</div>

                  {/* Crisis Helplines */}
                  {m.isCrisis && m.emergencyHelplines && (
                    <div className="mt-3 p-3 bg-white rounded-xl border border-red-200 text-xs space-y-1">
                      <strong className="block text-red-900 font-bold">Verified India 24x7 Helplines:</strong>
                      <div>Tele-MANAS: <strong>14416 / 1800-891-4416</strong> (Toll-Free)</div>
                      <div>National Emergency: <strong>112</strong></div>
                    </div>
                  )}

                  {/* Source Citations */}
                  {m.sourcesCited && m.sourcesCited.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-200/80 text-xs space-y-1">
                      <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px] block">
                        Verified Sources Consulted:
                      </span>
                      {m.sourcesCited.map((s, i) => (
                        <a
                          key={i}
                          href={s.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800 hover:underline mr-3"
                        >
                          <span>[{s.organization} - {s.title}]</span>
                          <ExternalLink className="w-3 h-3 ml-0.5" />
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {loading && (
            <div className="flex items-center space-x-2 text-xs text-slate-400 italic">
              <Bot className="w-4 h-4 animate-spin text-blue-500" />
              <span>MindScope Assistant is consulting guidance corpus...</span>
            </div>
          )}
        </div>

        {/* Chat Input Bar */}
        <div className="p-3 sm:p-4 bg-slate-50 border-t border-slate-200 flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about evidence-based coping strategies, sleep hygiene, or campus stress..."
            className="flex-1 border border-slate-300 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-800"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition shadow disabled:bg-blue-300"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
