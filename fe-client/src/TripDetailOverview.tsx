import {Trip} from "./Models.ts";
import {formatDate,formatTime} from "./utils/formatDate.ts"
import {getStatusColor} from "./utils/StatusColors.ts"

interface TimelineItem {
    type: 'flight' | 'accommodation' | 'activity';
    date: Date;
    title: string;
    subtitle: string;
    status: string;
    icon: string;
}

const TripDetailOverview = ({trip}: { trip: Trip }) => {


    // Combine all timeline items and sort by date
    const timelineItems: TimelineItem[] = [
        ...trip.flights.map(flight => ({
            type: 'flight' as const,
            date: flight.departure.time,
            title: `${flight.departure.city} → ${flight.arrival.city}`,
            subtitle: `${flight.airline} ${flight.flightNumber}`,
            status: flight.status,
            icon: '✈️',
        })),
        ...trip.accommodations.map(accommodation => ({
            type: 'accommodation' as const,
            date: accommodation.checkIn,
            title: accommodation.name,
            subtitle: `${accommodation.type.charAt(0).toUpperCase() + accommodation.type.slice(1)} • Check-in`,
            status: accommodation.status,
            icon: '🏨',
        })),
        ...trip.activities.map(activity => ({
            type: 'activity' as const,
            date: activity.date,
            title: activity.name,
            subtitle: activity.category,
            status: activity.status,
            icon: '📅',
        })),
    ].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h1 className="text-2xl font-bold mb-6">Trip Timeline</h1>

            <div className="relative">
                {/* Vertical line */}
                <div className="absolute left-[23px] top-8 bottom-8 w-0.5 bg-gray-200"/>

                <div className="space-y-6">
                    {timelineItems.map((item, index) => (
                        <div key={index} className="relative flex items-start gap-4">
                            {/* Icon */}
                            <div
                                className="flex-shrink-0 w-12 h-12 bg-white rounded-full flex items-center justify-center text-2xl border-2 border-gray-200 z-10">
                                {item.icon}
                            </div>

                            {/* Content */}
                            <div className="flex-1 flex items-center justify-between pt-2">
                                <div>
                                    <h3 className="font-semibold text-gray-900">{item.title}</h3>
                                    <p className="text-sm text-gray-600">{item.subtitle}</p>
                                </div>

                                <div className="text-right">
                                    <p className="text-sm text-gray-600 mb-1">
                                        {formatDate(item.date)} • {formatTime(item.date)}
                                    </p>
                                    <span
                                        className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                    {item.status}
                  </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TripDetailOverview;