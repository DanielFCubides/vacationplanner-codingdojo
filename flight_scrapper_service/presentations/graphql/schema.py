from datetime import datetime

from graphene import Schema, ObjectType, String, Float, Date, Field

from flights.infrastructure.flight_finder import FlightFinderWithConstant

# Flight Object

flight = {
    "airport": "a",
    "flight_number": "a",
    "cost": "a",
    "arrival_date": "a",
    "return_date": "a"
}

flight_repo = FlightFinderWithConstant()


class Flight(ObjectType):
    airport = String()
    flight_number = String()
    cost = Float()
    arrival_date = Date()
    return_date = Date()

    def resolve_airport(self, info):
        return "EL DORADO"

    def resolve_flight_number(self, info):
        return "AF 1265"

    def resolve_cost(self, info):
        return 3200

    def resolve_arrival_date(self, info):
        return datetime(2019, 5, 27)

    def resolve_return_date(self, info):
        return datetime(2019, 5, 27)


class RootQuery(ObjectType):
    flight = Field(Flight)

    def resolve_flight(self, info):
        result = flight_repo.get_all()[0]

        flight = Flight(airport=result["airport"], flight_number=result["flight_number"], cost=result["cost"],
                        arrival_date=result["arrival_date"], return_date=result["return_date"], )

        print(flight.__dict__)
        return flight


class Query(ObjectType):
    hello = String(description='A typical hello world')

    def resolve_hello(self, info):
        return 'World'


my_schema = Schema(query=RootQuery)
