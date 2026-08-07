"use client";

import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, AnalyticsDashboard, Job } from "@/lib/api";
import { Briefcase, Users, Trophy, TrendingUp } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

export default function DashboardPage() {
  const { data: analytics } = useQuery({
    queryKey: ["analytics"],
    queryFn: () => api<AnalyticsDashboard>("/analytics/dashboard"),
  });

  const { data: jobs } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => api<Job[]>("/jobs"),
  });

  const metrics = [
    { label: "Total Jobs", value: analytics?.total_jobs ?? 0, icon: Briefcase },
    { label: "Candidates", value: analytics?.total_candidates ?? 0, icon: Users },
    { label: "Rankings", value: analytics?.total_rankings ?? 0, icon: Trophy },
    { label: "Avg Score", value: `${Math.round((analytics?.avg_score ?? 0) * 100)}%`, icon: TrendingUp },
  ];

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Recruitment intelligence overview</p>
        </div>
        <Link href="/jobs/new"><Button>Create Job</Button></Link>
      </div>

      <div className="mb-8 grid gap-4 md:grid-cols-4">
        {metrics.map((m) => (
          <Card key={m.label}>
            <CardContent className="flex items-center gap-4 p-6">
              <m.icon className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">{m.label}</p>
                <p className="text-2xl font-bold">{m.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Score Distribution</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={analytics?.score_distribution ?? []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Hiring Funnel</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={Object.entries(analytics?.hiring_funnel ?? {}).map(([name, value]) => ({ name, value }))}
                  dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {COLORS.map((c, i) => <Cell key={i} fill={c} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader><CardTitle>Recent Jobs</CardTitle></CardHeader>
        <CardContent>
          {(jobs ?? []).slice(0, 5).map((job) => (
            <Link key={job.id} href={`/jobs/${job.id}`} className="flex items-center justify-between border-b py-3 last:border-0 hover:bg-slate-50">
              <div>
                <p className="font-medium">{job.title}</p>
                <p className="text-sm text-muted-foreground">{job.status}</p>
              </div>
              <Button variant="ghost" size="sm">View →</Button>
            </Link>
          ))}
          {!jobs?.length && <p className="text-muted-foreground">No jobs yet. Create your first job.</p>}
        </CardContent>
      </Card>
    </AppShell>
  );
}
