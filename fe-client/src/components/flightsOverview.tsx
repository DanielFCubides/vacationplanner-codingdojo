import { useState } from "react";
import { Flight, Trip } from "../Models.ts";
import { getStatusColor } from "../utils/StatusColors.ts";
import { formatDate } from "../utils/formatDate.ts";

interface TripFlightsOverviewProps {
    trip: Trip;
    onFlightUpdate?: (updatedFlight: Flight) => Promise<void>;
}

type FlightStatus = Flight["status"];

const toDateTimeLocal = (value: Date | string): string => {
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return "";
    // YYYY-MM-DDTHH:mm for <input type="datetime-local" />
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const TripFlightsOverview = ({ trip, onFlightUpdate }: TripFlightsOverviewProps) => {
    const [editingFlightId, setEditingFlightId] = useState<string | null>(null);
    const [draft, setDraft] = useState<Flight | null>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [errorByFlight, setErrorByFlight] = useState<Record<string, string>>({});

    const startEdit = (flight: Flight) => {
        setEditingFlightId(flight.id);
        setDraft({ ...flight, departure: { ...flight.departure }, arrival: { ...flight.arrival } });
        setErrorByFlight((prev) => {
            const next = { ...prev };
            delete next[flight.id];
            return next;
        });
    };

    const cancelEdit = () => {
        setEditingFlightId(null);
        setDraft(null);
    };

    const handleSave = async () => {
        if (!draft || !onFlightUpdate) return;
        setIsSaving(true);
        setErrorByFlight((prev) => {
            const next = { ...prev };
            delete next[draft.id];
            return next;
        });
        try {
            await onFlightUpdate(draft);
            setEditingFlightId(null);
            setDraft(null);
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to update flight";
            setErrorByFlight((prev) => ({ ...prev, [draft.id]: message }));
        } finally {
            setIsSaving(false);
        }
    };

    const updateDraft = (patch: Partial<Flight>) => {
        setDraft((prev) => (prev ? { ...prev, ...patch } : prev));
    };

    const updateDeparture = (patch: Partial<Flight["departure"]>) => {
        setDraft((prev) => (prev ? { ...prev, departure: { ...prev.departure, ...patch } } : prev));
    };

    const updateArrival = (patch: Partial<Flight["arrival"]>) => {
        setDraft((prev) => (prev ? { ...prev, arrival: { ...prev.arrival, ...patch } } : prev));
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold mb-4">Flights</h2>
            <div className="space-y-4">
                {trip.flights.map((flight) => {
                    const isEditing = editingFlightId === flight.id && draft !== null;
                    const errorMessage = errorByFlight[flight.id];

                    if (isEditing && draft) {
                        return (
                            <div key={flight.id} className="border border-blue-200 bg-blue-50/30 rounded-lg p-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    <label className="text-sm">
                                        <span className="block text-gray-600 mb-1">Airline</span>
                                        <input
                                            type="text"
                                            value={draft.airline}
                                            onChange={(e) => updateDraft({ airline: e.target.value })}
                                            className="w-full border border-gray-300 rounded px-2 py-1"
                                        />
                                    </label>
                                    <label className="text-sm">
                                        <span className="block text-gray-600 mb-1">Flight Number</span>
                                        <input
                                            type="text"
                                            value={draft.flightNumber}
                                            onChange={(e) => updateDraft({ flightNumber: e.target.value })}
                                            className="w-full border border-gray-300 rounded px-2 py-1"
                                        />
                                    </label>

                                    <fieldset className="border border-gray-200 rounded p-3 md:col-span-1">
                                        <legend className="text-xs text-gray-500 px-1">Departure</legend>
                                        <label className="text-sm block mb-2">
                                            <span className="block text-gray-600 mb-1">Airport (IATA)</span>
                                            <input
                                                type="text"
                                                maxLength={3}
                                                value={draft.departure.airport}
                                                onChange={(e) => updateDeparture({ airport: e.target.value.toUpperCase() })}
                                                className="w-full border border-gray-300 rounded px-2 py-1 uppercase"
                                            />
                                        </label>
                                        <label className="text-sm block mb-2">
                                            <span className="block text-gray-600 mb-1">City</span>
                                            <input
                                                type="text"
                                                value={draft.departure.city}
                                                onChange={(e) => updateDeparture({ city: e.target.value })}
                                                className="w-full border border-gray-300 rounded px-2 py-1"
                                            />
                                        </label>
                                        <label className="text-sm block">
                                            <span className="block text-gray-600 mb-1">Time</span>
                                            <input
                                                type="datetime-local"
                                                value={toDateTimeLocal(draft.departure.time)}
                                                onChange={(e) => updateDeparture({ time: new Date(e.target.value) })}
                                                className="w-full border border-gray-300 rounded px-2 py-1"
                                            />
                                        </label>
                                    </fieldset>

                                    <fieldset className="border border-gray-200 rounded p-3 md:col-span-1">
                                        <legend className="text-xs text-gray-500 px-1">Arrival</legend>
                                        <label className="text-sm block mb-2">
                                            <span className="block text-gray-600 mb-1">Airport (IATA)</span>
                                            <input
                                                type="text"
                                                maxLength={3}
                                                value={draft.arrival.airport}
                                                onChange={(e) => updateArrival({ airport: e.target.value.toUpperCase() })}
                                                className="w-full border border-gray-300 rounded px-2 py-1 uppercase"
                                            />
                                        </label>
                                        <label className="text-sm block mb-2">
                                            <span className="block text-gray-600 mb-1">City</span>
                                            <input
                                                type="text"
                                                value={draft.arrival.city}
                                                onChange={(e) => updateArrival({ city: e.target.value })}
                                                className="w-full border border-gray-300 rounded px-2 py-1"
                                            />
                                        </label>
                                        <label className="text-sm block">
                                            <span className="block text-gray-600 mb-1">Time</span>
                                            <input
                                                type="datetime-local"
                                                value={toDateTimeLocal(draft.arrival.time)}
                                                onChange={(e) => updateArrival({ time: new Date(e.target.value) })}
                                                className="w-full border border-gray-300 rounded px-2 py-1"
                                            />
                                        </label>
                                    </fieldset>

                                    <label className="text-sm">
                                        <span className="block text-gray-600 mb-1">Duration</span>
                                        <input
                                            type="text"
                                            value={draft.duration}
                                            onChange={(e) => updateDraft({ duration: e.target.value })}
                                            placeholder="2h 30m"
                                            className="w-full border border-gray-300 rounded px-2 py-1"
                                        />
                                    </label>
                                    <label className="text-sm">
                                        <span className="block text-gray-600 mb-1">Stops</span>
                                        <input
                                            type="number"
                                            min={0}
                                            value={draft.stops}
                                            onChange={(e) => updateDraft({ stops: Number(e.target.value) })}
                                            className="w-full border border-gray-300 rounded px-2 py-1"
                                        />
                                    </label>
                                    <label className="text-sm">
                                        <span className="block text-gray-600 mb-1">Price (USD)</span>
                                        <input
                                            type="number"
                                            min={0}
                                            step="0.01"
                                            value={draft.price}
                                            onChange={(e) => updateDraft({ price: Number(e.target.value) })}
                                            className="w-full border border-gray-300 rounded px-2 py-1"
                                        />
                                    </label>
                                    <label className="text-sm">
                                        <span className="block text-gray-600 mb-1">Cabin Class</span>
                                        <input
                                            type="text"
                                            value={draft.cabinClass}
                                            onChange={(e) => updateDraft({ cabinClass: e.target.value })}
                                            className="w-full border border-gray-300 rounded px-2 py-1"
                                        />
                                    </label>
                                    <label className="text-sm">
                                        <span className="block text-gray-600 mb-1">Status</span>
                                        <select
                                            value={draft.status}
                                            onChange={(e) => updateDraft({ status: e.target.value as FlightStatus })}
                                            className="w-full border border-gray-300 rounded px-2 py-1 capitalize"
                                        >
                                            <option value="confirmed">Confirmed</option>
                                            <option value="pending">Pending</option>
                                            <option value="cancelled">Cancelled</option>
                                        </select>
                                    </label>
                                </div>

                                {errorMessage && (
                                    <p className="text-sm text-red-600 mt-3">{errorMessage}</p>
                                )}

                                <div className="flex justify-end gap-2 mt-4">
                                    <button
                                        type="button"
                                        onClick={cancelEdit}
                                        disabled={isSaving}
                                        className="px-3 py-1 rounded border border-gray-300 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="button"
                                        onClick={handleSave}
                                        disabled={isSaving}
                                        className="px-3 py-1 rounded bg-blue-600 text-white text-sm hover:bg-blue-700 disabled:opacity-50"
                                    >
                                        {isSaving ? "Saving…" : "Save"}
                                    </button>
                                </div>
                            </div>
                        );
                    }

                    return (
                        <div key={flight.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <h3 className="font-semibold text-lg">
                                        {flight.departure.city} → {flight.arrival.city}
                                    </h3>
                                    <p className="text-sm text-gray-600">
                                        {flight.airline} {flight.flightNumber}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span
                                        className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(flight.status)}`}>
                                        {flight.status}
                                    </span>
                                    {onFlightUpdate && (
                                        <button
                                            type="button"
                                            onClick={() => startEdit(flight)}
                                            aria-label="Edit flight"
                                            title="Edit flight"
                                            className="p-1.5 rounded text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors"
                                        >
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                viewBox="0 0 24 24"
                                                fill="none"
                                                stroke="currentColor"
                                                strokeWidth="2"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                className="w-4 h-4"
                                            >
                                                <path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                                                <path d="m15 5 4 4" />
                                            </svg>
                                        </button>
                                    )}
                                </div>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mt-3">
                                <div>
                                    <p className="text-gray-500">Departure</p>
                                    <p className="font-medium">{formatDate(flight.departure.time)}</p>
                                    <p className="text-xs text-gray-600">{flight.departure.airport}</p>
                                </div>
                                <div>
                                    <p className="text-gray-500">Arrival</p>
                                    <p className="font-medium">{formatDate(flight.arrival.time)}</p>
                                    <p className="text-xs text-gray-600">{flight.arrival.airport}</p>
                                </div>
                                <div>
                                    <p className="text-gray-500">Duration</p>
                                    <p className="font-medium">{flight.duration}</p>
                                    <p className="text-xs text-gray-600">{flight.stops} stop{flight.stops !== 1 ? 's' : ''}</p>
                                </div>
                                <div>
                                    <p className="text-gray-500">Price</p>
                                    <p className="font-medium text-green-600">${flight.price}</p>
                                    <p className="text-xs text-gray-600">{flight.cabinClass}</p>
                                </div>
                            </div>
                            {errorMessage && (
                                <p className="text-sm text-red-600 mt-3">{errorMessage}</p>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default TripFlightsOverview;
