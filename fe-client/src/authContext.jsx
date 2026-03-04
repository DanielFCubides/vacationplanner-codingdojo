import React, { createContext, useState, useEffect } from 'react';
import authService from "./services/authService.js";
import { tripService } from "./services/TripService.ts";

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // On app start, verify session with the backend via the HTTPOnly cookie.
    // No localStorage involved — the cookie is sent automatically by the browser.
    useEffect(() => {
        const checkExistingSession = async () => {
            try {
                const currentUser = await authService.checkSession();
                if (currentUser) {
                    setUser(currentUser);
                }
            } catch (err) {
                console.error('Session check failed:', err);
            } finally {
                setLoading(false);
            }
        };

        checkExistingSession();
    }, []);

    /**
     * Direct Flow login (username + password).
     * The backend is NOT involved in this flow; Keycloak is called directly.
     */
    const login = async (username, password) => {
        try {
            setLoading(true);
            setError(null);
            const response = await authService.loginWithCredentials(username, password);

            if (response.success) {
                setUser(response.user);
            }
            return response;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Called after the backend has set the HTTPOnly cookie and redirected
     * the browser to the frontend /auth/callback route.
     * Accepts the result from authService.handleOAuthCallback() which
     * already contains the verified user info from the backend.
     *
     * @param {Object} result - Result from authService.handleOAuthCallback()
     */
    const loginWithOAuth = async (result) => {
        try {
            setLoading(true);
            setError(null);

            // If we're passed just a code string, handle it
            if (typeof result === 'string') {
                // console.log("⚠️ Received code string, but should receive result object");
                const response = await authService.handleOAuthCallback(window.location.href);
                if (response.success) {
                    // console.log("✅ OAuth successful, setting user:", response.user);
                    setUser(response.user);
                    setTokens(response.tokens);
                    tripService.setToken(response.tokens.accessToken);
                }
                return response;
            }

            // If we're passed the result object from handleOAuthCallback
            if (result && result.user) {
                // console.log("✅ Setting user from OAuth result:", result.user);
                setUser(result.user);
                setTokens(result.tokens);
                tripService.setToken(result.tokens.accessToken);
                return result;
            }

            return { success: false, error: 'Invalid OAuth result — no user info received' };
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Logout: calls the backend to invalidate the session cookie,
     * then clears local user state.
     */
    const logout = async () => {
        try {
            setLoading(true);
            await authService.logout();
            setUser(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const clearError = () => setError(null);

    const value = {
        user,
        loading,
        error,
        login,
        loginWithOAuth,
        logout,
        clearError,
        isAuthenticated: !!user,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export { AuthContext, AuthProvider };
