"""
Backward compatibility layer for old imports

This module re-exports from the new clean architecture location.
TODO: Remove this file once all imports are updated.
"""
from pathlib import Path


def get_secret(name: str, default: str | None = None) -> str | None:
    """Read a Docker secret mounted at /run/secrets/<name>."""
    secret_path = Path('/run/secrets', name)
    if not secret_path.is_file():
        return default
    return secret_path.read_text(encoding='utf-8').strip()


def __getattr__(name: str):
    """Lazily expose legacy settings without creating an import cycle."""
    if name in {'MIN_DELAY_ATTEMPT', 'MIN_FAILURE_ATTEMPTS'}:
        from config.settings import settings

        values = {
            'MIN_DELAY_ATTEMPT': settings.circuit_breaker_min_delay,
            'MIN_FAILURE_ATTEMPTS': settings.circuit_breaker_min_failures,
        }
        return values[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ['MIN_DELAY_ATTEMPT', 'MIN_FAILURE_ATTEMPTS', 'get_secret']
