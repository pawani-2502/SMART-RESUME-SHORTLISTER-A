"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowDown, Github, Linkedin, Mail, Globe } from "lucide-react";
import { DEVELOPER, PROJECT } from "../../../config/demo.config";
import { ShowcaseCard, ShowcaseBadge, ShowcaseButton } from "../../../shared/components/ui";
import { useWalkthrough } from "../../../walkthrough-engine";

function StepHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-8 text-center">
      <ShowcaseBadge>{subtitle}</ShowcaseBadge>
      <h2 className="mt-3 text-2xl font-bold sm:text-3xl">{title}</h2>
    </div>
  );
}

const ARCH_LAYERS = [
  { name: "Frontend", tech: "Next.js 15 · React · Tailwind" },
  { name: "FastAPI", tech: "REST API · Auth · Rate Limiting" },
  { name: "AI Services", tech: "24+ Engines · LangGraph Agents" },
  { name: "PostgreSQL", tech: "Jobs · Candidates · Rankings" },
  { name: "FAISS", tech: "Per-Job Vector Indices" },
  { name: "LLM Providers", tech: "Gemini · Groq · Ollama" },
];

export function StepSystemArchitecture() {
  return (
    <>
      <StepHeader title="System Architecture" subtitle="End-to-End Design" />
      <div className="mx-auto max-w-lg space-y-2">
        {ARCH_LAYERS.map((layer, i) => (
          <motion.div key={layer.name} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.12 }}>
            <ShowcaseCard className="text-center">
              <p className="font-bold">{layer.name}</p>
              <p className="text-xs text-slate-600">{layer.tech}</p>
            </ShowcaseCard>
            {i < ARCH_LAYERS.length - 1 && <div className="flex justify-center py-1"><ArrowDown className="h-4 w-4 text-primary" /></div>}
          </motion.div>
        ))}
      </div>
    </>
  );
}

const TECH_STACK = {
  Frontend: ["Next.js 15", "TypeScript", "Tailwind CSS", "ShadCN UI", "Recharts", "Framer Motion"],
  Backend: ["FastAPI", "Python 3.11", "SQLAlchemy", "Pydantic", "Celery"],
  Database: ["PostgreSQL 16", "Redis", "FAISS"],
  AI: ["sentence-transformers", "Cross-Encoder", "LangGraph", "Gemini", "Groq"],
  Infrastructure: ["Docker", "GitHub Actions", "Sentry", "SSE Progress"],
  Deployment: ["Vercel", "Railway", "Render", "DigitalOcean"],
};

export function StepTechStack() {
  return (
    <>
      <StepHeader title="Technology Stack" subtitle="Production-Grade" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(TECH_STACK).map(([category, items], i) => (
          <motion.div key={category} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.08 }}>
            <ShowcaseCard>
              <h4 className="mb-3 font-semibold text-primary">{category}</h4>
              <div className="flex flex-wrap gap-2">
                {items.map((t) => <span key={t} className="rounded-lg bg-slate-100 px-2 py-1 text-xs">{t}</span>)}
              </div>
            </ShowcaseCard>
          </motion.div>
        ))}
      </div>
    </>
  );
}

const FEATURE_GROUPS = [
  { title: "AI Features", count: 14, items: ["JD Intelligence", "Resume Parsing", "Hybrid Retrieval", "Scoring Engine", "Shadow Interview", "Skill Graph", "Temporal Decay"] },
  { title: "Recruiter Features", count: 10, items: ["Rankings", "Screening Tests", "Interview Packs", "Copilot", "Comparison", "Exports", "Audit Logs"] },
  { title: "Analytics", count: 4, items: ["Hiring Funnel", "Score Distribution", "Skill Heatmaps", "JD Quality"] },
  { title: "Infrastructure", count: 4, items: ["Celery Workers", "Redis Queue", "SSE Progress", "Rate Limiting"] },
];

export function StepFeatureShowcase() {
  return (
    <>
      <StepHeader title="Feature Showcase" subtitle={`${PROJECT.featureCount}+ Capabilities`} />
      <div className="grid gap-4 sm:grid-cols-2">
        {FEATURE_GROUPS.map((g, i) => (
          <ShowcaseCard key={g.title}>
            <div className="mb-3 flex items-center justify-between">
              <h4 className="font-semibold">{g.title}</h4>
              <ShowcaseBadge variant="success">{g.count}</ShowcaseBadge>
            </div>
            <ul className="space-y-1 text-sm text-slate-600">{g.items.map((item) => <li key={item}>✓ {item}</li>)}</ul>
          </ShowcaseCard>
        ))}
      </div>
    </>
  );
}

export function StepDeveloperProfile() {
  const d = DEVELOPER;
  return (
    <>
      <StepHeader title="Developer Profile" subtitle="Meet the Builder" />
      <ShowcaseCard className="mx-auto max-w-xl text-center" glow>
        <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 text-2xl font-bold text-primary">
          {d.name.split(" ").map((n) => n[0]).join("")}
        </div>
        <h3 className="text-2xl font-bold">{d.name}</h3>
          <p className="text-slate-600">{d.program}</p>
          {d.year && <p className="text-slate-600">{d.year}</p>}
        <p className="mt-2 font-medium">{d.institution}</p>
        <p className="text-slate-600">{d.campus}</p>
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          {d.interests.map((i) => <span key={i} className="rounded-full bg-primary/10 px-3 py-1 text-xs text-primary">{i}</span>)}
        </div>
        <div className="mt-6 flex justify-center gap-3">
          <a href={d.links.github} target="_blank" rel="noreferrer"><ShowcaseButton variant="ghost" className="!px-3"><Github className="h-4 w-4" /></ShowcaseButton></a>
          <a href={d.links.linkedin} target="_blank" rel="noreferrer"><ShowcaseButton variant="ghost" className="!px-3"><Linkedin className="h-4 w-4" /></ShowcaseButton></a>
          <a href={d.links.portfolio} target="_blank" rel="noreferrer"><ShowcaseButton variant="ghost" className="!px-3"><Globe className="h-4 w-4" /></ShowcaseButton></a>
          <a href={d.links.email}><ShowcaseButton variant="ghost" className="!px-3"><Mail className="h-4 w-4" /></ShowcaseButton></a>
        </div>
      </ShowcaseCard>
    </>
  );
}

function AnimatedCounter({ target, suffix = "" }: { target: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = Math.ceil(target / 40);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) { setCount(target); clearInterval(timer); }
      else setCount(start);
    }, 30);
    return () => clearInterval(timer);
  }, [target]);
  return <span>{count}{suffix}</span>;
}

export function StepProjectImpact() {
  const stats = [
    { label: "Features", value: 32, suffix: "+" },
    { label: "AI Agents", value: 4, suffix: "" },
    { label: "Analytics Modules", value: 6, suffix: "" },
    { label: "AI Engines", value: 24, suffix: "+" },
  ];
  return (
    <>
      <StepHeader title="Project Impact" subtitle="By the Numbers" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <ShowcaseCard key={s.label} className="text-center">
            <p className="text-4xl font-bold text-primary"><AnimatedCounter target={s.value} suffix={s.suffix} /></p>
            <p className="mt-2 text-sm text-slate-600">{s.label}</p>
          </ShowcaseCard>
        ))}
      </div>
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        {["Shadow Interview", "Recruiter Copilot", "Explainable Rankings", "Evidence Grounding"].map((f) => (
          <ShowcaseCard key={f} className="text-center text-sm font-medium">{f}</ShowcaseCard>
        ))}
      </div>
    </>
  );
}

export function StepRoadmap() {
  const plans = ["Feedback Learning Loop", "Predictive Hiring Models", "ATS Integrations", "Enterprise SSO", "Video Interview Analysis"];
  return (
    <>
      <StepHeader title="Future Roadmap" subtitle="What's Next" />
      <div className="mx-auto max-w-lg space-y-3">
        {plans.map((plan, i) => (
          <motion.div key={plan} initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}>
            <ShowcaseCard className="flex items-center gap-3">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500/20 text-sm font-bold">{i + 1}</span>
              <span>{plan}</span>
            </ShowcaseCard>
          </motion.div>
        ))}
      </div>
    </>
  );
}

export function StepFinalScreen() {
  const { reset } = useWalkthrough();
  return (
    <div className="py-12 text-center">
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
        <h2 className="text-3xl font-bold">Thank You</h2>
        <p className="mt-3 text-slate-600">You have completed the guided walkthrough.</p>
      </motion.div>
      <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
        <Link href="/"><ShowcaseButton variant="ghost">Back to Home</ShowcaseButton></Link>
        <Link href="/about"><ShowcaseButton variant="secondary">View About Page</ShowcaseButton></Link>
        <Link href="/login"><ShowcaseButton>Explore Platform</ShowcaseButton></Link>
        <ShowcaseButton variant="ghost" onClick={reset}>Replay Demo</ShowcaseButton>
      </div>
    </div>
  );
}
