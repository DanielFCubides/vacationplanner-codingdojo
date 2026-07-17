export const getStatusColor = (status: string): string => {
    const statusLower = status.toLowerCase();
    // PRD-07 FR-10: pending → gray, confirmed/booked → green, cancelled → red
    if (statusLower === 'confirmed') return 'bg-green-100 text-green-700';
    if (statusLower === 'booked') return 'bg-green-100 text-green-700';
    if (statusLower === 'pending') return 'bg-gray-100 text-gray-700';
    if (statusLower === 'cancelled') return 'bg-red-100 text-red-700';
    return 'bg-gray-100 text-gray-700';
};
