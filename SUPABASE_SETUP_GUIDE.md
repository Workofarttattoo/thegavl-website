# Supabase Setup for The GAVL

## ✅ CONFIGURATION COMPLETE

**Your Supabase Credentials:**
- **Project URL:** `https://urqlitnxxszwmeoscpxk.supabase.co`
- **Anon Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVycWxpdG54eHN6d21lb3NjcHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2ODE0OTksImV4cCI6MjA3NjI1NzQ5OX0.t89WETnuEVablfeX7VgNtA5IqOr22jrXDhwHaWSXtRE`

**Files Created:**
- ✅ `supabase-config.js` - Supabase client configuration with authentication functions
- ✅ `index_with_supabase.html` - Website with authentication and trial system

**Next Steps:**
1. Run the SQL setup (Step 3 below) in your Supabase dashboard
2. Enable email authentication (Step 4 below)
3. Test the website by opening `index_with_supabase.html`
4. Users can now sign up and get a 3-day trial with 2 free verdicts!

---

## Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Click "Start your project"
3. Create a new organization (or use existing)
4. Click "New Project"
5. Fill in:
   - Name: `thegavl-production`
   - Database Password: (generate strong password - SAVE THIS!)
   - Region: Choose closest to your users
   - Pricing: Free tier is fine to start

## Step 2: Get Your Credentials

After project is created:

1. Go to Project Settings (gear icon)
2. Click "API" in left sidebar
3. Copy these values:

```
Project URL: https://YOUR-PROJECT.supabase.co
anon/public key: eyJhbG... (long string)
```

## Step 3: Create Database Tables

Go to SQL Editor and run this:

```sql
-- Users table (extends Supabase auth.users)
CREATE TABLE public.profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  trial_started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  trial_ends_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '3 days'),
  trial_verdicts_used INTEGER DEFAULT 0,
  trial_verdicts_limit INTEGER DEFAULT 2,
  subscription_tier TEXT DEFAULT 'trial',
  subscription_status TEXT DEFAULT 'active',
  subscription_ends_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Allow users to read their own profile
CREATE POLICY "Users can view own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

-- Allow users to update their own profile
CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- Verdicts table
CREATE TABLE public.verdicts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) NOT NULL,
  case_title TEXT NOT NULL,
  case_description TEXT,
  verdict_result JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.verdicts ENABLE ROW LEVEL SECURITY;

-- Users can only see their own verdicts
CREATE POLICY "Users can view own verdicts"
  ON public.verdicts FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own verdicts"
  ON public.verdicts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Subscriptions table
CREATE TABLE public.subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) NOT NULL,
  plan_name TEXT NOT NULL,
  price_monthly DECIMAL(10,2),
  verdicts_per_month INTEGER,
  status TEXT DEFAULT 'active',
  current_period_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  current_period_end TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own subscriptions"
  ON public.subscriptions FOR SELECT
  USING (auth.uid() = user_id);

-- Function to create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, trial_started_at, trial_ends_at)
  VALUES (
    NEW.id,
    NEW.email,
    NOW(),
    NOW() + INTERVAL '3 days'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to auto-create profile
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to check trial status
CREATE OR REPLACE FUNCTION public.check_trial_status(user_uuid UUID)
RETURNS JSONB AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT jsonb_build_object(
    'is_trial_active', (
      trial_ends_at > NOW() AND
      trial_verdicts_used < trial_verdicts_limit
    ),
    'days_remaining', EXTRACT(DAY FROM (trial_ends_at - NOW())),
    'verdicts_remaining', (trial_verdicts_limit - trial_verdicts_used),
    'subscription_tier', subscription_tier
  )
  INTO result
  FROM public.profiles
  WHERE id = user_uuid;

  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Step 4: Enable Email Authentication

1. In Supabase Dashboard → Authentication → Providers
2. Make sure "Email" is enabled
3. Configure email templates (optional but recommended)
4. For production: Set up custom SMTP (Settings → Auth → SMTP Settings)

## Step 5: Configure Redirect URLs

1. Go to Authentication → URL Configuration
2. Add these to "Redirect URLs":
   ```
   https://thegavl.com/*
   https://workofarttattoo.github.io/thegavl-website/*
   http://localhost:3000/* (for local testing)
   ```

## Step 6: Test Database

Run this query to verify tables were created:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';
```

You should see:
- profiles
- verdicts
- subscriptions

## Next Steps:

After setup complete, update the website with your:
- Project URL
- Anon key

Then users can:
1. Sign up with email
2. Get instant 3-day free trial
3. Use 2 verdict analyses OR 3 days (whichever comes first)
4. Subscribe after trial ends

---

Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.
