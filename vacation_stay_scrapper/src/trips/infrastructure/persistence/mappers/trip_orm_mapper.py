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
from src.trips.infrastructure.persistence.models.accommodation_model import AccommodationModel
from src.trips.infrastructure.persistence.models.activity_model import ActivityModel
from src.trips.infrastructure.persistence.models.budget_category_model import BudgetCategoryModel
from src.trips.infrastructure.persistence.models.flight_model import FlightModel
from src.trips.infrastructure.persistence.models.traveler_model import TravelerModel
from src.trips.infrastructure.persistence.models.trip_model import TripModel


class TripOrmMapper:

    @staticmethod
    def to_domain(model: TripModel) -> Trip:
        travelers = [
            Traveler(
                id=t.id,
                name=t.name,
                email=t.email,
                role=t.role,
                avatar=t.avatar,
            )
            for t in model.travelers
        ]

        flights = [
            Flight(
                id=f.id,
                airline=f.airline,
                flight_number=f.flight_number,
                departure_airport=Airport(code=f.departure_airport_code, city=f.departure_airport_city),
                departure_time=f.departure_time,
                arrival_airport=Airport(code=f.arrival_airport_code, city=f.arrival_airport_city),
                arrival_time=f.arrival_time,
                duration=f.duration,
                price=Money(amount=f.price_amount, currency=f.price_currency),
                stops=f.stops,
                cabin_class=f.cabin_class,
                status=f.status,
            )
            for f in model.flights
        ]

        accommodations = [
            Accommodation(
                id=a.id,
                name=a.name,
                type=a.type,
                check_in=a.check_in,
                check_out=a.check_out,
                price_per_night=Money(amount=a.price_per_night_amount, currency=a.price_per_night_currency),
                total_price=Money(amount=a.total_price_amount, currency=a.total_price_currency),
                rating=a.rating,
                amenities=a.amenities,
                status=a.status,
                image=a.image,
            )
            for a in model.accommodations
        ]

        activities = [
            Activity(
                id=act.id,
                name=act.name,
                date=act.date,
                cost=Money(amount=act.cost_amount, currency=act.cost_currency),
                category=act.category,
                status=act.status,
                description=act.description,
            )
            for act in model.activities
        ]

        budget = None
        if model.budget_total_amount is not None:
            categories = [
                BudgetCategory(
                    category=bc.category,
                    planned=Money(amount=bc.planned_amount, currency=bc.planned_currency),
                    spent=Money(amount=bc.spent_amount, currency=bc.spent_currency),
                )
                for bc in model.budget_categories
            ]
            budget = Budget(
                total=Money(
                    amount=model.budget_total_amount,
                    currency=model.budget_total_currency or "USD",
                ),
                spent=Money(
                    amount=model.budget_spent_amount or Decimal("0"),
                    currency=model.budget_spent_currency or "USD",
                ),
                categories=categories,
            )

        return Trip(
            id=model.id,
            owner_id=model.owner_id,
            name=model.name,
            destination=model.destination,
            start_date=model.start_date,
            end_date=model.end_date,
            status=TripStatus(model.status),
            travelers=travelers,
            flights=flights,
            accommodations=accommodations,
            activities=activities,
            budget=budget,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(trip: Trip) -> TripModel:
        model = TripModel(
            owner_id=trip.owner_id,
            name=trip.name,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            status=trip.status.value,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

        if trip.id is not None:
            model.id = trip.id

        if trip.budget is not None:
            model.budget_total_amount = trip.budget.total.amount
            model.budget_total_currency = trip.budget.total.currency
            model.budget_spent_amount = trip.budget.spent.amount
            model.budget_spent_currency = trip.budget.spent.currency
            model.budget_categories = [
                BudgetCategoryModel(
                    category=bc.category,
                    planned_amount=bc.planned.amount,
                    planned_currency=bc.planned.currency,
                    spent_amount=bc.spent.amount,
                    spent_currency=bc.spent.currency,
                )
                for bc in trip.budget.categories
            ]

        model.travelers = [
            TravelerModel(
                id=t.id,
                name=t.name,
                email=t.email,
                role=t.role,
                avatar=t.avatar,
            )
            for t in trip.travelers
        ]

        model.flights = [
            FlightModel(
                id=f.id,
                airline=f.airline,
                flight_number=f.flight_number,
                departure_airport_code=f.departure_airport.code,
                departure_airport_city=f.departure_airport.city,
                departure_time=f.departure_time,
                arrival_airport_code=f.arrival_airport.code,
                arrival_airport_city=f.arrival_airport.city,
                arrival_time=f.arrival_time,
                duration=f.duration,
                price_amount=f.price.amount,
                price_currency=f.price.currency,
                stops=f.stops,
                cabin_class=f.cabin_class,
                status=f.status,
            )
            for f in trip.flights
        ]

        model.accommodations = [
            AccommodationModel(
                id=a.id,
                name=a.name,
                type=a.type,
                check_in=a.check_in,
                check_out=a.check_out,
                price_per_night_amount=a.price_per_night.amount,
                price_per_night_currency=a.price_per_night.currency,
                total_price_amount=a.total_price.amount,
                total_price_currency=a.total_price.currency,
                rating=a.rating,
                amenities=a.amenities,
                status=a.status,
                image=a.image,
            )
            for a in trip.accommodations
        ]

        model.activities = [
            ActivityModel(
                id=act.id,
                name=act.name,
                date=act.date,
                cost_amount=act.cost.amount,
                cost_currency=act.cost.currency,
                category=act.category,
                status=act.status,
                description=act.description,
            )
            for act in trip.activities
        ]

        return model
