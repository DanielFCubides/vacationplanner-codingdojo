import React from 'react';

interface BudgetStepProps {
    data: {
        totalBudget?: string;
    };
    onChange: (field: string, value: any) => void;
}

const BudgetStep: React.FC<BudgetStepProps> = ({ data, onChange }) => {
    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Budget</h2>
            <p className="text-gray-600 mb-6">Set your total trip budget (optional)</p>
            
            {/* Total Budget */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Total Budget
                </label>
                <div className="relative">
                    <span className="absolute left-3 top-2 text-gray-500">$</span>
                    <input
                        type="number"
                        value={data.totalBudget || ''}
                        onChange={(e) => onChange('totalBudget', e.target.value)}
                        placeholder="0.00"
                        min="0"
                        step="0.01"
                        className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                    Enter the total amount you plan to spend on this trip
                </p>
            </div>
        </div>
    );
};

export default BudgetStep;
