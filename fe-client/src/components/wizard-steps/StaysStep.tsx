import React from 'react';

interface StaysStepProps {
    data: {
        name?: string;
        type?: string;
        checkIn?: string;
        checkOut?: string;
        pricePerNight?: string;
    };
    onChange: (field: string, value: any) => void;
}

const StaysStep: React.FC<StaysStepProps> = ({ data, onChange }) => {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Accommodations</h2>
                <p className="text-gray-600">Add your accommodation details (optional)</p>
            </div>

            {/* Accommodation Name and Type Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Accommodation Name */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Accommodation Name
                    </label>
                    <input
                        type="text"
                        value={data.name || ''}
                        onChange={(e) => onChange('name', e.target.value)}
                        placeholder="e.g., Hilton Downtown"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>

                {/* Type Dropdown */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Type
                    </label>
                    <select
                        value={data.type || ''}
                        onChange={(e) => onChange('type', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="">Select type...</option>
                        <option value="hotel">Hotel</option>
                        <option value="airbnb">Airbnb</option>
                        <option value="hostel">Hostel</option>
                        <option value="resort">Resort</option>
                    </select>
                </div>
            </div>


            {/* Dates Section */}
            <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Stay Dates</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Check-in Date */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Check-in Date
                        </label>
                        <input
                            type="date"
                            value={data.checkIn || ''}
                            onChange={(e) => onChange('checkIn', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        />
                    </div>

                    {/* Check-out Date */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Check-out Date
                        </label>
                        <input
                            type="date"
                            value={data.checkOut || ''}
                            onChange={(e) => onChange('checkOut', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        />
                    </div>
                </div>
            </div>

            {/* Price Section */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price per Night
                </label>
                <div className="relative max-w-xs">
                    <span className="absolute left-3 top-2 text-gray-500">$</span>
                    <input
                        type="number"
                        value={data.pricePerNight || ''}
                        onChange={(e) => onChange('pricePerNight', e.target.value)}
                        placeholder="0.00"
                        min="0"
                        step="0.01"
                        className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                    Enter the nightly rate for this accommodation
                </p>
            </div>
        </div>
    );
};

export default StaysStep;
