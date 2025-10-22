import React from 'react';

const UserProfile = ({ user }) => {
    return (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-blue-800 mb-4">User Profile</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <p className="text-sm font-medium text-gray-600">Email</p>
                    <p className="text-blue-700 font-semibold">{user?.email || 'Not available'}</p>
                </div>
                <div>
                    <p className="text-sm font-medium text-gray-600">User ID</p>
                    <p className="text-blue-700">{user?.id || 'Not available'}</p>
                </div>
            </div>
        </div>
    );
};

export default UserProfile;
