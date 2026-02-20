import React, {useState} from 'react';
import {useAuth} from "./hooks/useAuth.js";
import {useNavigate} from "react-router-dom";
import lockLogo from './assets/LockLogo.png';
import authService from "./services/authService.js";

const LoginPage = () => {
    const [emailOrUsername, setEmailOrUsername] = useState('');
    const [password, setPassword] = useState('');
    const {login, loading, error, clearError} = useAuth();
    const navigate = useNavigate();

    // Get available flows from auth service
    const availableFlows = authService.getAvailableFlows();
    const showDirectFlow = availableFlows.includes('direct');
    const showStandardFlow = availableFlows.includes('standard');
    const onlyStandardFlow = showStandardFlow && !showDirectFlow;

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!emailOrUsername.trim() || loading) return;

        login(emailOrUsername, password)
            .then(() => {
                console.log('Login successful, redirecting to dashboard...');
                navigate('/dashboard');
            })
            .catch(() => {
                // Error is handled by context
            });
    };

    const handleKeycloakRedirect = () => {
        console.log('🔵 Initiating Keycloak redirect...');
        
        // Don't use async/await - call it synchronously to preserve user interaction chain
        authService.initiateStandardFlow().then(result => {
            console.log('🔵 Standard Flow result:', result);
            
            if (result.success && result.url) {
                console.log('🔵 Redirecting to:', result.url);
                // Use window.location.replace instead of href
                // This ensures no history entry and forces navigation
                window.location.replace(result.url);
                
                // This line should never execute if redirect works
                console.log('⚠️ This log indicates redirect might have failed!');
            } else {
                console.error('❌ Failed to get redirect URL:', result);
                alert('Failed to initiate Keycloak login. Check console for details.');
            }
        }).catch(err => {
            console.error('❌ Failed to initiate Keycloak flow:', err);
            alert('Error: ' + err.message);
        });
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center relative overflow-hidden">
            {/* Background decorative elements */}
            <div className="absolute top-0 left-0 w-64 h-64 transform -translate-x-1/2 -translate-y-1/2">
                <div className="w-full h-full bg-red-400 rounded-full opacity-80"></div>
            </div>
            <div className="absolute bottom-0 right-0 w-80 h-80 transform translate-x-1/3 translate-y-1/3">
                <div className="w-full h-full bg-red-400 rounded-full opacity-60"></div>
            </div>

            <div className="relative z-10 w-full max-w-md p-8">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-red-600 rounded-lg mb-4">
                        <img src={lockLogo} alt='logo'></img>
                    </div>

                    <h1 className="text-3xl font-semibold text-gray-900 mb-2">Sign in</h1>
                    <p className="text-gray-600">to continue to your Vacation Planner account.</p>
                </div>

                {/* Error message */}
                {error && (
                    <div className="mb-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded-md">
                        {error}
                        <button
                            onClick={clearError}
                            className="float-right text-red-500 hover:text-red-700"
                        >
                            ×
                        </button>
                    </div>
                )}

                {/* Standard Flow Only: Show Keycloak Redirect Button */}
                {onlyStandardFlow ? (
                    <div className="space-y-4">
                        <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
                            <p className="text-sm text-blue-800 text-center">
                                You will be redirected to Keycloak for secure authentication
                            </p>
                        </div>
                        
                        <button
                            onClick={handleKeycloakRedirect}
                            disabled={loading}
                            className="w-full py-3 px-4 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                        >
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                            {loading ? 'Redirecting...' : 'Take me to Keycloak'}
                        </button>

                        <p className="text-xs text-gray-500 text-center mt-4">
                            Standard Flow (OAuth 2.0 Authorization Code Grant)
                        </p>
                    </div>
                ) : (
                    /* Direct Flow: Show Username/Password Form */
                    showDirectFlow && (
                        <>
                            <div className="space-y-4">
                                <div>
                                    <input
                                        type="text"
                                        placeholder="Email address or Username"
                                        value={emailOrUsername}
                                        onChange={(e) => setEmailOrUsername(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent mb-3"
                                        disabled={loading}
                                        onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
                                    />
                                    <input
                                        type="password"
                                        placeholder="Password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                                        disabled={loading}
                                        onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
                                    />
                                </div>

                                <button
                                    onClick={handleSubmit}
                                    disabled={loading || !emailOrUsername.trim()}
                                    className="w-full py-3 px-4 bg-red-600 text-white rounded-md font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    {loading ? 'Signing in...' : 'Continue'}
                                </button>

                                <p className="text-xs text-gray-500 text-center mt-2">
                                    Direct Flow (Resource Owner Password Credentials)
                                </p>
                            </div>

                            {/* Show Standard Flow option if both are enabled */}
                            {showStandardFlow && (
                                <>
                                    <div className="my-6 flex items-center">
                                        <div className="flex-grow border-t border-gray-300"></div>
                                        <span className="px-4 text-gray-500 text-sm">or</span>
                                        <div className="flex-grow border-t border-gray-300"></div>
                                    </div>

                                    <button
                                        onClick={handleKeycloakRedirect}
                                        disabled={loading}
                                        className="w-full flex items-center justify-center px-4 py-3 border-2 border-blue-500 text-blue-600 rounded-md hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                    >
                                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                        </svg>
                                        Login with Keycloak (Standard Flow)
                                    </button>
                                </>
                            )}
                        </>
                    )
                )}

                {/* Footer links */}
                <div className="mt-6 text-center space-y-2">
                    <p className="text-sm text-gray-600">
                        Don't have an account?{' '}
                        <a href="#" className="text-blue-600 hover:underline">
                            Sign up
                        </a>
                    </p>
                    <p className="text-sm text-gray-600">
                        Can't sign in?{' '}
                        <a href="#" className="text-blue-600 hover:underline">
                            Click here
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
