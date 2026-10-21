import {useState} from "react";
import {Trip, ActivityInput} from "../Models.ts";
import {formatDate} from "../utils/formatDate.ts";
import ChildStatusControl from "./ChildStatusControl.tsx";
import TripActivityForm from "./TripActivityForm.tsx";

interface Props {
    trip: Trip;
    editable?: boolean;
    onStatusChange?: (activityId: string, newStatus: string) => void | Promise<void>;
    onActivityAdd?: (activity: ActivityInput) => void | Promise<void>;
}

const byDate = (a: Trip["activities"][number], b: Trip["activities"][number]) =>
    new Date(a.date).getTime() - new Date(b.date).getTime();

const ActivitiesOverview = ({trip, editable = true, onStatusChange, onActivityAdd}: Props) => {
    const [adding, setAdding] = useState(false);
    const [saving, setSaving] = useState(false);
    const [addError, setAddError] = useState<string | null>(null);
    const canAdd = editable && !!onActivityAdd;
    const activities = [...trip.activities].sort(byDate);

    const openAddForm = () => {
        setAdding(true);
        setAddError(null);
    };

    const handleAdd = async (activity: ActivityInput) => {
        setSaving(true);
        setAddError(null);
        try {
            await onActivityAdd?.(activity);
            setAdding(false);
        } catch (err) {
            setAddError(err instanceof Error ? err.message : "Failed to add activity");
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
            + Add activity
        </button>
    );

    return (
        <div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Activities</h2>
                    {canAdd && !adding && activities.length > 0 && addButton}
                </div>
                <div className="space-y-4">
                    {adding && (
                        <div className="border border-blue-200 bg-blue-50/40 rounded-lg p-4">
                            <h3 className="font-semibold text-lg">New activity</h3>
                            <TripActivityForm
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
                    {activities.length === 0 && !adding && (
                        <div className="text-center py-8 text-gray-500">
                            <p className="mb-3">No activities yet</p>
                            {canAdd && addButton}
                        </div>
                    )}
                    {activities.map((activity) => {
                        const cancelled = activity.status === 'cancelled';
                        return (
                        <div
                            key={activity.id}
                            className={`border border-gray-200 rounded-lg p-4 ${cancelled ? 'opacity-60' : ''}`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <h3 className="font-semibold text-lg">{activity.name}</h3>
                                    <p className="text-sm text-gray-600">{activity.category}</p>
                                </div>
                                <ChildStatusControl
                                    childType="activity"
                                    status={activity.status}
                                    editable={editable && !!onStatusChange}
                                    onSelect={(next) => onStatusChange?.(activity.id, next)}
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-sm mt-3">
                                <div>
                                    <p className="text-gray-500">Date</p>
                                    <p className="font-medium">{formatDate(activity.date)}</p>
                                </div>
                                <div>
                                    <p className="text-gray-500">Cost</p>
                                    <p className={`font-medium text-green-600 ${cancelled ? 'line-through' : ''}`}>
                                        {activity.cost === 0 ? 'Free' : `$${activity.cost}`}
                                    </p>
                                </div>
                            </div>
                            <p className="text-sm text-gray-600 mt-2">{activity.description}</p>
                        </div>
                        );
                    })}
                </div>
            </div>
        </div>
    )
}

export default ActivitiesOverview;
