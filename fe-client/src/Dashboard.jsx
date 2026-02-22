import React from 'react';
import {useAuth} from "./hooks/useAuth.js";
import {useNavigate} from "react-router-dom";
import UserProfile from "./components/UserProfile.jsx";
import TripPlansList from "./components/TripPlansList.jsx";
import AddTripContainer from "./components/AddTripContainer.tsx";

const Dashboard = () => {
    const {user, logout, tokens} = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-6xl mx-auto">
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <div className="flex justify-between items-center mb-6">
                        <h1 className="text-3xl font-bold text-gray-900">Vacation Planner Dashboard</h1>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                        >
                            Logout
                        </button>
                    </div>
                </div>

                {/* User Profile Section */}
                <UserProfile user={user} />

                <AddTripContainer/>

                {/* Trip Plans Section */}
                <TripPlansList />
            </div>
        </div>
    );
};
export default Dashboard;
