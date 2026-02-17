import React from 'react';

interface FlightsStepProps {
    data: {
        airline?: string;
        flightNumber?: string;
        departureAirport?: string;
        departureTime?: string;
        arrivalAirport?: string;
        arrivalTime?: string;
    };
    onChange: (field: string, value: any) => void;
}

const FlightsStep: React.FC<FlightsStepProps> = ({ data, onChange }) => {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Flights</h2>
                <p className="text-gray-600">Add your flight details (optional)</p>
            </div>

            {/* Airline and Flight Number Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Airline */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Airline
                    </label>
                    <input
                        type="text"
                        value={data.airline || ''}
                        onChange={(e) => onChange('airline', e.target.value)}
                        placeholder="e.g., United Airlines"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>

                {/* Flight Number */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Flight Number
                    </label>
                    <input
                        type="text"
                        value={data.flightNumber || ''}
                        onChange={(e) => onChange('flightNumber', e.target.value)}
                        placeholder="e.g., UA1234"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
            </div>


            {/* Departure Section */}
            <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Departure</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Departure Airport */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Airport
                        </label>
                        <input
                            type="text"
                            value={data.departureAirport || ''}
                            onChange={(e) => onChange('departureAirport', e.target.value)}
                            placeholder="e.g., JFK or New York"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        />
                    </div>

                    {/* Departure Time */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Departure Time
                        </label>
                        <input
                            type="datetime-local"
                            value={data.departureTime || ''}
                            onChange={(e) => onChange('departureTime', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        />
                    </div>
                </div>
            </div>


            {/* Arrival Section */}
            <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Arrival</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Arrival Airport */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Airport
                        </label>
                        <input
                            type="text"
                            value={data.arrivalAirport || ''}
                            onChange={(e) => onChange('arrivalAirport', e.target.value)}
                            placeholder="e.g., LAX or Los Angeles"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        />
                    </div>

                    {/* Arrival Time */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Arrival Time
                        </label>
                        <input
                            type="datetime-local"
                            value={data.arrivalTime || ''}
                            onChange={(e) => onChange('arrivalTime', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FlightsStep;
