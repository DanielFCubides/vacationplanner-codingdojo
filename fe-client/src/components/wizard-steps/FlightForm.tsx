import React from 'react';
import { FlightFormData } from '../../Models';

interface FlightFormProps {
    flight: FlightFormData;
    index: number;
    onChange: (index: number, field: keyof FlightFormData, value: string) => void;
    onRemove: (index: number) => void;
    canRemove: boolean;
}

// IATA airport codes are exactly three letters (e.g. JFK, BOG, CDG).
const IATA_PATTERN = /^[A-Z]{3}$/;

// Keep only letters, uppercase, and cap at 3 chars so the field can never
// hold a value the backend will reject (max_length=3).
const toIataCode = (value: string): string =>
    value.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 3);

export const isValidIata = (value: string): boolean => IATA_PATTERN.test(value);

const FlightForm: React.FC<FlightFormProps> = ({ flight, index, onChange, onRemove, canRemove }) => {
    const departureInvalid = flight.departureAirport.length > 0 && !isValidIata(flight.departureAirport);
    const arrivalInvalid = flight.arrivalAirport.length > 0 && !isValidIata(flight.arrivalAirport);

    return (
        <div className="border border-gray-200 rounded-xl p-5 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold text-gray-700">Flight {index + 1}</h3>
                {canRemove && (
                    <button
                        type="button"
                        onClick={() => onRemove(index)}
                        className="text-sm text-red-500 hover:text-red-700 font-medium"
                    >
                        Remove
                    </button>
                )}
            </div>

            {/* Airline and Flight Number */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Airline
                    </label>
                    <input
                        type="text"
                        value={flight.airline}
                        onChange={(e) => onChange(index, 'airline', e.target.value)}
                        placeholder="e.g., United Airlines"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Flight Number
                    </label>
                    <input
                        type="text"
                        value={flight.flightNumber}
                        onChange={(e) => onChange(index, 'flightNumber', e.target.value)}
                        placeholder="e.g., UA1234"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
            </div>

            {/* Departure */}
            <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="text-sm font-semibold text-gray-800 mb-3">Departure</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Airport (IATA code)
                        </label>
                        <input
                            type="text"
                            value={flight.departureAirport}
                            onChange={(e) => onChange(index, 'departureAirport', toIataCode(e.target.value))}
                            placeholder="e.g., JFK"
                            maxLength={3}
                            aria-invalid={departureInvalid}
                            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white uppercase ${
                                departureInvalid
                                    ? 'border-red-400 focus:ring-red-500'
                                    : 'border-gray-300 focus:ring-blue-500'
                            }`}
                        />
                        {departureInvalid && (
                            <p className="mt-1 text-xs text-red-600">Enter the 3-letter airport code (e.g., JFK).</p>
                        )}
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Departure Time
                        </label>
                        <input
                            type="datetime-local"
                            value={flight.departureTime}
                            onChange={(e) => onChange(index, 'departureTime', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        />
                    </div>
                </div>
            </div>

            {/* Arrival */}
            <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="text-sm font-semibold text-gray-800 mb-3">Arrival</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Airport (IATA code)
                        </label>
                        <input
                            type="text"
                            value={flight.arrivalAirport}
                            onChange={(e) => onChange(index, 'arrivalAirport', toIataCode(e.target.value))}
                            placeholder="e.g., LAX"
                            maxLength={3}
                            aria-invalid={arrivalInvalid}
                            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white uppercase ${
                                arrivalInvalid
                                    ? 'border-red-400 focus:ring-red-500'
                                    : 'border-gray-300 focus:ring-blue-500'
                            }`}
                        />
                        {arrivalInvalid && (
                            <p className="mt-1 text-xs text-red-600">Enter the 3-letter airport code (e.g., LAX).</p>
                        )}
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Arrival Time
                        </label>
                        <input
                            type="datetime-local"
                            value={flight.arrivalTime}
                            onChange={(e) => onChange(index, 'arrivalTime', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FlightForm;
