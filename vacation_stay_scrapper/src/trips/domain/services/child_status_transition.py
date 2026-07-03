"""
Child Status Transition Validators (domain service)

Encodes the per-type status state machines from PRD-07 (FR-3). Each validator
is a stateless, pure domain service: it knows only the legal transitions for
its child type and raises InvalidStatusTransition for anything else.

See ADR-002 for the design rationale (shared parameterized base + thin
subclasses). Transition rules are domain knowledge and therefore live in the
domain layer with no infrastructure imports.
"""
from typing import Dict, Set

from ....shared.domain.exceptions import InvalidStatusTransition


class ChildStatusTransitionValidator:
    """
    Base validator parameterized by a VALID_TRANSITIONS map.

    Subclasses override VALID_TRANSITIONS with a mapping of
    ``current_status -> {allowed next statuses}``. Same-state moves are only
    legal if a status explicitly lists itself as a target (none do today), so
    they are rejected as invalid transitions.
    """

    VALID_TRANSITIONS: Dict[str, Set[str]] = {}

    def validate(self, current: str, new_status: str) -> None:
        """
        Validate a transition from ``current`` to ``new_status``.

        Raises:
            InvalidStatusTransition: if the move is not in VALID_TRANSITIONS.
        """
        allowed = self.VALID_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            raise InvalidStatusTransition(
                f"Invalid transition: cannot move from '{current}' to '{new_status}'"
            )


class FlightStatusTransitionValidator(ChildStatusTransitionValidator):
    """Flight state machine: pending/confirmed/cancelled."""

    VALID_TRANSITIONS = {
        "pending": {"confirmed", "cancelled"},
        "confirmed": {"cancelled"},
        "cancelled": {"pending"},
    }
