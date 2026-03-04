import logging
import secrets

from keycloak import KeycloakOpenID
import redis.asyncio as aioredis
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class OIDCProvider:

    _ACCESS_TOKEN_SUFFIX = "access_token"
    _REFRESH_TOKEN_SUFFIX = "refresh_token"
    _USER_INFO_SUFFIX = "user_info"

    def __init__(self, keycloak_client: KeycloakOpenID, redis_client: aioredis.Redis):
        self.keycloak_client = keycloak_client
        self.redis_client = redis_client

    async def login(self, code: str, redirect_uri: str) -> str:
        token_response = await self.keycloak_client.a_token(
            grant_type='authorization_code',
            code=code,
            redirect_uri=redirect_uri
        )
        print("Token response: %s", token_response)

        session_id = secrets.token_urlsafe(32)
        await self._store_session(session_id, token_response)
        return session_id

    async def logout(self, session_id: str) -> None:
        try:
            refresh_token_raw = await self.redis_client.get(
                f'{session_id}:{self._REFRESH_TOKEN_SUFFIX}'
            )
            if refresh_token_raw:
                await self.keycloak_client.a_logout(refresh_token_raw)
        except Exception as e:
            print(f"Error during Keycloak logout: {e}")
        finally:
            await self._delete_session(session_id)

    async def _store_session(self, session_id: str, token_response: dict[str, Any]) -> None:
        if access_token := token_response.get('access_token'):
            await self.redis_client.set(
                f'{session_id}:{self._ACCESS_TOKEN_SUFFIX}',
                access_token
            )
            if expires_in := token_response.get('expires_in'):
                await self.redis_client.expire(
                    f'{session_id}:{self._ACCESS_TOKEN_SUFFIX}',
                    int(expires_in)
                )
            await self._get_user_info(session_id)

        if refresh_token := token_response.get('refresh_token'):
            await self.redis_client.set(
                f'{session_id}:{self._REFRESH_TOKEN_SUFFIX}',
                refresh_token
            )
            if refresh_expires_in := token_response.get('refresh_expires_in'):
                await self.redis_client.expire(
                    f'{session_id}:{self._REFRESH_TOKEN_SUFFIX}',
                    int(refresh_expires_in)
                )

        print("Session stored for session_id prefix")

    async def silent_check_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        access_token = await self.redis_client.get(
            f'{session_id}:{self._ACCESS_TOKEN_SUFFIX}'
        )

        if access_token:
            print("Access token still valid, returning cached session")
            return await self._get_user_info(session_id)

        print("Access token expired, attempting refresh")
        refresh_token = await self.redis_client.get(
            f'{session_id}:{self._REFRESH_TOKEN_SUFFIX}'
        )

        if not refresh_token:
            print("Refresh token expired, deleting all session data")
            await self._delete_session(session_id)
            return None

        try:
            new_token_response = await self.keycloak_client.a_refresh_token(refresh_token)
            print("Token refreshed successfully")

            await self._store_session(session_id, new_token_response)
            return await self._get_user_info(session_id)
        except Exception as e:
            print(f"Error refreshing token: {e}")
            await self._delete_session(session_id)
            return None

    async def revoke_session(self, session_id: str) -> None:
        await self.redis_client.sadd("revoked_tokens", session_id)
        await self._delete_session(session_id)
        print("Session revoked")

    async def _delete_session(self, session_id: str) -> None:
        await self.redis_client.delete(
            f'{session_id}:{self._ACCESS_TOKEN_SUFFIX}',
            f'{session_id}:{self._REFRESH_TOKEN_SUFFIX}',
            f'{session_id}:{self._USER_INFO_SUFFIX}',
        )

    async def _get_user_info(self, session_id: str) -> dict[str, Any]:
        user_info = await self.redis_client.get(f'{session_id}:{self._USER_INFO_SUFFIX}')
        if not user_info:
            try:
                access_token = await self.redis_client.get(f'{session_id}:{self._ACCESS_TOKEN_SUFFIX}')
                user_info = await self.keycloak_client.a_userinfo(access_token)
                await self.redis_client.set(f'{session_id}:{self._USER_INFO_SUFFIX}', json.dumps(user_info))
                return user_info
            except Exception as e:
                print(f"Could not fetch user info: {e}")
                # TODO: this shouldnt return an empty dict, it should raise an exception
                return {}
        return json.loads(user_info)
