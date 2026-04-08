"""
FastAPI Middleware Configuration

Provides middleware setup for the FastAPI application.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Callable
import time

from src.shared.infrastructure.logging.logger import setup_logger
from src.shared.domain.exceptions import (
    DomainException,
    EntityNotFound,
    ValidationError,
    BusinessRuleViolation,
    ServiceUnavailable
)

logger = setup_logger(__name__)


def setup_cors_middleware(app: FastAPI):
    """
    Configure CORS middleware
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_logging_middleware(app: FastAPI):
    """
    Add request/response logging middleware
    
    Args:
        app: FastAPI application instance
    """
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.2f}s"
        )
        
        return response


def setup_exception_handlers(app: FastAPI):
    """
    Register global exception handlers
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(EntityNotFound)
    async def entity_not_found_handler(
        request: Request,
        exc: EntityNotFound
    ):
        logger.warning(f"Entity not found: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(exc),
                "entity_type": exc.entity_type,
                "entity_id": exc.entity_id
            }
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request,
        exc: ValidationError
    ):
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Validation failed",
                "details": str(exc)
            }
        )
    
    @app.exception_handler(BusinessRuleViolation)
    async def business_rule_violation_handler(
        request: Request,
        exc: BusinessRuleViolation
    ):
        logger.warning(f"Business rule violation: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Business rule violation",
                "details": str(exc)
            }
        )
    
    @app.exception_handler(ServiceUnavailable)
    async def service_unavailable_handler(
        request: Request,
        exc: ServiceUnavailable
    ):
        logger.error(f"Service unavailable: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "Service temporarily unavailable",
                "details": str(exc)
            }
        )
    
    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request,
        exc: DomainException
    ):
        logger.error(f"Domain exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An error occurred",
                "details": str(exc)
            }
        )


def setup_middleware(app: FastAPI):
    """
    Setup all middleware for the application
    
    Args:
        app: FastAPI application instance
    """
    setup_cors_middleware(app)
    setup_logging_middleware(app)
    setup_exception_handlers(app)
    
    logger.info("Middleware configured successfully")
