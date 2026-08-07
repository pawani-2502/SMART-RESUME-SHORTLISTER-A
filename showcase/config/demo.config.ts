export const DEVELOPER = {
  name: "Pawani Sharma",
  program: "B.Tech CSE",
  year: "",
  institution: "SRM Institute of Science and Technology",
  campus: "KTR Campus, Chennai",
  interests: [
    "Artificial Intelligence",
    "Software Engineering",
    "Full Stack Development",
    "Explainable AI",
    "Intelligent Systems",
  ],
  links: {
    github: "https://github.com/pawani-2502/SMART-RESUME-SHORTLISTER-A",
    linkedin: "https://github.com/pawani-2502",
    portfolio: "https://github.com/pawani-2502",
    email: "mailto:pawani-2502@users.noreply.github.com",
  },
} as const;

export const PROJECT = {
  name: "Smart Resume Shortlister-A",
  tagline: "A Website Helpful for Recruiters — AI Recruitment Intelligence Platform",
  featureCount: 32,
  aiAgents: 4,
  analyticsModules: 6,
} as const;

export const DEMO_MODES = {
  quick: {
    id: "quick",
    label: "Quick Tour",
    durationMinutes: 2,
    stepIds: [
      "problem-statement",
      "jd-intelligence",
      "resume-intelligence",
      "scoring-engine",
      "shadow-interview",
      "recruiter-copilot",
      "analytics-dashboard",
      "feature-showcase",
      "developer-profile",
      "final-screen",
    ],
  },
  examiner: {
    id: "examiner",
    label: "Full Examiner Walkthrough",
    durationMinutes: 5,
    stepIds: [
      "problem-statement",
      "jd-intelligence",
      "resume-intelligence",
      "career-trajectory",
      "temporal-skill-decay",
      "latent-skill-graph",
      "hybrid-retrieval",
      "scoring-engine",
      "evidence-grounding",
      "shadow-interview",
      "recruiter-copilot",
      "candidate-comparison",
      "analytics-dashboard",
      "system-architecture",
      "tech-stack",
      "feature-showcase",
      "developer-profile",
      "project-impact",
      "roadmap",
      "final-screen",
    ],
  },
} as const;

export type DemoModeId = keyof typeof DEMO_MODES;

export const LOADING_SEQUENCE = [
  "Loading sample job description…",
  "Loading sample resumes…",
  "Preparing rankings…",
  "Loading interview simulations…",
  "Building analytics dashboard…",
  "Generating reports…",
  "Demo environment ready!",
];
