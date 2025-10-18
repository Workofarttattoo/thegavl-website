/**
 * Supabase Configuration for The GAVL
 * Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.
 */

const SUPABASE_URL = 'https://urqlitnxxszwmeoscpxk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVycWxpdG54eHN6d21lb3NjcHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2ODE0OTksImV4cCI6MjA3NjI1NzQ5OX0.t89WETnuEVablfeX7VgNtA5IqOr22jrXDhwHaWSXtRE';

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/**
 * Sign up a new user with email and password
 */
async function signUp(email, password, fullName) {
    try {
        const { data, error } = await supabase.auth.signUp({
            email: email,
            password: password,
            options: {
                data: {
                    full_name: fullName
                }
            }
        });

        if (error) throw error;

        console.log('[GAVL Auth] User signed up:', data);
        return { success: true, data };
    } catch (error) {
        console.error('[GAVL Auth] Sign up error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Sign in an existing user
 */
async function signIn(email, password) {
    try {
        const { data, error } = await supabase.auth.signInWithPassword({
            email: email,
            password: password
        });

        if (error) throw error;

        console.log('[GAVL Auth] User signed in:', data);
        return { success: true, data };
    } catch (error) {
        console.error('[GAVL Auth] Sign in error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Sign out current user
 */
async function signOut() {
    try {
        const { error } = await supabase.auth.signOut();
        if (error) throw error;

        console.log('[GAVL Auth] User signed out');
        return { success: true };
    } catch (error) {
        console.error('[GAVL Auth] Sign out error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Get current user session
 */
async function getSession() {
    try {
        const { data: { session }, error } = await supabase.auth.getSession();
        if (error) throw error;

        return { success: true, session };
    } catch (error) {
        console.error('[GAVL Auth] Get session error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Get current user profile
 */
async function getUserProfile(userId) {
    try {
        const { data, error } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', userId)
            .single();

        if (error) throw error;

        console.log('[GAVL] User profile:', data);
        return { success: true, profile: data };
    } catch (error) {
        console.error('[GAVL] Get profile error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Check trial status for current user
 */
async function checkTrialStatus(userId) {
    try {
        const { data, error } = await supabase
            .rpc('check_trial_status', { user_uuid: userId });

        if (error) throw error;

        console.log('[GAVL] Trial status:', data);
        return { success: true, status: data };
    } catch (error) {
        console.error('[GAVL] Check trial status error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Save a verdict to the database
 */
async function saveVerdict(userId, caseTitle, caseDescription, verdictResult) {
    try {
        const { data, error } = await supabase
            .from('verdicts')
            .insert([
                {
                    user_id: userId,
                    case_title: caseTitle,
                    case_description: caseDescription,
                    verdict_result: verdictResult
                }
            ])
            .select();

        if (error) throw error;

        console.log('[GAVL] Verdict saved:', data);

        // Increment verdict count in profile
        await incrementVerdictCount(userId);

        return { success: true, data };
    } catch (error) {
        console.error('[GAVL] Save verdict error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Increment verdict count for user
 */
async function incrementVerdictCount(userId) {
    try {
        const { data: profile } = await supabase
            .from('profiles')
            .select('trial_verdicts_used')
            .eq('id', userId)
            .single();

        const newCount = (profile?.trial_verdicts_used || 0) + 1;

        const { error } = await supabase
            .from('profiles')
            .update({
                trial_verdicts_used: newCount,
                updated_at: new Date().toISOString()
            })
            .eq('id', userId);

        if (error) throw error;

        console.log('[GAVL] Verdict count incremented:', newCount);
        return { success: true, count: newCount };
    } catch (error) {
        console.error('[GAVL] Increment verdict count error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Get all verdicts for a user
 */
async function getUserVerdicts(userId) {
    try {
        const { data, error } = await supabase
            .from('verdicts')
            .select('*')
            .eq('user_id', userId)
            .order('created_at', { ascending: false });

        if (error) throw error;

        console.log('[GAVL] User verdicts:', data);
        return { success: true, verdicts: data };
    } catch (error) {
        console.error('[GAVL] Get verdicts error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Listen for auth state changes
 */
function onAuthStateChange(callback) {
    supabase.auth.onAuthStateChange((event, session) => {
        console.log('[GAVL Auth] State changed:', event);
        callback(event, session);
    });
}

// Export functions for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        supabase,
        signUp,
        signIn,
        signOut,
        getSession,
        getUserProfile,
        checkTrialStatus,
        saveVerdict,
        getUserVerdicts,
        onAuthStateChange
    };
}
