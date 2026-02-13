"""
Backward compatibility layer for old imports

This module re-exports from the new clean architecture location.
TODO: Remove this file once all imports are updated.
"""
# Re-export from new location
from config.settings import settings

MIN_DELAY_ATTEMPT = settings.circuit_breaker_min_delay
MIN_FAILURE_ATTEMPTS = settings.circuit_breaker_min_failures

__all__ = ['MIN_DELAY_ATTEMPT', 'MIN_FAILURE_ATTEMPTS']
