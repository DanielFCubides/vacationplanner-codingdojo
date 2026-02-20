# StaysStep Component - Quick Reference

## Visual Layout

```
┌────────────────────────────────────────────────┐
│ Accommodations                                 │
│ Add your accommodation details (optional)      │
├────────────────────────────────────────────────┤
│                                                │
│ ┌─ Row 1: Basic Info ───────────────────────┐ │
│ │ Accommodation Name  │ Type                │ │
│ │ [Hilton Downtown]   │ [Hotel ▼]           │ │
│ └─────────────────────────────────────────────┘│
│                                                │
│ ┌─ Stay Dates (Purple BG) ──────────────────┐ │
│ │ Check-in Date      │ Check-out Date       │ │
│ │ [07/01/2025]       │ [07/05/2025]         │ │
│ └─────────────────────────────────────────────┘│
│                                                │
│ Price per Night                                │
│ $ [150.00]                                     │
│ Enter the nightly rate for this accommodation  │
└────────────────────────────────────────────────┘
```

## Field Details

| Field | Type | Options/Placeholder | Required |
|-------|------|---------------------|----------|
| Accommodation Name | text | "e.g., Hilton Downtown" | No |
| Type | select | Hotel, Airbnb, Hostel, Resort | No |
| Check-in Date | date | Native picker | No |
| Check-out Date | date | Native picker | No |
| Price per Night | number | "0.00" | No |

## Type Dropdown Options

```typescript
<option value="">Select type...</option>
<option value="hotel">Hotel</option>
<option value="airbnb">Airbnb</option>
<option value="hostel">Hostel</option>
<option value="resort">Resort</option>
```

**Why these options?**
- Match the Accommodation model type definition
- Cover most common accommodation categories
- Prevent invalid type values

## Auto-Calculations

### Nights Calculation
```typescript
const checkIn = new Date("2025-07-01");
const checkOut = new Date("2025-07-05");
const nights = Math.ceil(
    (checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60 * 24)
);
// Result: 4 nights
```

### Total Price Calculation
```typescript
const pricePerNight = 150;
const nights = 4;
const totalPrice = pricePerNight * nights;
// Result: $600
```

**When calculation happens:**
- Only on save (not in real-time in UI)
- Falls back to 1 night if dates missing
- Falls back to price per night if only one night


## Color Coding

**Purple Background** = Stay Dates section
- Distinct from Flights (blue/green)
- Groups related date fields
- Visual consistency across wizard

## Data Transformation

### Form Input → Accommodation Model

```typescript
// What user enters (all strings)
{
    name: "Hilton Downtown",
    type: "hotel",
    checkIn: "2025-07-01",
    checkOut: "2025-07-05",
    pricePerNight: "150"
}

// Transformed to Accommodation model
{
    id: "accommodation_1234567890",
    name: "Hilton Downtown",
    type: "hotel",
    image: "",
    checkIn: new Date("2025-07-01T00:00:00"),
    checkOut: new Date("2025-07-05T00:00:00"),
    pricePerNight: 150,
    totalPrice: 600,  // 4 nights × $150
    rating: 0,
    amenities: [],
    status: "pending"
}
```

### When Accommodation is NOT Created

Accommodation is only added if **at least one** of these is filled:
- name
- type

**Example:** User fills only dates/price but no name/type → No accommodation created

## Component Props

```typescript
interface StaysStepProps {
    data: {
        name?: string;
        type?: string;
        checkIn?: string;
        checkOut?: string;
        pricePerNight?: string;
    };
    onChange: (field: string, value: any) => void;
}
```

## Common User Patterns

### Scenario 1: Complete Info
User fills all fields → Full accommodation with calculated totals ✓

### Scenario 2: Name + Dates Only
User enters name and dates, no price → Accommodation created with $0 ✓

### Scenario 3: Skip Accommodation
User leaves all blank → No accommodation created ✓

### Scenario 4: Only Dates (No Name)
User enters dates but no name/type → No accommodation created ✗

### Scenario 5: Single Night Stay
Check-in: July 1, Check-out: July 2
→ 1 night, totalPrice = pricePerNight ✓

## Future Enhancements

### Phase 1: UI Improvements
- Show calculated nights in real-time
- Show calculated total price in form
- Add total price display below price per night

### Phase 2: Validation
- Check-out must be after check-in
- Dates within trip date range
- Price must be positive

### Phase 3: Multiple Accommodations
```typescript
accommodations: [
    { /* First hotel */ },
    { /* Second hotel */ }
]
```
- "Add Another Stay" button
- List of accommodations
- Edit/delete individual stays

### Phase 4: Rich Features
- Amenities checklist
- Star rating input
- Address/location field
- Image upload
- Booking confirmation tracking

## Testing Scenarios

### Happy Path
1. Name: "Hilton Downtown"
2. Type: "Hotel"  
3. Check-in: July 1, 2025
4. Check-out: July 5, 2025
5. Price: $150
6. Navigate → data persists ✓
7. Save → accommodation created ✓
8. Check totalPrice: $600 (4 nights × $150) ✓

### Edge Cases
1. Only name → Accommodation created ✓
2. Only dates → No accommodation created ✓
3. Same check-in/out date → 0 nights, price = 0 ✓
4. No dates → nights = 1, totalPrice = pricePerNight ✓
5. Very high price → Accepts it ✓

### Dropdown Interaction
1. Opens with "Select type..."
2. Shows 4 options
3. Selection updates immediately
4. Can change selection
5. Blank selection valid (optional field)

## Accessibility

- All inputs have labels
- Placeholder text provides examples
- Native date pickers work with keyboard
- Screen reader announces dropdown options
- Focus states visible
- Logical tab order
