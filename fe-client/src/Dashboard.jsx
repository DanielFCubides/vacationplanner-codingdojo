import React from 'react';
import {useAuth} from "./useAuth.js";
import {useNavigate} from "react-router-dom";

const Dashboard = () => {
    const {user, logout, tokens} = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    console.log("user", user);

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                        >
                            Logout
                        </button>
                    </div>

                    <div className="bg-green-50 border border-green-200 rounded-md p-4">
                        <h2 className="text-lg font-semibold text-green-800 mb-2">Welcome!</h2>
                        <p className="text-green-700">
                            You are successfully logged in as: <strong>{user?.email}</strong>
                        </p>
                        <p className="text-green-700 mt-1">
                            User ID: {user?.id}
                        </p>
                        <p className="text-green-700 mt-1 justify-between items-center mb-6">
                            Token: {tokens?.accessToken}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
export default Dashboard;
