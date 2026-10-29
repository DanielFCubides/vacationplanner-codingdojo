import {useState} from "react";
import {ActivityInput} from "../Models.ts";

interface Props {
    saving: boolean;
    error: string | null;
    onSave: (values: ActivityInput) => void;
    onCancel: () => void;
}

// Same Activity categories the new trip wizard offers.
const ACTIVITY_CATEGORIES = [
    "Sightseeing",
    "Adventure",
    "Food & Dining",
    "Entertainment",
    "Relaxation",
    "Shopping",
];

const inputClass = "w-full border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";
const labelClass = "block text-xs text-gray-500 mb-1";

const TripActivityForm = ({saving, error, onSave, onCancel}: Props) => {
    const [name, setName] = useState("");
    const [date, setDate] = useState("");
    const [category, setCategory] = useState(ACTIVITY_CATEGORIES[0]);
    const [cost, setCost] = useState("0");
    const [description, setDescription] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave({
            name,
            date,
            category,
            cost: Number(cost),
            description,
        });
    };

    return (
        <form onSubmit={handleSubmit} className="mt-3 space-y-3 border-t border-gray-200 pt-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                    <label className={labelClass}>Name</label>
                    <input className={inputClass} value={name} placeholder="e.g. Louvre tour"
                           onChange={(e) => setName(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Category</label>
                    <select className={inputClass} value={category}
                            onChange={(e) => setCategory(e.target.value)}>
                        {ACTIVITY_CATEGORIES.map((c) => (
                            <option key={c} value={c}>{c}</option>
                        ))}
                    </select>
                </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                    <label className={labelClass}>Date</label>
                    <input type="date" className={inputClass} value={date}
                           onChange={(e) => setDate(e.target.value)} required/>
                </div>
                <div>
                    <label className={labelClass}>Cost (USD, 0 if free)</label>
                    <input type="number" min={0} step="0.01" className={inputClass} value={cost}
                           onChange={(e) => setCost(e.target.value)} required/>
                </div>
            </div>
            <div>
                <label className={labelClass}>Description (optional)</label>
                <input className={inputClass} value={description}
                       onChange={(e) => setDescription(e.target.value)}/>
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

export default TripActivityForm;
