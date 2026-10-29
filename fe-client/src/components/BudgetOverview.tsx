import {useState} from "react";
import {BudgetInput, Trip} from "../Models.ts";
import {formatMoney} from "../utils/formatMoney.ts";
import TripBudgetForm from "./TripBudgetForm.tsx";

interface Props {
    trip: Trip;
    editable?: boolean;
    onBudgetUpdate?: (budget: BudgetInput) => void | Promise<void>;
}

const BudgetOverview = ({trip, editable = true, onBudgetUpdate}: Props) => {
    const [editing, setEditing] = useState(false);
    const [saving, setSaving] = useState(false);
    const [saveError, setSaveError] = useState<string | null>(null);
    const canEdit = editable && !!onBudgetUpdate;

    const {total, spent, categories} = trip.budget;
    const remaining = total - spent;
    const unallocated = total - categories.reduce((sum, c) => sum + c.planned, 0);
    const noBudget = total === 0 && categories.length === 0;

    const handleSave = async (budget: BudgetInput) => {
        setSaving(true);
        setSaveError(null);
        try {
            await onBudgetUpdate?.(budget);
            setEditing(false);
        } catch (err) {
            setSaveError(err instanceof Error ? err.message : "Failed to update budget");
        } finally {
            setSaving(false);
        }
    };

    const editButton = (
        <button
            type="button"
            onClick={() => {
                setEditing(true);
                setSaveError(null);
            }}
            className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
        >
            Edit budget
        </button>
    );

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Budget Overview</h2>
                {canEdit && !editing && !noBudget && editButton}
            </div>

            {editing ? (
                <TripBudgetForm
                    budget={trip.budget}
                    saving={saving}
                    error={saveError}
                    onSave={handleSave}
                    onCancel={() => {
                        setEditing(false);
                        setSaveError(null);
                    }}
                />
            ) : noBudget ? (
                <div className="text-center py-8 text-gray-500">
                    <p className="mb-1">No budget set</p>
                    {spent > 0 && <p className="text-sm mb-3">Spent so far: {formatMoney(spent)}</p>}
                    {canEdit && <div className="mt-3">{editButton}</div>}
                </div>
            ) : (
                <>
                    {/* Budget Summary */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div className="bg-blue-50 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">Budget total</p>
                            <p className="text-2xl font-bold text-blue-600">{formatMoney(total)}</p>
                        </div>
                        <div className="bg-green-50 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">Spent</p>
                            <p className="text-2xl font-bold text-green-600">{formatMoney(spent)}</p>
                            <p className="text-xs text-gray-500 mt-1">Confirmed and booked items</p>
                        </div>
                        <div className={`rounded-lg p-4 ${remaining < 0 ? "bg-red-50" : "bg-gray-50"}`}>
                            <p className="text-sm text-gray-600 mb-1">Remaining</p>
                            <p className={`text-2xl font-bold ${remaining < 0 ? "text-red-600" : "text-gray-600"}`}>
                                {formatMoney(remaining)}
                            </p>
                            {remaining < 0 && <p className="text-xs text-red-600 mt-1">Over budget</p>}
                        </div>
                    </div>

                    {/* Budget Categories */}
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="font-semibold">By Category</h3>
                        {categories.length > 0 && (
                            <span className={`text-sm ${unallocated < 0 ? "text-red-600" : "text-gray-600"}`}>
                                Unallocated: {formatMoney(unallocated)}
                            </span>
                        )}
                    </div>
                    {categories.length === 0 && (
                        <p className="text-sm text-gray-500">No Budget categories yet.</p>
                    )}
                    <div className="space-y-3">
                        {categories.map((category, index) => {
                            const percentUsed = category.planned > 0
                                ? (category.spent / category.planned) * 100
                                : null;
                            return (
                                <div key={index} className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium">{category.category}</span>
                                        <span className="text-sm text-gray-600">
                                            {formatMoney(category.spent)} / {formatMoney(category.planned)}
                                        </span>
                                    </div>
                                    {percentUsed === null ? (
                                        <p className="text-xs text-gray-400">—</p>
                                    ) : (
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full ${
                                                    percentUsed > 100 ? "bg-red-500" : "bg-green-500"
                                                }`}
                                                style={{width: `${Math.min(percentUsed, 100)}%`}}
                                            />
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                    {categories.length > 0 && (
                        <p className="text-xs text-gray-500 mt-3">
                            Category spent is recorded by hand and doesn't need to add up to Spent.
                        </p>
                    )}
                </>
            )}
        </div>
    );
};

export default BudgetOverview;
