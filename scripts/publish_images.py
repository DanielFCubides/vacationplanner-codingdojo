#!/usr/bin/env python3
"""Publish changed images and an immutable build mapping for a main commit."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

SERVICES = {
    "auth-service": "auth_service",
    "vacation-planner": "vacation_stay_scrapper",
    "flight-service": "flight_service",
    "fe-client": "fe-client",
}
SHA = re.compile(r"^[0-9a-f]{40}$")


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def load_manifest(path, namespace):
    data = json.loads(path.read_text())
    if data.get("schema_version") != 1 or data.get("registry") != namespace or not SHA.fullmatch(data.get("revision", "")):
        raise ValueError("Invalid baseline build manifest")
    images = data.get("images")
    if not isinstance(images, dict) or set(images) != set(SERVICES) or any(not re.fullmatch(r"sha-[0-9a-f]{40}", str(tag)) for tag in images.values()):
        raise ValueError("Invalid baseline image tags")
    return data


def main():
    namespace = os.environ.get("DOCKER_HUB_REGISTRY_SEBAS", "")
    revision = os.environ.get("GITHUB_SHA", "")
    username = os.environ.get("DOCKER_USERNAME", "")
    password = os.environ.get("DOCKER_PASSWORD", "")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", namespace) or not SHA.fullmatch(revision) or not username or not password:
        raise ValueError("Invalid or missing registry, revision, or registry credentials")
    repo = f"docker.io/{namespace}/vacation-planner-manifests"
    run("oras", "login", "docker.io", "-u", username, "--password-stdin", input=password, text=True, stdout=subprocess.DEVNULL)
    with tempfile.TemporaryDirectory(prefix="image-manifest-") as directory:
        root = Path(directory)
        bootstrap = os.environ.get("MANIFEST_BOOTSTRAP", "false").lower()
        if bootstrap not in ("true", "false", ""):
            raise ValueError("MANIFEST_BOOTSTRAP must be true or false")
        if bootstrap == "true":
            baseline = None
        else:
            # Fail closed if state is unavailable; do not interpret network or
            # authorization errors as a missing baseline.
            run("oras", "pull", f"{repo}:production-state", "-o", str(root))
            state = json.loads((root / "production-state.json").read_text())
            current = state.get("current") or {}
            digest = current.get("manifest_digest", "")
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
                raise ValueError("Invalid production-state manifest digest")
            run("oras", "pull", f"{repo}@{digest}", "-o", str(root))
            baseline = load_manifest(root / "manifest.json", namespace)
            if current.get("revision") != baseline["revision"]:
                raise ValueError("Production state and build manifest revision do not match")
            run("git", "merge-base", "--is-ancestor", baseline["revision"], revision)

        if baseline:
            changed = run("git", "diff", "--name-only", "-z", baseline["revision"], revision, stdout=subprocess.PIPE).stdout.decode().split("\0")
            shared = any(path and not any(path.startswith(folder + "/") for folder in SERVICES.values()) for path in changed)
            selected = [service for service, folder in SERVICES.items() if shared or any(path.startswith(folder + "/") for path in changed)]
            images = dict(baseline["images"])
        else:
            selected = list(SERVICES)
            images = {}

        for service in selected:
            tag = f"sha-{revision}"
            command = ["docker", "buildx", "build", "--push", "--platform", "linux/amd64,linux/arm64", "--target", "prod", "-t", f"{namespace}/{service}:{tag}"]
            if service == "fe-client":
                url = os.environ.get("VITE_AUTH_BACKEND_URL", "")
                if not url.startswith(("https://", "http://")):
                    raise ValueError("VITE_AUTH_BACKEND_URL must be a public HTTP(S) URL")
                command.extend(["--build-arg", f"VITE_AUTH_BACKEND_URL={url}"])
            command.append(SERVICES[service])
            run(*command)
            images[service] = tag

        manifest = {"schema_version": 1, "revision": revision, "registry": namespace, "images": images}
        path = root / "manifest.json"
        path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
        # Registry immutability makes an existing tag a safe hard failure.
        run("oras", "push", f"{repo}:build-{revision}", "--artifact-type", "application/vnd.vacation-planner.manifest.v1+json", "manifest.json:application/json", cwd=root)
        print(f"Published build manifest build-{revision}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"Image publishing failed: {exc}", file=sys.stderr)
        sys.exit(1)
