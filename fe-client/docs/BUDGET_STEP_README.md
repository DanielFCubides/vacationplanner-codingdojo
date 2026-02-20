# BudgetStep Component - Quick Reference

## What It Looks Like

```
┌─────────────────────────────────────────┐
│ Budget                                  │
├─────────────────────────────────────────┤
│ Set your total trip budget (optional)   │
│                                         │
│ Total Budget                            │
│ ┌────────────────────────────────────┐ │
│ │ $ 5000.00                          │ │
│ └────────────────────────────────────┘ │
│ Enter the total amount you plan to     │
│ spend on this trip                     │
└─────────────────────────────────────────┘
```

## Data Flow

```typescript
// User types in field
"5000" (string)
    ↓
onChange('totalBudget', '5000')
    ↓
formData.budget.totalBudget = "5000"
    ↓
// On save
parseFloat("5000") → 5000 (number)
    ↓
tripData.budget.total = 5000
    ↓
TripService.createTrip(tripData)
```

## Code Explanation

### Input Field Features
- **Type**: `number` (prevents non-numeric input)
- **Min**: `0` (no negative budgets)
- **Step**: `0.01` (allows cents: $1234.56)
- **Placeholder**: "0.00" (shows expected format)

### Styling Details
- **$ prefix**: Positioned with `absolute left-3` 
- **Left padding**: `pl-8` (space for $ sign)
- **Focus state**: Blue ring on focus
- **Helper text**: Gray, small font below input

### Why String in Component?
HTML inputs always return strings. We convert to number only when saving to the Trip model.

## Testing

### Manual Test
1. Navigate to Budget step (5 of 6)
2. Type: `5000`
3. See: `$ 5000`
4. Navigate back/forward
5. Value persists: ✓
6. Click "Save Trip"
7. Check console: `budget.total = 5000` ✓

### Edge Cases
- Empty field → saves as `0`
- Invalid number → saves as `0` (parseFloat returns NaN → default 0)
- Negative number → prevented by `min="0"`
- Decimal → works: `1234.56` ✓

## Next Enhancement Ideas

When ready to expand BudgetStep:

```typescript
// Add budget categories
categories: [
  { name: 'Flights', amount: 2000 },
  { name: 'Hotels', amount: 1500 },
  { name: 'Food', amount: 1000 },
  { name: 'Activities', amount: 500 }
]

// Add currency selector
currency: 'USD' | 'EUR' | 'GBP'
```
