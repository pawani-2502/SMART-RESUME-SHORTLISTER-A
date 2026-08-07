"use client";

import { use, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { JobSubNav } from "@/components/layout/sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ProgressTracker } from "@/components/progress-tracker";
import { api, apiUpload, Job, Candidate, Shortlist, RecruiterOverride, RankTaskResponse, BatchUploadResponse } from "@/lib/api";
import { Upload, Play, Settings, Users, Trophy } from "lucide-react";
import { formatScore, getConfidenceBadge } from "@/lib/utils";

export default function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const qc = useQueryClient();
  const [uploading, setUploading] = useState(false);
  const [rankTaskId, setRankTaskId] = useState<string | null>(null);
  const [batchTaskId, setBatchTaskId] = useState<string | null>(null);

  const { data: job } = useQuery({ queryKey: ["job", id], queryFn: () => api<Job>(`/jobs/${id}`) });
  const { data: candidates } = useQuery({ queryKey: ["candidates", id], queryFn: () => api<Candidate[]>(`/candidates/job/${id}`) });
  const { data: shortlist } = useQuery({ queryKey: ["rankings", id], queryFn: () => api<Shortlist>(`/jobs/${id}/rankings`), retry: false });
  const { data: override } = useQuery({ queryKey: ["override", id], queryFn: () => api<RecruiterOverride>(`/jobs/${id}/override`), retry: false });

  const rankMutation = useMutation({
    mutationFn: () => api<RankTaskResponse>(`/jobs/${id}/rank`, { method: "POST" }),
    onSuccess: (data) => setRankTaskId(data.task_id),
  });

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;
    setUploading(true);
    try {
      const fd = new FormData();
      for (const f of Array.from(files)) fd.append("files", f);
      const result = await apiUpload<BatchUploadResponse>(`/candidates/job/${id}/batch`, fd);
      setBatchTaskId(result.task_id);
    } finally {
      setUploading(false);
    }
  };

  const parsed = job?.parsed_data as Record<string, unknown> | undefined;
  const requiredSkills = (parsed?.required_skills as { name: string }[]) ?? [];

  return (
    <AppShell>
      <JobSubNav jobId={id} />
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{job?.title}</h1>
          <span className="text-sm text-muted-foreground">Status: {job?.status}</span>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => rankMutation.mutate()} disabled={rankMutation.isPending || !candidates?.length}>
            <Play className="mr-2 h-4 w-4" />{rankMutation.isPending ? "Ranking..." : "Run Ranking"}
          </Button>
          <Link href={`/jobs/${id}/settings`}><Button variant="outline"><Settings className="h-4 w-4" /></Button></Link>
        </div>
      </div>

      {(rankTaskId || batchTaskId) && (
        <div className="mb-6 space-y-3">
          {rankTaskId && (
            <ProgressTracker taskId={rankTaskId} label="Ranking in progress" onComplete={() => {
              setRankTaskId(null);
              qc.invalidateQueries({ queryKey: ["rankings", id] });
              qc.invalidateQueries({ queryKey: ["ranking-runs", id] });
            }} />
          )}
          {batchTaskId && (
            <ProgressTracker taskId={batchTaskId} label="Parsing resumes" onComplete={() => {
              setBatchTaskId(null);
              qc.invalidateQueries({ queryKey: ["candidates", id] });
            }} />
          )}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader><CardTitle>JD Intelligence</CardTitle></CardHeader>
            <CardContent>
              <div className="mb-4 flex flex-wrap gap-2">
                {requiredSkills.map((s, i) => (
                  <span key={i} className="rounded-full bg-blue-100 px-3 py-1 text-xs text-blue-800">
                    {typeof s === "object" ? s.name : String(s)}
                  </span>
                ))}
              </div>
              <p className="text-sm"><strong>Seniority:</strong> {String(parsed?.seniority ?? "N/A")}</p>
              <p className="mt-2 text-sm text-muted-foreground line-clamp-4">{job?.description}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2"><Users className="h-5 w-5" />Candidates ({candidates?.length ?? 0})</CardTitle>
              <label>
                <Button variant="outline" size="sm" asChild disabled={uploading}>
                  <span><Upload className="mr-2 h-4 w-4" />{uploading ? "Uploading..." : "Batch Upload"}</span>
                </Button>
                <input type="file" multiple accept=".pdf,.docx,.txt" className="hidden" onChange={handleUpload} />
              </label>
            </CardHeader>
            <CardContent>
              {(candidates ?? []).map((c) => (
                <Link key={c.id} href={`/candidates/${c.id}`} className="flex items-center justify-between border-b py-2 last:border-0 hover:bg-slate-50">
                  <span>{c.name ?? "Unknown"}</span>
                  <span className="text-xs text-muted-foreground">{c.status}</span>
                </Link>
              ))}
              {!candidates?.length && <p className="text-sm text-muted-foreground">Upload resumes to get started.</p>}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><Trophy className="h-5 w-5" />Shortlist</CardTitle></CardHeader>
            <CardContent>
              {(shortlist?.rankings ?? []).slice(0, 10).map((r) => (
                <div key={r.id} className="mb-3 border-b pb-3 last:border-0">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">#{r.rank} {r.candidate?.name}</span>
                    <span className="font-bold text-primary">{formatScore(r.final_score)}</span>
                  </div>
                  <span className={`text-xs ${getConfidenceBadge(r.confidence_level)}`}>{r.confidence_level}</span>
                  {r.human_review_required && <span className="ml-2 text-xs text-orange-600">Review needed</span>}
                </div>
              ))}
              {!shortlist?.rankings?.length && <p className="text-sm text-muted-foreground">Run ranking to see shortlist.</p>}
              {shortlist?.rankings?.length ? (
                <Link href={`/rankings?job=${id}`}><Button variant="link" className="mt-2 p-0">View full rankings →</Button></Link>
              ) : null}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
