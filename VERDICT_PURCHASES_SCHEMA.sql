-- Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.

-- TheGAVL Verdict Purchases Schema
-- Database schema for tracking verdict token purchases via Stripe

-- Verdict Purchases Table
CREATE TABLE verdict_purchases (
  id BIGSERIAL PRIMARY KEY,
  user_email VARCHAR(255) NOT NULL,
  purchase_type VARCHAR(50) NOT NULL, -- 'single', 'professional', 'firm'
  verdicts_purchased INTEGER NOT NULL,
  amount_paid DECIMAL(10,2) NOT NULL,
  stripe_payment_id VARCHAR(255) UNIQUE,
  stripe_session_id VARCHAR(255),
  purchase_date TIMESTAMPTZ DEFAULT NOW(),
  validity_days INTEGER NOT NULL, -- 30, 90, 180
  expiration_date TIMESTAMPTZ NOT NULL,
  status VARCHAR(50) DEFAULT 'completed', -- 'pending', 'completed', 'failed', 'refunded'
  FOREIGN KEY (user_email) REFERENCES gavl_users(email) ON DELETE CASCADE
);

-- Verdict Usage Table
CREATE TABLE verdict_usage (
  id BIGSERIAL PRIMARY KEY,
  user_email VARCHAR(255) NOT NULL,
  case_id VARCHAR(100) NOT NULL,
  verdict_type VARCHAR(50) NOT NULL, -- 'trial', 'purchased'
  purchase_id BIGINT, -- References verdict_purchases if purchased
  usage_date TIMESTAMPTZ DEFAULT NOW(),
  case_metadata JSONB, -- Store case details for analytics
  FOREIGN KEY (user_email) REFERENCES gavl_users(email) ON DELETE CASCADE,
  FOREIGN KEY (purchase_id) REFERENCES verdict_purchases(id) ON DELETE SET NULL
);

-- User Verdicts Balance View
CREATE OR REPLACE VIEW user_verdict_balance AS
SELECT
  u.email,
  u.name,
  -- Trial verdicts (always 2 if within 14 days)
  CASE
    WHEN EXTRACT(DAY FROM (NOW() - u.enrollment_date)) <= 14 THEN 2
    ELSE 0
  END - COALESCE(trial_used.count, 0) AS trial_verdicts_remaining,

  -- Purchased verdicts
  COALESCE(purchased.total_verdicts, 0) - COALESCE(purchased_used.count, 0) AS purchased_verdicts_remaining,

  -- Total available verdicts
  (CASE
    WHEN EXTRACT(DAY FROM (NOW() - u.enrollment_date)) <= 14 THEN 2
    ELSE 0
  END - COALESCE(trial_used.count, 0)) +
  (COALESCE(purchased.total_verdicts, 0) - COALESCE(purchased_used.count, 0)) AS total_verdicts_available

FROM gavl_users u

-- Count trial verdicts used
LEFT JOIN (
  SELECT user_email, COUNT(*) as count
  FROM verdict_usage
  WHERE verdict_type = 'trial'
  GROUP BY user_email
) trial_used ON u.email = trial_used.user_email

-- Sum purchased verdicts (only non-expired)
LEFT JOIN (
  SELECT user_email, SUM(verdicts_purchased) as total_verdicts
  FROM verdict_purchases
  WHERE status = 'completed'
    AND expiration_date > NOW()
  GROUP BY user_email
) purchased ON u.email = purchased.user_email

-- Count purchased verdicts used
LEFT JOIN (
  SELECT user_email, COUNT(*) as count
  FROM verdict_usage
  WHERE verdict_type = 'purchased'
  GROUP BY user_email
) purchased_used ON u.email = purchased_used.user_email;

-- Indexes for performance
CREATE INDEX idx_verdict_purchases_email ON verdict_purchases(user_email);
CREATE INDEX idx_verdict_purchases_stripe ON verdict_purchases(stripe_payment_id);
CREATE INDEX idx_verdict_purchases_expiration ON verdict_purchases(expiration_date);
CREATE INDEX idx_verdict_usage_email ON verdict_usage(user_email);
CREATE INDEX idx_verdict_usage_purchase ON verdict_usage(purchase_id);

-- Row Level Security Policies
ALTER TABLE verdict_purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE verdict_usage ENABLE ROW LEVEL SECURITY;

-- Users can view their own purchases
CREATE POLICY "Users can view own purchases" ON verdict_purchases
  FOR SELECT USING (auth.jwt() ->> 'email' = user_email);

-- Users can view their own usage
CREATE POLICY "Users can view own usage" ON verdict_usage
  FOR SELECT USING (auth.jwt() ->> 'email' = user_email);

-- Public insert for purchases (webhook will confirm)
CREATE POLICY "Public can insert purchases" ON verdict_purchases
  FOR INSERT WITH CHECK (true);

-- Public insert for usage tracking
CREATE POLICY "Public can insert usage" ON verdict_usage
  FOR INSERT WITH CHECK (true);

-- Function to record verdict usage
CREATE OR REPLACE FUNCTION record_verdict_usage(
  p_user_email VARCHAR(255),
  p_case_id VARCHAR(100),
  p_case_metadata JSONB DEFAULT '{}'
) RETURNS JSONB AS $$
DECLARE
  v_trial_remaining INTEGER;
  v_purchased_remaining INTEGER;
  v_verdict_type VARCHAR(50);
  v_purchase_id BIGINT;
  v_result JSONB;
BEGIN
  -- Check available verdicts
  SELECT trial_verdicts_remaining, purchased_verdicts_remaining
  INTO v_trial_remaining, v_purchased_remaining
  FROM user_verdict_balance
  WHERE email = p_user_email;

  -- Use trial verdicts first
  IF v_trial_remaining > 0 THEN
    v_verdict_type := 'trial';
    v_purchase_id := NULL;
  ELSIF v_purchased_remaining > 0 THEN
    v_verdict_type := 'purchased';
    -- Get oldest non-expired purchase
    SELECT id INTO v_purchase_id
    FROM verdict_purchases
    WHERE user_email = p_user_email
      AND status = 'completed'
      AND expiration_date > NOW()
    ORDER BY purchase_date ASC
    LIMIT 1;
  ELSE
    -- No verdicts available
    RETURN jsonb_build_object(
      'success', false,
      'error', 'No verdicts available',
      'trial_remaining', 0,
      'purchased_remaining', 0
    );
  END IF;

  -- Record usage
  INSERT INTO verdict_usage (user_email, case_id, verdict_type, purchase_id, case_metadata)
  VALUES (p_user_email, p_case_id, v_verdict_type, v_purchase_id, p_case_metadata);

  -- Return updated balance
  SELECT jsonb_build_object(
    'success', true,
    'verdict_type', v_verdict_type,
    'trial_remaining', trial_verdicts_remaining,
    'purchased_remaining', purchased_verdicts_remaining,
    'total_remaining', total_verdicts_available
  ) INTO v_result
  FROM user_verdict_balance
  WHERE email = p_user_email;

  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user verdict balance
CREATE OR REPLACE FUNCTION get_verdict_balance(p_user_email VARCHAR(255))
RETURNS JSONB AS $$
DECLARE
  v_result JSONB;
BEGIN
  SELECT jsonb_build_object(
    'email', email,
    'trial_verdicts', trial_verdicts_remaining,
    'purchased_verdicts', purchased_verdicts_remaining,
    'total_verdicts', total_verdicts_available
  ) INTO v_result
  FROM user_verdict_balance
  WHERE email = p_user_email;

  IF v_result IS NULL THEN
    RETURN jsonb_build_object(
      'error', 'User not found',
      'trial_verdicts', 0,
      'purchased_verdicts', 0,
      'total_verdicts', 0
    );
  END IF;

  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT ON user_verdict_balance TO anon, authenticated;
GRANT EXECUTE ON FUNCTION record_verdict_usage(VARCHAR, VARCHAR, JSONB) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_verdict_balance(VARCHAR) TO anon, authenticated;

-- Sample queries for testing:
/*
-- Check user's verdict balance
SELECT * FROM user_verdict_balance WHERE email = 'test@example.com';

-- Record verdict usage
SELECT record_verdict_usage('test@example.com', 'CASE-123', '{"case_type": "constitutional"}'::jsonb);

-- View all purchases
SELECT * FROM verdict_purchases WHERE user_email = 'test@example.com';

-- View usage history
SELECT * FROM verdict_usage WHERE user_email = 'test@example.com' ORDER BY usage_date DESC;
*/
