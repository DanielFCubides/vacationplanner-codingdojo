import json
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .auth_router import router as auth_router
from infrastructure.redis_client import get_redis_client
from auth_service.config import internal_routes
from redis.asyncio import Redis

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
    redis_client: Redis = Depends(get_redis_client)
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
    
    if normalized_endpoint not in available_routes and "/" not in available_routes:
         raise HTTPException(status_code=404, detail="Endpoint not allowed")

    session_token = request.cookies.get('session_token')

    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_data_raw = await redis_client.get(session_token)
    if not session_data_raw:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    try:
        session_data = json.loads(session_data_raw)
        access_token = session_data.get('access_token')
        if not access_token:
             raise HTTPException(status_code=401, detail="Session missing access token")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Corrupt session data")

    target_url = f"{router['main_url']}{endpoint_path}"
    
    proxy_headers = dict(request.headers)
    proxy_headers.pop('host', None)
    proxy_headers.pop('content-length', None)
    
    proxy_headers['Authorization'] = f"Bearer {access_token}"

    async with httpx.AsyncClient() as client:
        try:
            proxy_req = client.build_request(
                method=request.method,
                url=target_url,
                headers=proxy_headers,
                content=request.stream(),
                params=request.query_params
            )
            
            upstream_response = await client.send(proxy_req, stream=True)
            
            return StreamingResponse(
                upstream_response.aiter_raw(),
                status_code=upstream_response.status_code,
                headers=upstream_response.headers,
                background=None
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal proxy error: {str(e)}")
