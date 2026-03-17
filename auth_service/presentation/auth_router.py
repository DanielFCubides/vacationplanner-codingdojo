import os
from typing import Dict, Any

from providers.oidc_provider import OIDCProvider, get_oidc_provider

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.responses import RedirectResponse

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")
KEYCLOAK_REDIRECT_URI = os.getenv("KEYCLOAK_REDIRECT_URI", "http://localhost:8002/auth/login")

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login")
async def login(
    code: str,
    state: str,
    session_state: str | None = None,
    iss: str | None = None,
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> RedirectResponse:
    try:
        session_id = await provider.login(code, KEYCLOAK_REDIRECT_URI)

        redirect = RedirectResponse(url=f"{FRONTEND_URL}/", status_code=status.HTTP_302_FOUND)
        redirect.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False, 
            samesite="lax"
        )
        return redirect
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, str]:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    await provider.logout(session_id)
    response.delete_cookie("session_id")

    return {"message": "Logged out successfully"}


@router.get("/silent_check")
async def silent_check(
    request: Request,
    response: Response,
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    session_context = await provider.silent_check_session(session_id)
    if not session_context:
        response.delete_cookie("session_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired, please log in again"
        )
    return {"userinfo": session_context.user_info}
