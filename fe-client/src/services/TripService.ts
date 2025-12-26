import {Accommodation, Activity, Flight, Traveler, Trip} from "../Models";
import { faker } from '@faker-js/faker';


const airlines = ['United Airlines', 'Delta', 'American Airlines', 'Southwest', 'JetBlue', 'Alaska Airlines'];
const airports = [
    { code: 'JFK', city: 'New York' },
    { code: 'LAX', city: 'Los Angeles' },
    { code: 'ORD', city: 'Chicago' },
    { code: 'MIA', city: 'Miami' },
    { code: 'SFO', city: 'San Francisco' },
    { code: 'SEA', city: 'Seattle' },
    { code: 'DEN', city: 'Denver' },
    { code: 'ATL', city: 'Atlanta' },
];
const hotelTypes: Accommodation['type'][] = ['hotel', 'airbnb', 'hostel', 'resort'];
const amenities = ['WiFi', 'Pool', 'Gym', 'Spa', 'Restaurant', 'Bar', 'Room Service', 'Parking', 'Beach Access'];
const activityCategories = ['Sightseeing', 'Adventure', 'Food & Dining', 'Entertainment', 'Relaxation', 'Shopping'];

export function generateTraveler(isOwner = false): Traveler {
    const firstName = faker.person.firstName();
    const lastName = faker.person.lastName();
    return {
        id: faker.string.uuid(),
        name: `${firstName} ${lastName}`,
        email: faker.internet.email({ firstName, lastName }),
        role: isOwner ? 'owner' : faker.helpers.arrayElement(['editor', 'viewer']),
        avatar: `${firstName[0]}${lastName[0]}`.toUpperCase(),
    };
}

export function generateFlight(startDate: Date): Flight {
    const departureAirport = faker.helpers.arrayElement(airports);
    const arrivalAirport = faker.helpers.arrayElement(airports.filter(a => a.code !== departureAirport.code));
    const departureTime = faker.date.between({ from: startDate, to: new Date(startDate.getTime() + 7 * 24 * 60 * 60 * 1000) });
    const durationHours = faker.number.int({ min: 1, max: 8 });
    const arrivalTime = new Date(departureTime.getTime() + durationHours * 60 * 60 * 1000);

    return {
        id: faker.string.uuid(),
        airline: faker.helpers.arrayElement(airlines),
        flightNumber: `${faker.string.alpha({ length: 2, casing: 'upper' })}${faker.number.int({ min: 100, max: 9999 })}`,
        departure: {
            airport: departureAirport.code,
            city: departureAirport.city,
            time: departureTime,
        },
        arrival: {
            airport: arrivalAirport.code,
            city: arrivalAirport.city,
            time: arrivalTime,
        },
        duration: `${durationHours}h ${faker.number.int({ min: 0, max: 59 })}m`,
        stops: faker.helpers.arrayElement([0, 0, 0, 1, 1, 2]),
        price: faker.number.int({ min: 150, max: 800 }),
        cabinClass: faker.helpers.arrayElement(['Economy', 'Premium Economy', 'Business', 'First']),
        status: faker.helpers.arrayElement(['confirmed', 'confirmed', 'pending']),
    };
}

export function generateAccommodation(startDate: Date, endDate: Date): Accommodation {
    const checkIn = faker.date.between({ from: startDate, to: new Date(endDate.getTime() - 2 * 24 * 60 * 60 * 1000) });
    const nights = faker.number.int({ min: 2, max: 7 });
    const checkOut = new Date(checkIn.getTime() + nights * 24 * 60 * 60 * 1000);
    const pricePerNight = faker.number.int({ min: 80, max: 400 });

    return {
        id: faker.string.uuid(),
        name: faker.company.name() + ' ' + faker.helpers.arrayElement(['Hotel', 'Inn', 'Resort', 'Suites']),
        type: faker.helpers.arrayElement(hotelTypes),
        image: `https://picsum.photos/seed/${faker.string.alphanumeric(8)}/400/300`,
        checkIn,
        checkOut,
        pricePerNight,
        totalPrice: pricePerNight * nights,
        rating: faker.number.float({ min: 3.5, max: 5, fractionDigits: 1 }),
        amenities: faker.helpers.arrayElements(amenities, { min: 3, max: 6 }),
        status: faker.helpers.arrayElement(['confirmed', 'confirmed', 'pending']),
    };
}

export function generateActivity(startDate: Date, endDate: Date): Activity {
    const category = faker.helpers.arrayElement(activityCategories);
    const activityNames: Record<string, string[]> = {
        'Sightseeing': ['City Walking Tour', 'Museum Visit', 'Landmark Tour', 'Architecture Tour'],
        'Adventure': ['Hiking Trip', 'Scuba Diving', 'Zip Lining', 'Kayaking'],
        'Food & Dining': ['Food Tour', 'Cooking Class', 'Wine Tasting', 'Fine Dining'],
        'Entertainment': ['Theater Show', 'Concert', 'Night Club', 'Comedy Show'],
        'Relaxation': ['Spa Day', 'Beach Day', 'Yoga Session', 'Massage'],
        'Shopping': ['Market Tour', 'Shopping District', 'Outlet Mall', 'Souvenir Shopping'],
    };

    return {
        id: faker.string.uuid(),
        name: faker.helpers.arrayElement(activityNames[category]),
        date: faker.date.between({ from: startDate, to: endDate }),
        cost: faker.number.int({ min: 20, max: 300 }),
        status: faker.helpers.arrayElement(['booked', 'booked', 'pending']),
        category,
        description: faker.lorem.sentence(),
    };
}

export function generateTrip(id?: string): Trip {
    const startDate = faker.date.future({ years: 1 });
    const tripLength = faker.number.int({ min: 5, max: 14 });
    const endDate = new Date(startDate.getTime() + tripLength * 24 * 60 * 60 * 1000);

    const travelers = [
        generateTraveler(true),
        ...Array.from({ length: faker.number.int({ min: 1, max: 4 }) }, () => generateTraveler()),
    ];

    const flights = Array.from({ length: faker.number.int({ min: 1, max: 3 }) }, () => generateFlight(startDate));
    const accommodations = Array.from({ length: faker.number.int({ min: 1, max: 2 }) }, () => generateAccommodation(startDate, endDate));
    const activities = Array.from({ length: faker.number.int({ min: 3, max: 8 }) }, () => generateActivity(startDate, endDate));

    const flightsCost = flights.reduce((sum, f) => sum + f.price, 0);
    const accommodationsCost = accommodations.reduce((sum, a) => sum + a.totalPrice, 0);
    const activitiesCost = activities.reduce((sum, a) => sum + a.cost, 0);
    const miscCost = faker.number.int({ min: 100, max: 500 });
    const totalSpent = flightsCost + accommodationsCost + activitiesCost + miscCost;
    const totalBudget = Math.ceil(totalSpent * faker.number.float({ min: 1.1, max: 1.5 }));

    return {
        id: id || faker.string.uuid(),
        name: `${faker.helpers.arrayElement(['Summer', 'Winter', 'Spring', 'Fall'])} ${faker.helpers.arrayElement(['Adventure', 'Getaway', 'Escape', 'Vacation', 'Trip'])}`,
        destination: faker.location.city() + ', ' + faker.location.country(),
        startDate,
        endDate,
        status: faker.helpers.arrayElement(['planning', 'confirmed', 'confirmed']),
        travelers,
        flights,
        accommodations,
        activities,
        budget: {
            total: totalBudget,
            spent: totalSpent,
            categories: [
                { category: 'Flights', planned: Math.ceil(flightsCost * 1.1), spent: flightsCost },
                { category: 'Accommodations', planned: Math.ceil(accommodationsCost * 1.1), spent: accommodationsCost },
                { category: 'Activities', planned: Math.ceil(activitiesCost * 1.2), spent: activitiesCost },
                { category: 'Miscellaneous', planned: Math.ceil(miscCost * 1.3), spent: miscCost },
            ],
        },
    };
}

// Cache trips by ID to maintain consistency
const tripCache = new Map<string, Trip>();

export function getTripById(id: string): Trip {
    if (!tripCache.has(id)) {
        tripCache.set(id, generateTrip(id));
    }
    let trip = tripCache.get(id)!;
    return trip;
}

export function generateTrips(count: number): Trip[] {
    return Array.from({ length: count }, () => generateTrip());
}