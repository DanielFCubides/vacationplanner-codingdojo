from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from src.trips.presentation.api.routes import enrich_span_with_entity_ids


class _FakeRequest:
    def __init__(self, path_params):
        self.path_params = path_params


def _exporter():
    provider = TracerProvider()
    exp = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exp))
    return exp, provider.get_tracer(__name__)


def test_entity_ids_stamped_from_path_params():
    exp, tracer = _exporter()
    request = _FakeRequest({"trip_id": "42", "flight_id": "7"})
    with tracer.start_as_current_span("op"):
        enrich_span_with_entity_ids(request)
    attrs = exp.get_finished_spans()[0].attributes
    assert attrs["app.trip.id"] == "42"
    assert attrs["app.flight.id"] == "7"
    assert "app.accommodation.id" not in attrs


def test_missing_path_params_never_raises():
    exp, tracer = _exporter()
    with tracer.start_as_current_span("op"):
        enrich_span_with_entity_ids(object())
    assert exp.get_finished_spans()
