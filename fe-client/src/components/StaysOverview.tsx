import {Trip} from "../Models.ts";
import {getStatusColor} from "../utils/StatusColors.ts";
import {formatDate} from "../utils/formatDate.ts";

const StaysOverview = ({trip}: { trip: Trip }) => {
    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold mb-4">Accommodations</h2>
            <div className="space-y-4">
                {trip.accommodations.map((accommodation) => (
                    <div key={accommodation.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                            <div>
                                <h3 className="font-semibold text-lg">{accommodation.name}</h3>
                                <p className="text-sm text-gray-600 capitalize">{accommodation.type}</p>
                            </div>
                            <span
                                className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(accommodation.status)}`}>
                      {accommodation.status}
                    </span>
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
                                <p className="font-medium text-green-600">${accommodation.totalPrice}</p>
                            </div>
                        </div>
                        <div className="mt-3">
                            <p className="text-sm text-gray-600">
                                ⭐ {accommodation.rating} • {accommodation.amenities.slice(0, 3).join(' • ')}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default StaysOverview;