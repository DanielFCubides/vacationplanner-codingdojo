"""
Domain Exceptions

Business logic exceptions that can be raised across all domains.
"""


class DomainException(Exception):
    """Base exception for all domain-related errors"""
    pass


class HTTPException(DomainException):
    """Raised when HTTP operations fail"""
    pass


class UnknownException(DomainException):
    """Raised when an unexpected error occurs"""
    pass


class ServiceUnavailable(DomainException):
    """Raised when an external service is unavailable"""
    pass


class ValidationError(DomainException):
    """Raised when domain validation fails"""
    pass


class EntityNotFound(DomainException):
    """Raised when a requested entity is not found"""
    
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(
            f"{entity_type} with id '{entity_id}' not found"
        )


class BusinessRuleViolation(DomainException):
    """Raised when a business rule is violated"""
    pass


class ChildNotFound(EntityNotFound):
    """
    Raised when a trip child (flight, accommodation, or activity) is not
    found within a trip.

    Subclasses EntityNotFound so it is handled by the existing 404 handler,
    but renders a trip-scoped message ("Flight not found in this trip")
    instead of the generic entity message.
    """

    def __init__(self, child_type: str, child_id: str):
        self.entity_type = child_type
        self.entity_id = child_id
        DomainException.__init__(self, f"{child_type} not found in this trip")


class InvalidStatusTransition(ValidationError):
    """
    Raised when a status change is not a legal transition for a child type.

    Subclasses ValidationError so it inherits the existing 422 handler; the
    descriptive message is surfaced to the client in the response details.
    """
    pass
