"""
Round-trip tests for TripOrmMapper.

Every UI save goes through to_model -> Postgres -> to_domain; a field lost or
changed here silently corrupts the trip the UI shows after reload.
"""
from datetime import date, datetime
from decimal import Decimal

from src.trips.domain.entities.accommodation import Accommodation
from src.trips.domain.entities.activity import Activity
from src.trips.domain.entities.flight import Flight
from src.trips.domain.entities.traveler import Traveler
from src.trips.domain.entities.trip import Trip
from src.trips.domain.value_objects.airport import Airport
from src.trips.domain.value_objects.budget import Budget, BudgetCategory
from src.trips.domain.value_objects.money import Money
from src.trips.domain.value_objects.trip_status import TripStatus
from src.trips.infrastructure.persistence.mappers.trip_orm_mapper import TripOrmMapper


def usd(amount: str) -> Money:
    return Money(Decimal(amount), "USD")


def make_full_trip(**overrides) -> Trip:
    defaults = dict(
        id=7,
        owner_id="user-1",
        name="Eurotrip",
        destination="Paris",
        start_date=date(2026, 9, 19),
        end_date=date(2026, 9, 27),
        status=TripStatus.CONFIRMED,
        travelers=[
            Traveler(id="t1", name="Ana Gomez", email="ana@example.com", role="editor", avatar="AG"),
        ],
        flights=[
            Flight(
                id="f1",
                airline="Air France",
                flight_number="AF123",
                departure_airport=Airport(code="BOG", city="Bogota"),
                departure_time=datetime(2026, 9, 19, 17, 0),
                arrival_airport=Airport(code="CDG", city="Paris"),
                arrival_time=datetime(2026, 9, 20, 13, 0),
                duration="11h",
                price=usd("850.50"),
                stops=1,
                cabin_class="Business",
                status="confirmed",
            ),
        ],
        accommodations=[
            Accommodation(
                id="a1",
                name="Hotel Lutetia",
                type="hotel",
                check_in=date(2026, 9, 20),
                check_out=date(2026, 9, 23),
                price_per_night=usd("200.00"),
                total_price=usd("650.50"),
                rating=None,
                amenities=["WiFi", "Pool"],
                status="pending",
                image=None,
            ),
            Accommodation(
                id="a2",
                name="Le Marais loft",
                type="airbnb",
                check_in=date(2026, 9, 23),
                check_out=date(2026, 9, 27),
                price_per_night=usd("120.00"),
                total_price=usd("480.00"),
                rating=4.5,
                amenities=[],
                status="confirmed",
                image="https://example.com/loft.jpg",
            ),
        ],
        activities=[
            Activity(
                id="act1",
                name="Louvre tour",
                date=date(2026, 9, 21),
                cost=usd("45.00"),
                category="Culture",
                status="booked",
                description="Skip the line",
            ),
        ],
        budget=Budget(
            total=usd("5000.00"),
            spent=usd("1375.50"),
            categories=[
                BudgetCategory(category="Stays", planned=usd("1200.00"), spent=usd("480.00")),
            ],
        ),
        created_at=date(2026, 9, 1),
        updated_at=date(2026, 9, 2),
    )
    defaults.update(overrides)
    return Trip(**defaults)


class TestTripOrmMapperRoundTrip:

    def test_full_trip_survives_round_trip(self):
        trip = make_full_trip()

        restored = TripOrmMapper.to_domain(TripOrmMapper.to_model(trip))

        assert restored == trip

    def test_accommodation_without_rating_stays_without_rating(self):
        restored = TripOrmMapper.to_domain(TripOrmMapper.to_model(make_full_trip()))

        assert restored.accommodations[0].rating is None
        assert restored.accommodations[1].rating == 4.5

    def test_user_entered_accommodation_total_is_kept(self):
        restored = TripOrmMapper.to_domain(TripOrmMapper.to_model(make_full_trip()))

        assert restored.accommodations[0].total_price == usd("650.50")

    def test_trip_without_budget_round_trips_to_no_budget(self):
        trip = make_full_trip(budget=None)

        restored = TripOrmMapper.to_domain(TripOrmMapper.to_model(trip))

        assert restored.budget is None

    def test_new_trip_has_no_id_on_the_model(self):
        model = TripOrmMapper.to_model(make_full_trip(id=None))

        assert model.id_ is None
