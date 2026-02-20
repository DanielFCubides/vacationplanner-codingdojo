/**
 * useFeatureFlags Hook
 * 
 * React hook for accessing feature flags and flow configuration
 * throughout the application.
 */

import { useState, useEffect, useCallback } from 'react';
import { FEATURE_FLAGS, FeatureFlagUtils } from '../config/featureFlags.js';
import { KEYCLOAK_CONFIG, DEMO_CONFIG } from '../config/keycloakConfig.js';

export const useFeatureFlags = () => {
  const [currentFlow, setCurrentFlow] = useState(() => FeatureFlagUtils.getDefaultFlow());
  const [debugMode, setDebugMode] = useState(FEATURE_FLAGS.ENABLE_DEBUG_INFO);

  /**
   * Check if a specific feature is enabled
   */
  const isFeatureEnabled = useCallback((featureName) => {
    return FEATURE_FLAGS[featureName] === true;
  }, []);

  /**
   * Check if a specific flow is enabled
   */
  const isFlowEnabled = useCallback((flow) => {
    return FeatureFlagUtils.isFlowEnabled(flow);
  }, []);

  /**
   * Get all available flows
   */
  const getAvailableFlows = useCallback(() => {
    return FeatureFlagUtils.getAvailableFlows();
  }, []);

  /**
   * Switch to a different flow (if enabled)
   */
  const switchFlow = useCallback((newFlow) => {
    if (FeatureFlagUtils.isFlowEnabled(newFlow) || newFlow === 'both') {
      setCurrentFlow(newFlow);
      if (debugMode) {
        console.log('🔀 Flow switched to:', newFlow);
      }
      return true;
    }
    return false;
  }, [debugMode]);

  /**
   * Toggle debug mode
   */
  const toggleDebugMode = useCallback(() => {
    setDebugMode(prev => !prev);
  }, []);

  /**
   * Get demo user credentials based on current flow
   */
  const getDemoCredentials = useCallback((flow = currentFlow) => {
    if (flow === 'direct') {
      return DEMO_CONFIG.demoUsers.direct;
    }
    return DEMO_CONFIG.demoUsers.standard;
  }, [currentFlow]);

  /**
   * Get current configuration summary
   */
  const getConfigSummary = useCallback(() => {
    return {
      // Current state
      currentFlow,
      debugMode,
      
      // Available features
      availableFlows: getAvailableFlows(),
      
      // Feature flags
      showFlowSelector: isFeatureEnabled('SHOW_FLOW_SELECTOR'),
      demoMode: isFeatureEnabled('DEMO_MODE'),
      mockResponses: isFeatureEnabled('MOCK_KEYCLOAK_RESPONSES'),
      showTokenInfo: isFeatureEnabled('SHOW_TOKEN_INFO'),
      
      // Environment info
      environment: import.meta.env.MODE,
      keycloakUrl: KEYCLOAK_CONFIG.url,
      
      // Demo settings
      demoCredentials: getDemoCredentials()
    };
  }, [currentFlow, debugMode, isFeatureEnabled, getAvailableFlows, getDemoCredentials]);

  /**
   * Log configuration changes in debug mode
   */
  useEffect(() => {
    if (debugMode) {
      console.group('🚩 Feature Flags Update');
      console.log('Current Flow:', currentFlow);
      console.log('Available Flows:', getAvailableFlows());
      console.log('Configuration:', getConfigSummary());
      console.groupEnd();
    }
  }, [currentFlow, debugMode, getAvailableFlows, getConfigSummary]);

  return {
    // Current state
    currentFlow,
    debugMode,
    
    // Feature checks
    isFeatureEnabled,
    isFlowEnabled,
    
    // Flow management
    availableFlows: getAvailableFlows(),
    switchFlow,
    
    // Debug utilities
    toggleDebugMode,
    
    // Demo utilities
    getDemoCredentials,
    
    // Configuration access
    getConfigSummary,
    
    // Quick access to common flags
    flags: {
      showFlowSelector: isFeatureEnabled('SHOW_FLOW_SELECTOR'),
      demoMode: isFeatureEnabled('DEMO_MODE'),
      mockResponses: isFeatureEnabled('MOCK_KEYCLOAK_RESPONSES'),
      showTokenInfo: isFeatureEnabled('SHOW_TOKEN_INFO'),
      enableDebugInfo: isFeatureEnabled('ENABLE_DEBUG_INFO'),
      autoLogin: isFeatureEnabled('AUTO_LOGIN'),
    }
  };
};

export default useFeatureFlags;
