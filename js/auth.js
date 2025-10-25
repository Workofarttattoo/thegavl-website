/**
 * Supabase Authentication Manager - TheGAVL
 * Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.
 */

class AuthManager {
    constructor() {
        if (!AUTH_CONFIG) {
            throw new Error('AUTH_CONFIG not found. Please load auth-config.js first.');
        }

        const { createClient } = supabase;
        this.supabase = createClient(AUTH_CONFIG.SUPABASE_URL, AUTH_CONFIG.SUPABASE_ANON_KEY);
        this.config = AUTH_CONFIG;
    }

    /**
     * Register a new user
     */
    async register(email, password, userData) {
        try {
            const { data, error } = await this.supabase.auth.signUp({
                email: email,
                password: password,
                options: {
                    data: {
                        ...userData,
                        registration_date: new Date().toISOString(),
                        ip_address: await this.getUserIP()
                    },
                    emailRedirectTo: `${window.location.origin}${this.config.REDIRECT_URLS.VERIFY}`
                }
            });

            if (error) throw error;

            // Store email in sessionStorage for verify-email page
            sessionStorage.setItem('signupEmail', email);

            // Log registration
            await this.logEvent('user_registration', {
                email: email,
                ...userData
            }).catch(err => console.log('Logging failed:', err));

            return {
                success: true,
                data: data,
                message: 'Account created! Check your email to verify.'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                message: error.message
            };
        }
    }

    /**
     * Login user
     */
    async login(email, password) {
        try {
            const { data, error } = await this.supabase.auth.signInWithPassword({
                email: email,
                password: password
            });

            if (error) throw error;

            // Log login event
            const user = data.user;
            await this.logEvent('user_login', {
                user_id: user.id,
                email: user.email
            }).catch(err => console.log('Logging failed:', err));

            return {
                success: true,
                data: data,
                user: user,
                message: 'Login successful'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                message: this.getLoginErrorMessage(error.message)
            };
        }
    }

    /**
     * Check if user is already logged in
     */
    async checkSession() {
        try {
            const { data: { session } } = await this.supabase.auth.getSession();
            return session;
        } catch (error) {
            console.error('Session check error:', error);
            return null;
        }
    }

    /**
     * Logout user
     */
    async logout() {
        try {
            const { error } = await this.supabase.auth.signOut();
            if (error) throw error;

            sessionStorage.removeItem('signupEmail');
            return {
                success: true,
                message: 'Logged out successfully'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Send password reset email
     */
    async resetPassword(email) {
        try {
            const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
                redirectTo: `${window.location.origin}${this.config.REDIRECT_URLS.RESET}`
            });

            if (error) throw error;

            return {
                success: true,
                message: 'Password reset email sent'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Update password after reset
     */
    async updatePassword(newPassword) {
        try {
            const { error } = await this.supabase.auth.updateUser({
                password: newPassword
            });

            if (error) throw error;

            return {
                success: true,
                message: 'Password updated successfully'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Resend verification email
     */
    async resendVerificationEmail(email) {
        try {
            const { error } = await this.supabase.auth.resend({
                type: 'signup',
                email: email,
                options: {
                    emailRedirectTo: `${window.location.origin}${this.config.REDIRECT_URLS.VERIFY}`
                }
            });

            if (error) throw error;

            localStorage.setItem('lastResendTime', Date.now().toString());

            return {
                success: true,
                message: 'Verification email sent'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get user profile
     */
    async getUserProfile(userId) {
        try {
            const { data, error } = await this.supabase
                .from('profiles')
                .select('*')
                .eq('id', userId)
                .single();

            if (error) throw error;

            return {
                success: true,
                data: data
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Update user profile
     */
    async updateUserProfile(userId, updates) {
        try {
            const { data, error } = await this.supabase
                .from('profiles')
                .update(updates)
                .eq('id', userId)
                .select()
                .single();

            if (error) throw error;

            return {
                success: true,
                data: data
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get trial status (for TheGAVL)
     */
    async getTrialStatus(userId) {
        try {
            const { data, error } = await this.supabase
                .from('trial_accounts')
                .select('*')
                .eq('user_id', userId)
                .single();

            if (error) {
                // No trial found, create one
                return await this.createTrial(userId);
            }

            const trialStart = new Date(data.trial_start_date);
            const trialEnd = new Date(trialStart.getTime() + (this.config.TRIAL.DAYS * 24 * 60 * 60 * 1000));
            const now = new Date();
            const daysRemaining = Math.max(0, Math.ceil((trialEnd - now) / (24 * 60 * 60 * 1000)));

            return {
                success: true,
                data: {
                    ...data,
                    daysRemaining,
                    isActive: now < trialEnd,
                    casesUsed: data.cases_used || 0,
                    casesRemaining: this.config.TRIAL.CASES_LIMIT - (data.cases_used || 0)
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Create trial account
     */
    async createTrial(userId) {
        try {
            const { data, error } = await this.supabase
                .from('trial_accounts')
                .insert([{
                    user_id: userId,
                    trial_start_date: new Date().toISOString(),
                    cases_used: 0,
                    is_active: true
                }])
                .select()
                .single();

            if (error) throw error;

            return {
                success: true,
                data: {
                    ...data,
                    daysRemaining: this.config.TRIAL.DAYS,
                    casesRemaining: this.config.TRIAL.CASES_LIMIT
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Log event to analytics table
     */
    async logEvent(eventName, eventData) {
        try {
            const { error } = await this.supabase
                .from('analytics')
                .insert([{
                    event_name: eventName,
                    event_data: eventData,
                    ip_address: await this.getUserIP(),
                    user_agent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                }]);

            if (error) throw error;
            return { success: true };
        } catch (error) {
            console.log('Analytics logging failed:', error);
            return { success: false };
        }
    }

    /**
     * Get user's IP address
     */
    async getUserIP() {
        try {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            return data.ip;
        } catch (error) {
            return 'unknown';
        }
    }

    /**
     * Format login error messages
     */
    getLoginErrorMessage(error) {
        if (error.includes('Invalid login credentials')) {
            return 'Invalid email or password. Please check your credentials.';
        } else if (error.includes('Email not confirmed')) {
            return 'Please verify your email address before logging in. Check your inbox.';
        } else if (error.includes('User not found')) {
            return 'No account found with this email address.';
        } else {
            return error;
        }
    }

    /**
     * Validate email format
     */
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Validate password strength
     */
    validatePassword(password) {
        return {
            isValid: password.length >= 8,
            message: password.length < 8 ? 'Password must be at least 8 characters' : 'Password is valid'
        };
    }
}

// Initialize auth manager when script loads
const authManager = new AuthManager();
