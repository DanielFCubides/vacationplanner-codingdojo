import os
import configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read('conf.ini')

# Allow deployment/runtime configuration to override the checked-in defaults.
for section, key, env_name in (
    ('Redis', 'host', 'REDIS_HOST'),
    ('Redis', 'port', 'REDIS_PORT'),
    ('Kafka', 'host', 'KAFKA_HOST'),
    ('Kafka', 'port', 'KAFKA_PORT'),
    ('Default', 'repository', 'FLIGHT_REPOSITORY'),
    ('Default', 'publisher', 'FLIGHT_PUBLISHER'),
):
    if value := os.getenv(env_name):
        config[section][key] = value

root_path = os.path.dirname(__file__)
presentation_path = os.path.join(root_path, 'presentations')


def get_secret(name: str, default: str | None = None) -> str | None:
    """Read a Docker secret mounted at /run/secrets/<name>."""
    secret_path = Path('/run/secrets', name)
    if not secret_path.is_file():
        return default
    return secret_path.read_text(encoding='utf-8').strip()
