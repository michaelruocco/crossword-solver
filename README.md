# Crossword Solver

[![Quality gate status](https://sonarcloud.io/api/project_badges/measure?project=michaelruocco_crossword-solver&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=michaelruocco_crossword-solver)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=michaelruocco_crossword-solver&metric=coverage)](https://sonarcloud.io/summary/new_code?id=michaelruocco_crossword-solver)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=michaelruocco_crossword-solver&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=michaelruocco_crossword-solver)

## Building and Deploying to AWS

### Prerequisites

Install Node.js 22, pnpm, Python 3.14, uv, Terraform 1.10 or newer, AWS CLI v2, Docker,
and `zip`. Start Docker and configure AWS CLI credentials for the target AWS account.
Run the following commands from the repository root.

```
pnpm install --frozen-lockfile
uv sync --all-packages --frozen
```

### 1. Bootstrap the shared state bucket

Terraform needs an existing S3 bucket before it can initialize its remote backend. Create
this bucket once per account/project, before the first local deployment or deployment pipeline
run. It is shared by environments, with a separate state key for each environment.

Choose a globally unique bucket name and set the target environment and region:

```
export TF_STATE_BUCKET="<globally-unique-bucket-name>"
export AWS_REGION="eu-west-2"
export DEPLOY_ENV="dev"

./infrastructure/terraform/setup-state-bucket.sh "$TF_STATE_BUCKET" "$AWS_REGION"
```

The script enables versioning, default encryption, bucket-owner enforcement, and S3 public-access
blocking. The bucket is created outside the application's Terraform configuration, so destroying
an application environment does not delete its state bucket. Do not delete the bucket while its
state is still needed.

Subsequent deployments and additional environments in the same account reuse the existing bucket;
do not rerun the bucket creation script. For a future GitHub Actions deployment, configure the
same `TF_STATE_BUCKET` value and bootstrap the AWS OIDC provider and deployment role before the
first pipeline run. The deployment workflow is not yet included in this repository.

### 2. Initialize a new environment

For a clean environment with no existing infrastructure or local Terraform state:

```
terraform -chdir=infrastructure/terraform init \
  -backend-config="bucket=$TF_STATE_BUCKET" \
  -backend-config="key=crossword-solver/$DEPLOY_ENV/terraform.tfstate" \
  -backend-config="region=$AWS_REGION" \
  -backend-config="encrypt=true" \
  -backend-config="use_lockfile=true"
```

Terraform creates the state object when it first writes state; there is no need to create the
environment's key manually. S3 lock files prevent concurrent writes to the same environment's state.

For another environment, set `DEPLOY_ENV` to its name and use a fresh checkout, or rerun the
initialization command with `-reconfigure` to switch this checkout to that environment's key.
Always match `DEPLOY_ENV` in the state key to the `environment` variable when planning and applying.
Do not use `-migrate-state` to switch environments: that would copy the previous environment's state.

If adopting remote state for infrastructure already managed by a local state file, use
`-migrate-state` instead for the initial migration and confirm Terraform's prompt. Migration
preserves existing resources; do not initialize an empty state to manage them or destroy them
just to move state into S3.

### 3. Build and deploy

Build the Lambda packages and native layers before planning, since Terraform reads their
local artifacts:

```
pnpm exec nx run-many -t assemble
docker build --platform linux/amd64 -t crossword-solver-opencv-layer infrastructure/opencv
./infrastructure/opencv/build-layer.sh
./infrastructure/tesseract/build-layer.sh

terraform -chdir=infrastructure/terraform plan \
  -var="environment=$DEPLOY_ENV" -var="aws_region=$AWS_REGION"
terraform -chdir=infrastructure/terraform apply \
  -var="environment=$DEPLOY_ENV" -var="aws_region=$AWS_REGION"
```

Review the plan before confirming the apply. Once the infrastructure exists, deploy the UI and
print its URL:

```
pnpm nx run crossword_solver.ui:deploy
terraform -chdir=infrastructure/terraform output -raw ui_url
```

## Scaffolding New Projects

The projects in this repo were generated with [@aws/nx-plugin](https://www.npmjs.com/package/@aws/nx-plugin)
(see the `metadata.generator` entries in each `project.json`). The plugin is only needed to run its
generators, so it is not kept as a dependency: it pins older Nx versions, which pull in outdated
transitive dependencies (e.g. a vulnerable `axios`) and cause peer dependency conflicts.

To scaffold a new project, add it temporarily, run the generator, then remove it again:

```
pnpm add -D @aws/nx-plugin
pnpm exec nx g @aws/nx-plugin:py#lambda-function   # or ts#lambda-function, py#project, etc.
pnpm remove @aws/nx-plugin
pnpm dedupe
```

`pnpm dedupe` clears any older Nx packages the plugin left in the lockfile.

## Python Tests

Each Python project keeps unit tests in `tests/unit` and slower tests that use real resources (e.g. puzzle images)
in `tests/integration`, marked with `pytestmark = pytest.mark.integration`. To run one set or the other from a
project's directory:

```
uv run pytest tests -m "not integration"
uv run pytest tests -m integration
```

Pytest runs with `--import-mode=importlib` (set in each project's `pyproject.toml`), so a unit test and an
integration test can share the same file name, e.g. `tests/unit/test_grid_finder.py` and
`tests/integration/test_grid_finder.py`. The trade-off is that test modules cannot import from each other, so
shared fixtures and test helpers belong in a `conftest.py`, which pytest loads automatically for every test in
that directory and below. Fixtures and helpers shared between projects live in the `test-utils` library, which
projects add as a dev dependency. For example, `create-puzzle/tests/conftest.py` imports the `build_event`,
`build_sqs_event` and `lambda_context` fixtures from `crossword_solver_test_utils.fixtures`, and handler tests use
the `response_status` and `response_json` helpers from `crossword_solver_test_utils.responses`.
