"""
Unit tests for the child status transition validators (PRD-07, FR-3).

The validators are pure domain services: no repository, no I/O. They encode
the per-type state machines from the PRD and raise InvalidStatusTransition
for any move not in the transition table.
"""
import pytest

from src.shared.domain.exceptions import InvalidStatusTransition
from src.trips.domain.services.child_status_transition import (
    FlightStatusTransitionValidator,
    AccommodationStatusTransitionValidator,
)


class TestFlightStatusTransitionValidator:

    def setup_method(self):
        self.validator = FlightStatusTransitionValidator()

    @pytest.mark.parametrize(
        "current,new_status",
        [
            ("pending", "confirmed"),
            ("pending", "cancelled"),
            ("confirmed", "cancelled"),
            ("cancelled", "pending"),
        ],
    )
    def test_allows_valid_transitions(self, current, new_status):
        # Should not raise
        self.validator.validate(current, new_status)

    @pytest.mark.parametrize(
        "current,new_status",
        [
            ("confirmed", "pending"),   # the PRD's 422 example
            ("cancelled", "confirmed"),
            ("confirmed", "confirmed"),  # same-state is rejected (strict)
            ("pending", "pending"),
        ],
    )
    def test_rejects_invalid_transitions(self, current, new_status):
        with pytest.raises(InvalidStatusTransition):
            self.validator.validate(current, new_status)

    def test_rejects_unknown_target_value(self):
        with pytest.raises(InvalidStatusTransition):
            self.validator.validate("pending", "booked")

    def test_error_message_names_both_states(self):
        with pytest.raises(InvalidStatusTransition) as exc_info:
            self.validator.validate("confirmed", "pending")
        message = str(exc_info.value)
        assert "confirmed" in message
        assert "pending" in message


class TestAccommodationStatusTransitionValidator:

    def setup_method(self):
        self.validator = AccommodationStatusTransitionValidator()

    @pytest.mark.parametrize(
        "current,new_status",
        [
            ("pending", "confirmed"),
            ("pending", "cancelled"),
            ("confirmed", "cancelled"),
            ("cancelled", "pending"),
        ],
    )
    def test_allows_valid_transitions(self, current, new_status):
        self.validator.validate(current, new_status)

    @pytest.mark.parametrize(
        "current,new_status",
        [
            ("confirmed", "pending"),
            ("cancelled", "confirmed"),
            ("pending", "booked"),  # accommodations never use 'booked'
        ],
    )
    def test_rejects_invalid_transitions(self, current, new_status):
        with pytest.raises(InvalidStatusTransition):
            self.validator.validate(current, new_status)
