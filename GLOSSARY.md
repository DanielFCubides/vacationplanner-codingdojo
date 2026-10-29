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

**Activity**:
Something the Trip's travelers do on one date, e.g. a tour, a show or a dinner. It has an Activity category and a cost, which may be 0. It may fall outside the Trip's dates.
_Avoid_: Event, experience, excursion

**Activity category**:
The kind of Activity: Sightseeing, Adventure, Food & Dining, Entertainment, Relaxation or Shopping.
_Avoid_: Category (bare), type

**Booked**:
The committed state of an Activity. Flights and Accommodations use confirmed instead.
_Avoid_: Confirmed (for Activities)

**Budget category**:
A planned spending bucket on a Trip's budget, with its own planned and spent amounts, kept by hand. It is not linked to Activity categories.
_Avoid_: Category (bare)

**Budget total**:
The amount the traveler plans to spend on a Trip, set by the traveler. 0 means no budget has been set.
_Avoid_: Budget (bare, when the total is meant), limit

**Spent**:
The amount committed against a Trip's budget: the sum of confirmed Flight prices, confirmed Accommodation totals and booked Activity costs. It is always derived, never entered by the traveler.
_Avoid_: Cost, used, expenses

**Remaining**:
Budget total minus Spent. It goes negative when the Trip is over budget.
_Avoid_: Left, balance

**Category spent**:
An amount the traveler records by hand against one Budget category. It is independent of Spent, so the Category spent amounts need not add up to Spent.
_Avoid_: Spent (bare)

**Unallocated**:
Budget total minus the sum of the Budget categories' planned amounts. It goes negative when more is planned than the Budget total.
_Avoid_: Free, unassigned
