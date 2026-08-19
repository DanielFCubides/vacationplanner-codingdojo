import logging
import sys


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a stdout logger.

    OTLP log export is wired up (only when the collector is reachable) by
    ``telemetry.setup_telemetry`` via a handler on the root logger. This
    function only guarantees local stdout logging, which must always work
    regardless of whether the observability stack is running.
    """
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
