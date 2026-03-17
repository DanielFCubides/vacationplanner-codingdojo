import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .auth_router import router as auth_router
from providers.oidc_provider import OIDCProvider, get_oidc_provider
from config import internal_routes

app = FastAPI(
    title="Auth Service",
    description="Authentication BFF for Vacation Planner",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router)

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        service="auth-service",
        version="1.0.0"
    )


@app.api_route(
    "/{service_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
)
async def proxy_request(
    service_path: str,
    request: Request,
    provider: OIDCProvider = Depends(get_oidc_provider)
):
    try:
        service_name, endpoint_path = service_path.split('/', 1)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid path structure")

    router = internal_routes.get(service_name)
    if router is None:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    normalized_endpoint = f"/{endpoint_path}"
    available_routes = router.get('available_routes')

    route_allowed = False
    for route_pattern in available_routes:
        if normalized_endpoint == route_pattern:
            route_allowed = True
            break
        if matches_wildcard(normalized_endpoint, route_pattern):
            route_allowed = True
            break

    if not route_allowed:
        raise HTTPException(status_code=404, detail="Endpoint not allowed")

    session_id = request.cookies.get('session_id')

    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_context = await provider.silent_check_session(session_id)
    if not session_context:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    target_url = f"{router['main_url']}{endpoint_path}"

    proxy_headers = dict(request.headers)
    proxy_headers.pop('host', None)
    proxy_headers.pop('content-length', None)
    proxy_headers['Authorization'] = f"Bearer {session_context.access_token}"

    client = httpx.AsyncClient()
    try:
        proxy_req = client.build_request(
            method=request.method,
            url=target_url,
            headers=proxy_headers,
            content=request.stream(),
            params=request.query_params
        )

        upstream_response = await client.send(proxy_req, stream=True)

        async def stream_response():
            try:
                async for chunk in upstream_response.aiter_raw():
                    yield chunk
            finally:
                await upstream_response.aclose()
                await client.aclose()

        return StreamingResponse(
            stream_response(),
            status_code=upstream_response.status_code,
            headers=upstream_response.headers,
        )
    except httpx.RequestError as e:
        await client.aclose()
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except Exception as e:
        await client.aclose()
        raise HTTPException(status_code=500, detail=f"Internal proxy error: {str(e)}")

def matches_wildcard(route: str, pattern: str) -> bool:
    if '*' not in pattern:
        return False
    route_parts = route.split('/')
    pattern_parts = pattern.split('/')
    if len(route_parts) != len(pattern_parts):
        return False
    for r_part, p_part in zip(route_parts, pattern_parts):
        if p_part != '*' and p_part != r_part:
            return False
    return True