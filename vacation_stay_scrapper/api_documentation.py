"""
OpenAPI specification for Vacation Stay Scrapper API.

Defines the API documentation and schemas for current endpoints.
"""

openapi_info = {
    "title": "Vacation Stay Scrapper API",
    "description": """
    # Vacation Stay Scrapper API
    
    A REST API for vacation planning that provides flight search capabilities 
    and will be extended to include accommodation search and vacation plan management.
    
    ## Current Features
    - Health check endpoint
    - Flight search via external flight scrapper service
    
    ## Planned Features (Phase 1-5 Implementation)
    - Create and manage vacation plans
    - Search accommodations (real and fake data)
    - Integrated vacation planning workflow
    
    ## Authentication
    Currently no authentication is required. This will be added in future phases.
    
    ## Error Handling
    The API uses standard HTTP status codes and returns JSON error responses.
    """,
    "version": "1.0.0",
    "contact": {
        "name": "Vacation Planner Team",
        "email": "support@vacationplanner.com"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
}

openapi_tags = [
    {
        "name": "health",
        "description": "Health check and system status endpoints"
    },
    {
        "name": "vacation-planning", 
        "description": "Vacation planning and flight search operations"
    },
    {
        "name": "future-endpoints",
        "description": "Planned endpoints for upcoming phases (not yet implemented)"
    }
]

# Response schemas for better documentation
flight_response_example = {
    "flights": [
        {
            "outbound": {
                "date": "2025-09-15",
                "departure_time": "08:30",
                "landing_time": "11:45", 
                "price": "299.99",
                "flight_time": "11700"
            },
            "return_in": {
                "date": "2025-09-22",
                "departure_time": "14:20",
                "landing_time": "17:35",
                "price": "319.99", 
                "flight_time": "11700"
            }
        }
    ]
}

error_response_examples = {
    "400": {
        "description": "Bad Request - Invalid input parameters",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid search parameters provided"
                }
            }
        }
    },
    "500": {
        "description": "Internal Server Error - Service unavailable", 
        "content": {
            "application/json": {
                "example": {
                    "detail": "Flight scrapper service is currently unavailable"
                }
            }
        }
    },
    "503": {
        "description": "Service Unavailable - External service error",
        "content": {
            "application/json": {
                "example": {
                    "message": "Something went wrong"
                }
            }
        }
    }
}
