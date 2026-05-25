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


class UnauthorizedAccess(DomainException):
    """Raised when a user attempts to access a resource they don't own"""

    def __init__(self, resource_type: str, resource_id: str, user_id: str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.user_id = user_id
        super().__init__(
            f"User '{user_id}' is not authorized to access {resource_type} '{resource_id}'"
        )
