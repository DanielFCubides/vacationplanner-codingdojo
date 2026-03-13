import React, { createContext, useState, useEffect } from 'react';
import authService from "./services/authService.js";
import { tripService } from "./services/TripService.ts";

const AuthContext = createContext();



const AuthProvider = ({ children }) => {
    const [tokens, setTokens] = useState(null);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const checkExistingSession = async () => {
            try {
                const currentUser = await authService.checkSession();
                if (currentUser) {
                    setUser(currentUser);
                }
            } catch (error) {
                console.error('Session check failed:', err);
            } finally {
                setLoading(false);
            }
        };

        checkExistingSession();
    }, []);

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

    const loginWithOAuth = async (result) => {
        try {
            setLoading(true);
            setError(null);

            if (typeof result === 'string') {
                const response = await authService.handleOAuthCallback(window.location.href);
                if (response.success) {
                    setUser(response.user);
                    setTokens(response.tokens);
                    tripService.setToken(response.tokens.accessToken);
                }
                return response;
            }

            if (result && result.user) {
                setUser(result.user);
                setTokens(result.tokens);
                tripService.setToken(result.tokens.accessToken);
                return result;
            }

            // Fallback
            return { success: false, error: 'Invalid OAuth result — no user info received' };
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

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
        isAuthenticated: !!user
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export { AuthContext, AuthProvider };
