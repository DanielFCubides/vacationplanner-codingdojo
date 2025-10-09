// authService.js - Simple Keycloak username/password only
class AuthService {
  constructor() {
    // Use proxy in development, direct URL in production
    this.keycloakUrl = 'https://keycloack.dfcubidesc.com';
    this.realm = 'habit-tracker';
    this.clientId = 'habit-tracker-frontend';
    this.keycloackStandarflowUrl = "https://keycloack.dfcubidesc.com/reams/habit-tracker/protocol/openid-connect/auth?client_id=habit-tracker&response_type=code&localhost:=callback&scope='email profile openid'"
  }

  // Login with username/password using Keycloak REST API
  async loginWithCredentials(username, password) {
    try {
      const response = await fetch(`${this.keycloakUrl}/realms/${this.realm}/protocol/openid-connect/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'password',
          client_id: this.clientId,
          username: username,
          password: password,
          scope: 'openid profile email'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error_description || 'Invalid credentials');
      }

      const tokens = await response.json();
      
      // Parse user info from token
      const userInfo = this.parseJwt(tokens.access_token);
      
      // Store token in localStorage
      localStorage.setItem('authToken', tokens.access_token);
      localStorage.setItem('refreshToken', tokens.refresh_token);
      
      return {
        success: true,
        user: {
          id: userInfo.sub,
          email: userInfo.email,
          name: userInfo.name || userInfo.preferred_username,
          username: userInfo.preferred_username
        },
        token: tokens.access_token
      };
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  // Mock OAuth login (returns dummy data for now)
  async loginWithGoogle() {
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Store mock token
    const mockToken = 'mock-google-token-' + Date.now();
    localStorage.setItem('authToken', mockToken);
    
    return {
      success: true,
      user: {
        id: '2',
        email: 'user@gmail.com',
        name: 'Google User'
      },
      token: mockToken
    };
  }

  async loginWithApple() {
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Store mock token
    const mockToken = 'mock-apple-token-' + Date.now();
    localStorage.setItem('authToken', mockToken);
    
    return {
      success: true,
      user: {
        id: '3',
        email: 'user@icloud.com',
        name: 'Apple User'
      },
      token: mockToken
    };
  }

  // Exchange authorization code for access token
  async exchangeCodeForToken(code) {
    try {
      const response = await fetch(`${this.keycloakUrl}/realms/${this.realm}/protocol/openid-connect/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'authorization_code',
          code: code,
          redirect_uri: 'http://localhost:3001/auth/callback',
          client_id: this.clientId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error_description || 'Token exchange failed');
      }

      const tokens = await response.json();
      
      // Parse user info from token
      const userInfo = this.parseJwt(tokens.access_token);
      
      // Store tokens in localStorage
      localStorage.setItem('authToken', tokens.access_token);
      localStorage.setItem('refreshToken', tokens.refresh_token);
      if (tokens.id_token) {
        localStorage.setItem('idToken', tokens.id_token);
      }
      
      return {
        success: true,
        user: {
          id: userInfo.sub,
          email: userInfo.email,
          name: userInfo.name || userInfo.preferred_username,
          username: userInfo.preferred_username,
          token: tokens.access_token,
          refreshToken: tokens.refresh_token,
          idToken: tokens.id_token
        },

      };
    } catch (error) {
      console.error('Authorization code exchange failed:', error);
      throw error;
    }
  }

  // Logout
  async logout() {
    try {
      // Try to logout from Keycloak if we have a real token
      const token = this.getToken();
      if (token && !token.startsWith('mock-')) {
        // Optional: Call Keycloak logout endpoint
        // This is a best effort - don't throw if it fails
        try {
          await fetch(`${this.keycloakUrl}/realms/${this.realm}/protocol/openid-connect/logout`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'Authorization': `Bearer ${token}`
            },
            body: new URLSearchParams({
              client_id: this.clientId,
              refresh_token: localStorage.getItem('refreshToken') || ''
            })
          });
        } catch (logoutError) {
          console.warn('Keycloak logout failed:', logoutError);
        }
      }
      
      // Always clear local storage
      this.removeToken();
      
      return { success: true };
    } catch (error) {
      console.error('Logout failed:', error);
      // Still clear local storage even if logout fails
      this.removeToken();
      throw error;
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;
    
    // For mock tokens, just check if they exist
    if (token.startsWith('mock-')) return true;
    
    // For real tokens, check if expired
    try {
      const payload = this.parseJwt(token);
      const now = Date.now() / 1000;
      return payload.exp > now;
    } catch {
      return false;
    }
  }

  // Get current user from stored token
  getCurrentUser() {
    const token = this.getToken();
    if (!token) return null;
    // Parse real Keycloak token
    try {
      const userInfo = this.parseJwt(token);
      return {
        id: userInfo.sub,
        email: userInfo.email,
        name: userInfo.name || userInfo.preferred_username,
        username: userInfo.preferred_username
      };
    } catch {
      return null;
    }
  }

  // Get stored token
  getToken() {
    return localStorage.getItem('authToken');
  }

  // Remove token
  removeToken() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
  }

  // Utility: Parse JWT token
  parseJwt(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('JWT parsing failed:', error);
      return {};
    }
  }
}

export default new AuthService();