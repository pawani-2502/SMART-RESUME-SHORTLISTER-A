"use client";

import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

interface AuditEntry {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  created_at: string;
  after_data?: Record<string, unknown>;
}

export default function AuditPage() {
  const { data: logs } = useQuery({
    queryKey: ["audit"],
    queryFn: () => api<AuditEntry[]>("/audit/logs"),
  });

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold">Audit Trail</h1>
      <Card>
        <CardHeader><CardTitle>Recruitment Audit Log</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {(logs ?? []).map((log) => (
              <div key={log.id} className="flex items-center justify-between border-b py-3 last:border-0">
                <div>
                  <p className="font-medium text-sm">{log.action}</p>
                  <p className="text-xs text-muted-foreground">
                    {log.entity_type} · {log.entity_id}
                  </p>
                </div>
                <span className="text-xs text-muted-foreground">
                  {new Date(log.created_at).toLocaleString()}
                </span>
              </div>
            ))}
            {!logs?.length && <p className="text-muted-foreground">No audit events yet.</p>}
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
