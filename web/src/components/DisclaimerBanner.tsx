import { ShieldAlert } from "lucide-react";

export default function DisclaimerBanner() {
  return (
    <div className="bg-amber-50 border-b border-amber-200 text-amber-900 px-4 py-2 text-xs sm:text-sm">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
          <span>
            <strong>RESEARCH PROTOTYPE ONLY:</strong> MindScope is strictly an academic decision-support tool (Ages 15–25) and <strong>does NOT provide medical or psychiatric diagnoses</strong>.
          </span>
        </div>
        <div className="shrink-0 text-amber-800 hidden sm:block">
          In crisis? Call <strong>14416</strong> (Tele-MANAS) or <strong>112</strong>
        </div>
      </div>
    </div>
  );
}
