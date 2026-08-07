import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(score: number | null | undefined): string {
  if (score == null) return "N/A";
  return `${Math.round(score * 100)}%`;
}

export function getScoreColor(score: number | null | undefined): string {
  if (score == null) return "text-muted-foreground";
  if (score >= 0.75) return "text-green-600";
  if (score >= 0.55) return "text-yellow-600";
  return "text-red-600";
}

export function getConfidenceBadge(level: string | null | undefined): string {
  switch (level?.toLowerCase()) {
    case "high": return "bg-green-100 text-green-800";
    case "medium": return "bg-yellow-100 text-yellow-800";
    case "low": return "bg-red-100 text-red-800";
    default: return "bg-gray-100 text-gray-800";
  }
}
