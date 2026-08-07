"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { api } from "@/lib/api";
import { formatScore } from "@/lib/utils";
import { MessageSquare, ArrowLeft } from "lucide-react";

interface TranscriptTurn {
  role: string;
  content?: string;
  text?: string;
  evidence?: string | { snippet: string }[];
}

interface InterviewResult {
  transcript: TranscriptTurn[];
  readiness_score: number;
  communication_score: number;
  confidence_score: number;
  red_flags: string[];
  strengths: string[];
  weaknesses: string[];
  follow_up_questions: { question: string }[] | string[];
}

function getTurnText(turn: TranscriptTurn): string {
  return turn.content ?? turn.text ?? "";
}

function InterviewContent() {
  const params = useSearchParams();
  const candidateId = params.get("candidate");
  const jobId = params.get("job");

  const { data: simulation, isLoading, isError, refetch } = useQuery({
    queryKey: ["interview", jobId, candidateId],
    queryFn: async () => {
      if (!jobId || !candidateId) return null;
      return api<InterviewResult>(`/jobs/${jobId}/candidates/${candidateId}/interview`, { method: "POST" });
    },
    enabled: !!jobId && !!candidateId,
    retry: 1,
  });

  return (
    <AppShell>
      <div className="mb-6">
        {candidateId && (
          <Link href={`/candidates/${candidateId}`} className="inline-flex items-center gap-1 text-sm text-primary hover:underline">
            <ArrowLeft className="h-4 w-4" /> Back to candidate
          </Link>
        )}
        <h1 className="mt-2 flex items-center gap-2 text-2xl font-bold">
          <MessageSquare className="h-6 w-6" />Shadow Interview Simulation
        </h1>
      </div>

      {!jobId || !candidateId ? (
        <Card>
          <CardContent className="p-6">
            <p className="text-muted-foreground">
              Select a candidate from their detail page and click &ldquo;Generate Shadow Interview&rdquo; to run a simulation.
            </p>
            <Link href="/rankings"><Button className="mt-4" variant="outline">View Rankings</Button></Link>
          </CardContent>
        </Card>
      ) : isLoading ? (
        <LoadingState message="Generating shadow interview simulation..." />
      ) : isError ? (
        <ErrorState message="Failed to generate interview simulation" onRetry={() => refetch()} />
      ) : simulation ? (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            <Card>
              <CardHeader><CardTitle>Transcript</CardTitle></CardHeader>
              <CardContent className="max-h-[32rem] space-y-4 overflow-y-auto">
                {simulation.transcript?.map((turn, i) => (
                  <div key={i} className={`rounded-lg p-4 ${turn.role === "interviewer" ? "bg-slate-100" : "border bg-white"}`}>
                    <p className="text-xs font-medium uppercase text-muted-foreground">{turn.role}</p>
                    <p className="mt-1">{getTurnText(turn)}</p>
                    {Array.isArray(turn.evidence) && turn.evidence.map((e, j) => (
                      <p key={j} className="mt-2 rounded bg-yellow-50 p-2 text-xs italic text-yellow-800">
                        Evidence: {typeof e === "string" ? e : e.snippet}
                      </p>
                    ))}
                    {typeof turn.evidence === "string" && (
                      <p className="mt-2 rounded bg-yellow-50 p-2 text-xs italic text-yellow-800">
                        Evidence: {turn.evidence}
                      </p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-4">
            <Card className="border-primary/20 bg-primary/5">
              <CardHeader><CardTitle>Readiness Score</CardTitle></CardHeader>
              <CardContent>
                <p className="text-4xl font-bold text-primary">{formatScore(simulation.readiness_score)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Scores</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between"><span>Readiness</span><span className="font-bold">{formatScore(simulation.readiness_score)}</span></div>
                <div className="flex justify-between"><span>Communication</span><span className="font-bold">{formatScore(simulation.communication_score)}</span></div>
                <div className="flex justify-between"><span>Confidence</span><span className="font-bold">{formatScore(simulation.confidence_score)}</span></div>
              </CardContent>
            </Card>
            {simulation.strengths?.length > 0 && (
              <Card className="border-green-200">
                <CardHeader><CardTitle className="text-green-700">Strengths</CardTitle></CardHeader>
                <CardContent className="space-y-1">
                  {simulation.strengths.map((s, i) => <p key={i} className="text-sm text-green-800">✓ {s}</p>)}
                </CardContent>
              </Card>
            )}
            {simulation.weaknesses?.length > 0 && (
              <Card className="border-amber-200">
                <CardHeader><CardTitle className="text-amber-700">Weaknesses</CardTitle></CardHeader>
                <CardContent className="space-y-1">
                  {simulation.weaknesses.map((w, i) => <p key={i} className="text-sm text-amber-800">• {w}</p>)}
                </CardContent>
              </Card>
            )}
            {simulation.red_flags?.length > 0 && (
              <Card className="border-red-200">
                <CardHeader><CardTitle className="text-red-600">Red Flags</CardTitle></CardHeader>
                <CardContent>
                  {simulation.red_flags.map((f, i) => <p key={i} className="text-sm text-red-600">{f}</p>)}
                </CardContent>
              </Card>
            )}
            {simulation.follow_up_questions?.length > 0 && (
              <Card>
                <CardHeader><CardTitle>Follow-Up Questions</CardTitle></CardHeader>
                <CardContent className="space-y-2">
                  {simulation.follow_up_questions.map((q, i) => (
                    <p key={i} className="text-sm">{typeof q === "string" ? q : q.question}</p>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      ) : null}
    </AppShell>
  );
}

export default function InterviewPage() {
  return (
    <Suspense fallback={<AppShell><LoadingState message="Loading..." /></AppShell>}>
      <InterviewContent />
    </Suspense>
  );
}
