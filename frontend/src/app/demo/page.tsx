"use client";

import { Suspense } from "react";
import { ShowcaseDemoEntry } from "@showcase/demo/pages/ShowcaseDemoEntry";

export default function DemoRoute() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center">Loading demo…</div>}>
      <ShowcaseDemoEntry />
    </Suspense>
  );
}
