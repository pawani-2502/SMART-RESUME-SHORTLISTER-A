"use client";

import Link from "next/link";
import { Brain } from "lucide-react";
import { ShowcaseButton } from "../../shared/components/ui";

export function AboutHeader() {
  return (
    <header className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <Brain className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold text-slate-900">Smart Shortlister</span>
        </Link>
        <div className="flex items-center gap-2">
          <Link href="/demo?mode=examiner"><ShowcaseButton variant="secondary" className="!py-2">Demo</ShowcaseButton></Link>
          <Link href="/login"><ShowcaseButton className="!py-2">Platform</ShowcaseButton></Link>
        </div>
      </div>
    </header>
  );
}
