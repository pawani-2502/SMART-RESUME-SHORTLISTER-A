"use client";

import { use, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { JobSubNav } from "@/components/layout/sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { api, RankingRun } from "@/lib/api";
import { formatScore } from "@/lib/utils";
import { ArrowUp, ArrowDown, Minus, GitCompare } from "lucide-react";

interface RunDetail {
  run: RankingRun;
  rankings: Array<{
    candidate_id: string;
    candidate_name: string;
    rank: number;
    final_score: number;
    confidence_level: string;
    eligibility_status: string;
  }>;
}

interface CompareResult {
  run_a: RankingRun;
  run_b: RankingRun;
  rank_changes: Array<{
    candidate_id: string;
    candidate_name: string;
    rank_a: number | null;
    rank_b: number | null;
    rank_delta: number;
    score_a: number | null;
    score_b: number | null;
    score_delta: number;
  }>;
  summary: {
    candidates_moved_up: number;
    candidates_moved_down: number;
    avg_score_delta: number;
  };
}

export default function RankingHistoryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [selectedA, setSelectedA] = useState<string | null>(null);
  const [selectedB, setSelectedB] = useState<string | null>(null);

  const { data: runs, isLoading } = useQuery({
    queryKey: ["ranking-runs", id],
    queryFn: () => api<RankingRun[]>(`/ranking-history/jobs/${id}/runs`),
  });

  const { data: comparison } = useQuery({
    queryKey: ["ranking-compare", selectedA, selectedB],
    queryFn: () => api<CompareResult>(`/ranking-history/runs/compare?run_a=${selectedA}&run_b=${selectedB}`),
    enabled: !!selectedA && !!selectedB && selectedA !== selectedB,
  });

  const { data: runDetail } = useQuery({
    queryKey: ["ranking-run", selectedA],
    queryFn: () => api<RunDetail>(`/ranking-history/runs/${selectedA}`),
    enabled: !!selectedA && !selectedB,
  });

  return (
    <AppShell>
      <JobSubNav jobId={id} />
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Ranking History</h1>
        <p className="text-muted-foreground">View, compare, and analyze past ranking runs</p>
      </div>

      {isLoading ? <LoadingState /> : !runs?.length ? (
        <EmptyState title="No ranking history" description="Run ranking to create your first history entry." />
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-1">
            <CardHeader><CardTitle>Ranking Runs</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {runs.map((run) => (
                <button
                  key={run.id}
                  onClick={() => {
                    if (!selectedA || selectedA === run.id) setSelectedA(run.id);
                    else if (!selectedB) setSelectedB(run.id);
                    else { setSelectedA(run.id); setSelectedB(null); }
                  }}
                  className={`w-full rounded-lg border p-3 text-left text-sm transition-colors ${
                    selectedA === run.id || selectedB === run.id ? "border-primary bg-primary/5" : "hover:bg-slate-50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{new Date(run.created_at).toLocaleString()}</span>
                    {run.is_current && <span className="rounded bg-green-100 px-2 py-0.5 text-xs text-green-800">Current</span>}
                  </div>
                  <p className="text-xs text-muted-foreground capitalize">{run.status} · {run.candidate_count} candidates</p>
                  <p className="text-xs">Eligible: {run.eligible_count} · Ineligible: {run.ineligible_count}</p>
                </button>
              ))}
              {selectedA && selectedB && (
                <Button variant="outline" className="w-full" onClick={() => { setSelectedA(null); setSelectedB(null); }}>
                  Clear selection
                </Button>
              )}
            </CardContent>
          </Card>

          <div className="lg:col-span-2 space-y-6">
            {selectedA && selectedB && selectedA !== selectedB && comparison && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2"><GitCompare className="h-5 w-5" />Run Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mb-4 grid grid-cols-3 gap-4 text-center text-sm">
                    <div><p className="text-muted-foreground">Moved Up</p><p className="text-xl font-bold text-green-600">{comparison.summary.candidates_moved_up}</p></div>
                    <div><p className="text-muted-foreground">Moved Down</p><p className="text-xl font-bold text-red-600">{comparison.summary.candidates_moved_down}</p></div>
                    <div><p className="text-muted-foreground">Avg Score Δ</p><p className="text-xl font-bold">{comparison.summary.avg_score_delta?.toFixed(2) ?? "—"}</p></div>
                  </div>
                  <div className="space-y-2">
                    {comparison.rank_changes.map((c) => (
                      <div key={c.candidate_id} className="flex items-center justify-between rounded border p-3 text-sm">
                        <span className="font-medium">{c.candidate_name}</span>
                        <div className="flex items-center gap-4">
                          <span>#{c.rank_a ?? "—"} → #{c.rank_b ?? "—"}</span>
                          {c.rank_delta > 0 ? <ArrowUp className="h-4 w-4 text-green-600" /> :
                           c.rank_delta < 0 ? <ArrowDown className="h-4 w-4 text-red-500" /> :
                           <Minus className="h-4 w-4 text-muted-foreground" />}
                          <span className="text-muted-foreground">
                            {c.score_a != null ? formatScore(c.score_a) : "—"} → {c.score_b != null ? formatScore(c.score_b) : "—"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {selectedA && !selectedB && runDetail && (
              <Card>
                <CardHeader>
                  <CardTitle>Run Details — {new Date(runDetail.run.created_at).toLocaleString()}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mb-4 text-sm text-muted-foreground">
                    Weights: {JSON.stringify(runDetail.run.override_snapshot?.weights ?? {})}
                  </div>
                  <div className="space-y-2">
                    {runDetail.rankings.map((r) => (
                      <div key={r.candidate_id} className="flex items-center justify-between rounded border p-3 text-sm">
                        <span>#{r.rank} {r.candidate_name}</span>
                        <div className="flex items-center gap-3">
                          <span className="font-bold">{formatScore(r.final_score)}</span>
                          <span className="text-xs capitalize">{r.eligibility_status}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {selectedA && !selectedB && !runDetail && <LoadingState message="Loading run details..." />}
            {selectedA && selectedB && !comparison && selectedA !== selectedB && <LoadingState message="Comparing runs..." />}
            {!selectedA && (
              <EmptyState title="Select a run" description="Click a ranking run to view details. Select two runs to compare." />
            )}
          </div>
        </div>
      )}
    </AppShell>
  );
}
