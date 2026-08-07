"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { JobSubNav } from "@/components/layout/sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { api, JDQualityReport } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar } from "recharts";
import { AlertTriangle, Lightbulb } from "lucide-react";

function ScoreCard({ label, score, grade }: { label: string; score: number; grade?: string }) {
  const pct = Math.round(score * 100);
  const color = pct >= 85 ? "text-green-600" : pct >= 70 ? "text-blue-600" : pct >= 55 ? "text-yellow-600" : "text-red-600";
  return (
    <Card>
      <CardContent className="p-6 text-center">
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className={`text-4xl font-bold ${color}`}>{pct}%</p>
        {grade && <p className="mt-1 text-xs text-muted-foreground">Grade {grade}</p>}
      </CardContent>
    </Card>
  );
}

export default function JDQualityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["jd-quality", id],
    queryFn: () => api<JDQualityReport>(`/jobs/${id}/analyze-quality`, { method: "POST" }),
  });

  const chartData = data ? [
    { name: "Clarity", score: Math.round(data.clarity_score * 100) },
    { name: "Completeness", score: Math.round(data.completeness_score * 100) },
    { name: "Inclusivity", score: Math.round(data.inclusivity_score * 100) },
    { name: "Overall", score: Math.round(data.overall_score * 100) },
  ] : [];

  const radarData = data ? [
    { metric: "Clarity", value: data.clarity_score * 100 },
    { metric: "Completeness", value: data.completeness_score * 100 },
    { metric: "Inclusivity", value: data.inclusivity_score * 100 },
    { metric: "Bias Risk", value: (1 - data.inclusivity_score) * 100 },
  ] : [];

  return (
    <AppShell>
      <JobSubNav jobId={id} />
      <div className="mb-6">
        <h1 className="text-2xl font-bold">JD Quality Dashboard</h1>
        <p className="text-muted-foreground">Analyze job description quality, completeness, and bias risk</p>
      </div>

      {isLoading ? <LoadingState message="Analyzing job description..." /> :
       error ? <ErrorState message="Failed to analyze JD" onRetry={() => refetch()} /> :
       data && (
        <>
          <div className="mb-6 grid gap-4 sm:grid-cols-4">
            <ScoreCard label="JD Quality Score" score={data.overall_score} grade={data.grade} />
            <ScoreCard label="Completeness" score={data.completeness_score} />
            <ScoreCard label="Clarity" score={data.clarity_score} />
            <ScoreCard label="Inclusivity (Bias Risk ↓)" score={data.inclusivity_score} />
          </div>

          <div className="mb-6 grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Score Breakdown</CardTitle></CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="score" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Quality Radar</CardTitle></CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="metric" />
                    <Radar dataKey="value" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.3} />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-orange-500" />Issues & Missing Requirements</CardTitle></CardHeader>
              <CardContent>
                {data.issues.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No critical issues detected.</p>
                ) : (
                  <ul className="space-y-2">
                    {data.issues.map((issue, i) => (
                      <li key={i} className="rounded border border-orange-200 bg-orange-50 p-3 text-sm">{issue}</li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Lightbulb className="h-5 w-5 text-primary" />Suggested Improvements</CardTitle></CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {data.suggestions.map((s, i) => (
                    <li key={i} className="rounded border p-3 text-sm">{s}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}
