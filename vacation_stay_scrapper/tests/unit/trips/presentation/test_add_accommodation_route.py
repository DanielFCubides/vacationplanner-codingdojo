"""
Route tests for POST /api/trips/{trip_id}/accommodations.

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
from src.trips.presentation.api.dependencies import get_add_accommodation_use_case
from datetime import date


def accommodation_body(**overrides) -> dict:
    body = {
        "name": "Hotel Lutetia",
        "type": "hotel",
        "checkIn": "2026-09-20",
        "checkOut": "2026-09-23",
        "pricePerNight": 200,
        "totalPrice": 650.5,
        "status": "confirmed",
    }
    body.update(overrides)
    return body


@pytest.fixture
def use_case():
    async def execute(trip_id, accommodation, owner_id):
        trip = Trip(
            id=int(trip_id), owner_id=owner_id, name="Eurotrip",
            destination="Paris", start_date=date(2026, 9, 19),
            end_date=date(2026, 9, 27), status=TripStatus.PLANNING,
        )
        trip.add_accommodation(accommodation)
        return trip

    mock = AsyncMock()
    mock.execute.side_effect = execute
    return mock


@pytest.fixture
def client(use_case):
    app.dependency_overrides[get_current_user] = lambda: {"sub": "user-1"}
    app.dependency_overrides[get_add_accommodation_use_case] = lambda: use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestAddAccommodationRoute:

    def test_returns_201_with_new_accommodation_forced_to_pending(self, client, use_case):
        response = client.post("/api/trips/1/accommodations", json=accommodation_body())

        assert response.status_code == 201
        accommodations = response.json()["accommodations"]
        assert len(accommodations) == 1
        assert accommodations[0]["name"] == "Hotel Lutetia"
        assert accommodations[0]["status"] == "pending"
        assert accommodations[0]["id"]
        _, kwargs = use_case.execute.call_args
        assert kwargs["owner_id"] == "user-1"

    def test_keeps_user_entered_total(self, client):
        response = client.post("/api/trips/1/accommodations", json=accommodation_body())

        assert response.json()["accommodations"][0]["totalPrice"] == 650.5

    def test_rating_and_amenities_are_optional(self, client):
        response = client.post("/api/trips/1/accommodations", json=accommodation_body())

        accommodation = response.json()["accommodations"][0]
        assert accommodation["rating"] is None
        assert accommodation["amenities"] == []

    @pytest.mark.parametrize("accommodation_type", ["hotel", "airbnb", "hostel", "resort"])
    def test_accepts_every_accommodation_type(self, client, accommodation_type):
        response = client.post(
            "/api/trips/1/accommodations",
            json=accommodation_body(type=accommodation_type),
        )

        assert response.status_code == 201
        assert response.json()["accommodations"][0]["type"] == accommodation_type

    def test_unknown_type_returns_422(self, client):
        response = client.post(
            "/api/trips/1/accommodations", json=accommodation_body(type="camping")
        )

        assert response.status_code == 422

    def test_check_out_before_check_in_returns_422(self, client):
        response = client.post(
            "/api/trips/1/accommodations",
            json=accommodation_body(checkIn="2026-09-23", checkOut="2026-09-20"),
        )

        assert response.status_code == 422

    def test_missing_trip_returns_404(self, client, use_case):
        use_case.execute.side_effect = EntityNotFound(entity_type="Trip", entity_id="999")

        response = client.post("/api/trips/999/accommodations", json=accommodation_body())

        assert response.status_code == 404
