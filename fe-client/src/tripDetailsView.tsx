import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Trip } from "./Models.ts";
import TripDetailOverview from "./TripDetailOverview.tsx";
import TripFlightsOverview from "./components/flightsOverview.tsx";
import StayOverview from "./components/StaysOverview.tsx";
import ActivitiesOverview from "./components/ActivitiesOverview.tsx";
import BudgetOverview from "./components/BudgetOverview.tsx";
import { getStatusColor } from "./utils/StatusColors.ts";
import { formatDate } from "./utils/formatDate.ts";
import TravellersOverview from "./components/TravellersOverview.tsx";
import { tripService } from "./services/TripService.ts";
import { ChildType } from "./config/childStatusTransitions.ts";

type TabKey = 'overview' | 'flights' | 'stays' | 'activities' | 'budget' | 'team';

interface Tab {
    key: TabKey;
    label: string;
    icon: string;
}

interface Toast {
    message: string;
    type: 'error' | 'success';
}

/**
 * Return a shallow clone of the trip with a single child's status changed.
 * Used for the optimistic UI update before the PATCH resolves (FR-9).
 */
const applyChildStatus = (
    trip: Trip,
    childType: ChildType,
    childId: string,
    newStatus: string,
): Trip => {
    if (childType === 'flight') {
        return {
            ...trip,
            flights: trip.flights.map(f =>
                f.id === childId ? { ...f, status: newStatus as Trip['flights'][number]['status'] } : f),
        };
    }
    if (childType === 'accommodation') {
        return {
            ...trip,
            accommodations: trip.accommodations.map(a =>
                a.id === childId ? { ...a, status: newStatus as Trip['accommodations'][number]['status'] } : a),
        };
    }
    return {
        ...trip,
        activities: trip.activities.map(a =>
            a.id === childId ? { ...a, status: newStatus as Trip['activities'][number]['status'] } : a),
    };
};

const TripDetailsView = () => {
    const { tripId } = useParams();
    const [trip, setTrip] = useState<Trip | null>(null);
    const [activeTab, setActiveTab] = useState<TabKey>('overview');
    const [toast, setToast] = useState<Toast | null>(null);
    const navigate = useNavigate();

    /**
     * Update a child's status optimistically, then reconcile with the backend.
     * On failure, revert to the previous trip and surface the error (FR-9).
     */
    const handleChildStatusChange = async (
        childType: ChildType,
        childId: string,
        newStatus: string,
    ) => {
        if (!trip) return;
        const previous = trip;
        setTrip(applyChildStatus(trip, childType, childId, newStatus));
        try {
            let updated: Trip;
            if (childType === 'flight') {
                updated = await tripService.updateFlightStatus(previous.id, childId, newStatus);
            } else if (childType === 'accommodation') {
                updated = await tripService.updateAccommodationStatus(previous.id, childId, newStatus);
            } else {
                updated = await tripService.updateActivityStatus(previous.id, childId, newStatus);
            }
            // Authoritative response carries the recalculated budget (FR-12).
            setTrip(updated);
        } catch (err) {
            setTrip(previous);
            setToast({
                message: err instanceof Error ? err.message : 'Failed to update status',
                type: 'error',
            });
        }
    };

    // Define tabs
    const tabs: Tab[] = [
        { key: 'overview', label: 'Overview', icon: '📋' },
        { key: 'flights', label: 'Flights', icon: '✈️' },
        { key: 'stays', label: 'Stays', icon: '🏨' },
        { key: 'activities', label: 'Activities', icon: '📅' },
        { key: 'budget', label: 'Budget', icon: '💰' },
        { key: 'team', label: 'Team', icon: '👥' },
    ];

    useEffect(() => {
        const timer = setTimeout(async () => {
            if (tripId) {
                setTrip(await tripService.getTripById(tripId));
            }
        }, 500);

        return () => clearTimeout(timer);
    }, [tripId]);

    // Auto-dismiss the toast after a few seconds.
    useEffect(() => {
        if (!toast) return;
        const timer = setTimeout(() => setToast(null), 4000);
        return () => clearTimeout(timer);
    }, [toast]);

    const renderTabContent = () => {
        if (!trip) return null;

        switch (activeTab) {
            case 'overview':
                return <TripDetailOverview trip={trip} />;

            case 'flights':
                return <TripFlightsOverview
                    trip={trip}
                    onStatusChange={(flightId, newStatus) =>
                        handleChildStatusChange('flight', flightId, newStatus)}
                />;

            case 'stays':
                return <StayOverview
                    trip={trip}
                    onStatusChange={(accommodationId, newStatus) =>
                        handleChildStatusChange('accommodation', accommodationId, newStatus)}
                />;

            case 'activities':
                return <ActivitiesOverview
                    trip={trip}
                    onStatusChange={(activityId, newStatus) =>
                        handleChildStatusChange('activity', activityId, newStatus)}
                />;

            case 'budget':
                return <BudgetOverview trip={trip} />;

            case 'team':
                return <TravellersOverview trip={trip} />;

            default:
                return null;
        }
    };

    if (!tripId) {
        return (
            <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Trip not found</h2>
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    if (!trip) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading trip details...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            {/* Toast notification (FR-9) */}
            {toast && (
                <div
                    className={`fixed top-4 right-4 z-50 max-w-sm px-4 py-3 rounded-lg shadow-lg text-sm font-medium ${
                        toast.type === 'error'
                            ? 'bg-red-100 text-red-800 border border-red-200'
                            : 'bg-green-100 text-green-800 border border-green-200'
                    }`}
                    role="alert"
                >
                    {toast.message}
                </div>
            )}
            <div className="max-w-6xl mx-auto">
                {/* Breadcrumb Navigation */}
                <nav className="text-sm mb-6">
                    <span
                        className="text-gray-500 hover:text-gray-900 cursor-pointer transition-colors"
                        onClick={() => navigate('/dashboard')}
                    >
                        Dashboard
                    </span>
                    <span className="text-gray-400 mx-2">/</span>
                    <span className="text-gray-900 font-medium">{trip.name}</span>
                </nav>

                {/* Trip Header Card */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                        <div className="flex-1">
                            {/* Title and Status Badge */}
                            <div className="flex items-center gap-3 mb-3">
                                <h1 className="text-3xl font-bold text-gray-900">{trip.name}</h1>
                                <span
                                    className={`inline-block px-3 py-1 rounded-full text-sm font-medium capitalize ${getStatusColor(trip.status)}`}>
                                    {trip.status}
                                </span>
                            </div>

                            {/* Location */}
                            <p className="text-gray-600 flex items-center gap-2 mb-2">
                                <span className="text-lg">📍</span>
                                <span className="text-base">{trip.destination}</span>
                            </p>

                            {/* Dates */}
                            <p className="text-gray-600 flex items-center gap-2">
                                <span className="text-lg">📅</span>
                                <span className="text-base">
                                    {formatDate(trip.startDate)} - {formatDate(trip.endDate)}
                                </span>
                            </p>
                        </div>
                        <div>{trip.id}</div>

                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6 overflow-x-auto">
                    <nav className="flex">
                        {tabs.map((tab) => (
                            <button
                                key={tab.key}
                                onClick={() => setActiveTab(tab.key)}
                                className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === tab.key
                                    ? 'border-blue-600 text-blue-600'
                                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                                    }`}
                            >
                                <span className="text-lg">{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Tab Content */}
                {renderTabContent()}
            </div>
        </div>
    );
};

export default TripDetailsView;