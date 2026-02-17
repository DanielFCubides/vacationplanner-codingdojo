import React from 'react';

interface OverviewStepProps {
    data: {
        name?: string;
        destination?: string;
        startDate?: string;
        endDate?: string;
    };
    onChange: (field: string, value: string) => void;
}

const OverviewStep: React.FC<OverviewStepProps> = ({ data, onChange }) => {
    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Trip Overview</h2>
            
            {/* Trip Name */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Trip Name
                </label>
                <input
                    type="text"
                    value={data.name || ''}
                    onChange={(e) => onChange('name', e.target.value)}
                    placeholder="e.g., Summer Vacation 2025"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            {/* Destination */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Destination
                </label>
                <input
                    type="text"
                    value={data.destination || ''}
                    onChange={(e) => onChange('destination', e.target.value)}
                    placeholder="e.g., Paris, France"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            {/* Start Date */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Date
                </label>
                <input
                    type="date"
                    value={data.startDate || ''}
                    onChange={(e) => onChange('startDate', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            {/* End Date */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Date
                </label>
                <input
                    type="date"
                    value={data.endDate || ''}
                    onChange={(e) => onChange('endDate', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>
        </div>
    );
};

export default OverviewStep;
