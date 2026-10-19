import {useState} from "react";
import {Accommodation, AccommodationInput} from "../Models.ts";

interface Props {
    saving: boolean;
    error: string | null;
    onSave: (values: AccommodationInput) => void;
    onCancel: () => void;
}

const ACCOMMODATION_TYPES: Accommodation["type"][] = ["hotel", "airbnb", "hostel", "resort"];

const MS_PER_DAY = 24 * 60 * 60 * 1000;

const nightsBetween = (checkIn: string, checkOut: string): number => {
    if (!checkIn || !checkOut) return 0;
    return Math.round((new Date(checkOut).getTime() - new Date(checkIn).getTime()) / MS_PER_DAY);
};

const inputClass = "w-full border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";
const labelClass = "block text-xs text-gray-500 mb-1";

const TripAccommodationForm = ({saving, error, onSave, onCancel}: Props) => {
    const [name, setName] = useState("");
    const [type, setType] = useState<Accommodation["type"]>("hotel");
    const [checkIn, setCheckIn] = useState("");
    const [checkOut, setCheckOut] = useState("");
    const [pricePerNight, setPricePerNight] = useState("");
    const [totalPrice, setTotalPrice] = useState("");
    // Once the user types a total (fees, taxes), stop prefilling it.
    const [totalEdited, setTotalEdited] = useState(false);
    const [rating, setRating] = useState("");
    const [amenities, setAmenities] = useState("");
    const [validationError, setValidationError] = useState<string | null>(null);

    const nights = nightsBetween(checkIn, checkOut);

    const prefillTotal = (nextCheckIn: string, nextCheckOut: string, nextRate: string) => {
        if (totalEdited) return;
        const n = nightsBetween(nextCheckIn, nextCheckOut);
        const rate = Number(nextRate);
        setTotalPrice(n > 0 && rate > 0 ? (n * rate).toFixed(2) : "");
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (nights <= 0) {
            setValidationError("Check-out must be after check-in.");
            return;
        }
        setValidationError(null);
        onSave({
            name,
            type,
            checkIn,
            checkOut,
            pricePerNight: Number(pricePerNight),
            totalPrice: Number(totalPrice),
            rating: rating === "" ? null : Number(rating),
            amenities: amenities.split(",").map((a) => a.trim()).filter(Boolean),
        });
    };

    return (
        <form onSubmit={handleSubmit} className="mt-3 space-y-3 border-t border-gray-200 pt-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                    <label className={labelClass}>Name</label>
                    <input className={inputClass} value={name} placeholder="e.g. Hilton Downtown"
                           onChange={(e) => setName(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Type</label>
                    <select className={`${inputClass} capitalize`} value={type}
                            onChange={(e) => setType(e.target.value as Accommodation["type"])}>
                        {ACCOMMODATION_TYPES.map((t) => (
                            <option key={t} value={t}>{t}</option>
                        ))}
                    </select>
                </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                    <label className={labelClass}>Check-in</label>
                    <input type="date" className={inputClass} value={checkIn}
                           onChange={(e) => {
                               setCheckIn(e.target.value);
                               prefillTotal(e.target.value, checkOut, pricePerNight);
                           }} required/>
                </div>
                <div>
                    <label className={labelClass}>Check-out</label>
                    <input type="date" className={inputClass} value={checkOut} min={checkIn || undefined}
                           onChange={(e) => {
                               setCheckOut(e.target.value);
                               prefillTotal(checkIn, e.target.value, pricePerNight);
                           }} required/>
                </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div>
                    <label className={labelClass}>Price/Night (USD)</label>
                    <input type="number" min={0.01} step="0.01" className={inputClass} value={pricePerNight}
                           onChange={(e) => {
                               setPricePerNight(e.target.value);
                               prefillTotal(checkIn, checkOut, e.target.value);
                           }} required/>
                </div>
                <div>
                    <label className={labelClass}>
                        Total (USD){nights > 0 && ` · ${nights} night${nights !== 1 ? "s" : ""}`}
                    </label>
                    <input type="number" min={0.01} step="0.01" className={inputClass} value={totalPrice}
                           onChange={(e) => {
                               setTotalPrice(e.target.value);
                               setTotalEdited(true);
                           }} required/>
                </div>
                <div>
                    <label className={labelClass}>Rating (optional)</label>
                    <input type="number" min={0} max={5} step="0.1" className={inputClass} value={rating}
                           onChange={(e) => setRating(e.target.value)}/>
                </div>
                <div>
                    <label className={labelClass}>Amenities (optional)</label>
                    <input className={inputClass} value={amenities} placeholder="WiFi, Pool, Breakfast"
                           onChange={(e) => setAmenities(e.target.value)}/>
                </div>
            </div>
            {(validationError || error) && (
                <p className="text-sm text-red-600">{validationError || error}</p>
            )}
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

export default TripAccommodationForm;
