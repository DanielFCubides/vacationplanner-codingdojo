import {Trip} from "../Models.ts";

const TravellersOverview = ({trip}: { trip: Trip }) => {
    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold mb-4">Team Members</h2>
            <div className="space-y-3">
                {trip.travelers.map((traveler) => (
                    <div key={traveler.id}
                         className="flex items-center justify-between border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center gap-3">
                            <div
                                className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center font-semibold text-blue-600">
                                {traveler.avatar}
                            </div>
                            <div>
                                <p className="font-medium">{traveler.name}</p>
                                <p className="text-sm text-gray-600">{traveler.email}</p>
                            </div>
                        </div>
                        <span
                            className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium capitalize">
                    {traveler.role}
                  </span>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default TravellersOverview;