"""
OpenTelemetry bootstrap with graceful degradation.

`setup_telemetry()` is the single entry point every backend service calls at
startup. It decides — at runtime — whether centralized telemetry (traces,
metrics, logs to the OpenTelemetry Collector) can be enabled:

1. If ``OTEL_SDK_DISABLED`` is truthy, telemetry is skipped entirely.
2. Otherwise the collector endpoint is probed with a short TCP connect. If the
   collector is unreachable (observability stack not running), NO exporters are
   registered; a single warning is logged and the service continues on local
   stdout logging only.
3. If reachable, the tracer/meter/logger providers are configured with OTLP
   exporters and W3C trace-context propagation.

Any failure while configuring the SDK (including missing optional
dependencies) downgrades to the disabled state rather than raising — a broken
or absent collector must never stop a service from starting.

The heavy OpenTelemetry SDK imports are performed lazily inside the enabled
branch so this module (and the fallback path) can be imported and unit-tested
without the OTel packages installed.
"""
from __future__ import annotations

import logging
import os
import socket
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Default collector OTLP/HTTP endpoint (matches docker/compose.observability.yml).
DEFAULT_OTLP_ENDPOINT = "http://otel-collector:4318"
DEFAULT_OTLP_HTTP_PORT = 4318
# How long to wait for the collector TCP handshake before giving up.
PROBE_TIMEOUT_SECONDS = 0.5

# Ensures the "centralization unavailable" warning is emitted at most once per
# process, regardless of how many services/components call setup_telemetry().
_warned = False
# Cache so repeated calls in the same process are idempotent (mirrors how
# services may call this from multiple entry points).
_status: "Optional[TelemetryStatus]" = None


@dataclass(frozen=True)
class TelemetryStatus:
    """Outcome of a setup_telemetry() call."""

    enabled: bool
    service_name: str
    endpoint: str
    reason: Optional[str] = None


def _is_truthy(value: Optional[str]) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _endpoint_host_port(endpoint: str) -> tuple[str, int]:
    """Extract (host, port) from an OTLP endpoint URL for the reachability probe."""
    parsed = urlparse(endpoint)
    host = parsed.hostname or "otel-collector"
    port = parsed.port or DEFAULT_OTLP_HTTP_PORT
    return host, port


def _probe_collector(host: str, port: int, timeout: float = PROBE_TIMEOUT_SECONDS) -> bool:
    """Return True if a TCP connection to host:port succeeds within `timeout`."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def reset_telemetry_state() -> None:
    """Reset module state. Intended for tests only."""
    global _warned, _status
    _warned = False
    _status = None


def _disabled(service_name: str, endpoint: str, reason: str, *, warn: bool) -> "TelemetryStatus":
    """Build a disabled status, logging a single warning the first time."""
    global _warned, _status
    if warn and not _warned:
        logger.warning(
            "OpenTelemetry collector unreachable at %s; telemetry centralization "
            "disabled (%s), falling back to local stdout logging.",
            endpoint,
            reason,
        )
        _warned = True
    _status = TelemetryStatus(
        enabled=False, service_name=service_name, endpoint=endpoint, reason=reason
    )
    return _status


def setup_telemetry(service_name: str, app: object | None = None) -> "TelemetryStatus":
    """Configure centralized telemetry if the collector is reachable.

    Args:
        service_name: Resource ``service.name`` (falls back for ``OTEL_SERVICE_NAME``).
        app: Optional ASGI app (e.g. FastAPI) to auto-instrument. Instrumentation
            wiring is added by later phases; passing it here is safe today.

    Returns:
        TelemetryStatus describing whether telemetry was enabled and why not.
    """
    global _status
    if _status is not None:
        return _status

    resolved_name = os.getenv("OTEL_SERVICE_NAME", service_name)
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", DEFAULT_OTLP_ENDPOINT)

    # 1. Explicit opt-out — do not probe, do not warn (this is intentional).
    if _is_truthy(os.getenv("OTEL_SDK_DISABLED")):
        _status = TelemetryStatus(
            enabled=False,
            service_name=resolved_name,
            endpoint=endpoint,
            reason="OTEL_SDK_DISABLED",
        )
        logger.info("OpenTelemetry disabled via OTEL_SDK_DISABLED; using local logging only.")
        return _status

    # 2. Reachability probe — the graceful-degradation gate.
    host, port = _endpoint_host_port(endpoint)
    if not _probe_collector(host, port):
        return _disabled(resolved_name, endpoint, "collector unreachable", warn=True)

    # 3. Collector is reachable — configure the SDK. Any failure downgrades
    #    to disabled rather than propagating.
    try:
        _configure_sdk(resolved_name, endpoint, app)
    except Exception as exc:  # noqa: BLE001 - telemetry must never break startup
        return _disabled(
            resolved_name, endpoint, f"SDK setup failed: {exc!r}", warn=True
        )

    _status = TelemetryStatus(enabled=True, service_name=resolved_name, endpoint=endpoint)
    logger.info(
        "OpenTelemetry enabled for %s; exporting traces, metrics and logs to %s.",
        resolved_name,
        endpoint,
    )
    return _status


def _configure_sdk(service_name: str, endpoint: str, app: object | None) -> None:
    """Register tracer/meter/logger providers with OTLP exporters.

    Heavy OTel imports are performed here (lazily) so the fallback path never
    depends on the SDK being installed. Auto-instrumentation of specific
    frameworks is added by the per-service phases.
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
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces"))
    )
    trace.set_tracer_provider(tracer_provider)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics")
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Logs — attach an OTLP handler to the root logger; the stdout handler
    # configured by each service's logging setup stays in place.
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{endpoint}/v1/logs"))
    )
    _logs.set_logger_provider(logger_provider)
    logging.getLogger().addHandler(
        LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    )
