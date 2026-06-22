"""
Logging Configuration

Provides centralized logging setup with OpenTelemetry export.
"""
import logging
import os
import sys
from functools import cache
from typing import Optional

from opentelemetry import _logs
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


@cache
def _configure_otel_logging() -> None:
    resource = Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", "vacation-planner"),
    })
    provider = LoggerProvider(resource=resource)
    exporter = OTLPLogExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT", "http://otel-collector:4318/v1/logs"),
    )
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    _logs.set_logger_provider(provider)

    otel_handler = LoggingHandler(level=logging.NOTSET, logger_provider=provider)
    logging.getLogger().addHandler(otel_handler)


def setup_logger(
    logger_name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    formatter: Optional[logging.Formatter] = None
) -> logging.Logger:
    _configure_otel_logging()

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    if formatter is None:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_path = os.path.join(os.getcwd(), log_file)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = True
    return logger
