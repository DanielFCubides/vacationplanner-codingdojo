import './App.css'
import Dashboard from "./Dashboard.jsx";
import LoginPage from "./LoginPage.jsx";
import LandingPage from "./LandingPage.jsx";
import FlightDetailsView from "./flightDetailsView";
import {AuthProvider} from "./authContext.jsx";
import React, { useEffect } from 'react';
import {useAuth} from "./useAuth.js";
import authService from "./services/authService.js";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';

// Loading component for OAuth callback processing
const CallbackLoader = () => {
    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Processing authentication...</p>
            </div>
        </div>
    );
};

// OAuth Callback Handler Component
const OAuthCallbackHandler = () => {
    const { loginWithOAuth } = useAuth();
    const navigate = useNavigate();
    const [isProcessing, setIsProcessing] = React.useState(false);

    useEffect(() => {
        // Prevent multiple executions
        if (isProcessing) {
            console.log('⚠️ Already processing callback, skipping...');
            return;
        }

        const handleOAuthCallback = async () => {
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            const state = urlParams.get('state');
            const error = urlParams.get('error');
            
            console.log('🔵 OAuth Callback Handler - URL params:', { 
                code: code ? 'exists' : 'none', 
                state: state ? 'exists' : 'none',
                error 
            });
            
            // Handle OAuth error from Keycloak
            if (error) {
                console.error('❌ OAuth error from Keycloak:', error, urlParams.get('error_description'));
                navigate('/login', { 
                    state: { error: `Authentication failed: ${error}` },
                    replace: true 
                });
                return;
            }
            
            // Process authorization code
            if (code) {
                // Mark as processing to prevent duplicate calls
                setIsProcessing(true);
                
                try {
                    console.log('🔵 Processing OAuth callback with code and state');
                    console.log('🔵 Full callback URL:', window.location.href);
                    
                    // Use handleOAuthCallback instead of exchangeCodeForToken
                    // This properly validates state and exchanges code
                    const result = await authService.handleOAuthCallback(window.location.href);
                    
                    console.log('🔵 OAuth callback result:', result);
                    
                    if (result && result.success) {
                        console.log('✅ OAuth login successful, user:', result.user);
                        // Update auth context with the result (not just the code)
                        if (loginWithOAuth) {
                            await loginWithOAuth(result);
                        }
                        console.log('🎯 Navigating to dashboard...');
                        navigate('/dashboard', { replace: true });
                    } else {
                        console.error('❌ OAuth login failed:', result);
                        const errorMessage = result?.error || 'Authentication failed';
                        navigate('/login', { 
                            state: { error: errorMessage },
                            replace: true 
                        });
                    }
                } catch (error) {
                    console.error('❌ OAuth login error:', error);
                    navigate('/login', { 
                        state: { error: error.message || 'Authentication failed' },
                        replace: true 
                    });
                } finally {
                    setIsProcessing(false);
                }
            } else {
                // No code and no error = invalid callback
                console.warn('⚠️ No code parameter found in callback - redirecting to login');
                navigate('/login', { replace: true });
            }
        };

        handleOAuthCallback();
    }, [loginWithOAuth, navigate, isProcessing]);

    return <CallbackLoader />;
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const App = () => {
    const location = useLocation();
    const navigate = useNavigate();
    
    // Check for OAuth callback on root path (fallback)
    useEffect(() => {
        const urlParams = new URLSearchParams(location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        
        // If we have OAuth params on root path, redirect to proper callback handler
        if (code && location.pathname === '/') {
            console.log('🔄 OAuth callback detected on root path, redirecting to /auth/callback');
            navigate(`/auth/callback${location.search}`, { replace: true });
        }
    }, [location, navigate]);
    
    return (
        <div className="App">
            <Routes>
                {/* Landing Page - No authentication required */}
                <Route path="/" element={<LandingPage />} />
                
                {/* Login Page - No authentication required */}
                <Route path="/login" element={<LoginPage />} />
                
                {/* OAuth Callback Handler */}
                <Route path="/auth/callback" element={<OAuthCallbackHandler />} />
                
                {/* Protected Dashboard Route */}
                <Route 
                    path="/dashboard" 
                    element={
                        <ProtectedRoute>
                            <Dashboard />
                        </ProtectedRoute>
                    } 
                />
                <Route path="/trips/:tripId" element={<FlightDetailsView />} />
                
                {/* Catch all - redirect to landing page */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </div>
    );
};

// Root component with providers
const AppWithProviders = () => {
    return (
        <Router>
            <AuthProvider>
                <App/>
            </AuthProvider>
        </Router>
    );
};

export default AppWithProviders;
