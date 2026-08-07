"use client";

import { DemoShell } from "../layouts/DemoShell";
import { IntroScreen } from "../components/IntroScreen";
import { LoadingSequence } from "../components/LoadingSequence";
import { StepRenderer } from "../steps/StepRenderer";
import { useWalkthrough } from "../../walkthrough-engine";

export function DemoPageContent() {
  const { phase } = useWalkthrough();

  return (
    <DemoShell>
      {phase === "intro" && <IntroScreen />}
      {phase === "loading" && <LoadingSequence />}
      {(phase === "walkthrough" || phase === "complete") && <StepRenderer />}
    </DemoShell>
  );
}
