-- ============================================================================
-- SpotBot Database Schema - Initial Setup
-- ============================================================================
--
-- Purpose: Core database structure for SpotBot AI detection platform
--
-- Tables:
--   1. users - User accounts for authentication
--   2. submissions - Content submitted for analysis (audit trail)
--   3. detection_results - AI detection outcomes linked to submissions
--
-- Design decisions:
--   - UUID primary keys: Better for distributed systems, no sequence bottlenecks
--   - Timestamps with timezone: Handle users across timezones correctly
--   - CASCADE deletes: Clean up child records automatically
--   - JSONB for analysis_details: Flexible schema for different detection methods
--
-- Deployment: PostgreSQL 14+ (requires uuid-ossp extension)
-- ============================================================================

-- Enable UUID generation (PostgreSQL doesn't have this by default)
-- Why: UUID v4 provides globally unique IDs without coordination between servers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
-- Stores user accounts for authentication and submission tracking
--
-- Why each field:
--   - id: UUID instead of integer for security (harder to enumerate users)
--   - email: Primary login identifier, must be unique
--   - username: Public display name, must be unique
--   - hashed_password: Bcrypt hash (never store plain text!)
--   - is_active: Soft delete / account suspension without data loss
--   - is_superuser: Admin privileges (future: advanced features)
--   - created_at/updated_at: Audit trail for account lifecycle
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SUBMISSIONS TABLE
-- ============================================================================
-- Audit trail of all content submitted for AI detection analysis
--
-- Why this table:
--   - Track what users are analyzing (usage patterns, popular content types)
--   - Enable re-analysis if detection algorithms improve
--   - Debugging: Can see exactly what was submitted when issues occur
--   - Privacy: User_id is nullable (allow anonymous detection)
--
-- Content storage strategy:
--   - Small text: stored directly in content_text
--   - URLs: stored in content_url, fetched by detector
--   - Files: uploaded to storage, path in file_path
--
-- Foreign key:
--   - user_id references users(id) ON DELETE CASCADE
--   - Why CASCADE: If user deleted, remove their submissions (GDPR compliance)
-- ============================================================================
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL, -- 'text', 'image', 'video', 'url', 'file'
    content_text TEXT,
    content_url TEXT,
    file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- DETECTION_RESULTS TABLE
-- ============================================================================
-- Stores AI detection analysis results with confidence scores
--
-- Two-tier confidence model:
--   - confidence_score: Overall "is this AI?" probability (0-100%)
--   - model_confidence: "Which AI made this?" probability (0-100%, ≤ confidence_score)
--
-- Example: 45% overall confidence, 42% it's GPT specifically
-- Logic: Can't be MORE sure which model than whether it's AI at all
--
-- Fields explained:
--   - is_ai_generated: Boolean decision (true if confidence ≥ 40% threshold)
--   - detected_model: gpt/claude/gemini/llama/mistral or NULL if unclear
--   - analysis_details: JSONB with full scoring breakdown (flexible schema)
--
-- Why JSONB:
--   - Different detection methods produce different metadata
--   - Can query JSON fields with PostgreSQL operators
--   - Easier to evolve schema without migrations
--
-- NUMERIC(5,2) for confidence:
--   - Stores 0.00 to 100.00 precisely
--   - Avoids floating point rounding errors
-- ============================================================================
CREATE TABLE detection_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID REFERENCES submissions(id) ON DELETE CASCADE,
    is_ai_generated BOOLEAN,
    confidence_score DECIMAL(5,2) NOT NULL, -- 0.00 to 100.00
    detected_model VARCHAR(100), -- 'gpt-4', 'claude-3', 'gemini-pro', etc.
    model_confidence DECIMAL(5,2), -- confidence in model identification
    analysis_details JSONB, -- detailed breakdown
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bot reports table (for future Phase 2)
CREATE TABLE bot_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reporter_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reported_identifier VARCHAR(255) NOT NULL, -- email, username, IP, etc.
    identifier_type VARCHAR(50) NOT NULL, -- 'email', 'ip', 'username', etc.
    platform VARCHAR(100), -- 'twitter', 'reddit', 'facebook', etc.
    confidence_score DECIMAL(5,2),
    evidence JSONB,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'confirmed', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_submissions_user_id ON submissions(user_id);
CREATE INDEX idx_submissions_created_at ON submissions(created_at DESC);
CREATE INDEX idx_detection_results_submission_id ON detection_results(submission_id);
CREATE INDEX idx_bot_reports_identifier ON bot_reports(reported_identifier);
CREATE INDEX idx_bot_reports_status ON bot_reports(status);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
