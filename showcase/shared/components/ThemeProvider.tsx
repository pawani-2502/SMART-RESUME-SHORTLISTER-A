"use client";

import type { ReactNode } from "react";

/** Wraps showcase pages in the same light background as the main landing page. */
export function ShowcaseThemeProvider({ children }: { children: ReactNode }) {
  return <div className="showcase-shell">{children}</div>;
}
