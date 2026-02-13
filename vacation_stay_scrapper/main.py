"""
Vacation Planner API - Main Entry Point

This is a temporary main.py that uses the new shared infrastructure
while we complete the full migration to clean architecture.
"""
from datetime import date
from typing import Optional, Annotated

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from starlette import status

# Import from new shared infrastructure
from src.shared.infrastructure.auth.dependencies import get_current_user
from src.shared.presentation.middleware import setup_middleware
from src.shared.infrastructure.http.http_connector import HTTPConnector

# Old imports (will be migrated in next steps)
from services.flight_scrapper import FlightScrapper

# Create FastAPI app
app = FastAPI(
    title="Vacation Planner API",
    description="API for managing vacation plans, flights, and stays",
    version="1.0.0"
)

# Setup middleware (CORS, logging, exception handling)
setup_middleware(app)

# Initialize services (temporary - will be moved to DI container)
FLIGHT_SCRAPPER_SERVICE = 'localhost:8000/'
http_connector = HTTPConnector(
    url=FLIGHT_SCRAPPER_SERVICE,
    failure_attempts=3,
    delay=60
)
flight_services = FlightScrapper(http_connector)


# Request/Response Models
class SearchParams(BaseModel):
    """Flight search parameters"""
    origin: str
    destination: str
    arrival_date: date
    passengers: int = 1
    checked_baggage: int = 0
    carry_on_baggage: int = 1
    return_date: Optional[date] = None


# Routes
@app.get(
    '/',
    tags=["Health"],
    summary="Health check endpoint"
)
def index(
    user: Annotated[dict, Depends(get_current_user)]
):
    """
    Health check endpoint
    
    Requires authentication.
    """
    return {
        'message': 'Vacation Planner API is running',
        'status': 'healthy',
        'user': user.get('preferred_username', 'unknown')
    }


@app.post(
    '/vacation-plan',
    status_code=status.HTTP_200_OK,
    tags=["Vacation Plans"],
    summary="Search for vacation plans"
)
def get_vacation_plan(
    search_params: SearchParams,
    user: Annotated[dict, Depends(get_current_user)]
):
    """
    Search for vacation plans based on search criteria
    
    Requires authentication.
    
    Returns a list of available vacation plans matching the search parameters.
    """
    # TODO: Replace with actual service call
    # For now, return mock data
    return [
        {
            "id": 1,
            "title": f"Weekend in {search_params.destination}",
            "origin": search_params.origin,
            "destination": search_params.destination,
            "departureDate": search_params.arrival_date.isoformat(),
            "returnDate": search_params.return_date.isoformat() if search_params.return_date else None,
            "passengers": search_params.passengers,
            "flightPrice": 925.30,
            "status": "confirmed"
        }
    ]


# Additional routes can be added here
# In the future, these will be organized into domain-specific routers

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
