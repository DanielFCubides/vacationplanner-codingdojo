import React from 'react';
import { FlightFormData } from '../../Models';
import FlightForm from './FlightForm';

const emptyFlight = (): FlightFormData => ({
    airline: '',
    flightNumber: '',
    departureAirport: '',
    departureTime: '',
    arrivalAirport: '',
    arrivalTime: '',
});

interface FlightsStepProps {
    data: FlightFormData[];
    onChange: (field: string, value: FlightFormData[]) => void;
}

const FlightsStep: React.FC<FlightsStepProps> = ({ data, onChange }) => {
    // Ensure we always have at least one flight entry to render
    const flights: FlightFormData[] = data && data.length > 0 ? data : [emptyFlight()];

    const handleFieldChange = (index: number, field: keyof FlightFormData, value: string) => {
        const updated = flights.map((flight, i) =>
            i === index ? { ...flight, [field]: value } : flight
        );
        onChange('flights', updated);
    };

    const handleAddFlight = () => {
        onChange('flights', [...flights, emptyFlight()]);
    };

    const handleRemoveFlight = (index: number) => {
        const updated = flights.filter((_, i) => i !== index);
        onChange('flights', updated);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Flights</h2>
                <p className="text-gray-600">Add your flight details (optional)</p>
            </div>

            {/* Flight forms */}
            <div className="space-y-4">
                {flights.map((flight, index) => (
                    <FlightForm
                        key={index}
                        flight={flight}
                        index={index}
                        onChange={handleFieldChange}
                        onRemove={handleRemoveFlight}
                        canRemove={flights.length > 1}
                    />
                ))}
            </div>

            {/* Add Flight button */}
            <button
                type="button"
                onClick={handleAddFlight}
                className="w-full py-3 border-2 border-dashed border-blue-300 rounded-xl text-blue-600 hover:border-blue-500 hover:bg-blue-50 font-medium transition-colors"
            >
                + Add Another Flight
            </button>
        </div>
    );
};

export default FlightsStep;
