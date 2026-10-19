# Trip Planning

A traveler plans a Trip by gathering the flights, accommodations and activities it needs and tracking what has been committed against a budget.

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

**Accommodation**:
A place where a Trip's travelers sleep, from a check-in date to a check-out date. It is one of four types: hotel, airbnb, hostel or resort. Accommodations may overlap and may fall outside the Trip's dates.
_Avoid_: Stay, lodging, hotel (hotel is a type, not the thing)

**Nightly rate**:
The price of one night at an Accommodation.
_Avoid_: Price, rate

**Accommodation total**:
The full amount paid for an Accommodation, including fees and taxes beyond the Nightly rate. The user enters it; it is not nights × Nightly rate.
_Avoid_: Cost, price

**Spent**:
The amount committed against a Trip's budget: the sum of confirmed Flight prices, confirmed Accommodation totals and booked Activity costs.
_Avoid_: Cost, used, expenses
