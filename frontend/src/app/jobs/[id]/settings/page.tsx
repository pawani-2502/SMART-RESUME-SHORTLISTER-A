"use client";

import { use, useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LoadingState } from "@/components/ui/loading-state";
import { api, RecruiterOverride } from "@/lib/api";
import { showToast } from "@/components/ui/toast";

const WEIGHT_LABELS: Record<string, string> = {
  semantic_fit: "Semantic Fit",
  skill_coverage: "Skill Coverage",
  career_trajectory: "Career Trajectory",
  must_have_coverage: "Must-Have Coverage",
  reciprocal_fit: "Reciprocal Fit",
  interview_readiness: "Interview Readiness",
  verification_score: "Verification Score",
  leadership: "Leadership",
  domain_experience: "Domain Experience",
  credibility_penalty: "Credibility Penalty",
};

export default function JobSettingsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const qc = useQueryClient();
  const [skills, setSkills] = useState("");
  const [minYears, setMinYears] = useState(0);
  const [weights, setWeights] = useState<Record<string, number>>({});
  const [initialized, setInitialized] = useState(false);

  const { data: override, isLoading } = useQuery({
    queryKey: ["override", id],
    queryFn: () => api<RecruiterOverride>(`/jobs/${id}/override`),
  });

  useEffect(() => {
    if (override && !initialized) {
      if (override.weights) setWeights(override.weights);
      if (override.required_skills) setSkills(override.required_skills.join(", "));
      setMinYears(override.min_years_experience ?? 0);
      setInitialized(true);
    }
  }, [override, initialized]);

  const saveMutation = useMutation({
    mutationFn: () => api(`/jobs/${id}/override`, {
      method: "PUT",
      body: JSON.stringify({
        required_skills: skills.split(",").map((s) => s.trim()).filter(Boolean),
        nice_to_have_skills: override?.nice_to_have_skills ?? [],
        weights: { ...override?.weights, ...weights },
        min_years_experience: minYears,
      }),
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["override", id] });
      showToast("Recruiter overrides saved successfully");
    },
    onError: () => showToast("Failed to save overrides", "error"),
  });

  const currentWeights = { ...override?.weights, ...weights };

  if (isLoading) return <AppShell><LoadingState message="Loading settings..." /></AppShell>;

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold">Recruiter Overrides</h1>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Required Skills</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Python, React, AWS..."
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
            />
            <div>
              <label className="mb-1 block text-sm text-muted-foreground">Min years experience</label>
              <Input
                type="number"
                min={0}
                value={minYears}
                onChange={(e) => setMinYears(parseInt(e.target.value) || 0)}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Scoring Weights</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(WEIGHT_LABELS).map(([key, label]) => (
              <div key={key} className="flex items-center justify-between">
                <label className="text-sm">{label}</label>
                <Input
                  type="number" step="0.01" min="0" max="1"
                  className="w-24"
                  value={currentWeights[key] ?? 0}
                  onChange={(e) => setWeights({ ...weights, [key]: parseFloat(e.target.value) })}
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
      <Button className="mt-6" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
        {saveMutation.isPending ? "Saving..." : "Save Overrides"}
      </Button>
    </AppShell>
  );
}
