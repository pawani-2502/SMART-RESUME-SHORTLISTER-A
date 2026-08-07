"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { api, Job, Shortlist } from "@/lib/api";
import { formatScore, getScoreColor, getConfidenceBadge } from "@/lib/utils";
import { apiDownload } from "@/lib/api";
import { showToast } from "@/components/ui/toast";
import { Download, AlertTriangle, Loader2 } from "lucide-react";

function RankingsContent() {
  const params = useSearchParams();
  const jobId = params.get("job");
  const [exporting, setExporting] = useState<string | null>(null);

  const { data: jobs, isLoading: jobsLoading } = useQuery({ queryKey: ["jobs"], queryFn: () => api<Job[]>("/jobs") });
  const activeJobId = jobId || jobs?.[0]?.id;

  const { data: shortlist, isLoading: rankingsLoading } = useQuery({
    queryKey: ["rankings", activeJobId],
    queryFn: () => api<Shortlist>(`/jobs/${activeJobId}/rankings`),
    enabled: !!activeJobId,
  });

  const handleExport = async (format: string) => {
    if (!activeJobId) return;
    setExporting(format);
    try {
      const blob = await apiDownload(`/jobs/${activeJobId}/export`, { format, include_evidence: true });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `shortlist.${format === "excel" ? "xlsx" : format}`;
      a.click();
      URL.revokeObjectURL(url);
      showToast(`${format.toUpperCase()} export downloaded successfully`);
    } catch {
      showToast(`Failed to export ${format.toUpperCase()}`, "error");
    } finally {
      setExporting(null);
    }
  };

  if (jobsLoading || rankingsLoading) {
    return <AppShell><LoadingState message="Loading rankings..." /></AppShell>;
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Rankings</h1>
        <div className="flex flex-wrap gap-2">
          <select
            className="rounded-lg border px-3 py-2 text-sm shadow-sm"
            value={activeJobId ?? ""}
            onChange={(e) => window.location.href = `/rankings?job=${e.target.value}`}
          >
            {(jobs ?? []).map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
          </select>
          <Button variant="outline" onClick={() => handleExport("csv")} disabled={!!exporting}>
            {exporting === "csv" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
            CSV
          </Button>
          <Button variant="outline" onClick={() => handleExport("pdf")} disabled={!!exporting}>
            {exporting === "pdf" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
            PDF
          </Button>
        </div>
      </div>

      {shortlist && (
        <div className="mb-4 flex gap-4 text-sm">
          <span>Total: {shortlist.total_candidates}</span>
          <span className="text-green-600">Eligible: {shortlist.eligible_count}</span>
          <span className="text-red-600">Ineligible: {shortlist.ineligible_count}</span>
        </div>
      )}

      {!shortlist?.rankings?.length ? (
        <EmptyState title="No rankings yet" description="Upload resumes and run ranking for this job." />
      ) : (
        <div className="space-y-4">
          {shortlist.rankings.map((r) => (
            <Card key={r.id} className={`transition-shadow hover:shadow-md ${r.eligibility_status === "ineligible" ? "opacity-60" : ""}`}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <span className="text-2xl font-bold text-muted-foreground">#{r.rank ?? "—"}</span>
                      <div>
                        <Link href={`/candidates/${r.candidate_id}`} className="text-lg font-semibold hover:underline">
                          {r.candidate?.name ?? "Unknown"}
                        </Link>
                        <div className="mt-1 flex flex-wrap gap-2">
                          <span className={`rounded-full px-2 py-0.5 text-xs ${getConfidenceBadge(r.confidence_level)}`}>
                            {r.confidence_level} confidence
                          </span>
                          {r.human_review_required && (
                            <span className="flex items-center gap-1 text-xs text-orange-600">
                              <AlertTriangle className="h-3 w-3" />Human Review
                            </span>
                          )}
                          {r.eligibility_status === "ineligible" && (
                            <span className="text-xs text-red-600">INELIGIBLE</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <p className="mt-3 text-sm text-muted-foreground">{r.explanation}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-3xl font-bold ${getScoreColor(r.final_score)}`}>{formatScore(r.final_score)}</p>
                  </div>
                </div>
                {r.strengths?.length > 0 && (
                  <div className="mt-4">
                    <p className="text-xs font-medium text-green-700">Strengths</p>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {r.strengths.slice(0, 4).map((s, i) => (
                        <span key={i} className="rounded bg-green-50 px-2 py-0.5 text-xs text-green-800">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}

export default function RankingsPage() {
  return (
    <Suspense fallback={<AppShell><LoadingState message="Loading..." /></AppShell>}>
      <RankingsContent />
    </Suspense>
  );
}
