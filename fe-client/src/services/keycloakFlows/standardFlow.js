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
  validateOAuthState,
  parseCallbackUrl,
  cleanOAuthUrl
} from '../../utils/urlUtils.js';

export class StandardFlow {
  constructor(keycloakConfig) {
    this.keycloakUrl = keycloakConfig.url;
    this.realm = keycloakConfig.realm;
    this.clientId = keycloakConfig.clientId;
    this.redirectUri = keycloakConfig.redirectUri;
    this.scopes = keycloakConfig.scopes || 'openid profile email';
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

      console.log("auth url generated" + authUrl);

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
  async handleCallback(callbackUrl = window.location.href) {
    try {
      console.log('🔵 StandardFlow.handleCallback called with URL:', callbackUrl);
      
      // Parse callback parameters
      const { code, state, error, errorDescription } = parseCallbackUrl(callbackUrl);

      console.log('🔵 Parsed callback params:', { 
        hasCode: !!code, 
        hasState: !!state, 
        hasError: !!error 
      });

      // Handle OAuth errors
      if (error) {
        throw new Error(errorDescription || error);
      }

      // Check if we have an authorization code
      if (!code) {
        throw new Error('No authorization code received');
      }

      // Validate state parameter
      console.log('🔵 Validating state parameter...');
      const isValidState = validateOAuthState(state);
      console.log('🔵 State validation result:', isValidState);
      
      if (!isValidState) {
        throw new Error('Invalid state parameter - possible CSRF attack');
      }

      // Exchange authorization code for tokens
      const tokenResult = await this._exchangeCodeForTokens(code);
      
      // Clean URL from OAuth parameters
      cleanOAuthUrl();

      return tokenResult;

    } catch (error) {
      console.error('Standard flow callback handling failed:', error);
      
      // Clean URL even on error
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
   * Exchange authorization code for access tokens
   * @param {string} code - Authorization code from callback
   * @returns {Promise<Object>} - Token exchange result
   */
  async _exchangeCodeForTokens(code) {
    const tokenUrl = `${this.keycloakUrl}/realms/${this.realm}/protocol/openid-connect/token`;

    const requestBody = new URLSearchParams({
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: this.redirectUri,
      client_id: this.clientId
    });

    const response = await fetch(tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: requestBody
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error_description || 
        errorData.error || 
        `Token exchange failed (${response.status})`
      );
    }

    const tokens = await response.json();

    // Extract user information
    const user = extractUserFromToken(tokens.access_token);
    if (!user) {
      throw new Error('Failed to extract user information from token');
    }

    // Store tokens
    this._storeTokens(tokens);

    return {
      success: true,
      flow: 'standard',
      user: {
        ...user,
        flow: 'standard'
      },
      tokens: {
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        idToken: tokens.id_token,
        tokenType: tokens.token_type || 'Bearer',
        expiresIn: tokens.expires_in
      }
    };
  }

  /**
   * Store authentication tokens
   * @param {Object} tokens - Token response from Keycloak
   */
  _storeTokens(tokens) {
    localStorage.setItem('authToken', tokens.access_token);
    
    if (tokens.refresh_token) {
      localStorage.setItem('refreshToken', tokens.refresh_token);
    }
    
    if (tokens.id_token) {
      localStorage.setItem('idToken', tokens.id_token);
    }

    // Store flow type for debugging
    localStorage.setItem('authFlow', 'standard');
    
    // Clean up session storage
    sessionStorage.removeItem('authFlowInitiated');
  }

  /**
   * Check if we're currently handling a callback
   * @returns {boolean} - True if this appears to be a callback
   */
  isCallback(url = window.location.href) {
    const { isCallback } = parseCallbackUrl(url);
    return isCallback;
  }

  /**
   * Categorize error for better handling
   * @param {string} errorMessage - Error message
   * @returns {string} - Error category
   */
  _categorizeError(errorMessage) {
    const message = errorMessage.toLowerCase();
    
    if (message.includes('state') || message.includes('csrf')) {
      return 'security_error';
    }
    
    if (message.includes('code')) {
      return 'authorization_failed';
    }
    
    if (message.includes('access_denied')) {
      return 'access_denied';
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
