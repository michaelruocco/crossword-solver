# Crossword Solver

[![Quality gate status](https://sonarcloud.io/api/project_badges/measure?project=michaelruocco_crossword-solver&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=michaelruocco_crossword-solver)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=michaelruocco_crossword-solver&metric=coverage)](https://sonarcloud.io/summary/new_code?id=michaelruocco_crossword-solver)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=michaelruocco_crossword-solver&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=michaelruocco_crossword-solver)

## Local Development

### Prerequisites

Install Git, Node.js 22, pnpm 12.9.1, and uv. Run commands from the repository root unless a
different directory is shown. Install Python 3.14 with uv, then install the project dependencies:

```sh
uv python install 3.14
pnpm install --frozen-lockfile
uv sync --all-packages --frozen
```

AWS credentials, Terraform, Docker, and `zip` are not needed for the normal local build/lint/test
commands below. Terraform and AWS CLI v2 are needed for [AWS bootstrap](infrastructure/bootstrap/README.md).
Docker and `zip` are only needed if building the OpenCV Lambda layer locally.

### Build, Lint, and Test

Run targets across the whole workspace:

```sh
pnpm exec nx run-many -t build
pnpm exec nx run-many -t lint typecheck
pnpm exec nx run-many -t test
```

For the same complete set of targets used by CI, including deployable Lambda bundles:

```sh
pnpm exec nx run-many -t lint typecheck test build bundle
```

Python `build` targets also run lint, typecheck, and tests through their dependencies.
The default test targets include Python integration tests as well as unit tests.
Nx caches task results; use `--skip-nx-cache` to force execution.

### Check Only Affected Code

Fetch the comparison branch, then run checks for projects affected by changes since `origin/main`,
including their affected dependents. Nx also considers uncommitted changes when no explicit head
is supplied:

```sh
git fetch origin main
pnpm exec nx affected --base=origin/main -t lint typecheck test build bundle
```

Individual targets work the same way, for example:

```sh
pnpm exec nx affected --base=origin/main -t test
```

Choose another `--base` when comparing against a different branch or commit. On an up-to-date
`main` checkout with no local changes, there may be no affected projects.

### Include or Exclude Integration Tests

To run all workspace test targets but exclude Python integration tests:

```sh
PYTEST_ADDOPTS='-m "not integration"' pnpm exec nx run-many -t test --skip-nx-cache
```

For affected projects only:

```sh
PYTEST_ADDOPTS='-m "not integration"' pnpm exec nx affected --base=origin/main -t test --skip-nx-cache
```

`PYTEST_ADDOPTS` only affects pytest; TypeScript/UI tests run normally. Bypassing the Nx cache
avoids reusing results from a different marker selection. To exclude integration tests during
a combined check, set the same variable for the entire command, since Python builds also run tests:

```sh
PYTEST_ADDOPTS='-m "not integration"' pnpm exec nx run-many -t lint typecheck test build bundle --skip-nx-cache
```

To run only integration tests, run pytest from a Python project that has them, for example:

```sh
cd packages/lambdas/python-lambdas/adapter/grid_extractor
uv run pytest tests -m integration
```

Use `uv run pytest tests -m "not integration"` for just that project's unit tests, or
`uv run pytest tests` for both. Run pytest from the owning project's directory so its configured
report paths resolve correctly. Integration tests use real resources such as puzzle-image fixtures;
check the test's requirements before running. A package without matching tests exits with no tests selected.

### Run the UI

Set `VITE_API_BASE_URL` in `packages/ui/.env.local` to the deployed API Gateway base URL, then run:

```sh
pnpm exec nx run crossword_solver.ui:dev
```

Open the URL Vite prints. The API allows `http://127.0.0.1:5173` and `http://localhost:5173`;
if Vite selects another port because `5173` is busy, free the port and restart to avoid CORS errors.
See the [UI guide](packages/ui/README.md) for UI-specific commands.

### Python Test Conventions

Each Python project keeps unit tests in `tests/unit` and slower tests that use real resources
(e.g. puzzle images) in `tests/integration`, marked with `pytestmark = pytest.mark.integration`.

Pytest runs with `--import-mode=importlib` (set in each project's `pyproject.toml`), so a unit test
and an integration test can share the same filename. Test modules cannot import from each other;
shared fixtures and helpers belong in a `conftest.py`, which pytest loads for that directory and
below. Fixtures and helpers shared between projects live in the `test-utils` library, which
projects add as a dev dependency. Handler tests use its `response_status` and `response_json`
helpers from `crossword_solver_test_utils.responses`.

## Scaffolding New Projects

The projects in this repo were generated with [@aws/nx-plugin](https://www.npmjs.com/package/@aws/nx-plugin)
(see the `metadata.generator` entries in each `project.json`). The plugin is only needed to run its
generators, so it is not kept as a dependency: it pins older Nx versions, which pull in outdated
transitive dependencies (e.g. a vulnerable `axios`) and cause peer dependency conflicts.

To scaffold a new project, add it temporarily, run the generator, then remove it again:

```sh
pnpm add -D @aws/nx-plugin
pnpm exec nx g @aws/nx-plugin:py#lambda-function   # or ts#lambda-function, py#project, etc.
pnpm remove @aws/nx-plugin
pnpm dedupe
```

`pnpm dedupe` clears any older Nx packages the plugin left in the lockfile.

## Building and Deploying to AWS

Deployments run through GitHub Actions; local builds, Docker, and local Terraform application
commands are not required. The bootstrap guide lists the tools needed for initial AWS setup.
GitHub CLI (`gh`) is optional; workflows can also be started in the GitHub Actions UI.

### 1. Bootstrap AWS and GitHub

Follow the [bootstrap guide](infrastructure/bootstrap/README.md) to create the shared state
bucket, configure GitHub OIDC and the deployment role, and set GitHub environment variables.
It also covers adopting an existing role. Complete this setup before the first deployment;
subsequent deployments reuse it.

### 2. Publish the OpenCV layer

Run the [Publish OpenCV layer workflow](.github/workflows/publish-opencv-layer.yml) for the
branch or tag to deploy, and wait for it to finish before the first deployment:

```sh
gh workflow run publish-opencv-layer.yml --ref <branch-or-tag>
```

The workflow builds and publishes separately from deployment. It also runs automatically when
its inputs change on `main`. For a branch with layer changes, publish the updated layer before
deploying it.

The ZIP and its `SHA256SUMS` file are published as GitHub release assets under an
`opencv-layer-<hash>` tag. The
[version script](infrastructure/layer-release-tag.sh) takes `opencv` and derives
the hash from the layer's committed Dockerfile, build script, and publishing workflow,
plus the version script itself. Changing the version script requires a new layer release.
Application-only changes reuse existing releases,
and rerunning publication skips a release that already exists. Releases
are not marked as the repository's latest release.

Deployment resolves the layer's version from its selected commit, downloads the matching assets, and
verifies their SHA-256 checksums before Terraform runs. It never falls back to another version or
rebuilds the layer. An existing complete release is used immediately. If the exact release or
either asset is missing, deployment checks every 30 seconds for up to two hours, allowing the
independent publishing workflow to finish. If publication fails, the wait eventually times out
with instructions to publish the layer and retry; authentication and other API errors fail immediately.
Manual deployments also wait, but do not trigger publication automatically.
Keep these releases for old-commit deployments; do not replace their assets. Rebuilds after base
image or upstream dependency updates can be requested by changing a committed build input.

Publishing uses `GITHUB_TOKEN` with `contents: write`; deployment only needs `contents: read`.
No registry, additional credentials, or separate repository is required.

### 3. Deploy an environment

Merge the [Deploy workflow](.github/workflows/deploy.yml) into the default branch before using it.
The selected branch or tag must contain the workflow and the code to deploy; older tags without
the workflow cannot run it. Deploy only commits that have passed CI.

In **Actions > Deploy > Run workflow**, select a branch or tag in the native ref selector and
choose the target environment. Alternatively:

```sh
gh workflow run deploy.yml --ref <branch-or-tag> -f environment=dev
```

The workflow initializes the environment's S3 backend, prepares Lambda bundles, downloads the
OpenCV layer, applies a saved Terraform plan, and builds and uploads the UI. A new environment's
state object is created automatically; S3 lock files prevent concurrent state writes. Existing
locally managed infrastructure must have its state migrated first, as noted in the bootstrap guide.

The selected commit is checked out by SHA. The run summary and GitHub environment deployment
show the deployed UI URL. Pushes to `main` deploy to `dev` after successful CI; other branch
and tag deployments remain manual. Use GitHub environment approval rules when approval is required.

### Deploying with GitHub Actions

The committed Terraform provider lock file includes checksums for Linux AMD64 (GitHub Actions)
and macOS ARM64 (local development). After updating provider versions, refresh both platforms
and commit the updated lock file:

```sh
terraform -chdir=infrastructure/terraform providers lock \
  -platform=linux_amd64 -platform=darwin_arm64
```

The [CI workflow](.github/workflows/ci.yml) automatically calls the reusable
[Deploy workflow](.github/workflows/deploy.yml) for `dev` after all CI steps succeed on a push
to `main`. Pull requests do not deploy. The same deployment workflow can also be manually
triggered for a branch or tag and target environment, so deployment steps are maintained in one place.
It builds every Lambda package, downloads the prebuilt OpenCV layer, applies a saved Terraform plan,
then builds and uploads the UI using the deployed API URL. Runs for the same environment are
serialized and do not cancel an active deployment. An apply is automatic after planning; use
GitHub environment approval rules if a deployment requires approval before it starts.
Deployment does not rerun lint or tests. Automatic deployments download the Lambda bundles
produced by CI in the same workflow run, rather than rebuilding them. CI packages the bundles
in a tar archive to preserve permissions and symlinks, and retains the artifact for seven days.
A missing artifact fails deployment rather than silently rebuilding; after it expires, start a
new CI run or use a manual deployment. Manual deployments build their own Lambda bundles.
Both paths build the UI with the deployed environment's API URL.
New pushes do not cancel an active main-branch
CI/deployment run; superseded pull-request CI runs can still be cancelled.

#### Destroy an environment

The manual [Destroy environment workflow](.github/workflows/destroy.yml) permanently deletes
the selected environment's application infrastructure and data, including all versions of
objects in its application buckets and its DynamoDB tables. Back up anything needed first
and stop external writes/imports before starting.

In **Actions > Destroy environment > Run workflow**, select a trusted ref containing the
environment's current Terraform configuration, choose the environment, and type its exact
name in `confirmation`. Alternatively:

```sh
gh workflow run destroy.yml --ref main -f environment=dev -f confirmation=dev
```

The workflow uses the same OIDC role, GitHub environment protection rules, backend key, and
concurrency group as deployment, so deploy and destroy cannot run together for one environment.
It builds the Lambda bundles and downloads the matching published OpenCV layer because
Terraform still evaluates local artifact inputs for destruction. The layer release must exist.
It creates and automatically applies a saved destroy plan; environment approvals happen before
the job starts, not between plan and apply.

Bucket cleanup runs through [empty-destroy-buckets.sh](infrastructure/empty-destroy-buckets.sh).
Terraform's S3 bucket resource does not remove bucket contents when destroying a bucket;
S3 rejects `DeleteBucket` while objects remain. Versioning adds another wrinkle: removing an
object can create a delete marker while older versions remain, and those versions and markers
must also be explicitly deleted. The script removes current objects, then repeatedly lists and
deletes object versions and delete markers until each bucket is empty.

The script reads `destroy.tfplan` from `infrastructure/terraform`, gets bucket names from its
planned deletions, and accepts only this environment's puzzle-image, Lambda-layer, and UI buckets.
It refuses the shared Terraform state bucket and validates every planned bucket before deleting
anything. Once they are empty, Terraform can apply the saved destroy plan; that is why the
workflow uses `terraform apply destroy.tfplan` rather than making a new destroy plan.

The workflow runs the script automatically. To run it manually, first initialize Terraform and
create `destroy.tfplan` for the intended environment using the same state key; then, with AWS CLI
credentials for that environment, run from the repository root:

```sh
TF_VAR_environment=dev TF_STATE_BUCKET=<shared-state-bucket> bash infrastructure/empty-destroy-buckets.sh
terraform -chdir=infrastructure/terraform apply -lock-timeout=5m destroy.tfplan
```

This permanently removes application bucket data. Do not use a plan for a different environment.
If S3 rejects individual deletions, the script logs each failed object's key, version ID, error
code, and message before stopping. Its offline tests mock AWS and Terraform and require Bash and jq:

```sh
bash infrastructure/tests/empty-destroy-buckets.sh
```

The shared state bucket, state history, bootstrap deployment role, OIDC provider, and GitHub
environment remain intact. Bucket cleanup is irreversible even if Terraform subsequently fails;
resolve the failure and rerun to finish removing the environment. Avoid manual Terraform changes
while this workflow runs. Future pushes to `main` can recreate `dev` through automatic deployment.
