# Supabase Email Configuration Guide

## Quick Fix: Add Redirect URLs

1. Go to your Supabase Dashboard:
   https://supabase.com/dashboard/project/urqlitnxxszwmeoscpxk

2. Look for **Authentication** in the left sidebar

3. Click on **Settings** or **Configuration** under Authentication

4. Find **URL Configuration** section

5. Add these URLs to the "Redirect URLs" or "Site URL" field:
   ```
   http://localhost:8001/index_with_supabase.html
   http://localhost:8000/index_with_supabase.html
   https://thegavl.com/index_with_supabase.html
   ```

6. Click **Save**

## Alternative: Disable Email Confirmation via SQL

If you can't find the settings, run this SQL in the Supabase SQL Editor:

```sql
-- Disable email confirmation requirement
UPDATE auth.config 
SET enable_signup = true;

-- Or update the specific setting
ALTER TABLE auth.users 
ALTER COLUMN email_confirmed_at 
SET DEFAULT now();
```

## Or: Configure in auth.config table

```sql
-- Check current auth settings
SELECT * FROM auth.config;

-- Update to disable email confirmation
UPDATE auth.config 
SET 
  mailer_autoconfirm = true,
  sms_autoconfirm = true;
```

## Easiest Solution: Use Magic Link Instead

Instead of password signup, you can use magic link (passwordless) authentication which handles redirects automatically.

Change the signup form to use:

```javascript
const { data, error } = await supabase.auth.signInWithOtp({
  email: email,
  options: {
    emailRedirectTo: redirectUrl
  }
});
```
