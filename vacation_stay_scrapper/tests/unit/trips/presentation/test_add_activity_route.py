"""
Route tests for POST /api/trips/{trip_id}/activities.

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
from src.trips.presentation.api.dependencies import get_add_activity_use_case
from datetime import date


def activity_body(**overrides) -> dict:
    body = {
        "name": "Louvre tour",
        "date": "2026-09-21",
        "cost": 45,
        "category": "Sightseeing",
        "description": "Skip the line",
        "status": "booked",
    }
    body.update(overrides)
    return body


@pytest.fixture
def use_case():
    async def execute(trip_id, activity, owner_id):
        trip = Trip(
            id=int(trip_id), owner_id=owner_id, name="Eurotrip",
            destination="Paris", start_date=date(2026, 9, 19),
            end_date=date(2026, 9, 27), status=TripStatus.PLANNING,
        )
        trip.add_activity(activity)
        return trip

    mock = AsyncMock()
    mock.execute.side_effect = execute
    return mock


@pytest.fixture
def client(use_case):
    app.dependency_overrides[get_current_user] = lambda: {"sub": "user-1"}
    app.dependency_overrides[get_add_activity_use_case] = lambda: use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestAddActivityRoute:

    def test_returns_201_with_new_activity_forced_to_pending(self, client, use_case):
        response = client.post("/api/trips/1/activities", json=activity_body())

        assert response.status_code == 201
        activities = response.json()["activities"]
        assert len(activities) == 1
        assert activities[0]["name"] == "Louvre tour"
        assert activities[0]["category"] == "Sightseeing"
        assert activities[0]["status"] == "pending"
        assert activities[0]["id"]
        _, kwargs = use_case.execute.call_args
        assert kwargs["owner_id"] == "user-1"

    def test_free_activity_is_accepted(self, client):
        response = client.post("/api/trips/1/activities", json=activity_body(cost=0))

        assert response.status_code == 201
        assert response.json()["activities"][0]["cost"] == 0

    def test_description_is_optional(self, client):
        body = activity_body()
        del body["description"]

        response = client.post("/api/trips/1/activities", json=body)

        assert response.status_code == 201
        assert response.json()["activities"][0]["description"] == ""

    def test_negative_cost_returns_422(self, client):
        response = client.post("/api/trips/1/activities", json=activity_body(cost=-1))

        assert response.status_code == 422

    @pytest.mark.parametrize("category", ["", "   "])
    def test_blank_category_returns_422(self, client, category):
        response = client.post(
            "/api/trips/1/activities", json=activity_body(category=category)
        )

        assert response.status_code == 422

    def test_missing_trip_returns_404(self, client, use_case):
        use_case.execute.side_effect = EntityNotFound(entity_type="Trip", entity_id="999")

        response = client.post("/api/trips/999/activities", json=activity_body())

        assert response.status_code == 404
