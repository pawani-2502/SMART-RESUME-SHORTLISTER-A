"use client";

import Link from "next/link";
import { Play, FastForward, LayoutDashboard, Brain } from "lucide-react";
import { DEVELOPER, PROJECT } from "../../config/demo.config";
import { ShowcaseButton, ShowcaseCard } from "../../shared/components/ui";
import { FadeIn } from "../../shared/animations/motion";
import { useWalkthrough } from "../../walkthrough-engine";

export function IntroScreen() {
  const { startDemo, skipToFeatures } = useWalkthrough();

  return (
    <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-3xl flex-col items-center justify-center px-6 py-16 text-center">
      <FadeIn>
        <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
          <Brain className="h-9 w-9 text-primary" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">{PROJECT.name}</h1>
        <p className="mt-2 text-lg text-slate-600">{PROJECT.tagline}</p>
      </FadeIn>

      <FadeIn delay={0.2}>
        <ShowcaseCard className="mt-10 w-full text-left">
          <p className="text-xs font-semibold uppercase tracking-wider text-primary">Built By</p>
          <p className="mt-2 text-xl font-bold text-slate-900">{DEVELOPER.name}</p>
          <p className="text-slate-600">{DEVELOPER.program}</p>
          <p className="mt-1 font-medium text-slate-900">{DEVELOPER.institution}</p>
          <p className="text-slate-600">{DEVELOPER.campus}</p>
        </ShowcaseCard>
      </FadeIn>

      <FadeIn delay={0.35} className="mt-8 flex w-full flex-col gap-3 sm:flex-row sm:justify-center">
        <ShowcaseButton onClick={startDemo} className="w-full sm:w-auto">
          <Play className="h-4 w-4" /> Start Guided Demo
        </ShowcaseButton>
        <ShowcaseButton variant="secondary" onClick={skipToFeatures} className="w-full sm:w-auto">
          <FastForward className="h-4 w-4" /> Skip To Features
        </ShowcaseButton>
        <Link href="/login" className="w-full sm:w-auto">
          <ShowcaseButton variant="ghost" className="w-full">
            <LayoutDashboard className="h-4 w-4" /> Explore Platform
          </ShowcaseButton>
        </Link>
      </FadeIn>
    </div>
  );
}
