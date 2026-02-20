# ActivitiesStep Component - Quick Reference

## Visual Layout

```
┌────────────────────────────────────────────────┐
│ Activities                                     │
│ Add activities and experiences (optional)      │
├────────────────────────────────────────────────┤
│                                                │
│ Activity Name                                  │
│ [City Walking Tour, Museum Visit...........]   │
│                                                │
│ ┌─ Row 2: Date & Category ──────────────────┐ │
│ │ Date              │ Category              │ │
│ │ [07/02/2025]      │ [Sightseeing ▼]       │ │
│ └───────────────────────────────────────────┘  │
│                                                │
│ ┌─ Cost (Orange BG) ─────────────────────────┐│
│ │ Cost                                       ││
│ │ $ [50.00]                                  ││
│ │ Enter the cost for this activity           ││
│ └────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
```

## Field Details

| Field | Type | Options/Placeholder | Required |
|-------|------|---------------------|----------|
| Activity Name | text | "e.g., City Walking Tour, Museum Visit" | No |
| Date | date | Native picker | No |
| Category | select | 6 categories | No |
| Cost | number | "0.00" with $ prefix | No |

## Category Dropdown Options

```typescript
<option value="">Select category...</option>
<option value="Sightseeing">Sightseeing</option>
<option value="Adventure">Adventure</option>
<option value="Food & Dining">Food & Dining</option>
<option value="Entertainment">Entertainment</option>
<option value="Relaxation">Relaxation</option>
<option value="Shopping">Shopping</option>
```

**Category Alignment:**
- Matches Activity model category field
- Same categories as TripService generator
- Covers most common vacation activities
- Easy for users to classify experiences

## Color Coding

**Orange Background** = Cost section
- Fourth unique color in wizard
- Complements blue (flights), green (flights), purple (stays)
- Highlights the financial aspect
- Consistent with budget-related UI elements


## Data Transformation

### Form Input → Activity Model

```typescript
// What user enters (all strings)
{
    name: "City Walking Tour",
    date: "2025-07-02",
    category: "Sightseeing",
    cost: "50"
}

// Transformed to Activity model
{
    id: "activity_1234567890",
    name: "City Walking Tour",
    date: new Date("2025-07-02T00:00:00"),
    cost: 50,
    status: "pending",
    category: "Sightseeing",
    description: ""
}
```

### When Activity is NOT Created

Activity is only added if **at least one** of these is filled:
- name
- category

**Example:** User fills only date/cost but no name/category → No activity created

## Component Props

```typescript
interface ActivitiesStepProps {
    data: {
        name?: string;
        date?: string;
        category?: string;
        cost?: string;
    };
    onChange: (field: string, value: any) => void;
}
```

## Layout Strategy

**Full-width Name Field:**
- Activity names are often descriptive
- "City Walking Tour with Historical Commentary"
- "Food & Wine Tasting Experience"
- Needs more horizontal space than other fields

**Two-column Date & Category:**
- Both are selection-based inputs
- Similar visual weight
- Natural pairing (when + what type)

**Highlighted Cost Section:**
- Orange background draws attention
- Separates financial info
- Consistent with budget step theming

## Common User Patterns

### Scenario 1: Complete Activity
User fills all fields → Full activity object created ✓

### Scenario 2: Name Only
User enters name, no other fields → Activity created with defaults ✓

### Scenario 3: Skip Activity
User leaves all blank → No activity created ✓

### Scenario 4: Only Date/Cost
User enters date and cost but no name/category → No activity created ✗

### Scenario 5: Free Activity
User enters name/category but cost = 0 → Activity created with $0 ✓

## Activity Examples by Category

### Sightseeing
- City Walking Tour
- Museum Visit
- Landmark Tour
- Architecture Tour

### Adventure
- Hiking Trip
- Scuba Diving
- Zip Lining
- Kayaking

### Food & Dining
- Food Tour
- Cooking Class
- Wine Tasting
- Fine Dining Reservation

### Entertainment
- Theater Show
- Concert
- Night Club
- Comedy Show

### Relaxation
- Spa Day
- Beach Day
- Yoga Session
- Massage Appointment

### Shopping
- Market Tour
- Shopping District Visit
- Outlet Mall
- Souvenir Shopping

## Future Enhancements

### Phase 1: Description Field
```typescript
description: string;  // Currently empty string
```
- Add textarea below name
- Allow detailed notes
- Booking info, meeting points, etc.

### Phase 2: Multiple Activities
```typescript
activities: [
    { name: "Museum Visit", ... },
    { name: "Dinner Cruise", ... },
    { name: "City Tour", ... }
]
```
- "Add Activity" button
- List view of all activities
- Edit/delete individual activities
- Reorder by drag-and-drop

### Phase 3: Status Management
- Dropdown for status (Booked, Pending, Cancelled)
- Visual indicators (color badges)
- Filter by status

### Phase 4: Smart Features
- Duration field (in hours)
- Time of day (morning/afternoon/evening)
- Location/meeting point
- Suggested activities based on destination
- Calendar/timeline view
- Total activities cost calculation

## Testing Scenarios

### Happy Path
1. Name: "City Walking Tour"
2. Date: July 2, 2025
3. Category: "Sightseeing"
4. Cost: $50
5. Navigate → data persists ✓
6. Save → activity created ✓

### Edge Cases
1. Only name → Activity created with empty category ✓
2. Only category → Activity created with empty name ✗ (won't create)
3. Free activity (cost = 0) → Activity created ✓
4. High cost → Accepts any number ✓
5. Date outside trip range → Accepts it (validation could be added later) ✓

### Dropdown Interaction
1. Opens with "Select category..."
2. Shows 6 category options
3. Selection updates immediately
4. Can change selection
5. Blank selection valid (optional)

## Accessibility

- Activity name has clear label
- Date picker keyboard accessible
- Dropdown keyboard navigable
- Cost input announces $ prefix
- Helper text provides guidance
- Logical tab order
- Screen reader announces all labels
