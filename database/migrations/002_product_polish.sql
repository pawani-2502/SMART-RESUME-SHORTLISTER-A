-- Product polish migration (additive only)
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(1000);
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

ALTER TABLE rankings ADD COLUMN IF NOT EXISTS ranking_run_id UUID REFERENCES ranking_runs(id) ON DELETE SET NULL;

ALTER TABLE ranking_runs ADD COLUMN IF NOT EXISTS rankings_snapshot JSONB DEFAULT '[]';
ALTER TABLE ranking_runs ADD COLUMN IF NOT EXISTS summary_stats JSONB DEFAULT '{}';
ALTER TABLE ranking_runs ADD COLUMN IF NOT EXISTS is_current BOOLEAN DEFAULT TRUE;

ALTER TABLE screening_tests ADD COLUMN IF NOT EXISTS assigned_status VARCHAR(50) DEFAULT 'draft';
ALTER TABLE screening_tests ADD COLUMN IF NOT EXISTS pass_threshold DECIMAL(4,2) DEFAULT 0.6;
ALTER TABLE screening_tests ADD COLUMN IF NOT EXISTS analytics JSONB DEFAULT '{}';

ALTER TABLE interview_packs ADD COLUMN IF NOT EXISTS red_flags JSONB DEFAULT '[]';
ALTER TABLE interview_packs ADD COLUMN IF NOT EXISTS interview_objectives JSONB DEFAULT '[]';

CREATE TABLE IF NOT EXISTS task_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(100) UNIQUE NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'queued',
    current_step VARCHAR(100) DEFAULT 'queued',
    progress_pct DECIMAL(5,2) DEFAULT 0,
    eta_seconds INTEGER,
    message VARCHAR(500),
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_rankings_run ON rankings(ranking_run_id);
CREATE INDEX IF NOT EXISTS idx_ranking_runs_job ON ranking_runs(job_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_task_progress_task ON task_progress(task_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action, created_at DESC);
