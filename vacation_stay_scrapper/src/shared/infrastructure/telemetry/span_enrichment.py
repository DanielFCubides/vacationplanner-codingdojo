from typing import Any, Dict, Optional

from fastapi import Request
from opentelemetry import trace

ENDUSER_ID_ATTR = "enduser.id"

_ENTITY_ID_ATTRS = {
    "trip_id": "app.trip.id",
    "flight_id": "app.flight.id",
    "accommodation_id": "app.accommodation.id",
    "activity_id": "app.activity.id",
}


def set_enduser(claims: Dict[str, Any]) -> None:
    if trace is None:
        return
    username = claims.get("preferred_username") or claims.get("sub")
    if username:
        trace.get_current_span().set_attribute(ENDUSER_ID_ATTR, str(username))


def enrich_span_with_entity_ids(request: Request) -> None:
    if trace is None:
        return

    span = trace.get_current_span()
    path_params: Optional[Dict[str, Any]] = getattr(request, "path_params", None) or {}
    for param_name, attr_key in _ENTITY_ID_ATTRS.items():
        value = path_params.get(param_name)
        if value is not None:
            span.set_attribute(attr_key, str(value))

