import {useState} from "react";
import {Trip, AccommodationInput} from "../Models.ts";
import {formatDate} from "../utils/formatDate.ts";
import ChildStatusControl from "./ChildStatusControl.tsx";
import TripAccommodationForm from "./TripAccommodationForm.tsx";

interface Props {
    trip: Trip;
    editable?: boolean;
    onStatusChange?: (accommodationId: string, newStatus: string) => void | Promise<void>;
    onAccommodationAdd?: (accommodation: AccommodationInput) => void | Promise<void>;
}

const byCheckIn = (a: Trip["accommodations"][number], b: Trip["accommodations"][number]) =>
    new Date(a.checkIn).getTime() - new Date(b.checkIn).getTime();

const StaysOverview = ({trip, editable = true, onStatusChange, onAccommodationAdd}: Props) => {
    const [adding, setAdding] = useState(false);
    const [saving, setSaving] = useState(false);
    const [addError, setAddError] = useState<string | null>(null);
    const canAdd = editable && !!onAccommodationAdd;
    const accommodations = [...trip.accommodations].sort(byCheckIn);

    const openAddForm = () => {
        setAdding(true);
        setAddError(null);
    };

    const handleAdd = async (accommodation: AccommodationInput) => {
        setSaving(true);
        setAddError(null);
        try {
            await onAccommodationAdd?.(accommodation);
            setAdding(false);
        } catch (err) {
            setAddError(err instanceof Error ? err.message : "Failed to add accommodation");
        } finally {
            setSaving(false);
        }
    };

    const addButton = (
        <button
            type="button"
            onClick={openAddForm}
            className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
        >
            + Add accommodation
        </button>
    );

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Accommodations</h2>
                {canAdd && !adding && accommodations.length > 0 && addButton}
            </div>
            <div className="space-y-4">
                {adding && (
                    <div className="border border-blue-200 bg-blue-50/40 rounded-lg p-4">
                        <h3 className="font-semibold text-lg">New accommodation</h3>
                        <TripAccommodationForm
                            saving={saving}
                            error={addError}
                            onSave={handleAdd}
                            onCancel={() => {
                                setAdding(false);
                                setAddError(null);
                            }}
                        />
                    </div>
                )}
                {accommodations.length === 0 && !adding && (
                    <div className="text-center py-8 text-gray-500">
                        <p className="mb-3">No accommodations yet</p>
                        {canAdd && addButton}
                    </div>
                )}
                {accommodations.map((accommodation) => {
                    const cancelled = accommodation.status === 'cancelled';
                    return (
                    <div
                        key={accommodation.id}
                        className={`border border-gray-200 rounded-lg p-4 ${cancelled ? 'opacity-60' : ''}`}
                    >
                        <div className="flex justify-between items-start mb-2">
                            <div>
                                <h3 className="font-semibold text-lg">{accommodation.name}</h3>
                                <p className="text-sm text-gray-600 capitalize">{accommodation.type}</p>
                            </div>
                            <ChildStatusControl
                                childType="accommodation"
                                status={accommodation.status}
                                editable={editable && !!onStatusChange}
                                onSelect={(next) => onStatusChange?.(accommodation.id, next)}
                            />
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mt-3">
                            <div>
                                <p className="text-gray-500">Check-in</p>
                                <p className="font-medium">{formatDate(accommodation.checkIn)}</p>
                            </div>
                            <div>
                                <p className="text-gray-500">Check-out</p>
                                <p className="font-medium">{formatDate(accommodation.checkOut)}</p>
                            </div>
                            <div>
                                <p className="text-gray-500">Price/Night</p>
                                <p className="font-medium">${accommodation.pricePerNight}</p>
                            </div>
                            <div>
                                <p className="text-gray-500">Total</p>
                                <p className={`font-medium text-green-600 ${cancelled ? 'line-through' : ''}`}>${accommodation.totalPrice}</p>
                            </div>
                        </div>
                        <div className="mt-3">
                            <p className="text-sm text-gray-600">
                                ⭐ {accommodation.rating ?? '—'}
                                {accommodation.amenities.length > 0 && ` • ${accommodation.amenities.slice(0, 3).join(' • ')}`}
                            </p>
                        </div>
                    </div>
                    );
                })}
            </div>
        </div>
    )
}

export default StaysOverview;
