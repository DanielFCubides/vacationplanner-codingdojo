import React from 'react';

interface TeamStepProps {
    data: {
        name?: string;
        email?: string;
        role?: string;
    };
    onChange: (field: string, value: any) => void;
}

const TeamStep: React.FC<TeamStepProps> = ({ data, onChange }) => {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Team</h2>
                <p className="text-gray-600">Add travelers to your trip (optional)</p>
            </div>

            {/* Traveler Name */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Traveler Name
                </label>
                <input
                    type="text"
                    value={data.name || ''}
                    onChange={(e) => onChange('name', e.target.value)}
                    placeholder="e.g., John Doe"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            {/* Email and Role Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Email */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email
                    </label>
                    <input
                        type="email"
                        value={data.email || ''}
                        onChange={(e) => onChange('email', e.target.value)}
                        placeholder="john@example.com"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>

                {/* Role Dropdown */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Role
                    </label>
                    <select
                        value={data.role || ''}
                        onChange={(e) => onChange('role', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="">Select role...</option>
                        <option value="owner">Owner</option>
                        <option value="editor">Editor</option>
                        <option value="viewer">Viewer</option>
                    </select>
                </div>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start">
                    <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    <div className="text-sm text-blue-800">
                        <p className="font-medium mb-1">Role Permissions:</p>
                        <ul className="space-y-1 text-xs">
                            <li><strong>Owner:</strong> Full control - can edit everything and manage team</li>
                            <li><strong>Editor:</strong> Can view and edit trip details</li>
                            <li><strong>Viewer:</strong> Can only view trip information</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TeamStep;
