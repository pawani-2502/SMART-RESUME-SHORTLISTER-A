"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingState } from "@/components/ui/loading-state";
import { api, MultiJobFitResult, Candidate } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { formatScore } from "@/lib/utils";

const COLORS = ["#2563eb", "#7c3aed", "#0891b2", "#059669", "#d97706"];

export default function MultiJobFitPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const { data: candidate } = useQuery({
    queryKey: ["candidate", id],
    queryFn: () => api<Candidate>(`/candidates/${id}`),
  });

  const { data: fits, isLoading } = useQuery({
    queryKey: ["multi-job-fit", id],
    queryFn: () => api<MultiJobFitResult[]>(`/candidates/${id}/multi-job-fit`),
  });

  const chartData = (fits ?? []).slice(0, 8).map((f) => ({
    name: f.job_title.length > 20 ? f.job_title.slice(0, 18) + "…" : f.job_title,
    fit: Math.round(f.fit_score * 100),
    fullTitle: f.job_title,
  }));

  const bestFit = fits?.[0];
  const alternatives = fits?.slice(1, 4) ?? [];

  return (
    <AppShell>
      <div className="mb-6">
        <Link href={`/candidates/${id}`} className="text-sm text-primary hover:underline">← Back to candidate</Link>
        <h1 className="mt-2 text-2xl font-bold">Multi-Job Fit Analysis</h1>
        <p className="text-muted-foreground">{candidate?.name} — cross-role alignment</p>
      </div>

      {isLoading ? <LoadingState /> : (
        <div className="space-y-6">
          {bestFit && (
            <Card className="border-primary/20 bg-primary/5">
              <CardContent className="p-6">
                <p className="text-sm text-muted-foreground">Best Match</p>
                <p className="text-2xl font-bold">{bestFit.job_title}</p>
                <p className="text-3xl font-bold text-primary">{formatScore(bestFit.fit_score * 100)}</p>
                <p className="text-sm">{bestFit.recommendation}</p>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader><CardTitle>Role Comparison</CardTitle></CardHeader>
            <CardContent className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis type="category" dataKey="name" width={120} />
                  <Tooltip formatter={(v: number) => [`${v}%`, "Fit"]} labelFormatter={(_, payload) => payload?.[0]?.payload?.fullTitle ?? ""} />
                  <Bar dataKey="fit" radius={[0, 4, 4, 0]}>
                    {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>All Role Matches</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {(fits ?? []).map((f) => (
                  <div key={f.job_id} className="flex items-center justify-between rounded border p-3">
                    <div>
                      <Link href={`/jobs/${f.job_id}`} className="font-medium hover:underline">{f.job_title}</Link>
                      <p className="text-xs text-muted-foreground">{f.recommendation} · Skills {Math.round(f.skill_coverage * 100)}%</p>
                    </div>
                    <span className="text-lg font-bold text-primary">{formatScore(f.fit_score * 100)}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Alternative Role Recommendations</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {alternatives.map((f) => (
                  <div key={f.job_id} className="rounded border p-4">
                    <p className="font-medium">{f.job_title}</p>
                    <p className="text-sm text-primary">{formatScore(f.fit_score * 100)} match</p>
                    {f.missing_skills.length > 0 && (
                      <p className="mt-2 text-xs text-muted-foreground">
                        Gaps: {f.missing_skills.slice(0, 4).join(", ")}
                      </p>
                    )}
                  </div>
                ))}
                {!alternatives.length && <p className="text-sm text-muted-foreground">No alternative roles found.</p>}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </AppShell>
  );
}
