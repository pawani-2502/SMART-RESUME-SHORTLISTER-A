"use client";

import { createContext, useContext, useCallback, useMemo, useState, useEffect, type ReactNode } from "react";
import { DEMO_MODES, LOADING_SEQUENCE, type DemoModeId } from "../config/demo.config";
import { STEP_META } from "../config/steps.config";
import { demoData } from "../shared/data/load-demo-data";

type Phase = "intro" | "loading" | "walkthrough" | "complete";

interface WalkthroughContextValue {
  mode: DemoModeId;
  phase: Phase;
  stepIds: string[];
  currentStepIndex: number;
  currentStepId: string | null;
  currentMeta: (typeof STEP_META)[string] | null;
  totalSteps: number;
  progress: number;
  estimatedRemainingSeconds: number;
  isAutoPlaying: boolean;
  isPaused: boolean;
  loadingIndex: number;
  data: typeof demoData;
  startDemo: () => void;
  skipToFeatures: () => void;
  next: () => void;
  prev: () => void;
  goToStep: (index: number) => void;
  toggleAutoPlay: () => void;
  togglePause: () => void;
  reset: () => void;
}

const WalkthroughContext = createContext<WalkthroughContextValue | null>(null);

export function WalkthroughProvider({
  mode,
  autoStart = false,
  children,
}: {
  mode: DemoModeId;
  autoStart?: boolean;
  children: ReactNode;
}) {
  const stepIds = DEMO_MODES[mode].stepIds;
  const [phase, setPhase] = useState<Phase>("intro");
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [loadingIndex, setLoadingIndex] = useState(0);

  const currentStepId = phase === "walkthrough" ? stepIds[currentStepIndex] ?? null : null;
  const currentMeta = currentStepId ? STEP_META[currentStepId] ?? null : null;
  const totalSteps = stepIds.length;
  const progress = phase === "walkthrough" ? ((currentStepIndex + 1) / totalSteps) * 100 : 0;

  const estimatedRemainingSeconds = useMemo(() => {
    if (phase !== "walkthrough") return DEMO_MODES[mode].durationMinutes * 60;
    return stepIds.slice(currentStepIndex).reduce((sum, id) => sum + (STEP_META[id]?.estimatedSeconds ?? 15), 0);
  }, [phase, currentStepIndex, stepIds, mode]);

  const runLoading = useCallback(() => {
    setPhase("loading");
    setLoadingIndex(0);
    let i = 0;
    const interval = setInterval(() => {
      i += 1;
      setLoadingIndex(i);
      if (i >= LOADING_SEQUENCE.length - 1) {
        clearInterval(interval);
        setTimeout(() => {
          setPhase("walkthrough");
          setCurrentStepIndex(0);
        }, 600);
      }
    }, 450);
  }, []);

  const startDemo = useCallback(() => runLoading(), [runLoading]);
  const skipToFeatures = useCallback(() => {
    setPhase("walkthrough");
    setCurrentStepIndex(0);
  }, []);

  // Examiner mode: auto-start with no intro click required
  useEffect(() => {
    if (autoStart && phase === "intro") {
      runLoading();
    }
  }, [autoStart, phase, runLoading]);

  const next = useCallback(() => {
    setCurrentStepIndex((i) => {
      if (i >= stepIds.length - 1) {
        setPhase("complete");
        return i;
      }
      return i + 1;
    });
  }, [stepIds.length]);

  const prev = useCallback(() => {
    setCurrentStepIndex((i) => Math.max(0, i - 1));
  }, []);

  const goToStep = useCallback((index: number) => {
    setCurrentStepIndex(Math.max(0, Math.min(index, stepIds.length - 1)));
    setPhase("walkthrough");
  }, [stepIds.length]);

  const reset = useCallback(() => {
    setPhase("intro");
    setCurrentStepIndex(0);
    setIsAutoPlaying(false);
    setIsPaused(false);
  }, []);

  // Auto-play
  useEffect(() => {
    if (!isAutoPlaying || isPaused || phase !== "walkthrough" || !currentMeta) return;
    const timer = setTimeout(next, currentMeta.estimatedSeconds * 1000);
    return () => clearTimeout(timer);
  }, [isAutoPlaying, isPaused, phase, currentStepIndex, currentMeta, next]);

  const value: WalkthroughContextValue = {
    mode,
    phase,
    stepIds,
    currentStepIndex,
    currentStepId,
    currentMeta,
    totalSteps,
    progress,
    estimatedRemainingSeconds,
    isAutoPlaying,
    isPaused,
    loadingIndex,
    data: demoData,
    startDemo,
    skipToFeatures,
    next,
    prev,
    goToStep,
    toggleAutoPlay: () => setIsAutoPlaying((v) => !v),
    togglePause: () => setIsPaused((v) => !v),
    reset,
  };

  return (
    <WalkthroughContext.Provider value={value}>{children}</WalkthroughContext.Provider>
  );
}

export function useWalkthrough() {
  const ctx = useContext(WalkthroughContext);
  if (!ctx) throw new Error("useWalkthrough must be used within WalkthroughProvider");
  return ctx;
}
