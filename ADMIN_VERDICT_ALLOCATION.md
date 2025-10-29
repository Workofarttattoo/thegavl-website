# TheGAVL Admin - Manual Verdict Allocation Guide

**Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.**

This guide explains how to manually allocate verdicts to users after processing Square payments.

## Quick Start

After you receive payment via Square:
1. Note the customer's email and package purchased
2. Go to Supabase SQL Editor
3. Run the appropriate SQL command below
4. Customer can immediately use their verdicts

---

## SQL Commands for Verdict Allocation

### 1. Allocate Single Verdict ($39)

```sql
-- Replace 'customer@email.com' with actual customer email
-- Replace 'sqr_xxxxx' with Square payment ID

INSERT INTO verdict_purchases (
  user_email,
  purchase_type,
  verdicts_purchased,
  amount_paid,
  stripe_payment_id,
  validity_days,
  expiration_date,
  status
) VALUES (
  'customer@email.com',
  'single',
  1,
  39.00,
  'sqr_xxxxx',
  30,
  NOW() + INTERVAL '30 days',
  'completed'
);
```

### 2. Allocate Professional Package ($399 - 40 verdicts)

```sql
INSERT INTO verdict_purchases (
  user_email,
  purchase_type,
  verdicts_purchased,
  amount_paid,
  stripe_payment_id,
  validity_days,
  expiration_date,
  status
) VALUES (
  'customer@email.com',
  'professional',
  40,
  399.00,
  'sqr_xxxxx',
  90,
  NOW() + INTERVAL '90 days',
  'completed'
);
```

### 3. Allocate Firm Package ($999 - 125 verdicts)

```sql
INSERT INTO verdict_purchases (
  user_email,
  purchase_type,
  verdicts_purchased,
  amount_paid,
  stripe_payment_id,
  validity_days,
  expiration_date,
  status
) VALUES (
  'customer@email.com',
  'firm',
  125,
  999.00,
  'sqr_xxxxx',
  180,
  NOW() + INTERVAL '180 days',
  'completed'
);
```

### 4. Allocate Enterprise Package (Custom pricing, no expiration)

```sql
-- Replace [VERDICTS] and [AMOUNT] with agreed values
INSERT INTO verdict_purchases (
  user_email,
  purchase_type,
  verdicts_purchased,
  amount_paid,
  stripe_payment_id,
  validity_days,
  expiration_date,
  status
) VALUES (
  'customer@email.com',
  'enterprise',
  [VERDICTS],  -- e.g., 500
  [AMOUNT],    -- e.g., 3999.00
  'sqr_xxxxx',
  3650,  -- 10 years
  NOW() + INTERVAL '10 years',
  'completed'
);
```

---

## Checking User's Verdict Balance

Before or after allocation, check how many verdicts a user has:

```sql
-- Check user's current balance
SELECT * FROM user_verdict_balance
WHERE email = 'customer@email.com';
```

Returns:
- `trial_verdicts_remaining` - Free trial verdicts left (2 max)
- `purchased_verdicts_remaining` - Paid verdicts left
- `total_verdicts_available` - Total verdicts user can use

---

## Viewing Purchase History

See all purchases for a customer:

```sql
SELECT
  id,
  purchase_type,
  verdicts_purchased,
  amount_paid,
  purchase_date,
  expiration_date,
  status
FROM verdict_purchases
WHERE user_email = 'customer@email.com'
ORDER BY purchase_date DESC;
```

---

## Viewing Usage History

See how a customer has used their verdicts:

```sql
SELECT
  v.case_id,
  v.verdict_type,
  v.usage_date,
  v.case_metadata
FROM verdict_usage v
WHERE v.user_email = 'customer@email.com'
ORDER BY v.usage_date DESC;
```

---

## Common Admin Tasks

### Add Bonus Verdicts (Promotional/Comp)

```sql
-- Give customer 5 free verdicts (no expiration)
INSERT INTO verdict_purchases (
  user_email,
  purchase_type,
  verdicts_purchased,
  amount_paid,
  stripe_payment_id,
  validity_days,
  expiration_date,
  status
) VALUES (
  'customer@email.com',
  'promotional',
  5,
  0.00,
  'PROMO-' || to_char(NOW(), 'YYYYMMDD'),
  3650,
  NOW() + INTERVAL '10 years',
  'completed'
);
```

### Extend Expiration Date

```sql
-- Add 90 more days to a purchase
UPDATE verdict_purchases
SET expiration_date = expiration_date + INTERVAL '90 days'
WHERE id = [PURCHASE_ID];
```

### Issue Refund

```sql
-- Mark purchase as refunded
UPDATE verdict_purchases
SET status = 'refunded'
WHERE id = [PURCHASE_ID];

-- Note: This immediately removes verdicts from user's balance
```

### Reset User's Trial

```sql
-- If user had issues, reset their trial verdicts
-- This resets their enrollment date to today
UPDATE gavl_users
SET enrollment_date = NOW()
WHERE email = 'customer@email.com';
```

---

## Reporting Queries

### Daily Revenue Report

```sql
SELECT
  DATE(purchase_date) as date,
  COUNT(*) as purchases,
  SUM(amount_paid) as total_revenue,
  SUM(verdicts_purchased) as total_verdicts_sold
FROM verdict_purchases
WHERE status = 'completed'
  AND purchase_date >= NOW() - INTERVAL '30 days'
GROUP BY DATE(purchase_date)
ORDER BY date DESC;
```

### Active Users with Purchased Verdicts

```sql
SELECT
  email,
  name,
  purchased_verdicts_remaining,
  trial_verdicts_remaining
FROM user_verdict_balance
WHERE purchased_verdicts_remaining > 0
ORDER BY purchased_verdicts_remaining DESC;
```

### Top Customers

```sql
SELECT
  user_email,
  COUNT(*) as total_purchases,
  SUM(amount_paid) as lifetime_value,
  SUM(verdicts_purchased) as total_verdicts
FROM verdict_purchases
WHERE status = 'completed'
GROUP BY user_email
ORDER BY lifetime_value DESC
LIMIT 20;
```

### Expiring Verdicts (Next 7 Days)

```sql
SELECT
  p.user_email,
  u.name,
  p.verdicts_purchased,
  p.purchase_date,
  p.expiration_date,
  p.expiration_date - NOW() as days_remaining
FROM verdict_purchases p
JOIN gavl_users u ON p.user_email = u.email
WHERE p.status = 'completed'
  AND p.expiration_date BETWEEN NOW() AND NOW() + INTERVAL '7 days'
ORDER BY p.expiration_date ASC;
```

---

## Workflow: Processing a Phone Purchase

**Step-by-step workflow when customer calls:**

1. **Answer call and gather information:**
   - Customer name and email
   - Which package they want
   - Confirm pricing

2. **Process Square payment:**
   - Use Square POS or Virtual Terminal
   - Take payment (card on file, phone, or in-person)
   - Note Square payment ID

3. **Allocate verdicts in Supabase:**
   - Open Supabase SQL Editor
   - Run appropriate INSERT query (see above)
   - Replace `customer@email.com` with actual email
   - Replace `sqr_xxxxx` with Square payment ID
   - Execute query

4. **Confirm with customer:**
   - "Your [X] verdicts are now active"
   - "Log in at thegavl.com/onboarding.html"
   - "They'll expire in [X] days"

5. **Send confirmation email:**
   - Receipt from Square (automatic)
   - Welcome email with login instructions

---

## Troubleshooting

### Customer says "I don't see my verdicts"

```sql
-- Check their balance
SELECT * FROM user_verdict_balance WHERE email = 'customer@email.com';

-- Check if purchase was recorded
SELECT * FROM verdict_purchases WHERE user_email = 'customer@email.com';

-- If purchase is missing, run the INSERT command again
```

### Customer used wrong email

```sql
-- Update purchase to correct email
UPDATE verdict_purchases
SET user_email = 'correct@email.com'
WHERE user_email = 'wrong@email.com';
```

### Customer wants to transfer verdicts to different email

```sql
-- Transfer all purchases
UPDATE verdict_purchases
SET user_email = 'new@email.com'
WHERE user_email = 'old@email.com';

-- Transfer usage history
UPDATE verdict_usage
SET user_email = 'new@email.com'
WHERE user_email = 'old@email.com';
```

---

## Security Best Practices

1. **Never share Supabase credentials** - Only you should have access
2. **Always verify payment first** - Don't allocate verdicts before Square confirms
3. **Record Square payment IDs** - For audit trail and refunds
4. **Review purchases weekly** - Check for anomalies or issues
5. **Back up purchase data** - Export CSV monthly

---

## Contact Support

If you need help with Supabase or have questions:
- Supabase Docs: https://supabase.com/docs
- SQL Tutorial: https://www.postgresql.org/docs/

---

**Last Updated:** October 29, 2025
