-- Resume-Centric Smart Shortlister Database Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users & Auth
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'recruiter',
    organization VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Jobs
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    raw_text TEXT,
    file_path VARCHAR(1000),
    file_type VARCHAR(20),
    status VARCHAR(50) DEFAULT 'draft',
    parsed_data JSONB DEFAULT '{}',
    ideal_profile JSONB DEFAULT '{}',
    borderline_profile JSONB DEFAULT '{}',
    high_risk_profile JSONB DEFAULT '{}',
    hidden_requirements JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recruiter Overrides
CREATE TABLE recruiter_overrides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID UNIQUE REFERENCES jobs(id) ON DELETE CASCADE,
    required_skills JSONB DEFAULT '[]',
    nice_to_have_skills JSONB DEFAULT '[]',
    certifications JSONB DEFAULT '[]',
    education_requirements JSONB DEFAULT '[]',
    min_years_experience DECIMAL(4,1) DEFAULT 0,
    location_requirements JSONB DEFAULT '[]',
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    priority_skills JSONB DEFAULT '[]',
    weights JSONB DEFAULT '{
        "semantic_fit": 0.15,
        "skill_coverage": 0.15,
        "career_trajectory": 0.10,
        "must_have_coverage": 0.15,
        "reciprocal_fit": 0.10,
        "interview_readiness": 0.10,
        "verification_score": 0.05,
        "leadership": 0.05,
        "domain_experience": 0.10,
        "credibility_penalty": 0.05
    }',
    knockout_filters JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Candidates
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    file_path VARCHAR(1000),
    file_type VARCHAR(20),
    raw_text TEXT,
    parsed_data JSONB DEFAULT '{}',
    normalized_profile JSONB DEFAULT '{}',
    career_metrics JSONB DEFAULT '{}',
    skill_graph JSONB DEFAULT '{}',
    credibility JSONB DEFAULT '{}',
    blind_profile JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_candidates_job ON candidates(job_id);
CREATE INDEX idx_candidates_name_trgm ON candidates USING gin (name gin_trgm_ops);

-- Rankings
CREATE TABLE rankings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    rank INTEGER,
    final_score DECIMAL(6,4),
    score_breakdown JSONB DEFAULT '{}',
    semantic_fit DECIMAL(6,4),
    skill_coverage DECIMAL(6,4),
    career_trajectory DECIMAL(6,4),
    must_have_coverage DECIMAL(6,4),
    reciprocal_fit DECIMAL(6,4),
    interview_readiness DECIMAL(6,4),
    verification_score DECIMAL(6,4),
    leadership_score DECIMAL(6,4),
    domain_experience DECIMAL(6,4),
    credibility_penalty DECIMAL(6,4),
    confidence_score DECIMAL(6,4),
    confidence_level VARCHAR(20),
    eligibility_status VARCHAR(50) DEFAULT 'eligible',
    ineligibility_reasons JSONB DEFAULT '[]',
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    missing_requirements JSONB DEFAULT '[]',
    evidence JSONB DEFAULT '[]',
    human_review_required BOOLEAN DEFAULT FALSE,
    human_review_reasons JSONB DEFAULT '[]',
    bias_audit JSONB DEFAULT '{}',
    explanation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(job_id, candidate_id)
);

CREATE INDEX idx_rankings_job_score ON rankings(job_id, final_score DESC);

-- Interview Simulations
CREATE TABLE interview_simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    transcript JSONB DEFAULT '[]',
    readiness_score DECIMAL(6,4),
    communication_score DECIMAL(6,4),
    confidence_score DECIMAL(6,4),
    red_flags JSONB DEFAULT '[]',
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    follow_up_questions JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Screening Tests
CREATE TABLE screening_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    questions JSONB DEFAULT '[]',
    responses JSONB DEFAULT '[]',
    test_score DECIMAL(6,4),
    verification_score DECIMAL(6,4),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Interview Packs
CREATE TABLE interview_packs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    technical_questions JSONB DEFAULT '[]',
    behavioral_questions JSONB DEFAULT '[]',
    follow_up_questions JSONB DEFAULT '[]',
    gap_questions JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Batch Jobs
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'queued',
    total_files INTEGER DEFAULT 0,
    processed_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    progress DECIMAL(5,2) DEFAULT 0,
    errors JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Analytics Events
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_analytics_job ON analytics_events(job_id, created_at);

-- Seed default admin user (password: admin123)
INSERT INTO users (email, password_hash, full_name, role, organization)
VALUES (
    'admin@shortlister.ai',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYVzKqJ5qK5q',
    'Admin User',
    'admin',
    'Resume Shortlister'
);
