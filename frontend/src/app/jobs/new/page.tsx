"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { apiUpload, api, Job } from "@/lib/api";

export default function NewJobPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    setLoading(true);
    try {
      let job: Job;
      if (file) {
        const fd = new FormData();
        fd.append("title", title);
        fd.append("file", file);
        job = await apiUpload<Job>("/jobs/upload", fd);
      } else {
        job = await api<Job>("/jobs", {
          method: "POST",
          body: JSON.stringify({ title, text }),
        });
      }
      router.push(`/jobs/${job.id}`);
    } catch (e) {
      alert("Failed to create job");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold">Create New Job</h1>
      <Card className="max-w-2xl">
        <CardHeader><CardTitle>Job Description</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <Input placeholder="Job Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <Textarea
            placeholder="Paste job description text here..."
            rows={12}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div>
            <p className="mb-2 text-sm text-muted-foreground">Or upload PDF/DOCX</p>
            <Input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </div>
          <Button onClick={handleCreate} disabled={!title || loading || (!text && !file)}>
            {loading ? "Analyzing..." : "Create & Analyze JD"}
          </Button>
        </CardContent>
      </Card>
    </AppShell>
  );
}
