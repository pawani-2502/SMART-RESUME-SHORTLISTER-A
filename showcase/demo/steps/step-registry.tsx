import type { ComponentType } from "react";
import {
  StepProblemStatement, StepJDIntelligence, StepResumeIntelligence,
  StepCareerTrajectory, StepTemporalSkillDecay, StepLatentSkillGraph,
  StepHybridRetrieval, StepScoringEngine, StepEvidenceGrounding,
} from "./content/ai-steps";
import {
  StepShadowInterview, StepRecruiterCopilot, StepCandidateComparison, StepAnalyticsDashboard,
} from "./content/product-steps";
import {
  StepSystemArchitecture, StepTechStack, StepFeatureShowcase,
  StepDeveloperProfile, StepProjectImpact, StepRoadmap, StepFinalScreen,
} from "./content/meta-steps";

export const STEP_COMPONENTS: Record<string, ComponentType> = {
  "problem-statement": StepProblemStatement,
  "jd-intelligence": StepJDIntelligence,
  "resume-intelligence": StepResumeIntelligence,
  "career-trajectory": StepCareerTrajectory,
  "temporal-skill-decay": StepTemporalSkillDecay,
  "latent-skill-graph": StepLatentSkillGraph,
  "hybrid-retrieval": StepHybridRetrieval,
  "scoring-engine": StepScoringEngine,
  "evidence-grounding": StepEvidenceGrounding,
  "shadow-interview": StepShadowInterview,
  "recruiter-copilot": StepRecruiterCopilot,
  "candidate-comparison": StepCandidateComparison,
  "analytics-dashboard": StepAnalyticsDashboard,
  "system-architecture": StepSystemArchitecture,
  "tech-stack": StepTechStack,
  "feature-showcase": StepFeatureShowcase,
  "developer-profile": StepDeveloperProfile,
  "project-impact": StepProjectImpact,
  "roadmap": StepRoadmap,
  "final-screen": StepFinalScreen,
};
