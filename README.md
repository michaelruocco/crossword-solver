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
do not rerun the bucket creation script. For GitHub Actions deployments, configure the same
`TF_STATE_BUCKET` value and bootstrap AWS authentication as described below before the first run.

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
pnpm exec nx run-many -t bundle
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
It builds every Lambda package, downloads prebuilt native layers, applies a saved Terraform plan,
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

#### Publishing native layers

The [Publish OpenCV layer](.github/workflows/publish-opencv-layer.yml) and
[Publish Tesseract layer](.github/workflows/publish-tesseract-layer.yml) workflows build and
publish independently, separately from deployment. Each runs when its own inputs change on `main`,
or manually against a branch or tag. Both can run in parallel:

```sh
gh workflow run publish-opencv-layer.yml --ref <branch-or-tag>
gh workflow run publish-tesseract-layer.yml --ref <branch-or-tag>
```

Run both once after adding these workflows, and wait for them to finish before the first deployment.
For a branch with layer changes, publish only the changed layer before deploying it.

Each ZIP and its `SHA256SUMS` file are published as GitHub release assets under an
`opencv-layer-<hash>` or `tesseract-layer-<hash>` tag. The
[version script](infrastructure/layer-release-tag.sh) takes `opencv` or `tesseract` and derives
the hash from that layer's committed Dockerfile, build script, data, and publishing workflow,
plus the shared version script. Changing one layer does not change the other's release version;
changing the shared version script rebuilds both. Application-only changes reuse existing releases,
and rerunning publication skips a release that already exists. Releases
are not marked as the repository's latest release.

Deployment resolves each layer's version from its selected commit, downloads the matching assets, and
verifies their SHA-256 checksums before Terraform runs. It never falls back to another version or
rebuilds layers. If assets are missing, deployment fails with instructions to publish them first.
Keep these releases for old-commit deployments; do not replace their assets. Rebuilds after base
image or upstream dependency updates can be requested by changing a committed build input.

Publishing uses `GITHUB_TOKEN` with `contents: write`; deployment only needs `contents: read`.
No registry, additional credentials, or separate repository is required. Local Docker builds
remain available using the commands above.

#### One-time AWS and GitHub setup

1. Create the state bucket using the bootstrap instructions above. If deploying an existing
   environment, ensure its state has been migrated to the matching S3 key first.
2. In AWS IAM, register GitHub's OIDC provider, `https://token.actions.githubusercontent.com`,
   with audience `sts.amazonaws.com`, if the account does not already have it.
3. Create an IAM deployment role with a trust policy like the following, replacing
   `<aws-account-id>` and using the target GitHub environment name in the subject:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::<aws-account-id>:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
             "token.actions.githubusercontent.com:sub": "repo:michaelruocco/crossword-solver:environment:dev"
           }
         }
       }
     ]
   }
   ```

   Grant this role the permissions required to manage the resources in `infrastructure/terraform`
   (including the Lambda IAM roles and `iam:PassRole`), upload UI files, and invalidate CloudFront.
   It also needs `s3:ListBucket` on the state bucket, `s3:GetObject` and `s3:PutObject` on the
   environment's state object, and `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject` on its
   `.tflock` object. Scope state access to the environment's key and lock file. No AWS access keys
   are stored in GitHub.
4. Under **Settings > Environments**, create the target environment (for example, `dev`).
   Use lowercase letters, digits, and hyphens, starting with a letter. Configure deployment
   protection rules to allow only trusted branches and tags and add required reviewers where needed.
   The workflow's environment-based OIDC subject relies on these rules to restrict which code
   can assume the role.
5. Add these GitHub Actions variables at repository level, or override them in each environment:

   | Variable | Value |
   | --- | --- |
   | `AWS_ROLE_ARN` | ARN of the environment's OIDC deployment role |
   | `TF_STATE_BUCKET` | Name of the existing shared state bucket |
   | `AWS_REGION` | Deployment region; defaults to `eu-west-2` |
   | `TF_STATE_REGION` | State bucket region; defaults to `AWS_REGION` |

Each environment uses `crossword-solver/<environment>/terraform.tfstate` in the shared bucket.
The state bucket and OIDC resources are bootstrap prerequisites; this workflow does not create them.

#### Run a deployment

Merge the workflow into the default branch before using it. The selected branch or tag must also
contain the workflow and the code to deploy; older tags without the workflow cannot run it.
Deploy only commits that have passed CI.

In **Actions > Deploy > Run workflow**, select a branch or tag in the native ref selector and
choose the target environment.
GitHub cannot dynamically populate a custom workflow input with repository tags; the native ref
selector avoids maintaining a separate tag list.

Alternatively, dispatch an existing branch or tag explicitly with GitHub CLI:

```sh
gh workflow run deploy.yml --ref <branch-or-tag> -f environment=dev
```

The selected commit is checked out by SHA. The run summary and GitHub environment deployment
show the deployed UI URL. Pushes to `main` deploy to `dev` after successful CI; other branch
and tag deployments remain manual.

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
