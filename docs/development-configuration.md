# Local development configuration

The development Compose stack reads credentials from local files under the
repository-root `secrets/` directory. These files are intentionally not tracked
by Git or included in application image build contexts. Create or provision the
files locally before starting the stack; do not add their contents to this
documentation.

Required files:

| File | Used by |
|---|---|
| `secrets/keycloak_client_secret_key` | Auth service Keycloak client |
| `secrets/postgres_password` | PostgreSQL and vacation planner |
| `secrets/redis_password` | Redis, auth service, and flight service |
| `secrets/grafana_admin_password` | Local Grafana admin account in the optional observability stack |

Restrict local file permissions (for example, owner read/write only) and rotate
any credential that has previously been committed or otherwise exposed. Compose
mounts these files as read-only secrets at `/run/secrets/` inside the relevant
containers.

Non-secret development overrides can be supplied through the shell or an
ignored root `.env` file:

| Variable | Purpose | Default |
|---|---|---|
| `SERVER` | Flight API adapter (`rest`, `grpc`, or `graphql`) | `rest` |
| `SELENIUM_REMOTE_URL` | Selenium Grid URL for flight scraping | Uses `flight_service/conf.ini` when unset |
| `VITE_AUTH_BACKEND_URL` | Auth BFF URL used by the Vite development server | `http://localhost:8000` |

`fe-client` reads `VITE_AUTH_BACKEND_URL` at Vite startup. Its production image
is built with the same setting as a required build argument because Vite embeds
this value into the static bundle.

The local Compose dependencies require all three secret files even when a
particular application feature is not being exercised. Production server-side
configuration and secret synchronization are documented and implemented in a
separate deployment phase.
