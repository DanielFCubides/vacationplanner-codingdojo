"""
Backward compatibility layer for old imports

This module re-exports from the new clean architecture location.
TODO: Remove this file once all imports are updated.
"""
# Re-export from new location
from src.shared.infrastructure.http.circuit_breaker import CircuitBreaker, CircuitBreakerState

__all__ = ['CircuitBreaker', 'CircuitBreakerState']
