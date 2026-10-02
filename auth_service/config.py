import os
from pathlib import Path
import yaml


def get_allowed_hosts() -> list:
    return os.getenv("ALLOWED_HOSTS", "*").split(",")


def get_secret(name: str, default: str | None = None) -> str | None:
    """Read a Docker secret mounted at /run/secrets/<name>."""
    secret_path = Path("/run/secrets", name)
    if not secret_path.is_file():
        return default
    return secret_path.read_text(encoding="utf-8").strip()


def get_internal_router() -> dict:
    with open('routes.yml', 'r') as file:
        routes = yaml.safe_load(file)
    return routes


internal_routes = get_internal_router()
