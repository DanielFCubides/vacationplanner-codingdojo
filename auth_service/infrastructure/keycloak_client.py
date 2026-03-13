import os
from keycloak import KeycloakOpenID

KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080/")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "backend-client")
KEYCLOAK_REALM_NAME = os.getenv("KEYCLOAK_REALM_NAME", "master")
KEYCLOAK_CLIENT_SECRET_KEY = os.getenv("KEYCLOAK_CLIENT_SECRET_KEY", "secret")

async def get_keycloak_client() -> KeycloakOpenID:
    client = KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL,
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM_NAME,
        client_secret_key=KEYCLOAK_CLIENT_SECRET_KEY,
        verify=True
    )
    return client