/**
 * URL Utilities for Keycloak OAuth Flows
 * 
 * Utility functions for handling URL generation and parsing for OAuth flows
 */

/**
 * Generate Keycloak authorization URL for Standard Flow
 * @param {Object} config - Keycloak configuration
 * @returns {string} - Authorization URL
 */
export const generateAuthorizationUrl = (config) => {
  const {
    keycloakUrl,
    realm,
    clientId,
    redirectUri,
    scopes = 'openid profile email',
    state = null
  } = config;

  const baseUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/auth`;
  
  const params = new URLSearchParams({
    client_id: clientId,
    response_type: 'code',
    redirect_uri: redirectUri,
    scope: scopes
  });

  if (state) {
    params.append('state', state);
  }

  return `${baseUrl}?${params.toString()}`;
};

/**
 * Parse authorization code from callback URL
 * @param {string} url - Callback URL with authorization code
 * @returns {Object} - Parsed parameters (code, state, error)
 */
export const parseCallbackUrl = (url = window.location.href) => {
  try {
    const urlObj = new URL(url);
    const params = urlObj.searchParams;
    
    return {
      code: params.get('code'),
      state: params.get('state'),
      error: params.get('error'),
      errorDescription: params.get('error_description'),
      isCallback: params.has('code') || params.has('error')
    };
  } catch (error) {
    console.error('Failed to parse callback URL:', error);
    return {
      code: null,
      state: null,
      error: null,
      errorDescription: null,
      isCallback: false
    };
  }
};

/**
 * Generate state parameter for OAuth security
 * @returns {string} - Random state string
 */
export const generateState = () => {
  return btoa(Math.random().toString()).substr(10, 20);
};

/**
 * Store OAuth state in sessionStorage
 * @param {string} state - State parameter to store
 */
export const storeOAuthState = (state) => {
  sessionStorage.setItem('oauth_state', state);
};

/**
 * Retrieve and validate OAuth state
 * @param {string} receivedState - State received in callback
 * @returns {boolean} - True if state is valid
 */
export const validateOAuthState = (receivedState) => {
  const storedState = sessionStorage.getItem('oauth_state');
  
  console.log('🔍 State validation:', {
    stored: storedState,
    received: receivedState,
    match: storedState === receivedState
  });
  
  // Only remove if validation is successful
  if (storedState === receivedState) {
    sessionStorage.removeItem('oauth_state');
    return true;
  }
  
  return false;
};

/**
 * Clean current URL from OAuth parameters
 * Useful after processing the callback to clean the browser URL
 */
export const cleanOAuthUrl = () => {
  if (typeof window === 'undefined') return;
  
  const url = new URL(window.location);
  const params = url.searchParams;
  
  // Remove OAuth-specific parameters
  params.delete('code');
  params.delete('state');
  params.delete('error');
  params.delete('error_description');
  
  // Update URL without refresh if parameters were removed
  const newUrl = url.toString();
  if (newUrl !== window.location.href) {
    window.history.replaceState({}, document.title, newUrl);
  }
};

/**
 * Check if current URL is an OAuth callback
 * @returns {boolean} - True if current URL contains OAuth callback parameters
 */
export const isOAuthCallback = () => {
  const { isCallback } = parseCallbackUrl();
  return isCallback;
};

/**
 * Generate logout URL for Keycloak
 * @param {Object} config - Keycloak configuration
 * @param {string} redirectUri - Post-logout redirect URI (optional)
 * @returns {string} - Logout URL
 */
export const generateLogoutUrl = (config, redirectUri = null) => {
  const { keycloakUrl, realm } = config;
  const baseUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/logout`;
  
  if (!redirectUri) {
    return baseUrl;
  }
  
  const params = new URLSearchParams({
    post_logout_redirect_uri: redirectUri
  });
  
  return `${baseUrl}?${params.toString()}`;
};

/**
 * Get current page URL without OAuth parameters (for redirects)
 * @returns {string} - Clean current URL
 */
export const getCleanCurrentUrl = () => {
  if (typeof window === 'undefined') {
    return 'http://localhost:3001';
  }
  
  const url = new URL(window.location);
  const params = url.searchParams;
  
  // Remove OAuth parameters
  params.delete('code');
  params.delete('state');
  params.delete('error');
  params.delete('error_description');
  
  return url.toString();
};
