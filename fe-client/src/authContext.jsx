import React, {createContext, useState, useEffect} from 'react';
import authService from "./services/authService.js";

const AuthContext = createContext();



const AuthProvider = ({children}) => {
    const [tokens, setTokens] = useState(null);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Check if user is already logged in on app start
    useEffect(() => {
        const checkExistingAuth = () => {
            try {
                if (authService.isAuthenticated()) {
                    const currentUser = authService.getCurrentUser();
                    setUser(currentUser);
                    const currentToken = authService.getCurrentToken();
                    console.log('tokens: ',currentToken);
                    setTokens({"accessToken": currentToken});
                }



            } catch (error) {
                console.error('Auth check failed:', error);
                // Clear any invalid tokens
                authService.removeToken();
            } finally {
                setLoading(false);
            }
        };

        checkExistingAuth();
    }, []);

    const login = async (username, password) => {
        try {
            console.log("loging user" + user);
            setLoading(true);
            setError(null);
            const response = await authService.loginWithCredentials(username, password);

            if (response.success) {
                setUser(response.user);
                setTokens(response.tokens);
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
        console.log("Setting user from OAuth flow result:", result);
        try {
            setLoading(true);
            setError(null);

            // If we're passed just a code string, handle it
            if (typeof result === 'string') {
                console.log("⚠️ Received code string, but should receive result object");
                const response = await authService.handleOAuthCallback(window.location.href);
                if (response.success) {
                    console.log("✅ OAuth successful, setting user:", response.user);
                    setUser(response.user);
                    setTokens(response.tokens);
                }
                return response;
            }
            
            // If we're passed the result object from handleOAuthCallback
            if (result && result.user) {
                console.log("✅ Setting user from OAuth result:", result.user);
                setUser(result.user);
                setTokens(result.tokens);
                return result;
            }
            
            // Fallback
            return { success: false, error: 'Invalid OAuth result' };
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
            setTokens(null);
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
        isAuthenticated: !!user && authService.isAuthenticated(),
        tokens,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export {AuthContext, AuthProvider};
