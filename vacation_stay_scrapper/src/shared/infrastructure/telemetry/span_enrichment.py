from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping

from opentelemetry import trace

# OTel attribute values must be primitives: str, bool, int, float (or sequences of those).
AttributeValue = str | bool | int | float

ENDUSER_ID_ATTR = "enduser.id"

_ENTITY_ID_ATTRS = {
    "trip_id": "app.trip.id",
    "flight_id": "app.flight.id",
    "accommodation_id": "app.accommodation.id",
    "activity_id": "app.activity.id",
}


class OtelContext(ABC):
    @property
    @abstractmethod
    def attributes(self) -> Mapping[str, AttributeValue]:
        """All attributes — safe for traces and logs (any cardinality)."""

    @property
    def metric_labels(self) -> Mapping[str, AttributeValue]:
        """Low-cardinality subset safe to use as metric dimensions."""
        return {}


class UserContext(OtelContext):
    """Identifies the acting end user. High cardinality — traces/logs only."""

    def __init__(self, claims: Dict[str, Any]) -> None:
        self._username = claims.get("preferred_username") or claims.get("sub")

    @property
    def attributes(self) -> Mapping[str, AttributeValue]:
        if not self._username:
            return {}
        return {ENDUSER_ID_ATTR: str(self._username)}
    # metric_labels stays empty — user id is high cardinality.


class EntityContext(OtelContext):
    """Domain entity IDs pulled from request path params. High cardinality."""

    def __init__(self, path_params: Mapping[str, Any]) -> None:
        self._path_params = path_params or {}

    @property
    def attributes(self) -> Mapping[str, AttributeValue]:
        return {
            attr_key: str(self._path_params[param])
            for param, attr_key in _ENTITY_ID_ATTRS.items()
            if self._path_params.get(param) is not None
        }


def _merge_attributes(contexts: tuple[OtelContext, ...]) -> Dict[str, AttributeValue]:
    merged: Dict[str, AttributeValue] = {}
    for ctx in contexts:
        merged.update(ctx.attributes)
    return merged


def _merge_metric_labels(contexts: tuple[OtelContext, ...]) -> Dict[str, AttributeValue]:
    merged: Dict[str, AttributeValue] = {}
    for ctx in contexts:
        merged.update(ctx.metric_labels)
    return merged


def enrich_span(*contexts: OtelContext) -> None:
    """Set every context attribute on the current span."""
    span = trace.get_current_span()
    for key, value in _merge_attributes(contexts).items():
        span.set_attribute(key, value)


def enrich_log(*contexts: OtelContext) -> Dict[str, AttributeValue]:
    """Return a dict to pass as ``logger.info(..., extra=...)``."""
    return _merge_attributes(contexts)


def record_metric(counter, amount: int, *contexts: OtelContext) -> None:
    """Add to an OTel counter using only the low-cardinality metric labels."""
    counter.add(amount, attributes=_merge_metric_labels(contexts))
