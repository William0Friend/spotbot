-- SpotBot Database Schema
-- Bot detection and reporting platform

-- Users table for authentication and user management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    organization VARCHAR(255),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bot reports table - core reporting functionality
CREATE TABLE bot_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID REFERENCES users(id),
    ip_address INET NOT NULL,
    user_agent TEXT,
    request_url TEXT,
    request_method VARCHAR(10),
    request_headers JSONB,
    bot_type VARCHAR(100), -- 'scraper', 'crawler', 'spam', 'malicious', etc.
    confidence_score INTEGER CHECK (confidence_score BETWEEN 0 AND 100),
    evidence_data JSONB,
    country_code VARCHAR(2),
    asn INTEGER,
    isp VARCHAR(255),
    hostname VARCHAR(255),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending' -- 'pending', 'verified', 'rejected'
);

-- Bot patterns table - for pattern recognition and detection
CREATE TABLE bot_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(100) NOT NULL, -- 'user_agent', 'behavior', 'timing', etc.
    pattern_data JSONB NOT NULL,
    detection_rules JSONB NOT NULL,
    severity VARCHAR(50) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bot networks table - for tracking related bots and networks
CREATE TABLE bot_networks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    network_name VARCHAR(255) NOT NULL,
    description TEXT,
    network_type VARCHAR(100), -- 'botnet', 'scraping_farm', 'spam_network', etc.
    ip_ranges JSONB, -- Array of IP ranges
    asn_ranges JSONB, -- Array of ASN ranges
    associated_domains JSONB, -- Array of domains
    threat_level VARCHAR(50) DEFAULT 'medium',
    is_active BOOLEAN DEFAULT true,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bot activity logs - for tracking bot behavior patterns
CREATE TABLE bot_activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ip_address INET NOT NULL,
    user_agent TEXT,
    request_count INTEGER DEFAULT 1,
    unique_urls INTEGER DEFAULT 1,
    time_window INTERVAL DEFAULT '1 hour',
    behavior_score INTEGER CHECK (behavior_score BETWEEN 0 AND 100),
    activity_data JSONB,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API usage tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(255) NOT NULL,
    ip_address INET NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    window_end TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 hour'
);

-- Whitelist for legitimate bots
CREATE TABLE bot_whitelist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ip_address INET,
    ip_range CIDR,
    user_agent_pattern TEXT,
    organization VARCHAR(255),
    description TEXT,
    added_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_bot_reports_ip ON bot_reports(ip_address);
CREATE INDEX idx_bot_reports_reported_at ON bot_reports(reported_at);
CREATE INDEX idx_bot_reports_status ON bot_reports(status);
CREATE INDEX idx_bot_reports_bot_type ON bot_reports(bot_type);
CREATE INDEX idx_bot_activity_logs_ip ON bot_activity_logs(ip_address);
CREATE INDEX idx_bot_activity_logs_detected_at ON bot_activity_logs(detected_at);
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_window ON api_usage(window_start, window_end);
CREATE INDEX idx_users_api_key ON users(api_key);
CREATE INDEX idx_users_email ON users(email);