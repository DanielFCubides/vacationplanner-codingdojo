import logging
import os
import sys
from functools import cache

from opentelemetry import _logs
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


@cache
def _configure_otel_logging() -> None:
    resource = Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", "auth-service"),
    })
    provider = LoggerProvider(resource=resource)
    exporter = OTLPLogExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT", "http://otel-collector:4318/v1/logs"),
    )
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    _logs.set_logger_provider(provider)

    otel_handler = LoggingHandler(level=logging.NOTSET, logger_provider=provider)
    logging.getLogger().addHandler(otel_handler)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    _configure_otel_logging()

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not any(
        isinstance(handler, logging.StreamHandler) and
        handler.stream is sys.stdout
        for handler in logger.handlers
    ):
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = True
    return logger
