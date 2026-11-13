# Production image publishing

`.github/workflows/ci.yml` runs on pushes to `main`. It builds production image
targets independently and publishes a build mapping as an OCI artifact in
`<DOCKER_HUB_REGISTRY_SEBAS>/vacation-planner-manifests:build-<full-sha>`.
There is no test workflow yet. The previous automatic deployment job is removed;
publishing does not deploy the stack.

## GitHub production environment

Configure `DOCKER_HUB_REGISTRY_SEBAS` (Docker Hub namespace) and the public
`VITE_AUTH_BACKEND_URL` as variables, and `DOCKER_USERNAME_SEBAS` and
`DOCKER_PASSWORD_SEBAS` as secrets. The Docker Hub account needs push access to
all four image repositories and the manifest repository. Registry access must
also permit reading the artifacts. No secrets belong in frontend build args.

For the first run only, set `MANIFEST_BOOTSTRAP=true`: all four images are built
and a complete mapping is published. Bootstrap ignores any prior state, so remove
or set the variable to `false` before later builds. Until the future deployment
workflow creates `production-state`, non-bootstrap builds fail closed.

Normal builds retrieve `production-state` and its current build manifest by OCI
digest, verify the namespace and revision, and compare the deployed revision to
the current main commit. A changed service directory rebuilds that service; a
change outside the four service directories conservatively rebuilds all four.
The baseline must be an ancestor of the new revision. A production rollback can
therefore cause subsequent builds to rebuild all changes since the rolled-back
revision. If the baseline cannot be read or verified the build fails rather than
assuming tags. The manifest records a full SHA revision and four SHA tags.

The Docker Hub `build-*` immutable tag rule protects build artifacts. A rerun of
the same commit currently fails when its manifest tag already exists; investigate
the existing artifact rather than disabling the rule. Image tags also need
registry-side immutability policies if available: the build workflow alone does
not prevent a writer from replacing an application image tag. Treat registry
credentials and access controls accordingly. Docker Hub OCI artifact support and
the first real build must be verified before relying on the pipeline.

Deployment will use the build manifest and maintain `production-state` only after
health verification. The manifest is not evidence of a successful deployment.
Public frontend Keycloak URLs and redirects are currently baked into the bundle;
the existing frontend Dockerfile exposes only `VITE_AUTH_BACKEND_URL` as a build
argument. Resolve remaining production frontend configuration before deployment.
