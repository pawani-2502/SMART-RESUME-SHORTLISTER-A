const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export async function api<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }

  const res = await fetch(`${API_URL}/api/v1${endpoint}`, { ...options, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, err.detail || "Request failed");
  }

  if (res.status === 204) return {} as T;
  const contentType = res.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    return res.json();
  }
  return res as unknown as T;
}

export async function apiUpload<T>(endpoint: string, formData: FormData): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}/api/v1${endpoint}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, err.detail || "Upload failed");
  }
  return res.json();
}

export async function apiBlob(endpoint: string): Promise<Blob> {
  const token = getToken();
  const res = await fetch(`${API_URL}/api/v1${endpoint}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new ApiError(res.status, "Download failed");
  return res.blob();
}

export async function apiDownload(endpoint: string, body: object): Promise<Blob> {
  const token = getToken();
  const res = await fetch(`${API_URL}/api/v1${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new ApiError(res.status, "Export failed");
  return res.blob();
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  organization?: string;
}

export interface Job {
  id: string;
  title: string;
  description?: string;
  status: string;
  parsed_data: Record<string, unknown>;
  ideal_profile: Record<string, unknown>;
  borderline_profile: Record<string, unknown>;
  high_risk_profile: Record<string, unknown>;
  hidden_requirements: unknown[];
  created_at: string;
}

export interface Candidate {
  id: string;
  job_id: string;
  name?: string;
  email?: string;
  status: string;
  parsed_data: Record<string, unknown>;
  career_metrics: Record<string, unknown>;
  skill_graph: Record<string, unknown>;
  credibility: Record<string, unknown>;
  created_at: string;
}

export interface EvidenceItem {
  claim: string;
  section: string;
  source?: string;
  snippet: string;
  confidence: number;
}

export interface Ranking {
  id: string;
  job_id: string;
  candidate_id: string;
  rank?: number;
  final_score?: number;
  score_breakdown: Record<string, unknown>;
  semantic_fit?: number;
  skill_coverage?: number;
  career_trajectory?: number;
  must_have_coverage?: number;
  reciprocal_fit?: number;
  interview_readiness?: number;
  confidence_score?: number;
  confidence_level?: string;
  eligibility_status: string;
  ineligibility_reasons: string[];
  strengths: string[];
  weaknesses: string[];
  missing_requirements: string[];
  evidence: EvidenceItem[];
  human_review_required: boolean;
  human_review_reasons: string[];
  bias_audit: Record<string, unknown>;
  explanation?: string;
  candidate?: Candidate;
}

export interface Shortlist {
  job_id: string;
  total_candidates: number;
  eligible_count: number;
  ineligible_count: number;
  rankings: Ranking[];
}

export interface AnalyticsDashboard {
  total_jobs: number;
  total_candidates: number;
  total_rankings: number;
  avg_score: number;
  hiring_funnel: Record<string, number>;
  skill_distribution: { skill: string; count: number }[];
  score_distribution: { range: string; count: number }[];
  experience_distribution: { range: string; count: number }[];
  candidate_quality: Record<string, number>;
}

export interface RecruiterOverride {
  id: string;
  job_id: string;
  required_skills: string[];
  nice_to_have_skills: string[];
  certifications: string[];
  education_requirements: string[];
  min_years_experience: number;
  location_requirements: string[];
  salary_min?: number;
  salary_max?: number;
  priority_skills: string[];
  weights: Record<string, number>;
  knockout_filters: Record<string, unknown>;
}

export interface ScreeningTest {
  id: string;
  job_id: string;
  candidate_id: string;
  questions: Array<{ question?: string; type?: string; options?: string[] }>;
  responses: Array<Record<string, unknown>>;
  test_score?: number;
  verification_score?: number;
  status: string;
  candidate_name?: string;
  assigned_status?: string;
  analytics?: {
    passed?: boolean;
    pass_threshold?: number;
    question_breakdown?: Array<{ question: string; score: number; feedback?: string }>;
    total_questions?: number;
    answered?: number;
  };
}

export interface InterviewPack {
  id: string;
  job_id: string;
  candidate_id: string;
  technical_questions: Array<{ question?: string } | string>;
  behavioral_questions: Array<{ question?: string } | string>;
  follow_up_questions: Array<{ question?: string } | string>;
  gap_questions: Array<{ question?: string } | string>;
  candidate_name?: string;
  job_title?: string;
  red_flags?: string[];
  interview_objectives?: string[];
}

export interface JDQualityReport {
  overall_score: number;
  clarity_score: number;
  completeness_score: number;
  inclusivity_score: number;
  issues: string[];
  suggestions: string[];
  grade: string;
}

export interface ImprovementSuggestion {
  category: string;
  title: string;
  detail: string;
  priority: string;
}

export interface MultiJobFitResult {
  job_id: string;
  job_title: string;
  fit_score: number;
  skill_coverage: number;
  experience_fit: number;
  matched_skills: string[];
  missing_skills: string[];
  seniority_target: string;
  recommendation: string;
}

export interface RankingRun {
  id: string;
  job_id: string;
  status: string;
  candidate_count: number;
  eligible_count: number;
  ineligible_count: number;
  summary_stats: Record<string, unknown>;
  override_snapshot: Record<string, unknown>;
  is_current: boolean;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface RankTaskResponse {
  run_id: string;
  task_id: string;
  status: string;
  message: string;
}

export interface BatchUploadResponse {
  batch: { id: string; status: string; total_files: number };
  task_id: string;
}
