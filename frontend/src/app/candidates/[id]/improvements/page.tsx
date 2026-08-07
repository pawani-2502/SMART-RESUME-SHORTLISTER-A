"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { api, ImprovementSuggestion, Candidate } from "@/lib/api";
import { Download, Target, BookOpen, Award, Briefcase } from "lucide-react";

const categoryIcons: Record<string, typeof Target> = {
  skill_gap: Target,
  certification: Award,
  resume_quality: BookOpen,
  address_weakness: Briefcase,
};

const priorityColors: Record<string, string> = {
  high: "border-red-200 bg-red-50",
  medium: "border-yellow-200 bg-yellow-50",
  low: "border-slate-200 bg-slate-50",
};

export default function ImprovementsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const { data: candidate } = useQuery({
    queryKey: ["candidate", id],
    queryFn: () => api<Candidate>(`/candidates/${id}`),
  });

  const { data: suggestions, isLoading } = useQuery({
    queryKey: ["improvements", id],
    queryFn: () => api<ImprovementSuggestion[]>(`/candidates/${id}/improvements`),
  });

  const exportReport = () => {
    const text = [
      `Improvement Report — ${candidate?.name ?? "Candidate"}`,
      "",
      "90-Day Improvement Plan",
      "─────────────────────",
      ...(suggestions ?? []).slice(0, 5).map((s, i) => `${i + 1}. [${s.priority}] ${s.title}\n   ${s.detail}`),
      "",
      "Learning Roadmap",
      "────────────────",
      ...(suggestions ?? []).filter((s) => s.category === "skill_gap").map((s) => `• ${s.title}: ${s.detail}`),
    ].join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `improvement-report-${id}.txt`;
    a.click();
  };

  const missingSkills = (suggestions ?? []).filter((s) => s.category === "skill_gap");
  const missingCerts = (suggestions ?? []).filter((s) => s.category === "certification");
  const experienceGaps = (suggestions ?? []).filter((s) => s.category === "address_weakness");

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link href={`/candidates/${id}`} className="text-sm text-primary hover:underline">← Back to candidate</Link>
          <h1 className="mt-2 text-2xl font-bold">Improvement Report</h1>
          <p className="text-muted-foreground">{candidate?.name} — actionable development plan</p>
        </div>
        <Button variant="outline" onClick={exportReport} disabled={!suggestions?.length}>
          <Download className="mr-2 h-4 w-4" />Export
        </Button>
      </div>

      {isLoading ? <LoadingState /> : !suggestions?.length ? (
        <EmptyState title="No improvement suggestions" description="Run ranking first to generate gap analysis." />
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Missing Skills</p><p className="text-2xl font-bold">{missingSkills.length}</p></CardContent></Card>
            <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Certifications</p><p className="text-2xl font-bold">{missingCerts.length}</p></CardContent></Card>
            <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Experience Gaps</p><p className="text-2xl font-bold">{experienceGaps.length}</p></CardContent></Card>
          </div>

          <Card>
            <CardHeader><CardTitle>90-Day Improvement Plan</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {suggestions.slice(0, 5).map((s, i) => {
                const Icon = categoryIcons[s.category] ?? Target;
                return (
                  <div key={i} className={`flex gap-3 rounded-lg border p-4 ${priorityColors[s.priority] ?? ""}`}>
                    <Icon className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{s.title}</p>
                        <span className="rounded-full bg-white px-2 py-0.5 text-xs capitalize">{s.priority}</span>
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">{s.detail}</p>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Suggested Learning Roadmap</CardTitle></CardHeader>
            <CardContent>
              <ol className="list-decimal space-y-2 pl-5 text-sm">
                {missingSkills.map((s, i) => (
                  <li key={i}><strong>{s.title}</strong> — {s.detail}</li>
                ))}
                {missingCerts.map((s, i) => (
                  <li key={`c-${i}`}><strong>Certification:</strong> {s.title} — {s.detail}</li>
                ))}
              </ol>
            </CardContent>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
