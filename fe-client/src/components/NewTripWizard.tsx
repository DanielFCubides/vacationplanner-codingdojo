import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tripService } from '../services/TripService';

// Import step components
import OverviewStep from './wizard-steps/OverviewStep';
import FlightsStep from './wizard-steps/FlightsStep';
import StaysStep from './wizard-steps/StaysStep';
import ActivitiesStep from './wizard-steps/ActivitiesStep';
import BudgetStep from './wizard-steps/BudgetStep';
import TeamStep from './wizard-steps/TeamStep';

const NewTripWizard = () => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(0);
    const [formData, setFormData] = useState({
        overview: {
            name: '',
            destination: '',
            startDate: '',
            endDate: '',
        },
        flights: {
            airline: '',
            flightNumber: '',
            departureAirport: '',
            departureTime: '',
            arrivalAirport: '',
            arrivalTime: '',
        },
        stays: {
            name: '',
            type: '',
            checkIn: '',
            checkOut: '',
            pricePerNight: '',
        },
        activities: {
            name: '',
            date: '',
            category: '',
            cost: '',
        },
        budget: {
            totalBudget: '',
        },
        team: {
            name: '',
            email: '',
            role: '',
        },
    });

    // Step configuration
    const steps = [
        { id: 'overview', label: 'Overview', component: OverviewStep },
        { id: 'flights', label: 'Flights', component: FlightsStep },
        { id: 'stays', label: 'Stays', component: StaysStep },
        { id: 'activities', label: 'Activities', component: ActivitiesStep },
        { id: 'budget', label: 'Budget', component: BudgetStep },
        { id: 'team', label: 'Team', component: TeamStep },
    ];

    // Handle field changes
    const handleFieldChange = (field: string, value: any) => {
        const stepId = steps[currentStep].id;
        setFormData(prev => ({
            ...prev,
            [stepId]: {
                ...prev[stepId],
                [field]: value,
            },
        }));
    };

    // Navigation handlers
    const goToNextStep = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(prev => prev + 1);
        }
    };

    const goToPreviousStep = () => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1);
        }
    };

    // Save trip
    const handleSaveTrip = async () => {
        try {
            // Parse budget value
            const totalBudget = formData.budget.totalBudget 
                ? parseFloat(formData.budget.totalBudget) 
                : 0;
            
            // Create flights array if flight data exists
            const flights = [];
            if (formData.flights.airline || formData.flights.flightNumber) {
                flights.push({
                    id: `flight_${Date.now()}`,
                    airline: formData.flights.airline || '',
                    flightNumber: formData.flights.flightNumber || '',
                    departure: {
                        airport: formData.flights.departureAirport || '',
                        city: formData.flights.departureAirport || '',
                        time: formData.flights.departureTime 
                            ? new Date(formData.flights.departureTime) 
                            : new Date(),
                    },
                    arrival: {
                        airport: formData.flights.arrivalAirport || '',
                        city: formData.flights.arrivalAirport || '',
                        time: formData.flights.arrivalTime 
                            ? new Date(formData.flights.arrivalTime) 
                            : new Date(),
                    },
                    duration: '1',
                    stops: 0,
                    price: 0,
                    cabinClass: 'Economy',
                    status: 'pending' as const,
                });
            }
            
            // Create accommodations array if accommodation data exists
            const accommodations = [];
            if (formData.stays.name || formData.stays.type) {
                const pricePerNight = formData.stays.pricePerNight 
                    ? parseFloat(formData.stays.pricePerNight) 
                    : 0;
                
                // Calculate nights and total price
                let nights = 1;
                let totalPrice = pricePerNight;
                if (formData.stays.checkIn && formData.stays.checkOut) {
                    const checkIn = new Date(formData.stays.checkIn);
                    const checkOut = new Date(formData.stays.checkOut);
                    nights = Math.ceil((checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60 * 24));
                    totalPrice = pricePerNight * nights;
                }
                
                accommodations.push({
                    id: `accommodation_${Date.now()}`,
                    name: formData.stays.name || '',
                    type: (formData.stays.type || 'hotel') as 'hotel' | 'airbnb' | 'hostel' | 'resort',
                    image: '',
                    checkIn: formData.stays.checkIn 
                        ? new Date(formData.stays.checkIn) 
                        : new Date(),
                    checkOut: formData.stays.checkOut 
                        ? new Date(formData.stays.checkOut) 
                        : new Date(),
                    pricePerNight: pricePerNight,
                    totalPrice: totalPrice,
                    rating: 0,
                    amenities: [],
                    status: 'pending' as const,
                });
            }
            
            // Create activities array if activity data exists
            const activities = [];
            if (formData.activities.name || formData.activities.category) {
                const activityCost = formData.activities.cost 
                    ? parseFloat(formData.activities.cost) 
                    : 0;
                
                activities.push({
                    id: `activity_${Date.now()}`,
                    name: formData.activities.name || '',
                    date: formData.activities.date 
                        ? new Date(formData.activities.date) 
                        : new Date(),
                    cost: activityCost,
                    status: 'pending' as const,
                    category: formData.activities.category || '',
                    description: '',
                });
            }
            
            // Create travelers array if traveler data exists
            const travelers = [];
            if (formData.team.name || formData.team.email) {
                // Generate initials for avatar
                const nameParts = (formData.team.name || '').trim().split(' ');
                const initials = nameParts.length >= 2 
                    ? `${nameParts[0][0]}${nameParts[nameParts.length - 1][0]}`.toUpperCase()
                    : (formData.team.name || 'U')[0].toUpperCase();
                
                travelers.push({
                    id: `traveler_${Date.now()}`,
                    name: formData.team.name || '',
                    email: formData.team.email || '',
                    role: (formData.team.role || 'viewer') as 'owner' | 'editor' | 'viewer',
                    avatar: initials,
                });
            }
            
            // Prepare trip data for the service
            const tripData = {
                name: formData.overview.name || 'Untitled Trip',
                destination: formData.overview.destination || 'TBD',
                startDate: formData.overview.startDate 
                    ? new Date(formData.overview.startDate) 
                    : new Date(),
                endDate: formData.overview.endDate 
                    ? new Date(formData.overview.endDate) 
                    : new Date(),
                status: 'planning' as const,
                travelers: travelers,
                flights: flights,
                accommodations: accommodations,
                activities: activities,
                budget: {
                    total: totalBudget,
                    spent: 0,
                    categories: [],
                },
            };

            // Call the service to create trip
            const createdTrip = await tripService.createTrip(tripData);
            
            console.log('✅ Trip created:', createdTrip);
            
            // Navigate to dashboard or trip details
            navigate('/dashboard');
        } catch (error) {
            console.error('❌ Error creating trip:', error);
            alert('Failed to create trip. Please try again.');
        }
    };

    // Render current step component
    const CurrentStepComponent = steps[currentStep].component;
    const currentStepData = formData[steps[currentStep].id];

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-3xl mx-auto px-4">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Create New Trip</h1>
                    <p className="text-gray-600 mt-2">
                        Step {currentStep + 1} of {steps.length}: {steps[currentStep].label}
                    </p>
                </div>

                {/* Progress Bar */}
                <div className="mb-8">
                    <div className="flex items-center justify-between mb-2">
                        {steps.map((step, index) => (
                            <div 
                                key={step.id}
                                className={`flex-1 ${index !== steps.length - 1 ? 'mr-2' : ''}`}
                            >
                                <div 
                                    className={`h-2 rounded-full ${
                                        index <= currentStep 
                                            ? 'bg-blue-600' 
                                            : 'bg-gray-300'
                                    }`}
                                />
                            </div>
                        ))}
                    </div>
                    <div className="flex justify-between text-xs text-gray-600">
                        {steps.map(step => (
                            <span key={step.id}>{step.label}</span>
                        ))}
                    </div>
                </div>

                {/* Form Card */}
                <div className="bg-white rounded-lg shadow-md p-8 mb-6">
                    <CurrentStepComponent 
                        data={currentStepData}
                        onChange={handleFieldChange}
                    />
                </div>

                {/* Navigation Buttons */}
                <div className="flex justify-between items-center">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium"
                    >
                        Cancel
                    </button>
                    
                    <div className="flex gap-3">
                        {currentStep > 0 && (
                            <button
                                onClick={goToPreviousStep}
                                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                            >
                                Previous
                            </button>
                        )}
                        
                        {currentStep < steps.length - 1 ? (
                            <button
                                onClick={goToNextStep}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                            >
                                Next
                            </button>
                        ) : (
                            <button
                                onClick={handleSaveTrip}
                                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                            >
                                Save Trip
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NewTripWizard;
