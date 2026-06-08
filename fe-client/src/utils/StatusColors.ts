export const getStatusColor = (status: string): string => {
    const statusLower = status.toLowerCase();

    // Trip status colors
    if (statusLower === 'planning') return 'bg-blue-100 text-blue-700';
    if (statusLower === 'confirmed') return 'bg-green-100 text-green-700';
    if (statusLower === 'in_progress') return 'bg-amber-100 text-amber-700';
    if (statusLower === 'completed') return 'bg-gray-100 text-gray-700';
    if (statusLower === 'cancelled') return 'bg-red-100 text-red-700';

    // Flight/accommodation/activity status colors
    if (statusLower === 'pending') return 'bg-yellow-100 text-yellow-700';
    if (statusLower === 'booked') return 'bg-blue-100 text-blue-700';

    // Default fallback
    return 'bg-gray-100 text-gray-700';
};
