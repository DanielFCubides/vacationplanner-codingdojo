import os
from keycloak import KeycloakOpenID


def _get_secret(env_name: str, file_env_name: str, default: str = "") -> str:
    secret_file = os.getenv(file_env_name)
    if secret_file:
        try:
            with open(secret_file, encoding="utf-8") as file:
                return file.read().strip()
        except OSError as exc:
            raise RuntimeError(f"Unable to read secret file configured by {file_env_name}") from exc
    return os.getenv(env_name, default)


KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080/")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "backend-client")
KEYCLOAK_REALM_NAME = os.getenv("KEYCLOAK_REALM_NAME", "master")
KEYCLOAK_CLIENT_SECRET_KEY = _get_secret(
    "KEYCLOAK_CLIENT_SECRET_KEY",
    "KEYCLOAK_CLIENT_SECRET_FILE",
)

async def get_keycloak_client() -> KeycloakOpenID:
    client = KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL,
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM_NAME,
        client_secret_key=KEYCLOAK_CLIENT_SECRET_KEY,
        verify=True
    )
    return client
