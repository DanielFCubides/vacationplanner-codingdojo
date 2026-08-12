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
