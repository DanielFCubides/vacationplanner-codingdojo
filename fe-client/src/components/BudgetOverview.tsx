import {Trip} from "../Models.ts";

const BudgetOverview = ({trip}: { trip: Trip }) => {
    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold mb-4">Budget Overview</h2>

        {/* Budget Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Total Budget</p>
                <p className="text-2xl font-bold text-blue-600">${trip.budget.total.toLocaleString()}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Spent</p>
                <p className="text-2xl font-bold text-green-600">${trip.budget.spent.toLocaleString()}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Remaining</p>
                <p className="text-2xl font-bold text-gray-600">
                    ${(trip.budget.total - trip.budget.spent).toLocaleString()}
                </p>
            </div>
        </div>

        {/* Budget Categories */}
        <h3 className="font-semibold mb-3">By Category</h3>
        <div className="space-y-3">
            {trip.budget.categories.map((category, index) => {
                const percentUsed = (category.spent / category.planned) * 100;
                return (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-center mb-2">
                            <span className="font-medium">{category.category}</span>
                            <span className="text-sm text-gray-600">
                        ${category.spent} / ${category.planned}
                      </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                                className={`h-2 rounded-full ${
                                    percentUsed > 100 ? 'bg-red-500' : 'bg-green-500'
                                }`}
                                style={{width: `${Math.min(percentUsed, 100)}%`}}
                            />
                        </div>
                    </div>
                );
            })}
        </div>
    </div>
    );
}

export default BudgetOverview;