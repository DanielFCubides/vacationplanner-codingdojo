            "StaySearchCriteria": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "check_in_date": {"type": "string", "format": "date"},
                    "check_out_date": {"type": "string", "format": "date"},
                    "guests": {"type": "integer", "minimum": 1},
                    "nights": {"type": "integer"},
                    "stay_types": {"type": "array", "items": {"type": "string"}, "nullable": True},
                    "min_price": {"type": "string", "nullable": True},
                    "max_price": {"type": "string", "nullable": True},
                    "min_rating": {"type": "number", "minimum": 0, "maximum": 5, "nullable": True},
                    "required_amenities": {"type": "array", "items": {"type": "string"}, "nullable": True},
                    "max_results": {"type": "integer", "default": 20}
                }
            },
            "CreateVacationPlanRequest": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "example": "Summer Vacation in Miami"},
                    "description": {"type": "string", "example": "A wonderful beach vacation"},
                    "flight_search_params": {"$ref": "#/components/schemas/SearchParams"},
                    "stay_search_params": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "check_in_date": {"type": "string", "format": "date"},
                            "check_out_date": {"type": "string", "format": "date"},
                            "guests": {"type": "integer", "minimum": 1}
                        }
                    },
                    "total_budget": {"type": "string", "nullable": True},
                    "notes": {"type": "string"},
                    "use_fake_data": {"type": "boolean", "default": False, "description": "Use generated fake data for development/testing"}
                },
                "required": ["title"]
            },
            "UpdateVacationPlanRequest": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string", "enum": ["draft", "confirmed", "cancelled", "completed"]},
                    "total_budget": {"type": "string", "nullable": True},
                    "notes": {"type": "string"}
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Internal error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                },
                "required": ["detail"]
            }
        },
        "responses": {
            "BadRequest": {
                "description": "Bad Request - Invalid input parameters",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "detail": "Invalid search parameters provided",
                            "error_code": "INVALID_PARAMETERS"
                        }
                    }
                }
            },
            "NotFound": {
                "description": "Resource not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "detail": "Vacation plan not found",
                            "error_code": "RESOURCE_NOT_FOUND"
                        }
                    }
                }
            },
            "ServiceUnavailable": {
                "description": "Service Unavailable - External service error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "detail": "Flight search service is currently unavailable",
                            "error_code": "SERVICE_UNAVAILABLE"
                        }
                    }
                }
            },
            "InternalServerError": {
                "description": "Internal Server Error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "detail": "An unexpected error occurred",
                            "error_code": "INTERNAL_ERROR"
                        }
                    }
                }
            }
        }
    }
}

# Configuration examples for documentation
configuration_examples = {
    "environment_variables": {
        "USE_FAKE_FLIGHTS": "true",
        "USE_FAKE_STAYS": "true", 
        "FLIGHT_SERVICE_URL": "localhost:8001",
        "VACATION_STORAGE": "memory",
        "VACATION_FILE_PATH": "/data/plans.json",
        "FAKER_LOCALE": "en_US",
        "STAYS_PER_SEARCH": "10"
    },
    "fake_data_examples": {
        "stay_search_response": {
            "stays": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Ocean View Hotel & Spa",
                    "stay_type": "hotel",
                    "location": {
                        "city": "Miami Beach",
                        "country": "USA",
                        "address": "1234 Ocean Drive",
                        "full_location": "1234 Ocean Drive, Miami Beach, USA"
                    },
                    "pricing": {
                        "price_per_night": "189.99",
                        "currency": "USD",
                        "taxes_and_fees": "23.50"
                    },
                    "max_guests": 4,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "amenities": ["wifi", "pool", "gym", "breakfast", "sea_view"],
                    "description": "Luxury hotel with stunning ocean views and modern amenities",
                    "rating": 4.5,
                    "review_count": 1247,
                    "host_name": "Ocean View Hotels"
                }
            ],
            "total": 1,
            "fake_data_used": True
        },
        "vacation_plan_example": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Miami Beach Getaway",
            "description": "A relaxing beach vacation with ocean views",
            "status": "draft",
            "flight_info": {
                "origin": "BOG",
                "destination": "MIA", 
                "departure_date": "2025-09-15",
                "return_date": "2025-09-22",
                "passengers": 2,
                "price": "899.98"
            },
            "stay_info": {
                "location": "Miami Beach",
                "check_in_date": "2025-09-15",
                "check_out_date": "2025-09-22",
                "guests": 2,
                "nights": 7,
                "price_per_night": "189.99",
                "total_price": "1329.93"
            },
            "total_cost": "2229.91",
            "is_complete": True
        }
    }
}
