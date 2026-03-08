-- Database Schema for Telecom Call Records

CREATE TABLE IF NOT EXISTS call_records (
    id SERIAL PRIMARY KEY,
    customer_phone VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL, -- 'voice', 'whatsapp', 'chat'
    transcript TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    intent VARCHAR(50), -- billing_issue, network_issue, etc.
    outcome VARCHAR(20) NOT NULL CHECK (outcome IN ('resolved', 'escalated', 'failed')),
    confidence_score NUMERIC(3, 2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    csat_score INTEGER CHECK (csat_score BETWEEN 1 AND 5), -- Customer Satisfaction Score
    duration_seconds INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index 1: Optimize searches for recent calls by a specific customer.
-- Why: Frequently used in 'get_recent(phone)' to show history to the agent.
CREATE INDEX idx_customer_phone_date ON call_records (customer_phone, created_at DESC);

-- Index 2: Optimize analytics for intent and outcome.
-- Why: Directly supports the 'lowest_resolution_intents' query which groups by intent and filters by outcome.
CREATE INDEX idx_intent_outcome ON call_records (intent, outcome);

-- Index 3: Partition-like filtering by date for reporting.
-- Why: Speed up 'last 7 days' range queries which are common in executive dashboards.
CREATE INDEX idx_created_at_brin ON call_records USING btree (created_at);
