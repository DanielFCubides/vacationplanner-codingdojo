import { FEATURE_FLAGS } from './featureFlags.js';

export const getBaseConfig = () => ({
  url: import.meta.env.VITE_KEYCLOAK_URL || 'https://keycloack.dfcubidesc.com',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'habit-tracker',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'auth-service',
  redirectUri: import.meta.env.VITE_KEYCLOAK_REDIRECT_URI || getDefaultRedirectUri(),
  scopes: import.meta.env.VITE_KEYCLOAK_SCOPES || 'openid profile email'
});

const getDefaultRedirectUri = () => {
  return 'http://localhost:8002/auth/login';
};

export const KEYCLOAK_CONFIGS = {
  direct: {
    ...getBaseConfig(),
    grantType: 'password',
    supportsPKCE: false,
    requiresRedirect: false,
    endpoints: {
      token: (config) => `${config.url}/realms/${config.realm}/protocol/openid-connect/token`,
      userInfo: (config) => `${config.url}/realms/${config.realm}/protocol/openid-connect/userinfo`,
      logout: (config) => `${config.url}/realms/${config.realm}/protocol/openid-connect/logout`
    }
  },

  standard: {
    ...getBaseConfig(),
    grantType: 'authorization_code',
    responseType: 'code',
    supportsPKCE: true,
    requiresRedirect: true,
    endpoints: {
      authorize: (config) => `${config.url}/realms/${config.realm}/protocol/openid-connect/auth`,
      token: (config) => `${config.url}/realms/${config.realm}/protocol/openid-connect/token`,
      userInfo: (config) => `${config.url}/realms/${config.realm}/protocol/openid-connect/userinfo`,
      logout: (config) => `${config.url}/realms/${config.realm}/protocol/openid-connect/logout`
    }
  }
};


export const getKeycloakConfig = (flow = 'direct') => {
  const config = KEYCLOAK_CONFIGS[flow];

  if (!config) {
    throw new Error(`Unknown Keycloak flow: ${flow}`);
  }

  return {
    ...config,
    endpoints: Object.fromEntries(
      Object.entries(config.endpoints).map(([key, fn]) => [key, fn(config)])
    )
  };
};

export const getAllKeycloakConfigs = () => {
  return Object.fromEntries(
    Object.keys(KEYCLOAK_CONFIGS).map(flow => [
      flow,
      getKeycloakConfig(flow)
    ])
  );
};

export const validateKeycloakConfig = (flow = 'direct') => {
  const errors = [];
  const warnings = [];

  try {
    const config = getKeycloakConfig(flow);

    if (!config.url) errors.push('Keycloak URL is required');
    if (!config.realm) errors.push('Keycloak realm is required');
    if (!config.clientId) errors.push('Keycloak client ID is required');

    if (flow === 'standard') {
      if (!config.redirectUri) {
        errors.push('Redirect URI is required for standard flow');
      } else if (!config.redirectUri.startsWith('http')) {
        warnings.push('Redirect URI should use HTTPS in production');
      }
    }

    if (config.url && !config.url.startsWith('http')) {
      errors.push('Keycloak URL must start with http:// or https://');
    }

    if (import.meta.env.DEV) {
      if (config.url.includes('localhost') || config.url.includes('127.0.0.1')) {
        warnings.push('Using localhost Keycloak in development mode');
      }

      if (config.redirectUri && config.redirectUri.includes('localhost')) {
        warnings.push('Using localhost redirect URI in development mode');
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      config
    };

  } catch (error) {
    return {
      valid: false,
      errors: [error.message],
      warnings: [],
      config: null
    };
  }
};


if (import.meta.env.DEV && FEATURE_FLAGS.ENABLE_DEBUG_INFO) {
  console.group('🔑 Keycloak Configuration');

  Object.keys(KEYCLOAK_CONFIGS).forEach(flow => {
    const validation = validateKeycloakConfig(flow);
    const config = validation.config;

    console.group(`${flow.toUpperCase()} Flow`);
    console.log('Valid:', validation.valid);
    console.log('URL:', config?.url);
    console.log('Realm:', config?.realm);
    console.log('Client ID:', config?.clientId);

    if (config?.redirectUri) {
      console.log('Redirect URI:', config.redirectUri);
    }

    if (validation.warnings.length > 0) {
      console.warn('Warnings:', validation.warnings);
    }

    if (validation.errors.length > 0) {
      console.error('Errors:', validation.errors);
    }

    console.groupEnd();
  });

  console.groupEnd();
}

export const KEYCLOAK_CONFIG = getBaseConfig();
export const DEMO_CONFIG = {
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
  mockDelays: {
    login: parseInt(import.meta.env.VITE_MOCK_LOGIN_DELAY || '1000'),
    tokenExchange: parseInt(import.meta.env.VITE_MOCK_TOKEN_DELAY || '800'),
    logout: parseInt(import.meta.env.VITE_MOCK_LOGOUT_DELAY || '500')
  }
};

export default {
  getKeycloakConfig,
  getAllKeycloakConfigs,
  validateKeycloakConfig,
  KEYCLOAK_CONFIGS
};
