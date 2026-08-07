"use client";

import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function SettingsPage() {
  const user = typeof window !== "undefined"
    ? JSON.parse(localStorage.getItem("user") || "{}")
    : {};

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold">Settings</h1>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Profile</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <p><strong>Name:</strong> {user.full_name ?? "—"}</p>
            <p><strong>Email:</strong> {user.email ?? "—"}</p>
            <p><strong>Role:</strong> {user.role ?? "recruiter"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Platform Info</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>Resume-Centric Smart Shortlister v1.0.0</p>
            <p>32 AI modules · Evidence-grounded ranking</p>
            <p>API: {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}</p>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
