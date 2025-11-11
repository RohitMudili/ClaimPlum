-- Supabase Schema for Plum OPD Claim Adjudication System
-- Run this in your Supabase SQL Editor

-- ============================================
-- 1. MEMBERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS members (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    policy_number TEXT UNIQUE NOT NULL,
    policy_start_date TIMESTAMPTZ NOT NULL,
    policy_end_date TIMESTAMPTZ,
    policy_status TEXT DEFAULT 'active',
    annual_limit DECIMAL(10,2) DEFAULT 50000.00,
    ytd_claims DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX idx_members_policy_number ON members(policy_number);
CREATE INDEX idx_members_status ON members(policy_status);

-- ============================================
-- 2. CLAIMS TABLE
-- ============================================
CREATE TYPE claim_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');

CREATE TABLE IF NOT EXISTS claims (
    id SERIAL PRIMARY KEY,
    claim_id TEXT UNIQUE NOT NULL,
    member_id TEXT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    submission_date TIMESTAMPTZ DEFAULT NOW(),
    treatment_date TIMESTAMPTZ,
    status claim_status DEFAULT 'PENDING',
    claim_amount DECIMAL(10,2) DEFAULT 0.00,
    approved_amount DECIMAL(10,2) DEFAULT 0.00,
    decision TEXT,
    confidence_score DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Indexes for fast queries
CREATE INDEX idx_claims_claim_id ON claims(claim_id);
CREATE INDEX idx_claims_member_id ON claims(member_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_submission_date ON claims(submission_date DESC);

-- ============================================
-- 3. DOCUMENTS TABLE
-- ============================================
CREATE TYPE document_type AS ENUM ('PRESCRIPTION', 'BILL', 'TEST_REPORT', 'OTHER');

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    claim_id INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    document_type document_type NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    extracted_data JSONB,
    processing_status TEXT DEFAULT 'pending',
    processing_method TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_documents_claim_id ON documents(claim_id);

-- ============================================
-- 4. DECISIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS decisions (
    id SERIAL PRIMARY KEY,
    claim_id INTEGER UNIQUE NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    decision_type TEXT NOT NULL,
    approved_amount DECIMAL(10,2) DEFAULT 0.00,
    claimed_amount DECIMAL(10,2) DEFAULT 0.00,
    copay_amount DECIMAL(10,2) DEFAULT 0.00,
    non_covered_amount DECIMAL(10,2) DEFAULT 0.00,
    exceeded_limits_amount DECIMAL(10,2) DEFAULT 0.00,
    network_discount DECIMAL(10,2) DEFAULT 0.00,
    confidence_score DECIMAL(3,2) DEFAULT 0.00,
    fraud_flags JSONB DEFAULT '[]'::jsonb,
    rejection_reasons JSONB DEFAULT '[]'::jsonb,
    adjudication_steps JSONB,
    notes TEXT,
    next_steps TEXT,
    is_network_hospital BOOLEAN DEFAULT FALSE,
    cashless_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_decisions_claim_id ON decisions(claim_id);

-- ============================================
-- 5. AUTO-UPDATE TIMESTAMPS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_members_updated_at BEFORE UPDATE ON members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_claims_updated_at BEFORE UPDATE ON claims
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 6. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on all tables
ALTER TABLE members ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;

-- MEMBERS POLICIES
-- Allow service role full access
CREATE POLICY "Service role has full access to members"
    ON members
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Allow authenticated users to read all members
CREATE POLICY "Authenticated users can read members"
    ON members
    FOR SELECT
    TO authenticated
    USING (true);

-- CLAIMS POLICIES
-- Service role full access
CREATE POLICY "Service role has full access to claims"
    ON claims
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Authenticated users can read all claims
CREATE POLICY "Authenticated users can read claims"
    ON claims
    FOR SELECT
    TO authenticated
    USING (true);

-- Authenticated users can insert claims
CREATE POLICY "Authenticated users can create claims"
    ON claims
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Authenticated users can update their claims
CREATE POLICY "Users can update claims"
    ON claims
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- DOCUMENTS POLICIES
-- Service role full access
CREATE POLICY "Service role has full access to documents"
    ON documents
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Authenticated users can read documents
CREATE POLICY "Authenticated users can read documents"
    ON documents
    FOR SELECT
    TO authenticated
    USING (true);

-- Authenticated users can insert documents
CREATE POLICY "Authenticated users can create documents"
    ON documents
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- DECISIONS POLICIES
-- Service role full access
CREATE POLICY "Service role has full access to decisions"
    ON decisions
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Authenticated users can read decisions
CREATE POLICY "Authenticated users can read decisions"
    ON decisions
    FOR SELECT
    TO authenticated
    USING (true);

-- Authenticated users can insert decisions
CREATE POLICY "Service can create decisions"
    ON decisions
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- ============================================
-- 7. HELPER VIEWS (Optional)
-- ============================================

-- View for claim summary
CREATE OR REPLACE VIEW claim_summary AS
SELECT
    c.claim_id,
    c.member_id,
    m.name as member_name,
    c.status,
    c.claim_amount,
    c.approved_amount,
    c.decision,
    c.submission_date,
    c.processed_at,
    d.decision_type,
    d.confidence_score,
    d.fraud_flags,
    d.cashless_approved
FROM claims c
JOIN members m ON c.member_id = m.id
LEFT JOIN decisions d ON d.claim_id = c.id;

-- ============================================
-- DONE! Your Supabase database is ready.
-- ============================================

-- To get your connection details:
-- 1. Go to Supabase Dashboard > Settings > API
-- 2. Copy your project URL and anon/service keys
-- 3. Add them to your .env file
