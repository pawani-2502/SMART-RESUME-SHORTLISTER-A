"use client";

import { useSearchParams } from "next/navigation";
import { useMemo } from "react";
import { WalkthroughProvider } from "../../walkthrough-engine";
import { ShowcaseThemeProvider } from "../../shared/components/ThemeProvider";
import { DemoPageContent } from "./DemoPage";
import type { DemoModeId } from "../../config/demo.config";
import "../../shared/styles/showcase.css";

export function ShowcaseDemoEntry() {
  const searchParams = useSearchParams();
  const mode = useMemo((): DemoModeId => {
    const m = searchParams.get("mode");
    return m === "quick" ? "quick" : "examiner";
  }, [searchParams]);

  return (
    <ShowcaseThemeProvider>
      <WalkthroughProvider mode={mode} autoStart={mode === "examiner"}>
        <DemoPageContent />
      </WalkthroughProvider>
    </ShowcaseThemeProvider>
  );
}
