"""
Unit tests for TripMapper.apply_flight_update.

Verifies that a partial FlightUpdateRequest merges onto an existing
Flight entity while preserving its id and any fields not provided.
"""
from datetime import datetime

from src.trips.presentation.api.schemas import (
    FlightUpdateRequest,
    FlightLocationRequest,
)
from src.trips.presentation.mappers.trip_mapper import TripMapper
from src.trips.domain.entities.flight import Flight
from src.trips.domain.value_objects.airport import Airport
from src.trips.domain.value_objects.money import Money


def make_flight() -> Flight:
    return Flight(
        id="f1",
        airline="Iberia",
        flight_number="IB3166",
        departure_airport=Airport(code="BCN", city="Barcelona"),
        departure_time=datetime(2025, 7, 1, 10, 0),
        arrival_airport=Airport(code="LHR", city="London"),
        arrival_time=datetime(2025, 7, 1, 12, 30),
        duration="2h 30m",
        price=Money.from_float(150.0),
        stops=0,
        cabin_class="Economy",
        status="pending",
    )


class TestApplyFlightUpdate:

    def test_preserves_id_and_untouched_fields_on_partial_update(self):
        flight = make_flight()

        result = TripMapper.apply_flight_update(
            flight, FlightUpdateRequest(airline="Ryanair")
        )

        assert result.id == "f1"
        assert result.airline == "Ryanair"
        assert result.flight_number == "IB3166"
        assert result.departure_airport.code == "BCN"
        assert result.arrival_time == datetime(2025, 7, 1, 12, 30)
        assert result.duration == "2h 30m"
        assert result.price.amount == 150.0
        assert result.stops == 0
        assert result.cabin_class == "Economy"
        assert result.status == "pending"

    def test_applies_all_provided_fields(self):
        flight = make_flight()
        request = FlightUpdateRequest(
            airline="Vueling",
            flightNumber="VY1234",
            departure=FlightLocationRequest(
                airport="MAD", city="Madrid", time=datetime(2025, 7, 2, 8, 0)
            ),
            arrival=FlightLocationRequest(
                airport="BCN", city="Barcelona", time=datetime(2025, 7, 2, 9, 15)
            ),
            duration="1h 15m",
            stops=1,
            price=89.99,
            cabinClass="Business",
            status="confirmed",
        )

        result = TripMapper.apply_flight_update(flight, request)

        assert result.id == "f1"
        assert result.airline == "Vueling"
        assert result.flight_number == "VY1234"
        assert result.departure_airport.code == "MAD"
        assert result.departure_airport.city == "Madrid"
        assert result.departure_time == datetime(2025, 7, 2, 8, 0)
        assert result.arrival_airport.code == "BCN"
        assert result.arrival_time == datetime(2025, 7, 2, 9, 15)
        assert result.duration == "1h 15m"
        assert result.price.amount == 89.99
        assert result.stops == 1
        assert result.cabin_class == "Business"
        assert result.status == "confirmed"

    def test_partial_departure_replaces_location_as_a_unit(self):
        flight = make_flight()
        request = FlightUpdateRequest(
            departure=FlightLocationRequest(
                airport="MAD", city="Madrid", time=datetime(2025, 7, 1, 6, 0)
            )
        )

        result = TripMapper.apply_flight_update(flight, request)

        assert result.departure_airport.code == "MAD"
        assert result.departure_airport.city == "Madrid"
        assert result.departure_time == datetime(2025, 7, 1, 6, 0)
        assert result.arrival_airport.code == "LHR"

    def test_price_converted_to_money(self):
        flight = make_flight()

        result = TripMapper.apply_flight_update(
            flight, FlightUpdateRequest(price=200.0)
        )

        assert isinstance(result.price, Money)
        assert result.price.amount == 200.0
