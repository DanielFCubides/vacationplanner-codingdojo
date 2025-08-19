from datetime import date
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette import status
from services.flight_scrapper import FlightScrapper
from utils.connector import HTTPConnector
from api_documentation import openapi_info, openapi_tags, flight_response_example, error_response_examples

app = FastAPI(
    **openapi_info,
    openapi_tags=openapi_tags
)

FLIGHT_SCRAPPER_SERVICE = 'localhost:8001/'  # Updated to correct port
http_connector = HTTPConnector(FLIGHT_SCRAPPER_SERVICE)
flight_services = FlightScrapper(http_connector)


class SearchParams(BaseModel):
    """Search parameters for flight and vacation planning."""
    origin: str = Field(
        ..., 
        description="Origin city or airport code (e.g., 'BOG', 'Bogota')",
        example="BOG"
    )
    destination: str = Field(
        ..., 
        description="Destination city or airport code (e.g., 'MIA', 'Miami')",
        example="MIA"
    )
    arrival_date: date = Field(
        ..., 
        description="Departure date in YYYY-MM-DD format",
        example="2025-09-15"
    )
    passengers: int = Field(
        default=1, 
        ge=1, 
        le=9,
        description="Number of passengers (1-9)",
        example=2
    )
    checked_baggage: int = Field(
        default=0, 
        ge=0, 
        le=5,
        description="Number of checked bags per passenger",
        example=1
    )
    carry_on_baggage: int = Field(
        default=1, 
        ge=0, 
        le=2,
        description="Number of carry-on bags per passenger",
        example=1
    )
    return_date: Optional[date] = Field(
        default=None,
        description="Return date for round-trip flights (YYYY-MM-DD format)",
        example="2025-09-22"
    )


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    message: str = Field(description="Status message")
    timestamp: Optional[str] = Field(default=None, description="Response timestamp")


class FlightSearchResponse(BaseModel):
    """Flight search response model."""
    flights: List[Dict[str, Any]] = Field(
        description="List of available flights",
        example=flight_response_example["flights"]
    )


@app.get(
    '/', 
    tags=["health"],
    summary="Health Check",
    description="Check if the API service is running and healthy",
    response_model=HealthCheckResponse,
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"message": "health-check"}
                }
            }
        }
    }
)
def index() -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Returns a simple health status to verify the service is running.
    """
    return HealthCheckResponse(message="health-check")


@app.post(
    '/vacation-plan', 
    tags=["vacation-planning"],
    summary="Search Flights for Vacation Planning",
    description="""
    Search for flights based on travel parameters.
    
    This endpoint integrates with the flight scrapper service to find available flights
    for vacation planning. Currently returns flight data only, but will be extended
    to include accommodation search and complete vacation plan creation.
    
    **Note**: This endpoint currently calls the flight scrapper service. Make sure
    the flight scrapper service is running on localhost:8001.
    """,
    response_model=FlightSearchResponse,
    responses={
        200: {
            "description": "Successful flight search",
            "content": {
                "application/json": {
                    "example": flight_response_example
                }
            }
        },
        **error_response_examples
    }
)
def get_vacation_plan(search_params: SearchParams) -> FlightSearchResponse:
    """
    Search for flights and create vacation plan.
    
    Searches for available flights based on the provided search parameters.
    In future phases, this will be extended to include accommodation search
    and complete vacation plan management.
    
    Args:
        search_params: Flight search parameters including origin, destination, dates, etc.
        
    Returns:
        Flight search results with available options
        
    Raises:
        HTTPException: If search parameters are invalid or service is unavailable
    """
    try:
        flights = flight_services.get_flights(
            search_params={
                "origin": search_params.origin,
                "destination": search_params.destination,
                "arrival_date": search_params.arrival_date,
                "passengers": search_params.passengers,
                "return_date": search_params.return_date,
                "checked_baggage": search_params.checked_baggage,
                "carry_on_baggage": search_params.carry_on_baggage
            }
        )
        return FlightSearchResponse(**flights)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid search parameters: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Flight search service is currently unavailable"
        )
