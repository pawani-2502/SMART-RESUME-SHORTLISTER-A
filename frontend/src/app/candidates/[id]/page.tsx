"use client";

import { use, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { api, Candidate, Ranking } from "@/lib/api";
import { formatScore, getScoreColor } from "@/lib/utils";
import { MessageSquare, FileText, Brain } from "lucide-react";

export default function CandidateDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"overview" | "evidence" | "graph">("overview");

  const { data: candidate, isLoading } = useQuery({
    queryKey: ["candidate", id],
    queryFn: () => api<Candidate>(`/candidates/${id}`),
  });

  const jobId = candidate?.job_id;
  const { data: shortlist } = useQuery({
    queryKey: ["rankings", jobId],
    queryFn: () => api<{ rankings: Ranking[] }>(`/jobs/${jobId}/rankings`),
    enabled: !!jobId,
  });

  const ranking = shortlist?.rankings?.find((r) => r.candidate_id === id);

  const { data: knowledgeGraph } = useQuery({
    queryKey: ["kg", id],
    queryFn: () => api<{ nodes: unknown[]; edges: unknown[] }>(`/candidates/${id}/knowledge-graph`),
    enabled: activeTab === "graph",
  });

  const { data: recommendation } = useQuery({
    queryKey: ["recommendation", id],
    queryFn: () => api<{ label: string; action: string; rationale: string }>(`/candidates/${id}/recommendation`),
    enabled: !!ranking,
  });


  const parsed = candidate?.parsed_data as Record<string, unknown> | undefined;

  if (isLoading) return <AppShell><LoadingState message="Loading candidate..." /></AppShell>;

  return (
    <AppShell>
      <div className="mb-6">
        <Link href={`/jobs/${jobId}`} className="text-sm text-primary hover:underline">← Back to job</Link>
        <h1 className="mt-2 text-2xl font-bold">{candidate?.name ?? "Candidate"}</h1>
        <p className="text-muted-foreground">{candidate?.email}</p>
      </div>

      {ranking && (
        <Card className="mb-6 border-primary/20 bg-primary/5">
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-muted-foreground">Overall Fit</p>
              <p className={`text-4xl font-bold ${getScoreColor(ranking.final_score)}`}>{formatScore(ranking.final_score)}</p>
              <p className="text-sm">Rank #{ranking.rank} · {ranking.confidence_level} confidence</p>
            </div>
            {recommendation && (
              <div className="text-right">
                <p className="text-lg font-semibold">{recommendation.label}</p>
                <p className="text-sm text-muted-foreground">{recommendation.action}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <div className="mb-4 flex flex-wrap gap-2">
        {(["overview", "evidence", "graph"] as const).map((tab) => (
          <Button key={tab} variant={activeTab === tab ? "default" : "outline"} size="sm" onClick={() => setActiveTab(tab)}>
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </Button>
        ))}
        <Button
          variant="outline"
          size="sm"
          onClick={() => jobId && router.push(`/interview?job=${jobId}&candidate=${id}`)}
          disabled={!jobId}
        >
          <MessageSquare className="mr-1 h-4 w-4" />
          Generate Shadow Interview
        </Button>
        <Link href={`/jobs/${jobId}/candidates/${id}/interview-pack`}>
          <Button variant="outline" size="sm"><FileText className="mr-1 h-4 w-4" />Interview Pack</Button>
        </Link>
        <Link href={`/candidates/${id}/improvements`}>
          <Button variant="outline" size="sm"><Brain className="mr-1 h-4 w-4" />Improvements</Button>
        </Link>
        <Link href={`/candidates/${id}/multi-job-fit`}>
          <Button variant="outline" size="sm">Multi-Job Fit</Button>
        </Link>
      </div>

      {activeTab === "overview" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>Score Breakdown</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {ranking && [
                ["Semantic Fit", ranking.semantic_fit],
                ["Skill Coverage", ranking.skill_coverage],
                ["Career Trajectory", ranking.career_trajectory],
                ["Must-Have Coverage", ranking.must_have_coverage],
                ["Interview Readiness", ranking.interview_readiness],
              ].map(([label, score]) => (
                <div key={String(label)} className="flex justify-between text-sm">
                  <span>{label}</span>
                  <span className="font-medium">{formatScore(score as number)}</span>
                </div>
              ))}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Skills</CardTitle></CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {((parsed?.skills as { name: string }[]) ?? []).map((s, i) => (
                <span key={i} className="rounded-full bg-slate-100 px-3 py-1 text-xs">{s.name ?? String(s)}</span>
              ))}
            </CardContent>
          </Card>
          {ranking?.bias_audit && (
            <Card>
              <CardHeader><CardTitle>Bias Audit</CardTitle></CardHeader>
              <CardContent className="text-sm">
                <p>Original: {formatScore((ranking.bias_audit as Record<string, number>).original_score)}</p>
                <p>Blind: {formatScore((ranking.bias_audit as Record<string, number>).blind_score)}</p>
                <p>Delta: {((ranking.bias_audit as Record<string, number>).fairness_difference ?? 0).toFixed(3)}</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === "evidence" && (
        <Card>
          <CardHeader><CardTitle>Evidence Viewer</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {(ranking?.evidence ?? []).map((e, i) => (
              <div key={i} className="rounded-lg border p-4">
                <p className="font-medium text-sm">{e.claim}</p>
                <p className="mt-1 text-xs text-muted-foreground">{e.section} · confidence: {Math.round(e.confidence * 100)}%</p>
                <p className="mt-2 rounded bg-slate-50 p-2 text-sm italic">&ldquo;{e.snippet}&rdquo;</p>
              </div>
            ))}
            {!ranking?.evidence?.length && <p className="text-muted-foreground">No evidence available. Run ranking first.</p>}
          </CardContent>
        </Card>
      )}

      {activeTab === "graph" && knowledgeGraph && (
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Brain className="h-5 w-5" />Knowledge Graph</CardTitle></CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-muted-foreground">
              {knowledgeGraph.nodes?.length ?? 0} nodes · {knowledgeGraph.edges?.length ?? 0} edges
            </p>
            <div className="flex flex-wrap gap-2">
              {(knowledgeGraph.nodes as { type: string; label: string }[])?.map((n, i) => (
                <span key={i} className={`rounded px-2 py-1 text-xs ${
                  n.type === "skill" ? "bg-blue-100 text-blue-800" :
                  n.type === "experience" ? "bg-green-100 text-green-800" :
                  "bg-slate-100 text-slate-600"
                }`}>{n.label}</span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </AppShell>
  );
}
