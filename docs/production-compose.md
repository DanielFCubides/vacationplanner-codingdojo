# Production Compose stack

`docker/compose.prod.yml` defines only the four application services. It uses
prebuilt Docker Hub images, the configuration files provisioned by the manual
sync workflow, and file-backed secrets. It does not define infrastructure or
development bind mounts. See `docs/production-config-sync.md` for the server
setup and required service configuration.

## Images and configuration

The Compose process must receive `DOCKER_HUB_REGISTRY_SEBAS`,
`AUTH_SERVICE_TAG`, `VACATION_PLANNER_TAG`, `FLIGHT_SERVICE_TAG`, and
`FE_CLIENT_TAG` for interpolation. Supply the Docker Hub namespace in the
registry variable and immutable commit-SHA tags in the service variables. These
are Compose interpolation variables, not values read from the service
`env_file` entries. A later deployment phase will provide them to Portainer.

The stack reads `/opt/vacation-planner/config/<service>.env` and the required
files in `/opt/vacation-planner/secrets/` on the Docker host. Provision and sync
all four service files before deployment. Portainer and the Docker daemon must
be able to access the files, and secret-consuming containers join supplementary
GID `10001` (`vacation-secrets`). Verify file permissions and secret access on
the target Docker host, including any user-namespace remapping.

`fe-client` serves static files on container port 80. Its `VITE_*` settings are
embedded at image build time; its synced runtime env file cannot alter the
bundle. Ensure the future image build supplies browser-reachable public URLs and
does not put secrets into the bundle.

## Networking and exposure

The application services share the Compose default network and can reach one
another by service name and container port, for example
`http://vacation-planner:8000`. The ports published on the host are 8000 (auth),
8001 (vacation planner), 8002 (flight), and 3001 (frontend). These mappings bind
all host interfaces by default; restrict exposure with a firewall or proxy
before deploying. Browser-facing URLs such as `FRONTEND_URL` must be externally
resolvable, not Compose service names.

PostgreSQL, Redis, Kafka, Selenium and Keycloak are managed separately. Their
configured hostnames or URLs must be reachable from the application containers;
this stack does not create or attach an external infrastructure network. If
dependencies are accessible only on a separate Docker network, a later
deployment configuration must attach the stack to that network. Flight
Selenium connectivity may remain unavailable while its deployment is in
progress. The checked-in auth proxy routes also need review: the flights route
currently targets `flights:8000`, which does not match this stack's
`flight-service:8080`.

## Local syntax validation

With Docker Compose supporting `--no-env-resolution`, validate the Compose
model without the production env files or real image tags:

```sh
DOCKER_HUB_REGISTRY_SEBAS=example \
AUTH_SERVICE_TAG=placeholder VACATION_PLANNER_TAG=placeholder \
FLIGHT_SERVICE_TAG=placeholder FE_CLIENT_TAG=placeholder \
docker compose -f docker/compose.prod.yml config --no-env-resolution --quiet
```

This checks the Compose model only; it does not validate server-side file
contents, host connectivity, image availability, container permissions, or
application behavior. Image publishing, Portainer Git-stack updates, and
redeployment remain future phases.
