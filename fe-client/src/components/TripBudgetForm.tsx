import {useState} from "react";
import {BudgetInput, Trip} from "../Models.ts";
import {formatMoney} from "../utils/formatMoney.ts";

interface Props {
    budget: Trip["budget"];
    saving: boolean;
    error: string | null;
    onSave: (values: BudgetInput) => void;
    onCancel: () => void;
}

interface CategoryRow {
    key: number;
    category: string;
    planned: string;
    spent: string;
}

const inputClass = "w-full border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";
const labelClass = "block text-xs text-gray-500 mb-1";

const TripBudgetForm = ({budget, saving, error, onSave, onCancel}: Props) => {
    const [total, setTotal] = useState(String(budget.total));
    const [rows, setRows] = useState<CategoryRow[]>(
        budget.categories.map((c, i) => ({
            key: i,
            category: c.category,
            planned: String(c.planned),
            spent: String(c.spent),
        }))
    );
    const [nextKey, setNextKey] = useState(budget.categories.length);
    const [validationError, setValidationError] = useState<string | null>(null);

    const unallocated = Number(total || 0) - rows.reduce((sum, r) => sum + Number(r.planned || 0), 0);

    const updateRow = (key: number, field: keyof Omit<CategoryRow, "key">, value: string) =>
        setRows(rows.map((r) => (r.key === key ? {...r, [field]: value} : r)));

    const addRow = () => {
        setRows([...rows, {key: nextKey, category: "", planned: "0", spent: "0"}]);
        setNextKey(nextKey + 1);
    };

    const removeRow = (key: number) => setRows(rows.filter((r) => r.key !== key));

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const names = rows.map((r) => r.category.trim().toLowerCase());
        const duplicate = names.find((n, i) => names.indexOf(n) !== i);
        if (duplicate !== undefined) {
            setValidationError(`Budget category names must be unique ("${duplicate}").`);
            return;
        }
        setValidationError(null);
        onSave({
            total: Number(total),
            categories: rows.map((r) => ({
                category: r.category.trim(),
                planned: Number(r.planned),
                spent: Number(r.spent),
            })),
        });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="md:w-1/3">
                <label className={labelClass}>Budget total (USD, 0 = no budget)</label>
                <input type="number" min={0} step="0.01" className={inputClass} value={total}
                       onChange={(e) => setTotal(e.target.value)} required/>
            </div>

            <div>
                <div className="flex justify-between items-center mb-2">
                    <h3 className="font-semibold">Budget categories</h3>
                    <span className={`text-sm ${unallocated < 0 ? "text-red-600" : "text-gray-600"}`}>
                        Unallocated: {formatMoney(unallocated)}
                    </span>
                </div>
                <div className="space-y-2">
                    {rows.map((row) => (
                        <div key={row.key} className="grid grid-cols-[1fr_7rem_7rem_auto] gap-2 items-end">
                            <div>
                                <label className={labelClass}>Name</label>
                                <input className={inputClass} value={row.category} placeholder="e.g. Food"
                                       onChange={(e) => updateRow(row.key, "category", e.target.value)}
                                       required/>
                            </div>
                            <div>
                                <label className={labelClass}>Planned</label>
                                <input type="number" min={0} step="0.01" className={inputClass}
                                       value={row.planned}
                                       onChange={(e) => updateRow(row.key, "planned", e.target.value)}
                                       required/>
                            </div>
                            <div>
                                <label className={labelClass}>Category spent</label>
                                <input type="number" min={0} step="0.01" className={inputClass}
                                       value={row.spent}
                                       onChange={(e) => updateRow(row.key, "spent", e.target.value)}
                                       required/>
                            </div>
                            <button type="button" onClick={() => removeRow(row.key)}
                                    aria-label={`Remove ${row.category || "category"}`}
                                    className="px-2 py-1.5 text-gray-500 hover:text-red-600">
                                ✕
                            </button>
                        </div>
                    ))}
                    {rows.length === 0 && (
                        <p className="text-sm text-gray-500">No Budget categories.</p>
                    )}
                </div>
                <button type="button" onClick={addRow}
                        className="mt-2 text-sm text-blue-600 hover:text-blue-800">
                    + Add category
                </button>
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

export default TripBudgetForm;
