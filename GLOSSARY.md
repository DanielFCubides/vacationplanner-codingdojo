# Trip Planning

A traveler plans a Trip by gathering the flights, stays and activities it needs and tracking what has been committed against a budget.

## Language

**Trip**:
A planned journey to a destination between a start and end date, owned by one user.
_Avoid_: Plan, vacation, itinerary

**Trip child**:
A Flight, Accommodation or Activity that belongs to a Trip.
_Avoid_: Item, booking, component

**Flight**:
One leg of travel between two airports under a single flight number. Connections on the same ticket are stops, not extra Flights; a return journey is two Flights.
_Avoid_: Booking, segment, ticket

**Stop**:
An intermediate landing within a single Flight.
_Avoid_: Layover, connection

**Spent**:
The amount committed against a Trip's budget: the sum of confirmed Flights and Accommodations and booked Activities.
_Avoid_: Cost, used, expenses
