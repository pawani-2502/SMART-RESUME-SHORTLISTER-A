"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { api, Job, Candidate } from "@/lib/api";
import { formatScore } from "@/lib/utils";
import { Users, Loader2 } from "lucide-react";

export default function ComparisonPage() {
  const [jobId, setJobId] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [compareEnabled, setCompareEnabled] = useState(false);

  const { data: jobs, isLoading: jobsLoading } = useQuery({ queryKey: ["jobs"], queryFn: () => api<Job[]>("/jobs") });
  const activeJob = jobId || jobs?.[0]?.id || "";

  const { data: candidates, isLoading: candidatesLoading } = useQuery({
    queryKey: ["candidates", activeJob],
    queryFn: () => api<Candidate[]>(`/candidates/job/${activeJob}`),
    enabled: !!activeJob,
  });

  const { data: comparison, isLoading: comparing, isFetching, refetch } = useQuery({
    queryKey: ["comparison", activeJob, selected],
    queryFn: () => api<{
      candidates: Record<string, unknown>[];
      skill_overlap: { common_skills: string[] };
      recommendations: { type: string; reason: string }[];
    }>(`/jobs/${activeJob}/compare`, {
      method: "POST",
      body: JSON.stringify({ candidate_ids: selected }),
    }),
    enabled: compareEnabled && selected.length >= 2,
  });

  useEffect(() => {
    if (selected.length >= 2) {
      setCompareEnabled(true);
    } else {
      setCompareEnabled(false);
    }
  }, [selected]);

  const toggle = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length < 10 ? [...prev, id] : prev
    );
  };

  const isLoading = jobsLoading || candidatesLoading;
  const showComparisonLoading = (comparing || isFetching) && selected.length >= 2;

  return (
    <AppShell>
      <h1 className="mb-2 text-2xl font-bold">Candidate Comparison</h1>
      <p className="mb-6 text-muted-foreground">Select 2–10 candidates to compare side-by-side</p>

      {isLoading ? (
        <LoadingState message="Loading jobs and candidates..." />
      ) : (
        <>
          <select
            className="mb-4 rounded-lg border px-3 py-2 text-sm shadow-sm"
            value={activeJob}
            onChange={(e) => { setJobId(e.target.value); setSelected([]); setCompareEnabled(false); }}
          >
            {(jobs ?? []).map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
          </select>

          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Select Candidates ({selected.length}/10)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!candidates?.length ? (
                <EmptyState title="No candidates" description="Upload resumes to this job first." />
              ) : (
                <div className="flex flex-wrap gap-2">
                  {(candidates ?? []).map((c) => (
                    <Button
                      key={c.id}
                      variant={selected.includes(c.id) ? "default" : "outline"}
                      size="sm"
                      onClick={() => toggle(c.id)}
                      className="transition-all"
                    >
                      {c.name ?? "Unknown"}
                    </Button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {selected.length >= 2 && (
            <div className="mb-6 flex items-center gap-3">
              <Button onClick={() => refetch()} disabled={showComparisonLoading}>
                {showComparisonLoading ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Comparing...</>
                ) : "Refresh Comparison"}
              </Button>
              <span className="text-sm text-muted-foreground">{selected.length} candidates selected</span>
            </div>
          )}

          {selected.length < 2 && selected.length > 0 && (
            <p className="mb-6 text-sm text-amber-600">Select at least 2 candidates to compare.</p>
          )}

          {showComparisonLoading && !comparison && (
            <LoadingState message="Running AI comparison analysis..." />
          )}

          {comparison && !showComparisonLoading && (
            <div className="space-y-6 animate-in fade-in duration-300">
              {comparison.recommendations?.map((r, i) => (
                <div key={i} className="rounded-lg border border-primary/20 bg-primary/5 p-4">
                  <p className="font-medium">{r.type}</p>
                  <p className="text-sm text-muted-foreground">{r.reason}</p>
                </div>
              ))}

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {comparison.candidates?.map((c) => (
                  <Card key={String(c.candidate_id)} className="transition-shadow hover:shadow-md">
                    <CardHeader>
                      <CardTitle>{String(c.name)}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold text-primary">{formatScore(c.final_score as number)}</p>
                      <p className="text-sm text-muted-foreground">{String(c.skill_count)} skills · {String(c.total_years)} yrs</p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {comparison.skill_overlap?.common_skills?.length > 0 && (
                <Card>
                  <CardHeader><CardTitle>Common Skills</CardTitle></CardHeader>
                  <CardContent className="flex flex-wrap gap-2">
                    {comparison.skill_overlap.common_skills.map((s) => (
                      <span key={s} className="rounded-full bg-blue-100 px-3 py-1 text-xs text-blue-800">{s}</span>
                    ))}
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </>
      )}
    </AppShell>
  );
}
