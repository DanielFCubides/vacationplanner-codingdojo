/**
 * Mock Keycloak Service
 * 
 * Provides mock implementations of Keycloak flows for demo purposes.
 * Simulates realistic response times and different user scenarios.
 */

import { FEATURE_FLAGS } from '../config/featureFlags.js';

export class MockKeycloakService {
  constructor() {
    this.mockUsers = this._generateMockUsers();
    this.mockDelay = {
      login: parseInt(import.meta.env.VITE_MOCK_LOGIN_DELAY) || 1000,
      token: parseInt(import.meta.env.VITE_MOCK_TOKEN_DELAY) || 800,
      logout: parseInt(import.meta.env.VITE_MOCK_LOGOUT_DELAY) || 500
    };
  }

  /**
   * Mock direct flow authentication
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Promise<Object>} - Mock authentication result
   */
  async mockDirectFlow(username, password) {
    await this._simulateDelay(this.mockDelay.login);

    // Check for demo credentials
    const user = this._findUser(username, password);
    
    if (!user) {
      return {
        success: false,
        error: 'Invalid username or password',
        errorType: 'invalid_credentials'
      };
    }

    const tokens = this._generateMockTokens('direct', user.id);

    return {
      success: true,
      flow: 'direct',
      user: {
        ...user,
        flow: 'direct'
      },
      tokens
    };
  }

  /**
   * Mock standard flow authentication
   * @param {string} authCode - Mock authorization code
   * @returns {Promise<Object>} - Mock authentication result
   */
  async mockStandardFlow(authCode = null) {
    await this._simulateDelay(this.mockDelay.token);

    // Simulate different scenarios based on auth code
    if (authCode === 'fail') {
      return {
        success: false,
        error: 'Invalid authorization code',
        errorType: 'authorization_failed'
      };
    }

    const user = this.mockUsers.standard;
    const tokens = this._generateMockTokens('standard', user.id);

    return {
      success: true,
      flow: 'standard',
      user: {
        ...user,
        flow: 'standard'
      },
      tokens
    };
  }

  /**
   * Mock OAuth provider flows (Google, Apple, etc.)
   * @param {string} provider - OAuth provider name
   * @returns {Promise<Object>} - Mock authentication result
   */
  async mockOAuthProvider(provider) {
    await this._simulateDelay(this.mockDelay.login);

    const user = this.mockUsers[provider.toLowerCase()];
    
    if (!user) {
      return {
        success: false,
        error: `${provider} authentication not configured`,
        errorType: 'provider_not_supported'
      };
    }

    const tokens = this._generateMockTokens(provider.toLowerCase(), user.id);

    return {
      success: true,
      flow: provider.toLowerCase(),
      user: {
        ...user,
        flow: provider.toLowerCase()
      },
      tokens
    };
  }

  /**
   * Mock logout
   * @returns {Promise<Object>} - Mock logout result
   */
  async mockLogout() {
    await this._simulateDelay(this.mockDelay.logout);

    return {
      success: true,
      message: 'Successfully logged out'
    };
  }

  /**
   * Mock token refresh
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} - Mock token refresh result
   */
  async mockRefreshToken(refreshToken) {
    await this._simulateDelay(this.mockDelay.token / 2);

    if (!refreshToken || !refreshToken.startsWith('mock-refresh-')) {
      return {
        success: false,
        error: 'Invalid refresh token',
        errorType: 'invalid_token'
      };
    }

    // Extract user ID from refresh token (simplified)
    const userId = refreshToken.includes('direct') ? '1' : '2';
    const flow = refreshToken.includes('direct') ? 'direct' : 'standard';
    
    const tokens = this._generateMockTokens(flow, userId);

    return {
      success: true,
      tokens
    };
  }

  /**
   * Generate mock users for different scenarios
   * @returns {Object} - Mock user database
   */
  _generateMockUsers() {
    const demoDirectUser = import.meta.env.VITE_DEMO_DIRECT_USERNAME || 'demo-direct';
    const demoStandardUser = import.meta.env.VITE_DEMO_STANDARD_USERNAME || 'demo-oauth';
    
    return {
      // Direct flow demo user
      [demoDirectUser]: {
        id: '1',
        username: demoDirectUser,
        email: `${demoDirectUser}@example.com`,
        name: 'Direct Flow Demo User',
        roles: ['user', 'demo'],
        groups: ['demo-users'],
        password: import.meta.env.VITE_DEMO_DIRECT_PASSWORD || 'demo123'
      },

      // Standard flow user
      standard: {
        id: '2',
        username: demoStandardUser,
        email: `${demoStandardUser}@example.com`,
        name: 'Standard Flow Demo User',
        roles: ['user', 'demo'],
        groups: ['demo-users']
      },

      // OAuth provider users
      google: {
        id: '3',
        username: 'google-user',
        email: 'user@gmail.com',
        name: 'Google OAuth User',
        roles: ['user'],
        groups: ['oauth-users']
      },

      apple: {
        id: '4',
        username: 'apple-user',
        email: 'user@icloud.com',
        name: 'Apple OAuth User',
        roles: ['user'],
        groups: ['oauth-users']
      }
    };
  }

  /**
   * Find user by credentials
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Object|null} - User object or null
   */
  _findUser(username, password) {
    // Check direct demo user
    const demoDirectUser = import.meta.env.VITE_DEMO_DIRECT_USERNAME || 'demo-direct';
    const demoDirectPassword = import.meta.env.VITE_DEMO_DIRECT_PASSWORD || 'demo123';
    
    if (username === demoDirectUser && password === demoDirectPassword) {
      return this.mockUsers[demoDirectUser];
    }

    // Check for generic demo credentials
    if (username === 'demo' && password === 'demo') {
      return {
        id: '5',
        username: 'demo',
        email: 'demo@example.com',
        name: 'Generic Demo User',
        roles: ['user'],
        groups: []
      };
    }

    // Allow any username with password "test" for testing
    if (password === 'test') {
      return {
        id: Math.random().toString(36).substr(2, 9),
        username: username,
        email: username.includes('@') ? username : `${username}@example.com`,
        name: `Test User (${username})`,
        roles: ['user', 'test'],
        groups: ['test-users']
      };
    }

    return null;
  }

  /**
   * Generate mock JWT-like tokens
   * @param {string} flow - Authentication flow used
   * @param {string} userId - User ID
   * @returns {Object} - Mock tokens
   */
  _generateMockTokens(flow, userId) {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);

    return {
      accessToken: `mock-${flow}-${timestamp}-${random}`,
      refreshToken: `mock-refresh-${flow}-${timestamp}`,
      idToken: `mock-id-${flow}-${timestamp}`,
      tokenType: 'Bearer',
      expiresIn: 3600,
      scope: 'openid profile email'
    };
  }

  /**
   * Simulate network delay
   * @param {number} ms - Delay in milliseconds
   * @returns {Promise} - Resolves after delay
   */
  async _simulateDelay(ms) {
    // Allow instant responses in test mode
    if (import.meta.env.VITE_INSTANT_MOCK_RESPONSES === 'true') {
      return;
    }

    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get mock user info (for debugging)
   * @returns {Object} - Mock users and configuration
   */
  getDebugInfo() {
    return {
      mockUsers: Object.keys(this.mockUsers),
      delays: this.mockDelay,
      demoCredentials: {
        direct: {
          username: import.meta.env.VITE_DEMO_DIRECT_USERNAME || 'demo-direct',
          password: import.meta.env.VITE_DEMO_DIRECT_PASSWORD || 'demo123'
        },
        generic: {
          username: 'demo',
          password: 'demo'
        },
        test: {
          username: 'any-username',
          password: 'test'
        }
      }
    };
  }
}

export default new MockKeycloakService();
