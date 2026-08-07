"use client";

import { STEP_COMPONENTS } from "./step-registry";
import { useWalkthrough } from "../../walkthrough-engine";
import { FadeIn } from "../../shared/animations/motion";

export function StepRenderer() {
  const { currentStepId } = useWalkthrough();
  if (!currentStepId) return null;
  const Step = STEP_COMPONENTS[currentStepId];
  if (!Step) return <p className="p-8 text-center text-slate-600">Step not found: {currentStepId}</p>;

  return (
    <FadeIn key={currentStepId} className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-12">
      <Step />
    </FadeIn>
  );
}
