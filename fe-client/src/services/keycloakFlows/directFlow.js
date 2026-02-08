/**
 * Direct Flow (Resource Owner Password Credentials Grant) Implementation
 * 
 * This flow allows users to authenticate directly with username/password
 * against Keycloak without redirects. Uses the OAuth 2.0 Resource Owner 
 * Password Credentials Grant type.
 */

import { extractUserFromToken } from '../../utils/tokenUtils.js';

export class DirectFlow {
  constructor(keycloakConfig) {
    this.keycloakUrl = keycloakConfig.url;
    this.realm = keycloakConfig.realm;
    this.clientId = keycloakConfig.clientId;
    this.scopes = keycloakConfig.scopes || 'openid profile email';
  }

  /**
   * Authenticate user with username and password
   * @param {string} username - User's username or email
   * @param {string} password - User's password
   * @returns {Promise<Object>} - Authentication result
   */
  async authenticate(username, password) {
    try {
      console.log("initialize direct Flow")
      // Build token endpoint URL
      const tokenUrl = `${this.keycloakUrl}/realms/${this.realm}/protocol/openid-connect/token`;

      // Prepare request body
      const requestBody = new URLSearchParams({
        grant_type: 'password',
        client_id: this.clientId,
        username: username,
        password: password,
        scope: this.scopes
      });

      // Make token request
      const response = await fetch(tokenUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: requestBody
      });

      // Handle response
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error_description || 
          errorData.error || 
          `Authentication failed (${response.status})`
        );
      }

      const tokens = await response.json();

      // Extract user information from token
      const user = extractUserFromToken(tokens.access_token);
      if (!user) {
        throw new Error('Failed to extract user information from token');
      }

      // Store tokens
      this._storeTokens(tokens);

      return {
        success: true,
        flow: 'direct',
        user: {
          ...user,
          flow: 'direct'
        },
        tokens: {
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          idToken: tokens.id_token,
          tokenType: tokens.token_type || 'Bearer',
          expiresIn: tokens.expires_in
        }
      };

    } catch (error) {
      console.error('Direct flow authentication failed:', error);
      
      return {
        success: false,
        flow: 'direct',
        error: error.message,
        errorType: this._categorizeError(error.message)
      };
    }
  }

  /**
   * Store authentication tokens
   * @param {Object} tokens - Token response from Keycloak
   */
  _storeTokens(tokens) {
    // IMPORTANT: Use 'authToken' key to match authService.getToken()
    localStorage.setItem('authToken', tokens.access_token);

    if (tokens.refresh_token) {
      localStorage.setItem('refreshToken', tokens.refresh_token);
    }

    if (tokens.id_token) {
      localStorage.setItem('idToken', tokens.id_token);
    }

    // Store flow type for debugging
    localStorage.setItem('authFlow', 'direct');
  }

  /**
   * Categorize error for better handling
   * @param {string} errorMessage - Error message
   * @returns {string} - Error category
   */
  _categorizeError(errorMessage) {
    const message = errorMessage.toLowerCase();
    
    if (message.includes('invalid') || message.includes('credentials')) {
      return 'invalid_credentials';
    }
    
    if (message.includes('unauthorized')) {
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
