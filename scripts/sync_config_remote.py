"""Remote receiver. Reads an allowlisted JSON payload from stdin."""
import fcntl
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import time

ROOT = Path("/opt/vacation-planner")
# Numeric ID of the host's dedicated vacation-secrets group.
SECRET_GROUP = 10001
ALLOWED = {
    "config/auth-service.env", "config/vacation-planner.env", "config/flight-service.env", "config/fe-client.env",
    "secrets/keycloak_client_secret_key", "secrets/postgres_password", "secrets/redis_password",
}


def check_directory(path):
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o027:
        raise ValueError(f"Unsafe directory: {path}")


def check_secret_access(path):
    info = path.stat()
    if info.st_gid != SECRET_GROUP or not info.st_mode & stat.S_IXGRP:
        raise ValueError(f"Directory must be traversable by group {SECRET_GROUP}: {path}")


def main():
    payload = json.load(sys.stdin)
    files = payload.get("files")
    if not isinstance(files, dict) or not files or not set(files) <= ALLOWED or type(payload.get("validate_only")) is not bool:
        raise ValueError("Invalid sync payload")
    if os.geteuid() == 0:
        raise ValueError("Sync must run as the unprivileged directory owner")
    if SECRET_GROUP not in os.getgroups() and SECRET_GROUP != os.getegid():
        raise ValueError(f"Sync user must belong to group {SECRET_GROUP}; reconnect after updating group membership")
    for path in (ROOT, ROOT / "config", ROOT / "secrets", ROOT / "backups"):
        check_directory(path)
    for path in (ROOT, ROOT / "secrets"):
        check_secret_access(path)
    for relative, content in files.items():
        if not isinstance(content, str) or "\x00" in content:
            raise ValueError("Invalid file content")
        destination = ROOT / relative
        if destination.is_symlink() or (destination.exists() and not destination.is_file()):
            raise ValueError(f"Unsafe destination: {relative}")
        if destination.exists():
            info = destination.stat()
            expected_mode = 0o640 if relative.startswith("secrets/") else 0o600
            if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != expected_mode or (relative.startswith("secrets/") and info.st_gid != SECRET_GROUP):
                raise ValueError(f"Unsafe ownership or permissions: {relative}")
    lock_path = ROOT / ".sync.lock"
    if lock_path.is_symlink() or not lock_path.is_file():
        raise ValueError("Missing or unsafe synchronization lock file")
    lock_info = lock_path.stat()
    if lock_info.st_uid != os.geteuid() or lock_info.st_mode & 0o077:
        raise ValueError("Unsafe synchronization lock permissions")
    if payload["validate_only"]:
        print("Validation succeeded; no server files changed")
        return

    # The pre-provisioned lock file avoids changing anything in validation mode.
    with open(lock_path, "r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        changed = []
        for relative, content in files.items():
            target = ROOT / relative
            data = content.encode("utf-8")
            if target.exists() and target.read_bytes() == data:
                continue
            changed.append((relative, data))
        if not changed:
            print("No configuration changes")
            return
        backup = Path(tempfile.mkdtemp(prefix=time.strftime("%Y%m%dT%H%M%SZ-", time.gmtime()), dir=ROOT / "backups"))
        os.chmod(backup, 0o700)
        staged = []
        try:
            for relative, data in changed:
                target = ROOT / relative
                if target.exists():
                    backup_file = backup / relative
                    backup_file.parent.mkdir(mode=0o700, exist_ok=True)
                    shutil.copyfile(target, backup_file)
                    os.chmod(backup_file, 0o600)
                fd, temporary = tempfile.mkstemp(prefix=".sync-", dir=target.parent)
                staged.append(temporary)
                with os.fdopen(fd, "wb") as output:
                    if relative.startswith("secrets/"):
                        os.fchown(output.fileno(), -1, SECRET_GROUP)
                        os.fchmod(output.fileno(), 0o640)
                    else:
                        os.fchmod(output.fileno(), 0o600)
                    output.write(data)
                    output.flush()
                    os.fsync(output.fileno())
            for (relative, _), temporary in zip(changed, staged):
                os.replace(temporary, ROOT / relative)
            print("Updated files: " + ", ".join(relative for relative, _ in changed))
            print("Backup directory: " + backup.name)
            print("Containers were not restarted")
        finally:
            for temporary in staged:
                if os.path.exists(temporary):
                    os.unlink(temporary)


try:
    main()
except (ValueError, OSError, json.JSONDecodeError) as exc:
    print(f"Remote validation or synchronization failed: {exc}", file=sys.stderr)
    sys.exit(1)
