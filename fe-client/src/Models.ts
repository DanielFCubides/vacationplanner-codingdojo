export interface Trip {
    id: string;
    name: string;
    destination: string;
    startDate: Date;
    endDate: Date;
    status: 'planning' | 'confirmed' | 'completed';
    travelers: Traveler[];
    flights: Flight[];
    accommodations: Accommodation[];
    activities: Activity[];
    budget: {
        total: number;
        spent: number;
        categories: BudgetCategory[];
    };
}

export interface Traveler {
    id: string;
    name: string;
    email: string;
    role: 'owner' | 'editor' | 'viewer';
    avatar: string;
}

export interface FlightFormData {
    airline: string;
    flightNumber: string;
    departureAirport: string;
    departureTime: string;
    arrivalAirport: string;
    arrivalTime: string;
}

export interface Flight {
    id: string;
    airline: string;
    flightNumber: string;
    departure: {
        airport: string;
        city: string;
        time: Date;
    };
    arrival: {
        airport: string;
        city: string;
        time: Date;
    };
    duration: string;
    stops: number;
    price: number;
    cabinClass: string;
    status: 'confirmed' | 'pending' | 'cancelled';
}

export interface Accommodation {
    id: string;
    name: string;
    type: 'hotel' | 'airbnb' | 'hostel' | 'resort';
    image: string;
    checkIn: Date;
    checkOut: Date;
    pricePerNight: number;
    totalPrice: number;
    rating: number;
    amenities: string[];
    status: 'confirmed' | 'pending' | 'cancelled';
}

export interface Activity {
    id: string;
    name: string;
    date: Date;
    cost: number;
    status: 'booked' | 'pending' | 'cancelled';
    category: string;
    description: string;
}

export interface BudgetCategory {
    category: string;
    planned: number;
    spent: number;
}