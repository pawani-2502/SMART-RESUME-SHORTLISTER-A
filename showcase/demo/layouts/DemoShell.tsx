"use client";

import Link from "next/link";
import { Brain, Home, Info } from "lucide-react";
import { ShowcaseButton } from "../../shared/components/ui";
import { useWalkthrough } from "../../walkthrough-engine";
import { DemoControls } from "../components/DemoControls";

export function DemoShell({ children }: { children: React.ReactNode }) {
  const { phase } = useWalkthrough();

  return (
    <div className="flex min-h-screen flex-col">
      <header className="showcase-no-print sticky top-0 z-50 border-b bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2">
            <Brain className="h-7 w-7 text-primary" />
            <span className="text-lg font-bold text-slate-900">Smart Shortlister</span>
            <span className="hidden text-sm text-muted-foreground sm:inline">· Demo</span>
          </Link>
          <div className="flex items-center gap-2">
            <Link href="/about"><ShowcaseButton variant="ghost" className="!px-3 !py-2"><Info className="h-4 w-4" /></ShowcaseButton></Link>
            <Link href="/"><ShowcaseButton variant="ghost" className="!px-3 !py-2"><Home className="h-4 w-4" /></ShowcaseButton></Link>
          </div>
        </div>
        {phase === "walkthrough" && <DemoControls />}
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
}
