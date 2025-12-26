import React, {useEffect, useState} from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import {Trip} from "./Models.ts";
import {getTripById} from "./services/TripService";
import TripDetailOverview from "./TripDetailOverview.tsx";


const FlightDetailsView = () => {

    const formatDate = (date: Date) => {
        return new Date(date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });
    };

    const {tripId} = useParams();
    const [trip, setTrip] = useState<Trip | null>(null);
    useEffect(() => {
        // Simulate loading delay
        const timer = setTimeout(() => {
            if (tripId) {
                setTrip(getTripById(tripId));
            }
        }, 500);

        return () => clearTimeout(timer);
    }, [tripId]);
    const navigate = useNavigate();
    if (!tripId) return (
        <div>
            <div className="min-h-screen bg-secondary p-8 flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-foreground mb-4">Trip not found</h2>
                    <button onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
                </div>
            </div>
        </div>
    )
    if (trip) return (
        <div>
            <div className="max-w-6xl mx-auto">
                <nav className="text-sm mb-4">
                    <span
                        className="text-muted-foreground hover:text-foreground cursor-pointer"
                        onClick={() => navigate('/dashboard')}
                    >
                Dashboard
                    </span>
                    <span className="text-muted-foreground mx-2">/</span>
                    <span className="text-foreground">{tripId}</span>
                </nav>
            </div>

            <div className="bg-card rounded-lg shadow p-6 mb-6">
                <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <h1 className="text-2xl md:text-3xl font-bold text-foreground">{trip.name}</h1>

                            {trip.status.charAt(0).toUpperCase() + trip.status.slice(1)}

                        </div>
                        <p className="text-muted-foreground flex items-center gap-2">
                            <span>📍</span>
                            {trip.destination}
                        </p>
                        <p className="text-muted-foreground flex items-center gap-2 mt-1">
                            <span>📅</span>
                            {formatDate(trip.startDate)} - {formatDate(trip.endDate)}
                        </p>
                    </div>
                </div>
            </div>

            <TripDetailOverview trip={trip}/>
        </div>

    );
};

export default FlightDetailsView;

