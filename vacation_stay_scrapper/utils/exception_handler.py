"""
Backward compatibility layer for old imports

This module re-exports from the new clean architecture location.
TODO: Remove this file once all imports are updated.
"""
# Re-export from new location
from src.shared.presentation.exception_handlers import GracefulDegradationService

__all__ = ['GracefulDegradationService']
