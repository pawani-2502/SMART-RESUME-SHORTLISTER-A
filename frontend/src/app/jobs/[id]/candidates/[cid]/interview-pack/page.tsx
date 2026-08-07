"use client";

import { use, useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { JobSubNav } from "@/components/layout/sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { ProgressTracker } from "@/components/progress-tracker";
import { api, InterviewPack, apiBlob } from "@/lib/api";
import { Copy, Download, Printer, FileText, Loader2 } from "lucide-react";
import { showToast } from "@/components/ui/toast";

function QuestionList({ title, questions, variant }: { title: string; questions: Array<{ question?: string } | string>; variant?: string }) {
  if (!questions?.length) return null;
  return (
    <Card>
      <CardHeader><CardTitle className="text-lg">{title}</CardTitle></CardHeader>
      <CardContent>
        <ol className="list-decimal space-y-3 pl-5">
          {questions.map((q, i) => (
            <li key={i} className="text-sm">{typeof q === "object" ? q.question : String(q)}</li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}

export default function InterviewPackPage({ params }: { params: Promise<{ id: string; cid: string }> }) {
  const { id, cid } = use(params);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [packId, setPackId] = useState<string | null>(null);

  const { data: packs, refetch } = useQuery({
    queryKey: ["interview-packs", id],
    queryFn: () => api<Array<InterviewPack & { id: string }>>(`/interview-packs/jobs/${id}`),
  });

  const existing = packs?.find((p) => p.candidate_id === cid);
  const activeId = packId ?? existing?.id;

  const { data: pack, isLoading } = useQuery({
    queryKey: ["interview-pack", activeId],
    queryFn: () => api<InterviewPack>(`/interview-packs/${activeId}`),
    enabled: !!activeId,
  });

  const generateMutation = useMutation({
    mutationFn: () => api<{ task_id: string }>(`/interview-packs/jobs/${id}/candidates/${cid}/generate`, { method: "POST" }),
    onSuccess: (data) => setTaskId(data.task_id),
  });

  const syncGenerateMutation = useMutation({
    mutationFn: () => api<InterviewPack>(`/interview-packs/jobs/${id}/candidates/${cid}/generate-sync`, { method: "POST" }),
    onSuccess: (data) => { setPackId(data.id); refetch(); showToast("Interview pack generated successfully"); },
  });

  const copyAll = () => {
    if (!pack) return;
    const toQuestions = (qs: Array<{ question?: string } | string> | string | undefined) => {
      if (!qs) return [];
      return typeof qs === "string" ? [qs] : qs;
    };
    const sections: Array<[string, Array<{ question?: string } | string>]> = [
      ["Technical", toQuestions(pack.technical_questions)],
      ["Behavioral", toQuestions(pack.behavioral_questions)],
      ["Gap-Focused", toQuestions(pack.gap_questions)],
      ["Follow-Up", toQuestions(pack.follow_up_questions)],
    ];
    const text = sections.map(([title, qs]) =>
      `${title}:\n${qs.map((q, i) => `${i + 1}. ${typeof q === "object" ? q.question : q}`).join("\n")}`
    ).join("\n\n");
    navigator.clipboard.writeText(text);
  };

  const printPack = () => window.print();

  return (
    <AppShell>
      <JobSubNav jobId={id} />
      <div className="mb-6 flex items-center justify-between print:hidden">
        <div>
          <Link href={`/candidates/${cid}`} className="text-sm text-primary hover:underline">← Back to candidate</Link>
          <h1 className="mt-2 text-2xl font-bold">Interview Pack</h1>
          <p className="text-muted-foreground">{pack?.candidate_name} · {pack?.job_title}</p>
        </div>
        <div className="flex gap-2">
          {!pack && (
            <Button onClick={() => syncGenerateMutation.mutate()} disabled={syncGenerateMutation.isPending}>
              {syncGenerateMutation.isPending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Generating...</> : <><FileText className="mr-2 h-4 w-4" />Generate Pack</>}
            </Button>
          )}
          {pack && (
            <>
              <Button variant="outline" onClick={copyAll}><Copy className="mr-2 h-4 w-4" />Copy</Button>
              <Button variant="outline" onClick={printPack}><Printer className="mr-2 h-4 w-4" />Print</Button>
              <Button variant="outline" onClick={async () => {
                try {
                  const blob = await apiBlob(`/interview-packs/${pack.id}/export-pdf`);
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `interview-pack-${pack.id}.pdf`;
                  a.click();
                  URL.revokeObjectURL(url);
                  showToast("PDF downloaded successfully");
                } catch {
                  showToast("Failed to download PDF", "error");
                }
              }}><Download className="mr-2 h-4 w-4" />PDF</Button>
            </>
          )}
        </div>
      </div>

      {taskId && (
        <ProgressTracker taskId={taskId} label="Generating interview pack" onComplete={() => { setTaskId(null); refetch(); }} />
      )}

      {isLoading ? <LoadingState /> : !pack ? (
        <EmptyState title="No interview pack" description="Generate a candidate-specific interview pack." actionLabel="Generate" onAction={() => syncGenerateMutation.mutate()} />
      ) : (
        <div className="space-y-6 print:space-y-4">
          {(pack.red_flags?.length ?? 0) > 0 && (
            <Card className="border-orange-200 bg-orange-50">
              <CardHeader><CardTitle className="text-orange-800">Red Flags</CardTitle></CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 text-sm text-orange-900">
                  {pack.red_flags!.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </CardContent>
            </Card>
          )}
          {(pack.interview_objectives?.length ?? 0) > 0 && (
            <Card>
              <CardHeader><CardTitle>Interview Objectives</CardTitle></CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 text-sm">
                  {pack.interview_objectives!.map((o, i) => <li key={i}>{o}</li>)}
                </ul>
              </CardContent>
            </Card>
          )}
          <QuestionList title="Technical Questions" questions={pack.technical_questions} />
          <QuestionList title="Behavioral Questions" questions={pack.behavioral_questions} />
          <QuestionList title="Gap-Focused Questions" questions={pack.gap_questions} />
          <QuestionList title="Follow-Up Questions" questions={pack.follow_up_questions} />
        </div>
      )}
    </AppShell>
  );
}
