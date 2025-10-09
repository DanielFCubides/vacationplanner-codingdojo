/**
 * FeatureFlagTest Component
 * 
 * Simple test component to verify feature flag system is working.
 * Shows current configuration and allows testing of flag switching.
 */

import React from 'react';
import useFeatureFlags from '../hooks/useFeatureFlags.js';

const FeatureFlagTest = () => {
  const {
    currentFlow,
    debugMode,
    flags,
    availableFlows,
    switchFlow,
    toggleDebugMode,
    getDemoCredentials,
    getConfigSummary
  } = useFeatureFlags();

  const configSummary = getConfigSummary();
  const demoCredentials = getDemoCredentials();

  return (
    <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg m-4">
      <h3 className="text-lg font-bold mb-4 text-gray-800">
        🚩 Feature Flag Test Panel
      </h3>
      
      {/* Current Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-white p-4 rounded border">
          <h4 className="font-semibold text-gray-700 mb-2">Current Configuration</h4>
          <ul className="text-sm space-y-1">
            <li><strong>Current Flow:</strong> {currentFlow}</li>
            <li><strong>Available Flows:</strong> {availableFlows.join(', ')}</li>
            <li><strong>Environment:</strong> {configSummary.environment}</li>
            <li><strong>Debug Mode:</strong> {debugMode ? '✅' : '❌'}</li>
          </ul>
        </div>
        
        <div className="bg-white p-4 rounded border">
          <h4 className="font-semibold text-gray-700 mb-2">Feature Flags</h4>
          <ul className="text-sm space-y-1">
            <li><strong>Show Flow Selector:</strong> {flags.showFlowSelector ? '✅' : '❌'}</li>
            <li><strong>Demo Mode:</strong> {flags.demoMode ? '✅' : '❌'}</li>
            <li><strong>Mock Responses:</strong> {flags.mockResponses ? '✅' : '❌'}</li>
            <li><strong>Show Token Info:</strong> {flags.showTokenInfo ? '✅' : '❌'}</li>
          </ul>
        </div>
      </div>

      {/* Demo Credentials */}
      {flags.demoMode && (
        <div className="bg-blue-50 p-4 rounded border border-blue-200 mb-6">
          <h4 className="font-semibold text-blue-800 mb-2">Demo Credentials</h4>
          <div className="text-sm">
            <p><strong>Username:</strong> {demoCredentials.username}</p>
            <p><strong>Password:</strong> {demoCredentials.password}</p>
            <p><strong>Email:</strong> {demoCredentials.email}</p>
          </div>
        </div>
      )}

      {/* Flow Switching Controls */}
      <div className="bg-white p-4 rounded border mb-4">
        <h4 className="font-semibold text-gray-700 mb-3">Flow Controls</h4>
        <div className="flex flex-wrap gap-2">
          {availableFlows.map(flow => (
            <button
              key={flow}
              onClick={() => switchFlow(flow)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                currentFlow === flow
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {flow.charAt(0).toUpperCase() + flow.slice(1)} Flow
            </button>
          ))}
          
          {availableFlows.length > 1 && (
            <button
              onClick={() => switchFlow('both')}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                currentFlow === 'both'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Both Flows
            </button>
          )}
        </div>
      </div>

      {/* Debug Controls */}
      <div className="bg-white p-4 rounded border">
        <h4 className="font-semibold text-gray-700 mb-3">Debug Controls</h4>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={toggleDebugMode}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              debugMode
                ? 'bg-red-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {debugMode ? 'Disable' : 'Enable'} Debug Mode
          </button>
          
          <button
            onClick={() => console.log('Full Config:', getConfigSummary())}
            className="px-3 py-1 bg-blue-200 text-blue-700 rounded text-sm font-medium hover:bg-blue-300 transition-colors"
          >
            Log Full Config
          </button>
        </div>
      </div>

      {/* Environment Info */}
      {debugMode && (
        <div className="bg-yellow-50 p-4 rounded border border-yellow-200 mt-4">
          <h4 className="font-semibold text-yellow-800 mb-2">Debug Information</h4>
          <pre className="text-xs bg-yellow-100 p-2 rounded overflow-auto">
            {JSON.stringify(configSummary, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default FeatureFlagTest;
