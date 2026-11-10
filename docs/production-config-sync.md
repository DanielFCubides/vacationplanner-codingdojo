# Production configuration sync

The manually dispatched **Synchronize production configuration** workflow in
`.github/workflows/sync-env.yml` writes configuration only; it does not build
images, update Portainer, restart containers, or verify application readiness.
The existing `docker-image.yml` workflow remains separate and unchanged; its
build and deployment behavior will be revised in a later phase.

## Provisioning

An administrator must prepare `/opt/vacation-planner` and its `config`,
`secrets`, and `backups` directories as root-owned directories. Set the root and
`secrets` directories to group ID `10001` with mode `0710`, and set `config` and
`backups` to mode `0700`. Create a root-owned `0600`
`/opt/vacation-planner/.sync.lock` file.
The SSH account must execute the receiver as root, with Python 3 installed.
The workflow fails closed if it cannot verify these requirements. Restrict SSH
access and protect the GitHub `production` environment with approvals.

Secrets are owned by root, group `10001`, with mode `0640`; env files remain
root-only (`0600`). UID 10001 can read secrets **only when the container process
also belongs to group 10001** (as its primary or supplementary group). UID and
GID are separate: verify the image's actual group and, if needed, configure
`group_add: ["10001"]` in the future production Compose file. Account for user
namespace remapping and test on the actual Docker host. Every process in that
group can read these secrets; do not use it for unrelated containers.
Existing root-only secret files must be migrated by an administrator to these
permissions before validation succeeds.

## GitHub production environment inputs

| Type | Name | Purpose |
|---|---|---|
| Variable | `SERVICES_HOST`, `SERVICES_SSH_USER` | SSH host and root-capable account |
| Secret | `SERVICES_SSH_KEY` | SSH private key |
| Secret | `SERVICES_SSH_KNOWN_HOSTS` | Verified SSH known_hosts entry; acquire and verify out-of-band |
| Variable | `KEYCLOAK_SERVER_URL`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_REALM_NAME` | Auth Keycloak connection |
| Variable | `FRONTEND_URL`, `KEYCLOAK_REDIRECT_URI` | Auth frontend and callback URLs |
| Variable | `KEYCLOAK_BASE_URL`, `KEYCLOAK_REALM` | Vacation planner Keycloak connection |
| Variable | `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_DB` | Vacation planner database connection |
| Variable | `REDIS_HOST` | Auth and flight Redis host |
| Variable | `SELENIUM_REMOTE_URL` | Flight Selenium URL, including any required path |
| Secret | `KEYCLOAK_CLIENT_SECRET_KEY` | Auth client secret |
| Secret | `POSTGRES_PASSWORD` | Vacation planner database password |
| Secret | `REDIS_SECRET` | Shared Redis password |

Required values must be non-empty single-line strings. Env-file values cannot
contain single quotes or backslashes. Values are never passed as SSH command
arguments. SSH uses the pinned known-hosts file, not trust-on-first-use.

## File mapping and operation

Each selection writes `config/<service>.env` for `auth-service`,
`vacation-planner`, `flight-service`, or `fe-client`. The frontend env file is
empty: Vite settings are embedded at image build time, not read from runtime
env files. Auth writes `secrets/keycloak_client_secret_key` and
`secrets/redis_password`; vacation planner writes `secrets/postgres_password`;
flight writes `secrets/redis_password`. Redis is shared: changing that file
affects both auth and flight when they are later recreated. Synchronizing a
single service can therefore change a secret used by another service.

Run the workflow first with `validate_only=true`, then run it with `false`.
Validation checks inputs and remote destinations without writing server files.
Updates stage files on the destination filesystem and atomically replace each
changed file after backing up old contents. The workflow reports filenames,
not contents or hashes. A failed multi-file update can be partial; inspect the
reported error and protected backup before retrying. Existing containers do not
receive updated environment values until recreated.

Backups under `/opt/vacation-planner/backups/` contain sensitive values; restrict
access and establish retention and encrypted off-host recovery separately.
To recover, an administrator should inspect the appropriate protected backup,
restore env files with root ownership and mode `0600`, and secret files with
root ownership, group `10001`, and mode `0640`, then use the
future deployment process to recreate affected containers. Coordinate secret
rotation with the external PostgreSQL, Redis, or Keycloak provider first; sync
does not change their credentials. Do not log or share the secret files.
