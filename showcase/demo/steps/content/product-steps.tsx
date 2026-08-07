"use client";

import { motion } from "framer-motion";
import { MessageSquare, Bot, User } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { ShowcaseCard, ShowcaseBadge } from "../../../shared/components/ui";
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

export function StepShadowInterview() {
  const { data } = useWalkthrough();
  const iv = data.interview;
  return (
    <>
      <StepHeader title="Shadow Interview" subtitle="AI Simulation" />
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <ShowcaseCard className="text-center"><p className="text-xs text-slate-600">Readiness</p><p className="text-2xl font-bold text-primary">{formatPct(iv.readiness_score)}</p></ShowcaseCard>
        <ShowcaseCard><p className="text-xs font-semibold text-emerald-700">Strengths</p><ul className="mt-2 text-sm">{iv.strengths.map((s, i) => <li key={i}>• {s}</li>)}</ul></ShowcaseCard>
        <ShowcaseCard><p className="text-xs font-semibold text-amber-400">Weaknesses</p><ul className="mt-2 text-sm">{iv.weaknesses.map((s, i) => <li key={i}>• {s}</li>)}</ul></ShowcaseCard>
      </div>
      <ShowcaseCard>
        <div className="mb-4 flex items-center gap-4 text-sm">
          <span className="flex items-center gap-1"><Bot className="h-4 w-4" /> AI Interviewer</span>
          <span className="flex items-center gap-1"><User className="h-4 w-4" /> Resume-Grounded Twin</span>
        </div>
        <div className="max-h-64 space-y-3 overflow-y-auto">
          {iv.transcript.map((t, i) => (
            <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.15 }}
              className={`rounded-lg p-3 text-sm ${t.role === "interviewer" ? "bg-primary/10 ml-0 mr-8" : "bg-slate-50 ml-8 mr-0"}`}>
              <p className="text-xs font-semibold capitalize text-slate-600">{t.role}</p>
              <p className="mt-1">{t.text}</p>
              {"evidence" in t && t.evidence && <p className="mt-2 text-xs italic text-primary">📎 {t.evidence}</p>}
            </motion.div>
          ))}
        </div>
      </ShowcaseCard>
      <ShowcaseCard className="mt-4">
        <p className="mb-2 font-semibold">Follow-Up Questions</p>
        <ul className="text-sm text-slate-600">{iv.follow_up_questions.map((q, i) => <li key={i}>• {q}</li>)}</ul>
      </ShowcaseCard>
    </>
  );
}

export function StepRecruiterCopilot() {
  const { data } = useWalkthrough();
  return (
    <>
      <StepHeader title="Recruiter Copilot" subtitle="AI Hiring Assistant" />
      <div className="space-y-4">
        {data.reports.copilot_responses.map((item, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.12 }}>
            <ShowcaseCard>
              <p className="flex items-center gap-2 font-medium text-primary">
                <MessageSquare className="h-4 w-4" /> {item.query}
              </p>
              <p className="mt-3 text-sm text-slate-600">{item.response}</p>
            </ShowcaseCard>
          </motion.div>
        ))}
      </div>
    </>
  );
}

export function StepCandidateComparison() {
  const { data } = useWalkthrough();
  const cmp = data.reports.comparison;
  const chartData = [
    { name: "Skills", a: cmp.skills.a * 100, b: cmp.skills.b * 100 },
    { name: "Experience", a: cmp.experience.a * 100, b: cmp.experience.b * 100 },
    { name: "Trajectory", a: cmp.trajectory.a * 100, b: cmp.trajectory.b * 100 },
    { name: "Readiness", a: cmp.readiness.a * 100, b: cmp.readiness.b * 100 },
  ];
  return (
    <>
      <StepHeader title="Candidate Comparison" subtitle={`${cmp.candidate_a} vs ${cmp.candidate_b}`} />
      <div className="mb-6 flex justify-center gap-8 text-sm font-semibold">
        <span className="text-primary">{cmp.candidate_a}</span>
        <span className="text-slate-600">vs</span>
        <span className="text-slate-600">{cmp.candidate_b}</span>
      </div>
      <ShowcaseCard className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis domain={[0, 100]} stroke="#94a3b8" />
            <Tooltip />
            <Bar dataKey="a" fill="hsl(var(--primary))" name={cmp.candidate_a} radius={[4, 4, 0, 0]} />
            <Bar dataKey="b" fill="hsl(var(--primary) / 0.6)" name={cmp.candidate_b} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ShowcaseCard>
      <ShowcaseCard className="mt-4 text-center">
        <p className="text-sm text-slate-600">Recommendation</p>
        <p className="mt-1 font-medium">{cmp.recommendation}</p>
      </ShowcaseCard>
    </>
  );
}

const COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b"];

export function StepAnalyticsDashboard() {
  const { data } = useWalkthrough();
  const a = data.analytics;
  const funnelData = Object.entries(a.hiring_funnel).map(([k, v]) => ({ stage: k, count: v }));
  return (
    <>
      <StepHeader title="Analytics Dashboard" subtitle="Hiring Intelligence" />
      <div className="grid gap-4 sm:grid-cols-4 mb-6">
        {[
          { label: "Jobs", value: a.total_jobs },
          { label: "Candidates", value: a.total_candidates },
          { label: "Rankings", value: a.total_rankings },
          { label: "Avg Score", value: formatPct(a.avg_score) },
        ].map((s) => (
          <ShowcaseCard key={s.label} className="text-center">
            <p className="text-xs text-slate-600">{s.label}</p>
            <p className="text-2xl font-bold">{s.value}</p>
          </ShowcaseCard>
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <ShowcaseCard className="h-64">
          <p className="mb-2 font-semibold">Hiring Funnel</p>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={funnelData} layout="vertical">
              <XAxis type="number" stroke="#94a3b8" />
              <YAxis type="category" dataKey="stage" width={80} stroke="#94a3b8" />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ShowcaseCard>
        <ShowcaseCard className="h-64">
          <p className="mb-2 font-semibold">Skill Distribution</p>
          <ResponsiveContainer width="100%" height="90%">
            <PieChart>
              <Pie data={a.skill_distribution.slice(0, 5)} dataKey="count" nameKey="skill" cx="50%" cy="50%" outerRadius={80}>
                {a.skill_distribution.slice(0, 5).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ShowcaseCard>
      </div>
    </>
  );
}
