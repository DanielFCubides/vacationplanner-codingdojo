/**
 * Feature Flags Configuration
 * 
 * Simple feature flag system for controlling Keycloak login experiences.
 * Uses environment variables for easy configuration switching.
 */

// Default feature flags - can be overridden by environment variables
const DEFAULT_FLAGS = {
  // Login flow options
  ENABLE_DIRECT_FLOW: true,
  ENABLE_STANDARD_FLOW: true,
  DEFAULT_LOGIN_FLOW: 'both', // 'direct' | 'standard' | 'both'
  
  // Demo and testing modes
  DEMO_MODE: false,
  MOCK_KEYCLOAK_RESPONSES: false,
  
  // UI Features
  SHOW_FLOW_SELECTOR: true,
  ENABLE_DEBUG_INFO: false,
  SHOW_TOKEN_INFO: false,
  
  // Development helpers
  AUTO_LOGIN: false,
  SKIP_VALIDATION: false
};

/**
 * Get feature flag value from environment or default
 */
const getEnvFlag = (key, defaultValue) => {
  const envKey = `VITE_${key}`;
  const envValue = import.meta.env[envKey];
  
  if (envValue === undefined) return defaultValue;
  
  // Handle boolean conversion
  if (typeof defaultValue === 'boolean') {
    return envValue === 'true';
  }
  
  // Handle string values
  return envValue;
};

/**
 * Feature flags with environment variable overrides
 */
export const FEATURE_FLAGS = {
  // Login flows
  ENABLE_DIRECT_FLOW: getEnvFlag('ENABLE_DIRECT_FLOW', DEFAULT_FLAGS.ENABLE_DIRECT_FLOW),
  ENABLE_STANDARD_FLOW: getEnvFlag('ENABLE_STANDARD_FLOW', DEFAULT_FLAGS.ENABLE_STANDARD_FLOW),
  DEFAULT_LOGIN_FLOW: getEnvFlag('DEFAULT_LOGIN_FLOW', DEFAULT_FLAGS.DEFAULT_LOGIN_FLOW),
  
  // Demo modes
  DEMO_MODE: getEnvFlag('DEMO_MODE', DEFAULT_FLAGS.DEMO_MODE),
  MOCK_KEYCLOAK_RESPONSES: getEnvFlag('MOCK_KEYCLOAK_RESPONSES', DEFAULT_FLAGS.MOCK_KEYCLOAK_RESPONSES),
  
  // UI features
  SHOW_FLOW_SELECTOR: getEnvFlag('SHOW_FLOW_SELECTOR', DEFAULT_FLAGS.SHOW_FLOW_SELECTOR),
  ENABLE_DEBUG_INFO: getEnvFlag('ENABLE_DEBUG_INFO', DEFAULT_FLAGS.ENABLE_DEBUG_INFO),
  SHOW_TOKEN_INFO: getEnvFlag('SHOW_TOKEN_INFO', DEFAULT_FLAGS.SHOW_TOKEN_INFO),
  
  // Development
  AUTO_LOGIN: getEnvFlag('AUTO_LOGIN', DEFAULT_FLAGS.AUTO_LOGIN),
  SKIP_VALIDATION: getEnvFlag('SKIP_VALIDATION', DEFAULT_FLAGS.SKIP_VALIDATION)
};

/**
 * Utility functions for feature flags
 */
export const FeatureFlagUtils = {
  /**
   * Check if a specific login flow is enabled
   */
  isFlowEnabled: (flow) => {
    switch (flow) {
      case 'direct':
        return FEATURE_FLAGS.ENABLE_DIRECT_FLOW;
      case 'standard':
        return FEATURE_FLAGS.ENABLE_STANDARD_FLOW;
      default:
        return false;
    }
  },

  /**
   * Get available login flows
   */
  getAvailableFlows: () => {
    const flows = [];
    if (FEATURE_FLAGS.ENABLE_DIRECT_FLOW) flows.push('direct');
    if (FEATURE_FLAGS.ENABLE_STANDARD_FLOW) flows.push('standard');
    return flows;
  },

  /**
   * Get the default flow to display
   */
  getDefaultFlow: () => {
    const availableFlows = FeatureFlagUtils.getAvailableFlows();
    
    // If both flows are available and default is 'both', return 'both'
    if (FEATURE_FLAGS.DEFAULT_LOGIN_FLOW === 'both' && availableFlows.length > 1) {
      return 'both';
    }
    
    // If specific flow is set as default and available, return it
    if (availableFlows.includes(FEATURE_FLAGS.DEFAULT_LOGIN_FLOW)) {
      return FEATURE_FLAGS.DEFAULT_LOGIN_FLOW;
    }
    
    // Fallback to first available flow
    return availableFlows[0] || 'direct';
  },

  /**
   * Check if demo mode is active
   */
  isDemoMode: () => FEATURE_FLAGS.DEMO_MODE || FEATURE_FLAGS.MOCK_KEYCLOAK_RESPONSES,

  /**
   * Get debug information
   */
  getDebugInfo: () => ({
    flags: FEATURE_FLAGS,
    availableFlows: FeatureFlagUtils.getAvailableFlows(),
    defaultFlow: FeatureFlagUtils.getDefaultFlow(),
    demoMode: FeatureFlagUtils.isDemoMode(),
    environment: import.meta.env.MODE
  })
};

/**
 * Console log feature flags in development
 */
if (import.meta.env.DEV && FEATURE_FLAGS.ENABLE_DEBUG_INFO) {
  console.group('🚩 Feature Flags Configuration');
  console.log('Available Flows:', FeatureFlagUtils.getAvailableFlows());
  console.log('Default Flow:', FeatureFlagUtils.getDefaultFlow());
  console.log('Demo Mode:', FeatureFlagUtils.isDemoMode());
  console.log('All Flags:', FEATURE_FLAGS);
  console.groupEnd();
}

export default FEATURE_FLAGS;
