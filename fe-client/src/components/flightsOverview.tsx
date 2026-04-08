import {Trip} from "../Models.ts";
import {getStatusColor} from "../utils/StatusColors.ts";
import {formatDate} from "../utils/formatDate.ts";

const TripFlightsOverview = ({trip}: { trip: Trip }) => {
    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold mb-4">Flights</h2>
            <div className="space-y-4">
                {trip.flights.map((flight) => (
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
                            <span
                                className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(flight.status)}`}>
                      {flight.status}
                    </span>
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
                    </div>
                ))}
            </div>
        </div>
    );
}

export default TripFlightsOverview;