"""
Unit tests for the OpenTelemetry bootstrap (Phase 1).

These focus on the graceful-degradation contract: when the collector is
unreachable (or telemetry is explicitly disabled), setup_telemetry() must
return a disabled status, emit at most one warning, and never raise — so a
service can always start regardless of the observability stack.

The tests deliberately avoid requiring the OpenTelemetry SDK to be installed:
the fallback paths exercised here never import it.
"""
import logging

import pytest

from src.shared.infrastructure.telemetry import otel


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch):
    """Clear cached status/warning flag and env between tests."""
    otel.reset_telemetry_state()
    for var in ("OTEL_SDK_DISABLED", "OTEL_SERVICE_NAME", "OTEL_EXPORTER_OTLP_ENDPOINT"):
        monkeypatch.delenv(var, raising=False)
    yield
    otel.reset_telemetry_state()


def _force_unreachable(monkeypatch):
    monkeypatch.setattr(otel, "_probe_collector", lambda host, port, timeout=0.5: False)


def _force_reachable(monkeypatch):
    monkeypatch.setattr(otel, "_probe_collector", lambda host, port, timeout=0.5: True)


class TestGracefulFallback:

    def test_unreachable_collector_disables_telemetry(self, monkeypatch):
        _force_unreachable(monkeypatch)

        status = otel.setup_telemetry("vacation-planner")

        assert status.enabled is False
        assert status.service_name == "vacation-planner"
        assert status.reason == "collector unreachable"

    def test_unreachable_collector_logs_exactly_one_warning(self, monkeypatch, caplog):
        _force_unreachable(monkeypatch)

        with caplog.at_level(logging.WARNING, logger=otel.logger.name):
            otel.setup_telemetry("vacation-planner")
            # A second component re-entering in the same process must not warn
            # again: clear only the cached status, keeping the _warned flag.
            otel._status = None
            otel.setup_telemetry("vacation-planner")

        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 1
        assert "telemetry centralization" in warnings[0].getMessage()

    def test_setup_never_raises_when_probe_fails(self, monkeypatch):
        _force_unreachable(monkeypatch)
        # Should simply return, not raise.
        assert otel.setup_telemetry("svc").enabled is False


class TestExplicitDisable:

    def test_sdk_disabled_flag_skips_probe_and_stays_disabled(self, monkeypatch):
        monkeypatch.setenv("OTEL_SDK_DISABLED", "true")

        # Probe must not even be consulted; make it blow up if called.
        def _boom(*_a, **_k):
            raise AssertionError("probe should not run when OTEL_SDK_DISABLED is set")

        monkeypatch.setattr(otel, "_probe_collector", _boom)

        status = otel.setup_telemetry("svc")

        assert status.enabled is False
        assert status.reason == "OTEL_SDK_DISABLED"


class TestConfig:

    def test_service_name_env_overrides_argument(self, monkeypatch):
        _force_unreachable(monkeypatch)
        monkeypatch.setenv("OTEL_SERVICE_NAME", "override-name")

        status = otel.setup_telemetry("passed-name")

        assert status.service_name == "override-name"

    def test_endpoint_host_port_parsing(self):
        assert otel._endpoint_host_port("http://otel-collector:4318") == (
            "otel-collector",
            4318,
        )

    def test_endpoint_host_port_defaults_port(self):
        host, port = otel._endpoint_host_port("http://collector")
        assert (host, port) == ("collector", otel.DEFAULT_OTLP_HTTP_PORT)

    def test_sdk_failure_downgrades_to_disabled(self, monkeypatch):
        _force_reachable(monkeypatch)

        def _boom(*_a, **_k):
            raise RuntimeError("no otel installed")

        monkeypatch.setattr(otel, "_configure_sdk", _boom)

        status = otel.setup_telemetry("svc")

        assert status.enabled is False
        assert status.reason.startswith("SDK setup failed")
