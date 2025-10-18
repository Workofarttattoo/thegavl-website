-- Quick Password Reset SQL
-- Run this in Supabase SQL Editor if you need immediate access

-- Option 1: Set a new password directly (replace YOUR_EMAIL and NEW_PASSWORD)
UPDATE auth.users 
SET encrypted_password = crypt('NEW_PASSWORD', gen_salt('bf'))
WHERE email = 'YOUR_EMAIL';

-- Option 2: Delete the old account so you can create a new one
DELETE FROM auth.users WHERE email = 'YOUR_EMAIL';

-- Then sign up again with the same email and a new password!
