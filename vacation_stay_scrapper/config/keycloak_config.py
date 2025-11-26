from pydantic_settings import BaseSettings


class KeycloakSettings(BaseSettings):
    KEYCLOAK_SERVER_URL: str = "https://keycloak.dfcubidesc.com"
    KEYCLOAK_REALM: str = "your-realm-name"
    KEYCLOAK_CLIENT_ID: str = "your-client-id"
    KEYCLOAK_PUBLIC_KEY_ENDPOINT: str = "/auth/realms/{realm}/protocol/openid-connect/certs"

    @property
    def public_key_url(self) -> str:
        return f"{self.KEYCLOAK_SERVER_URL}{self.KEYCLOAK_PUBLIC_KEY_ENDPOINT.format(realm=self.KEYCLOAK_REALM)}"

    class Config:
        case_sensitive = True


keycloak_settings = KeycloakSettings()