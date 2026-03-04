/**
 * Enhanced Authentication Service with Flow Detection
 *
 * This service orchestrates different Keycloak authentication flows.
 *
 * For the Standard Flow (Authorization Code Grant):
 *   - The backend handles the Keycloak callback, exchanges the code for tokens,
 *     and sets an HTTPOnly session cookie.
 *   - The frontend NEVER sees or stores any tokens.
 *   - Authentication state is determined by calling the backend session endpoint.
 *
 * For the Direct Flow (Resource Owner Password Credentials):
 *   - Username/password are sent to Keycloak directly from the frontend.
 *   - This flow can also be migrated to go through the backend if desired.
 */

import { FEATURE_FLAGS, FeatureFlagUtils } from '../config/featureFlags.js';
import { DirectFlow } from './keycloakFlows/directFlow.js';
import { StandardFlow } from './keycloakFlows/standardFlow.js';
import mockKeycloakService from './mockKeycloakService.js';
import { cleanOAuthUrl } from '../utils/urlUtils.js';
import { getBaseConfig } from '../config/keycloakConfig.js';

class EnhancedAuthService {
    constructor() {
        this.keycloakConfig = this._getKeycloakConfig();
        this.backendBaseUrl = import.meta.env.VITE_AUTH_BACKEND_URL || 'http://localhost:8002';
        this.currentFlow = null;

        // In-memory user cache — never persisted to localStorage
        this._cachedUser = null;

        // Initialize flow handlers
        this.directFlow = new DirectFlow(this.keycloakConfig);
        this.standardFlow = new StandardFlow(this.keycloakConfig, this.backendBaseUrl);

        // Auto-detect current flow on initialization
        this._detectCurrentFlow();

        if (FEATURE_FLAGS.ENABLE_DEBUG_INFO) {
            console.log('🔐 Enhanced Auth Service initialized:', {
                availableFlows: FeatureFlagUtils.getAvailableFlows(),
                defaultFlow: FeatureFlagUtils.getDefaultFlow(),
                currentFlow: this.currentFlow,
                demoMode: FeatureFlagUtils.isDemoMode()
            });
        }
    }

    // ---------------------------------------------------------------------------
    // Public API
    // ---------------------------------------------------------------------------

    /**
     * Authenticate using the specified flow
     * @param {string} flow - Authentication flow ('direct' | 'standard' | 'auto')
     * @param {Object} credentials - Authentication credentials
     * @returns {Promise<Object>} - Authentication result
     */
    async loginWithFlow(flow = 'auto', credentials = {}) {
        try {
            const actualFlow = this._resolveFlow(flow);

            if (!FeatureFlagUtils.isFlowEnabled(actualFlow)) {
                throw new Error(`Flow '${actualFlow}' is not enabled`);
            }

            this.currentFlow = actualFlow;

            switch (actualFlow) {
                case 'direct':
                    return await this._handleDirectLogin(credentials);

                case 'standard':
                    return await this._handleStandardLogin(credentials);

                default:
                    throw new Error(`Unsupported flow: ${actualFlow}`);
            }
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    /**
     * Legacy method: Login with username/password (Direct Flow)
     */
    async loginWithCredentials(username, password) {
        return this.loginWithFlow('direct', { username, password });
    }

    /**
     * Handle the frontend side of the OAuth callback.
     * By the time the browser lands here, the backend has already consumed the
     * authorization code, set the HTTPOnly cookie, and redirected the browser
     * to the frontend. This method simply verifies the session with the backend.
     *
     * @returns {Promise<Object>} - Authentication result with user info
     */
    async handleOAuthCallback() {
        if (!FeatureFlagUtils.isFlowEnabled('standard')) {
            throw new Error('Standard flow is not enabled');
        }

        this.currentFlow = 'standard';
        const result = await this.standardFlow.handleCallback();
        console.log('🔵 Standard flow result:', result);
        if (result.success && result.user) {
            this._cachedUser = result.user;
        }

        return result;
    }

    /**
     * Initiate Standard Flow (OAuth redirect to Keycloak)
     * @returns {Promise<Object>} - Flow initiation result
     */
    async initiateStandardFlow() {
        if (!FeatureFlagUtils.isFlowEnabled('standard')) {
            throw new Error('Standard flow is not enabled');
        }

        this.currentFlow = 'standard';
        console.log('🔵 Initiating standard flow...');
        const result = await this.standardFlow.initiateFlow();
        console.log('🔵 Standard flow result:', result);
        return result;
    }

    /**
     * Check if an active session exists by calling the backend.
     * The HTTPOnly cookie is sent automatically by the browser.
     * Returns the user object on success, or null if not authenticated.
     *
     * @returns {Promise<Object|null>} - User info or null
     */
    async checkSession() {
        try {
            const response = await fetch(`${this.backendBaseUrl}/auth/silent_check`, {
                method: 'GET',
                credentials: 'include',
                headers: { 'Accept': 'application/json' },
            });

            if (response.status === 401 || response.status === 403) {
                this._cachedUser = null;
                return null;
            }

            if (!response.ok) {
                console.warn(`Session check returned ${response.status}`);
                this._cachedUser = null;
                return null;
            }

            const data = await response.json();
            const user = data.userinfo || data;
            this._cachedUser = user;
            return user;

        } catch (error) {
            console.error('Session check failed:', error);
            this._cachedUser = null;
            return null;
        }
    }

    /**
     * Logout: calls the backend to invalidate the session cookie,
     * then clears all in-memory and sessionStorage state.
     * @returns {Promise<Object>} - Logout result
     */
    async logout() {
        try {
            // Handle mock logout
            if (FEATURE_FLAGS.MOCK_KEYCLOAK_RESPONSES) {
                const result = await mockKeycloakService.mockLogout();
                this._clearState();
                return result;
            }

            // Call backend to invalidate the cookie
            await fetch(`${this.backendBaseUrl}/auth/logout`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Accept': 'application/json' }
            });

        } catch (logoutError) {
            console.warn('Backend logout request failed:', logoutError);
        } finally {
            this._clearState();
        }

        return { success: true };
    }

    /**
     * Check if user is authenticated.
     * Uses the in-memory cached user to avoid an extra network request.
     * For a fresh check call checkSession() directly.
     * @returns {boolean}
     */
    isAuthenticated() {
        return !!this._cachedUser;
    }

    /**
     * Get current user information from memory cache.
     * @returns {Object|null}
     */
    getCurrentUser() {
        return this._cachedUser || null;
    }

    /**
     * Get current authentication flow
     * @returns {string|null}
     */
    getCurrentFlow() {
        return this.currentFlow || sessionStorage.getItem('authFlow') || null;
    }

    /**
     * Get available authentication flows
     * @returns {Array<string>}
     */
    getAvailableFlows() {
        return FeatureFlagUtils.getAvailableFlows();
    }

    /**
     * Check if a specific flow is enabled
     * @param {string} flow
     * @returns {boolean}
     */
    isFlowEnabled(flow) {
        return FeatureFlagUtils.isFlowEnabled(flow);
    }

    // Legacy OAuth social login mocks
    async loginWithGoogle() {
        return await mockKeycloakService.mockOAuthProvider('google');
    }

    async loginWithApple() {
        return await mockKeycloakService.mockOAuthProvider('apple');
    }

    // ---------------------------------------------------------------------------
    // Private helpers
    // ---------------------------------------------------------------------------

    async _handleDirectLogin({ username, password }) {
        if (!username || !password) {
            throw new Error('Username and password are required for direct flow');
        }
        const result = await this.directFlow.authenticate(username, password);
        if (result.success && result.user) {
            this._cachedUser = result.user;
        }
        return result;
    }

    async _handleStandardLogin() {
        // Standard flow only initiates the redirect; callback is handled separately
        return await this.initiateStandardFlow();
    }

    _resolveFlow(flow) {
        if (flow === 'auto') {
            return FeatureFlagUtils.getDefaultFlow() === 'both'
                ? 'direct'
                : FeatureFlagUtils.getDefaultFlow();
        }
        return flow;
    }

    _getKeycloakConfig() {
        return getBaseConfig();
    }

    _detectCurrentFlow() {
        // Check stored flow from sessionStorage (set during initiateFlow)
        const storedFlow = sessionStorage.getItem('authFlow');
        if (storedFlow && FeatureFlagUtils.isFlowEnabled(storedFlow)) {
            this.currentFlow = storedFlow;
            return;
        }

        // Default to configured default flow
        this.currentFlow = FeatureFlagUtils.getDefaultFlow();
    }

    /**
     * Clear all in-memory and sessionStorage auth state.
     * No localStorage is used anymore.
     */
    _clearState() {
        this._cachedUser = null;
        this.currentFlow = null;
        sessionStorage.removeItem('oauth_state');
        sessionStorage.removeItem('authFlow');
        sessionStorage.removeItem('authFlowInitiated');
        cleanOAuthUrl();
    }

    /** @deprecated No tokens stored in frontend — kept for backward compatibility */
    removeToken() {
        this._clearState();
    }

    /** @deprecated Use handleOAuthCallback() instead */
    async exchangeCodeForToken() {
        console.warn('exchangeCodeForToken() is deprecated. Token exchange is handled by the backend.');
        return await this.handleOAuthCallback();
    }
}

export default new EnhancedAuthService();
