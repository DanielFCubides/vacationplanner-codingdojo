import React from 'react';

interface ActivitiesStepProps {
    data: {
        name?: string;
        date?: string;
        category?: string;
        cost?: string;
    };
    onChange: (field: string, value: any) => void;
}

const ActivitiesStep: React.FC<ActivitiesStepProps> = ({ data, onChange }) => {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Activities</h2>
                <p className="text-gray-600">Add activities and experiences (optional)</p>
            </div>

            {/* Activity Name */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Activity Name
                </label>
                <input
                    type="text"
                    value={data.name || ''}
                    onChange={(e) => onChange('name', e.target.value)}
                    placeholder="e.g., City Walking Tour, Museum Visit"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            {/* Date and Category Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Date */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Date
                    </label>
                    <input
                        type="date"
                        value={data.date || ''}
                        onChange={(e) => onChange('date', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>

                {/* Category Dropdown */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Category
                    </label>
                    <select
                        value={data.category || ''}
                        onChange={(e) => onChange('category', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="">Select category...</option>
                        <option value="Sightseeing">Sightseeing</option>
                        <option value="Adventure">Adventure</option>
                        <option value="Food & Dining">Food & Dining</option>
                        <option value="Entertainment">Entertainment</option>
                        <option value="Relaxation">Relaxation</option>
                        <option value="Shopping">Shopping</option>
                    </select>
                </div>
            </div>


            {/* Cost Section */}
            <div className="bg-orange-50 p-4 rounded-lg">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Cost
                    </label>
                    <div className="relative max-w-xs">
                        <span className="absolute left-3 top-2 text-gray-500">$</span>
                        <input
                            type="number"
                            value={data.cost || ''}
                            onChange={(e) => onChange('cost', e.target.value)}
                            placeholder="0.00"
                            min="0"
                            step="0.01"
                            className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                        Enter the cost for this activity
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ActivitiesStep;
