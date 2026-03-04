import './App.css'
import Dashboard from "./Dashboard.jsx";
import LoginPage from "./LoginPage.jsx";
import LandingPage from "./LandingPage.jsx";
import TripDetailsView from "./tripDetailsView.tsx";
import NewTripWizard from "./components/NewTripWizard.tsx";
import { AuthProvider } from "./authContext.jsx";
import React, { useEffect } from 'react';
<<<<<<< Updated upstream
import {useAuth} from "./hooks/useAuth.js";
import authService from "./services/authService.js";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
=======
import { useAuth } from "./useAuth.js";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
>>>>>>> Stashed changes

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
//
// The backend receives the Keycloak ?code=, exchanges it, sets the HTTPOnly
// cookie, and then redirects the browser to '/' (root).
// authContext's startup checkSession() fires at '/' and populates the user.
//
// This component is only reached if the user navigates directly to
// /auth/callback. It simply waits for the auth context to resolve and
// redirects to /dashboard if a valid session exists.
const OAuthCallbackHandler = () => {
    const { isAuthenticated, loading, loginWithOAuth, user } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        // Wait until authContext has finished the startup checkSession() call
        if (loading) return;

        if (isAuthenticated && user) {
            console.log('✅ Session already active, redirecting to dashboard:', user);
            loginWithOAuth({ success: true, user });
            navigate('/dashboard', { replace: true });
        } else {
            console.warn('⚠️ No active session found at /auth/callback, redirecting to login');
            navigate('/login', { replace: true });
        }
    }, [isAuthenticated, loading, user, loginWithOAuth, navigate]);

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

// Root Handler
//
// The backend redirects to '/' after setting the HTTPOnly cookie.
// authContext's startup checkSession() runs here and sets the user.
// Once loading is done, redirect authenticated users to /dashboard;
// otherwise show the LandingPage normally.
const RootHandler = () => {
    const { isAuthenticated, loading } = useAuth();

    if (loading) return <CallbackLoader />;
    if (isAuthenticated) return <Navigate to="/dashboard" replace />;
    return <LandingPage />;
};

const App = () => {
    return (
        <div className="App">
            <Routes>
                {/* Landing Page — redirects to /dashboard if session cookie is active */}
                <Route path="/" element={<RootHandler />} />

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

                {/* New Trip Wizard - Protected */}
                <Route
                    path="/trips/new"
                    element={
                        <ProtectedRoute>
                            <NewTripWizard />
                        </ProtectedRoute>
                    }
                />

                {/* Trip Details - Protected */}
                <Route
                    path="/trips/:tripId"
                    element={
                        <ProtectedRoute>
                            <TripDetailsView />
                        </ProtectedRoute>
                    }
                />

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
                <App />
            </AuthProvider>
        </Router>
    );
};

export default AppWithProviders;
