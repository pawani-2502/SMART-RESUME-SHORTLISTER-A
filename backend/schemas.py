from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    organization: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Jobs
class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    text: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class JobResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    status: str
    parsed_data: dict = {}
    ideal_profile: dict = {}
    borderline_profile: dict = {}
    high_risk_profile: dict = {}
    hidden_requirements: list = []
    created_at: datetime

    class Config:
        from_attributes = True


# Recruiter Overrides
class RecruiterOverrideCreate(BaseModel):
    required_skills: list[str] = []
    nice_to_have_skills: list[str] = []
    certifications: list[str] = []
    education_requirements: list[str] = []
    min_years_experience: float = 0
    location_requirements: list[str] = []
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    priority_skills: list[str] = []
    weights: Optional[dict] = None
    knockout_filters: Optional[dict] = None


class RecruiterOverrideResponse(BaseModel):
    id: UUID
    job_id: UUID
    required_skills: list
    nice_to_have_skills: list
    certifications: list
    education_requirements: list
    min_years_experience: float
    location_requirements: list
    salary_min: Optional[float]
    salary_max: Optional[float]
    priority_skills: list
    weights: dict
    knockout_filters: dict

    class Config:
        from_attributes = True


# Candidates
class CandidateResponse(BaseModel):
    id: UUID
    job_id: UUID
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    status: str
    parsed_data: dict = {}
    normalized_profile: dict = {}
    career_metrics: dict = {}
    skill_graph: dict = {}
    credibility: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True


# Rankings
class RankingResponse(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    rank: Optional[int]
    final_score: Optional[float]
    score_breakdown: dict = {}
    semantic_fit: Optional[float]
    skill_coverage: Optional[float]
    career_trajectory: Optional[float]
    must_have_coverage: Optional[float]
    reciprocal_fit: Optional[float]
    interview_readiness: Optional[float]
    verification_score: Optional[float]
    leadership_score: Optional[float]
    domain_experience: Optional[float]
    credibility_penalty: Optional[float]
    confidence_score: Optional[float]
    confidence_level: Optional[str]
    eligibility_status: str
    ineligibility_reasons: list = []
    strengths: list = []
    weaknesses: list = []
    missing_requirements: list = []
    evidence: list = []
    human_review_required: bool = False
    human_review_reasons: list = []
    bias_audit: dict = {}
    explanation: Optional[str]
    candidate: Optional[CandidateResponse] = None

    class Config:
        from_attributes = True


class ShortlistResponse(BaseModel):
    job_id: UUID
    total_candidates: int
    eligible_count: int
    ineligible_count: int
    rankings: list[RankingResponse]


# Comparison
class ComparisonRequest(BaseModel):
    candidate_ids: list[UUID] = Field(..., min_length=2, max_length=10)


class ComparisonResponse(BaseModel):
    job_id: UUID
    candidates: list[dict]
    skill_overlap: dict
    recommendations: list[dict]


# Interview
class InterviewSimulationResponse(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    transcript: list
    readiness_score: Optional[float]
    communication_score: Optional[float]
    confidence_score: Optional[float]
    red_flags: list
    strengths: list
    weaknesses: list
    follow_up_questions: list
    created_at: datetime

    class Config:
        from_attributes = True


class ScreeningTestResponse(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    questions: list
    responses: list
    test_score: Optional[float]
    verification_score: Optional[float]
    status: str

    class Config:
        from_attributes = True


class InterviewPackResponse(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    technical_questions: list
    behavioral_questions: list
    follow_up_questions: list
    gap_questions: list

    class Config:
        from_attributes = True


class TestSubmission(BaseModel):
    responses: list[dict]


# Batch
class BatchJobResponse(BaseModel):
    id: UUID
    job_id: UUID
    status: str
    total_files: int
    processed_files: int
    failed_files: int
    progress: float
    errors: list
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Analytics
class AnalyticsDashboard(BaseModel):
    total_jobs: int
    total_candidates: int
    total_rankings: int
    avg_score: float
    hiring_funnel: dict
    skill_distribution: list
    score_distribution: list
    experience_distribution: list
    candidate_quality: dict


# Export
class ExportRequest(BaseModel):
    format: str = Field(..., pattern="^(pdf|csv|excel|json)$")
    include_evidence: bool = True
    include_interviews: bool = False


# Evidence
class EvidenceItem(BaseModel):
    claim: str
    section: str
    snippet: str
    confidence: float


class EvidenceResponse(BaseModel):
    candidate_id: UUID
    score_type: str
    evidence: list[EvidenceItem]
