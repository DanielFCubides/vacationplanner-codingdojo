from typing import Any

from graphene import Schema, ObjectType, String, Float, List, Field, Int

from flights.domain.scrappers.base import create_driver
from flights.infrastructure.avianca import FlightFinderAvianca
from utils.urls import DynamicURL

#flight_repo = FlightFinderAvianca(
#    url=DynamicURL.from_url('https://www.avianca.com/es/booking/select/'),
#    scrapper=AviancaScrapper(driver='firefox', create_driver=create_driver)
#)


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
        #results = flight_repo.get_all()
        #return results
        pass

    def resolve_flight(self, info, id_: int):
        #flight = flight_repo.get(id_fly=id_)
        #return flight if flight else None
        pass


class Query(ObjectType):
    hello = String(description='A typical hello world')

    def resolve_hello(self, info):
        return 'World'


my_schema = Schema(query=RootQuery)
