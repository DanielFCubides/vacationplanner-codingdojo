import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from src.shared.infrastructure.telemetry.span_enrichment import (
    enrich_span_with_entity_ids,
    set_enduser,
)


@pytest.fixture
def exporter():
    provider = TracerProvider()
    exp = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exp))
    tracer = provider.get_tracer(__name__)
    return exp, tracer


class _FakeRequest:
    def __init__(self, path_params):
        self.path_params = path_params


def test_set_enduser_prefers_preferred_username(exporter):
    exp, tracer = exporter
    with tracer.start_as_current_span("op"):
        set_enduser({"preferred_username": "alice", "sub": "uuid-1"})
    span = exp.get_finished_spans()[0]
    assert span.attributes["enduser.id"] == "alice"


def test_set_enduser_falls_back_to_sub(exporter):
    exp, tracer = exporter
    with tracer.start_as_current_span("op"):
        set_enduser({"sub": "uuid-1"})
    span = exp.get_finished_spans()[0]
    assert span.attributes["enduser.id"] == "uuid-1"


def test_entity_ids_stamped_from_path_params(exporter):
    exp, tracer = exporter
    request = _FakeRequest({"trip_id": "42", "flight_id": "7"})
    with tracer.start_as_current_span("op"):
        enrich_span_with_entity_ids(request)
    attrs = exp.get_finished_spans()[0].attributes
    assert attrs["app.trip.id"] == "42"
    assert attrs["app.flight.id"] == "7"
    assert "app.accommodation.id" not in attrs


def test_enrichment_never_raises_on_bad_input(exporter):
    exp, tracer = exporter
    with tracer.start_as_current_span("op"):
        # Missing path_params attribute entirely.
        enrich_span_with_entity_ids(object())
        set_enduser({})
    # No exception == pass; span still recorded.
    assert exp.get_finished_spans()
