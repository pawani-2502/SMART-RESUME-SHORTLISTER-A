"use client";

import Link from "next/link";
import { ArrowRight, Brain, Shield, Zap, BarChart3, Rocket, Mail, Github, Linkedin } from "lucide-react";
import { AboutHeader } from "../components/AboutHeader";
import { DEVELOPER, PROJECT } from "../../config/demo.config";
import { demoData } from "../../shared/data/load-demo-data";
import { ShowcaseThemeProvider } from "../../shared/components/ThemeProvider";
import { ShowcaseCard, ShowcaseButton, ShowcaseBadge } from "../../shared/components/ui";
import { FadeIn, StaggerList, StaggerItem } from "../../shared/animations/motion";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import "../../shared/styles/showcase.css";

function Section({ id, children, className }: { id?: string; children: React.ReactNode; className?: string }) {
  return <section id={id} className={`py-16 sm:py-24 ${className ?? ""}`}>{children}</section>;
}

export function AboutPageContent() {
  const analytics = demoData.analytics;

  return (
    <div className="min-h-screen">
      <AboutHeader />
      {/* Hero */}
      <Section className="relative overflow-hidden pt-12">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <FadeIn>
            <ShowcaseBadge>Portfolio Showcase</ShowcaseBadge>
            <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl">
              <span className="text-primary">{PROJECT.name}</span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">{PROJECT.tagline}</p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <Link href="/demo?mode=examiner"><ShowcaseButton><PlayIcon /> Start Demo</ShowcaseButton></Link>
              <Link href="/login"><ShowcaseButton variant="secondary">Explore Platform</ShowcaseButton></Link>
            </div>
          </FadeIn>
        </div>
      </Section>

      {/* Screenshots / UI Showcase */}
      <Section id="screenshots">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-10 text-center text-3xl font-bold">Platform Screenshots</h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { title: "Rankings Dashboard", desc: "AI-ranked shortlist with evidence-backed scores", gradient: "from-blue-500/20 to-blue-600/10" },
              { title: "Shadow Interview", desc: "Simulated interview with readiness scoring", gradient: "from-purple-500/20 to-purple-600/10" },
              { title: "Analytics Hub", desc: "Hiring funnel, score distribution, skill heatmaps", gradient: "from-emerald-500/20 to-emerald-600/10" },
              { title: "Candidate Comparison", desc: "Side-by-side multi-candidate evaluation", gradient: "from-amber-500/20 to-amber-600/10" },
              { title: "Screening Tests", desc: "Auto-generated skill verification assessments", gradient: "from-rose-500/20 to-rose-600/10" },
              { title: "Interview Packs", desc: "Tailored technical and behavioral question sets", gradient: "from-cyan-500/20 to-cyan-600/10" },
            ].map((s) => (
              <ShowcaseCard key={s.title} className="overflow-hidden p-0">
                <div className={`flex h-36 items-center justify-center bg-gradient-to-br ${s.gradient}`}>
                  <span className="rounded-lg bg-white/80 px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm">{s.title}</span>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold">{s.title}</h3>
                  <p className="mt-1 text-sm text-slate-600">{s.desc}</p>
                </div>
              </ShowcaseCard>
            ))}
          </div>
        </div>
      </Section>

      {/* Project Vision */}
      <Section id="vision-detail">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <h2 className="text-3xl font-bold text-slate-900">Project Vision</h2>
          <p className="mt-4 text-lg text-slate-600">
            Build the most transparent, evidence-grounded AI hiring platform — where recruiters trust every ranking,
            candidates understand every decision, and organizations hire better, faster, and fairer.
          </p>
        </div>
      </Section>

      {/* Screenshots / UI Showcase */}
      <Section id="screenshots">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-10 text-center text-3xl font-bold">Platform Screenshots</h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { title: "Rankings Dashboard", desc: "AI-ranked shortlist with evidence-backed scores", gradient: "from-blue-500/20 to-blue-600/10" },
              { title: "Shadow Interview", desc: "Simulated interview with readiness scoring", gradient: "from-purple-500/20 to-purple-600/10" },
              { title: "Analytics Hub", desc: "Hiring funnel, skill heatmaps, score distribution", gradient: "from-emerald-500/20 to-emerald-600/10" },
              { title: "Candidate Comparison", desc: "Side-by-side multi-candidate evaluation", gradient: "from-amber-500/20 to-amber-600/10" },
              { title: "Interview Packs", desc: "Auto-generated technical & behavioral questions", gradient: "from-rose-500/20 to-rose-600/10" },
              { title: "Recruiter Copilot", desc: "AI assistant for hiring decisions", gradient: "from-cyan-500/20 to-cyan-600/10" },
            ].map((s) => (
              <ShowcaseCard key={s.title} className={`overflow-hidden bg-gradient-to-br ${s.gradient}`}>
                <div className="mb-4 flex h-32 items-center justify-center rounded-lg border border-slate-200/50 bg-white/60">
                  <BarChart3 className="h-12 w-12 text-primary/40" />
                </div>
                <h3 className="font-semibold">{s.title}</h3>
                <p className="mt-1 text-sm text-slate-600">{s.desc}</p>
              </ShowcaseCard>
            ))}
          </div>
        </div>
      </Section>

      {/* Project Vision */}
      <Section id="vision-detail">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <h2 className="text-3xl font-bold text-slate-900">Project Vision</h2>
          <p className="mt-4 text-lg text-slate-600">
            Build the most transparent, evidence-grounded AI hiring platform — where recruiters trust every ranking,
            candidates receive fair evaluation, and hiring decisions are explainable to the last resume snippet.
          </p>
        </div>
      </Section>

      {/* Vision */}
      <Section id="vision">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <h2 className="text-3xl font-bold text-slate-900">Vision</h2>
          <p className="mt-4 text-lg text-slate-600">
            Transform recruitment from keyword matching into evidence-grounded, explainable AI intelligence —
            where every hiring decision is transparent, auditable, and fair.
          </p>
        </div>
      </Section>

      {/* Problem */}
      <Section id="problem">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-8 text-center text-3xl font-bold">Why ATS Systems Fail</h2>
          <div className="grid gap-6 md:grid-cols-2">
            <ShowcaseCard className="border-red-200 bg-red-50">
              <h3 className="font-semibold text-red-700">The Problem</h3>
              <ul className="mt-4 space-y-2 text-sm text-slate-600">
                <li>• Keyword filters miss qualified candidates</li>
                <li>• No explainability for ranking decisions</li>
                <li>• Resume spam overwhelms recruiters</li>
                <li>• Hidden talent lost to rigid matching</li>
              </ul>
            </ShowcaseCard>
            <ShowcaseCard glow>
              <h3 className="font-semibold text-emerald-700">Our Solution</h3>
              <ul className="mt-4 space-y-2 text-sm text-slate-600">
                <li>• 24+ AI modules for deep candidate understanding</li>
                <li>• Every score backed by resume evidence</li>
                <li>• Shadow interviews and recruiter copilot</li>
                <li>• Career trajectory and skill graph analysis</li>
              </ul>
            </ShowcaseCard>
          </div>
        </div>
      </Section>

      {/* Core Features */}
      <Section id="features">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-10 text-center text-3xl font-bold">Core Features</h2>
          <StaggerList className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { icon: Brain, title: "JD Intelligence", desc: "Parse and analyze job descriptions" },
              { icon: Shield, title: "Evidence Grounding", desc: "Every claim cites resume proof" },
              { icon: Zap, title: "Shadow Interview", desc: "AI interview simulation" },
              { icon: BarChart3, title: "Analytics", desc: "Hiring funnel and insights" },
            ].map((f) => (
              <StaggerItem key={f.title}>
                <ShowcaseCard>
                  <f.icon className="mb-3 h-8 w-8 text-primary" />
                  <h3 className="font-semibold">{f.title}</h3>
                  <p className="mt-1 text-sm text-slate-600">{f.desc}</p>
                </ShowcaseCard>
              </StaggerItem>
            ))}
          </StaggerList>
        </div>
      </Section>

      {/* AI Pipeline */}
      <Section id="pipeline">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <h2 className="text-3xl font-bold">AI Pipeline</h2>
          <div className="mt-8 flex flex-wrap justify-center gap-2 text-sm">
            {["JD Parse", "Resume Parse", "Retrieval", "Rerank", "Score", "Evidence", "Rank"].map((s, i) => (
              <span key={s} className="flex items-center gap-2">
                <span className="rounded-lg bg-blue-500/20 px-3 py-1.5 font-medium">{s}</span>
                {i < 6 && <ArrowRight className="h-4 w-4 text-slate-600" />}
              </span>
            ))}
          </div>
        </div>
      </Section>

      {/* Architecture */}
      <Section id="architecture">
        <div className="mx-auto max-w-lg px-6">
          <h2 className="mb-8 text-center text-3xl font-bold">Architecture</h2>
          {["Next.js Frontend", "FastAPI Backend", "AI Engines", "PostgreSQL + FAISS", "LLM Providers"].map((l) => (
            <ShowcaseCard key={l} className="mb-2 text-center font-medium">{l}</ShowcaseCard>
          ))}
        </div>
      </Section>

      {/* Tech Stack */}
      <Section id="tech">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-8 text-center text-3xl font-bold">Technology Stack</h2>
          <div className="flex flex-wrap justify-center gap-3">
            {["Next.js", "TypeScript", "FastAPI", "PostgreSQL", "FAISS", "Redis", "Celery", "Gemini", "Docker"].map((t) => (
              <span key={t} className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium shadow-sm">{t}</span>
            ))}
          </div>
        </div>
      </Section>

      {/* Analytics Showcase */}
      <Section id="analytics">
        <div className="mx-auto max-w-4xl px-6">
          <h2 className="mb-8 text-center text-3xl font-bold">Analytics Showcase</h2>
          <ShowcaseCard className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.score_distribution}>
                <XAxis dataKey="range" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ShowcaseCard>
        </div>
      </Section>

      {/* Statistics */}
      <Section id="stats">
        <div className="mx-auto grid max-w-4xl grid-cols-2 gap-4 px-6 sm:grid-cols-4">
          {[
            { label: "AI Features", value: "32+" },
            { label: "Engines", value: "24+" },
            { label: "Agents", value: "4" },
            { label: "Modules", value: "6" },
          ].map((s) => (
            <ShowcaseCard key={s.label} className="text-center">
              <p className="text-3xl font-bold text-primary">{s.value}</p>
              <p className="text-sm text-slate-600">{s.label}</p>
            </ShowcaseCard>
          ))}
        </div>
      </Section>

      {/* Developer Profile */}
      <Section id="developer">
        <div className="mx-auto max-w-xl px-6">
          <h2 className="mb-8 text-center text-3xl font-bold">Developer Profile</h2>
          <ShowcaseCard className="text-center" glow>
            <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 text-2xl font-bold text-primary">PS</div>
            <h3 className="text-2xl font-bold">{DEVELOPER.name}</h3>
            <p className="text-slate-600">{DEVELOPER.program}</p>
            <p className="mt-1 font-medium">{DEVELOPER.institution}</p>
            <p className="text-slate-600">{DEVELOPER.campus}</p>
            <div className="mt-4 flex justify-center gap-3">
              <a href={DEVELOPER.links.github}><Github className="h-5 w-5 text-slate-600 hover:text-primary" /></a>
              <a href={DEVELOPER.links.linkedin}><Linkedin className="h-5 w-5 text-slate-600 hover:text-primary" /></a>
              <a href={DEVELOPER.links.email}><Mail className="h-5 w-5 text-slate-600 hover:text-primary" /></a>
            </div>
          </ShowcaseCard>
        </div>
      </Section>

      {/* Roadmap */}
      <Section id="roadmap">
        <div className="mx-auto max-w-2xl px-6">
          <h2 className="mb-8 text-center text-3xl font-bold">Future Roadmap</h2>
          <div className="space-y-3">
            {["Feedback Learning", "Predictive Hiring", "ATS Integrations", "Enterprise SSO", "Video Interview AI"].map((r, i) => (
              <ShowcaseCard key={r} className="flex items-center gap-3">
                <Rocket className="h-5 w-5 text-primary" />
                <span>{r}</span>
              </ShowcaseCard>
            ))}
          </div>
        </div>
      </Section>

      {/* Contact + Footer */}
      <footer className="border-t border-slate-200 py-12">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <p className="text-lg font-semibold">{PROJECT.name}</p>
          <p className="mt-2 text-slate-600">Built by {DEVELOPER.name}</p>
          <div className="mt-6 flex justify-center gap-4">
            <Link href="/demo?mode=quick"><ShowcaseButton variant="secondary">Quick Demo</ShowcaseButton></Link>
            <Link href="/demo?mode=examiner"><ShowcaseButton>Full Walkthrough</ShowcaseButton></Link>
          </div>
          <p className="mt-8 text-xs text-slate-600">© 2026 Smart Resume Shortlister-A</p>
        </div>
      </footer>
    </div>
  );
}

function PlayIcon() {
  return <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>;
}

export function ShowcaseAboutEntry() {
  return (
    <ShowcaseThemeProvider>
      <AboutPageContent />
    </ShowcaseThemeProvider>
  );
}
