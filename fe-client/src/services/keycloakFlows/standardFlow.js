/**
 * Standard Flow (Authorization Code Grant) Implementation
 * 
 * This flow implements the OAuth 2.0 Authorization Code Grant with PKCE.
 * Users are redirected to Keycloak for authentication, then redirected back
 * with an authorization code that is exchanged for tokens.
 */

import { extractUserFromToken } from '../../utils/tokenUtils.js';
import {
  generateAuthorizationUrl,
  generateState,
  storeOAuthState,
  cleanOAuthUrl
} from '../../utils/urlUtils.js';
import { BACKEND_URL } from '../../config/constants.js';

export class StandardFlow {
  constructor(keycloakConfig, backendBaseUrl) {
    this.keycloakUrl = keycloakConfig.url;
    this.realm = keycloakConfig.realm;
    this.clientId = keycloakConfig.clientId;
    this.redirectUri = keycloakConfig.redirectUri;
    this.scopes = keycloakConfig.scopes || 'openid profile email';
    this.backendBaseUrl = backendBaseUrl || BACKEND_URL;
  }

  /**
   * Initiate the authorization code flow by redirecting to Keycloak
   * @returns {Promise<Object>} - Flow initiation result
   */
  async initiateFlow() {
    try {

      // Generate state for security
      const state = generateState();
      storeOAuthState(state);

      // Generate authorization URL
      const authUrl = generateAuthorizationUrl({
        keycloakUrl: this.keycloakUrl,
        realm: this.realm,
        clientId: this.clientId,
        redirectUri: this.redirectUri,
        scopes: this.scopes,
        state: state
      });

      console.log('🔵 StandardFlow: Authorization URL generated', authUrl);

      // Store flow initiation info
      sessionStorage.setItem('authFlow', 'standard');
      sessionStorage.setItem('authFlowInitiated', Date.now().toString());

      return {
        success: true,
        flow: 'standard',
        action: 'redirect',
        url: authUrl,
        state: state
      };

    } catch (error) {
      console.error('Standard flow initiation failed:', error);

      return {
        success: false,
        flow: 'standard',
        error: error.message,
        errorType: 'initiation_failed'
      };
    }
  }

  /**
   * Handle the authorization callback and exchange code for tokens
   * @param {string} callbackUrl - The callback URL with authorization code
   * @returns {Promise<Object>} - Authentication result
   */
  async handleCallback() {
    try {
      console.log('🔵 StandardFlow.handleCallback: verifying session with backend');
      cleanOAuthUrl();

      const user = await this._checkSession();
      if (!user) {
        throw new Error('No valid session found after OAuth callback');
      }

      sessionStorage.removeItem('authFlow');
      sessionStorage.removeItem('authFlowInitiated');

      return {
        success: true,
        flow: 'standard',
        user: {
          ...user,
          flow: 'standard'
        }
      };

    } catch (error) {
      console.error('Standard flow callback handling failed:', error);
      cleanOAuthUrl();

      return {
        success: false,
        flow: 'standard',
        error: error.message,
        errorType: this._categorizeError(error.message)
      };
    }
  }

  async _checkSession() {
    const url = `${this.backendBaseUrl}/auth/silent_check`;
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json'
      }
    });
    if (response.status >= 401 && response.status < 500) {
      return null;
    }
    if (!response.ok) {
      throw new Error(`Session check failed (${response.status})`);
    }
    const data = await response.json();
    return data.userinfo;
  }

  /**
   * Categorize error for better handling
   * @param {string} errorMessage - Error message
   * @returns {string} - Error category
   */
  _categorizeError(errorMessage) {
    const message = errorMessage.toLowerCase();

    if (message.includes('session') || message.includes('cookie')) {
      return 'session_error';
    }

    if (message.includes('401') || message.includes('403')) {
      return 'unauthorized';
    }

    if (message.includes('network') || message.includes('fetch')) {
      return 'network_error';
    }

    if (message.includes('timeout')) {
      return 'timeout';
    }

    return 'unknown_error';
  }
}
