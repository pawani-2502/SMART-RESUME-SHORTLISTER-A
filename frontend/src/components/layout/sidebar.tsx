"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Briefcase, Users, Trophy, BarChart3, Settings,
  GitCompare, MessageSquare, LogOut, ClipboardList, FileText, History, Shield,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useSignOut } from "@/components/layout/app-shell";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/jobs", label: "Jobs", icon: Briefcase },
  { href: "/rankings", label: "Rankings", icon: Trophy },
  { href: "/comparison", label: "Compare", icon: GitCompare },
  { href: "/interview", label: "Interview Sim", icon: MessageSquare },
  { href: "/copilot", label: "AI Copilot", icon: MessageSquare },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/audit", label: "Audit Logs", icon: Shield },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const signOut = useSignOut();

  return (
    <aside className="flex h-screen w-64 flex-col border-r bg-white">
      <div className="flex h-16 items-center border-b px-6">
        <div>
          <h1 className="text-lg font-bold text-primary">Smart Shortlister</h1>
          <p className="text-xs text-muted-foreground">AI Hiring Copilot</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-4">
        <button
          onClick={signOut}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-accent"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}

export const jobSubNav = (jobId: string) => [
  { href: `/jobs/${jobId}`, label: "Overview", icon: Briefcase },
  { href: `/jobs/${jobId}/screening`, label: "Screening Tests", icon: ClipboardList },
  { href: `/jobs/${jobId}/jd-quality`, label: "JD Quality", icon: FileText },
  { href: `/jobs/${jobId}/ranking-history`, label: "Ranking History", icon: History },
  { href: `/jobs/${jobId}/settings`, label: "Settings", icon: Settings },
];

export function JobSubNav({ jobId }: { jobId: string }) {
  const pathname = usePathname();
  return (
    <div className="mb-6 flex flex-wrap gap-2 border-b pb-4">
      {jobSubNav(jobId).map((item) => {
        const Icon = item.icon;
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium",
              active ? "bg-primary text-primary-foreground" : "bg-white text-muted-foreground hover:bg-slate-100"
            )}
          >
            <Icon className="h-3.5 w-3.5" />
            {item.label}
          </Link>
        );
      })}
    </div>
  );
}
