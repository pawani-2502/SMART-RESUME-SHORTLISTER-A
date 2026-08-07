"use client";

import { ChevronLeft, ChevronRight, Pause, Play, SkipForward } from "lucide-react";
import { useWalkthrough } from "../../walkthrough-engine";
import { ShowcaseButton } from "../../shared/components/ui";

export function DemoControls() {
  const {
    currentStepIndex,
    totalSteps,
    progress,
    estimatedRemainingSeconds,
    currentMeta,
    isAutoPlaying,
    isPaused,
    next,
    prev,
    toggleAutoPlay,
    togglePause,
    stepIds,
    goToStep,
  } = useWalkthrough();

  const mins = Math.floor(estimatedRemainingSeconds / 60);
  const secs = estimatedRemainingSeconds % 60;

  return (
    <div className="border-t bg-white/80 px-4 py-3">
      <div className="mx-auto max-w-7xl">
        <div className="mb-2 flex items-center justify-between text-xs text-slate-600">
          <span>Step {currentStepIndex + 1} of {totalSteps} — {currentMeta?.title}</span>
          <span>~{mins}:{secs.toString().padStart(2, "0")} remaining</span>
        </div>
        <div className="mb-3 h-1.5 overflow-hidden rounded-full bg-slate-200">
          <div className="h-full rounded-full bg-primary transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex gap-1">
            <ShowcaseButton variant="ghost" className="!px-3 !py-1.5" onClick={prev} disabled={currentStepIndex === 0}>
              <ChevronLeft className="h-4 w-4" /> Prev
            </ShowcaseButton>
            <ShowcaseButton variant="ghost" className="!px-3 !py-1.5" onClick={next}>
              Next <ChevronRight className="h-4 w-4" />
            </ShowcaseButton>
          </div>
          <div className="hidden gap-1 overflow-x-auto sm:flex">
            {stepIds.map((id, i) => (
              <button
                key={id}
                onClick={() => goToStep(i)}
                className={`h-2 w-2 shrink-0 rounded-full transition-colors ${i === currentStepIndex ? "bg-primary" : i < currentStepIndex ? "bg-primary/40" : "bg-slate-300"}`}
                aria-label={`Go to step ${i + 1}`}
              />
            ))}
          </div>
          <div className="flex gap-1">
            <ShowcaseButton variant="ghost" className="!px-3 !py-1.5" onClick={toggleAutoPlay}>
              {isAutoPlaying ? "Auto On" : "Auto Play"}
            </ShowcaseButton>
            {isAutoPlaying && (
              <ShowcaseButton variant="ghost" className="!px-3 !py-1.5" onClick={togglePause}>
                {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
              </ShowcaseButton>
            )}
            <ShowcaseButton variant="primary" className="!px-3 !py-1.5" onClick={next}>
              <SkipForward className="h-4 w-4" /> Skip
            </ShowcaseButton>
          </div>
        </div>
      </div>
    </div>
  );
}
