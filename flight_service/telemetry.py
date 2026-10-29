from __future__ import annotations

import logging
import os
import socket
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DEFAULT_OTLP_ENDPOINT = "http://otel-collector:4318"
DEFAULT_OTLP_HTTP_PORT = 4318
PROBE_TIMEOUT_SECONDS = 0.5
_warned = False
_status: "Optional[TelemetryStatus]" = None


@dataclass(frozen=True)
class TelemetryStatus:
    enabled: bool
    service_name: str
    endpoint: str
    reason: Optional[str] = None


def _is_truthy(value: Optional[str]) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _endpoint_host_port(endpoint: str) -> tuple[str, int]:
    parsed = urlparse(endpoint)
    host = parsed.hostname or "otel-collector"
    port = parsed.port or DEFAULT_OTLP_HTTP_PORT
    return host, port


def _probe_collector(host: str, port: int, timeout: float = PROBE_TIMEOUT_SECONDS) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def reset_telemetry_state() -> None:
    global _warned, _status
    _warned = False
    _status = None


def _disabled(service_name: str, endpoint: str, reason: str, *, warn: bool) -> TelemetryStatus:
    global _warned, _status
    if warn and not _warned:
        logger.warning(
            f"OpenTelemetry collector unreachable at {endpoint}; telemetry centralization disabled "
            f"({reason}), falling back to local stdout logging."
        )
        _warned = True
    _status = TelemetryStatus(enabled=False, service_name=service_name, endpoint=endpoint, reason=reason)
    return _status


def setup_telemetry(service_name: str, app: object | None = None) -> TelemetryStatus:
    """Configure centralized telemetry for flight_service if the collector is reachable.

    Traces, metrics and logs are exported over OTLP/HTTP. The Flask (REST/GraphQL),
    requests and logging libraries are auto-instrumented globally; whichever server
    type ``SERVER`` selects starts *after* this runs, so it inherits the setup.
    gRPC gets export + graceful fallback but no framework spans. If the collector
    cannot be reached (or OTEL is disabled), the service continues with local
    stdout logging only — telemetry setup never breaks startup.

    Returns:
        TelemetryStatus describing whether telemetry was enabled and why not.
    """
    global _status
    if _status is not None:
        return _status

    resolved_name = os.getenv("OTEL_SERVICE_NAME", service_name)
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", DEFAULT_OTLP_ENDPOINT)

    if _is_truthy(os.getenv("OTEL_SDK_DISABLED")):
        _status = TelemetryStatus(
            enabled=False, service_name=resolved_name, endpoint=endpoint, reason="OTEL_SDK_DISABLED",
        )
        logger.info("OpenTelemetry disabled via OTEL_SDK_DISABLED; using local logging only.")
        return _status

    # Reachability probe — the graceful-degradation gate.
    host, port = _endpoint_host_port(endpoint)
    if not _probe_collector(host, port):
        return _disabled(resolved_name, endpoint, "collector unreachable", warn=True)

    # Collector reachable — configure the SDK. Any failure downgrades to disabled.
    try:
        _configure_sdk(resolved_name, endpoint, app)
    except Exception as exc:  # noqa: BLE001 - telemetry must never break startup
        return _disabled(resolved_name, endpoint, f"SDK setup failed: {exc!r}", warn=True)

    _status = TelemetryStatus(enabled=True, service_name=resolved_name, endpoint=endpoint)
    logger.info(
        f"OpenTelemetry enabled for {resolved_name}; exporting traces, metrics and logs to {endpoint}."
    )
    return _status


def _configure_sdk(service_name: str, endpoint: str, app: object | None) -> None:
    """Register providers, OTLP exporters and auto-instrumentation.

    Heavy OTel imports are performed here (lazily) so the fallback path never
    depends on the SDK being installed.
    """
    from opentelemetry import _logs, metrics, trace
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create({"service.name": service_name})

    # Traces
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")))
    trace.set_tracer_provider(tracer_provider)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics"))
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Logs — attach an OTLP handler to the root logger; the stdout handler
    # configured via logging.basicConfig stays in place.
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{endpoint}/v1/logs")))
    _logs.set_logger_provider(logger_provider)
    logging.getLogger().addHandler(LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider))

    # Auto-instrumentation. requests injects W3C traceparent on outbound calls
    # (cross-service tracing); logging stamps trace_id/span_id into logs; Flask
    # is instrumented globally so the REST/GraphQL app created afterwards by
    # app_factory() is auto-wired (gRPC has no Flask app — no framework spans).
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor

    LoggingInstrumentor().instrument(set_logging_format=False)
    RequestsInstrumentor().instrument()
    FlaskInstrumentor().instrument(tracer_provider=tracer_provider, meter_provider=meter_provider)
