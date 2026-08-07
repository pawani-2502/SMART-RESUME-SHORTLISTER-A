"use client";

import { use, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { LoadingState } from "@/components/ui/loading-state";
import { api, ScreeningTest } from "@/lib/api";
import { CheckCircle2 } from "lucide-react";

export default function TakeTestPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const qc = useQueryClient();
  const [responses, setResponses] = useState<Record<number, string>>({});
  const [submitted, setSubmitted] = useState(false);

  const { data: test, isLoading } = useQuery({
    queryKey: ["test", id],
    queryFn: () => api<ScreeningTest>(`/screening/tests/${id}`),
  });

  const submitMutation = useMutation({
    mutationFn: () => api(`/screening/tests/${id}/submit`, {
      method: "POST",
      body: JSON.stringify({
        responses: (test?.questions ?? []).map((q, i) => ({
          question_index: i,
          question: typeof q === "object" ? q.question : q,
          answer: responses[i] ?? "",
        })),
      }),
    }),
    onSuccess: () => {
      setSubmitted(true);
      qc.invalidateQueries({ queryKey: ["test", id] });
    },
  });

  if (isLoading) return <AppShell><LoadingState /></AppShell>;

  const analytics = test?.analytics;
  const passed = analytics?.passed;

  return (
    <AppShell>
      <div className="mx-auto max-w-3xl">
        <Link href={`/jobs/${test?.job_id}/screening`} className="text-sm text-primary hover:underline">← Back to screening</Link>
        <h1 className="mt-2 text-2xl font-bold">Screening Test</h1>
        <p className="text-muted-foreground">{test?.candidate_name}</p>

        {submitted || test?.status === "completed" ? (
          <Card className="mt-6">
            <CardContent className="p-6 text-center">
              <CheckCircle2 className={`mx-auto mb-4 h-12 w-12 ${passed ? "text-green-600" : "text-orange-500"}`} />
              <h2 className="text-xl font-bold">{passed ? "Passed" : "Completed"}</h2>
              <p className="mt-2 text-muted-foreground">
                Score: {((test?.test_score ?? 0) * 100).toFixed(0)}%
                {analytics?.pass_threshold != null && ` (threshold: ${(analytics.pass_threshold * 100).toFixed(0)}%)`}
              </p>
              {analytics?.question_breakdown && (
                <div className="mt-6 text-left">
                  <h3 className="font-semibold">Question Breakdown</h3>
                  {analytics.question_breakdown.map((q, i) => (
                    <div key={i} className="mt-2 rounded border p-3 text-sm">
                      <p>{q.question}</p>
                      <p className="text-muted-foreground">Score: {((q.score ?? 0) * 100).toFixed(0)}%</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <Card className="mt-6">
            <CardHeader><CardTitle>{(test?.questions ?? []).length} Questions</CardTitle></CardHeader>
            <CardContent className="space-y-6">
              {(test?.questions ?? []).map((q, i) => (
                <div key={i}>
                  <label className="mb-2 block font-medium">
                    Q{i + 1}. {typeof q === "object" ? q.question : String(q)}
                  </label>
                  <Textarea
                    rows={3}
                    value={responses[i] ?? ""}
                    onChange={(e) => setResponses({ ...responses, [i]: e.target.value })}
                    placeholder="Your answer..."
                  />
                </div>
              ))}
              <Button
                className="w-full"
                disabled={submitMutation.isPending}
                onClick={() => submitMutation.mutate()}
              >
                {submitMutation.isPending ? "Submitting..." : "Submit Answers"}
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
