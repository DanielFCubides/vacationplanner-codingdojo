# TeamStep Component - Quick Reference

## Visual Layout

```
┌────────────────────────────────────────────────┐
│ Team                                           │
│ Add travelers to your trip (optional)          │
├────────────────────────────────────────────────┤
│                                                │
│ Traveler Name                                  │
│ [John Doe....................................]  │
│                                                │
│ ┌─ Row 2: Email & Role ──────────────────────┐│
│ │ Email              │ Role                  ││
│ │ [john@example.com] │ [Editor ▼]            ││
│ └───────────────────────────────────────────┘ │
│                                                │
│ ┌─ Role Permissions (Blue Info Box) ─────────┐│
│ │ ℹ️  Role Permissions:                       ││
│ │                                             ││
│ │ • Owner: Full control - manage everything  ││
│ │ • Editor: Can view and edit trip details   ││
│ │ • Viewer: Can only view trip information   ││
│ └─────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
```

## Field Details

| Field | Type | Options/Placeholder | Required |
|-------|------|---------------------|----------|
| Traveler Name | text | "e.g., John Doe" | No |
| Email | email | "john@example.com" | No |
| Role | select | Owner, Editor, Viewer | No |

## Role System

### Owner
- **Full control** over the trip
- Can edit all trip details
- Can manage team members
- Can delete the trip
- **Use case:** Trip organizer

### Editor  
- Can view trip details
- Can edit trip details
- Cannot manage team
- **Use case:** Active collaborators

### Viewer
- Can only view trip information
- Cannot edit anything
- **Use case:** Passive participants, family members who just need info

**Default Role:** Viewer (safest, least permissions)

## Auto-Generated Avatars

The system automatically generates avatar initials from names:

```typescript
"John Doe" → "JD"
"Alice Smith" → "AS"
"Bob" → "B"
"" → "U" (Unknown)
```

**Algorithm:**
1. If full name (2+ words): First letter of first + last name
2. If single name: First letter only
3. If empty: "U" for Unknown

**Why?**
- Visual identity without image upload
- Consistent 2-letter format
- Easy to recognize in UI
- No external dependencies


## Data Transformation

### Form Input → Traveler Model

```typescript
// What user enters
{
    name: "John Doe",
    email: "john@example.com",
    role: "editor"
}

// Transformed to Traveler model
{
    id: "traveler_1234567890",
    name: "John Doe",
    email: "john@example.com",
    role: "editor",
    avatar: "JD"  // Auto-generated
}
```

### When Traveler is NOT Created

Traveler is only added if **at least one** of these is filled:
- name
- email

**Example:** User fills only role but no name/email → No traveler created

## Component Props

```typescript
interface TeamStepProps {
    data: {
        name?: string;
        email?: string;
        role?: string;
    };
    onChange: (field: string, value: any) => void;
}
```

## Info Box Design

The blue info box serves multiple purposes:
1. **Educates** users about role permissions upfront
2. **Reduces support questions** about what roles mean
3. **Helps users choose** the right role
4. **Professional appearance** with icon and formatting

**Color choice:** Blue (team/collaboration theme)

## Common User Patterns

### Scenario 1: Complete Traveler Info
User fills all fields → Full traveler created with initials ✓

### Scenario 2: Name Only
User enters name, no email → Traveler created, role defaults to "viewer" ✓

### Scenario 3: Skip Team
User leaves all blank → No traveler created ✓

### Scenario 4: Email Only
User enters email but no name → Traveler created with empty name ✓

### Scenario 5: No Role Selected
User fills name/email, no role → Role defaults to "viewer" (safest) ✓

## Layout Strategy

**Full-width Name Field:**
- Person's identity is primary information
- Names can be long
- Deserves prominence

**Two-column Email & Role:**
- Both are secondary attributes
- Similar visual weight
- Natural pairing (contact + permission)

**Info Box at Bottom:**
- Doesn't interrupt form flow
- Available for reference
- Not intrusive

## Future Enhancements

### Phase 1: Multiple Travelers
```typescript
travelers: [
    { name: "John Doe", email: "john@...", role: "owner" },
    { name: "Jane Smith", email: "jane@...", role: "editor" },
    { name: "Bob Jones", email: "bob@...", role: "viewer" }
]
```
- "Add Traveler" button
- List view with avatars
- Edit/delete individual travelers
- Drag to reorder

### Phase 2: Email Integration
- Send invite emails to travelers
- Email validation (format check)
- Duplicate email detection
- Confirmation emails

### Phase 3: Rich Profiles
- Phone number
- Profile photo upload
- Emergency contact
- Dietary restrictions
- Passport information (for international trips)
- Birthday (for special occasions)

### Phase 4: Collaboration Features
- Real-time presence (who's viewing)
- Activity feed (who edited what)
- Comments/chat
- @mentions
- Notifications

## Testing Scenarios

### Happy Path
1. Name: "John Doe"
2. Email: "john@example.com"
3. Role: "Editor"
4. Navigate → data persists ✓
5. Save → traveler created ✓
6. Check avatar: "JD" ✓

### Edge Cases
1. Single name "Alice" → avatar: "A" ✓
2. Empty name → avatar: "U" ✓
3. No role selected → defaults to "viewer" ✓
4. Only email → traveler created ✓
5. Only role → no traveler created ✗

### Email Input
- Accepts valid email formats
- Shows browser validation
- Type="email" provides mobile keyboard optimization

### Dropdown Interaction
1. Opens with "Select role..."
2. Shows 3 role options
3. Selection updates immediately
4. Can change selection
5. Blank selection defaults to "viewer"

## Accessibility

- All inputs have clear labels
- Email input type for validation
- Dropdown keyboard navigable
- Info box readable by screen readers
- Icon has proper semantic meaning
- Logical tab order
- Focus states visible

## Real-World Usage

**Typical Trip Scenarios:**

**Solo Traveler:**
- Skip this step entirely
- Or add yourself as owner

**Couple:**
- Add partner as "editor"
- Both can plan together

**Family Trip:**
- Parents as "owner" or "editor"
- Kids as "viewer"

**Group Travel:**
- Organizer as "owner"
- Active planners as "editor"
- Others as "viewer"

**Work Trip:**
- Admin as "owner"
- Colleagues as "editor"
- Executives as "viewer"
