"use client";

import { useEffect, useState, useRef, useCallback } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface TaskProgress {
  task_id: string;
  task_type: string;
  status: string;
  step: string;
  percentage: number;
  message: string;
  eta_seconds?: number;
  error?: string;
  meta?: Record<string, unknown>;
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export function useProgress(taskId: string | null | undefined, onComplete?: () => void) {
  const [progress, setProgress] = useState<TaskProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const completedRef = useRef(false);

  const handleComplete = useCallback(() => {
    if (!completedRef.current) {
      completedRef.current = true;
      onComplete?.();
    }
  }, [onComplete]);

  useEffect(() => {
    if (!taskId) return;
    completedRef.current = false;
    const token = getToken();
    if (!token) {
      setError("Not authenticated");
      return;
    }

    const url = `${API_URL}/api/v1/progress/${taskId}/stream?token=${encodeURIComponent(token)}`;
    const es = new EventSource(url);

    es.addEventListener("progress", (e) => {
      try {
        const data = JSON.parse(e.data) as TaskProgress;
        setProgress(data);
        if (data.status === "completed") {
          handleComplete();
          es.close();
        } else if (data.status === "failed") {
          setError(data.error || data.message || "Task failed");
          es.close();
        }
      } catch {
        setError("Failed to parse progress");
      }
    });

    es.onerror = () => {
      fetch(`${API_URL}/api/v1/progress/${taskId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((r) => r.json())
        .then((data: TaskProgress) => {
          setProgress(data);
          if (data.status === "completed") handleComplete();
          else if (data.status === "failed") setError(data.error || "Task failed");
        })
        .catch(() => setError("Connection lost"));
      es.close();
    };

    return () => es.close();
  }, [taskId, handleComplete]);

  return { progress, error };
}
