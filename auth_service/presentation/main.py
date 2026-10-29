import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

try:  # Telemetry is optional — the service must run even without the OTel API.
    from opentelemetry import trace
except Exception:  # noqa: BLE001
    trace = None

from presentation.auth_router import router as auth_router
from providers.oidc_provider import OIDCProvider, get_oidc_provider
from config import internal_routes, get_allowed_hosts
from log_config import get_logger
from telemetry import setup_telemetry


logger = get_logger(__name__)

app = FastAPI(
    title="Auth Service",
    description="Authentication BFF for Vacation Planner",
    version="1.0.0"
)

# Centralized telemetry — traces/metrics/logs to the OTel collector when it is
# reachable; otherwise a single warning and local stdout logging only.
setup_telemetry("auth-service", app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_hosts(),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router)

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str


@app.get("/health", response_model=HealthCheckResponse, tags=["health"])
async def health_check():
    logger.info("Health check requested")
    return HealthCheckResponse(
        status="healthy",
        service="auth-service",
        version="1.0.0"
    )


@app.api_route(
    "/{service_path:path}", 
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    tags=["proxy"]
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
        logger.error("Service not found", extra={"service_name": service_name, "endpoint_path": endpoint_path})
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

    await log_downstream_target(normalized_endpoint, request, service_name)

    session_id = request.cookies.get('session_id')

    if not session_id:
        logger.debug("No session ID found", extra={"service_name": service_name, "endpoint_path": endpoint_path})
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_context = await provider.silent_check_session(session_id)
    if not session_context:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    await log_acting_user(session_context)

    target_url = f"{router['main_url']}{endpoint_path}"

    proxy_headers = dict(request.headers)
    proxy_headers.pop('host', None)
    proxy_headers.pop('content-length', None)
    proxy_headers['Authorization'] = f"Bearer {session_context.access_token}"
    logger.debug("Authentication headers proxied")

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

        logger.info("Proxied request", extra={"url": target_url, "method": request.method})
        return StreamingResponse(
            stream_response(),
            status_code=upstream_response.status_code,
            headers=upstream_response.headers,
        )
    except httpx.RequestError as e:
        await client.aclose()
        logger.error("Service unavailable", extra={"error": str(e)})
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except Exception as e:
        await client.aclose()
        logger.error("Internal proxy error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Internal proxy error: {str(e)}")


async def log_acting_user(session_context):
    # Attribute the trace to the acting user (best-effort).
    try:
        user_info = session_context.user_info or {}
        username = user_info.get("preferred_username") or user_info.get("sub")
        if username:
            trace.get_current_span().set_attribute("enduser.id", str(username))
    except Exception as e:
        logger.error("preferred_username not attached", extra={"error": str(e)})


async def log_downstream_target(normalized_endpoint: str, request, service_name: str):
    # Rename the catch-all proxy span to the real downstream target so traces
    # show e.g. "POST /vacation-planner/api/trips" instead of
    # "POST /{service_path:path}". Best-effort — telemetry never breaks the request.
    try:
        span = trace.get_current_span()
        route = f"/{service_name}{normalized_endpoint}"
        span.update_name(f"{request.method} {route}")
        span.set_attribute("http.route", route)
        span.set_attribute("app.proxy.service", service_name)
    except Exception as e:
        logger.error("downstream target not attached", extra={"error": str(e)})  # noqa: BLE001


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