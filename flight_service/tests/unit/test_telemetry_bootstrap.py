"""
Unit tests for the OpenTelemetry bootstrap (Phase 4).

These focus on the graceful-degradation contract: when the collector is
unreachable (or telemetry is explicitly disabled), setup_telemetry() must
return a disabled status, emit at most one warning, and never raise — so the
flight service can always start regardless of the observability stack.

The tests deliberately avoid requiring the OpenTelemetry SDK to be installed:
the fallback paths exercised here never import it.
"""
import logging

import pytest

import telemetry


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch):
    """Clear cached status/warning flag and env between tests."""
    telemetry.reset_telemetry_state()
    for var in ("OTEL_SDK_DISABLED", "OTEL_SERVICE_NAME", "OTEL_EXPORTER_OTLP_ENDPOINT"):
        monkeypatch.delenv(var, raising=False)
    yield
    telemetry.reset_telemetry_state()


def _force_unreachable(monkeypatch):
    monkeypatch.setattr(telemetry, "_probe_collector", lambda host, port, timeout=0.5: False)


class TestGracefulFallback:

    def test_unreachable_collector_disables_telemetry(self, monkeypatch):
        _force_unreachable(monkeypatch)

        status = telemetry.setup_telemetry("flight-service")

        assert status.enabled is False
        assert status.service_name == "flight-service"
        assert status.reason == "collector unreachable"

    def test_unreachable_collector_logs_exactly_one_warning(self, monkeypatch, caplog):
        _force_unreachable(monkeypatch)

        with caplog.at_level(logging.WARNING, logger=telemetry.logger.name):
            telemetry.setup_telemetry("flight-service")
            # A second component re-entering must not warn again.
            telemetry._status = None
            telemetry.setup_telemetry("flight-service")

        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 1
        assert "telemetry centralization" in warnings[0].getMessage()

    def test_setup_never_raises_when_probe_fails(self, monkeypatch):
        _force_unreachable(monkeypatch)
        assert telemetry.setup_telemetry("flight-service").enabled is False
