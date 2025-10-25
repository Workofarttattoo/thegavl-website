/**
 * Supabase Authentication Configuration - TheGAVL
 * Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.
 */

const AUTH_CONFIG = {
    PROJECT_NAME: 'thegavl',
    SUPABASE_URL: 'https://urqlitnxxszwmeoscpxk.supabase.co',
    SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVycWxpdG54eHN6d21lb3NjcHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA1MzE2NjAsImV4cCI6MjA3NjEwNzY2MH0.2dFr4n1h7jXdH4pLvN8qK9mX3aB5cC6dE7fG8hI9jK0',
    REDIRECT_URLS: {
        LOGIN: '/index.html',
        VERIFY: '/verify-email.html',
        RESET: '/reset-password.html'
    },
    EMAIL_CONFIG: {
        FROM: 'noreply@thegavl.com',
        VERIFICATION_SUBJECT: 'Verify your TheGAVL account',
        RESET_SUBJECT: 'Reset your TheGAVL password'
    },
    TRIAL: {
        DAYS: 14,
        CASES_LIMIT: 1000
    }
};
