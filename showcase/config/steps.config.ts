import type { DemoModeId } from "./demo.config";

export interface DemoStepMeta {
  id: string;
  title: string;
  subtitle: string;
  estimatedSeconds: number;
}

export const STEP_META: Record<string, DemoStepMeta> = {
  "problem-statement": { id: "problem-statement", title: "Problem Statement", subtitle: "Why traditional ATS fails", estimatedSeconds: 15 },
  "jd-intelligence": { id: "jd-intelligence", title: "JD Intelligence", subtitle: "AI-powered job description analysis", estimatedSeconds: 18 },
  "resume-intelligence": { id: "resume-intelligence", title: "Resume Intelligence", subtitle: "Structured resume extraction", estimatedSeconds: 18 },
  "career-trajectory": { id: "career-trajectory", title: "Career Trajectory", subtitle: "Growth and promotion analysis", estimatedSeconds: 15 },
  "temporal-skill-decay": { id: "temporal-skill-decay", title: "Temporal Skill Decay", subtitle: "Recency-adjusted skill scoring", estimatedSeconds: 12 },
  "latent-skill-graph": { id: "latent-skill-graph", title: "Latent Skill Graph", subtitle: "Skill ontology inference", estimatedSeconds: 15 },
  "hybrid-retrieval": { id: "hybrid-retrieval", title: "Hybrid Retrieval", subtitle: "BM25 + embeddings + reranking", estimatedSeconds: 15 },
  "scoring-engine": { id: "scoring-engine", title: "Scoring Engine", subtitle: "Multi-factor candidate scoring", estimatedSeconds: 18 },
  "evidence-grounding": { id: "evidence-grounding", title: "Evidence Grounding", subtitle: "Every score cites resume proof", estimatedSeconds: 15 },
  "shadow-interview": { id: "shadow-interview", title: "Shadow Interview", subtitle: "AI interview simulation", estimatedSeconds: 20 },
  "recruiter-copilot": { id: "recruiter-copilot", title: "Recruiter Copilot", subtitle: "AI hiring assistant", estimatedSeconds: 18 },
  "candidate-comparison": { id: "candidate-comparison", title: "Candidate Comparison", subtitle: "Side-by-side evaluation", estimatedSeconds: 15 },
  "analytics-dashboard": { id: "analytics-dashboard", title: "Analytics Dashboard", subtitle: "Hiring intelligence metrics", estimatedSeconds: 18 },
  "system-architecture": { id: "system-architecture", title: "System Architecture", subtitle: "End-to-end platform design", estimatedSeconds: 15 },
  "tech-stack": { id: "tech-stack", title: "Tech Stack", subtitle: "Technologies powering the platform", estimatedSeconds: 12 },
  "feature-showcase": { id: "feature-showcase", title: "Feature Showcase", subtitle: "Complete capability overview", estimatedSeconds: 15 },
  "developer-profile": { id: "developer-profile", title: "Developer Profile", subtitle: "Meet the builder", estimatedSeconds: 12 },
  "project-impact": { id: "project-impact", title: "Project Impact", subtitle: "Scale and achievements", estimatedSeconds: 12 },
  "roadmap": { id: "roadmap", title: "Roadmap", subtitle: "Future vision", estimatedSeconds: 12 },
  "final-screen": { id: "final-screen", title: "Thank You", subtitle: "Walkthrough complete", estimatedSeconds: 10 },
};

export interface WalkthroughState {
  mode: DemoModeId;
  phase: "intro" | "loading" | "walkthrough" | "complete";
  currentStepIndex: number;
  stepIds: string[];
  isAutoPlaying: boolean;
  isPaused: boolean;
}
