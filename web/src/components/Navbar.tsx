"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, Brain, Compass, MessageSquare, ShieldAlert, Sparkles, AlertCircle } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Overview", href: "/", icon: Compass },
    { name: "Factor Importance", href: "/factors", icon: Activity },
    { name: "Causal What-If", href: "/whatif", icon: Brain },
    { name: "Text Insights", href: "/text-insights", icon: Sparkles },
    { name: "Support Assistant", href: "/assistant", icon: MessageSquare },
    { name: "Limitations & Ethics", href: "/limitations", icon: ShieldAlert },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-sm">
                M
              </div>
              <div>
                <span className="font-bold text-lg text-slate-900 tracking-tight">MindScope</span>
                <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                  Research AI (Ages 15-25)
                </span>
              </div>
            </Link>
          </div>

          <nav className="hidden md:flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-700 font-semibold"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center space-x-2">
            <div className="hidden lg:flex items-center space-x-1 text-xs bg-red-50 text-red-700 border border-red-200 px-2.5 py-1.5 rounded-lg">
              <AlertCircle className="w-3.5 h-3.5 text-red-600" />
              <span>Helpline: <strong>Tele-MANAS 14416</strong></span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
