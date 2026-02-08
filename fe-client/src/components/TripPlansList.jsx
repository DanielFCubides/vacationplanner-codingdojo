import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tripService } from '../services/TripService';

const TripPlansList = () => {
    const navigate = useNavigate();
    const [trips, setTrips] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadTrips();
    }, []);

    const loadTrips = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await tripService.getAllTrips();
            setTrips(data);
        } catch (err) {
            console.error('Failed to load trips:', err);
            setError('Failed to load trips. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status.toLowerCase()) {
            case 'confirmed': return 'bg-green-100 text-green-800 border-green-200';
            case 'planning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            case 'completed': return 'bg-gray-100 text-gray-800 border-gray-200';
            default: return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    const formatDate = (date) => {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    };

    const handleCardClick = (tripId) => {
        navigate(`/trips/${tripId}`);
    };

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">My Trip Plans</h2>
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-3 text-gray-600">Loading trips...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">My Trip Plans</h2>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800">{error}</p>
                    <button
                        onClick={loadTrips}
                        className="mt-2 text-sm text-red-600 hover:text-red-700 font-medium"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    if (trips.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">My Trip Plans</h2>
                <div className="text-center py-12">
                    <p className="text-gray-600 mb-4">No trips planned yet</p>
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        Plan Your First Trip
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800">My Trip Plans</h2>
                <span className="text-sm text-gray-600">{trips.length} trip{trips.length !== 1 ? 's' : ''}</span>
            </div>
            <div className="space-y-4">
                {trips.map((trip) => (
                    <div
                        key={trip.id}
                        onClick={() => handleCardClick(trip.id)}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-lg hover:border-gray-300 transition-all cursor-pointer group"
                    >
                        {/* Header with Title and Status */}
                        <div className="flex justify-between items-start mb-3">
                            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                                {trip.name}
                            </h3>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(trip.status)} capitalize`}>
                                {trip.status}
                            </span>
                        </div>

                        {/* Trip Details Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                            <div>
                                <p className="text-gray-500 text-xs mb-1">Destination</p>
                                <p className="font-medium text-gray-900">{trip.destination}</p>
                            </div>
                            <div>
                                <p className="text-gray-500 text-xs mb-1">Departure</p>
                                <p className="font-medium text-gray-900">{formatDate(trip.startDate)}</p>
                            </div>
                            <div>
                                <p className="text-gray-500 text-xs mb-1">Return</p>
                                <p className="font-medium text-gray-900">{formatDate(trip.endDate)}</p>
                            </div>
                            <div>
                                <p className="text-gray-500 text-xs mb-1">Budget</p>
                                <p className="font-semibold text-green-600">
                                    ${trip.budget.total.toLocaleString()}
                                </p>
                            </div>
                        </div>

                        {/* Footer with Travelers, Flights, and View Details Button */}
                        <div className="flex justify-between items-center pt-3 border-t border-gray-100">
                            <div className="flex items-center gap-4 text-sm text-gray-600">
                                <div className="flex items-center gap-1">
                                    <span>👥</span>
                                    <span>{trip.travelers.length}</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <span>✈️</span>
                                    <span>{trip.flights.length}</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <span>🏨</span>
                                    <span>{trip.accommodations.length}</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <span>📅</span>
                                    <span>{trip.activities.length}</span>
                                </div>
                            </div>

                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleCardClick(trip.id);
                                }}
                                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                            >
                                View Details
                                <svg
                                    className="w-4 h-4"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M9 5l7 7-7 7"
                                    />
                                </svg>
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TripPlansList;