import { FEATURE_FLAGS, FeatureFlagUtils } from '../config/featureFlags.js';
import { DirectFlow } from './keycloakFlows/directFlow.js';
import { StandardFlow } from './keycloakFlows/standardFlow.js';
import mockKeycloakService from './mockKeycloakService.js';
import { extractUserFromToken, getTokenDebugInfo, isMockToken, isTokenExpired } from '../utils/tokenUtils.js';
import { cleanOAuthUrl, isOAuthCallback } from '../utils/urlUtils.js';
import { getBaseConfig } from '../config/keycloakConfig.js'


class EnhancedAuthService {
    constructor() {
        this.keycloakConfig = this._getKeycloakConfig();
        this.backendBaseUrl = import.meta.env.VITE_AUTH_BACKEND_URL || 'http://localhost:8002';
        this.currentFlow = null;

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

    /**
     * Authenticate using the specified flow
     * @param {string} flow - Authentication flow ('direct' | 'standard' | 'auto')
     * @param {Object} credentials - Authentication credentials
     * @returns {Promise<Object>} - Authentication result
     */
    async loginWithFlow(flow = 'auto', credentials = {}) {
        try {
            // Determine actual flow to use
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
     * @param {string} username - Username
     * @param {string} password - Password
     * @returns {Promise<Object>} - Authentication result
     */
    async loginWithCredentials(username, password) {
        return this.loginWithFlow('direct', { username, password });
    }

    /**
     * Handle OAuth callback (Standard Flow)
     * @param {string} callbackUrl - Optional callback URL
     * @returns {Promise<Object>} - Authentication result
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
     * Initiate Standard Flow (OAuth redirect)
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
     * Logout from current session
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

    isAuthenticated() {
        return !!this._cachedUser;
    }

    getCurrentUser() {
        return this._cachedUser || null
    }

    getCurrentFlow() {
        return this.currentFlow || sessionStorage.getItem('authFlow') || null;
    }

    getAvailableFlows() {
        return FeatureFlagUtils.getAvailableFlows();
    }

    isFlowEnabled(flow) {
        return FeatureFlagUtils.isFlowEnabled(flow);
    }

    async loginWithGoogle() {
        return await mockKeycloakService.mockOAuthProvider('google');
    }

    async loginWithApple() {
        return await mockKeycloakService.mockOAuthProvider('apple');
    }

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

    async _handleStandardLogin(credentials = {}) {
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
        return getBaseConfig()
    }

    _detectCurrentFlow() {
        const storedFlow = localStorage.getItem('authFlow');
        if (storedFlow && FeatureFlagUtils.isFlowEnabled(storedFlow)) {
            this.currentFlow = storedFlow;
            return;
        }
        this.currentFlow = FeatureFlagUtils.getDefaultFlow()
    }

    _clearState() {
        this._cachedUser = null;
        this.currentFlow = null;
        sessionStorage.removeItem('oauth_state');
        sessionStorage.removeItem('authFlow');
        sessionStorage.removeItem('authFlowInitiated');
        cleanOAuthUrl();
    }

    removeToken() {
        this._clearState();
    }

    /** @deprecated Use handleOAuthCallback() instead */
    async exchangeCodeForToken(code) {
        console.warn('exchangeCodeForToken() is deprecated. Token exchange is handled by the backend.');
        return await this.handleOAuthCallback();
    }
}

export default new EnhancedAuthService();
