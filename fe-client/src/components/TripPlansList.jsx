import React from 'react';

// Simple fake data based on the vacation planner system structure
const fakeTripPlans = [
    {
        id: 1,
        title: "Weekend in Bogotá",
        origin: "CTG",
        destination: "BOG",
        departureDate: "2025-11-15",
        returnDate: "2025-11-17",
        passengers: 2,
        flightPrice: 925.30,
        status: "confirmed"
    },
    {
        id: 2,
        title: "Medellín Adventure",
        origin: "BOG",
        destination: "MDE",
        departureDate: "2025-12-10",
        returnDate: "2025-12-15",
        passengers: 1,
        flightPrice: 523.15,
        status: "planning"
    },
    {
        id: 3,
        title: "Caribbean Coast Trip",
        origin: "BOG",
        destination: "CTG",
        departureDate: "2025-12-20",
        returnDate: "2025-12-25",
        passengers: 4,
        flightPrice: 1250.00,
        status: "draft"
    }
];

const TripPlansList = () => {
    const getStatusColor = (status) => {
        switch (status) {
            case 'confirmed': return 'bg-green-100 text-green-800 border-green-200';
            case 'planning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            case 'draft': return 'bg-gray-100 text-gray-800 border-gray-200';
            default: return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">My Trip Plans</h2>
            <div className="space-y-4">
                {fakeTripPlans.map((trip) => (
                    <div key={trip.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start mb-2">
                            <h3 className="text-lg font-medium text-gray-900">{trip.title}</h3>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(trip.status)}`}>
                                {trip.status}
                            </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                                <p className="text-gray-600">Route</p>
                                <p className="font-medium">{trip.origin} → {trip.destination}</p>
                            </div>
                            <div>
                                <p className="text-gray-600">Departure</p>
                                <p className="font-medium">{trip.departureDate}</p>
                            </div>
                            <div>
                                <p className="text-gray-600">Return</p>
                                <p className="font-medium">{trip.returnDate}</p>
                            </div>
                            <div>
                                <p className="text-gray-600">Price</p>
                                <p className="font-medium text-green-600">${trip.flightPrice.toFixed(2)}</p>
                            </div>
                        </div>
                        <div className="mt-2 text-sm text-gray-600">
                            <span>{trip.passengers} passenger{trip.passengers > 1 ? 's' : ''}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TripPlansList;
