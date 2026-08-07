"use client";

import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { useProgress } from "@/hooks/use-progress";

interface ProgressTrackerProps {
  taskId: string | null | undefined;
  onComplete?: () => void;
  label?: string;
}

export function ProgressTracker({ taskId, onComplete, label }: ProgressTrackerProps) {
  const { progress, error } = useProgress(taskId, onComplete);

  if (!taskId) return null;
  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="flex items-center gap-2 p-4 text-sm text-red-700">
          <XCircle className="h-4 w-4" /> {error}
        </CardContent>
      </Card>
    );
  }
  if (!progress) return null;

  const pct = progress.percentage ?? 0;
  const isDone = progress.status === "completed";
  const isFailed = progress.status === "failed";

  return (
    <Card>
      <CardContent className="p-4">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="flex items-center gap-2 font-medium">
            {isDone ? <CheckCircle2 className="h-4 w-4 text-green-600" /> :
             isFailed ? <XCircle className="h-4 w-4 text-red-500" /> :
             <Loader2 className="h-4 w-4 animate-spin text-primary" />}
            {label || progress.step || "Processing"}
          </span>
          <span className="text-muted-foreground">{pct}%</span>
        </div>
        <Progress value={pct} className="h-2" />
        <p className="mt-2 text-xs text-muted-foreground">{progress.message}</p>
        {progress.eta_seconds != null && progress.status === "processing" && (
          <p className="mt-1 text-xs text-muted-foreground">~{progress.eta_seconds}s remaining</p>
        )}
      </CardContent>
    </Card>
  );
}
