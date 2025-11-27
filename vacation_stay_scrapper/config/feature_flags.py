"""
Feature flags for controlling application behavior.

Simple boolean flags for enabling/disabling features and data sources.
"""
import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class FeatureFlags:
    """
    Feature flags for application configuration.
    
    Controls various aspects of the application behavior,
    especially for switching between real and fake data sources.
    """
    # Data source flags
    use_fake_flights: bool = False
    use_fake_stays: bool = False
    
    # Application features
    enable_caching: bool = True
    enable_logging: bool = True
    enable_metrics: bool = False
    
    @classmethod
    def from_environment(cls) -> 'FeatureFlags':
        """
        Create feature flags from environment variables.
        
        Environment variables are parsed as boolean values.
        Accepts: true/false, 1/0, yes/no (case insensitive)
        
        Returns:
            FeatureFlags instance configured from environment
        """
        return cls(
            use_fake_flights=_parse_bool_env('USE_FAKE_FLIGHTS', False),
            use_fake_stays=_parse_bool_env('USE_FAKE_STAYS', False),
            enable_caching=_parse_bool_env('ENABLE_CACHING', True),
            enable_logging=_parse_bool_env('ENABLE_LOGGING', True),
            enable_metrics=_parse_bool_env('ENABLE_METRICS', False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feature flags to dictionary for logging/debugging."""
        return {
            'use_fake_flights': self.use_fake_flights,
            'use_fake_stays': self.use_fake_stays,
            'enable_caching': self.enable_caching,
            'enable_logging': self.enable_logging,
            'enable_metrics': self.enable_metrics
        }


def _parse_bool_env(env_var: str, default: bool) -> bool:
    """
    Parse boolean value from environment variable.
    
    Args:
        env_var: Environment variable name
        default: Default value if env var is not set
        
    Returns:
        Boolean value
    """
    value = os.getenv(env_var, '').lower()
    if value in ('true', '1', 'yes', 'on'):
        return True
    elif value in ('false', '0', 'no', 'off'):
        return False
    else:
        return default
