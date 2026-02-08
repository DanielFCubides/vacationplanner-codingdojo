import React from "react";
import { useNavigate } from "react-router-dom";

const AddTripContainer = () => {
    const navigate = useNavigate();

    const handleAddTrip = () => {
        navigate('/trips/new');
    };

    return (
        <div>
            <div 
                className="bg-blue-50 border-2 border-blue-200 rounded-lg p-2 mb-6 cursor-pointer hover:bg-blue-100 hover:border-blue-300 transition-all"
                onClick={handleAddTrip}
            >
                <div className="flex items-center justify-center">
                    <div className="text-center">
                        <svg 
                            className="w-12 h-12 text-blue-600 mx-auto mb-2" 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                        >
                            <path 
                                strokeLinecap="round" 
                                strokeLinejoin="round" 
                                strokeWidth={2} 
                                d="M12 4v16m8-8H4" 
                            />
                        </svg>
                        <h2 className="text-xl font-semibold text-blue-800">Add New Trip</h2>
                        <p className="text-sm text-blue-600 mt-1">Click to start planning your vacation</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AddTripContainer;