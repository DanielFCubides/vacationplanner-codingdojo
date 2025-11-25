/**
 * JWT Token Utilities
 * 
 * Utility functions for handling JWT tokens from Keycloak
 */

/**
 * Parse JWT token and extract payload
 * @param {string} token - JWT token string
 * @returns {Object|null} - Parsed token payload or null if invalid
 */
export const parseJwt = (token) => {
  try {
    if (!token || typeof token !== 'string') {
      return null;
    }

    const base64Url = token.split('.')[1];
    if (!base64Url) {
      return null;
    }

    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );
    
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('JWT parsing failed:', error);
    return null;
  }
};

/**
 * Check if token is expired
 * @param {string} token - JWT token string
 * @returns {boolean} - True if token is expired
 */
export const isTokenExpired = (token) => {
  if (!token || token.startsWith('mock-')) {
    return false; // Mock tokens never expire
  }

  try {
    const payload = parseJwt(token);
    if (!payload || !payload.exp) {
      return true;
    }

    const now = Math.floor(Date.now() / 1000);
    return payload.exp < now;
  } catch {
    return true;
  }
};

/**
 * Extract user information from JWT token
 * @param {string} token - JWT token string
 * @returns {Object|null} - User information object or null
 */
export const extractUserFromToken = (token) => {
  if (!token) return null;

  // Handle mock tokens
  if (token.startsWith('mock-')) {
    return extractUserFromMockToken(token);
  }

  // Parse real Keycloak token
  const payload = parseJwt(token);
  if (!payload) return null;

  return {
    id: payload.sub,
    email: payload.email,
    name: payload.name || payload.preferred_username,
    username: payload.preferred_username,
    roles: payload.realm_access?.roles || [],
    groups: payload.groups || []
  };
};

/**
 * Extract user information from mock tokens
 * @param {string} token - Mock token string
 * @returns {Object} - Mock user information
 */
export const extractUserFromMockToken = (token) => {
  if (token.startsWith('mock-direct-')) {
    return {
      id: '1',
      email: 'direct@example.com',
      name: 'Direct Flow User',
      username: 'direct-user',
      roles: ['user'],
      groups: [],
      flow: 'direct'
    };
  }

  if (token.startsWith('mock-standard-')) {
    return {
      id: '2',
      email: 'standard@example.com',
      name: 'Standard Flow User',
      username: 'standard-user',
      roles: ['user'],
      groups: [],
      flow: 'standard'
    };
  }

  if (token.startsWith('mock-google-')) {
    return {
      id: '3',
      email: 'user@gmail.com',
      name: 'Google OAuth User',
      username: 'google-user',
      roles: ['user'],
      groups: [],
      flow: 'google'
    };
  }

  if (token.startsWith('mock-apple-')) {
    return {
      id: '4',
      email: 'user@icloud.com',
      name: 'Apple OAuth User',
      username: 'apple-user',
      roles: ['user'],
      groups: [],
      flow: 'apple'
    };
  }

  return {
    id: '0',
    email: 'unknown@example.com',
    name: 'Unknown User',
    username: 'unknown-user',
    roles: [],
    groups: [],
    flow: 'unknown'
  };
};

/**
 * Check if token is a mock token
 * @param {string} token - Token string
 * @returns {boolean} - True if token is a mock token
 */
export const isMockToken = (token) => {
  return token && typeof token === 'string' && token.startsWith('mock-');
};

/**
 * Get token expiration time as Date object
 * @param {string} token - JWT token string
 * @returns {Date|null} - Expiration date or null
 */
export const getTokenExpiration = (token) => {
  if (!token || isMockToken(token)) {
    return null; // Mock tokens don't have expiration
  }

  const payload = parseJwt(token);
  if (!payload || !payload.exp) {
    return null;
  }

  return new Date(payload.exp * 1000);
};

/**
 * Get token information for debugging
 * @param {string} token - JWT token string
 * @returns {Object} - Token debug information
 */
export const getTokenDebugInfo = (token) => {
  if (!token) {
    return { valid: false, error: 'No token provided' };
  }

  const isMock = isMockToken(token);
  const payload = isMock ? null : parseJwt(token);
  const expiration = getTokenExpiration(token);
  const expired = isTokenExpired(token);
  const user = extractUserFromToken(token);

  return {
    valid: !expired,
    isMock,
    expired,
    expiration,
    user,
    payload: isMock ? { type: 'mock' } : payload,
    issued: payload?.iat ? new Date(payload.iat * 1000) : null,
    issuer: payload?.iss || null
  };
};
