/**
 * Standard Flow (Authorization Code Grant) Implementation
 *
 * This flow initiates the OAuth 2.0 Authorization Code Grant.
 * The browser is redirected to Keycloak, which then redirects to the
 * BACKEND callback URI. The backend exchanges the code for tokens,
 * sets an HTTPOnly session cookie, and redirects back to the frontend.
 *
 * The frontend never sees nor stores any tokens.
 */

import {
  generateAuthorizationUrl,
  generateState,
  storeOAuthState,
  cleanOAuthUrl
} from '../../utils/urlUtils.js';

export class StandardFlow {
  constructor(keycloakConfig, backendBaseUrl) {
    this.keycloakUrl = keycloakConfig.url;
    this.realm = keycloakConfig.realm;
    this.clientId = keycloakConfig.clientId;
    this.redirectUri = keycloakConfig.redirectUri;
    this.scopes = keycloakConfig.scopes || 'openid profile email';
    this.backendBaseUrl = backendBaseUrl || import.meta.env.VITE_AUTH_BACKEND_URL || 'http://localhost:8002';
  }

  /**
   * Initiate the authorization code flow by redirecting to Keycloak.
   * The redirect_uri sent to Keycloak is the BACKEND endpoint that will
   * receive the code from Keycloak, exchange it, set the HTTPOnly cookie,
   * and then redirect the browser back to the frontend.
   * @returns {Promise<Object>} - Flow initiation result
   */
  async initiateFlow() {
    try {
      const state = generateState();
      storeOAuthState(state);

      const authUrl = generateAuthorizationUrl({
        keycloakUrl: this.keycloakUrl,
        realm: this.realm,
        clientId: this.clientId,
        redirectUri: this.redirectUri,
        scopes: this.scopes,
        state: state
      });

      console.log('🔵 StandardFlow: Authorization URL generated', authUrl);

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
   * Handle the frontend callback after the backend has already completed
   * the token exchange and set the HTTPOnly session cookie.
   *
   * At this point there is NO ?code= in the URL — the backend consumed it.
   * We simply call the backend session endpoint to verify the cookie and
   * retrieve the authenticated user's info.
   *
   * @returns {Promise<Object>} - Authentication result with user info
   */
  async handleCallback() {
    try {
      console.log('🔵 StandardFlow.handleCallback: verifying session with backend');

      // Clean any leftover OAuth params from the URL (should be none, but be safe)
      cleanOAuthUrl();

      // Verify the session cookie by calling the backend
      const user = await this._checkSession();

      if (!user) {
        throw new Error('No valid session found after OAuth callback');
      }

      // Clean up session storage state tracking
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

  /**
   * Call the backend session/me endpoint to verify the HTTPOnly cookie
   * and retrieve current user info. The browser automatically sends the
   * cookie because credentials: 'include' is set.
   *
   * @returns {Promise<Object|null>} - User info object or null if not authenticated
   */
  async _checkSession() {
    const url = `${this.backendBaseUrl}/auth/silent_check`;

    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json'
      }
    });

    if (response.status === 401 || response.status === 403) {
      return null;
    }

    if (!response.ok) {
      throw new Error(`Session check failed (${response.status})`);
    }

    const data = await response.json();
    return data.userinfo
  };

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
