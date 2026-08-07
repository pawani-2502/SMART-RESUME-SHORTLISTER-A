"use client";

import { cn } from "../utils";

export function ShowcaseCard({
  children,
  className,
  glow,
}: {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded-xl border bg-white p-6 shadow-sm",
        glow && "ring-1 ring-primary/20 border-primary/20",
        className
      )}
    >
      {children}
    </div>
  );
}

export function ShowcaseBadge({
  children,
  variant = "default",
}: {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning";
}) {
  const colors = {
    default: "bg-primary/10 text-primary",
    success: "bg-emerald-100 text-emerald-800",
    warning: "bg-amber-100 text-amber-800",
  };
  return (
    <span className={cn("inline-flex rounded-full px-3 py-1 text-xs font-medium", colors[variant])}>
      {children}
    </span>
  );
}

export function ShowcaseButton({
  children,
  variant = "primary",
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" }) {
  const variants = {
    primary: "bg-primary text-primary-foreground hover:bg-primary/90",
    secondary: "border border-input bg-background hover:bg-accent text-foreground",
    ghost: "hover:bg-accent hover:text-accent-foreground",
  };
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-md px-5 py-2.5 text-sm font-medium transition-colors",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
