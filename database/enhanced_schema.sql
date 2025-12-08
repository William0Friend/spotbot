-- ============================================================================
-- SpotBot Enhanced Database Schema - Two-Tier Confidence System
-- ============================================================================
--
-- Purpose: Extend basic detection schema with detailed confidence tracking
--
-- New tables:
--   1. ai_model_scores - Per-model confidence scores (Tier 2)
--   2. pattern_matches - Individual pattern hits with scores
--   3. confidence_breakdown - Component scores (multi-factor breakdown)
--   4. linguistic_analysis - Text statistics and metrics
--
-- Why this enhancement:
--   - Basic schema: Single confidence score (is it AI?)
--   - Enhanced schema: Multiple model scores (which AI? how confident for each?)
--   - Pattern tracking: See exactly which patterns matched
--   - Factor breakdown: Understand how confidence was calculated
--   - Analytics: Train better models using historical pattern data
--
-- Migration strategy:
--   - Tables use IF NOT EXISTS (safe to run on existing DB)
--   - Backward compatible: detection_results still works alone
--   - Forward compatible: New detections can populate enhanced tables
--
-- Deployment: Run after init.sql, before first detection
-- ============================================================================

-- Migration note: Uncomment if you need to recreate tables
-- DROP TABLE IF EXISTS linguistic_analysis CASCADE;
-- DROP TABLE IF EXISTS confidence_breakdown CASCADE;
-- DROP TABLE IF EXISTS pattern_matches CASCADE;
-- DROP TABLE IF EXISTS ai_model_scores CASCADE;

-- ============================================================================
-- AI_MODEL_SCORES TABLE
-- ============================================================================
-- Per-model confidence scores for two-tier system
--
-- Example: Detection result has 45% overall confidence
-- This table stores: GPT 42%, Claude 40%, Gemini 15%
--
-- Why separate table:
--   - Multiple models per detection (not just "detected_model")
--   - Rank models by confidence (1st, 2nd, 3rd place)
--   - Track runner-up models (maybe it's mixed AI output?)
--
-- Use case:
--   - Show user: "70% GPT, 30% Claude" (mixed content detection)
--   - Analytics: Which models are commonly confused?
--   - Training: Build ensemble models using all scores
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_model_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detection_result_id UUID NOT NULL REFERENCES detection_results(id) ON DELETE CASCADE,
    model_name VARCHAR(50) NOT NULL, -- 'gpt', 'claude', 'gemini', 'llama', 'mistral'
    confidence_score DECIMAL(5,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    pattern_count INTEGER DEFAULT 0,
    rank INTEGER, -- Ranking among all detected models
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(detection_result_id, model_name)
);

-- Table for storing individual pattern matches
CREATE TABLE IF NOT EXISTS pattern_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detection_result_id UUID NOT NULL REFERENCES detection_results(id) ON DELETE CASCADE,
    pattern_type VARCHAR(50) NOT NULL, -- 'model_specific', 'ai_characteristic', 'unnatural_phrase', 'formatting', 'linguistic'
    pattern_category VARCHAR(50), -- Model name for model-specific patterns, or category name
    pattern_text TEXT NOT NULL, -- The actual regex or pattern that matched
    match_count INTEGER DEFAULT 1, -- Number of times this pattern matched
    score_contribution DECIMAL(5,2), -- How much this pattern contributed to the overall score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing scoring breakdown (two-tier system)
CREATE TABLE IF NOT EXISTS confidence_breakdown (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detection_result_id UUID NOT NULL REFERENCES detection_results(id) ON DELETE CASCADE,
    
    -- Overall AI confidence (Tier 1)
    overall_confidence DECIMAL(5,2) NOT NULL CHECK (overall_confidence >= 0 AND overall_confidence <= 100),
    confidence_label VARCHAR(20), -- 'Very High', 'High', 'Moderate', 'Low', 'Very Low'
    
    -- Model-specific confidence (Tier 2)
    model_confidence DECIMAL(5,2) CHECK (model_confidence >= 0 AND model_confidence <= 100),
    detected_model VARCHAR(50),
    
    -- Scoring components
    model_specific_score DECIMAL(5,2) DEFAULT 0, -- 40% weight
    ai_characteristics_score DECIMAL(5,2) DEFAULT 0, -- 25% weight
    unnatural_phrases_score DECIMAL(5,2) DEFAULT 0, -- 20% weight
    linguistic_patterns_score DECIMAL(5,2) DEFAULT 0, -- 10% weight
    formatting_score DECIMAL(5,2) DEFAULT 0, -- 5% weight
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(detection_result_id)
);

-- Table for storing linguistic analysis details
CREATE TABLE IF NOT EXISTS linguistic_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detection_result_id UUID NOT NULL REFERENCES detection_results(id) ON DELETE CASCADE,
    text_length INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    sentence_count INTEGER NOT NULL,
    avg_sentence_length DECIMAL(6,2),
    sentence_length_variance DECIMAL(8,2),
    comma_ratio DECIMAL(4,2),
    paragraph_breaks INTEGER DEFAULT 0,
    analysis_notes TEXT[], -- Array of linguistic observations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(detection_result_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_model_scores_detection ON ai_model_scores(detection_result_id);
CREATE INDEX IF NOT EXISTS idx_ai_model_scores_model ON ai_model_scores(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_model_scores_confidence ON ai_model_scores(confidence_score DESC);

CREATE INDEX IF NOT EXISTS idx_pattern_matches_detection ON pattern_matches(detection_result_id);
CREATE INDEX IF NOT EXISTS idx_pattern_matches_type ON pattern_matches(pattern_type);
CREATE INDEX IF NOT EXISTS idx_pattern_matches_category ON pattern_matches(pattern_category);

CREATE INDEX IF NOT EXISTS idx_confidence_breakdown_detection ON confidence_breakdown(detection_result_id);
CREATE INDEX IF NOT EXISTS idx_confidence_breakdown_model ON confidence_breakdown(detected_model);
CREATE INDEX IF NOT EXISTS idx_confidence_breakdown_overall ON confidence_breakdown(overall_confidence DESC);

CREATE INDEX IF NOT EXISTS idx_linguistic_analysis_detection ON linguistic_analysis(detection_result_id);

-- View for easy querying of complete detection results with two-tier confidence
CREATE OR REPLACE VIEW detection_results_detailed AS
SELECT 
    dr.id,
    dr.submission_id,
    dr.is_ai_generated,
    dr.confidence_score,
    dr.detected_model,
    dr.model_confidence,
    dr.created_at,
    
    -- Two-tier confidence from breakdown
    cb.overall_confidence,
    cb.confidence_label,
    cb.model_confidence as tier2_model_confidence,
    cb.detected_model as tier2_detected_model,
    
    -- Scoring breakdown
    cb.model_specific_score,
    cb.ai_characteristics_score,
    cb.unnatural_phrases_score,
    cb.linguistic_patterns_score,
    cb.formatting_score,
    
    -- Linguistic details
    la.text_length,
    la.word_count,
    la.sentence_count,
    la.avg_sentence_length,
    la.sentence_length_variance,
    
    -- Aggregated pattern info
    (SELECT COUNT(*) FROM pattern_matches WHERE detection_result_id = dr.id) as total_patterns_matched,
    (SELECT COUNT(DISTINCT model_name) FROM ai_model_scores WHERE detection_result_id = dr.id) as models_detected_count
    
FROM detection_results dr
LEFT JOIN confidence_breakdown cb ON dr.id = cb.detection_result_id
LEFT JOIN linguistic_analysis la ON dr.id = la.detection_result_id;

-- Function to get top patterns for a detection
CREATE OR REPLACE FUNCTION get_top_patterns(p_detection_id UUID, p_limit INTEGER DEFAULT 10)
RETURNS TABLE (
    pattern_type VARCHAR(50),
    pattern_category VARCHAR(50),
    pattern_text TEXT,
    match_count INTEGER,
    score_contribution DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pm.pattern_type,
        pm.pattern_category,
        pm.pattern_text,
        pm.match_count,
        pm.score_contribution
    FROM pattern_matches pm
    WHERE pm.detection_result_id = p_detection_id
    ORDER BY pm.score_contribution DESC, pm.match_count DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get model ranking for a detection
CREATE OR REPLACE FUNCTION get_model_rankings(p_detection_id UUID)
RETURNS TABLE (
    model_name VARCHAR(50),
    confidence_score DECIMAL(5,2),
    pattern_count INTEGER,
    rank INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ams.model_name,
        ams.confidence_score,
        ams.pattern_count,
        ams.rank
    FROM ai_model_scores ams
    WHERE ams.detection_result_id = p_detection_id
    ORDER BY ams.rank ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE ai_model_scores IS 'Stores confidence scores for each AI model detected (Tier 2 confidence)';
COMMENT ON TABLE pattern_matches IS 'Individual pattern matches with scoring contributions';
COMMENT ON TABLE confidence_breakdown IS 'Two-tier confidence system: overall AI confidence (Tier 1) and model-specific (Tier 2)';
COMMENT ON TABLE linguistic_analysis IS 'Detailed linguistic analysis metrics';
COMMENT ON VIEW detection_results_detailed IS 'Complete detection results with two-tier confidence and aggregated metrics';
