"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api, Job } from "@/lib/api";
import { Plus, Briefcase } from "lucide-react";

export default function JobsPage() {
  const { data: jobs, isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => api<Job[]>("/jobs"),
  });

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Jobs</h1>
        <Link href="/jobs/new"><Button><Plus className="mr-2 h-4 w-4" />New Job</Button></Link>
      </div>

      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {(jobs ?? []).map((job) => (
            <Link key={job.id} href={`/jobs/${job.id}`}>
              <Card className="transition-shadow hover:shadow-md">
                <CardHeader>
                  <div className="flex items-start gap-3">
                    <Briefcase className="mt-1 h-5 w-5 text-primary" />
                    <div>
                      <CardTitle className="text-lg">{job.title}</CardTitle>
                      <span className={`mt-1 inline-block rounded-full px-2 py-0.5 text-xs ${
                        job.status === "ranked" ? "bg-green-100 text-green-800" : "bg-slate-100 text-slate-600"
                      }`}>{job.status}</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="line-clamp-2 text-sm text-muted-foreground">
                    {job.description || "No description"}
                  </p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    Created {new Date(job.created_at).toLocaleDateString()}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </AppShell>
  );
}
