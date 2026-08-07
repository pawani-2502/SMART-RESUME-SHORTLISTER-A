"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, Job } from "@/lib/api";
import { Send, Bot, User } from "lucide-react";

interface ChatMessage {
  role: string;
  content: string;
  citations?: { snippet: string }[];
}

export default function CopilotPage() {
  const params = useSearchParams();
  const [jobId, setJobId] = useState(params.get("job") ?? "");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const { data: jobs } = useQuery({ queryKey: ["jobs"], queryFn: () => api<Job[]>("/jobs") });
  const activeJob = jobId || jobs?.[0]?.id || "";

  const { data: history } = useQuery({
    queryKey: ["copilot-history", activeJob],
    queryFn: () => api<ChatMessage[]>(`/jobs/${activeJob}/copilot/history`),
    enabled: !!activeJob,
  });

  const chatMutation = useMutation({
    mutationFn: (msg: string) =>
      api<{ answer: string; citations: { snippet: string }[] }>(`/jobs/${activeJob}/copilot/chat`, {
        method: "POST",
        body: JSON.stringify({ message: msg }),
      }),
    onSuccess: (data, msg) => {
      setMessages((prev) => [
        ...prev,
        { role: "user", content: msg },
        { role: "assistant", content: data.answer, citations: data.citations },
      ]);
      setMessage("");
    },
  });

  const displayMessages = messages.length ? messages : (history ?? []);
  const suggestions = [
    "Who should I interview first?",
    "What skills are missing in the candidate pool?",
    "Why is the top candidate ranked #1?",
    "Compare the top 3 candidates",
  ];

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold">Recruiter AI Copilot</h1>

      <select className="mb-4 rounded border px-3 py-2" value={activeJob} onChange={(e) => setJobId(e.target.value)}>
        {(jobs ?? []).map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
      </select>

      <Card className="flex h-[600px] flex-col">
        <CardHeader><CardTitle>Chat</CardTitle></CardHeader>
        <CardContent className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 space-y-4 overflow-y-auto pb-4">
            {displayMessages.map((m, i) => (
              <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : ""}`}>
                {m.role === "assistant" && <Bot className="h-6 w-6 shrink-0 text-primary" />}
                <div className={`max-w-[80%] rounded-lg p-3 ${m.role === "user" ? "bg-primary text-white" : "bg-slate-100"}`}>
                  <p className="text-sm">{m.content}</p>
                  {m.citations?.map((c, j) => (
                    <p key={j} className="mt-2 text-xs italic opacity-75">{c.snippet}</p>
                  ))}
                </div>
                {m.role === "user" && <User className="h-6 w-6 shrink-0" />}
              </div>
            ))}
          </div>

          <div className="mb-3 flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button key={s} onClick={() => setMessage(s)} className="rounded-full bg-slate-100 px-3 py-1 text-xs hover:bg-slate-200">
                {s}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <Input
              placeholder="Ask about candidates, rankings, or hiring decisions..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && message && chatMutation.mutate(message)}
            />
            <Button onClick={() => message && chatMutation.mutate(message)} disabled={chatMutation.isPending}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
