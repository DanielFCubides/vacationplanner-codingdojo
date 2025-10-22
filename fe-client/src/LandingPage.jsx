import React from 'react';
import { useNavigate } from 'react-router-dom';
import lockLogo from './assets/LockLogo.png';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute top-0 left-0 w-96 h-96 transform -translate-x-1/2 -translate-y-1/2">
        <div className="w-full h-full bg-blue-400 rounded-full opacity-20 blur-3xl"></div>
      </div>
      <div className="absolute bottom-0 right-0 w-96 h-96 transform translate-x-1/3 translate-y-1/3">
        <div className="w-full h-full bg-blue-400 rounded-full opacity-20 blur-3xl"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 w-full max-w-4xl px-8 py-12 text-center">
        {/* Logo and Title */}
        <div className="mb-12">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-2xl mb-6 transform hover:scale-105 transition-transform">
            <img src={lockLogo} alt="Vacation Planner Logo" className="w-16 h-16" />
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
            Vacation Planner
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-600 max-w-2xl mx-auto">
            Plan your perfect vacation in minutes. Compare flights, find stays, and build your dream itinerary with AI-powered recommendations.
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-12 max-w-3xl mx-auto">
          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-3">✈️</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Find Flights</h3>
            <p className="text-gray-600 text-sm">Compare prices across airlines and find the best deals</p>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-3">🏨</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Book Stays</h3>
            <p className="text-gray-600 text-sm">Discover perfect accommodations for your trip</p>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-3">🗺️</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Plan Itinerary</h3>
            <p className="text-gray-600 text-sm">Get AI-powered recommendations for your dream vacation</p>
          </div>
        </div>

        {/* CTA Button */}
        <div className="space-y-4">
          <button
            onClick={handleGetStarted}
            className="px-12 py-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-lg font-semibold rounded-lg shadow-lg hover:from-blue-600 hover:to-blue-700 transform hover:scale-105 transition-all duration-200"
          >
            Start Planning
          </button>
          
          <p className="text-gray-500 text-sm">
            Click to access your account and start planning your vacation
          </p>
        </div>

        {/* Info Section */}
        <div className="mt-16 pt-8 border-t border-gray-200">
          <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Free to use</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>No credit card required</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Secure authentication</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
