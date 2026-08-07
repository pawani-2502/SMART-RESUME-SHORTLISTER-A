"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Loader2 } from "lucide-react";
import { LOADING_SEQUENCE } from "../../config/demo.config";
import { useWalkthrough } from "../../walkthrough-engine";
import { ShowcaseCard } from "../../shared/components/ui";

export function LoadingSequence() {
  const { loadingIndex } = useWalkthrough();

  return (
    <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-lg flex-col items-center justify-center px-6">
      <ShowcaseCard className="w-full">
        <div className="mb-6 flex justify-center">
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
            <Loader2 className="h-10 w-10 text-primary" />
          </motion.div>
        </div>
        <h2 className="text-center text-lg font-semibold text-slate-900">Preparing Demo Environment</h2>
        <p className="mt-1 text-center text-sm text-slate-600">No login · No uploads · Instant preview</p>
        <ul className="mt-8 space-y-3">
          {LOADING_SEQUENCE.map((item, i) => {
            const done = i < loadingIndex;
            const active = i === loadingIndex;
            return (
              <motion.li
                key={item}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`flex items-center gap-3 text-sm ${active ? "font-medium text-primary" : done ? "text-emerald-600" : "text-slate-500"}`}
              >
                {done ? <CheckCircle2 className="h-4 w-4 shrink-0" /> :
                 active ? <Loader2 className="h-4 w-4 shrink-0 animate-spin" /> :
                 <span className="h-4 w-4 shrink-0 rounded-full border border-slate-300" />}
                {item}
              </motion.li>
            );
          })}
        </ul>
      </ShowcaseCard>
    </div>
  );
}
