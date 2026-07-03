"""
Unit tests for the PRD-07 child-status domain exceptions.

These exceptions subclass existing domain exceptions so they inherit the
existing FastAPI exception handlers (404 / 422) without new middleware:
    - ChildNotFound       -> EntityNotFound -> HTTP 404
    - InvalidStatusTransition -> ValidationError -> HTTP 422
"""
import pytest

from src.shared.domain.exceptions import (
    DomainException,
    EntityNotFound,
    ValidationError,
    ChildNotFound,
    InvalidStatusTransition,
)


class TestChildNotFound:

    def test_is_an_entity_not_found(self):
        exc = ChildNotFound(child_type="Flight", child_id="f1")
        assert isinstance(exc, EntityNotFound)
        assert isinstance(exc, DomainException)

    def test_exposes_entity_type_and_id_for_the_handler(self):
        exc = ChildNotFound(child_type="Accommodation", child_id="a9")
        assert exc.entity_type == "Accommodation"
        assert exc.entity_id == "a9"

    def test_message_is_trip_scoped(self):
        exc = ChildNotFound(child_type="Flight", child_id="f1")
        assert str(exc) == "Flight not found in this trip"


class TestInvalidStatusTransition:

    def test_is_a_validation_error(self):
        exc = InvalidStatusTransition("Invalid transition")
        assert isinstance(exc, ValidationError)
        assert isinstance(exc, DomainException)

    def test_preserves_the_descriptive_message(self):
        message = "Invalid transition: cannot move from 'confirmed' to 'pending'"
        exc = InvalidStatusTransition(message)
        assert str(exc) == message
