import {Trip} from "./Models.ts";


const TripDetailOverview = ({trip}: Trip) => {

    const formatDate = (date: Date) => {
        return new Date(date).toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
        });
    };

    const formatTime = (date: Date) => {
        return new Date(date).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
        });
    };
    console.log("trip info: ", trip);
    const timelineItems = [
        ...trip.flights.map(flight => ({
            type: 'flight' as const,
            date: flight.departure.time,
            title: `${flight.departure.city} → ${flight.arrival.city}`,
            subtitle: `${flight.airline} ${flight.flightNumber}`,
            status: flight.status,
            icon: '✈️',
        }))
    ]

    return (
        <div className="space-y-6">
            <div className="bg-card rounded-lg shadow p-6 mb-6">
                Trip Timeline

                <div className="space-y-4">
                    {timelineItems.map((item, index) => (
                        <div key={index} className="flex items-start space-x-4">
                            <div className="flex-shrink-0">
                                <span className="text-2xl">{item.icon}</span>
                                <p className="font-medium text-foreground">{item.title}</p>
                                <p className="text-sm text-muted-foreground">{item.subtitle}</p>
                                <span className="text-sm text-muted-foreground">
                                {formatDate(item.date)} • {formatTime(item.date)}
                            </span>
                                <p className="text-sm text-foreground">{item.status}</p>

                            </div>
                        </div>
                    ))}
                </div>
            </div>


        </div>
    )
}


export default TripDetailOverview;