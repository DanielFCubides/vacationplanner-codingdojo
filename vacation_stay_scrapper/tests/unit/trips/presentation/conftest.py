"""
Shared fixtures for UI flow tests.

Only auth and the repository are swapped out: use cases, the Trip aggregate
and the mappers run for real, so each test replays what the fe-client does
against the API. Request bodies mirror what the UI actually sends
(NewTripWizard, TripFlightForm, TripAccommodationForm, patchChildStatus).
"""
import pytest
from fastapi.testclient import TestClient

from main import app
from src.shared.infrastructure.auth.dependencies import get_current_user
from src.trips.infrastructure.persistence.in_memory_trip_repository import InMemoryTripRepository
from src.trips.presentation.api.dependencies import get_trip_repository


class UiSession:
    """A TestClient whose authenticated user can be switched mid-test."""

    def __init__(self, client: TestClient):
        self.client = client
        self.user = "user-1"

    def as_user(self, sub: str) -> "UiSession":
        self.user = sub
        return self

    def __getattr__(self, name):
        return getattr(self.client, name)


@pytest.fixture
def repo() -> InMemoryTripRepository:
    return InMemoryTripRepository()


@pytest.fixture
def ui(repo):
    session = UiSession(TestClient(app))
    app.dependency_overrides[get_current_user] = lambda: {"sub": session.user}
    app.dependency_overrides[get_trip_repository] = lambda: repo
    yield session
    app.dependency_overrides.clear()


def wizard_flight(**overrides) -> dict:
    """Flight entry as NewTripWizard serializes it (price/duration are placeholders)."""
    flight = {
        "id": "flight_1700000000000_0",
        "airline": "Air France",
        "flightNumber": "AF123",
        "departure": {"airport": "BOG", "city": "BOG", "time": "2026-09-19T17:00:00.000Z"},
        "arrival": {"airport": "CDG", "city": "CDG", "time": "2026-09-20T13:00:00.000Z"},
        "duration": "1",
        "stops": 0,
        "price": 0,
        "cabinClass": "Economy",
        "status": "pending",
    }
    flight.update(overrides)
    return flight


def wizard_accommodation(**overrides) -> dict:
    """Accommodation entry as NewTripWizard serializes it (total = nights x rate, rating 0)."""
    accommodation = {
        "id": "accommodation_1700000000000",
        "name": "Hotel Lutetia",
        "type": "hotel",
        "image": "",
        "checkIn": "2026-09-20",
        "checkOut": "2026-09-23",
        "pricePerNight": 200,
        "totalPrice": 600,
        "rating": 0,
        "amenities": [],
        "status": "pending",
    }
    accommodation.update(overrides)
    return accommodation


def wizard_activity(**overrides) -> dict:
    activity = {
        "id": "activity_1700000000000",
        "name": "Louvre tour",
        "date": "2026-09-21",
        "cost": 45,
        "status": "pending",
        "category": "Culture",
        "description": "",
    }
    activity.update(overrides)
    return activity


def wizard_traveler(**overrides) -> dict:
    traveler = {
        "id": "traveler_1700000000000",
        "name": "Ana Gomez",
        "email": "ana@example.com",
        "role": "editor",
        "avatar": "AG",
    }
    traveler.update(overrides)
    return traveler


def wizard_trip_body(**overrides) -> dict:
    """Overview-only trip as NewTripWizard sends it when optional steps are skipped."""
    body = {
        "name": "Eurotrip",
        "destination": "Paris",
        "startDate": "2026-09-19",
        "endDate": "2026-09-27",
        "status": "planning",
        "travelers": [],
        "flights": [],
        "accommodations": [],
        "activities": [],
        "budget": {"total": 5000, "spent": 0, "categories": []},
    }
    body.update(overrides)
    return body


def flight_form_body(**overrides) -> dict:
    """FlightInput as TripFlightForm submits it (add and edit)."""
    body = {
        "airline": "Air France",
        "flightNumber": "AF123",
        "departure": {"airport": "BOG", "city": "Bogota", "time": "2026-09-19T17:00:00.000Z"},
        "arrival": {"airport": "CDG", "city": "Paris", "time": "2026-09-20T13:00:00.000Z"},
        "duration": "11h",
        "stops": 0,
        "price": 850.5,
        "cabinClass": "Economy",
    }
    body.update(overrides)
    return body


def accommodation_form_body(**overrides) -> dict:
    """AccommodationInput as TripAccommodationForm submits it."""
    body = {
        "name": "Hotel Lutetia",
        "type": "hotel",
        "checkIn": "2026-09-20",
        "checkOut": "2026-09-23",
        "pricePerNight": 200,
        "totalPrice": 650.5,
        "rating": None,
        "amenities": [],
    }
    body.update(overrides)
    return body
