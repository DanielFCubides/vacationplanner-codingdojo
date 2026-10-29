"""
Route tests for POST /api/trips/{trip_id}/flights.

Auth and the use case are overridden so only the presentation layer
(request mapping, forced pending status, error mapping) is exercised.
"""
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from main import app
from src.shared.domain.exceptions import EntityNotFound
from src.shared.infrastructure.auth.dependencies import get_current_user
from src.trips.domain.entities.trip import Trip
from src.trips.domain.value_objects.trip_status import TripStatus
from src.trips.presentation.api.dependencies import get_add_flight_use_case
from datetime import date


def flight_body(**overrides) -> dict:
    body = {
        "airline": "Air France",
        "flightNumber": "AF123",
        "departure": {"airport": "BOG", "city": "Bogota", "time": "2026-09-19T17:00:00Z"},
        "arrival": {"airport": "CDG", "city": "Paris", "time": "2026-09-20T13:00:00Z"},
        "duration": "11h",
        "stops": 0,
        "price": 850.5,
        "cabinClass": "Economy",
        "status": "confirmed",
    }
    body.update(overrides)
    return body


@pytest.fixture
def use_case():
    async def execute(trip_id, flight, owner_id):
        trip = Trip(
            id=int(trip_id), owner_id=owner_id, name="Eurotrip",
            destination="Paris", start_date=date(2026, 9, 19),
            end_date=date(2026, 9, 27), status=TripStatus.PLANNING,
        )
        trip.add_flight(flight)
        return trip

    mock = AsyncMock()
    mock.execute.side_effect = execute
    return mock


@pytest.fixture
def client(use_case):
    app.dependency_overrides[get_current_user] = lambda: {"sub": "user-1"}
    app.dependency_overrides[get_add_flight_use_case] = lambda: use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestAddFlightRoute:

    def test_returns_201_with_new_flight_forced_to_pending(self, client, use_case):
        response = client.post("/api/trips/1/flights", json=flight_body())

        assert response.status_code == 201
        flights = response.json()["flights"]
        assert len(flights) == 1
        assert flights[0]["airline"] == "Air France"
        assert flights[0]["status"] == "pending"
        assert flights[0]["id"]
        _, kwargs = use_case.execute.call_args
        assert kwargs["owner_id"] == "user-1"

    def test_arrival_before_departure_returns_422(self, client):
        body = flight_body(
            arrival={"airport": "CDG", "city": "Paris", "time": "2026-09-19T10:00:00Z"}
        )

        response = client.post("/api/trips/1/flights", json=body)

        assert response.status_code == 422

    def test_missing_trip_returns_404(self, client, use_case):
        use_case.execute.side_effect = EntityNotFound(entity_type="Trip", entity_id="999")

        response = client.post("/api/trips/999/flights", json=flight_body())

        assert response.status_code == 404
