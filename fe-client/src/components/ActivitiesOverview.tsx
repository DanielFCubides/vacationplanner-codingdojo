import {Trip} from "../Models.ts";
import {formatDate} from "../utils/formatDate.ts";
import ChildStatusControl from "./ChildStatusControl.tsx";

interface Props {
    trip: Trip;
    editable?: boolean;
    onStatusChange?: (activityId: string, newStatus: string) => void | Promise<void>;
}

const ActivitiesOverview = ({trip, editable = true, onStatusChange}: Props) => {
    return (
        <div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-bold mb-4">Activities</h2>
                <div className="space-y-4">
                    {trip.activities.map((activity) => {
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
                                    <p className={`font-medium text-green-600 ${cancelled ? 'line-through' : ''}`}>${activity.cost}</p>
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
