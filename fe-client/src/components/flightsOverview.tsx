import {useState} from "react";
import {Trip, Flight} from "../Models.ts";
import {formatDate} from "../utils/formatDate.ts";
import ChildStatusControl from "./ChildStatusControl.tsx";
import FlightEditForm from "./FlightEditForm.tsx";

interface Props {
    trip: Trip;
    editable?: boolean;
    onStatusChange?: (flightId: string, newStatus: string) => void | Promise<void>;
    onFlightUpdate?: (flightId: string, updates: Partial<Flight>) => void | Promise<void>;
}

const TripFlightsOverview = ({trip, editable = true, onStatusChange, onFlightUpdate}: Props) => {
    const [editingId, setEditingId] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);
    const [editError, setEditError] = useState<string | null>(null);
    const canEdit = editable && !!onFlightUpdate;

    const handleSave = async (flightId: string, updates: Partial<Flight>) => {
        setSaving(true);
        setEditError(null);
        try {
            await onFlightUpdate?.(flightId, updates);
            setEditingId(null);
        } catch (err) {
            setEditError(err instanceof Error ? err.message : "Failed to update flight");
        } finally {
            setSaving(false);
        }
    };
    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold mb-4">Flights</h2>
            <div className="space-y-4">
                {trip.flights.map((flight) => {
                    const cancelled = flight.status === 'cancelled';
                    const isEditing = editingId === flight.id;
                    return (
                    <div
                        key={flight.id}
                        className={`border border-gray-200 rounded-lg p-4 ${cancelled ? 'opacity-60' : ''}`}
                    >
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
                                {canEdit && !isEditing && (
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setEditingId(flight.id);
                                            setEditError(null);
                                        }}
                                        className="text-sm text-blue-600 hover:underline"
                                    >
                                        Edit
                                    </button>
                                )}
                                <ChildStatusControl
                                    childType="flight"
                                    status={flight.status}
                                    editable={editable && !!onStatusChange}
                                    onSelect={(next) => onStatusChange?.(flight.id, next)}
                                />
                            </div>
                        </div>
                        {isEditing ? (
                            <FlightEditForm
                                flight={flight}
                                saving={saving}
                                error={editError}
                                onSave={(updates) => handleSave(flight.id, updates)}
                                onCancel={() => {
                                    setEditingId(null);
                                    setEditError(null);
                                }}
                            />
                        ) : (
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
                                <p className={`font-medium text-green-600 ${cancelled ? 'line-through' : ''}`}>${flight.price}</p>
                                <p className="text-xs text-gray-600">{flight.cabinClass}</p>
                            </div>
                        </div>
                        )}
                    </div>
                    );
                })}
            </div>
        </div>
    );
}

export default TripFlightsOverview;
