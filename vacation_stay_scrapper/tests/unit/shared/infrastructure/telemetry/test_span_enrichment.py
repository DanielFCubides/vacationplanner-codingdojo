import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from src.shared.infrastructure.telemetry.span_enrichment import (
    EntityContext,
    UserContext,
    enrich_log,
    enrich_span,
    record_metric,
)


@pytest.fixture
def exporter():
    provider = TracerProvider()
    exp = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exp))
    tracer = provider.get_tracer(__name__)
    return exp, tracer


def test_user_context_prefers_preferred_username(exporter):
    exp, tracer = exporter
    with tracer.start_as_current_span("op"):
        enrich_span(UserContext({"preferred_username": "alice", "sub": "uuid-1"}))
    span = exp.get_finished_spans()[0]
    assert span.attributes["enduser.id"] == "alice"


def test_user_context_falls_back_to_sub(exporter):
    exp, tracer = exporter
    with tracer.start_as_current_span("op"):
        enrich_span(UserContext({"sub": "uuid-1"}))
    span = exp.get_finished_spans()[0]
    assert span.attributes["enduser.id"] == "uuid-1"


def test_entity_context_maps_path_params_to_attributes():
    attrs = EntityContext({"trip_id": "42", "flight_id": "7"}).attributes
    assert attrs["app.trip.id"] == "42"
    assert attrs["app.flight.id"] == "7"
    assert "app.accommodation.id" not in attrs


def test_enrich_span_merges_multiple_contexts(exporter):
    exp, tracer = exporter
    with tracer.start_as_current_span("op"):
        enrich_span(
            UserContext({"preferred_username": "alice"}),
            EntityContext({"trip_id": "42"}),
        )
    attrs = exp.get_finished_spans()[0].attributes
    assert attrs["enduser.id"] == "alice"
    assert attrs["app.trip.id"] == "42"


class _FakeCounter:
    def __init__(self):
        self.calls = []

    def add(self, amount, attributes):
        self.calls.append((amount, attributes))


def test_metric_labels_exclude_high_cardinality_ids():
    counter = _FakeCounter()
    record_metric(
        counter, 1, UserContext({"sub": "uuid-1"}), EntityContext({"trip_id": "42"})
    )
    # User and entity IDs are high cardinality — never surfaced as metric labels.
    assert counter.calls == [(1, {})]


def test_enrich_log_returns_attribute_dict():
    extra = enrich_log(UserContext({"preferred_username": "alice"}))
    assert extra == {"enduser.id": "alice"}


def test_enrichment_never_raises_on_empty_contexts(exporter):
    exp, tracer = exporter
    with tracer.start_as_current_span("op"):
        # Empty inputs yield no attributes but must not raise.
        enrich_span(EntityContext({}), UserContext({}))
    # No exception == pass; span still recorded.
    assert exp.get_finished_spans()
