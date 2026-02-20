# FlightsStep Component - Quick Reference

## Visual Layout

### Desktop (2-column grid)
```
┌────────────────────────────────────────────────┐
│ Flights                                        │
│ Add your flight details (optional)             │
├────────────────────────────────────────────────┤
│                                                │
│ ┌─ Row 1: Basic Info ───────────────────────┐ │
│ │ Airline          │ Flight Number          │ │
│ │ [Input]          │ [Input]                │ │
│ └──────────────────────────────────────────┬─┘ │
│                                            │   │
│ ┌─ Departure (Blue BG) ─────────────────────┐ │
│ │ Airport          │ Departure Time         │ │
│ │ [Input]          │ [DateTime Picker]      │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ ┌─ Arrival (Green BG) ──────────────────────┐ │
│ │ Airport          │ Arrival Time           │ │
│ │ [Input]          │ [DateTime Picker]      │ │
│ └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

### Mobile (Stacked)
All fields stack vertically in order:
1. Airline
2. Flight Number
3. Departure Airport
4. Departure Time
5. Arrival Airport
6. Arrival Time

## Field Details

| Field | Type | Placeholder | Required |
|-------|------|-------------|----------|
| Airline | text | "e.g., United Airlines" | No |
| Flight Number | text | "e.g., UA1234" | No |
| Departure Airport | text | "e.g., JFK or New York" | No |
| Departure Time | datetime-local | - | No |
| Arrival Airport | text | "e.g., LAX or Los Angeles" | No |
| Arrival Time | datetime-local | - | No |

## Color Coding

**Why color sections?**
- **Blue background** = Departure (sky/taking off)
- **Green background** = Arrival (land/destination)
- Visual cue helps distinguish similar fields
- Improves scannability of form

## Data Transformation

### Form Input → Flight Model

```typescript
// What user enters (all strings)
{
    airline: "United Airlines",
    flightNumber: "UA1234",
    departureAirport: "JFK",
    departureTime: "2025-07-01T10:00",
    arrivalAirport: "LAX", 
    arrivalTime: "2025-07-01T13:30"
}

// Transformed to Flight model
{
    id: "flight_1625140800000",
    airline: "United Airlines",
    flightNumber: "UA1234",
    departure: {
        airport: "JFK",
        city: "JFK",  // Same as airport for now
        time: new Date("2025-07-01T10:00:00")
    },
    arrival: {
        airport: "LAX",
        city: "LAX",  // Same as airport for now
        time: new Date("2025-07-01T13:30:00")
    },
    duration: "",  // Not calculated yet
    stops: 0,      // Default
    price: 0,      // Not collected yet
    cabinClass: "Economy",  // Default
    status: "pending"
}
```

### When Flight is NOT Created

Flight is only added to trip if **at least one** of these is filled:
- airline
- flightNumber

**Example:** User fills only airports/times but no airline → No flight created

## Code Structure

### Component Props
```typescript
interface FlightsStepProps {
    data: {
        airline?: string;
        flightNumber?: string;
        departureAirport?: string;
        departureTime?: string;
        arrivalAirport?: string;
        arrivalTime?: string;
    };
    onChange: (field: string, value: any) => void;
}
```

### Grid Responsive Classes
- `grid-cols-1` - Mobile: 1 column
- `md:grid-cols-2` - Desktop: 2 columns
- `gap-4` - Spacing between fields

### Background Colors
- `bg-blue-50` - Light blue (Departure section)
- `bg-green-50` - Light green (Arrival section)  
- `bg-white` - White inputs (stand out on colored backgrounds)

## Common User Patterns

### Scenario 1: Complete Flight Info
User fills all fields → Full flight object created ✓

### Scenario 2: Partial Info (Airline only)
User enters airline but no times → Flight created with empty times ✓

### Scenario 3: Skip Flight
User leaves all blank → No flight created, empty flights array ✓

### Scenario 4: Only Times (No Airline)
User enters times but no airline/number → No flight created ✗

## Future Enhancements

### Phase 1: Validation
- Arrival time must be after departure time
- If one field filled, require airport at minimum
- Date validation (within trip dates)

### Phase 2: Multiple Flights
```typescript
flights: [
    { /* Outbound flight */ },
    { /* Return flight */ }
]
```
- "Add Flight" button
- List of entered flights
- Edit/delete individual flights

### Phase 3: Enhanced Fields
- Cabin class dropdown
- Price input
- Stops count
- Layover airports
- Booking confirmation number

### Phase 4: Smart Features
- Auto-calculate duration
- Airport code lookup (JFK → John F. Kennedy International)
- Flight status integration
- Price tracking

## Testing Scenarios

### Happy Path
1. Fill airline: "Delta"
2. Fill flight number: "DL123"
3. Fill departure: "ATL", select time
4. Fill arrival: "LAX", select time
5. Navigate away and back → data persists ✓
6. Save → flight created ✓

### Edge Cases
1. Enter only airline → Flight created with empty fields ✓
2. Enter only times → No flight created ✓
3. Leave all blank → No flight created ✓
4. Enter very long airline name → Accepts it ✓

### Datetime-local Input
- Shows native picker on desktop
- Shows native picker on mobile
- Format: YYYY-MM-DDTHH:mm
- User selects date then time

## Accessibility

- All inputs have labels
- Placeholder text provides examples
- Color is not the only differentiator (section headers too)
- Keyboard navigation works
- Screen reader friendly
