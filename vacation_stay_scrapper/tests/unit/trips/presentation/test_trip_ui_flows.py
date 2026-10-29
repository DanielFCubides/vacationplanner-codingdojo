"""
UI flow tests: replay each fe-client screen's calls against the real API stack
(routes -> use cases -> Trip aggregate -> mappers) with an in-memory repository.

See conftest.py for the request bodies, which mirror what the UI sends.
"""
import pytest

from .conftest import (
    accommodation_form_body,
    flight_form_body,
    wizard_accommodation,
    wizard_activity,
    wizard_flight,
    wizard_traveler,
    wizard_trip_body,
)

TRIPS = "/api/trips"


def create_trip(ui, **overrides) -> dict:
    response = ui.post(TRIPS, json=wizard_trip_body(**overrides))
    assert response.status_code == 201, response.text
    return response.json()


def add_flight(ui, trip_id: str, **overrides) -> dict:
    response = ui.post(f"{TRIPS}/{trip_id}/flights", json=flight_form_body(**overrides))
    assert response.status_code == 201, response.text
    return response.json()["flights"][-1]


def add_accommodation(ui, trip_id: str, **overrides) -> dict:
    response = ui.post(
        f"{TRIPS}/{trip_id}/accommodations", json=accommodation_form_body(**overrides)
    )
    assert response.status_code == 201, response.text
    return response.json()["accommodations"][-1]


def set_status(ui, trip_id: str, child: str, child_id: str, status: str):
    return ui.patch(f"{TRIPS}/{trip_id}/{child}/{child_id}/status", json={"status": status})


def spent(ui, trip_id: str) -> float:
    return ui.get(f"{TRIPS}/{trip_id}").json()["budget"]["spent"]


class TestNewTripWizard:

    def test_full_wizard_creates_trip_with_every_child_pending(self, ui, repo):
        body = wizard_trip_body(
            travelers=[wizard_traveler()],
            flights=[wizard_flight()],
            accommodations=[wizard_accommodation()],
            activities=[wizard_activity()],
        )

        response = ui.post(TRIPS, json=body)

        assert response.status_code == 201
        trip = response.json()
        assert trip["id"]
        assert trip["status"] == "planning"
        assert trip["budget"] == {"total": 5000, "spent": 0, "categories": []}
        children = trip["travelers"] + trip["flights"] + trip["accommodations"] + trip["activities"]
        assert len(children) == 4
        # Server assigns its own ids instead of the wizard's temporary ones
        assert all(not c["id"].startswith(("flight_", "accommodation_", "activity_", "traveler_"))
                   for c in children)
        assert all(c["status"] == "pending"
                   for c in trip["flights"] + trip["accommodations"] + trip["activities"])

    def test_owner_comes_from_token_not_body(self, ui, repo):
        trip = create_trip(ui)

        assert repo._storage[int(trip["id"])].owner_id == "user-1"

    def test_overview_only_trip_is_created(self, ui):
        trip = create_trip(ui, budget={"total": 0, "spent": 0, "categories": []})

        assert trip["flights"] == trip["accommodations"] == trip["activities"] == []

    def test_end_date_before_start_date_is_rejected(self, ui):
        response = ui.post(TRIPS, json=wizard_trip_body(startDate="2026-09-27", endDate="2026-09-19"))

        assert response.status_code == 422

    def test_flight_with_placeholder_price_is_accepted(self, ui):
        trip = create_trip(ui, flights=[wizard_flight(price=0)])

        assert trip["flights"][0]["price"] == 0

    def test_stay_without_price_is_rejected_today(self, ui):
        # Known gap: the wizard sends pricePerNight/totalPrice 0 when the user
        # skips the price, but the API requires both > 0, so the whole trip
        # creation fails with 422.
        body = wizard_trip_body(
            accommodations=[wizard_accommodation(pricePerNight=0, totalPrice=0)]
        )

        response = ui.post(TRIPS, json=body)

        assert response.status_code == 422


class TestTripPlansList:

    def test_lists_only_the_callers_trips(self, ui):
        create_trip(ui, name="Mine")
        ui.as_user("user-2")
        create_trip(ui, name="Theirs")
        ui.as_user("user-1")

        response = ui.get(TRIPS)

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert [t["name"] for t in body["trips"]] == ["Mine"]

    def test_user_without_trips_sees_empty_list(self, ui):
        create_trip(ui)

        response = ui.as_user("user-2").get(TRIPS)

        assert response.json() == {"trips": [], "total": 0}


class TestTripDetails:

    def test_returns_full_trip_shape_the_ui_reads(self, ui):
        created = create_trip(ui, accommodations=[wizard_accommodation()])

        response = ui.get(f"{TRIPS}/{created['id']}")

        assert response.status_code == 200
        trip = response.json()
        assert trip["startDate"] == "2026-09-19"
        assert trip["endDate"] == "2026-09-27"
        accommodation = trip["accommodations"][0]
        assert {"checkIn", "checkOut", "pricePerNight", "totalPrice", "rating", "amenities"} <= accommodation.keys()

    def test_missing_trip_returns_404(self, ui):
        assert ui.get(f"{TRIPS}/999").status_code == 404

    def test_someone_elses_trip_returns_404(self, ui):
        trip = create_trip(ui)

        assert ui.as_user("user-2").get(f"{TRIPS}/{trip['id']}").status_code == 404


class TestTripStatus:

    def test_changes_status(self, ui):
        trip = create_trip(ui)

        response = ui.patch(f"{TRIPS}/{trip['id']}/status", json={"status": "confirmed"})

        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"
        assert ui.get(f"{TRIPS}/{trip['id']}").json()["status"] == "confirmed"

    def test_unknown_status_returns_422(self, ui):
        trip = create_trip(ui)

        response = ui.patch(f"{TRIPS}/{trip['id']}/status", json={"status": "booked"})

        assert response.status_code == 422

    def test_someone_elses_trip_returns_404(self, ui):
        trip = create_trip(ui)

        response = ui.as_user("user-2").patch(
            f"{TRIPS}/{trip['id']}/status", json={"status": "confirmed"}
        )

        assert response.status_code == 404


class TestFlightsTab:

    def test_add_edit_confirm_cancel_journey_tracks_spent(self, ui):
        trip_id = create_trip(ui)["id"]

        flight = add_flight(ui, trip_id)
        assert flight["status"] == "pending"
        assert spent(ui, trip_id) == 0

        edited = ui.put(
            f"{TRIPS}/{trip_id}/flights/{flight['id']}", json=flight_form_body(price=900)
        )
        assert edited.status_code == 200
        [edited_flight] = edited.json()["flights"]
        assert edited_flight["id"] == flight["id"]
        assert edited_flight["price"] == 900

        confirmed = set_status(ui, trip_id, "flights", flight["id"], "confirmed")
        assert confirmed.status_code == 200
        assert confirmed.json()["budget"]["spent"] == 900

        cancelled = set_status(ui, trip_id, "flights", flight["id"], "cancelled")
        assert cancelled.status_code == 200
        assert cancelled.json()["budget"]["spent"] == 0

    def test_adding_a_flight_keeps_other_children(self, ui):
        trip_id = create_trip(ui, accommodations=[wizard_accommodation()])["id"]

        add_flight(ui, trip_id)

        trip = ui.get(f"{TRIPS}/{trip_id}").json()
        assert len(trip["flights"]) == 1
        assert len(trip["accommodations"]) == 1

    def test_illegal_transition_returns_422(self, ui):
        trip_id = create_trip(ui)["id"]
        flight = add_flight(ui, trip_id)
        set_status(ui, trip_id, "flights", flight["id"], "confirmed")

        response = set_status(ui, trip_id, "flights", flight["id"], "pending")

        assert response.status_code == 422

    def test_edit_with_arrival_before_departure_returns_422(self, ui):
        trip_id = create_trip(ui)["id"]
        flight = add_flight(ui, trip_id)

        response = ui.put(
            f"{TRIPS}/{trip_id}/flights/{flight['id']}",
            json=flight_form_body(
                arrival={"airport": "CDG", "city": "Paris", "time": "2026-09-19T10:00:00.000Z"}
            ),
        )

        assert response.status_code == 422

    def test_unknown_flight_returns_404(self, ui):
        trip_id = create_trip(ui)["id"]

        assert set_status(ui, trip_id, "flights", "nope", "confirmed").status_code == 404
        assert ui.put(f"{TRIPS}/{trip_id}/flights/nope", json=flight_form_body()).status_code == 404


class TestStaysTab:

    def test_add_confirm_cancel_journey_tracks_accommodation_total(self, ui):
        trip_id = create_trip(ui)["id"]

        accommodation = add_accommodation(ui, trip_id, totalPrice=650.5)
        assert accommodation["status"] == "pending"
        assert accommodation["rating"] is None
        assert spent(ui, trip_id) == 0

        confirmed = set_status(ui, trip_id, "accommodations", accommodation["id"], "confirmed")
        assert confirmed.status_code == 200
        # Accommodation total, not nights x nightly rate (3 x 200 = 600)
        assert confirmed.json()["budget"]["spent"] == 650.5

        cancelled = set_status(ui, trip_id, "accommodations", accommodation["id"], "cancelled")
        assert cancelled.json()["budget"]["spent"] == 0

    @pytest.mark.parametrize("accommodation_type", ["hotel", "airbnb", "hostel", "resort"])
    def test_every_accommodation_type_can_be_added(self, ui, accommodation_type):
        trip_id = create_trip(ui)["id"]

        accommodation = add_accommodation(ui, trip_id, type=accommodation_type)

        assert accommodation["type"] == accommodation_type

    def test_added_accommodation_is_listed_on_trip_details(self, ui):
        trip_id = create_trip(ui)["id"]
        accommodation = add_accommodation(ui, trip_id, amenities=["WiFi", "Pool"], rating=4.5)

        [listed] = ui.get(f"{TRIPS}/{trip_id}").json()["accommodations"]

        assert listed["id"] == accommodation["id"]
        assert listed["amenities"] == ["WiFi", "Pool"]
        assert listed["rating"] == 4.5

    def test_illegal_transition_returns_422(self, ui):
        trip_id = create_trip(ui)["id"]
        accommodation = add_accommodation(ui, trip_id)
        set_status(ui, trip_id, "accommodations", accommodation["id"], "confirmed")

        response = set_status(ui, trip_id, "accommodations", accommodation["id"], "pending")

        assert response.status_code == 422

    def test_unknown_accommodation_returns_404(self, ui):
        trip_id = create_trip(ui)["id"]

        assert set_status(ui, trip_id, "accommodations", "nope", "confirmed").status_code == 404


class TestActivitiesTab:

    def test_booking_adds_cost_and_cancelling_removes_it(self, ui):
        trip = create_trip(ui, activities=[wizard_activity(cost=45)])
        activity_id = trip["activities"][0]["id"]

        booked = set_status(ui, trip["id"], "activities", activity_id, "booked")
        assert booked.status_code == 200
        assert booked.json()["budget"]["spent"] == 45

        cancelled = set_status(ui, trip["id"], "activities", activity_id, "cancelled")
        assert cancelled.json()["budget"]["spent"] == 0

    def test_confirmed_is_not_an_activity_status(self, ui):
        trip = create_trip(ui, activities=[wizard_activity()])
        activity_id = trip["activities"][0]["id"]

        response = set_status(ui, trip["id"], "activities", activity_id, "confirmed")

        assert response.status_code == 422


def budget_form_body(**overrides) -> dict:
    """Budget as the Budget tab edit form submits it."""
    body = {
        "total": 3000,
        "categories": [
            {"category": "Food", "planned": 600, "spent": 120},
            {"category": "Transport", "planned": 400, "spent": 0},
        ],
    }
    body.update(overrides)
    return body


def put_budget(ui, trip_id: str, **overrides):
    return ui.put(f"{TRIPS}/{trip_id}/budget", json=budget_form_body(**overrides))


class TestBudgetTab:

    def test_edit_total_and_categories_keeps_spent_derived(self, ui):
        trip_id = create_trip(ui)["id"]
        flight = add_flight(ui, trip_id, price=900)
        set_status(ui, trip_id, "flights", flight["id"], "confirmed")

        response = put_budget(ui, trip_id)

        assert response.status_code == 200
        assert response.json()["budget"] == {
            "total": 3000,
            "spent": 900,
            "categories": [
                {"category": "Food", "planned": 600, "spent": 120},
                {"category": "Transport", "planned": 400, "spent": 0},
            ],
        }
        assert ui.get(f"{TRIPS}/{trip_id}").json()["budget"]["total"] == 3000

    def test_spent_sent_by_the_client_is_ignored(self, ui):
        trip_id = create_trip(ui)["id"]

        response = ui.put(
            f"{TRIPS}/{trip_id}/budget", json={**budget_form_body(), "spent": 999}
        )

        assert response.json()["budget"]["spent"] == 0

    def test_removing_every_category_and_zero_total_is_allowed(self, ui):
        trip_id = create_trip(ui)["id"]
        put_budget(ui, trip_id)

        response = put_budget(ui, trip_id, total=0, categories=[])

        assert response.status_code == 200
        assert response.json()["budget"] == {"total": 0, "spent": 0, "categories": []}

    def test_total_below_spent_is_allowed(self, ui):
        trip_id = create_trip(ui)["id"]
        flight = add_flight(ui, trip_id, price=900)
        set_status(ui, trip_id, "flights", flight["id"], "confirmed")

        response = put_budget(ui, trip_id, total=500)

        assert response.status_code == 200
        assert response.json()["budget"]["spent"] == 900

    def test_duplicate_category_names_return_422(self, ui):
        trip_id = create_trip(ui)["id"]

        response = put_budget(ui, trip_id, categories=[
            {"category": "Food", "planned": 100, "spent": 0},
            {"category": " food ", "planned": 50, "spent": 0},
        ])

        assert response.status_code == 422
        assert ui.get(f"{TRIPS}/{trip_id}").json()["budget"]["total"] == 5000

    @pytest.mark.parametrize("body", [
        {"total": -1},
        {"categories": [{"category": "Food", "planned": -1, "spent": 0}]},
        {"categories": [{"category": "Food", "planned": 10, "spent": -1}]},
        {"categories": [{"category": "", "planned": 10, "spent": 0}]},
        {"categories": [{"category": "   ", "planned": 10, "spent": 0}]},
    ])
    def test_invalid_budget_returns_422(self, ui, body):
        trip_id = create_trip(ui)["id"]

        assert put_budget(ui, trip_id, **body).status_code == 422

    def test_missing_trip_returns_404(self, ui):
        assert put_budget(ui, "999").status_code == 404

    def test_trip_update_cannot_overwrite_spent(self, ui):
        trip_id = create_trip(ui)["id"]

        response = ui.put(
            f"{TRIPS}/{trip_id}",
            json={"budget": {"total": 100, "spent": 999, "categories": []}},
        )

        assert response.status_code == 200
        assert response.json()["budget"]["spent"] == 0

    def test_trip_creation_cannot_set_spent(self, ui):
        trip = create_trip(ui, budget={"total": 100, "spent": 999, "categories": []})

        assert trip["budget"]["spent"] == 0


class TestOwnership:

    @pytest.fixture
    def foreign_trip(self, ui):
        trip = create_trip(
            ui, accommodations=[wizard_accommodation()], activities=[wizard_activity()]
        )
        flight = add_flight(ui, trip["id"])
        ui.as_user("user-2")
        return trip, flight

    def test_cannot_add_children_to_someone_elses_trip(self, ui, foreign_trip):
        trip, _ = foreign_trip

        assert ui.post(f"{TRIPS}/{trip['id']}/flights", json=flight_form_body()).status_code == 404
        assert ui.post(
            f"{TRIPS}/{trip['id']}/accommodations", json=accommodation_form_body()
        ).status_code == 404
        assert put_budget(ui, trip["id"]).status_code == 404

    def test_cannot_change_children_of_someone_elses_trip(self, ui, foreign_trip):
        trip, flight = foreign_trip
        trip_id = trip["id"]

        assert ui.put(
            f"{TRIPS}/{trip_id}/flights/{flight['id']}", json=flight_form_body()
        ).status_code == 404
        assert set_status(ui, trip_id, "flights", flight["id"], "confirmed").status_code == 404
        assert set_status(
            ui, trip_id, "accommodations", trip["accommodations"][0]["id"], "confirmed"
        ).status_code == 404
        assert set_status(
            ui, trip_id, "activities", trip["activities"][0]["id"], "booked"
        ).status_code == 404

    def test_owner_trip_is_left_untouched(self, ui, foreign_trip):
        trip, _ = foreign_trip
        ui.post(f"{TRIPS}/{trip['id']}/flights", json=flight_form_body())

        owner_view = ui.as_user("user-1").get(f"{TRIPS}/{trip['id']}").json()

        assert len(owner_view["flights"]) == 1
