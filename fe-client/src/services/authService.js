/**
 * Enhanced Authentication Service with Flow Detection
 * 
 * This service orchestrates different Keycloak authentication flows based on
 * feature flags and provides a unified interface for authentication operations.
 */

import { FEATURE_FLAGS, FeatureFlagUtils } from '../config/featureFlags.js';
import { DirectFlow } from './keycloakFlows/directFlow.js';
import { StandardFlow } from './keycloakFlows/standardFlow.js';
import mockKeycloakService from './mockKeycloakService.js';
import { 
  extractUserFromToken, 
  isTokenExpired, 
  getTokenDebugInfo,
  isMockToken 
} from '../utils/tokenUtils.js';
import { 
  isOAuthCallback,
  cleanOAuthUrl 
} from '../utils/urlUtils.js';

class EnhancedAuthService {
  constructor() {
    this.keycloakConfig = this._getKeycloakConfig();
    this.currentFlow = null;
    
    // Initialize flow handlers
    this.directFlow = new DirectFlow(this.keycloakConfig);
    this.standardFlow = new StandardFlow(this.keycloakConfig);
    
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
  async handleOAuthCallback(callbackUrl) {
    if (!FeatureFlagUtils.isFlowEnabled('standard')) {
      throw new Error('Standard flow is not enabled');
    }

    this.currentFlow = 'standard';
    return await this.standardFlow.handleCallback(callbackUrl);
  }

  /**
   * Check if current URL is an OAuth callback
   * @returns {boolean} - True if current URL is a callback
   */
  isOAuthCallback() {
    return isOAuthCallback();
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
    console.log("initating flow" );
    const result = await this.standardFlow.initiateFlow();
    console.log("result", result );
    // Return the result immediately - let the caller handle the redirect
    // This preserves the user interaction chain
    return result;
  }

  /**
   * Legacy OAuth methods (now use mock service)
   * @param {string} provider - OAuth provider name
   * @returns {Promise<Object>} - Authentication result
   */
  async loginWithGoogle() {
    return await mockKeycloakService.mockOAuthProvider('google');
  }

  async loginWithApple() {
    return await mockKeycloakService.mockOAuthProvider('apple');
  }

  /**
   * Logout from current session
   * @returns {Promise<Object>} - Logout result
   */
  async logout() {
    try {
      const token = this.getToken();
      
      // Handle mock logout
      if (FEATURE_FLAGS.MOCK_KEYCLOAK_RESPONSES || isMockToken(token)) {
        const result = await mockKeycloakService.mockLogout();
        this._clearTokens();
        this.currentFlow = null;
        return result;
      }

      // Handle real Keycloak logout
      if (token && !isMockToken(token)) {
        try {
          const logoutUrl = `${this.keycloakConfig.url}/realms/${this.keycloakConfig.realm}/protocol/openid-connect/logout`;
          
          await fetch(logoutUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'Authorization': `Bearer ${token}`
            },
            body: new URLSearchParams({
              client_id: this.keycloakConfig.clientId,
              refresh_token: localStorage.getItem('refreshToken') || ''
            })
          });
        } catch (logoutError) {
          console.warn('Keycloak logout request failed:', logoutError);
        }
      }

      this._clearTokens();
      this.currentFlow = null;

      return { success: true };
      
    } catch (error) {
      console.error('Logout failed:', error);
      
      // Always clear tokens even if logout fails
      this._clearTokens();
      this.currentFlow = null;
      
      throw error;
    }
  }

  /**
   * Check if user is authenticated
   * @returns {boolean} - True if user is authenticated
   */
  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;
    
    return !isTokenExpired(token);
  }

  /**
   * Get current user information
   * @returns {Object|null} - Current user or null
   */
  getCurrentUser() {
    const token = this.getToken();
    if (!token) return null;
    
    return extractUserFromToken(token);
  }


  getCurrentToken() {
    const token = this.getToken();
    if (!token) return null;

    return token;
  }

  /**
   * Get stored authentication token
   * @returns {string|null} - Authentication token or null
   */
  getToken() {
    return localStorage.getItem('authToken');
  }

  /**
   * Get current authentication flow
   * @returns {string|null} - Current flow or null
   */
  getCurrentFlow() {
    return this.currentFlow || localStorage.getItem('authFlow') || null;
  }

  /**
   * Get available authentication flows
   * @returns {Array<string>} - Available flows
   */
  getAvailableFlows() {
    return FeatureFlagUtils.getAvailableFlows();
  }

  /**
   * Check if a specific flow is enabled
   * @param {string} flow - Flow name
   * @returns {boolean} - True if flow is enabled
   */
  isFlowEnabled(flow) {
    return FeatureFlagUtils.isFlowEnabled(flow);
  }

  /**
   * Get debug information about current auth state
   * @returns {Object} - Debug information
   */
  getDebugInfo() {
    const token = this.getToken();
    
    return {
      authService: {
        currentFlow: this.currentFlow,
        availableFlows: this.getAvailableFlows(),
        isAuthenticated: this.isAuthenticated(),
        currentUser: this.getCurrentUser()
      },
      token: token ? getTokenDebugInfo(token) : null,
      featureFlags: FeatureFlagUtils.getDebugInfo(),
      mockService: FEATURE_FLAGS.MOCK_KEYCLOAK_RESPONSES ? 
        mockKeycloakService.getDebugInfo() : null,
      keycloakConfig: this.keycloakConfig
    };
  }

  /**
   * Handle Direct Flow authentication
   * @param {Object} credentials - Username and password
   * @returns {Promise<Object>} - Authentication result
   */
  async _handleDirectLogin(credentials) {
    const { username, password } = credentials;
    
    if (!username || !password) {
      throw new Error('Username and password are required for direct flow');
    }

    return await this.directFlow.authenticate(username, password);
  }

  /**
   * Handle Standard Flow authentication
   * @param {Object} credentials - Optional parameters
   * @returns {Promise<Object>} - Authentication result
   */
  async _handleStandardLogin(credentials = {}) {
    // Check if we're handling a callback
    if (this.isOAuthCallback()) {
      return await this.handleOAuthCallback();
    }
    
    // Otherwise initiate the flow
    return await this.initiateStandardFlow();
  }

  /**
   * Resolve flow name to actual implementation
   * @param {string} flow - Requested flow
   * @returns {string} - Resolved flow name
   */
  _resolveFlow(flow) {
    if (flow === 'auto') {
      return FeatureFlagUtils.getDefaultFlow() === 'both' ? 
        'direct' : FeatureFlagUtils.getDefaultFlow();
    }
    
    return flow;
  }

  /**
   * Get Keycloak configuration from environment
   * @returns {Object} - Keycloak configuration
   */
  _getKeycloakConfig() {
    return {
      url: import.meta.env.VITE_KEYCLOAK_URL || 'https://keycloack.dfcubidesc.com',
      realm: import.meta.env.VITE_KEYCLOAK_REALM || 'habit-tracker',
      clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'habit-tracker-frontend',
      redirectUri: import.meta.env.VITE_KEYCLOAK_REDIRECT_URI || 'http://localhost:3001/auth/callback',
      scopes: import.meta.env.VITE_KEYCLOAK_SCOPES || 'openid profile email'
    };
  }

  /**
   * Detect current authentication flow
   */
  _detectCurrentFlow() {
    // Check if we're handling an OAuth callback
    if (this.isOAuthCallback()) {
      this.currentFlow = 'standard';
      return;
    }

    // Check stored flow
    const storedFlow = localStorage.getItem('authFlow');
    if (storedFlow && FeatureFlagUtils.isFlowEnabled(storedFlow)) {
      this.currentFlow = storedFlow;
      return;
    }

    // Check if we have a valid token to infer flow
    const token = this.getToken();
    if (token) {
      if (isMockToken(token)) {
        if (token.includes('direct')) this.currentFlow = 'direct';
        else if (token.includes('standard')) this.currentFlow = 'standard';
      }
    }

    // Default to configured default flow
    if (!this.currentFlow) {
      this.currentFlow = FeatureFlagUtils.getDefaultFlow();
    }
  }

  /**
   * Clear all stored tokens and auth data
   */
  _clearTokens() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('idToken');
    localStorage.removeItem('authFlow');
    sessionStorage.removeItem('oauth_state');
    sessionStorage.removeItem('authFlow');
    sessionStorage.removeItem('authFlowInitiated');
    cleanOAuthUrl();
  }

  /**
   * Utility: Parse JWT token (for backward compatibility)
   * @param {string} token - JWT token
   * @returns {Object} - Parsed token payload
   */
  parseJwt(token) {
    return extractUserFromToken(token);
  }

  /**
   * Utility: Remove tokens (for backward compatibility)
   */
  removeToken() {
    this._clearTokens();
  }

  /**
   * Exchange authorization code for tokens (for backward compatibility)
   * @param {string} code - Authorization code
   * @returns {Promise<Object>} - Token exchange result
   */
  async exchangeCodeForToken(code) {
    if (!FeatureFlagUtils.isFlowEnabled('standard')) {
      throw new Error('Standard flow is not enabled');
    }

    this.currentFlow = 'standard';
    console.log("handle callback:" + `${window.location.origin}?code=${code}`)
    return await this.standardFlow.handleCallback(`${window.location.origin}?code=${code}`);
  }
}

export default new EnhancedAuthService();
