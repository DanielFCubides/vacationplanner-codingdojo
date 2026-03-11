# Vacation Planner Auth Service
 
By centralizing authentication logic in this service, the frontend application avoids dealing with tokens directly. Instead, it relies on HTTP-only cookies (`session_id`), and this service attaches the correct OIDC access tokens to requests before forwarding them to downstream internal APIs.

## Features

- **OIDC Authentication Flow**: Login, logout, and token introspection via Keycloak.
- **Session Management**: Securely handles sessions with Redis, mitigating token exposure to the frontend.
- **Reverse Proxy**: Intelligently routes requests to appropriate downstream services, injecting `Authorization: Bearer <token>` automatically based on the active session.

## Endpoints

### Authentication (`/auth`)

These endpoints manage the user lifecycle with the OIDC provider (Keycloak). 
- `GET /auth/login` - The callback endpoint for the OIDC flow. Trades an authorization code for tokens, creates a session in Redis, sets a `session_id` cookie, and redirects to the frontend.
- `POST /auth/logout` - Terminates the session in Keycloak and Redis, and clears the frontend cookie.
- `GET /auth/silent_check` - Validates the active session and returns user info. Performs token introspection and refresh transparently if necessary. 

### Reverse Proxy Handler (`/{service_path:path}`)

Any route other than `/auth` and `/health` is evaluated by the reverse proxy. 

**Logic Flow:**
1. The path is parsed to identify the target `service_name` (e.g., `/user-service/api/profile` => service: `user-service`, endpoint: `api/profile`).
2. The service configuration is loaded from `routes.yml`.
3. Validates the endpoint against allowed `available_routes`.
4. Retrieves `session_token` from cookies and fetches the corresponding JWT `access_token` from Redis.
5. Injects the `Authorization: Bearer` header.
6. Forwards the request and streams the response back to the client.

## Usage & Examples

### 1. Typical Login Flow

The user clicks "Login" on the frontend and is redirected to your OIDC Provider portal (Keycloak). Upon successful authentication, Keycloak redirects the user to the auth service:

```http
GET http://localhost:8002/auth/login?code=123abc456def&state=xyz
```

The service processes the code, generates a secure `session_id`, sets the cookie, and directs the user to the frontend url (set up in an env var`FRONTEND_URL`).

### 2. Requesting Internal APIs

When the frontend needs to fetch user trips data from a downstream `vacation_stay_service`, it requests the auth BFF instead:

```javascript
// Frontend fetch (browser automatically includes the session_id cookie)
fetch('http://localhost:8002/user-service/api/profile', {
    method: 'GET'
});
```

The auth service looks up the cookie, gets the valid JWT from Redis, and makes this request behind the scenes:

```http
GET http://internal-vacation-stay-service-url/api/trips
Authorization: Bearer <valid_access_token>
```

## Running the Service

### Prerequisites
- A configured remote Keycloak instance.
- A `routes.yml` file defining your downstream services in the project root.

### Environment Variables

You can configure the behavior via environment variables (or a `.env` file):

```bash
# Keycloak
KEYCLOAK_SERVER_URL=http://localhost:8080/
KEYCLOAK_CLIENT_ID=backend-client
KEYCLOAK_REALM_NAME=master
KEYCLOAK_CLIENT_SECRET_KEY=secret

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Internal
FRONTEND_URL=http://localhost:3001
```

### Installation and Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server using Uvicorn:
   ```bash
   fastapi dev presentation/main.py --port 8002
   # OR
   uvicorn presentation.main:app --host 0.0.0.0 --port 8002 --reload
   ```

### Running with docker
You can also run the service using Docker. The provided `Dockerfile` exposes port `8000` and runs the application using the FastAPI CLI.

1. Build the Docker image:
   ```bash
   docker build -t auth-service .
   ```

2. Run the Docker container:
   ```bash
   docker run -p 8000:8000 --env-file .env auth-service
   ```
   *Note: Ensure your `.env` file contains the required environment variables (Keycloak, Redis, etc.) or pass them using `-e` flags. If Redis or Keycloak are running on your host machine, you may need to use `--network host` or map `localhost` to `host.docker.internal` depending on your OS.*
