"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { X, Check, ArrowDown } from "lucide-react";
import { ShowcaseCard, ShowcaseBadge } from "../../../shared/components/ui";
import { StaggerList, StaggerItem, SlideIn } from "../../../shared/animations/motion";
import { useWalkthrough } from "../../../walkthrough-engine";
import { formatPct } from "../../../shared/utils";

function StepHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-8 text-center">
      <ShowcaseBadge>{subtitle}</ShowcaseBadge>
      <h2 className="mt-3 text-2xl font-bold sm:text-3xl">{title}</h2>
    </div>
  );
}

export function StepProblemStatement() {
  const traditional = ["Keyword Matching", "Hidden Talent Loss", "Resume Spam", "No Explainability"];
  const ours = ["Explainable AI", "Career Trajectory Analysis", "Temporal Skill Decay", "Shadow Interview", "Recruiter Copilot"];
  return (
    <>
      <StepHeader title="Why Traditional ATS Systems Fail" subtitle="Problem Statement" />
      <div className="grid gap-6 md:grid-cols-2">
        <SlideIn direction="left">
          <ShowcaseCard className="border-red-500/20">
            <h3 className="mb-4 font-semibold text-red-700">Traditional ATS</h3>
            <StaggerList className="space-y-3">
              {traditional.map((item) => (
                <StaggerItem key={item} className="flex items-center gap-2 text-sm">
                  <X className="h-4 w-4 shrink-0 text-red-500" /> {item}
                </StaggerItem>
              ))}
            </StaggerList>
          </ShowcaseCard>
        </SlideIn>
        <SlideIn direction="right">
          <ShowcaseCard glow>
            <h3 className="mb-4 font-semibold text-emerald-700">Our Platform</h3>
            <StaggerList className="space-y-3">
              {ours.map((item) => (
                <StaggerItem key={item} className="flex items-center gap-2 text-sm">
                  <Check className="h-4 w-4 shrink-0 text-emerald-600" /> {item}
                </StaggerItem>
              ))}
            </StaggerList>
          </ShowcaseCard>
        </SlideIn>
      </div>
    </>
  );
}

export function StepJDIntelligence() {
  const { data } = useWalkthrough();
  const job = data.job;
  const skills = job.parsed_data.required_skills as { name: string }[];
  const soft = job.parsed_data.soft_skills as string[];
  return (
    <>
      <StepHeader title="Job Description Intelligence" subtitle="AI Analysis Pipeline" />
      <div className="mb-6 flex flex-col items-center gap-2 text-sm text-slate-600">
        <motion.span animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 2 }}>Input JD</motion.span>
        <ArrowDown className="h-4 w-4" />
        <span className="font-medium text-primary">AI Analysis</span>
        <ArrowDown className="h-4 w-4" />
        <span>Extracted Intelligence</span>
      </div>
      <ShowcaseCard className="mb-6"><p className="text-sm text-slate-600">{job.description}</p></ShowcaseCard>
      <div className="grid gap-4 sm:grid-cols-2">
        <ShowcaseCard>
          <h4 className="mb-3 font-semibold">Must-Have Skills</h4>
          <div className="flex flex-wrap gap-2">
            {skills.slice(0, 6).map((s, i) => (
              <motion.span key={i} initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: i * 0.08 }}
                className="rounded-lg bg-primary/10 px-3 py-1 text-xs font-medium">{s.name}</motion.span>
            ))}
          </div>
        </ShowcaseCard>
        <ShowcaseCard>
          <h4 className="mb-3 font-semibold">Soft Skills</h4>
          <div className="flex flex-wrap gap-2">
            {soft.map((s, i) => <span key={i} className="rounded-lg bg-primary/10 px-3 py-1 text-xs text-primary">{s}</span>)}
          </div>
        </ShowcaseCard>
      </div>
    </>
  );
}

export function StepResumeIntelligence() {
  const { data } = useWalkthrough();
  const c = data.resumes.candidates[0];
  const sections = [
    { label: "Skills", items: c.skills },
    { label: "Projects", items: c.projects },
    { label: "Experience", items: c.experience.map((e) => `${e.title} @ ${e.company}`) },
    { label: "Education", items: c.education.map((e) => `${e.degree}, ${e.institution}`) },
    { label: "Certifications", items: c.certifications },
    { label: "Achievements", items: c.achievements },
  ];
  return (
    <>
      <StepHeader title="Resume Intelligence" subtitle={c.name} />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sections.map((sec, i) => (
          <motion.div key={sec.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <ShowcaseCard>
              <h4 className="mb-2 font-semibold text-primary">{sec.label}</h4>
              <ul className="space-y-1 text-sm text-slate-600">{sec.items.map((item, j) => <li key={j}>• {item}</li>)}</ul>
            </ShowcaseCard>
          </motion.div>
        ))}
      </div>
    </>
  );
}

export function StepCareerTrajectory() {
  const roles = ["Intern", "Junior Developer", "Software Engineer", "Senior Engineer"];
  const metrics = [
    { label: "Trajectory Score", value: "88%" },
    { label: "Growth Potential", value: "High" },
    { label: "Promotion Velocity", value: "1.2 yrs/level" },
    { label: "Leadership Growth", value: "Strong" },
  ];
  return (
    <>
      <StepHeader title="Career Trajectory Analysis" subtitle="Growth Timeline" />
      <div className="mb-8 flex flex-wrap items-center justify-center gap-2">
        {roles.map((role, i) => (
          <div key={role} className="flex items-center gap-2">
            <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.2 }}
              className="rounded-xl border border-blue-500/30 bg-primary/10 px-4 py-2 text-sm font-medium">{role}</motion.div>
            {i < roles.length - 1 && <span className="text-primary">→</span>}
          </div>
        ))}
      </div>
      <div className="grid gap-4 sm:grid-cols-4">
        {metrics.map((m) => (
          <ShowcaseCard key={m.label} className="text-center">
            <p className="text-xs text-slate-600">{m.label}</p>
            <p className="mt-1 text-xl font-bold text-primary">{m.value}</p>
          </ShowcaseCard>
        ))}
      </div>
    </>
  );
}

export function StepTemporalSkillDecay() {
  const examples = [
    { skill: "React", year: "2026", score: 95, fresh: true },
    { skill: "React", year: "2020", score: 42, fresh: false },
  ];
  return (
    <>
      <StepHeader title="Temporal Skill Decay" subtitle="Recency-Adjusted Scoring" />
      <div className="grid gap-6 md:grid-cols-2">
        {examples.map((ex, i) => (
          <motion.div key={ex.year} initial={{ opacity: 0, x: i === 0 ? -20 : 20 }} animate={{ opacity: 1, x: 0 }}>
            <ShowcaseCard glow={ex.fresh}>
              <p className="text-lg font-bold">{ex.skill} ({ex.year})</p>
              <p className="text-sm text-slate-600">Freshness Score = {ex.score}</p>
              <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-200">
                <motion.div className={`h-full rounded-full ${ex.fresh ? "bg-emerald-500" : "bg-amber-500"}`}
                  initial={{ width: 0 }} animate={{ width: `${ex.score}%` }} transition={{ duration: 1 }} />
              </div>
            </ShowcaseCard>
          </motion.div>
        ))}
      </div>
    </>
  );
}

export function StepLatentSkillGraph() {
  const nodes = ["PyTorch", "Deep Learning", "Machine Learning", "Python"];
  const [hovered, setHovered] = useState<number | null>(null);
  return (
    <>
      <StepHeader title="Latent Skill Graph" subtitle="Interactive Ontology" />
      <div className="flex flex-col items-center gap-2 py-8">
        {nodes.map((node, i) => (
          <div key={node} className="flex flex-col items-center">
            <motion.button
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              animate={{ scale: hovered === i ? 1.08 : 1 }}
              className={`rounded-xl border px-8 py-3 font-medium transition-colors ${hovered === i ? "border-primary bg-primary/10" : "border-slate-200 bg-slate-50"}`}
            >
              {node}
            </motion.button>
            {i < nodes.length - 1 && <ArrowDown className="my-2 h-5 w-5 text-primary" />}
          </div>
        ))}
      </div>
      {hovered !== null && (
        <p className="text-center text-sm text-slate-600">Inferred relationship: {nodes[hovered]} → foundational skills in graph</p>
      )}
    </>
  );
}

export function StepHybridRetrieval() {
  const stages = ["BM25 Keyword Search", "Dense Embeddings", "Cross-Encoder Rerank", "Top Candidates"];
  return (
    <>
      <StepHeader title="Hybrid Retrieval Engine" subtitle="Multi-Stage Pipeline" />
      <div className="mx-auto max-w-md space-y-3">
        {stages.map((stage, i) => (
          <motion.div key={stage} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.25 }}>
            <ShowcaseCard className="text-center">
              <p className="font-medium">{stage}</p>
              {i < stages.length - 1 && <p className="mt-2 text-primary">×</p>}
            </ShowcaseCard>
          </motion.div>
        ))}
      </div>
    </>
  );
}

export function StepScoringEngine() {
  const { data } = useWalkthrough();
  const top = data.rankings.rankings[0];
  const factors = [
    { label: "Semantic Fit", value: top.semantic_fit },
    { label: "Skill Coverage", value: top.skill_coverage },
    { label: "Trajectory", value: top.career_trajectory },
    { label: "Interview Readiness", value: top.interview_readiness },
    { label: "Credibility", value: top.credibility },
  ];
  return (
    <>
      <StepHeader title="Scoring Engine" subtitle={top.candidate_name} />
      <ShowcaseCard className="mb-6 text-center" glow>
        <p className="text-sm text-slate-600">Final Score</p>
        <p className="text-5xl font-bold text-primary">{formatPct(top.final_score)}</p>
      </ShowcaseCard>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {factors.map((f, i) => (
          <ShowcaseCard key={f.label}>
            <div className="flex justify-between text-sm">
              <span>{f.label}</span>
              <span className="font-bold">{formatPct(f.value)}</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-200">
              <motion.div className="h-full bg-primary" initial={{ width: 0 }} animate={{ width: `${f.value * 100}%` }} transition={{ delay: i * 0.1 }} />
            </div>
          </ShowcaseCard>
        ))}
      </div>
    </>
  );
}

export function StepEvidenceGrounding() {
  const { data } = useWalkthrough();
  const evidence = data.reports.evidence;
  return (
    <>
      <StepHeader title="Evidence Grounding" subtitle="Click Score → View Proof" />
      <div className="mb-4 text-center text-sm text-slate-600">Score → Resume Evidence → Citations</div>
      <div className="space-y-4">
        {evidence.map((e, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <ShowcaseCard>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium">{e.claim}</p>
                  <p className="mt-1 text-xs text-slate-600">{e.section} · {formatPct(e.confidence)} confidence</p>
                  <p className="mt-2 rounded-lg bg-slate-50 p-3 text-sm italic">&ldquo;{e.snippet}&rdquo;</p>
                </div>
              </div>
            </ShowcaseCard>
          </motion.div>
        ))}
      </div>
    </>
  );
}
