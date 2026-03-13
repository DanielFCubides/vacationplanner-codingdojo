import {Trip} from "../Models.ts";
import {getStatusColor} from "../utils/StatusColors.ts";
import {formatDate} from "../utils/formatDate.ts";

const ActivitiesOverview = ({trip}: { trip: Trip }) => {
    return (
        <div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-bold mb-4">Activities</h2>
                <div className="space-y-4">
                    {trip.activities.map((activity) => (
                        <div key={activity.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <h3 className="font-semibold text-lg">{activity.name}</h3>
                                    <p className="text-sm text-gray-600">{activity.category}</p>
                                </div>
                                <span
                                    className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(activity.status)}`}>
                      {activity.status}
                    </span>
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-sm mt-3">
                                <div>
                                    <p className="text-gray-500">Date</p>
                                    <p className="font-medium">{formatDate(activity.date)}</p>
                                </div>
                                <div>
                                    <p className="text-gray-500">Cost</p>
                                    <p className="font-medium text-green-600">${activity.cost}</p>
                                </div>
                            </div>
                            <p className="text-sm text-gray-600 mt-2">{activity.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default ActivitiesOverview;