"""
Backward compatibility layer for old imports

This module re-exports from the new clean architecture location.
TODO: Remove this file once all imports are updated.
"""
# Re-export from new location
from src.shared.domain.exceptions import (
    DomainException,
    HTTPException,
    UnknownException,
    ServiceUnavailable,
    ValidationError,
    EntityNotFound,
    BusinessRuleViolation
)

__all__ = [
    'DomainException',
    'HTTPException',
    'UnknownException',
    'ServiceUnavailable',
    'ValidationError',
    'EntityNotFound',
    'BusinessRuleViolation'
]
