import {useState} from "react";
import {Flight} from "../Models.ts";

interface Props {
    flight: Flight;
    saving: boolean;
    error: string | null;
    onSave: (updates: Partial<Flight>) => void;
    onCancel: () => void;
}

const toInputValue = (time: Date | string): string => {
    const d = new Date(time);
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const toIso = (value: string): string => new Date(value).toISOString();

const inputClass = "w-full border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";
const labelClass = "block text-xs text-gray-500 mb-1";

const FlightEditForm = ({flight, saving, error, onSave, onCancel}: Props) => {
    const [airline, setAirline] = useState(flight.airline);
    const [flightNumber, setFlightNumber] = useState(flight.flightNumber);
    const [departureAirport, setDepartureAirport] = useState(flight.departure.airport);
    const [departureCity, setDepartureCity] = useState(flight.departure.city);
    const [departureTime, setDepartureTime] = useState(toInputValue(flight.departure.time));
    const [arrivalAirport, setArrivalAirport] = useState(flight.arrival.airport);
    const [arrivalCity, setArrivalCity] = useState(flight.arrival.city);
    const [arrivalTime, setArrivalTime] = useState(toInputValue(flight.arrival.time));
    const [duration, setDuration] = useState(flight.duration);
    const [stops, setStops] = useState(String(flight.stops));
    const [price, setPrice] = useState(String(flight.price));
    const [cabinClass, setCabinClass] = useState(flight.cabinClass);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave({
            airline,
            flightNumber,
            departure: {
                airport: departureAirport.toUpperCase(),
                city: departureCity,
                time: toIso(departureTime),
            },
            arrival: {
                airport: arrivalAirport.toUpperCase(),
                city: arrivalCity,
                time: toIso(arrivalTime),
            },
            duration,
            stops: Number(stops),
            price: Number(price),
            cabinClass,
        });
    };

    return (
        <form onSubmit={handleSubmit} className="mt-3 space-y-3 border-t border-gray-200 pt-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                    <label className={labelClass}>Airline</label>
                    <input className={inputClass} value={airline}
                           onChange={(e) => setAirline(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Flight number</label>
                    <input className={inputClass} value={flightNumber}
                           onChange={(e) => setFlightNumber(e.target.value)} required/>
                </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                    <label className={labelClass}>Departure airport</label>
                    <input className={inputClass} value={departureAirport} maxLength={3}
                           onChange={(e) => setDepartureAirport(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Departure city</label>
                    <input className={inputClass} value={departureCity}
                           onChange={(e) => setDepartureCity(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Departure time</label>
                    <input type="datetime-local" className={inputClass} value={departureTime}
                           onChange={(e) => setDepartureTime(e.target.value)} required/>
                </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                    <label className={labelClass}>Arrival airport</label>
                    <input className={inputClass} value={arrivalAirport} maxLength={3}
                           onChange={(e) => setArrivalAirport(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Arrival city</label>
                    <input className={inputClass} value={arrivalCity}
                           onChange={(e) => setArrivalCity(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Arrival time</label>
                    <input type="datetime-local" className={inputClass} value={arrivalTime}
                           onChange={(e) => setArrivalTime(e.target.value)} required/>
                </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div>
                    <label className={labelClass}>Duration</label>
                    <input className={inputClass} value={duration}
                           onChange={(e) => setDuration(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Stops</label>
                    <input type="number" min={0} className={inputClass} value={stops}
                           onChange={(e) => setStops(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Price (USD)</label>
                    <input type="number" min={0} step="0.01" className={inputClass} value={price}
                           onChange={(e) => setPrice(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Cabin class</label>
                    <select className={inputClass} value={cabinClass}
                            onChange={(e) => setCabinClass(e.target.value)}>
                        <option value="Economy">Economy</option>
                        <option value="Business">Business</option>
                        <option value="First">First</option>
                    </select>
                </div>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <div className="flex gap-2">
                <button type="submit" disabled={saving}
                        className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50">
                    {saving ? "Saving…" : "Save"}
                </button>
                <button type="button" onClick={onCancel} disabled={saving}
                        className="px-3 py-1.5 bg-gray-200 text-gray-700 text-sm rounded-md hover:bg-gray-300 disabled:opacity-50">
                    Cancel
                </button>
            </div>
        </form>
    );
};

export default FlightEditForm;
