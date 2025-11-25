/**
 * Environment Configuration
 * 
 * Centralized configuration for different environments and Keycloak settings.
 * Reads from environment variables and provides sensible defaults.
 */

/**
 * Keycloak configuration based on environment
 */
export const KEYCLOAK_CONFIG = {
  // Base Keycloak settings
  url: import.meta.env.VITE_KEYCLOAK_URL || 'https://keycloack.dfcubidesc.com',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'habit-tracker',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'habit-tracker-frontend',
  
  // OAuth settings
  redirectUri: import.meta.env.VITE_KEYCLOAK_REDIRECT_URI || 'http://localhost:3001/auth/callback',
  scopes: import.meta.env.VITE_KEYCLOAK_SCOPES || 'openid profile email',
  
  // Flow-specific settings
  standardFlowEnabled: import.meta.env.VITE_KEYCLOAK_STANDARD_FLOW_ENABLED === 'true',
  directFlowEnabled: import.meta.env.VITE_KEYCLOAK_DIRECT_FLOW_ENABLED !== 'false', // Default true
};

/**
 * Application configuration
 */
export const APP_CONFIG = {
  // App settings
  name: import.meta.env.VITE_APP_NAME || 'Habit Tracker',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  environment: import.meta.env.MODE || 'development',
  
  // API settings
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
  apiTimeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
  
  // Debug settings
  enableLogging: import.meta.env.VITE_ENABLE_LOGGING !== 'false', // Default true in dev
  logLevel: import.meta.env.VITE_LOG_LEVEL || 'info',
};

/**
 * Demo configuration
 */
export const DEMO_CONFIG = {
  // Demo users for testing
  demoUsers: {
    direct: {
      username: import.meta.env.VITE_DEMO_DIRECT_USERNAME || 'demo-direct',
      password: import.meta.env.VITE_DEMO_DIRECT_PASSWORD || 'demo123',
      email: 'direct-user@demo.com',
      name: 'Direct Flow Demo User'
    },
    standard: {
      username: import.meta.env.VITE_DEMO_STANDARD_USERNAME || 'demo-oauth',
      password: import.meta.env.VITE_DEMO_STANDARD_PASSWORD || 'demo123',
      email: 'oauth-user@demo.com',
      name: 'Standard Flow Demo User'
    }
  },
  
  // Mock response delays (ms)
  mockDelays: {
    login: parseInt(import.meta.env.VITE_MOCK_LOGIN_DELAY || '1000'),
    tokenExchange: parseInt(import.meta.env.VITE_MOCK_TOKEN_DELAY || '800'),
    logout: parseInt(import.meta.env.VITE_MOCK_LOGOUT_DELAY || '500')
  }
};

/**
 * URL builders for Keycloak endpoints
 */
export const buildKeycloakUrls = (config = KEYCLOAK_CONFIG) => ({
  // Token endpoints
  tokenEndpoint: `${config.url}/realms/${config.realm}/protocol/openid-connect/token`,
  userInfoEndpoint: `${config.url}/realms/${config.realm}/protocol/openid-connect/userinfo`,
  logoutEndpoint: `${config.url}/realms/${config.realm}/protocol/openid-connect/logout`,
  
  // Authorization endpoint for standard flow
  authorizationUrl: `${config.url}/realms/${config.realm}/protocol/openid-connect/auth`,
  
  // Admin endpoints (if needed)
  adminUrl: `${config.url}/admin/realms/${config.realm}`,
  
  // Build authorization URL with parameters
  buildAuthUrl: (state = null) => {
    const params = new URLSearchParams({
      client_id: config.clientId,
      response_type: 'code',
      redirect_uri: config.redirectUri,
      scope: config.scopes,
    });
    
    if (state) {
      params.append('state', state);
    }
    
    return `${buildKeycloakUrls().authorizationUrl}?${params.toString()}`;
  }
});

/**
 * Environment detection utilities
 */
export const Environment = {
  isDevelopment: () => import.meta.env.MODE === 'development',
  isProduction: () => import.meta.env.MODE === 'production',
  isStaging: () => import.meta.env.MODE === 'staging',
  
  // Get current environment info
  getInfo: () => ({
    mode: import.meta.env.MODE,
    dev: import.meta.env.DEV,
    prod: import.meta.env.PROD,
    baseUrl: import.meta.env.BASE_URL,
    command: import.meta.env.COMMAND
  })
};

/**
 * Configuration validation
 */
export const validateConfiguration = () => {
  const errors = [];
  const warnings = [];
  
  // Check required Keycloak settings
  if (!KEYCLOAK_CONFIG.url) {
    errors.push('KEYCLOAK_URL is required');
  }
  
  if (!KEYCLOAK_CONFIG.realm) {
    errors.push('KEYCLOAK_REALM is required');
  }
  
  if (!KEYCLOAK_CONFIG.clientId) {
    errors.push('KEYCLOAK_CLIENT_ID is required');
  }
  
  // Check redirect URI format
  try {
    new URL(KEYCLOAK_CONFIG.redirectUri);
  } catch {
    errors.push('KEYCLOAK_REDIRECT_URI must be a valid URL');
  }
  
  // Warnings for development
  if (Environment.isDevelopment()) {
    if (KEYCLOAK_CONFIG.redirectUri.includes('localhost')) {
      warnings.push('Using localhost redirect URI - ensure Keycloak is configured accordingly');
    }
  }
  
  return { errors, warnings, isValid: errors.length === 0 };
};

/**
 * Log configuration in development
 */
if (Environment.isDevelopment() && APP_CONFIG.enableLogging) {
  const validation = validateConfiguration();
  
  console.group('⚙️  Environment Configuration');
  console.log('Environment:', Environment.getInfo());
  console.log('Keycloak Config:', KEYCLOAK_CONFIG);
  console.log('App Config:', APP_CONFIG);
  console.log('Demo Config:', DEMO_CONFIG);
  
  if (validation.warnings.length > 0) {
    console.warn('Warnings:', validation.warnings);
  }
  
  if (validation.errors.length > 0) {
    console.error('Errors:', validation.errors);
  }
  
  console.groupEnd();
}

export { KEYCLOAK_CONFIG as default };
