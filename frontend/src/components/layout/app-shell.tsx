"use client";

import { useEffect } from "react";
import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "unauthenticated") {
      const legacy = localStorage.getItem("token");
      if (!legacy) router.push("/login");
    } else if (session?.accessToken) {
      localStorage.setItem("token", session.accessToken);
      if (session.user) localStorage.setItem("user", JSON.stringify(session.user));
    }
  }, [status, session, router]);

  if (status === "loading") {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  const hasAuth = status === "authenticated" || (typeof window !== "undefined" && localStorage.getItem("token"));
  if (!hasAuth) return null;

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-slate-50 p-6">{children}</main>
    </div>
  );
}

export function useSignOut() {
  return () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    signOut({ callbackUrl: "/login" });
  };
}
