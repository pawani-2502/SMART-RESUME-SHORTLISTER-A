"use client";

import { AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({ title = "Something went wrong", message, onRetry, className }: ErrorStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center rounded-lg border border-red-200 bg-red-50 py-12 px-6 text-center", className)}>
      <AlertCircle className="mb-3 h-8 w-8 text-red-500" />
      <h3 className="font-semibold text-red-900">{title}</h3>
      {message && <p className="mt-2 text-sm text-red-700">{message}</p>}
      {onRetry && <Button variant="outline" className="mt-4" onClick={onRetry}>Try again</Button>}
    </div>
  );
}
