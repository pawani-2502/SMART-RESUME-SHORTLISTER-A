"use client";

import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, AnalyticsDashboard } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line,
} from "recharts";

export default function AnalyticsPage() {
  const { data: analytics } = useQuery({
    queryKey: ["analytics"],
    queryFn: () => api<AnalyticsDashboard>("/analytics/dashboard"),
  });

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold">Analytics</h1>

      <div className="mb-8 grid gap-4 md:grid-cols-4">
        {[
          { label: "Jobs", value: analytics?.total_jobs },
          { label: "Candidates", value: analytics?.total_candidates },
          { label: "Rankings", value: analytics?.total_rankings },
          { label: "High Quality %", value: `${analytics?.candidate_quality?.high_quality_pct ?? 0}%` },
        ].map((m) => (
          <Card key={m.label}>
            <CardContent className="p-6">
              <p className="text-sm text-muted-foreground">{m.label}</p>
              <p className="text-2xl font-bold">{m.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Experience Distribution</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={analytics?.experience_distribution ?? []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Top Skills in Pool</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={(analytics?.skill_distribution ?? []).slice(0, 8)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="skill" width={80} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
