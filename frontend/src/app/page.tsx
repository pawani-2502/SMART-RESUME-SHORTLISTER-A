"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Brain, Shield, Zap, BarChart3, ArrowRight, Play, Layers, Target, Sparkles } from "lucide-react";

const SECTIONS = [
  {
    id: "problem",
    icon: Target,
    title: "The Problem",
    content: "Traditional ATS systems rely on keyword matching. Recruiters drown in resumes, miss qualified talent, and can't explain why candidates rank where they do.",
    bullets: ["Keyword filters miss strong candidates", "No explainability for decisions", "Hours wasted on manual screening", "Hidden bias in hiring pipelines"],
  },
  {
    id: "solution",
    icon: Sparkles,
    title: "Our Solution",
    content: "An AI recruitment intelligence platform that understands resumes deeply, grounds every score in evidence, and gives recruiters superpowers.",
    bullets: ["24+ AI engines analyze every resume", "Every score cites resume proof", "Shadow interviews before real calls", "Transparent, auditable rankings"],
  },
  {
    id: "features",
    icon: Zap,
    title: "Key Features",
    content: "End-to-end hiring intelligence from job description to final shortlist.",
    bullets: ["JD Intelligence & Resume Parsing", "Multi-factor Scoring Engine", "Shadow Interview Simulation", "Screening Tests & Interview Packs", "Recruiter Copilot & Analytics"],
  },
  {
    id: "architecture",
    icon: Layers,
    title: "Architecture",
    content: "Production-grade stack built for scale and explainability.",
    bullets: ["Next.js 15 frontend with real-time progress", "FastAPI backend with async workers", "PostgreSQL + Redis + Celery pipeline", "Multi-LLM AI engine layer"],
  },
  {
    id: "results",
    icon: BarChart3,
    title: "Results",
    content: "Demonstrated impact across the full hiring funnel.",
    bullets: ["91% top candidate fit score", "60% faster shortlist generation", "100% evidence-grounded rankings", "847 candidates processed in demo dataset"],
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <header className="sticky top-0 z-40 border-b bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <Brain className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold">Smart Resume Shortlister-A</span>
          </div>
          <div className="flex gap-3">
            <Link href="/about"><Button variant="ghost">About</Button></Link>
            <Link href="/login"><Button variant="outline">Sign In</Button></Link>
            <Link href="/demo?mode=examiner"><Button>Start Guided Demo</Button></Link>
          </div>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="mx-auto max-w-6xl px-6 py-20 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border bg-white px-4 py-1.5 text-sm text-slate-600 shadow-sm">
            <Sparkles className="h-4 w-4 text-primary" /> Hackathon Demo Ready — No Login Required
          </div>
          <h1 className="mt-6 text-5xl font-bold tracking-tight text-slate-900">
            AI Hiring Copilot for
            <span className="text-primary"> Evidence-Grounded </span>
            Shortlisting
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
            Go beyond keyword matching. Understand career trajectories, verify claims,
            simulate interviews, and produce transparent ranked shortlists with citations.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Link href="/demo?mode=examiner">
              <Button size="lg" className="gap-2">
                <Play className="h-5 w-5" /> Start Guided Demo
              </Button>
            </Link>
            <Link href="/demo?mode=quick">
              <Button size="lg" variant="outline">Quick Tour (2 min)</Button>
            </Link>
            <Link href="/about">
              <Button size="lg" variant="ghost">About the Project</Button>
            </Link>
          </div>
        </section>

        {/* Guided flow sections */}
        <section className="border-y bg-slate-50/50 py-20">
          <div className="mx-auto max-w-6xl px-6">
            <h2 className="mb-12 text-center text-3xl font-bold">Understand the Platform in 5 Minutes</h2>
            <div className="space-y-8">
              {SECTIONS.map((section, i) => (
                <div
                  key={section.id}
                  className="flex flex-col gap-6 rounded-2xl border bg-white p-8 shadow-sm transition-shadow hover:shadow-md md:flex-row md:items-start"
                >
                  <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-primary/10">
                    <section.icon className="h-7 w-7 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-bold text-white">{i + 1}</span>
                      <h3 className="text-xl font-bold">{section.title}</h3>
                    </div>
                    <p className="mt-3 text-slate-600">{section.content}</p>
                    <ul className="mt-4 grid gap-2 sm:grid-cols-2">
                      {section.bullets.map((b) => (
                        <li key={b} className="flex items-start gap-2 text-sm text-slate-600">
                          <ArrowRight className="mt-0.5 h-4 w-4 shrink-0 text-primary" />{b}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-12 text-center">
              <Link href="/demo?mode=examiner">
                <Button size="lg" className="gap-2">
                  <Play className="h-5 w-5" /> Start Guided Demo
                </Button>
              </Link>
              <p className="mt-3 text-sm text-slate-500">No login · No setup · No uploads required</p>
            </div>
          </div>
        </section>

        {/* Feature cards */}
        <section className="mx-auto max-w-6xl px-6 py-20">
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {[
              { icon: Brain, title: "24 AI Modules", desc: "JD intelligence, skill graphs, hybrid retrieval, shadow interviews" },
              { icon: Shield, title: "Evidence Grounded", desc: "Every score traceable to resume snippets. No unsupported claims." },
              { icon: Zap, title: "Batch Processing", desc: "Process hundreds of resumes with async queue and progress tracking" },
              { icon: BarChart3, title: "Analytics Dashboard", desc: "Hiring funnel, score distribution, skill heatmaps" },
            ].map((f, i) => (
              <div key={i} className="rounded-xl border bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
                <f.icon className="mb-4 h-10 w-10 text-primary" />
                <h3 className="text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm text-slate-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t py-8 text-center text-sm text-slate-500">
        Built by Pawani Sharma · SRM Institute of Science and Technology, Chennai
      </footer>
    </div>
  );
}
