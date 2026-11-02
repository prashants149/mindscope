import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import DisclaimerBanner from "@/components/DisclaimerBanner";

export const metadata: Metadata = {
  title: "MindScope - AI Youth Mental Health Research Platform",
  description: "Explainable and Causal AI Research System for Youth Mental Health Issues (Ages 15-25)",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 antialiased">
        <DisclaimerBanner />
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 space-y-2">
            <p>
              MindScope &copy; 2026. Final-Year B.Tech CSE (AI) Capstone Project.
            </p>
            <p>
              Academic Research Prototype. Strictly non-diagnostic. For psychological distress in India, call <strong>Tele-MANAS (14416 / 1800-891-4416)</strong> or <strong>112</strong>.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
