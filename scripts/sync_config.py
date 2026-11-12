#!/usr/bin/env python3
"""Send explicitly mapped configuration to the production host over SSH."""
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


SERVICES = {
    "auth-service": {
        "env": ["KEYCLOAK_SERVER_URL", "KEYCLOAK_CLIENT_ID", "KEYCLOAK_REALM_NAME", "FRONTEND_URL", "KEYCLOAK_REDIRECT_URI", "REDIS_HOST"],
        "secrets": {"keycloak_client_secret_key": "KEYCLOAK_CLIENT_SECRET_KEY", "redis_password": "REDIS_SECRET"},
        "fixed": {"KEYCLOAK_CLIENT_SECRET_FILE": "/run/secrets/keycloak_client_secret_key", "REDIS_PASSWORD_FILE": "/run/secrets/redis_password"},
    },
    "vacation-planner": {
        "env": ["POSTGRES_HOST", "POSTGRES_USER", "POSTGRES_DB", "KEYCLOAK_BASE_URL", "KEYCLOAK_REALM", "KEYCLOAK_CLIENT_ID"],
        "secrets": {"postgres_password": "POSTGRES_PASSWORD"},
        "fixed": {"POSTGRES_PASSWORD_FILE": "/run/secrets/postgres_password"},
    },
    "flight-service": {
        "env": ["REDIS_HOST", "SELENIUM_REMOTE_URL"],
        "secrets": {"redis_password": "REDIS_SECRET"},
        "fixed": {"SERVER": "rest", "REDIS_PASSWORD_FILE": "/run/secrets/redis_password"},
    },
    "fe-client": {"env": [], "secrets": {}, "fixed": {}},
}


def required(name):
    value = os.environ.get(name, "")
    if not value.strip() or "\n" in value or "\r" in value or "\x00" in value:
        raise ValueError(f"Missing or invalid required input: {name}")
    return value


def main():
    selected = os.environ.get("SYNC_SERVICE", "all")
    if selected != "all" and selected not in SERVICES:
        raise ValueError("Invalid service selection")
    mode = os.environ.get("SYNC_VALIDATE_ONLY", "true").lower()
    if mode not in ("true", "false"):
        raise ValueError("Invalid validation mode")
    services = list(SERVICES) if selected == "all" else [selected]
    files = {}
    for name in services:
        spec = SERVICES[name]
        values = {key: required(key) for key in spec["env"]}
        values.update(spec["fixed"])
        # Compose env_file accepts single-quoted literals; double single quotes
        # are not portable, so reject values containing quotes or newlines.
        if any("'" in value or "\\" in value for value in values.values()):
            raise ValueError(f"Invalid env-file value for {name}")
        files[f"config/{name}.env"] = "".join(f"{key}='{value}'\n" for key, value in values.items())
        for filename, source in spec["secrets"].items():
            files[f"secrets/{filename}"] = required(source)

    host, user = required("SERVICES_HOST"), required("SERVICES_SSH_USER")
    if not re.fullmatch(r"[A-Za-z0-9_.:-]+", host) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", user):
        raise ValueError("Invalid SSH host or user")
    key = os.environ.get("SERVICES_SSH_KEY", "")
    known_hosts = os.environ.get("SERVICES_SSH_KNOWN_HOSTS", "")
    if not key.strip() or not known_hosts.strip():
        raise ValueError("SSH key and pinned known-hosts entry are required")
    remote_script = Path(__file__).with_name("sync_config_remote.py").read_bytes()
    encoded = base64.b64encode(remote_script).decode("ascii")
    command = f"python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\""
    with tempfile.TemporaryDirectory(prefix="vacation-sync-") as directory:
        directory = Path(directory)
        key_path, hosts_path = directory / "key", directory / "known_hosts"
        key_path.write_text(key.rstrip() + "\n", encoding="utf-8")
        hosts_path.write_text(known_hosts.rstrip() + "\n", encoding="utf-8")
        key_path.chmod(0o600)
        hosts_path.chmod(0o600)
        payload = json.dumps({"files": files, "validate_only": mode == "true"})
        subprocess.run([
            "ssh", "-i", str(key_path), "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=yes", "-o", f"UserKnownHostsFile={hosts_path}",
            "-o", "BatchMode=yes", "--", f"{user}@{host}", command,
        ], input=payload, text=True, check=True)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Configuration synchronization failed: SSH exited with status {exc.returncode}; see preceding output", file=sys.stderr)
        sys.exit(1)
    except (ValueError, OSError) as exc:
        print(f"Configuration synchronization failed: {exc}", file=sys.stderr)
        sys.exit(1)
