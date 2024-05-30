from typing import Any

from graphene import Schema, ObjectType, String, Float, List, Field, Int

from flights.infrastructure.flight_finder import FlightFinderWithConstant


flight_repo = FlightFinderWithConstant()


class Flight(ObjectType):
    departure_date = String()
    cost = Float()
    return_date = String()

    def resolve_departure_date(self: dict[str, Any], info):
        return self.get('departureDate')

    def resolve_cost(self: dict[str, Any], info):
        taxes = self.get('prices').get('totalPrices')[0].get('totalTaxes')
        base_price = self.get('prices').get('totalPrices')[0].get('total')
        return base_price + taxes

    def resolve_return_date(self: dict[str, Any], info):
        return self.get('returnDate')


class RootQuery(ObjectType):
    flights = List(Flight)
    flight = Field(Flight, id_=Int())

    def resolve_flights(self, info):
        results = flight_repo.get_all()
        return results

    def resolve_flight(self, info, id_: int):
        flight = flight_repo.get(id_fly=id_)
        return flight if flight else None


class Query(ObjectType):
    hello = String(description='A typical hello world')

    def resolve_hello(self, info):
        return 'World'


my_schema = Schema(query=RootQuery)
