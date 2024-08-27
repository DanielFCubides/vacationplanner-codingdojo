from datetime import datetime

FLIGHTS = [
    {
        "origin": "JFK",
        "destination": "LAX",
        "price": 350.00,
        "flight_time": "6h 15m",
        "arrival_date": datetime(2024, 7, 21, 14, 30),
        "return_date": datetime(2024, 7, 28, 10, 45)
    },
    {
        "origin": "LAX",
        "destination": "ORD",
        "price": 250.00,
        "flight_time": "4h 30m",
        "arrival_date": datetime(2024, 7, 22, 16, 0),
        "return_date": datetime(2024, 7, 29, 12, 0)
    },
    {
        "origin": "ORD",
        "destination": "MIA",
        "price": 200.00,
        "flight_time": "3h 45m",
        "arrival_date": datetime(2024, 7, 23, 13, 15),
        "return_date": datetime(2024, 7, 30, 11, 30)
    },
    {
        "origin": "MIA",
        "destination": "DFW",
        "price": 180.00,
        "flight_time": "3h 30m",
        "arrival_date": datetime(2024, 7, 24, 15, 0),
        "return_date": datetime(2024, 7, 31, 10, 15)
    }
]