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
    """Configure centralized telemetry for auth_service if the collector is reachable.

    Traces, metrics and logs are exported over OTLP/HTTP and the FastAPI, httpx
    and logging libraries are auto-instrumented. If the collector cannot be
    reached (or OTEL is disabled), the service continues with local stdout
    logging only — telemetry setup never breaks startup.

    Args:
        service_name: Resource ``service.name`` (overridable via ``OTEL_SERVICE_NAME``).
        app: The FastAPI app to auto-instrument.

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
    # Provider/exporter/instrumentation wiring lands in the next commit. Until
    # then this raises, and setup_telemetry() downgrades to disabled — the
    # service keeps running on local stdout logging.
    raise NotImplementedError("SDK wiring not yet implemented")
