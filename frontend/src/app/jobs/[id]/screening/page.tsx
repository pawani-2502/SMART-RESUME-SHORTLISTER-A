"use client";

import { use, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { JobSubNav } from "@/components/layout/sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { ProgressTracker } from "@/components/progress-tracker";
import { api, ScreeningTest, Candidate } from "@/lib/api";
import { CheckCircle2, XCircle, Eye, Send, Plus, FileText } from "lucide-react";
import { showToast } from "@/components/ui/toast";
import { formatScore } from "@/lib/utils";

export default function ScreeningPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const qc = useQueryClient();
  const [taskId, setTaskId] = useState<string | null>(null);
  const [previewId, setPreviewId] = useState<string | null>(null);

  const { data: tests, isLoading } = useQuery({
    queryKey: ["screening-tests", id],
    queryFn: () => api<ScreeningTest[]>(`/screening/jobs/${id}/tests`),
  });
  const { data: analytics } = useQuery({
    queryKey: ["screening-analytics", id],
    queryFn: () => api<{ total_tests: number; completed: number; passed: number; failed: number; avg_score: number }>(`/screening/jobs/${id}/analytics`),
  });
  const { data: candidates } = useQuery({
    queryKey: ["candidates", id],
    queryFn: () => api<Candidate[]>(`/candidates/job/${id}`),
  });
  const { data: preview } = useQuery({
    queryKey: ["test-preview", previewId],
    queryFn: () => api<ScreeningTest>(`/screening/tests/${previewId}`),
    enabled: !!previewId,
  });

  const generateMutation = useMutation({
    mutationFn: (candidateId: string) =>
      api<{ task_id: string }>(`/screening/jobs/${id}/candidates/${candidateId}/generate`, { method: "POST" }),
    onSuccess: (data) => { setTaskId(data.task_id); showToast("Screening test generation started"); },
  });

  const assignMutation = useMutation({
    mutationFn: (testId: string) => api(`/screening/tests/${testId}/assign`, { method: "POST" }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["screening-tests", id] }); showToast("Test assigned to candidate"); },
  });

  const candidatesWithoutTest = (candidates ?? []).filter(
    (c) => !(tests ?? []).some((t) => t.candidate_id === c.id)
  );

  return (
    <AppShell>
      <JobSubNav jobId={id} />
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Screening Tests</h1>
          <p className="text-muted-foreground">Generate, assign, and review candidate screening tests</p>
        </div>
      </div>

      {taskId && (
        <div className="mb-6">
          <ProgressTracker taskId={taskId} label="Generating test" onComplete={() => {
            setTaskId(null);
            qc.invalidateQueries({ queryKey: ["screening-tests", id] });
            showToast("Screening test generated successfully");
          }} />
        </div>
      )}

      {analytics && (
        <div className="mb-6 grid gap-4 sm:grid-cols-4">
          {[
            { label: "Total Tests", value: analytics.total_tests },
            { label: "Completed", value: analytics.completed },
            { label: "Passed", value: analytics.passed, color: "text-green-600" },
            { label: "Avg Score", value: formatScore(analytics.avg_score * 100) },
          ].map((s) => (
            <Card key={s.label}>
              <CardContent className="p-4">
                <p className="text-xs text-muted-foreground">{s.label}</p>
                <p className={`text-2xl font-bold ${s.color ?? ""}`}>{s.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Test Dashboard</CardTitle></CardHeader>
          <CardContent>
            {isLoading ? <LoadingState /> : !tests?.length ? (
              <EmptyState title="No screening tests yet" description="Generate a test for a candidate to get started." />
            ) : (
              <div className="space-y-3">
                {tests.map((t) => (
                  <div key={t.id} className="flex items-center justify-between rounded-lg border p-4">
                    <div>
                      <p className="font-medium">{t.candidate_name ?? "Candidate"}</p>
                      <p className="text-xs text-muted-foreground capitalize">{t.assigned_status} · {t.status}</p>
                      {t.test_score != null && (
                        <p className="text-sm">Score: {formatScore(t.test_score * 100)}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {t.analytics?.passed != null && (
                        t.analytics.passed
                          ? <CheckCircle2 className="h-5 w-5 text-green-600" />
                          : <XCircle className="h-5 w-5 text-red-500" />
                      )}
                      <Button size="sm" variant="outline" onClick={() => setPreviewId(t.id)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                      {t.assigned_status === "draft" && (
                        <Button size="sm" onClick={() => assignMutation.mutate(t.id)}>
                          <Send className="mr-1 h-4 w-4" />Assign
                        </Button>
                      )}
                      {t.assigned_status === "assigned" && (
                        <Link href={`/tests/${t.id}/take`}>
                          <Button size="sm" variant="secondary">Take Test</Button>
                        </Link>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Plus className="h-4 w-4" />Generate Test</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {candidatesWithoutTest.length === 0 ? (
              <p className="text-sm text-muted-foreground">All candidates have tests.</p>
            ) : candidatesWithoutTest.map((c) => (
              <Button
                key={c.id}
                variant="outline"
                className="w-full justify-start"
                disabled={generateMutation.isPending}
                onClick={() => generateMutation.mutate(c.id)}
              >
                {c.name ?? "Unknown"}
              </Button>
            ))}
          </CardContent>
        </Card>
      </div>

      {preview && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Test Preview — {preview.candidate_name}</CardTitle>
          </CardHeader>
          <CardContent>
            {(preview.questions ?? []).map((q, i) => (
              <div key={i} className="mb-4 rounded border p-3">
                <p className="font-medium">Q{i + 1}. {typeof q === "object" ? q.question : String(q)}</p>
                {q.type && <span className="text-xs text-muted-foreground">{q.type}</span>}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </AppShell>
  );
}
