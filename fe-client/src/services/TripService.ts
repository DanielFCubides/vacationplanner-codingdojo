import {Trip} from "../Models";
// ============================================
// INTERFACE - Contract for trip operations
// ============================================

export interface ITripService {
    getAllTrips(): Promise<Trip[]>;

    getTripById(id: string): Promise<Trip | null>;

    createTrip(trip: Partial<Trip>): Promise<Trip>;

    updateTrip(id: string, updates: Partial<Trip>): Promise<Trip>;

    deleteTrip(id: string): Promise<boolean>;
}

// ============================================
// SIMPLE IN-MEMORY IMPLEMENTATION
// ============================================

class SimpleTripService implements ITripService {
    private trips: Trip[] = [];

    /**
     * Get all trips
     */
    async getAllTrips(): Promise<Trip[]> {
        await this.delay(300);
        return [...this.trips]; // Return copy to prevent direct mutation
    }

    /**
     * Get trip by ID
     */
    async getTripById(id: string): Promise<Trip | null> {
        await this.delay(200);
        const trip = this.trips.find(t => t.id === id);
        return trip || null;
    }

    /**
     * Create new trip
     */
    async createTrip(tripData: Partial<Trip>): Promise<Trip> {
        await this.delay(400);

        // Generate ID if not provided
        const newId = tripData.id || `trip_${Date.now()}`;

        // Create full trip object with defaults
        const newTrip: Trip = {
            id: newId,
            name: tripData.name || 'Untitled Trip',
            destination: tripData.destination || 'TBD',
            startDate: tripData.startDate || new Date(),
            endDate: tripData.endDate || new Date(),
            status: tripData.status || 'planning',
            travelers: tripData.travelers || [],
            flights: tripData.flights || [],
            accommodations: tripData.accommodations || [],
            activities: tripData.activities || [],
            budget: tripData.budget || {
                total: 0,
                spent: 0,
                categories: [],
            },
        };

        this.trips.push(newTrip);

        console.log('✅ Trip created:', newTrip);
        console.log('📋 Total trips:', this.trips.length);

        return newTrip;
    }


    /**
     * Update existing trip
     */
    async updateTrip(id: string, updates: Partial<Trip>): Promise<Trip> {
        await this.delay(300);

        const index = this.trips.findIndex(t => t.id === id);
        if (index === -1) {
            throw new Error(`Trip with id ${id} not found`);
        }

        // Merge updates with existing trip
        const updatedTrip = {
            ...this.trips[index],
            ...updates,
            id, // Ensure ID doesn't change
        };

        this.trips[index] = updatedTrip;

        console.log('✅ Trip updated:', updatedTrip);

        return updatedTrip;
    }

    /**
     * Delete trip
     */
    async deleteTrip(id: string): Promise<boolean> {
        await this.delay(200);

        const index = this.trips.findIndex(t => t.id === id);
        if (index === -1) {
            return false;
        }

        this.trips.splice(index, 1);

        console.log('🗑️ Trip deleted:', id);
        console.log('📋 Remaining trips:', this.trips.length);

        return true;
    }

    /**
     * Simulate network delay
     */
    private delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ============================================
// API IMPLEMENTATION (for future use)
// ============================================
class ApiTripService implements ITripService {
    private host: string;
    private baseUrl: string;
    private token: string;

    constructor(baseUrl: string = 'http://127.0.0.1:8000/api/trips') {
        this.baseUrl = baseUrl;
    }

    async getAllTrips(): Promise<Trip[]> {
        const response = await fetch(this.baseUrl, {
                method: 'GET',
                headers: this.setHeaders(),
            }
        );

        if (!response.ok) {
            throw new Error('Failed to fetch trips');
        }

        return response.json();
    }

    async getTripById(id: string): Promise<Trip | null> {
        const response = await fetch(`${this.baseUrl}/${id}`, {
            method: 'GET',
            headers: this.setHeaders(),
        });
        if (response.status === 404) return null;
        if (!response.ok) throw new Error('Failed to fetch trip');
        return response.json();
    }

    async createTrip(tripData: Partial<Trip>): Promise<Trip> {
        // Note: owner_id is never sent in the request body.
        // The backend derives it automatically from the JWT token (sub claim).
        const response = await fetch(this.baseUrl, {
            method: 'POST',
            headers: this.setHeaders(),
            body: JSON.stringify(tripData),
        });
        if (!response.ok) throw new Error('Failed to create trip');
        return response.json();
    }

    async updateTrip(id: string, updates: Partial<Trip>): Promise<Trip> {
        const response = await fetch(`${this.baseUrl}/${id}`, {
            method: 'PUT',
            headers: this.setHeaders(),
            body: JSON.stringify(updates),
        });
        if (!response.ok) throw new Error('Failed to update trip');
        return response.json();
    }


    async deleteTrip(id: string): Promise<boolean> {
        const response = await fetch(`${this.baseUrl}/${id}`, {
            method: 'DELETE',
            headers: this.setHeaders(),
        });
        return response.ok;
    }

    private setHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`
        };
    }

    public setToken(token: string){
        this.token = token
    }

}

// ============================================
// SERVICE FACTORY
// ============================================

function createTripService(): ITripService {
    // For now, always use simple in-memory service
    // Later: can switch based on environment variable
    console.log('🔧 Using Simple In-Memory Trip Service');
    return new ApiTripService();
}

// ============================================
// EXPORTS
// ============================================

export const tripService = createTripService();
